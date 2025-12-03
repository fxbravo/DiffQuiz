"""
Génération et validation des quiz.
"""
import json
import random
import logging
from typing import List, Dict, Any, Optional
from diffquiz.config import Settings
from diffquiz.llm_client import call_llm_api
from diffquiz.exceptions import QuizGenerationError, ValidationError

logger = logging.getLogger(__name__)


def clean_json_text(text: str) -> str:
    """
    Nettoie la réponse du LLM pour extraire uniquement le JSON valide.
    
    Args:
        text: Texte brut de la réponse LLM.
        
    Returns:
        JSON nettoyé.
    """
    text = text.strip()
    
    # Si le LLM met des balises markdown, extraire le contenu
    if "```json" in text:
        parts = text.split("```json")
        if len(parts) > 1:
            text = parts[1].split("```")[0].strip()
    elif "```" in text:
        # Chercher le premier bloc de code
        parts = text.split("```")
        if len(parts) > 1:
            # Prendre le contenu du premier bloc (index 1)
            text = parts[1].strip()
            # Si le bloc commence par "json\n" ou "json ", le retirer
            if text.startswith("json\n"):
                text = text[5:]
            elif text.startswith("json "):
                text = text[5:]
    
    # Chercher la première occurrence de '[' et la dernière de ']' pour un tableau JSON
    start_index = text.find('[')
    end_index = text.rfind(']')
    
    if start_index != -1 and end_index != -1 and start_index < end_index:
        json_candidate = text[start_index:end_index + 1]
        # Vérifier que c'est bien du JSON valide en comptant les accolades
        if json_candidate.count('[') == json_candidate.count(']'):
            return json_candidate
    
    # Chercher aussi un objet JSON '{' ... '}'
    start_index = text.find('{')
    end_index = text.rfind('}')
    
    if start_index != -1 and end_index != -1 and start_index < end_index:
        json_candidate = text[start_index:end_index + 1]
        # Vérifier que c'est bien du JSON valide
        if json_candidate.count('{') == json_candidate.count('}'):
            return json_candidate
    
    # Si rien ne fonctionne, retourner le texte nettoyé et laisser json.loads() gérer l'erreur
    logger.warning(f"Impossible d'extraire proprement le JSON. Texte reçu (premiers 500 caractères): {text[:500]}")
    return text.strip()


def _validate_option_lengths(options: List[str], question_num: int) -> None:
    """
    Vérifie que les options ont des longueurs similaires pour éviter que la bonne réponse soit identifiable.
    
    Args:
        options: Liste des options à valider.
        question_num: Numéro de la question (pour les messages d'erreur).
    """
    if len(options) < 2:
        return
    
    # Compter les mots dans chaque option (en retirant le préfixe "A) ", "B) ", etc.)
    word_counts = []
    for opt in options:
        # Retirer le préfixe "X) " si présent
        text = opt.split(')', 1)[1].strip() if ')' in opt else opt.strip()
        word_count = len(text.split())
        word_counts.append(word_count)
    
    if not word_counts:
        return
    
    # Calculer la moyenne et vérifier les écarts
    avg_words = sum(word_counts) / len(word_counts)
    max_diff_percent = 0.3  # 30% de différence max
    
    for idx, count in enumerate(word_counts):
        diff_percent = abs(count - avg_words) / avg_words if avg_words > 0 else 0
        if diff_percent > max_diff_percent:
            logger.warning(
                f"Question {question_num}, option {chr(65 + idx)} : "
                f"longueur déséquilibrée ({count} mots vs moyenne {avg_words:.1f} mots, "
                f"écart {diff_percent*100:.1f}%). "
                f"Risque que la bonne réponse soit identifiable par sa longueur."
            )


def validate_quiz_schema(quiz_data: List[Dict[str, Any]]) -> None:
    """
    Valide le schéma du quiz.
    
    Args:
        quiz_data: Données du quiz à valider.
        
    Raises:
        ValidationError: Si le schéma est invalide.
    """
    if not isinstance(quiz_data, list):
        raise ValidationError("Le quiz doit être une liste de questions")
    
    if len(quiz_data) == 0:
        raise ValidationError("Le quiz ne peut pas être vide")
    
    required_fields = ['question', 'options', 'answer', 'explanation']
    option_labels = ['A', 'B', 'C', 'D']
    
    for i, question in enumerate(quiz_data):
        if not isinstance(question, dict):
            raise ValidationError(f"Question {i+1} doit être un dictionnaire")
        
        # Vérifier les champs requis
        for field in required_fields:
            if field not in question:
                raise ValidationError(f"Question {i+1} manque le champ '{field}'")
        
        # Vérifier les options
        options = question['options']
        if not isinstance(options, list) or len(options) < 2:
            raise ValidationError(f"Question {i+1} doit avoir au moins 2 options")
        
        if len(options) > len(option_labels):
            raise ValidationError(f"Question {i+1} a trop d'options (max {len(option_labels)})")
        
        # Vérifier la réponse
        answer = question['answer'].strip().upper()
        if answer not in option_labels[:len(options)]:
            raise ValidationError(
                f"Question {i+1} : réponse '{answer}' invalide. "
                f"Attendu: {', '.join(option_labels[:len(options)])}"
            )
        
        # Vérifier l'équilibre de longueur des options (avertissement seulement)
        _validate_option_lengths(options, i + 1)


def generate_quiz_prompt(diff_text: str, count: int) -> tuple:
    """
    Génère les prompts système et utilisateur pour le LLM.
    
    Args:
        diff_text: Texte du diff.
        count: Nombre de questions à générer.
        
    Returns:
        Tuple (prompt_system, prompt_user).
    """
    prompt_system = """Tu es un expert technique Senior en développement logiciel, spécialisé en sécurité et bonnes pratiques. 
Ton rôle est de créer des QCM de haute qualité qui testent vraiment les connaissances techniques et détectent les risques de sécurité.
Tu es un générateur de JSON strict. Tu ne parles pas, tu ne dis pas bonjour. Tu sors uniquement du JSON valide."""

    prompt_user = f"""
Analyse le code suivant (git diff) et génère un QCM technique de haute qualité qui teste les connaissances ET détecte les risques de sécurité.

Code Diff:
{diff_text}

=== OBJECTIFS PRINCIPAUX ===
1. TESTER LES CONNAISSANCES : Vérifier que le développeur comprend vraiment ce qu'il a écrit/modifié
2. DÉTECTER LES RISQUES : Identifier tout code dangereux ou problématique dans les changements

=== RISQUES DE SÉCURITÉ À DÉTECTER (PRIORITÉ ABSOLUE) ===
- Commandes shell dangereuses : rm -rf, rm -f, del /f, format, etc.
- Opérations DB destructives : DROP TABLE, DELETE FROM, TRUNCATE, DROP DATABASE
- Injections SQL : requêtes non préparées, concaténation de strings dans SQL
- XSS (Cross-Site Scripting) : sortie HTML non échappée, innerHTML non sécurisé
- Path traversal : ../ dans les chemins de fichiers
- Hardcoded secrets : mots de passe, clés API, tokens en clair dans le code
- Accès fichiers non sécurisés : FileInputStream sans validation, accès système de fichiers
- Commandes système : Runtime.exec(), ProcessBuilder avec input utilisateur
- Désérialisation non sécurisée : ObjectInputStream avec données non fiables
- Logs contenant des données sensibles : mots de passe, tokens, données personnelles
- Gestion d'erreurs révélant trop d'infos : stack traces complets en production
- Authentification/autorisation manquante ou faible
- Race conditions : accès concurrent non protégé
- DoS potentiels : boucles infinies, regex ReDoS, requêtes N+1

=== TYPES DE QUESTIONS À GÉNÉRER ===
Priorité 1 - SÉCURITÉ (si risques détectés) :
- "Quel risque de sécurité présente cette modification ?"
- "Pourquoi cette ligne de code est-elle dangereuse ?"
- "Quelle est la conséquence de cette opération ?"

Priorité 2 - COMPRÉHENSION TECHNIQUE :
- "Quel est l'effet de cette modification sur [comportement spécifique] ?"
- "Pourquoi cette approche est-elle préférable à [alternative] ?"
- "Quelle est la complexité algorithmique de ce code ?"
- "Quel pattern de design est utilisé ici ?"

Priorité 3 - BONNES PRATIQUES :
- "Quelle amélioration pourrait être apportée à ce code ?"
- "Quel principe SOLID est violé ici ?"
- "Pourquoi cette pratique est-elle recommandée ?"

=== RÈGLES STRICTES POUR LES QUESTIONS ===
1. Chaque question doit être PRÉCISE et TESTABLE
2. Les questions doivent porter sur le CODE MODIFIÉ, pas sur des concepts généraux
3. Les mauvaises réponses doivent être CRÉDIBLES (pas évidentes)
4. Les explications doivent être DÉTAILLÉES et ÉDUCATIVES
5. Si un risque de sécurité est détecté, il DOIT faire l'objet d'au moins une question
6. Les questions doivent tester la COMPRÉHENSION, pas la mémorisation

=== RÈGLES CRITIQUES POUR LES OPTIONS DE RÉPONSE ===
1. **LONGUEUR UNIFORME** : Toutes les options (A, B, C, D) doivent avoir une longueur SIMILAIRE (±20% de mots)
   - La bonne réponse NE DOIT PAS être plus longue que les autres
   - Les distracteurs doivent être aussi détaillés et crédibles que la bonne réponse
2. **CRÉDIBILITÉ** : Chaque distracteur doit être plausible et basé sur des erreurs réelles que pourrait faire un développeur
3. **DIVERSITÉ** : Variez les types d'erreurs dans les distracteurs (conceptuel, syntaxique, logique, sécurité)
4. **PAS DE PATTERNS VISIBLES** : Ne pas utiliser de formulations comme "C'est correct car..." uniquement dans la bonne réponse

=== FORMAT DE SORTIE ===
Génère exactement {count} question(s) au format JSON strict :

[
  {{
    "question": "Question précise sur le code modifié",
    "options": [
      "A) Réponse avec longueur similaire aux autres (15-25 mots)",
      "B) Distracteur crédible avec longueur similaire (15-25 mots)",
      "C) Distracteur crédible avec longueur similaire (15-25 mots)",
      "D) Distracteur crédible avec longueur similaire (15-25 mots)"
    ],
    "answer": "A",
    "explanation": "Explication détaillée et éducative expliquant pourquoi la bonne réponse est correcte ET pourquoi les autres sont incorrectes. Inclure des exemples concrets si pertinent."
  }}
]

IMPORTANT :
- La bonne réponse peut être en A, B, C ou D. Variez la position de la bonne réponse entre les questions.
- TOUTES les options doivent avoir une longueur SIMILAIRE (15-25 mots chacune). La bonne réponse ne doit JAMAIS être significativement plus longue.
- Chaque distracteur doit être aussi détaillé et crédible que la bonne réponse.

=== INSTRUCTIONS FINALES ===
1. Analyse d'abord le code pour identifier les risques et points importants
2. Génère exactement {count} question(s) de qualité
3. Format RAW JSON ARRAY uniquement (pas de Markdown, pas d'introduction)
4. Si des risques de sécurité sont détectés, ils DOIVENT être couverts par les questions
5. Les questions doivent être adaptées au niveau junior mais tester vraiment la compréhension
6. Chaque explication doit être éducative et aider à apprendre
7. **CRITIQUE** : Vérifie que toutes les options ont une longueur similaire avant de générer le JSON. Si la bonne réponse est plus longue, réécris-la pour qu'elle soit aussi concise que les distracteurs.
"""
    
    return prompt_system, prompt_user


def generate_quiz(diff_text: str, count: int, settings: Settings) -> Optional[List[Dict[str, Any]]]:
    """
    Génère un quiz basé sur le diff.
    
    Args:
        diff_text: Texte du diff.
        count: Nombre de questions à générer.
        settings: Configuration de l'application.
        
    Returns:
        Liste de questions du quiz ou None en cas d'erreur.
        
    Raises:
        QuizGenerationError: En cas d'erreur de génération.
    """
    if not diff_text:
        logger.warning("Aucun diff fourni")
        return None
    
    if count <= 0:
        logger.warning(f"Nombre de questions invalide : {count}")
        return None
    
    # Limiter la longueur du diff
    truncated_diff = diff_text[:settings.max_diff_length]
    if len(diff_text) > settings.max_diff_length:
        logger.warning(f"Diff tronqué de {len(diff_text)} à {settings.max_diff_length} caractères")
    
    try:
        # Générer les prompts
        prompt_system, prompt_user = generate_quiz_prompt(truncated_diff, count)
        
        # Appeler l'API LLM
        content = call_llm_api(prompt_system, prompt_user, settings)
        
        if not content:
            logger.error("Aucun contenu reçu de l'API LLM")
            return None
        
        # Nettoyer et parser le JSON
        cleaned_json = clean_json_text(content)
        logger.debug(f"JSON nettoyé (premiers 200 caractères): {cleaned_json[:200]}")
        
        try:
            quiz_data = json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON à la position {e.pos}: {e.msg}")
            logger.error(f"Contexte autour de l'erreur: ...{cleaned_json[max(0, e.pos-50):e.pos+50]}...")
            logger.error(f"JSON complet reçu (premiers 1000 caractères):\n{cleaned_json[:1000]}")
            raise
        
        # Valider le schéma
        validate_quiz_schema(quiz_data)
        
        # Mélanger les options
        shuffled_quiz = shuffle_quiz_options(quiz_data)
        
        logger.info(f"Quiz généré avec succès : {len(shuffled_quiz)} questions")
        return shuffled_quiz
        
    except (json.JSONDecodeError, ValidationError) as e:
        error_msg = f"Erreur de validation du quiz : {e}"
        logger.error(error_msg)
        raise QuizGenerationError(error_msg) from e
    except Exception as e:
        error_msg = f"Erreur lors de la génération du quiz : {e}"
        logger.error(error_msg, exc_info=True)
        raise QuizGenerationError(error_msg) from e


def shuffle_quiz_options(quiz_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Mélange aléatoirement l'ordre des options pour chaque question.
    
    Args:
        quiz_data: Liste des questions du quiz.
        
    Returns:
        Quiz avec options mélangées.
    """
    if not quiz_data:
        return quiz_data
    
    shuffled_quiz = []
    option_labels = ['A', 'B', 'C', 'D']
    
    for question in quiz_data:
        shuffled_question = question.copy()
        options = question.get('options', [])
        
        if not options:
            shuffled_quiz.append(shuffled_question)
            continue
        
        correct_answer_letter = question.get('answer', 'A').strip().upper()
        correct_index = ord(correct_answer_letter) - ord('A')
        
        if correct_index < 0 or correct_index >= len(options):
            correct_index = 0
        
        # Extraire les textes des options
        options_with_text = []
        for opt in options:
            if ')' in opt:
                opt_text = opt.split(')', 1)[1].strip()
            else:
                opt_text = opt.strip()
            options_with_text.append(opt_text)
        
        # Mélanger les indices
        indices = list(range(len(options_with_text)))
        random.shuffle(indices)
        
        # Trouver la nouvelle position de la bonne réponse
        new_correct_index = None
        for i, idx in enumerate(indices):
            if idx == correct_index:
                new_correct_index = i
                break
        
        if new_correct_index is None:
            new_correct_index = 0
        
        # Reconstruire les options
        shuffled_options = []
        for i, idx in enumerate(indices):
            shuffled_options.append(f"{option_labels[i]}) {options_with_text[idx]}")
        
        shuffled_question['options'] = shuffled_options
        shuffled_question['answer'] = option_labels[new_correct_index]
        
        shuffled_quiz.append(shuffled_question)
    
    return shuffled_quiz


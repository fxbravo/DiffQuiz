#!/usr/bin/env python3
"""
Point d'entrée principal pour DiffQuiz.
Génère un quiz basé sur les modifications Git pour valider les connaissances des développeurs.
"""
import os
import sys
import logging
from typing import Optional

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from diffquiz.config import get_settings
from diffquiz.git_utils import get_git_diff, calculate_question_count
from diffquiz.quiz_generator import generate_quiz
from diffquiz.html_generator import generate_html
from diffquiz.security import hash_quiz_answers
from diffquiz.exceptions import DiffQuizError, GitDiffError, QuizGenerationError


def _write_pass_mode_files(error_reason: str) -> None:
    """
    Écrit les fichiers pour le mode PASS (fallback en cas d'erreur).
    
    Args:
        error_reason: Raison de l'erreur (pour logging).
    """
    logger.warning("⚠️ Mode PASS activé pour ne pas bloquer la production")
    with open("quiz.env", "w", encoding="utf-8") as f:
        f.write("EXPECTED_SECRET_HASH=PASS\n")
    with open("quiz_report.html", "w", encoding="utf-8") as f:
        f.write("<h1>Erreur IA - Utilisez le code 'PASS' pour valider.</h1>")


def get_commit_url() -> Optional[str]:
    """
    Récupère l'URL du commit depuis les variables d'environnement.
    
    Returns:
        URL du commit ou None si non disponible.
    """
    # GitHub Actions
    if os.environ.get('GITHUB_SHA'):
        github_server = os.environ.get('GITHUB_SERVER_URL', 'https://github.com')
        github_repo = os.environ.get('GITHUB_REPOSITORY', '')
        github_sha = os.environ.get('GITHUB_SHA', '')
        if github_repo and github_sha:
            return f"{github_server}/{github_repo}/commit/{github_sha}"
    
    # GitLab CI/CD
    elif os.environ.get('CI_COMMIT_SHA'):
        gitlab_project_url = os.environ.get('CI_PROJECT_URL', '')
        gitlab_sha = os.environ.get('CI_COMMIT_SHA', '')
        if gitlab_project_url and gitlab_sha:
            return f"{gitlab_project_url}/-/commit/{gitlab_sha}"
    
    return None


def main() -> int:
    """
    Fonction principale.
    
    Returns:
        Code de sortie (0 = succès, 1 = erreur).
    """
    try:
        logger.info("🚀 Démarrage du Compliance Guard...")
        
        # Charger la configuration
        try:
            settings = get_settings()
            logger.info(f"Configuration chargée : modèle={settings.llm_model}, API={settings.llm_api_url}")
        except Exception as e:
            logger.error(f"❌ Erreur de configuration : {e}")
            return 1
        
        # 1. Récupération du Diff
        try:
            diff = get_git_diff()
        except GitDiffError as e:
            logger.error(f"❌ {e}")
            return 1
        
        if not diff:
            logger.info("ℹ️ Aucun diff significatif trouvé. Mode SKIP.")
            with open("quiz.env", "w", encoding="utf-8") as f:
                f.write("EXPECTED_SECRET_HASH=SKIP\n")
            return 0
        
        # 2. Calcul du nombre de questions
        count = calculate_question_count(
            diff,
            lines_per_question=settings.lines_per_question,
            max_questions=settings.max_questions
        )
        logger.info(f"📝 Analyse du code : {len(diff)} caractères. Génération de {count} question(s)...")
        
        # 3. Génération du quiz
        try:
            quiz = generate_quiz(diff, count, settings)
        except QuizGenerationError as e:
            logger.error(f"❌ Erreur lors de la génération du quiz : {e}")
            _write_pass_mode_files("Erreur lors de la génération du quiz")
            return 0
        
        if not quiz:
            logger.warning("⚠️ Échec de la génération du quiz (Erreur IA/Réseau). Mode PASS activé.")
            _write_pass_mode_files("Erreur IA/Réseau")
            return 0
        
        # 4. Calcul du hash des réponses correctes (code secret basé sur les réponses)
        # Le code secret est le hash des bonnes réponses - jamais présent dans le HTML initial
        correct_answers = [q['answer'] for q in quiz]
        secret_hash = hash_quiz_answers(correct_answers)
        logger.info(f"✅ Hash des réponses calculé (code secret basé sur {len(correct_answers)} réponses)")
        
        # 5. Génération du HTML (sans code secret en clair)
        commit_url = get_commit_url()
        html_content = generate_html(quiz, correct_answers, commit_url)
        
        # 6. Sauvegarde des fichiers
        try:
            # Sauvegarde HTML
            with open("quiz_report.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info("✅ Fichier HTML sauvegardé : quiz_report.html")
            
            # Sauvegarde du hash attendu (le code secret sera calculé côté client après validation)
            with open("quiz.env", "w", encoding="utf-8") as f:
                f.write(f"EXPECTED_SECRET_HASH={secret_hash}\n")
            logger.info("✅ Hash attendu sauvegardé : quiz.env")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde des fichiers : {e}")
            return 1
        
        logger.info("✅ Quiz généré avec succès.")
        logger.info("👉 Ouvrez l'artifact 'quiz_report.html' pour répondre aux questions.")
        
        return 0
        
    except DiffQuizError as e:
        logger.error(f"❌ Erreur DiffQuiz : {e}")
        return 1
    except Exception as e:
        logger.error(f"❌ Erreur inattendue : {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())


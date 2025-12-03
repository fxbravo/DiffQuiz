# Changelog

## [1.0.0] - 2025-01-27

### 🔒 Sécurité
- ✅ Validation obligatoire de `LLM_API_KEY` avec erreur explicite si manquante
- ✅ Amélioration de la gestion SSL avec support des certificats CA locaux
- ✅ Hash avec salt pour les codes secrets (fonction `hash_secret_with_salt`)
- ✅ Validation du schéma JSON des réponses LLM avec `validate_quiz_schema`
- ✅ Comparaison constante des hashs pour éviter les attaques par timing

### 🏗️ Architecture
- ✅ Refactorisation complète en modules séparés :
  - `diffquiz/config.py` : Configuration centralisée avec pydantic
  - `diffquiz/git_utils.py` : Utilitaires Git
  - `diffquiz/llm_client.py` : Client API LLM
  - `diffquiz/quiz_generator.py` : Génération et validation des quiz
  - `diffquiz/html_generator.py` : Génération HTML
  - `diffquiz/security.py` : Fonctions de sécurité
  - `diffquiz/exceptions.py` : Exceptions personnalisées
- ✅ Renommage de `generate_quiz 1.py` → `generate_quiz.py`

### 📝 Qualité de Code
- ✅ Ajout de type hints sur toutes les fonctions
- ✅ Remplacement de `print()` par `logging` structuré
- ✅ Extraction des constantes magiques dans la configuration
- ✅ Gestion d'erreurs améliorée avec exceptions personnalisées
- ✅ Documentation avec docstrings

### 🧪 Tests
- ✅ Création de tests unitaires de base :
  - `tests/test_security.py` : Tests de sécurité
  - `tests/test_git_utils.py` : Tests des utilitaires Git
  - `tests/test_quiz_generator.py` : Tests de génération de quiz
- ✅ Configuration pytest avec couverture de code

### 📦 Dépendances
- ✅ Ajout de `requirements.txt` avec pydantic et pytest
- ✅ Mise à jour des fichiers CI/CD pour utiliser `requirements.txt`

### 🔧 CI/CD
- ✅ Mise à jour de `.github/workflows/test.pipeline.yml` pour le nouveau chemin
- ✅ Mise à jour de `.gitlab-ci.yml` pour le nouveau chemin
- ✅ Installation des dépendances depuis `requirements.txt`

### 📚 Documentation
- ✅ Création de `CHANGELOG.md`
- ✅ Documentation des modules avec docstrings

### ⚠️ Breaking Changes
- Le fichier `generate_quiz 1.py` a été renommé en `generate_quiz.py`
- La variable d'environnement `LLM_API_KEY` est maintenant obligatoire (erreur si manquante)
- Nouvelle structure modulaire : le code est maintenant dans le package `diffquiz/`

### 🔄 Migration
Pour migrer depuis l'ancienne version :
1. Renommer les références à `generate_quiz 1.py` → `generate_quiz.py`
2. Installer les dépendances : `pip install -r requirements.txt`
3. S'assurer que `LLM_API_KEY` est définie dans les variables d'environnement
4. Mettre à jour les scripts CI/CD si nécessaire



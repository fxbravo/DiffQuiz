# DiffQuiz

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/fxbravo/DiffQuiz/test.pipeline.yml?branch=main&label=CI)](https://github.com/fxbravo/DiffQuiz/actions)
[![GitHub Stars](https://img.shields.io/github/stars/fxbravo/DiffQuiz?style=social)](https://github.com/fxbravo/DiffQuiz)

**🎯 Générateur de quiz IA qui bloque les pipelines CI/CD jusqu'à ce que les développeurs prouvent qu'ils comprennent leur code**

🌍 **[Read in English](README.md)**

Système de quiz automatisé pour valider les connaissances des développeurs juniors avant de merger leur code en production.

## 🎬 Comment ça fonctionne ?

### Flux complet du pipeline

1. **Push du code** → Le pipeline se déclenche automatiquement
2. **Génération du quiz** → Un quiz est généré basé sur les modifications (git diff)
3. **Pipeline bloqué** ⏸️ → Le pipeline s'arrête et attend la validation
4. **Répondre au quiz** → Le développeur répond au QCM en ligne
5. **Obtenir le code secret** → Code affiché uniquement après avoir répondu correctement
6. **Valider le quiz** → Le développeur saisit le code secret pour débloquer
7. **Pipeline continue** ✅ → Les tests et le déploiement peuvent s'exécuter

### Support multi-plateforme

DiffQuiz fonctionne avec **GitHub** et **GitLab**. Choisissez la plateforme qui vous convient :

- **GitHub** : Utilisez `.github/workflows/test.pipeline.yml`
- **GitLab** : Utilisez `.gitlab-ci.yml`

Le fichier Python `generate_quiz.py` fonctionne avec les deux plateformes sans modification.

## 🎯 Objectif

DiffQuiz génère automatiquement des quiz techniques basés sur les modifications de code (git diff) pour :
- ✅ Tester la compréhension réelle du code modifié
- 🔒 Détecter les risques de sécurité (injection SQL, commandes dangereuses, etc.)
- 📚 Améliorer les compétences des développeurs juniors
- 🛡️ Protéger la production contre le code malveillant ou dangereux

## 🚀 Fonctionnalités

### Génération automatique de quiz
- Analyse du git diff pour générer des questions pertinentes
- Détection automatique des risques de sécurité
- Adaptation du nombre de questions selon la taille des modifications
- Support multi-langages (détection automatique)

### Interface utilisateur moderne
- 📊 Barre de progression en temps réel
- ✅ Validation question par question avec feedback immédiat
- 💾 Sauvegarde automatique des réponses (localStorage)
- 🌙 Mode sombre/clair
- 🎉 Animations de succès
- 📋 Bouton copier le code secret

### Sécurité renforcée
- **Code secret basé sur les réponses** : Le code secret est calculé à partir du hash des réponses correctes
- **Aucun code secret dans le HTML initial** : Le code secret n'est jamais présent dans le code source HTML
- **Validation côté serveur** : Le hash est calculé côté client uniquement après validation des réponses
- **Hash SHA256** : Utilisation d'un salt fixe pour compatibilité CI/CD
- Détection exhaustive des vulnérabilités

### Intégration CI/CD
- **GitHub** : Déploiement automatique sur GitHub Pages
- **GitLab** : Déploiement automatique sur GitLab Pages
- Organisation par branche
- URL publique pour chaque quiz
- Lien direct vers le commit modifié

## 📋 Prérequis

- Python 3.11+
- Compte GitHub ou GitLab avec CI/CD activé
- Clé API OpenAI (ou serveur Ollama)
- Repository configuré

## 🔧 Installation

### Étape 1 : Cloner le repository

```bash
git clone https://github.com/fxbravo/DiffQuiz.git
cd DiffQuiz
```

### Étape 2 : Choisir votre plateforme

Le repository contient les fichiers pour **GitHub** et **GitLab**. Supprimez celui que vous n'utilisez pas :

**Pour GitHub :**
- ✅ Gardez `.github/workflows/test.pipeline.yml`
- ❌ Supprimez `gitlab-ci.yml`

**Pour GitLab :**
- ✅ Gardez `gitlab-ci.yml`
- ❌ Supprimez `.github/workflows/test.pipeline.yml`

### Étape 3 : Installer les dépendances Python

```bash
pip install -r requirements.txt
```

Les dépendances incluent :
- `pydantic` et `pydantic-settings` : Configuration et validation
- `pytest` et `pytest-cov` : Tests unitaires (optionnel pour l'utilisation)

### Étape 4 : Configuration GitHub

1. **Configurer les secrets** :
   - Allez dans **Settings** → **Secrets and variables** → **Actions**
   - Ajoutez le secret `OPENAI_API_KEY` avec votre clé API OpenAI

2. **Configurer GitHub Pages** :
   - Allez dans **Settings** → **Pages**
   - Source : branche `gh-pages`
   - Dossier : `/ (root)`

3. **Configurer les permissions** :
   - Allez dans **Settings** → **Actions** → **General**
   - **Workflow permissions** : Sélectionnez "Read and write permissions"

### Étape 5 : Configuration GitLab

1. **Configurer les variables CI/CD** :
   - Allez dans **Settings** → **CI/CD** → **Variables**
   - Ajoutez la variable `OPENAI_API_KEY` avec votre clé API OpenAI
   - Cochez "Mask variable" et "Protect variable" si nécessaire

2. **Configurer GitLab Pages** :
   - Le job `pages` dans `gitlab-ci.yml` déploie automatiquement
   - L'URL sera : `https://[group].gitlab.io/[project]/`
   - Vérifiez dans **Settings** → **Pages** que c'est activé

## 🎮 Utilisation

### Flux complet illustré

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Push du code                                             │
│    ↓                                                        │
│ 2. Génération du quiz (job: generate-quiz)                  │
│    • Analyse du git diff                                    │
│    • Génération des questions par IA                        │
│    • Déploiement sur Pages                                  │
│    ↓                                                        │
│ 3. ⏸️ PIPELINE BLOQUÉ                                       │
│    • Le pipeline s'arrête ici                               │
│    • URL du quiz affichée dans les logs                     │
│    ↓                                                        │
│ 4. Répondre au quiz                                         │
│    • Ouvrir l'URL du quiz                                   │
│    • Répondre aux questions                                 │
│    • Code secret calculé automatiquement après validation   │
│    ↓                                                        │
│ 5. Valider le quiz (job: validate-quiz)                     │
│    • Copier le code secret affiché                          │
│    • Saisir le code secret                                  │
│    • Validation côté serveur (hash comparé)                 │
│    ↓                                                        │
│ 6. ✅ Pipeline continue                                     │
│    • Tests s'exécutent (job: run-tests)                     │
│    • Déploiement peut continuer                             │
└─────────────────────────────────────────────────────────────┘
```

### Utilisation sur GitHub

#### Workflow automatique

1. **Push du code** : Le workflow se déclenche automatiquement sur chaque push vers `main`
2. **Génération du quiz** : Un quiz est généré basé sur les modifications
3. **Accès au quiz** : L'URL est affichée dans les logs du workflow
4. **Répondre au quiz** : Ouvrez l'URL et répondez aux questions
5. **Validation** : Copiez le code secret et validez via "Run workflow"

#### Validation manuelle

1. Allez dans **Actions** → **Test DiffQuiz Pipeline**
2. Cliquez sur **"Run workflow"**
3. Saisissez le code secret obtenu après avoir répondu au quiz dans le champ `quiz_secret`
4. Cliquez sur **"Run workflow"** pour valider
5. Le pipeline continue avec les tests

### Utilisation sur GitLab

#### Workflow automatique

1. **Push du code** : Le pipeline se déclenche automatiquement
2. **Génération du quiz** : Le job `generate-quiz` génère le quiz
3. **Accès au quiz** : L'URL est affichée dans les logs du job
4. **Répondre au quiz** : Ouvrez l'URL et répondez aux questions
5. **Validation** : Copiez le code secret et validez via le job manuel

#### Validation manuelle

1. Allez dans **CI/CD** → **Pipelines**
2. Trouvez le pipeline en attente (icône pause ⏸️)
3. Cliquez sur le job **"validate-quiz"** → **"Play"**
4. Dans la popup, ajoutez la variable :
   - **Key** : `QUIZ_SECRET`
   - **Value** : Le code secret obtenu après avoir répondu au quiz
5. Cliquez sur **"Run job"** pour valider
6. Le pipeline continue avec les tests

## 📁 Structure du projet

```
DiffQuiz/
├── generate_quiz.py       # Script principal de génération de quiz
├── diffquiz/              # Package Python modulaire
│   ├── __init__.py        # Initialisation du package
│   ├── config.py          # Configuration centralisée
│   ├── exceptions.py      # Exceptions personnalisées
│   ├── git_utils.py       # Utilitaires Git
│   ├── html_generator.py  # Génération HTML
│   ├── llm_client.py      # Client API LLM
│   ├── quiz_generator.py  # Génération de quiz
│   └── security.py        # Fonctions de sécurité
├── tests/                 # Tests unitaires
│   ├── __init__.py
│   ├── test_git_utils.py
│   ├── test_quiz_generator.py
│   └── test_security.py
├── .github/
│   ├── TROUBLESHOOTING_PAGES.md  # Guide dépannage GitHub Pages
│   └── workflows/
│       └── test.pipeline.yml     # Workflow GitHub Actions
├── gitlab-ci.yml          # Workflow GitLab CI/CD (template)
├── requirements.txt       # Dépendances Python
├── pytest.ini             # Configuration pytest
├── test-QCM.py            # Fichier de démonstration (vulnérabilités)
├── CHANGELOG.md           # Historique des versions
├── LICENSE                # Licence MIT
└── README.md              # Documentation
```

**Important** : Supprimez le fichier de workflow de la plateforme que vous n'utilisez pas :
- **GitHub** : Supprimez `gitlab-ci.yml`
- **GitLab** : Supprimez `.github/workflows/test.pipeline.yml`

## 🔍 Détection de sécurité

DiffQuiz détecte automatiquement :

- ⚠️ **Commandes shell dangereuses** : `rm -rf`, `rm -f`, `del /f`, etc.
- ⚠️ **Opérations DB destructives** : `DROP TABLE`, `DELETE FROM`, `TRUNCATE`
- ⚠️ **Injections SQL** : Requêtes non préparées, concaténation de strings
- ⚠️ **XSS** : Sortie HTML non échappée
- ⚠️ **Path traversal** : `../` dans les chemins de fichiers
- ⚠️ **Secrets hardcodés** : Mots de passe, clés API en clair
- ⚠️ **Commandes système** : `Runtime.exec()`, `ProcessBuilder`
- ⚠️ **Désérialisation non sécurisée**
- ⚠️ **Logs de données sensibles**
- ⚠️ **Et bien plus...**

## 🎨 Fonctionnalités UI/UX

### Mode sombre
- Toggle en haut à droite de la page
- Préférence sauvegardée dans le navigateur

### Sauvegarde automatique
- Les réponses sont sauvegardées automatiquement
- Reprise possible après fermeture de la page

### Validation immédiate
- Feedback instantané après chaque réponse
- Indicateurs visuels (vert = correct, rouge = incorrect)
- Explications affichées automatiquement

### Barre de progression
- Compteur "Question X / Y"
- Barre de progression visuelle
- Mise à jour en temps réel

## 🔐 Sécurité

### Protection contre la triche
- **Code secret basé sur les réponses** : Le code secret est le hash SHA256 des réponses correctes du quiz
- **Aucun code secret dans le HTML initial** : Le code secret n'est jamais présent dans le code source HTML, même en inspectant le fichier
- **Calcul dynamique côté client** : Le code secret est calculé uniquement après avoir répondu correctement à toutes les questions
- **Validation côté serveur** : Le hash calculé côté client est comparé avec le hash attendu stocké dans `quiz.env`
- **Salt fixe** : Utilisation d'un salt fixe (`DIFFQUIZ_SALT_2025`) pour garantir la compatibilité avec les workflows CI/CD

### Fonctionnement de la sécurité
1. **Génération** : Le hash des réponses correctes est calculé côté serveur et stocké dans `quiz.env`
2. **HTML généré** : Le HTML ne contient que les questions et les réponses correctes (pour validation), mais **pas le code secret**
3. **Validation côté client** : Après avoir répondu correctement, le JavaScript calcule le hash des réponses et l'affiche comme code secret
4. **Validation CI/CD** : Le code secret saisi est hashé et comparé avec le hash attendu dans `quiz.env`

### Avantages de cette approche
- ✅ Impossible d'extraire le code secret depuis le code source HTML
- ✅ Le code secret n'existe qu'après validation complète des réponses
- ✅ Même en téléchargeant l'artifact HTML, le code secret reste inaccessible
- ✅ Validation côté serveur garantit l'intégrité du processus

## 📊 Organisation des quiz

Les quiz sont organisés par branche et accessibles via Pages :

### GitHub Pages
```
https://[username].github.io/[repo]/branches/[branch-name]/quiz/[run_id]/
```

### GitLab Pages
```
https://[group].gitlab.io/[project]/branches/[branch-name]/quiz/[pipeline_id]/
```

Exemples :
- Branche `main` : `/branches/main/quiz/[id]/`
- Branche `feature/login` : `/branches/feature-login/quiz/[id]/`

## 🛠️ Configuration

### Variables d'environnement

- `LLM_API_KEY` : Clé API OpenAI (requis)
- `LLM_API_URL` : URL de l'API (défaut: OpenAI)
- `LLM_MODEL` : Modèle à utiliser (défaut: gpt-4o-mini)
- `SSL_VERIFY` : Vérification SSL (défaut: True)

### Personnalisation du prompt

Le prompt de génération peut être modifié dans `diffquiz/quiz_generator.py` :
- Détection de risques de sécurité
- Types de questions à générer
- Niveau de difficulté
- Langages supportés

## 🐛 Dépannage

### Le workflow/pipeline échoue
- **GitHub** : Vérifiez que `OPENAI_API_KEY` est configuré dans Settings → Secrets
- **GitLab** : Vérifiez que `OPENAI_API_KEY` est configuré dans Settings → CI/CD → Variables
- Vérifiez les logs du workflow/pipeline pour les erreurs
- Assurez-vous que Pages est configuré correctement

### Le quiz ne s'affiche pas
- **GitHub** : Vérifiez que GitHub Pages est activé (Settings → Pages)
- **GitLab** : Vérifiez que GitLab Pages est activé (le job `pages` doit s'exécuter)
- Attendez quelques minutes pour la propagation
- Vérifiez l'URL dans les logs du workflow/pipeline

### Erreur 404 sur Pages
- **GitHub** : Vérifiez que la branche `gh-pages` existe et que Pages pointe vers cette branche
- **GitLab** : Vérifiez que le job `pages` s'est exécuté avec succès
- Vérifiez que le déploiement a réussi dans les logs

### Le pipeline ne se bloque pas
- **GitHub** : Vérifiez que le job `validate-quiz` a `if: github.event_name == 'workflow_dispatch'`
- **GitLab** : Vérifiez que le job `validate-quiz` a `when: manual` et `allow_failure: false`
- Le pipeline doit s'arrêter après `generate-quiz` et attendre la validation manuelle

### Les tests ne s'exécutent pas après validation
- Vérifiez que le job de tests dépend du job `validate-quiz` (via `needs:`)
- Vérifiez que la validation a réussi (code secret correct)
- Les tests ne doivent s'exécuter que si le quiz est validé

## 🏗️ Qualité du Code

DiffQuiz suit les principes de développement logiciel modernes :

- ✅ **SOLID** : Architecture modulaire avec responsabilités claires
- ✅ **Clean Code** : Code lisible, documenté et maintenable
- ✅ **KISS** : Simplicité et clarté avant tout
- ✅ **DRY** : Pas de duplication de code
- ✅ **YAGNI** : Pas de fonctionnalités inutiles

## 📝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ouvrir une issue pour signaler un bug
- Proposer de nouvelles fonctionnalités
- Soumettre une pull request

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## 🙏 Remerciements

Un grand merci à Titi <3

DiffQuiz est conçu pour améliorer la qualité du code et la sécurité des applications en formant les développeurs juniors de manière interactive et engageante.

---

**🎯 DiffQuiz : Answer questions before Production !**

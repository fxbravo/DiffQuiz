# DiffQuiz

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/fxbravo/DiffQuiz/test.pipeline.yml?branch=main&label=CI)](https://github.com/fxbravo/DiffQuiz/actions)
[![GitHub Stars](https://img.shields.io/github/stars/fxbravo/DiffQuiz?style=social)](https://github.com/fxbravo/DiffQuiz)

**🎯 AI-powered code quiz generator that blocks CI/CD pipelines until developers prove they understand their code**

🌍 **[Lire en Français](README_FR.md)**

An automated quiz system to validate junior developers' knowledge before merging their code to production.

## 🎬 How Does It Work?

### Complete Pipeline Flow

1. **Push code** → Pipeline triggers automatically
2. **Quiz generation** → A quiz is generated based on code changes (git diff)
3. **Pipeline blocked** ⏸️ → Pipeline stops and waits for validation
4. **Answer the quiz** → Developer answers the online MCQ
5. **Get the secret code** → Code displayed only after answering correctly
6. **Validate quiz** → Developer enters the secret code to unblock
7. **Pipeline continues** ✅ → Tests and deployment can proceed

### Multi-Platform Support

DiffQuiz works with both **GitHub** and **GitLab**. Choose your platform:

- **GitHub**: Use `.github/workflows/test.pipeline.yml`
- **GitLab**: Use `.gitlab-ci.yml`

The `generate_quiz.py` Python file works with both platforms without modification.

## 🎯 Objective

DiffQuiz automatically generates technical quizzes based on code changes (git diff) to:
- ✅ Test actual understanding of modified code
- 🔒 Detect security risks (SQL injection, dangerous commands, etc.)
- 📚 Improve junior developers' skills
- 🛡️ Protect production from malicious or dangerous code

## 🚀 Features

### Automatic Quiz Generation
- Git diff analysis to generate relevant questions
- Automatic security risk detection
- Question count adapts to modification size
- Multi-language support (automatic detection)

### Modern User Interface
- 📊 Real-time progress bar
- ✅ Question-by-question validation with instant feedback
- 💾 Automatic answer saving (localStorage)
- 🌙 Dark/light mode
- 🎉 Success animations
- 📋 Copy secret code button

### Enhanced Security
- **Answer-based secret code**: Secret code is calculated from the hash of correct answers
- **No secret code in initial HTML**: Secret code is never present in HTML source code
- **Server-side validation**: Hash is calculated client-side only after answer validation
- **SHA256 hash**: Uses a fixed salt for CI/CD compatibility
- Exhaustive vulnerability detection

### CI/CD Integration
- **GitHub**: Automatic deployment on GitHub Pages
- **GitLab**: Automatic deployment on GitLab Pages
- Branch-based organization
- Public URL for each quiz
- Direct link to modified commit

## 📋 Prerequisites

- Python 3.11+
- GitHub or GitLab account with CI/CD enabled
- OpenAI API key (or Ollama server)
- Configured repository

## 🔧 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/fxbravo/DiffQuiz.git
cd DiffQuiz
```

### Step 2: Choose Your Platform

The repository contains files for both **GitHub** and **GitLab**. Delete the one you don't use:

**For GitHub:**
- ✅ Keep `.github/workflows/test.pipeline.yml`
- ❌ Delete `gitlab-ci.yml`

**For GitLab:**
- ✅ Keep `gitlab-ci.yml`
- ❌ Delete `.github/workflows/test.pipeline.yml`

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Dependencies include:
- `pydantic` and `pydantic-settings`: Configuration and validation
- `pytest` and `pytest-cov`: Unit tests (optional for usage)

### Step 4: GitHub Configuration

1. **Configure secrets**:
   - Go to **Settings** → **Secrets and variables** → **Actions**
   - Add `OPENAI_API_KEY` secret with your OpenAI API key

2. **Configure GitHub Pages**:
   - Go to **Settings** → **Pages**
   - Source: `gh-pages` branch
   - Folder: `/ (root)`

3. **Configure permissions**:
   - Go to **Settings** → **Actions** → **General**
   - **Workflow permissions**: Select "Read and write permissions"

### Step 5: GitLab Configuration

1. **Configure CI/CD variables**:
   - Go to **Settings** → **CI/CD** → **Variables**
   - Add `OPENAI_API_KEY` variable with your OpenAI API key
   - Check "Mask variable" and "Protect variable" if needed

2. **Configure GitLab Pages**:
   - The `pages` job in `gitlab-ci.yml` deploys automatically
   - URL will be: `https://[group].gitlab.io/[project]/`
   - Check in **Settings** → **Pages** that it's enabled

## 🎮 Usage

### Illustrated Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Push code                                                │
│    ↓                                                        │
│ 2. Quiz generation (job: generate-quiz)                     │
│    • Git diff analysis                                      │
│    • AI-powered question generation                         │
│    • Pages deployment                                       │
│    ↓                                                        │
│ 3. ⏸️ PIPELINE BLOCKED                                      │
│    • Pipeline stops here                                    │
│    • Quiz URL displayed in logs                             │
│    ↓                                                        │
│ 4. Answer the quiz                                          │
│    • Open quiz URL                                          │
│    • Answer questions                                       │
│    • Secret code calculated automatically after validation  │
│    ↓                                                        │
│ 5. Validate quiz (job: validate-quiz)                       │
│    • Copy displayed secret code                             │
│    • Enter secret code                                      │
│    • Server-side validation (hash comparison)               │
│    ↓                                                        │
│ 6. ✅ Pipeline continues                                    │
│    • Tests run (job: run-tests)                             │
│    • Deployment can continue                                │
└─────────────────────────────────────────────────────────────┘
```

### GitHub Usage

#### Automatic Workflow

1. **Push code**: Workflow triggers automatically on each push to `main`
2. **Quiz generation**: A quiz is generated based on modifications
3. **Quiz access**: URL is displayed in workflow logs
4. **Answer quiz**: Open URL and answer questions
5. **Validation**: Copy secret code and validate via "Run workflow"

#### Manual Validation

1. Go to **Actions** → **Test DiffQuiz Pipeline**
2. Click **"Run workflow"**
3. Enter the secret code obtained after answering the quiz in `quiz_secret` field
4. Click **"Run workflow"** to validate
5. Pipeline continues with tests

### GitLab Usage

#### Automatic Workflow

1. **Push code**: Pipeline triggers automatically
2. **Quiz generation**: `generate-quiz` job generates the quiz
3. **Quiz access**: URL is displayed in job logs
4. **Answer quiz**: Open URL and answer questions
5. **Validation**: Copy secret code and validate via manual job

#### Manual Validation

1. Go to **CI/CD** → **Pipelines**
2. Find the waiting pipeline (pause icon ⏸️)
3. Click on **"validate-quiz"** job → **"Play"**
4. In the popup, add the variable:
   - **Key**: `QUIZ_SECRET`
   - **Value**: Secret code obtained after answering the quiz
5. Click **"Run job"** to validate
6. Pipeline continues with tests

## 📁 Project Structure

```
DiffQuiz/
├── generate_quiz.py       # Main quiz generation script
├── diffquiz/              # Modular Python package
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Centralized configuration
│   ├── exceptions.py      # Custom exceptions
│   ├── git_utils.py       # Git utilities
│   ├── html_generator.py  # HTML generation
│   ├── llm_client.py      # LLM API client
│   ├── quiz_generator.py  # Quiz generation
│   └── security.py        # Security functions
├── tests/                 # Unit tests
│   ├── __init__.py
│   ├── test_git_utils.py
│   ├── test_quiz_generator.py
│   └── test_security.py
├── .github/
│   ├── TROUBLESHOOTING_PAGES.md  # GitHub Pages troubleshooting guide
│   └── workflows/
│       └── test.pipeline.yml     # GitHub Actions workflow
├── gitlab-ci.yml          # GitLab CI/CD workflow (template)
├── requirements.txt       # Python dependencies
├── pytest.ini             # pytest configuration
├── test-QCM.py            # Demo file (vulnerabilities)
├── CHANGELOG.md           # Version history
├── LICENSE                # MIT License
└── README.md              # Documentation
```

**Important**: Delete the workflow file for the platform you don't use:
- **GitHub**: Delete `gitlab-ci.yml`
- **GitLab**: Delete `.github/workflows/test.pipeline.yml`

## 🔍 Security Detection

DiffQuiz automatically detects:

- ⚠️ **Dangerous shell commands**: `rm -rf`, `rm -f`, `del /f`, etc.
- ⚠️ **Destructive DB operations**: `DROP TABLE`, `DELETE FROM`, `TRUNCATE`
- ⚠️ **SQL injections**: Unprepared queries, string concatenation
- ⚠️ **XSS**: Unescaped HTML output
- ⚠️ **Path traversal**: `../` in file paths
- ⚠️ **Hardcoded secrets**: Passwords, API keys in plain text
- ⚠️ **System commands**: `Runtime.exec()`, `ProcessBuilder`
- ⚠️ **Insecure deserialization**
- ⚠️ **Sensitive data logging**
- ⚠️ **And much more...**

## 🎨 UI/UX Features

### Dark Mode
- Toggle in top right corner
- Preference saved in browser

### Automatic Saving
- Answers are saved automatically
- Resume possible after closing page

### Instant Validation
- Instant feedback after each answer
- Visual indicators (green = correct, red = incorrect)
- Explanations displayed automatically

### Progress Bar
- "Question X / Y" counter
- Visual progress bar
- Real-time updates

## 🔐 Security

### Anti-Cheating Protection
- **Answer-based secret code**: Secret code is the SHA256 hash of correct quiz answers
- **No secret code in initial HTML**: Secret code is never present in HTML source, even when inspecting the file
- **Dynamic client-side calculation**: Secret code is calculated only after correctly answering all questions
- **Server-side validation**: Client-side calculated hash is compared with expected hash stored in `quiz.env`
- **Fixed salt**: Uses a fixed salt (`DIFFQUIZ_SALT_2025`) to ensure CI/CD workflow compatibility

### Security Workflow
1. **Generation**: Correct answers hash is calculated server-side and stored in `quiz.env`
2. **Generated HTML**: HTML contains only questions and correct answers (for validation), but **not the secret code**
3. **Client-side validation**: After answering correctly, JavaScript calculates the hash and displays it as secret code
4. **CI/CD validation**: Entered secret code is hashed and compared with expected hash in `quiz.env`

### Advantages of This Approach
- ✅ Impossible to extract secret code from HTML source
- ✅ Secret code only exists after complete answer validation
- ✅ Even when downloading HTML artifact, secret code remains inaccessible
- ✅ Server-side validation guarantees process integrity

## 📊 Quiz Organization

Quizzes are organized by branch and accessible via Pages:

### GitHub Pages
```
https://[username].github.io/[repo]/branches/[branch-name]/quiz/[run_id]/
```

### GitLab Pages
```
https://[group].gitlab.io/[project]/branches/[branch-name]/quiz/[pipeline_id]/
```

Examples:
- `main` branch: `/branches/main/quiz/[id]/`
- `feature/login` branch: `/branches/feature-login/quiz/[id]/`

## 🛠️ Configuration

### Environment Variables

- `LLM_API_KEY`: OpenAI API key (required)
- `LLM_API_URL`: API URL (default: OpenAI)
- `LLM_MODEL`: Model to use (default: gpt-4o-mini)
- `SSL_VERIFY`: SSL verification (default: True)

### Prompt Customization

The generation prompt can be modified in `diffquiz/quiz_generator.py`:
- Security risk detection
- Question types to generate
- Difficulty level
- Supported languages

## 🐛 Troubleshooting

### Workflow/Pipeline Fails
- **GitHub**: Check that `OPENAI_API_KEY` is configured in Settings → Secrets
- **GitLab**: Check that `OPENAI_API_KEY` is configured in Settings → CI/CD → Variables
- Check workflow/pipeline logs for errors
- Ensure Pages is configured correctly

### Quiz Doesn't Display
- **GitHub**: Check that GitHub Pages is enabled (Settings → Pages)
- **GitLab**: Check that GitLab Pages is enabled (`pages` job must run)
- Wait a few minutes for propagation
- Check URL in workflow/pipeline logs

### 404 Error on Pages
- **GitHub**: Check that `gh-pages` branch exists and Pages points to this branch
- **GitLab**: Check that `pages` job ran successfully
- Check that deployment succeeded in logs

### Pipeline Doesn't Block
- **GitHub**: Check that `validate-quiz` job has `if: github.event_name == 'workflow_dispatch'`
- **GitLab**: Check that `validate-quiz` job has `when: manual` and `allow_failure: false`
- Pipeline should stop after `generate-quiz` and wait for manual validation

### Tests Don't Run After Validation
- Check that test job depends on `validate-quiz` job (via `needs:`)
- Check that validation succeeded (correct secret code)
- Tests should only run if quiz is validated

## 🏗️ Code Quality

DiffQuiz follows modern software development principles:

- ✅ **SOLID**: Modular architecture with clear responsibilities
- ✅ **Clean Code**: Readable, documented, and maintainable code
- ✅ **KISS**: Simplicity and clarity first
- ✅ **DRY**: No code duplication
- ✅ **YAGNI**: No unnecessary features

## 📝 Contributing

Contributions are welcome! Feel free to:
- Open an issue to report a bug
- Propose new features
- Submit a pull request

## 📄 License

MIT License - See LICENSE file for more details.

## 🙏 Acknowledgments

A big thank you to Titi <3

DiffQuiz is designed to improve code quality and application security by training junior developers in an interactive and engaging way.

---

**🎯 DiffQuiz: Answer questions before Production!**

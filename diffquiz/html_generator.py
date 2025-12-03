"""
Génération du fichier HTML interactif pour le quiz.
"""
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def generate_html(quiz_data: List[Dict[str, Any]], correct_answers: List[str], commit_url: Optional[str] = None) -> str:
    """
    Génère le fichier HTML interactif pour le quiz.
    
    Le code secret n'est jamais inclus dans le HTML initial. Il est calculé côté client
    après validation des réponses, garantissant qu'un développeur ne peut pas l'extraire
    sans répondre correctement au quiz.
    
    Args:
        quiz_data: Liste des questions du quiz.
        correct_answers: Liste des réponses correctes (pour calcul du hash côté client).
        commit_url: URL optionnelle vers le commit.
        
    Returns:
        Contenu HTML généré.
    """
    if not quiz_data:
        logger.error("Aucune donnée de quiz fournie")
        return "<h1>Erreur de génération</h1>"
    
    js_answers = json.dumps(correct_answers)
    total_questions = len(quiz_data)
    
    commit_link = ''
    if commit_url:
        commit_link = f'<p class="text-muted"><small>📝 <a href="{commit_url}" target="_blank">Voir les modifications du commit</a></small></p>'
    
    # Générer le HTML des questions
    questions_html = generate_questions_html(quiz_data)
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validation Code Junior</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    {generate_css()}
</head>
<body class="container py-5">
    {generate_theme_toggle()}
    {generate_card_header()}
    <div class="card-body">
        <p class="lead">Le pipeline CI/CD est bloqué. Répondez correctement pour obtenir le code de déblocage.</p>
        {commit_link}
        {generate_progress_bar(total_questions)}
        <hr>
        <form id="quizForm">
            {questions_html}
            <button type="button" class="btn btn-primary btn-lg w-100" onclick="validateQuiz()">Valider mes réponses</button>
        </form>
        {generate_secret_box()}
        <div id="animationContainer" class="success-animation"></div>
    </div>
</div>
{generate_javascript(js_answers, total_questions)}
</body>
</html>"""
    
    return html


def generate_css() -> str:
    """Génère le CSS pour le quiz."""
    return """<style>
    body { background-color: #f4f6f9; }
    .explanation { display: none; margin-top: 10px; font-style: italic; color: #666; }
    .secret-box { display: none; margin-top: 30px; padding: 20px; border: 2px dashed #28a745; background: #e8f5e9; text-align: center; position: relative; }
    
    .progress-container { margin-bottom: 20px; }
    .progress-label { display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: 600; color: #495057; }
    .progress { height: 25px; border-radius: 15px; overflow: hidden; }
    .progress-bar { transition: width 0.3s ease; background: linear-gradient(90deg, #28a745 0%, #20c997 100%); }
    
    @keyframes confetti {
        0% { transform: translateY(0) rotate(0deg); opacity: 1; }
        100% { transform: translateY(-100vh) rotate(720deg); opacity: 0; }
    }
    @keyframes star {
        0%, 100% { transform: scale(1) rotate(0deg); opacity: 1; }
        50% { transform: scale(1.5) rotate(180deg); opacity: 0.8; }
    }
    .confetti {
        position: fixed;
        width: 10px;
        height: 10px;
        background: #ffd700;
        position: absolute;
        animation: confetti 3s ease-out forwards;
        pointer-events: none;
    }
    .star {
        position: absolute;
        font-size: 2rem;
        color: #ffd700;
        animation: star 1s ease-in-out;
        pointer-events: none;
    }
    .success-animation {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
    }
    
    .copy-btn { margin-top: 15px; transition: all 0.3s ease; }
    .copy-btn:hover { transform: scale(1.05); }
    .copy-btn.copied { background-color: #28a745 !important; border-color: #28a745 !important; }
    .secret-code {
        font-size: 2.5rem;
        font-weight: bold;
        letter-spacing: 3px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 15px 0;
    }
    
    body.dark-mode { background-color: #1a1a1a; color: #e0e0e0; }
    body.dark-mode .card { background-color: #2d2d2d; color: #e0e0e0; }
    body.dark-mode .card-header { background-color: #1a1a1a !important; }
    body.dark-mode .list-group-item { background-color: #3d3d3d; color: #e0e0e0; border-color: #555; }
    body.dark-mode .list-group-item:hover { background-color: #4d4d4d; }
    body.dark-mode .alert-info { background-color: #1e3a5f; color: #b3d9ff; border-color: #2a4a7a; }
    .theme-toggle { position: fixed; top: 20px; right: 20px; z-index: 1000; }
    
    .question-validated { border-left: 4px solid #28a745; padding-left: 15px; }
    .question-error { border-left: 4px solid #dc3545; padding-left: 15px; }
</style>"""


def generate_theme_toggle() -> str:
    """Génère le bouton de bascule du thème."""
    return """<button class="btn btn-outline-secondary theme-toggle" id="themeToggle" onclick="toggleDarkMode()" title="Changer le thème">
    🌙
</button>"""


def generate_card_header() -> str:
    """Génère l'en-tête de la carte."""
    return """<div class="card shadow">
    <div class="card-header bg-dark text-white">
        <h2 class="mb-0">🛡️ Contrôle de Connaissance Code</h2>
    </div>"""


def generate_progress_bar(total_questions: int) -> str:
    """Génère la barre de progression."""
    return f"""<div class="progress-container">
    <div class="progress-label">
        <span>📊 Progression</span>
        <span id="progressText">Question 0 / {total_questions}</span>
    </div>
    <div class="progress">
        <div class="progress-bar progress-bar-striped progress-bar-animated" 
             id="progressBar" 
             role="progressbar" 
             style="width: 0%" 
             aria-valuenow="0" 
             aria-valuemin="0" 
             aria-valuemax="100">
        </div>
    </div>
</div>"""


def generate_questions_html(quiz_data: List[Dict[str, Any]]) -> str:
    """Génère le HTML pour toutes les questions."""
    html_parts = []
    for i, q in enumerate(quiz_data):
        html_parts.append(f"""
        <div class="mb-4" id="card-{i}">
            <h5>{i+1}. {q['question']}</h5>
            <div class="list-group">""")
        
        for opt in q['options']:
            val = opt.split(')')[0].strip() if ')' in opt else opt[0]
            html_parts.append(f"""
                <label class="list-group-item list-group-item-action">
                    <input class="form-check-input me-1" type="radio" name="q{i}" value="{val}" onchange="validateQuestion({i})">
                    {opt}
                </label>""")
        
        html_parts.append(f"""
            </div>
            <div id="expl-{i}" class="explanation alert alert-info">{q.get('explanation', '')}</div>
            <div id="feedback-{i}" class="mt-2"></div>
        </div>""")
    
    return ''.join(html_parts)


def generate_secret_box() -> str:
    """
    Génère la boîte du code secret.
    
    Le code secret sera calculé et affiché dynamiquement après validation des réponses.
    """
    return """<div id="secretBox" class="secret-box">
    <h4>✅ Succès !</h4>
    <p>Copiez la valeur <b>QUIZ_SECRET</b> à mettre dans key</p>
    <p>Copiez ce code secret suivant à mettre dans Value:</p>
    <div class="secret-code" id="secretCode"></div>
    <button type="button" class="btn btn-success copy-btn" id="copyBtn" onclick="copySecretCode()">
        📋 Copier le code
    </button>
    <p class="text-muted mt-3">Utilisez-le dans le job suivant (wait-for-quiz-answer) pour valider le merge.</p>
</div>"""


def generate_javascript(js_answers: str, total_questions: int) -> str:
    """Génère le JavaScript pour l'interactivité."""
    return f"""<script>
    const correctAnswers = {js_answers};
    const totalQuestions = {total_questions};
    const STORAGE_KEY = 'quiz_progress_' + window.location.pathname;
    
    document.addEventListener('DOMContentLoaded', function() {{
        const darkMode = localStorage.getItem('darkMode') === 'true';
        if (darkMode) {{
            document.body.classList.add('dark-mode');
            document.getElementById('themeToggle').textContent = '☀️';
        }}
        loadSavedAnswers();
        const radioInputs = document.querySelectorAll('input[type="radio"]');
        radioInputs.forEach(input => {{
            input.addEventListener('change', function() {{
                updateProgress();
                saveAnswers();
            }});
        }});
        updateProgress();
    }});
    
    function toggleDarkMode() {{
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDark);
        document.getElementById('themeToggle').textContent = isDark ? '☀️' : '🌙';
    }}
    
    function saveAnswers() {{
        const answers = {{}};
        correctAnswers.forEach((ans, index) => {{
            const selected = document.querySelector(`input[name="q${{index}}"]:checked`);
            if (selected) {{
                answers[index] = selected.value;
            }}
        }});
        localStorage.setItem(STORAGE_KEY, JSON.stringify(answers));
    }}
    
    function loadSavedAnswers() {{
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {{
            try {{
                const answers = JSON.parse(saved);
                Object.keys(answers).forEach(index => {{
                    const value = answers[index];
                    const input = document.querySelector(`input[name="q${{index}}"][value="${{value}}"]`);
                    if (input) {{
                        input.checked = true;
                    }}
                }});
            }} catch (e) {{
                console.error('Erreur lors du chargement des réponses:', e);
            }}
        }}
    }}
    
    function validateQuestion(index) {{
        const selected = document.querySelector(`input[name="q${{index}}"]:checked`);
        const card = document.getElementById(`card-${{index}}`);
        const expl = document.getElementById(`expl-${{index}}`);
        const feedback = document.getElementById(`feedback-${{index}}`);
        const correctAnswer = correctAnswers[index];
        
        if (!selected) {{
            return;
        }}
        
        card.classList.remove('question-validated', 'question-error');
        card.querySelectorAll('.list-group-item').forEach(el => {{
            el.classList.remove('list-group-item-success', 'list-group-item-danger');
        }});
        
        const userAnswer = selected.value.trim().toUpperCase();
        const isCorrect = userAnswer === correctAnswer.trim().toUpperCase();
        
        if (isCorrect) {{
            selected.parentElement.classList.add('list-group-item-success');
            card.classList.add('question-validated');
            expl.style.display = 'block';
            feedback.innerHTML = '<span class="badge bg-success">✅ Correct</span>';
        }} else {{
            selected.parentElement.classList.add('list-group-item-danger');
            card.classList.add('question-error');
            feedback.innerHTML = '<span class="badge bg-danger">❌ Incorrect</span>';
        }}
        
        saveAnswers();
    }}
    
    function updateProgress() {{
        const answered = document.querySelectorAll('input[type="radio"]:checked').length;
        const percentage = (answered / totalQuestions) * 100;
        document.getElementById('progressBar').style.width = percentage + '%';
        document.getElementById('progressBar').setAttribute('aria-valuenow', percentage);
        document.getElementById('progressText').textContent = `Question ${{answered}} / ${{totalQuestions}}`;
    }}
    
    function copySecretCode() {{
        const secretCode = document.getElementById('secretCode').textContent;
        const copyBtn = document.getElementById('copyBtn');
        
        navigator.clipboard.writeText(secretCode).then(function() {{
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '✅ Copié !';
            copyBtn.classList.add('copied');
            setTimeout(function() {{
                copyBtn.innerHTML = originalText;
                copyBtn.classList.remove('copied');
            }}, 2000);
        }}).catch(function(err) {{
            const textArea = document.createElement('textarea');
            textArea.value = secretCode;
            document.body.appendChild(textArea);
            textArea.select();
            try {{
                document.execCommand('copy');
                copyBtn.innerHTML = '✅ Copié !';
                copyBtn.classList.add('copied');
                setTimeout(function() {{
                    copyBtn.innerHTML = '📋 Copier le code';
                    copyBtn.classList.remove('copied');
                }}, 2000);
            }} catch (err) {{
                alert('Impossible de copier. Code: ' + secretCode);
            }}
            document.body.removeChild(textArea);
        }});
    }}
    
    function createConfetti() {{
        const container = document.getElementById('animationContainer');
        const colors = ['#ffd700', '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b', '#eb4d4b', '#6c5ce7'];
        
        for (let i = 0; i < 50; i++) {{
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.top = '100%';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDelay = Math.random() * 0.5 + 's';
            confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
            container.appendChild(confetti);
            setTimeout(() => confetti.remove(), 5000);
        }}
    }}
    
    function createStars() {{
        const secretBox = document.getElementById('secretBox');
        const starSymbols = ['⭐', '✨', '🌟', '💫'];
        
        for (let i = 0; i < 10; i++) {{
            const star = document.createElement('div');
            star.className = 'star';
            star.textContent = starSymbols[Math.floor(Math.random() * starSymbols.length)];
            star.style.left = Math.random() * 100 + '%';
            star.style.top = Math.random() * 100 + '%';
            star.style.animationDelay = Math.random() * 0.5 + 's';
            secretBox.appendChild(star);
            setTimeout(() => star.remove(), 1000);
        }}
    }}

    // Fonction pour calculer le hash SHA256 (identique à hash_quiz_answers en Python)
    async function hashAnswers(answers) {{
        // Créer une chaîne unique à partir des réponses (triée pour garantir l'ordre)
        const answersString = answers.map(a => String(a).toUpperCase().trim()).sort().join('|');
        
        // Salt fixe (identique à Python)
        const FIXED_SALT = 'DIFFQUIZ_SALT_2025';
        const data = answersString + FIXED_SALT;
        
        // Calculer SHA256
        const encoder = new TextEncoder();
        const dataBuffer = encoder.encode(data);
        const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        
        return hashHex;
    }}

    function validateQuiz() {{
        let unanswered = [];

        correctAnswers.forEach((ans, index) => {{
            const selected = document.querySelector(`input[name="q${{index}}"]:checked`);
            const card = document.getElementById(`card-${{index}}`);
            const expl = document.getElementById(`expl-${{index}}`);

            if (!selected) {{
                unanswered.push(index + 1);
                return;
            }}

            validateQuestion(index);
        }});
        
        updateProgress();

        if (unanswered.length > 0) {{
            alert(`Veuillez répondre aux questions : ${{unanswered.join(', ')}}`);
            return;
        }}

        const allAnsweredCorrectly = correctAnswers.every((ans, index) => {{
            const selected = document.querySelector(`input[name="q${{index}}"]:checked`);
            return selected && selected.value.trim().toUpperCase() === ans.trim().toUpperCase();
        }});

        if (allAnsweredCorrectly) {{
            // Calculer le hash des réponses correctes (code secret)
            hashAnswers(correctAnswers).then(secretHash => {{
                // Afficher le code secret calculé
                document.getElementById('secretCode').textContent = secretHash;
                document.getElementById('secretBox').style.display = 'block';
                localStorage.removeItem(STORAGE_KEY);
                createConfetti();
                createStars();
                window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }});
            }}).catch(err => {{
                console.error('Erreur lors du calcul du hash:', err);
                alert('Erreur lors du calcul du code secret. Veuillez réessayer.');
            }});
        }} else {{
            alert('Certaines réponses sont incorrectes. Vérifiez les questions marquées en rouge.');
        }}
    }}
</script>"""


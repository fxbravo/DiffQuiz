"""
Utilitaires Git pour récupérer les différences de code.
"""
import subprocess
import logging
from typing import Optional
from diffquiz.exceptions import GitDiffError

logger = logging.getLogger(__name__)


def get_git_diff() -> Optional[str]:
    """
    Récupère le diff des changements validés entre le HEAD actuel et le précédent.
    
    Returns:
        Le diff en texte ou None si aucun diff disponible.
        
    Raises:
        GitDiffError: Si git n'est pas disponible ou en cas d'erreur.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD^", "HEAD", "--unified=0"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        diff_text = result.stdout.strip()
        
        if not diff_text:
            logger.warning("Aucun diff trouvé (peut-être le premier commit ?)")
            return None
            
        logger.info(f"Diff récupéré : {len(diff_text)} caractères")
        return diff_text
        
    except subprocess.CalledProcessError as e:
        logger.warning(f"Impossible de récupérer le git diff : {e.stderr}")
        return None
    except FileNotFoundError:
        error_msg = "Git n'est pas installé ou non disponible dans le PATH"
        logger.error(error_msg)
        raise GitDiffError(error_msg)
    except subprocess.TimeoutExpired:
        error_msg = "Timeout lors de la récupération du git diff"
        logger.error(error_msg)
        raise GitDiffError(error_msg)
    except Exception as e:
        error_msg = f"Erreur inattendue lors de la récupération du git diff : {e}"
        logger.error(error_msg)
        raise GitDiffError(error_msg) from e


def calculate_question_count(diff_text: Optional[str], lines_per_question: int = 20, max_questions: int = 5) -> int:
    """
    Calcule le nombre de questions basé sur la taille du diff.
    
    Args:
        diff_text: Le texte du diff.
        lines_per_question: Nombre de lignes modifiées par question.
        max_questions: Nombre maximum de questions.
        
    Returns:
        Le nombre de questions (entre 1 et max_questions).
    """
    if not diff_text:
        return 0
    
    lines = diff_text.splitlines()
    # Compter les lignes ajoutées/supprimées
    changes = sum(1 for line in lines if line.startswith('+') or line.startswith('-'))
    
    if changes == 0:
        return 0
    
    # Calculer le nombre de questions
    count = (changes + lines_per_question - 1) // lines_per_question  # Équivalent à math.ceil
    return max(1, min(max_questions, count))



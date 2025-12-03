"""
Exceptions personnalisées pour DiffQuiz.
"""


class DiffQuizError(Exception):
    """Exception de base pour DiffQuiz."""
    pass


class GitDiffError(DiffQuizError):
    """Erreur lors de la récupération du git diff."""
    pass


class LLMAPIError(DiffQuizError):
    """Erreur lors de l'appel à l'API LLM."""
    pass


class QuizGenerationError(DiffQuizError):
    """Erreur lors de la génération du quiz."""
    pass


class SecurityError(DiffQuizError):
    """Erreur de sécurité."""
    pass


class ValidationError(DiffQuizError):
    """Erreur de validation."""
    pass


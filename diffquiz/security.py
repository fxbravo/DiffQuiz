"""
Fonctions de sécurité : hash, validation, etc.
"""
import secrets
import hashlib
import logging
from typing import Tuple
from diffquiz.exceptions import SecurityError

logger = logging.getLogger(__name__)

# Constante partagée pour le salt fixe (DRY)
FIXED_SALT = "DIFFQUIZ_SALT_2025"


def generate_secret_code(length: int = 6) -> str:
    """
    Génère un code secret aléatoire.
    
    Args:
        length: Longueur du code (par défaut 6).
        
    Returns:
        Code secret généré.
    """
    if length < 4 or length > 20:
        raise SecurityError("La longueur du code secret doit être entre 4 et 20")
    
    return ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(length))


def hash_secret_with_salt(secret: str, salt_length: int = 16) -> Tuple[str, str]:
    """
    Hash un secret avec un salt aléatoire.
    
    Args:
        secret: Le secret à hasher.
        salt_length: Longueur du salt en bytes.
        
    Returns:
        Tuple (hash_hex, salt_hex).
    """
    if not secret:
        raise SecurityError("Le secret ne peut pas être vide")
    
    # Générer un salt aléatoire
    salt = secrets.token_hex(salt_length)
    
    # Hasher le secret avec le salt
    hash_obj = hashlib.sha256((secret + salt).encode('utf-8'))
    secret_hash = hash_obj.hexdigest()
    
    logger.debug(f"Secret hashé avec salt (salt_length={salt_length})")
    return secret_hash, salt


def verify_secret(secret: str, expected_hash: str, salt: str) -> bool:
    """
    Vérifie un secret contre un hash attendu avec salt.
    
    Args:
        secret: Le secret à vérifier.
        expected_hash: Le hash attendu.
        salt: Le salt utilisé pour le hash.
        
    Returns:
        True si le secret correspond, False sinon.
    """
    if not secret or not expected_hash or not salt:
        return False
    
    # Calculer le hash du secret fourni avec le salt
    hash_obj = hashlib.sha256((secret + salt).encode('utf-8'))
    computed_hash = hash_obj.hexdigest()
    
    # Comparaison constante pour éviter les attaques par timing
    return secrets.compare_digest(computed_hash, expected_hash)


def hash_secret_simple(secret: str) -> str:
    """
    Hash simple d'un secret avec salt fixe.
    
    Utilise un salt fixe pour simplifier l'intégration avec les workflows CI/CD.
    C'est suffisant pour un outil de vérification de qualité de code pour développeurs juniors.
    
    Philosophie pragmatique : Si un junior arrive à hacker le système pour obtenir le code
    sans répondre au quiz, c'est qu'il a les compétences techniques qu'on cherche à vérifier !
    
    Args:
        secret: Le secret à hasher.
        
    Returns:
        Hash hexadécimal.
    """
    hash_obj = hashlib.sha256((secret + FIXED_SALT).encode('utf-8'))
    return hash_obj.hexdigest()


def hash_quiz_answers(answers: list) -> str:
    """
    Hash les réponses d'un quiz pour générer un code secret basé sur les bonnes réponses.
    
    Le code secret est le hash des réponses correctes. Cela garantit que :
    - Le code secret n'est jamais présent dans le HTML initial
    - Seules les bonnes réponses permettent d'obtenir le code secret
    - Le hash est calculé côté client après validation des réponses
    
    Args:
        answers: Liste des réponses correctes (ex: ['A', 'B', 'C']).
        
    Returns:
        Hash hexadécimal des réponses.
    """
    if not answers:
        raise SecurityError("Les réponses ne peuvent pas être vides")
    
    # Créer une chaîne unique à partir des réponses (triée pour garantir l'ordre)
    answers_string = '|'.join(sorted(str(a).upper().strip() for a in answers))
    
    # Hasher avec le même salt fixe que hash_secret_simple pour compatibilité CI/CD
    hash_obj = hashlib.sha256((answers_string + FIXED_SALT).encode('utf-8'))
    
    logger.debug(f"Hash des réponses calculé ({len(answers)} réponses)")
    return hash_obj.hexdigest()


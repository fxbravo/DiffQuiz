"""
Tests pour le module security.
"""
import pytest
from diffquiz.security import (
    generate_secret_code,
    hash_secret_with_salt,
    verify_secret,
    hash_secret_simple
)
from diffquiz.exceptions import SecurityError


def test_generate_secret_code_default():
    """Test génération d'un code secret par défaut."""
    code = generate_secret_code()
    assert len(code) == 6
    assert code.isalnum()
    assert code.isupper() or any(c.isdigit() for c in code)


def test_generate_secret_code_custom_length():
    """Test génération d'un code secret avec longueur personnalisée."""
    code = generate_secret_code(10)
    assert len(code) == 10


def test_generate_secret_code_invalid_length():
    """Test génération avec longueur invalide."""
    with pytest.raises(SecurityError):
        generate_secret_code(3)  # Trop court
    
    with pytest.raises(SecurityError):
        generate_secret_code(21)  # Trop long


def test_hash_secret_with_salt():
    """Test hash avec salt."""
    secret = "TEST123"
    hash1, salt1 = hash_secret_with_salt(secret)
    hash2, salt2 = hash_secret_with_salt(secret)
    
    # Les hashs doivent être différents (salt différent)
    assert hash1 != hash2
    assert salt1 != salt2
    
    # Mais la vérification doit fonctionner
    assert verify_secret(secret, hash1, salt1)
    assert verify_secret(secret, hash2, salt2)
    assert not verify_secret("WRONG", hash1, salt1)


def test_hash_secret_simple():
    """Test hash simple (compatibilité)."""
    secret = "TEST123"
    hash1 = hash_secret_simple(secret)
    hash2 = hash_secret_simple(secret)
    
    # Le hash doit être déterministe
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex


def test_verify_secret_edge_cases():
    """Test cas limites de vérification."""
    assert not verify_secret("", "hash", "salt")
    assert not verify_secret("secret", "", "salt")
    assert not verify_secret("secret", "hash", "")



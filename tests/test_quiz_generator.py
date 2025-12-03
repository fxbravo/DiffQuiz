"""
Tests pour le module quiz_generator.
"""
import pytest
import json
from diffquiz.quiz_generator import (
    clean_json_text,
    validate_quiz_schema,
    shuffle_quiz_options
)
from diffquiz.exceptions import ValidationError


def test_clean_json_text_simple():
    """Test nettoyage JSON simple."""
    text = '[{"question": "test"}]'
    assert clean_json_text(text) == text


def test_clean_json_text_with_markdown():
    """Test nettoyage JSON avec markdown."""
    text = '```json\n[{"question": "test"}]\n```'
    result = clean_json_text(text)
    assert result == '[{"question": "test"}]'


def test_clean_json_text_with_text_before():
    """Test nettoyage JSON avec texte avant."""
    text = 'Some text before [{"question": "test"}]'
    result = clean_json_text(text)
    assert result == '[{"question": "test"}]'


def test_validate_quiz_schema_valid():
    """Test validation d'un quiz valide."""
    quiz = [{
        "question": "Test?",
        "options": ["A) Option 1", "B) Option 2"],
        "answer": "A",
        "explanation": "Explanation"
    }]
    validate_quiz_schema(quiz)  # Ne doit pas lever d'exception


def test_validate_quiz_schema_empty():
    """Test validation d'un quiz vide."""
    with pytest.raises(ValidationError):
        validate_quiz_schema([])


def test_validate_quiz_schema_missing_field():
    """Test validation avec champ manquant."""
    quiz = [{
        "question": "Test?",
        "options": ["A) Option 1"],
        # "answer" manquant
    }]
    with pytest.raises(ValidationError):
        validate_quiz_schema(quiz)


def test_validate_quiz_schema_invalid_answer():
    """Test validation avec réponse invalide."""
    quiz = [{
        "question": "Test?",
        "options": ["A) Option 1", "B) Option 2"],
        "answer": "Z",  # Invalide
        "explanation": "Explanation"
    }]
    with pytest.raises(ValidationError):
        validate_quiz_schema(quiz)


def test_shuffle_quiz_options():
    """Test mélange des options."""
    quiz = [{
        "question": "Test?",
        "options": ["A) Option 1", "B) Option 2", "C) Option 3"],
        "answer": "A",
        "explanation": "Explanation"
    }]
    
    shuffled = shuffle_quiz_options(quiz)
    assert len(shuffled) == 1
    assert len(shuffled[0]['options']) == 3
    assert shuffled[0]['answer'] in ['A', 'B', 'C']
    # La bonne réponse doit toujours être correcte après mélange
    answer_letter = shuffled[0]['answer']
    answer_index = ord(answer_letter) - ord('A')
    # Vérifier que l'option correspondante contient "Option 1"
    assert "Option 1" in shuffled[0]['options'][answer_index]



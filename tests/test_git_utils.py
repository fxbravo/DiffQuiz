"""
Tests pour le module git_utils.
"""
import pytest
from diffquiz.git_utils import calculate_question_count


def test_calculate_question_count_empty():
    """Test avec diff vide."""
    assert calculate_question_count(None) == 0
    assert calculate_question_count("") == 0


def test_calculate_question_count_small():
    """Test avec petit diff."""
    diff = "\n".join([f"+line {i}" for i in range(10)])
    assert calculate_question_count(diff) == 1


def test_calculate_question_count_medium():
    """Test avec diff moyen."""
    diff = "\n".join([f"+line {i}" for i in range(50)])
    assert calculate_question_count(diff, lines_per_question=20) == 3


def test_calculate_question_count_max():
    """Test avec diff très grand."""
    diff = "\n".join([f"+line {i}" for i in range(200)])
    assert calculate_question_count(diff, lines_per_question=20, max_questions=5) == 5


def test_calculate_question_count_no_changes():
    """Test avec diff sans changements."""
    diff = "some text without + or -"
    assert calculate_question_count(diff) == 0



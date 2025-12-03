"""
Configuration centralisée avec validation.
"""
import os
import logging
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuration de l'application avec validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Configuration LLM
    llm_api_url: str = Field(
        default="https://api.openai.com/v1/chat/completions",
        description="URL de l'API LLM"
    )
    llm_model: str = Field(
        default="gpt-4o-mini",
        description="Modèle LLM à utiliser"
    )
    llm_api_key: str = Field(
        ...,
        min_length=1,
        description="Clé API LLM (requis)"
    )
    
    # Configuration SSL
    ssl_verify: bool = Field(
        default=True,
        description="Vérifier les certificats SSL"
    )
    ssl_ca_bundle: Optional[str] = Field(
        default=None,
        description="Chemin vers le bundle CA pour serveurs internes"
    )
    
    # Configuration Quiz
    lines_per_question: int = Field(
        default=20,
        ge=1,
        description="Nombre de lignes modifiées par question"
    )
    max_questions: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Nombre maximum de questions"
    )
    max_diff_length: int = Field(
        default=10000,
        ge=1000,
        description="Longueur maximale du diff en caractères"
    )
    
    # Configuration Timeout
    llm_timeout_seconds: int = Field(
        default=300,
        ge=30,
        le=600,
        description="Timeout pour les appels LLM en secondes"
    )
    
    # Configuration Hash
    hash_salt_length: int = Field(
        default=16,
        ge=8,
        le=32,
        description="Longueur du salt pour le hash"
    )
    
    @field_validator('llm_api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Valide que la clé API est fournie."""
        if not v or v.strip() == "":
            raise ValueError("LLM_API_KEY environment variable is required and cannot be empty")
        return v
    
    @field_validator('ssl_verify', mode='before')
    @classmethod
    def parse_ssl_verify(cls, v) -> bool:
        """Parse SSL_VERIFY depuis string."""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 't', 'yes')
        return bool(v)


def get_settings() -> Settings:
    """Récupère la configuration validée."""
    try:
        return Settings()
    except Exception as e:
        logger.error(f"Erreur de configuration : {e}")
        raise


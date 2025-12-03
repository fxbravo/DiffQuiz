"""
Client pour l'API LLM avec gestion d'erreurs améliorée.
"""
import json
import ssl
import urllib.request
import urllib.error
import logging
from typing import Optional, Dict, Any
from diffquiz.config import Settings
from diffquiz.exceptions import LLMAPIError

logger = logging.getLogger(__name__)


def create_ssl_context(settings: Settings) -> ssl.SSLContext:
    """
    Crée un contexte SSL sécurisé.
    
    Args:
        settings: Configuration de l'application.
        
    Returns:
        Contexte SSL configuré.
    """
    ctx = ssl.create_default_context()
    
    # Pour les serveurs internes avec certificat auto-signé
    if settings.ssl_ca_bundle:
        try:
            ctx.load_verify_locations(settings.ssl_ca_bundle)
            logger.info(f"CA bundle chargé depuis {settings.ssl_ca_bundle}")
        except Exception as e:
            logger.warning(f"Impossible de charger le CA bundle : {e}")
    
    # Désactiver SSL uniquement si explicitement demandé ET avec un CA bundle
    # Sinon, toujours vérifier SSL
    if not settings.ssl_verify:
        if not settings.ssl_ca_bundle:
            logger.warning(
                "SSL_VERIFY=False mais aucun SSL_CA_BUNDLE fourni. "
                "C'est dangereux ! Utilisez un certificat CA local."
            )
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        logger.warning("⚠️ SSL verification désactivée - Risque de sécurité")
    else:
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
    
    return ctx


def call_llm_api(
    prompt_system: str,
    prompt_user: str,
    settings: Settings
) -> Optional[str]:
    """
    Appelle l'API LLM pour générer du contenu.
    
    Args:
        prompt_system: Prompt système.
        prompt_user: Prompt utilisateur.
        settings: Configuration de l'application.
        
    Returns:
        Contenu généré ou None en cas d'erreur.
        
    Raises:
        LLMAPIError: En cas d'erreur API.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.llm_api_key}"
    }
    
    # Détection du type d'API
    is_openai = "openai.com" in settings.llm_api_url.lower()
    
    payload: Dict[str, Any] = {
        "model": settings.llm_model,
        "stream": False,
        "messages": [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user}
        ],
        "temperature": 0.2,
    }
    
    # Adaptation du payload selon l'API
    if is_openai:
        payload["max_tokens"] = 4096
    else:
        payload["options"] = {"num_predict": 4096}
    
    # Créer le contexte SSL
    ctx = create_ssl_context(settings)
    
    try:
        logger.info(f"Appel LLM vers : {settings.llm_api_url} (Modèle: {settings.llm_model})")
        
        req = urllib.request.Request(
            settings.llm_api_url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers
        )
        
        with urllib.request.urlopen(
            req,
            context=ctx,
            timeout=settings.llm_timeout_seconds
        ) as response:
            response_text = response.read().decode('utf-8')
            result = json.loads(response_text)
            
            # Extraction du contenu selon le format
            content = ""
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
            elif 'message' in result:
                content = result['message']['content']
            else:
                error_msg = f"Format de réponse API inconnu : {list(result.keys())}"
                logger.error(error_msg)
                raise LLMAPIError(error_msg)
            
            logger.info(f"Réponse LLM reçue : {len(content)} caractères")
            return content
            
    except urllib.error.HTTPError as e:
        error_detail = e.read().decode('utf-8', errors='ignore')
        error_msg = f"Erreur HTTP {e.code}: {e.reason}"
        logger.error(f"{error_msg} - Détail: {error_detail[:200]}")
        raise LLMAPIError(error_msg) from e
    except urllib.error.URLError as e:
        error_msg = f"Erreur de connexion (Réseau/SSL) : {e.reason}"
        logger.error(error_msg)
        raise LLMAPIError(error_msg) from e
    except json.JSONDecodeError as e:
        error_msg = f"Erreur de parsing JSON de la réponse API : {e}"
        logger.error(error_msg)
        raise LLMAPIError(error_msg) from e
    except Exception as e:
        error_msg = f"Erreur inattendue lors de l'appel LLM : {e}"
        logger.error(error_msg, exc_info=True)
        raise LLMAPIError(error_msg) from e



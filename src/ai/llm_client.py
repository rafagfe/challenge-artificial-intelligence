"""
LLM client functions.
"""
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from groq import Groq
from langsmith import Client as LangSmithClient

logger = logging.getLogger(__name__)


def create_groq_client(api_key: Optional[str]) -> Optional[Groq]:
    """
    Create and return a Groq client instance.
    
    Args:
        api_key (Optional[str]): Groq API key
        
    Returns:
        Optional[Groq]: Groq client instance or None if no API key
    """
    if not api_key:
        logger.warning("Groq API key not provided")
        return None
    
    try:
        client = Groq(api_key=api_key)
        logger.info("Groq client created successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create Groq client: {e}")
        return None


def create_openai_client(api_key: Optional[str]) -> Optional[OpenAI]:
    """
    Create and return an OpenAI client instance.
    
    Args:
        api_key (Optional[str]): OpenAI API key
        
    Returns:
        Optional[OpenAI]: OpenAI client instance or None if no API key
    """
    if not api_key:
        logger.warning("OpenAI API key not provided")
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        logger.info("OpenAI client created successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create OpenAI client: {e}")
        return None


def create_langsmith_client(api_key: Optional[str]) -> Optional[LangSmithClient]:
    """
    Create and return a LangSmith client instance.
    
    Args:
        api_key (Optional[str]): LangSmith API key
        
    Returns:
        Optional[LangSmithClient]: LangSmith client instance or None if no API key
    """
    if not api_key:
        logger.warning("LangSmith API key not provided")
        return None
    
    try:
        client = LangSmithClient(api_key=api_key)
        logger.info("LangSmith client created successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create LangSmith client: {e}")
        return None


def create_all_clients(api_keys: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """
    Create all LLM clients based on available API keys.
    
    Args:
        api_keys (Dict[str, Optional[str]]): Dictionary of API keys
        
    Returns:
        Dict[str, Any]: Dictionary of created clients
    """
    clients = {}
    
    clients["groq"] = create_groq_client(api_keys.get("groq_api_key"))
    clients["openai"] = create_openai_client(api_keys.get("openai_api_key"))
    clients["langsmith"] = create_langsmith_client(api_keys.get("langsmith_api_key"))
    
    active_clients = [name for name, client in clients.items() if client is not None]
    logger.info(f"Created {len(active_clients)} active clients: {active_clients}")
    
    return clients 
"""
Configuration functions for the Adaptive Learning System.
"""
import os
from pathlib import Path
from typing import Optional, Dict


def get_api_keys() -> Dict[str, Optional[str]]:
    """Get API keys from environment variables."""
    return {
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "langsmith_api_key": os.getenv("LANGSMITH_API_KEY")
    }


def get_model_settings() -> Dict[str, str]:
    """Get model configuration settings."""
    return {
        "groq_model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "openai_tts_model": os.getenv("OPENAI_TTS_MODEL", "tts-1"),
        "openai_tts_voice": os.getenv("OPENAI_TTS_VOICE", "alloy")
    }


def get_paths() -> Dict[str, Path]:
    """Get all file paths used by the application."""
    project_root = Path(__file__).parent.parent.parent
    files_chat_path = Path("./files_chat")
    
    return {
        "project_root": project_root,
        "resources_path": Path("./resources"),
        "files_chat_path": files_chat_path,
        "chroma_db_path": files_chat_path / "chroma_db",
        "database_path": files_chat_path / "database.db",
        "audio_path": files_chat_path / "audios",
        "video_path": files_chat_path / "videos",
        "states_path": files_chat_path / "states_audio_video"
    }


def get_processing_settings() -> Dict[str, int]:
    """Get processing configuration settings."""
    return {
        "video_chunk_duration": int(os.getenv("VIDEO_CHUNK_DURATION", "25")),
        "max_search_results": int(os.getenv("MAX_SEARCH_RESULTS", "3")),
        "max_tokens_response": int(os.getenv("MAX_TOKENS_RESPONSE", "800")),
        "max_tokens_analysis": int(os.getenv("MAX_TOKENS_ANALYSIS", "300"))
    }


def get_chromadb_settings() -> Dict[str, str]:
    """Get ChromaDB configuration settings."""
    return {
        "collection_name": os.getenv("COLLECTION_NAME", "learning_content")
    }


def get_log_level() -> str:
    """Get logging level."""
    return os.getenv("LOG_LEVEL", "INFO")


def validate_api_keys() -> Dict[str, bool]:
    """Validate and return available API keys."""
    api_keys = get_api_keys()
    return {
        "groq": bool(api_keys["groq_api_key"]),
        "openai": bool(api_keys["openai_api_key"]),
        "langsmith": bool(api_keys["langsmith_api_key"])
    }


def ensure_directories() -> None:
    """Create necessary directories if they don't exist."""
    paths = get_paths()
    directories = [
        paths["files_chat_path"],
        paths["chroma_db_path"],
        paths["audio_path"],
        paths["video_path"],
        paths["states_path"]
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True) 
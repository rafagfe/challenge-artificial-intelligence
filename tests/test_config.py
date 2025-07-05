"""
Tests for configuration module.
"""
import pytest
import os
from unittest.mock import patch
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.settings import (
    get_api_keys,
    get_model_settings,
    get_paths,
    get_processing_settings,
    validate_api_keys,
    ensure_directories
)


class TestConfigSettings:
    """Test configuration functions."""
    
    def test_get_api_keys_no_env(self):
        """Test getting API keys when none are set."""
        with patch.dict(os.environ, {}, clear=True):
            api_keys = get_api_keys()
            
            assert api_keys["groq_api_key"] is None
            assert api_keys["openai_api_key"] is None
            assert api_keys["langsmith_api_key"] is None
    
    def test_get_api_keys_with_env(self):
        """Test getting API keys when environment variables are set."""
        test_keys = {
            "GROQ_API_KEY": "test_groq_key",
            "OPENAI_API_KEY": "test_openai_key",
            "LANGSMITH_API_KEY": "test_langsmith_key"
        }
        
        with patch.dict(os.environ, test_keys):
            api_keys = get_api_keys()
            
            assert api_keys["groq_api_key"] == "test_groq_key"
            assert api_keys["openai_api_key"] == "test_openai_key"
            assert api_keys["langsmith_api_key"] == "test_langsmith_key"
    
    def test_get_model_settings_defaults(self):
        """Test getting model settings with defaults."""
        with patch.dict(os.environ, {}, clear=True):
            settings = get_model_settings()
            
            assert settings["groq_model"] == "llama-3.3-70b-versatile"
            assert settings["openai_tts_model"] == "tts-1"
            assert settings["openai_tts_voice"] == "alloy"
    
    def test_get_model_settings_custom(self):
        """Test getting model settings with custom values."""
        custom_settings = {
            "GROQ_MODEL": "custom-model",
            "OPENAI_TTS_MODEL": "tts-2",
            "OPENAI_TTS_VOICE": "nova"
        }
        
        with patch.dict(os.environ, custom_settings):
            settings = get_model_settings()
            
            assert settings["groq_model"] == "custom-model"
            assert settings["openai_tts_model"] == "tts-2"
            assert settings["openai_tts_voice"] == "nova"
    
    def test_get_paths(self):
        """Test getting file paths."""
        paths = get_paths()
        
        assert isinstance(paths["project_root"], Path)
        assert isinstance(paths["resources_path"], Path)
        assert isinstance(paths["files_chat_path"], Path)
        assert isinstance(paths["chroma_db_path"], Path)
        assert isinstance(paths["database_path"], Path)
        assert isinstance(paths["audio_path"], Path)
        assert isinstance(paths["video_path"], Path)
        assert isinstance(paths["states_path"], Path)
    
    def test_get_processing_settings_defaults(self):
        """Test getting processing settings with defaults."""
        with patch.dict(os.environ, {}, clear=True):
            settings = get_processing_settings()
            
            assert settings["video_chunk_duration"] == 25
            assert settings["max_search_results"] == 3
            assert settings["max_tokens_response"] == 800
            assert settings["max_tokens_analysis"] == 300
    
    def test_validate_api_keys_none(self):
        """Test API key validation when none are available."""
        with patch.dict(os.environ, {}, clear=True):
            validation = validate_api_keys()
            
            assert validation["groq"] is False
            assert validation["openai"] is False
            assert validation["langsmith"] is False
    
    def test_validate_api_keys_available(self):
        """Test API key validation when keys are available."""
        test_keys = {
            "GROQ_API_KEY": "test_key",
            "OPENAI_API_KEY": "test_key"
        }
        
        with patch.dict(os.environ, test_keys, clear=True):
            validation = validate_api_keys()
            
            assert validation["groq"] is True
            assert validation["openai"] is True
            # langsmith should be False because we cleared environment and didn't set LANGSMITH_API_KEY
            assert validation["langsmith"] is False
    
    def test_ensure_directories(self, tmp_path):
        """Test directory creation."""
        # This would require mocking the paths or using a temporary directory
        # For now, just test that the function runs without error
        try:
            ensure_directories()
        except Exception as e:
            pytest.fail(f"ensure_directories() raised {e} unexpectedly") 
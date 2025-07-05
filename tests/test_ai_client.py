"""
Tests for AI client module.
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai.llm_client import (
    create_groq_client,
    create_openai_client,
    create_langsmith_client,
    create_all_clients
)


class TestAIClients:
    """Test AI client creation functions."""
    
    def test_create_groq_client_no_key(self):
        """Test creating Groq client without API key."""
        client = create_groq_client(None)
        assert client is None
    
    def test_create_groq_client_empty_key(self):
        """Test creating Groq client with empty API key."""
        client = create_groq_client("")
        assert client is None
    
    @patch('ai.llm_client.Groq')
    def test_create_groq_client_with_key(self, mock_groq):
        """Test creating Groq client with valid API key."""
        mock_client = Mock()
        mock_groq.return_value = mock_client
        
        client = create_groq_client("test_key")
        
        mock_groq.assert_called_once_with(api_key="test_key")
        assert client == mock_client
    
    @patch('ai.llm_client.Groq')
    def test_create_groq_client_exception(self, mock_groq):
        """Test creating Groq client when exception occurs."""
        mock_groq.side_effect = Exception("API error")
        
        client = create_groq_client("test_key")
        
        assert client is None
    
    def test_create_openai_client_no_key(self):
        """Test creating OpenAI client without API key."""
        client = create_openai_client(None)
        assert client is None
    
    @patch('ai.llm_client.OpenAI')
    def test_create_openai_client_with_key(self, mock_openai):
        """Test creating OpenAI client with valid API key."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        client = create_openai_client("test_key")
        
        mock_openai.assert_called_once_with(api_key="test_key")
        assert client == mock_client
    
    def test_create_langsmith_client_no_key(self):
        """Test creating LangSmith client without API key."""
        client = create_langsmith_client(None)
        assert client is None
    
    @patch('ai.llm_client.LangSmithClient')
    def test_create_langsmith_client_with_key(self, mock_langsmith):
        """Test creating LangSmith client with valid API key."""
        mock_client = Mock()
        mock_langsmith.return_value = mock_client
        
        client = create_langsmith_client("test_key")
        
        mock_langsmith.assert_called_once_with(api_key="test_key")
        assert client == mock_client
    
    @patch('ai.llm_client.create_groq_client')
    @patch('ai.llm_client.create_openai_client')
    @patch('ai.llm_client.create_langsmith_client')
    def test_create_all_clients(self, mock_langsmith, mock_openai, mock_groq):
        """Test creating all clients at once."""
        # Setup mocks
        mock_groq_client = Mock()
        mock_openai_client = Mock()
        mock_langsmith_client = Mock()
        
        mock_groq.return_value = mock_groq_client
        mock_openai.return_value = mock_openai_client
        mock_langsmith.return_value = mock_langsmith_client
        
        api_keys = {
            "groq_api_key": "groq_key",
            "openai_api_key": "openai_key",
            "langsmith_api_key": "langsmith_key"
        }
        
        clients = create_all_clients(api_keys)
        
        # Verify all clients were created
        mock_groq.assert_called_once_with("groq_key")
        mock_openai.assert_called_once_with("openai_key")
        mock_langsmith.assert_called_once_with("langsmith_key")
        
        # Verify return structure
        assert clients["groq"] == mock_groq_client
        assert clients["openai"] == mock_openai_client
        assert clients["langsmith"] == mock_langsmith_client
    
    @patch('ai.llm_client.create_groq_client')
    @patch('ai.llm_client.create_openai_client')
    @patch('ai.llm_client.create_langsmith_client')
    def test_create_all_clients_partial_keys(self, mock_langsmith, mock_openai, mock_groq):
        """Test creating clients with partial API keys."""
        mock_groq.return_value = Mock()
        mock_openai.return_value = None
        mock_langsmith.return_value = None
        
        api_keys = {
            "groq_api_key": "groq_key",
            "openai_api_key": None,
            "langsmith_api_key": None
        }
        
        clients = create_all_clients(api_keys)
        
        assert clients["groq"] is not None
        assert clients["openai"] is None
        assert clients["langsmith"] is None 
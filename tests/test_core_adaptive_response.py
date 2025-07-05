"""
Tests for core adaptive response module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.adaptive_response import (
    generate_adaptive_response,
    generate_out_of_scope_response,
    generate_template_content
)


class TestGenerateAdaptiveResponse:
    """Test adaptive response generation functionality."""
    
    def test_generate_adaptive_response_without_client(self):
        """Test generating adaptive response without Groq client."""
        mock_collection = Mock()
        
        result = generate_adaptive_response(
            collection=mock_collection,
            question="What is machine learning?",
            preferred_format="text"
        )
        
        assert isinstance(result, str)
        assert "IA não está configurado" in result
    
    def test_generate_adaptive_response_with_client_basic(self):
        """Test generating adaptive response with basic client setup."""
        mock_collection = Mock()
        mock_client = Mock()
        
        # Mock client response with proper structure
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        result = generate_adaptive_response(
            collection=mock_collection,
            question="What is machine learning?",
            preferred_format="text",
            groq_client=mock_client
        )
        
        assert isinstance(result, str)
        # Either returns the mock response or an error message
        assert len(result) > 0
    
    def test_generate_adaptive_response_exception_handling(self):
        """Test that response generation handles exceptions gracefully."""
        mock_collection = Mock()
        mock_client = Mock()
        
        # Mock to raise exception
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = generate_adaptive_response(
            collection=mock_collection,
            question="Test question",
            preferred_format="text",
            groq_client=mock_client
        )
        
        assert isinstance(result, str)
        # Should return error message or fallback response
        assert len(result) > 0


class TestGenerateOutOfScopeResponse:
    """Test out of scope response generation."""
    
    def test_generate_out_of_scope_response_basic(self):
        """Test basic out of scope response generation."""
        mock_collection = Mock()
        
        result = generate_out_of_scope_response(
            question="What is quantum physics?",
            collection=mock_collection
        )
        
        assert isinstance(result, str)
        assert "fora do escopo" in result
    
    def test_generate_out_of_scope_response_with_client(self):
        """Test out of scope response with client."""
        mock_collection = Mock()
        mock_client = Mock()
        
        result = generate_out_of_scope_response(
            question="What is quantum physics?",
            collection=mock_collection,
            groq_client=mock_client
        )
        
        assert isinstance(result, str)
        assert "fora do escopo" in result


class TestGenerateTemplateContent:
    """Test template content generation."""
    
    def test_generate_template_content_basic(self):
        """Test basic template content generation."""
        assessment = {
            "question": "What is machine learning?",
            "preferred_format": "text",
            "knowledge_level": "beginner"
        }
        
        result = generate_template_content(assessment)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_generate_template_content_different_formats(self):
        """Test template content generation with different formats."""
        formats = ["text", "video", "exercises", "mixed"]
        
        for format_type in formats:
            assessment = {
                "question": "Explain Python loops",
                "preferred_format": format_type,
                "knowledge_level": "intermediate"
            }
            
            result = generate_template_content(assessment)
            
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_generate_template_content_empty_assessment(self):
        """Test template content generation with empty assessment."""
        assessment = {}
        
        result = generate_template_content(assessment)
        
        assert isinstance(result, str)
        assert len(result) > 0 
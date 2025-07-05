"""
Tests for core question analysis module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.question_analysis import (
    analyze_question_maturity,
    classify_question_type,
    check_question_scope,
    analyze_indexed_content
)


class TestAnalyzeQuestionMaturity:
    """Test question maturity analysis functionality."""
    
    def test_analyze_question_maturity_without_client(self):
        """Test analyzing question maturity without Groq client."""
        result = analyze_question_maturity("What is machine learning?")
        
        assert isinstance(result, dict)
        assert "knowledge_level" in result
        assert "topics" in result
        assert "confidence" in result
        assert result["knowledge_level"] == "intermediate"
    
    def test_analyze_question_maturity_with_client(self):
        """Test analyzing question maturity with Groq client."""
        mock_client = Mock()
        
        # Mock successful response with proper structure
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "knowledge_level": "beginner",
            "topics": ["machine learning", "artificial intelligence"],
            "confidence": 0.9,
            "reasoning": "Basic question about ML"
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        
        result = analyze_question_maturity("What is machine learning?", mock_client)
        
        assert isinstance(result, dict)
        assert "knowledge_level" in result
        assert "topics" in result
        assert "confidence" in result
    
    def test_analyze_question_maturity_client_error(self):
        """Test analyzing question maturity with client error."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = analyze_question_maturity("What is AI?", mock_client)
        
        assert isinstance(result, dict)
        assert result["knowledge_level"] == "intermediate"
        assert "confidence" in result


class TestClassifyQuestionType:
    """Test question type classification."""
    
    def test_classify_question_type_without_client(self):
        """Test classifying question type without Groq client."""
        result = classify_question_type("How does neural network work?")
        
        assert isinstance(result, dict)
        assert "type" in result
        assert "verbosity" in result
        assert "style" in result
    
    def test_classify_question_type_with_client(self):
        """Test classifying question type with Groq client."""
        mock_client = Mock()
        
        # Mock successful response with proper structure
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "type": "technical",
            "verbosity": "detailed",
            "style": "educational",
            "reasoning": "Technical question requiring detailed explanation"
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        
        result = classify_question_type("How does neural network work?", mock_client)
        
        assert isinstance(result, dict)
        assert "type" in result
        assert "verbosity" in result
        assert "style" in result
    
    def test_classify_question_type_client_error(self):
        """Test classifying question type with client error."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = classify_question_type("How does ML work?", mock_client)
        
        assert isinstance(result, dict)
        assert result["type"] == "technical"
        assert result["verbosity"] == "moderate"


class TestCheckQuestionScope:
    """Test question scope validation."""
    
    def test_check_question_scope_without_client(self):
        """Test checking question scope without Groq client."""
        mock_collection = Mock()
        
        result = check_question_scope("What is AI?", mock_collection)
        
        assert isinstance(result, dict)
        assert "in_scope" in result
        assert "confidence" in result
        assert "reasoning" in result
    
    def test_check_question_scope_with_client(self):
        """Test checking question scope with Groq client."""
        mock_collection = Mock()
        mock_client = Mock()
        
        result = check_question_scope("What is AI?", mock_collection, mock_client)
        
        assert isinstance(result, dict)
        assert "in_scope" in result
        assert "confidence" in result
    
    def test_check_question_scope_client_error(self):
        """Test checking question scope with client error."""
        mock_collection = Mock()
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = check_question_scope("What is AI?", mock_collection, mock_client)
        
        assert isinstance(result, dict)
        assert "in_scope" in result


class TestAnalyzeIndexedContent:
    """Test indexed content analysis."""
    
    def test_analyze_indexed_content_without_client(self):
        """Test analyzing indexed content without Groq client."""
        mock_collection = Mock()
        
        result = analyze_indexed_content(mock_collection)
        
        assert isinstance(result, dict)
    
    def test_analyze_indexed_content_with_client(self):
        """Test analyzing indexed content with Groq client."""
        mock_collection = Mock()
        mock_client = Mock()
        
        result = analyze_indexed_content(mock_collection, mock_client)
        
        assert isinstance(result, dict)
    
    def test_analyze_indexed_content_client_error(self):
        """Test analyzing indexed content with client error."""
        mock_collection = Mock()
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = analyze_indexed_content(mock_collection, mock_client)
        
        assert isinstance(result, dict) 
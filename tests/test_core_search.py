"""
Tests for core search module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.search import (
    search_content,
    rerank_results,
    search_and_rerank
)


class TestSearchContent:
    """Test content search functionality."""
    
    def test_search_content_basic(self):
        """Test basic content search."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "documents": [["doc1", "doc2"]],
            "metadatas": [[{"type": "text"}, {"type": "pdf"}]]
        }
        
        results = search_content(mock_collection, "test query", 2)
        
        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0]["content"] == "doc1"
        assert results[0]["metadata"]["type"] == "text"
    
    def test_search_content_empty_query(self):
        """Test search with empty query."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "documents": [[]],
            "metadatas": [[]]
        }
        
        results = search_content(mock_collection, "", 3)
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_search_content_exception(self):
        """Test search content handles exceptions."""
        mock_collection = Mock()
        mock_collection.query.side_effect = Exception("Search error")
        
        results = search_content(mock_collection, "test query", 3)
        
        assert results == []


class TestRerankResults:
    """Test result reranking functionality."""
    
    def test_rerank_results_empty(self):
        """Test reranking with empty results."""
        results = rerank_results("test query", [], 3)
        
        assert results == []
    
    def test_rerank_results_basic(self):
        """Test basic result reranking."""
        initial_results = [
            {"content": "machine learning content", "metadata": {"type": "text"}},
            {"content": "other content", "metadata": {"type": "pdf"}}
        ]
        
        reranked = rerank_results("machine learning", initial_results, 2)
        
        assert isinstance(reranked, list)
        assert len(reranked) <= 2
        assert "relevance_score" in reranked[0]
        assert "keyword_matches" in reranked[0]
    
    def test_rerank_results_with_bonuses(self):
        """Test reranking with content type bonuses."""
        initial_results = [
            {"content": "exercise practice question", "metadata": {"type": "exercise"}},
            {"content": "regular content", "metadata": {"type": "text"}}
        ]
        
        reranked = rerank_results("exercise practice", initial_results, 2)
        
        assert isinstance(reranked, list)
        assert len(reranked) == 2
        # Exercise content should have higher score for exercise query
        assert reranked[0]["relevance_score"] >= reranked[1]["relevance_score"]


class TestSearchAndRerank:
    """Test combined search and rerank functionality."""
    
    @patch('core.search.search_content')
    @patch('core.search.rerank_results')
    def test_search_and_rerank_basic(self, mock_rerank, mock_search):
        """Test basic search and rerank workflow."""
        mock_search.return_value = [
            {"content": "result 1", "metadata": {"type": "text"}},
            {"content": "result 2", "metadata": {"type": "pdf"}}
        ]
        mock_rerank.return_value = [
            {"content": "result 1", "metadata": {"type": "text"}, "relevance_score": 0.9}
        ]
        
        mock_collection = Mock()
        results = search_and_rerank(mock_collection, "test query", 5, 1)
        
        mock_search.assert_called_once_with(mock_collection, "test query", 5)
        mock_rerank.assert_called_once()
        assert isinstance(results, list)
        assert len(results) == 1
    
    @patch('core.search.search_content')
    def test_search_and_rerank_no_results(self, mock_search):
        """Test search and rerank with no initial results."""
        mock_search.return_value = []
        
        mock_collection = Mock()
        results = search_and_rerank(mock_collection, "test query", 5, 3)
        
        assert results == []
    
    def test_search_and_rerank_integration(self):
        """Test actual search and rerank integration."""
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "documents": [["machine learning content", "AI content"]],
            "metadatas": [[{"type": "text"}, {"type": "pdf"}]]
        }
        
        results = search_and_rerank(mock_collection, "machine learning", 2, 1)
        
        assert isinstance(results, list)
        assert len(results) <= 1 
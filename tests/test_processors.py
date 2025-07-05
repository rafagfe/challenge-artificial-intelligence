"""
Tests for processors module.
"""
import pytest
import tempfile
import json
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from processors.text_processor import process_text_file
from processors.json_processor import process_json_file


class TestTextProcessor:
    """Test text file processor."""
    
    def test_process_text_file(self):
        """Test processing a text file."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            test_content = "Este é um texto de teste para processamento."
            tmp_file.write(test_content)
            tmp_file_path = tmp_file.name
        
        try:
            result = process_text_file(tmp_file_path)
            
            # Verify result structure
            assert "content" in result
            assert "metadata" in result
            
            # Verify content
            assert result["content"] == test_content
            
            # Verify metadata
            metadata = result["metadata"]
            assert metadata["type"] == "text"
            assert metadata["source"] == "file"
            assert metadata["file"] == Path(tmp_file_path).name
            
        finally:
            # Clean up
            Path(tmp_file_path).unlink()
    
    def test_process_text_file_empty(self):
        """Test processing an empty text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write("")
            tmp_file_path = tmp_file.name
        
        try:
            result = process_text_file(tmp_file_path)
            
            assert result["content"] == ""
            assert result["metadata"]["type"] == "text"
            
        finally:
            Path(tmp_file_path).unlink()


class TestJsonProcessor:
    """Test JSON file processor."""
    
    def test_process_json_list(self):
        """Test processing JSON file with list structure."""
        test_data = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(test_data, tmp_file)
            tmp_file_path = tmp_file.name
        
        try:
            result = process_json_file(tmp_file_path)
            
            # Should return list of chunks
            assert isinstance(result, list)
            assert len(result) == 2
            
            # Check first chunk
            first_chunk = result[0]
            assert "content" in first_chunk
            assert "metadata" in first_chunk
            assert first_chunk["metadata"]["type"] == "structured"
            assert first_chunk["metadata"]["exercise_id"] == 1
            
        finally:
            Path(tmp_file_path).unlink()
    
    def test_process_json_exercise_format(self):
        """Test processing JSON file with exercise format."""
        test_data = {
            "name": "Teste de Python",
            "content": [
                {
                    "title": "Questão 1",
                    "content": {
                        "html": "O que é Python?",
                        "options": [
                            {"content": {"html": "Uma linguagem"}, "correct": True},
                            {"content": {"html": "Um animal"}, "correct": False}
                        ]
                    }
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(test_data, tmp_file)
            tmp_file_path = tmp_file.name
        
        try:
            result = process_json_file(tmp_file_path)
            
            assert isinstance(result, list)
            assert len(result) == 1
            
            chunk = result[0]
            assert "Title: Questão 1" in chunk["content"]
            assert "Question: O que é Python?" in chunk["content"]
            assert "✓ Uma linguagem" in chunk["content"]
            assert "✗ Um animal" in chunk["content"]
            assert chunk["metadata"]["type"] == "exercise"
            assert chunk["metadata"]["subject"] == "Teste de Python"
            
        finally:
            Path(tmp_file_path).unlink()
    
    def test_process_json_single_object(self):
        """Test processing JSON file with single object."""
        test_data = {"key": "value", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(test_data, tmp_file)
            tmp_file_path = tmp_file.name
        
        try:
            result = process_json_file(tmp_file_path)
            
            assert isinstance(result, list)
            assert len(result) == 1
            
            chunk = result[0]
            assert "content" in chunk
            assert chunk["metadata"]["type"] == "structured"
            assert chunk["metadata"]["exercise_id"] == 1
            
        finally:
            Path(tmp_file_path).unlink()


class TestProcessorIntegration:
    """Integration tests for processors."""
    
    def test_processor_output_consistency(self):
        """Test that all processors return consistent output format."""
        # Create test text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_text:
            tmp_text.write("Test content")
            text_path = tmp_text.name
        
        # Create test JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_json:
            json.dump([{"test": "data"}], tmp_json)
            json_path = tmp_json.name
        
        try:
            text_result = process_text_file(text_path)
            json_result = process_json_file(json_path)
            
            # Both should return dict with content and metadata for single documents
            assert isinstance(text_result, dict)
            assert "content" in text_result
            assert "metadata" in text_result
            
            # JSON returns list, but each item should have same structure
            assert isinstance(json_result, list)
            json_item = json_result[0]
            assert "content" in json_item
            assert "metadata" in json_item
            
            # Metadata should have consistent fields
            for result in [text_result, json_item]:
                metadata = result["metadata"]
                assert "type" in metadata
                assert "file" in metadata
                
        finally:
            Path(text_path).unlink()
            Path(json_path).unlink() 
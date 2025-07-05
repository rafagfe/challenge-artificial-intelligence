"""
Tests for core indexing module.
"""
import pytest
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.indexing import (
    process_all_files,
    index_documents,
    get_resources_state,
    save_index_state,
    load_index_state
)


class TestProcessAllFiles:
    """Test process_all_files function."""
    
    def test_process_all_files_empty_directory(self):
        """Test processing empty resources directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            documents = process_all_files(tmp_dir)
            assert documents == []
    
    def test_process_all_files_nonexistent_directory(self):
        """Test processing non-existent directory."""
        documents = process_all_files("/nonexistent/path")
        assert documents == []
    
    @patch('core.indexing.process_text_file')
    def test_process_all_files_with_text_file(self, mock_process_text):
        """Test processing directory with text file."""
        mock_process_text.return_value = {
            "content": "test content",
            "metadata": {"type": "text", "file": "test.txt"}
        }
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a test file
            test_file = Path(tmp_dir) / "test.txt"
            test_file.write_text("test content")
            
            documents = process_all_files(tmp_dir)
            
            assert len(documents) == 1
            assert documents[0]["content"] == "test content"
            mock_process_text.assert_called_once()
    
    @patch('core.indexing.process_pdf_file')
    def test_process_all_files_with_pdf_file(self, mock_process_pdf):
        """Test processing directory with PDF file."""
        mock_process_pdf.return_value = [{
            "content": "pdf content",
            "metadata": {"type": "pdf", "file": "test.pdf"}
        }]
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a test PDF file
            test_file = Path(tmp_dir) / "test.pdf"
            test_file.write_bytes(b"fake pdf content")
            
            documents = process_all_files(tmp_dir)
            
            assert len(documents) == 1
            assert documents[0]["content"] == "pdf content"
            mock_process_pdf.assert_called_once()
    
    @patch('core.indexing.process_json_file')
    def test_process_all_files_with_json_file(self, mock_process_json):
        """Test processing directory with JSON file."""
        mock_process_json.return_value = [{
            "content": "json content",
            "metadata": {"type": "structured", "file": "test.json"}
        }]
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a test JSON file
            test_file = Path(tmp_dir) / "test.json"
            test_file.write_text('{"test": "data"}')
            
            documents = process_all_files(tmp_dir)
            
            assert len(documents) == 1
            assert documents[0]["content"] == "json content"
            mock_process_json.assert_called_once()
    
    def test_process_all_files_unsupported_file(self):
        """Test processing directory with unsupported file type."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create an unsupported file
            test_file = Path(tmp_dir) / "test.unknown"
            test_file.write_text("unknown content")
            
            documents = process_all_files(tmp_dir)
            
            assert documents == []


class TestIndexDocuments:
    """Test index_documents function."""
    
    def test_index_documents_empty_list(self):
        """Test indexing empty document list."""
        mock_collection = Mock()
        
        index_documents(mock_collection, [])
        
        # Should still call add with empty lists
        mock_collection.add.assert_called_once_with(
            documents=[],
            metadatas=[],
            ids=[]
        )
    
    def test_index_documents_single_document(self):
        """Test indexing single document."""
        mock_collection = Mock()
        documents = [{
            "content": "test content",
            "metadata": {"type": "text", "file": "test.txt"}
        }]
        
        with patch('core.indexing.datetime') as mock_datetime:
            mock_datetime.now.return_value.timestamp.return_value = 1234567890
            
            index_documents(mock_collection, documents)
            
            mock_collection.add.assert_called_once()
            call_args = mock_collection.add.call_args
            
            assert call_args[1]["documents"] == ["test content"]
            assert call_args[1]["metadatas"] == [{"type": "text", "file": "test.txt"}]
            assert len(call_args[1]["ids"]) == 1
            assert "doc_0_1234567890" in call_args[1]["ids"][0]
    
    def test_index_documents_multiple_documents(self):
        """Test indexing multiple documents."""
        mock_collection = Mock()
        documents = [
            {"content": "content1", "metadata": {"type": "text"}},
            {"content": "content2", "metadata": {"type": "pdf"}}
        ]
        
        index_documents(mock_collection, documents)
        
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        
        assert len(call_args[1]["documents"]) == 2
        assert len(call_args[1]["metadatas"]) == 2
        assert len(call_args[1]["ids"]) == 2


class TestResourcesState:
    """Test resources state management functions."""
    
    def test_get_resources_state_empty_directory(self):
        """Test getting state of empty directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            state = get_resources_state(tmp_dir)
            assert state == {}
    
    def test_get_resources_state_nonexistent_directory(self):
        """Test getting state of non-existent directory."""
        state = get_resources_state("/nonexistent/path")
        assert state == {}
    
    def test_get_resources_state_with_files(self):
        """Test getting state of directory with files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create test files
            file1 = Path(tmp_dir) / "file1.txt"
            file2 = Path(tmp_dir) / "file2.pdf"
            
            file1.write_text("content1")
            file2.write_bytes(b"content2")
            
            state = get_resources_state(tmp_dir)
            
            assert "file1.txt" in state
            assert "file2.pdf" in state
            assert isinstance(state["file1.txt"], float)  # modification time
            assert isinstance(state["file2.pdf"], float)
    
    def test_save_and_load_index_state(self):
        """Test saving and loading index state."""
        test_state = {
            "file1.txt": 1234567890.0,
            "file2.pdf": 1234567891.0
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            state_file = Path(tmp_file.name)
        
        try:
            # Test saving
            save_index_state(state_file, test_state)
            assert state_file.exists()
            
            # Test loading
            loaded_state = load_index_state(state_file)
            assert loaded_state == test_state
            
        finally:
            if state_file.exists():
                state_file.unlink()
    
    def test_load_index_state_nonexistent_file(self):
        """Test loading state from non-existent file."""
        nonexistent_file = Path("/nonexistent/state.json")
        state = load_index_state(nonexistent_file)
        assert state == {}
    
    def test_load_index_state_corrupted_file(self):
        """Test loading state from corrupted JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_file.write("invalid json content")
            state_file = Path(tmp_file.name)
        
        try:
            state = load_index_state(state_file)
            assert state == {}
        finally:
            state_file.unlink()


class TestIndexingIntegration:
    """Integration tests for indexing module."""
    
    @patch('core.indexing.process_text_file')
    @patch('core.indexing.process_json_file')
    def test_process_all_files_mixed_types(self, mock_process_json, mock_process_text):
        """Test processing directory with mixed file types."""
        mock_process_text.return_value = {
            "content": "text content",
            "metadata": {"type": "text"}
        }
        mock_process_json.return_value = [{
            "content": "json content", 
            "metadata": {"type": "structured"}
        }]
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create mixed files
            text_file = Path(tmp_dir) / "test.txt"
            json_file = Path(tmp_dir) / "test.json"
            unsupported_file = Path(tmp_dir) / "test.unknown"
            
            text_file.write_text("text")
            json_file.write_text('{"test": "data"}')
            unsupported_file.write_text("unknown")
            
            documents = process_all_files(tmp_dir)
            
            # Should process 2 supported files
            assert len(documents) == 2
            
            # Verify both processors were called
            mock_process_text.assert_called_once()
            mock_process_json.assert_called_once()
    
    def test_state_management_workflow(self):
        """Test complete state management workflow."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_file = Path(tmp_dir) / "state.json"
            
            # Create some files
            file1 = Path(tmp_dir) / "file1.txt"
            file1.write_text("content1")
            
            # Get initial state
            initial_state = get_resources_state(tmp_dir)
            save_index_state(state_file, initial_state)
            
            # Verify state was saved
            loaded_state = load_index_state(state_file)
            assert loaded_state == initial_state
            
            # Modify files (add new file)
            file2 = Path(tmp_dir) / "file2.txt"
            file2.write_text("content2")
            
            # Get new state
            new_state = get_resources_state(tmp_dir)
            
            # States should be different
            assert new_state != initial_state
            assert "file2.txt" in new_state
            assert "file2.txt" not in initial_state 
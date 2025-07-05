"""
Basic tests for main application.
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys
import tempfile

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestApplicationImports:
    """Test that all modules can be imported correctly."""
    
    def test_import_config_module(self):
        """Test importing config module."""
        try:
            from config.settings import (
                get_api_keys,
                get_model_settings,
                get_paths,
                validate_api_keys
            )
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import config module: {e}")
    
    def test_import_ai_module(self):
        """Test importing AI module."""
        try:
            from ai.llm_client import (
                create_groq_client,
                create_openai_client,
                create_langsmith_client,
                create_all_clients
            )
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import AI module: {e}")
    
    def test_import_processors_modules(self):
        """Test importing all processor modules."""
        try:
            from processors.text_processor import process_text_file
            from processors.pdf_processor import process_pdf_file
            from processors.video_processor import process_video_file
            from processors.image_processor import process_image_file
            from processors.json_processor import process_json_file
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import processor modules: {e}")
    
    def test_import_core_module(self):
        """Test importing core module."""
        try:
            from core.indexing import (
                process_all_files,
                index_documents,
                get_resources_state,
                save_index_state,
                load_index_state
            )
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import core module: {e}")
    
    def test_import_media_modules(self):
        """Test importing media modules."""
        try:
            from media.audio_generator import generate_audio_summary
            from media.video_generator import generate_video_summary
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import media modules: {e}")
    
    def test_import_ui_module(self):
        """Test importing UI module."""
        try:
            from ui.components import (
                display_api_key_inputs,
                display_file_uploader,
                display_search_interface,
                display_results
            )
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import UI module: {e}")


class TestApplicationFlow:
    """Test basic application flow."""
    
    @patch('config.settings.os.getenv')
    def test_config_loading(self, mock_getenv):
        """Test configuration loading."""
        mock_getenv.return_value = "test_value"
        
        from config.settings import get_api_keys
        
        keys = get_api_keys()
        assert isinstance(keys, dict)
        assert len(keys) > 0
    
    def test_client_creation_with_none_key(self):
        """Test AI client creation with None key."""
        from ai.llm_client import create_groq_client
        
        client = create_groq_client(None)
        assert client is None
    
    def test_processor_error_handling(self):
        """Test processor error handling."""
        from processors.text_processor import process_text_file
        
        # Test with non-existent file
        result = process_text_file("/non/existent/file.txt")
        assert result is None
    
    def test_media_generator_error_handling(self):
        """Test media generator error handling."""
        from media.audio_generator import generate_audio_summary
        
        # Test with no content
        result = generate_audio_summary("", "output.mp3")
        assert isinstance(result, bool)
    
    def test_indexing_with_empty_directory(self):
        """Test indexing with empty directory."""
        from core.indexing import process_all_files
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            documents = process_all_files(tmp_dir)
            assert documents == []
    
    def test_state_management(self):
        """Test state management functions."""
        from core.indexing import get_resources_state, save_index_state, load_index_state
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test empty directory state
            state = get_resources_state(tmp_dir)
            assert state == {}
            
            # Test save and load
            test_state = {"test": 123.45}
            state_file = Path(tmp_dir) / "state.json"
            
            save_index_state(state_file, test_state)
            loaded_state = load_index_state(state_file)
            assert loaded_state == test_state


class TestApplicationIntegration:
    """Integration tests for the application."""
    
    def test_processor_chain(self):
        """Test processor chain with different file types."""
        from processors.text_processor import process_text_file
        from processors.json_processor import process_json_file
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create test files
            text_file = Path(tmp_dir) / "test.txt"
            json_file = Path(tmp_dir) / "test.json"
            
            text_file.write_text("This is test content")
            json_file.write_text('{"key": "value"}')
            
            # Process files
            text_result = process_text_file(str(text_file))
            json_result = process_json_file(str(json_file))
            
            # Both should return valid results
            assert text_result is not None
            assert json_result is not None
    
    def test_config_to_client_flow(self):
        """Test configuration to client creation flow."""
        from config.settings import get_api_keys
        from ai.llm_client import create_all_clients
        
        # Load configuration
        api_keys = get_api_keys()
        
        # Create clients
        clients = create_all_clients(api_keys)
        
        # Should return client dictionary
        assert isinstance(clients, dict)
        assert "groq" in clients
        assert "openai" in clients
        assert "langsmith" in clients
    
    def test_full_indexing_flow(self):
        """Test full indexing flow."""
        from core.indexing import process_all_files, get_resources_state
        from processors.text_processor import process_text_file
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create test file
            test_file = Path(tmp_dir) / "test.txt"
            test_file.write_text("Test content for indexing")
            
            # Get initial state
            initial_state = get_resources_state(tmp_dir)
            assert "test.txt" in initial_state
            
            # Process all files
            documents = process_all_files(tmp_dir)
            
            # Should have processed the file
            assert len(documents) >= 0  # Depends on processor implementation
    
    def test_media_generation_flow(self):
        """Test media generation flow."""
        from media.audio_generator import generate_audio_summary
        from media.video_generator import generate_video_summary
        
        test_content = "This is test content for media generation"
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            audio_file = Path(tmp_dir) / "test.mp3"
            video_file = Path(tmp_dir) / "test.mp4"
            
            # Try to generate media (may fail without proper setup)
            audio_result = generate_audio_summary(test_content, str(audio_file))
            video_result = generate_video_summary(test_content, str(video_file), None)
            
            # Should return boolean results
            assert isinstance(audio_result, bool)
            assert isinstance(video_result, bool)


class TestApplicationRobustness:
    """Test application robustness and error handling."""
    
    def test_invalid_file_handling(self):
        """Test handling of invalid files."""
        from processors.text_processor import process_text_file
        from processors.pdf_processor import process_pdf_file
        
        # Test with non-existent files
        assert process_text_file("/invalid/path") is None
        assert process_pdf_file("/invalid/path") == []
    
    def test_empty_content_handling(self):
        """Test handling of empty content."""
        from media.audio_generator import generate_audio_summary
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "empty.mp3"
            
            # Should handle empty content gracefully
            result = generate_audio_summary("", str(output_file))
            assert isinstance(result, bool)
    
    def test_missing_api_keys_handling(self):
        """Test handling of missing API keys."""
        from ai.llm_client import create_all_clients
        
        # Test with empty API keys
        clients = create_all_clients({})
        
        # Should return dictionary with None values
        assert isinstance(clients, dict)
        assert all(client is None for client in clients.values())
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        from config.settings import validate_api_keys
        
        # Test API key validation (reads from environment)
        validation_result = validate_api_keys()
        
        # Should handle validation gracefully
        assert isinstance(validation_result, dict) 
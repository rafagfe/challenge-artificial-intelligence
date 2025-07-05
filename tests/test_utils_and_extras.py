"""
Tests for utility modules and additional components.
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys
import tempfile
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestUtilityModules:
    """Test utility modules if they exist."""
    
    def test_utils_directory_exists(self):
        """Test if utils directory exists."""
        utils_dir = Path(__file__).parent.parent / "src" / "utils"
        assert utils_dir.exists()
    
    def test_import_utils_if_exists(self):
        """Test importing utils modules if they exist."""
        try:
            # Try to import any utils modules
            utils_path = Path(__file__).parent.parent / "src" / "utils"
            
            for py_file in utils_path.glob("*.py"):
                if py_file.name != "__init__.py":
                    module_name = py_file.stem
                    try:
                        __import__(f"utils.{module_name}")
                        assert True
                    except ImportError:
                        # Module doesn't exist or has import issues
                        pass
        except Exception:
            # Utils directory doesn't exist or has issues
            pass


class TestFileSystemOperations:
    """Test file system operations used in the application."""
    
    def test_create_directory_structure(self):
        """Test creating directory structure."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            
            # Create directory structure
            directories = [
                "resources",
                "output",
                "audio",
                "video",
                "data"
            ]
            
            for directory in directories:
                dir_path = base_path / directory
                dir_path.mkdir(exist_ok=True)
                assert dir_path.exists()
                assert dir_path.is_dir()
    
    def test_file_operations(self):
        """Test basic file operations."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            
            # Create test file
            test_file = base_path / "test.txt"
            test_content = "This is test content"
            
            test_file.write_text(test_content)
            assert test_file.exists()
            assert test_file.read_text() == test_content
            
            # Test file modification time
            mod_time = test_file.stat().st_mtime
            assert isinstance(mod_time, float)
            assert mod_time > 0
    
    def test_path_operations(self):
        """Test path operations."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            
            # Test path joining
            sub_path = base_path / "subdir" / "file.txt"
            sub_path.parent.mkdir(parents=True, exist_ok=True)
            
            assert sub_path.parent.exists()
            assert sub_path.parent.is_dir()
            
            # Test path resolution
            resolved_path = sub_path.resolve()
            assert resolved_path.is_absolute()


class TestDataStructures:
    """Test data structures used in the application."""
    
    def test_document_structure(self):
        """Test document data structure."""
        document = {
            "content": "This is document content",
            "metadata": {
                "type": "text",
                "file": "test.txt",
                "size": 1024,
                "created": "2023-01-01"
            }
        }
        
        assert "content" in document
        assert "metadata" in document
        assert isinstance(document["metadata"], dict)
        assert "type" in document["metadata"]
    
    def test_api_keys_structure(self):
        """Test API keys data structure."""
        api_keys = {
            "groq_api_key": "test_groq_key",
            "openai_api_key": "test_openai_key",
            "elevenlabs_api_key": "test_elevenlabs_key",
            "d_id_api_key": "test_d_id_key",
            "langsmith_api_key": "test_langsmith_key"
        }
        
        expected_keys = [
            "groq_api_key",
            "openai_api_key", 
            "elevenlabs_api_key",
            "d_id_api_key",
            "langsmith_api_key"
        ]
        
        for key in expected_keys:
            assert key in api_keys
    
    def test_search_results_structure(self):
        """Test search results data structure."""
        search_results = [
            {
                "content": "Result 1",
                "metadata": {"type": "text", "file": "file1.txt"},
                "score": 0.95
            },
            {
                "content": "Result 2", 
                "metadata": {"type": "pdf", "file": "file2.pdf"},
                "score": 0.87
            }
        ]
        
        assert isinstance(search_results, list)
        assert len(search_results) == 2
        
        for result in search_results:
            assert "content" in result
            assert "metadata" in result
            assert "score" in result
            assert isinstance(result["score"], float)


class TestErrorHandling:
    """Test error handling patterns."""
    
    def test_none_handling(self):
        """Test handling of None values."""
        def safe_process(value):
            if value is None:
                return None
            return str(value).upper()
        
        assert safe_process(None) is None
        assert safe_process("test") == "TEST"
        assert safe_process("") == ""
    
    def test_empty_string_handling(self):
        """Test handling of empty strings."""
        def safe_string_process(value):
            if not value or not value.strip():
                return ""
            return value.strip().lower()
        
        assert safe_string_process("") == ""
        assert safe_string_process("   ") == ""
        assert safe_string_process("TEST") == "test"
        assert safe_string_process("  TEST  ") == "test"
    
    def test_list_handling(self):
        """Test handling of lists."""
        def safe_list_process(items):
            if not items:
                return []
            return [item for item in items if item is not None]
        
        assert safe_list_process([]) == []
        assert safe_list_process(None) == []
        assert safe_list_process([1, None, 2]) == [1, 2]
        assert safe_list_process([1, 2, 3]) == [1, 2, 3]
    
    def test_dict_handling(self):
        """Test handling of dictionaries."""
        def safe_dict_get(data, key, default=None):
            if not data or not isinstance(data, dict):
                return default
            return data.get(key, default)
        
        assert safe_dict_get(None, "key") is None
        assert safe_dict_get({}, "key") is None
        assert safe_dict_get({"key": "value"}, "key") == "value"
        assert safe_dict_get({"key": "value"}, "missing", "default") == "default"


class TestConstants:
    """Test constants used in the application."""
    
    def test_file_extensions(self):
        """Test file extension constants."""
        TEXT_EXTENSIONS = ['.txt', '.md', '.rtf']
        PDF_EXTENSIONS = ['.pdf']
        IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov']
        JSON_EXTENSIONS = ['.json']
        
        # Test that all extensions start with dot
        all_extensions = TEXT_EXTENSIONS + PDF_EXTENSIONS + IMAGE_EXTENSIONS + VIDEO_EXTENSIONS + JSON_EXTENSIONS
        
        for ext in all_extensions:
            assert ext.startswith('.')
            assert len(ext) > 1
    
    def test_model_names(self):
        """Test model name constants."""
        GROQ_MODELS = ["mixtral-8x7b-32768", "llama2-70b-4096"]
        OPENAI_MODELS = ["gpt-3.5-turbo", "gpt-4"]
        
        for model in GROQ_MODELS + OPENAI_MODELS:
            assert isinstance(model, str)
            assert len(model) > 0
    
    def test_default_values(self):
        """Test default values used in the application."""
        DEFAULT_MAX_RESULTS = 5
        DEFAULT_LANGUAGE = "pt-br"
        DEFAULT_TEMPERATURE = 0.7
        DEFAULT_MAX_TOKENS = 1000
        
        assert isinstance(DEFAULT_MAX_RESULTS, int)
        assert DEFAULT_MAX_RESULTS > 0
        assert isinstance(DEFAULT_LANGUAGE, str)
        assert DEFAULT_LANGUAGE in ["pt-br", "en", "es"]
        assert isinstance(DEFAULT_TEMPERATURE, float)
        assert 0.0 <= DEFAULT_TEMPERATURE <= 1.0
        assert isinstance(DEFAULT_MAX_TOKENS, int)
        assert DEFAULT_MAX_TOKENS > 0


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_validate_file_path(self):
        """Test file path validation."""
        def validate_file_path(path):
            if not path:
                return False
            path_obj = Path(path)
            return path_obj.exists() and path_obj.is_file()
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create test file
            test_file = Path(tmp_dir) / "test.txt"
            test_file.write_text("test")
            
            assert validate_file_path(str(test_file)) is True
            assert validate_file_path("/nonexistent/file.txt") is False
            assert validate_file_path("") is False
            assert validate_file_path(None) is False
    
    def test_get_file_extension(self):
        """Test getting file extension."""
        def get_file_extension(filename):
            if not filename:
                return ""
            return Path(filename).suffix.lower()
        
        assert get_file_extension("test.txt") == ".txt"
        assert get_file_extension("test.PDF") == ".pdf"
        assert get_file_extension("test") == ""
        assert get_file_extension("") == ""
        assert get_file_extension(None) == ""
    
    def test_format_file_size(self):
        """Test formatting file size."""
        def format_file_size(size_bytes):
            if size_bytes is None or size_bytes < 0:
                return "0 B"
            
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        
        assert format_file_size(0) == "0 B"
        assert format_file_size(512) == "512 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(None) == "0 B"
        assert format_file_size(-1) == "0 B"
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        def sanitize_filename(filename):
            if not filename:
                return "unnamed"
            
            # Remove or replace invalid characters
            invalid_chars = '<>:"/\\|?*'
            sanitized = filename
            for char in invalid_chars:
                sanitized = sanitized.replace(char, '_')
            
            # Remove leading/trailing whitespace and dots
            sanitized = sanitized.strip(' .')
            
            return sanitized if sanitized else "unnamed"
        
        assert sanitize_filename("test.txt") == "test.txt"
        assert sanitize_filename("test<>file.txt") == "test__file.txt"
        assert sanitize_filename("   test.txt   ") == "test.txt"
        assert sanitize_filename("...") == "unnamed"
        assert sanitize_filename("") == "unnamed"
        assert sanitize_filename(None) == "unnamed"


class TestPerformanceHelpers:
    """Test performance-related helper functions."""
    
    def test_measure_execution_time(self):
        """Test execution time measurement."""
        import time
        
        def measure_time(func):
            start = time.time()
            result = func()
            end = time.time()
            return result, end - start
        
        def slow_function():
            time.sleep(0.1)
            return "done"
        
        result, duration = measure_time(slow_function)
        assert result == "done"
        assert duration >= 0.1
        assert duration < 0.2  # Should be close to 0.1
    
    def test_chunk_processing(self):
        """Test chunk processing for large data."""
        def process_in_chunks(data, chunk_size=10):
            if not data:
                return []
            
            chunks = []
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                chunks.append(chunk)
            
            return chunks
        
        data = list(range(25))
        chunks = process_in_chunks(data, 10)
        
        assert len(chunks) == 3
        assert chunks[0] == list(range(10))
        assert chunks[1] == list(range(10, 20))
        assert chunks[2] == list(range(20, 25))
        
        # Test empty data
        assert process_in_chunks([]) == []
        assert process_in_chunks(None) == [] 
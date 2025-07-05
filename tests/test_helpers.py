"""
Tests for helper functions and utilities.
"""

import pytest
from pathlib import Path
import sys
import tempfile

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestFileHelpers:
    """Test file handling helper functions."""

    def test_file_extension_detection(self):
        """Test file extension detection."""

        def get_file_extension(filename):
            return Path(filename).suffix.lower()

        assert get_file_extension("test.txt") == ".txt"
        assert get_file_extension("document.PDF") == ".pdf"
        assert get_file_extension("data.json") == ".json"
        assert get_file_extension("video.mp4") == ".mp4"
        assert get_file_extension("image.PNG") == ".png"
        assert get_file_extension("file_without_extension") == ""

    def test_file_size_formatting(self):
        """Test file size formatting."""

        def format_file_size(size_bytes):
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"

        assert format_file_size(512) == "512 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(2048) == "2.0 KB"

    def test_path_validation(self):
        """Test path validation."""

        def is_valid_path(path):
            try:
                Path(path)
                return True
            except (OSError, ValueError):
                return False

        assert is_valid_path("/home/user/file.txt") is True
        assert is_valid_path("relative/path/file.txt") is True
        assert is_valid_path("") is True  # Empty path is valid Path object
        assert is_valid_path("C:\\Windows\\file.txt") is True


class TestDataHelpers:
    """Test data handling helper functions."""

    def test_safe_dict_get(self):
        """Test safe dictionary access."""

        def safe_get(data, key, default=None):
            if not data or not isinstance(data, dict):
                return default
            return data.get(key, default)

        test_dict = {"key1": "value1", "key2": "value2"}

        assert safe_get(test_dict, "key1") == "value1"
        assert safe_get(test_dict, "missing") is None
        assert safe_get(test_dict, "missing", "default") == "default"
        assert safe_get(None, "key") is None
        assert safe_get([], "key") is None

    def test_list_filtering(self):
        """Test list filtering functions."""

        def filter_none(items):
            return [item for item in items if item is not None]

        def filter_empty_strings(items):
            return [item for item in items if item and item.strip()]

        test_list = [1, None, 2, None, 3]
        assert filter_none(test_list) == [1, 2, 3]

        string_list = ["hello", "", "world", "   ", "test"]
        assert filter_empty_strings(string_list) == ["hello", "world", "test"]

    def test_string_helpers(self):
        """Test string helper functions."""

        def clean_string(text):
            return text.strip() if text else ""

        def is_empty_string(text):
            return not text or not text.strip()

        assert clean_string("  hello  ") == "hello"
        assert clean_string("") == ""
        assert clean_string(None) == ""

        assert is_empty_string("") is True
        assert is_empty_string("   ") is True
        assert is_empty_string("hello") is False
        assert is_empty_string(None) is True


class TestValidationHelpers:
    """Test validation helper functions."""

    def test_api_key_validation(self):
        """Test API key validation."""

        def is_valid_api_key(key):
            if not key or not isinstance(key, str):
                return False
            return len(key.strip()) > 0

        assert is_valid_api_key("valid_key_123") is True
        assert is_valid_api_key("") is False
        assert is_valid_api_key("   ") is False
        assert is_valid_api_key(None) is False
        assert is_valid_api_key(123) is False

    def test_email_validation(self):
        """Test basic email validation."""

        def is_valid_email(email):
            if not email or "@" not in email:
                return False
            parts = email.split("@")
            if len(parts) != 2 or not parts[0] or not parts[1]:
                return False
            return "." in parts[1]

        assert is_valid_email("test@example.com") is True
        assert is_valid_email("user@domain.org") is True
        assert is_valid_email("invalid.email") is False
        assert is_valid_email("@example.com") is False
        assert is_valid_email("test@") is False

    def test_number_validation(self):
        """Test number validation."""

        def is_positive_number(value):
            try:
                return float(value) > 0
            except (ValueError, TypeError):
                return False

        assert is_positive_number(5) is True
        assert is_positive_number(5.5) is True
        assert is_positive_number("5") is True
        assert is_positive_number(0) is False
        assert is_positive_number(-1) is False
        assert is_positive_number("invalid") is False
        assert is_positive_number(None) is False


class TestFormatHelpers:
    """Test formatting helper functions."""

    def test_time_formatting(self):
        """Test time formatting functions."""

        def format_duration(seconds):
            if seconds < 60:
                return f"{seconds:.1f}s"
            elif seconds < 3600:
                return f"{seconds/60:.1f}m"
            else:
                return f"{seconds/3600:.1f}h"

        assert format_duration(30) == "30.0s"
        assert format_duration(90) == "1.5m"
        assert format_duration(3600) == "1.0h"
        assert format_duration(7200) == "2.0h"

    def test_percentage_formatting(self):
        """Test percentage formatting."""

        def format_percentage(value, total):
            if total == 0:
                return "0%"
            return f"{(value / total) * 100:.1f}%"

        assert format_percentage(1, 4) == "25.0%"
        assert format_percentage(3, 4) == "75.0%"
        assert format_percentage(0, 4) == "0.0%"
        assert format_percentage(1, 0) == "0%"

    def test_text_truncation(self):
        """Test text truncation."""

        def truncate_text(text, max_length=50):
            if not text or len(text) <= max_length:
                return text
            return text[: max_length - 3] + "..."

        short_text = "This is short"
        long_text = "This is a very long text that needs to be truncated"

        assert truncate_text(short_text) == short_text
        # The long text should be truncated to exactly 50 characters
        truncated = truncate_text(long_text)
        assert len(truncated) == 50
        assert truncated.endswith("...")
        assert truncate_text("") == ""
        assert truncate_text(None) is None


class TestUtilityFunctions:
    """Test utility functions."""

    def test_chunk_list(self):
        """Test chunking lists."""

        def chunk_list(items, chunk_size):
            chunks = []
            for i in range(0, len(items), chunk_size):
                chunks.append(items[i : i + chunk_size])
            return chunks

        data = list(range(10))
        chunks = chunk_list(data, 3)

        assert len(chunks) == 4
        assert chunks[0] == [0, 1, 2]
        assert chunks[1] == [3, 4, 5]
        assert chunks[2] == [6, 7, 8]
        assert chunks[3] == [9]

        # Test empty list
        assert chunk_list([], 3) == []

    def test_flatten_list(self):
        """Test flattening nested lists."""

        def flatten_list(nested_list):
            flattened = []
            for item in nested_list:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            return flattened

        nested = [[1, 2], [3, 4], [5]]
        assert flatten_list(nested) == [1, 2, 3, 4, 5]

        mixed = [1, [2, 3], 4, [5, 6]]
        assert flatten_list(mixed) == [1, 2, 3, 4, 5, 6]

        # Test empty list
        assert flatten_list([]) == []

    def test_unique_list(self):
        """Test removing duplicates from list."""

        def unique_list(items):
            return list(dict.fromkeys(items))

        duplicates = [1, 2, 2, 3, 1, 4, 3]
        assert unique_list(duplicates) == [1, 2, 3, 4]

        strings = ["a", "b", "a", "c", "b"]
        assert unique_list(strings) == ["a", "b", "c"]

        # Test empty list
        assert unique_list([]) == []


class TestErrorHandling:
    """Test error handling utilities."""

    def test_safe_division(self):
        """Test safe division function."""

        def safe_divide(a, b, default=0):
            try:
                return a / b
            except ZeroDivisionError:
                return default

        assert safe_divide(10, 2) == 5
        assert safe_divide(10, 0) == 0
        assert safe_divide(10, 0, -1) == -1

    def test_safe_conversion(self):
        """Test safe type conversion."""

        def safe_int(value, default=0):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        def safe_float(value, default=0.0):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        assert safe_int("123") == 123
        assert safe_int("invalid") == 0
        assert safe_int(None) == 0
        assert safe_int("invalid", -1) == -1

        assert safe_float("123.45") == 123.45
        assert safe_float("invalid") == 0.0
        assert safe_float(None) == 0.0

    def test_exception_handling(self):
        """Test exception handling patterns."""

        def safe_function_call(func, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return f"Error: {str(e)}"

        def working_function(x):
            return x * 2

        def failing_function(x):
            raise ValueError("Test error")

        assert safe_function_call(working_function, 5) == 10
        assert "Error: Test error" in safe_function_call(failing_function, 5)

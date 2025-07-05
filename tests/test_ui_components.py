"""
Tests for UI components module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import tempfile

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ui.components import (
    display_api_key_inputs,
    display_file_uploader,
    display_processing_progress,
    display_search_interface,
    display_results,
    display_media_generation_section,
    display_sidebar_controls,
    display_file_manager,
    display_configuration_panel,
)


class TestApiKeyInputs:
    """Test API key input components."""

    @patch("ui.components.st")
    def test_display_api_key_inputs_returns_dict(self, mock_st):
        """Test that API key inputs returns a dictionary."""
        mock_st.sidebar.text_input.return_value = "test_key"
        mock_st.sidebar.expander.return_value.__enter__.return_value = Mock()

        api_keys = display_api_key_inputs()

        assert isinstance(api_keys, dict)
        assert "groq_api_key" in api_keys
        assert "openai_api_key" in api_keys
        assert "elevenlabs_api_key" in api_keys
        assert "d_id_api_key" in api_keys
        assert "langsmith_api_key" in api_keys


class TestFileUploader:
    """Test file uploader components."""

    @patch("ui.components.st")
    def test_display_file_uploader_returns_files(self, mock_st):
        """Test that file uploader returns files."""
        mock_files = [Mock(), Mock()]
        mock_st.file_uploader.return_value = mock_files

        uploaded_files = display_file_uploader()

        assert uploaded_files == mock_files
        mock_st.file_uploader.assert_called_once()


class TestProcessingProgress:
    """Test processing progress components."""

    @patch("ui.components.st")
    def test_display_processing_progress_returns_progress_bar(self, mock_st):
        """Test that processing progress returns a progress bar."""
        mock_progress = Mock()
        mock_st.progress.return_value = mock_progress

        progress_bar = display_processing_progress()

        assert progress_bar == mock_progress
        mock_st.progress.assert_called_once_with(0)


class TestSearchInterface:
    """Test search interface components."""

    @patch("ui.components.st")
    def test_display_search_interface_returns_query_and_button(self, mock_st):
        """Test that search interface returns query and button state."""
        mock_st.text_input.return_value = "test query"
        mock_st.button.return_value = True

        query, search_clicked = display_search_interface()

        assert query == "test query"
        assert search_clicked is True
        mock_st.text_input.assert_called_once()
        mock_st.button.assert_called_once()


class TestResultsDisplay:
    """Test results display components."""

    @patch("ui.components.st")
    def test_display_results_empty_shows_info(self, mock_st):
        """Test that empty results shows info message."""
        display_results([])

        mock_st.info.assert_called_once_with("Nenhum resultado encontrado.")

    @patch("ui.components.st")
    def test_display_results_with_data_shows_expanders(self, mock_st):
        """Test that results with data shows expanders."""
        mock_results = [
            {"content": "Result 1", "metadata": {"type": "text"}},
            {"content": "Result 2", "metadata": {"type": "pdf"}},
        ]

        display_results(mock_results)

        assert mock_st.expander.call_count == 2


class TestMediaGenerationSection:
    """Test media generation section components."""

    @patch("ui.components.st")
    def test_display_media_generation_section_returns_options(self, mock_st):
        """Test that media generation section returns options."""
        mock_st.checkbox.side_effect = [True, False]  # Audio enabled, video disabled
        mock_st.button.return_value = True
        mock_st.text_area.return_value = "test content"

        # Mock columns to return two mock objects that work as context managers
        mock_col1 = Mock()
        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=None)
        mock_col2 = Mock()
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)
        mock_st.columns.return_value = [mock_col1, mock_col2]

        audio_enabled, video_enabled, generate_clicked = (
            display_media_generation_section()
        )

        assert audio_enabled is True
        assert video_enabled is False
        assert generate_clicked is True


class TestSidebarControls:
    """Test sidebar controls components."""

    @patch("ui.components.st")
    def test_display_sidebar_controls_returns_dict(self, mock_st):
        """Test that sidebar controls returns a dictionary."""
        mock_st.sidebar.selectbox.return_value = "Groq"
        mock_st.sidebar.slider.return_value = 5
        mock_st.sidebar.button.return_value = False

        controls = display_sidebar_controls()

        assert isinstance(controls, dict)
        assert "model" in controls
        assert "max_results" in controls
        assert "clear_cache" in controls


class TestFileManager:
    """Test file manager components."""

    @patch("ui.components.st")
    def test_display_file_manager_creates_expander(self, mock_st):
        """Test that file manager creates an expander."""
        mock_st.sidebar.expander.return_value.__enter__.return_value = Mock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            display_file_manager(tmp_dir)

            mock_st.sidebar.expander.assert_called_once_with(
                "📁 Gerenciador de Arquivos"
            )


class TestConfigurationPanel:
    """Test configuration panel components."""

    @patch("ui.components.st")
    def test_display_configuration_panel_returns_dict(self, mock_st):
        """Test that configuration panel returns a dictionary."""
        mock_st.sidebar.expander.return_value.__enter__.return_value = Mock()
        mock_st.sidebar.selectbox.return_value = "pt-br"
        mock_st.sidebar.slider.return_value = 0.7

        config = display_configuration_panel()

        assert isinstance(config, dict)
        mock_st.sidebar.expander.assert_called_once_with("⚙️ Configurações")


class TestUIComponentsIntegration:
    """Integration tests for UI components."""

    @patch("ui.components.st")
    def test_all_components_work_together(self, mock_st):
        """Test that all components can work together without conflicts."""
        # Setup all mocks
        mock_st.text_input.return_value = "test query"
        mock_st.button.return_value = True
        mock_st.file_uploader.return_value = None
        mock_st.checkbox.return_value = False
        mock_st.progress.return_value = Mock()
        mock_st.sidebar.expander.return_value.__enter__.return_value = Mock()
        mock_st.sidebar.selectbox.return_value = "Groq"
        mock_st.sidebar.slider.return_value = 5
        mock_st.sidebar.button.return_value = False
        mock_st.text_area.return_value = "test content"

        # Mock columns to return two mock objects that work as context managers
        mock_col1 = Mock()
        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=None)
        mock_col2 = Mock()
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)
        mock_st.columns.return_value = [mock_col1, mock_col2]

        # Test each component
        api_keys = display_api_key_inputs()
        assert isinstance(api_keys, dict)

        files = display_file_uploader()
        assert files is None

        query, search_clicked = display_search_interface()
        assert query == "test query"
        assert search_clicked is True

        progress = display_processing_progress("Processing...")
        assert progress is not None

        display_results([])

        audio_enabled, video_enabled, generate_clicked = (
            display_media_generation_section()
        )
        assert isinstance(audio_enabled, bool)
        assert isinstance(video_enabled, bool)
        assert isinstance(generate_clicked, bool)

        controls = display_sidebar_controls()
        assert isinstance(controls, dict)

        config = display_configuration_panel()
        assert isinstance(config, dict)

        with tempfile.TemporaryDirectory() as tmp_dir:
            display_file_manager(tmp_dir)

        # All components should work without errors
        assert True

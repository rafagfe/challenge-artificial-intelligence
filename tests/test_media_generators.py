"""
Tests for media generators module.
"""

import pytest
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from media.audio_generator import (
    generate_audio_with_gTTS,
    generate_audio_with_elevenlabs,
    generate_audio_with_openai,
    generate_audio_summary,
)
from media.video_generator import (
    generate_video_with_d_id,
    generate_video_from_text,
    generate_video_summary,
)


class TestAudioGenerator:
    """Test audio generation functions."""

    @patch("media.audio_generator.gTTS")
    def test_generate_audio_with_gTTS_success(self, mock_gtts):
        """Test successful audio generation with gTTS."""
        mock_tts = Mock()
        mock_gtts.return_value = mock_tts

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "test.mp3"

            result = generate_audio_with_gTTS("Hello world", str(output_file))

            assert result is True
            mock_gtts.assert_called_once_with(text="Hello world", lang="pt-br")
            mock_tts.save.assert_called_once_with(str(output_file))

    @patch("media.audio_generator.gTTS")
    def test_generate_audio_with_gTTS_failure(self, mock_gtts):
        """Test failed audio generation with gTTS."""
        mock_gtts.side_effect = Exception("TTS error")

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "test.mp3"

            result = generate_audio_with_gTTS("Hello world", str(output_file))

            assert result is False

    def test_generate_audio_with_elevenlabs_no_key(self):
        """Test ElevenLabs generation without API key."""
        result = generate_audio_with_elevenlabs("Hello world", "output.mp3", None)
        assert result is False

    @patch("media.audio_generator.requests.post")
    def test_generate_audio_with_elevenlabs_success(self, mock_post):
        """Test successful ElevenLabs generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_post.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "test.mp3"

            result = generate_audio_with_elevenlabs(
                "Hello world", str(output_file), "fake_api_key"
            )

            assert result is True
            assert output_file.exists()
            assert output_file.read_bytes() == b"fake audio data"

    @patch("media.audio_generator.requests.post")
    def test_generate_audio_with_elevenlabs_failure(self, mock_post):
        """Test failed ElevenLabs generation."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "test.mp3"

            result = generate_audio_with_elevenlabs(
                "Hello world", str(output_file), "fake_api_key"
            )

            assert result is False

    def test_generate_audio_with_openai_no_client(self):
        """Test OpenAI generation without client."""
        result = generate_audio_with_openai("Hello world", "output.mp3", None)
        assert result is False

    @patch("media.audio_generator.requests.post")
    def test_generate_audio_with_openai_success(self, mock_post):
        """Test successful OpenAI generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake audio data"
        mock_post.return_value = mock_response

        mock_client = Mock()
        mock_client.api_key = "test_key"

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "test.mp3"

            result = generate_audio_with_openai(
                "Hello world", str(output_file), mock_client
            )

            assert result is True
            assert output_file.exists()

    @patch("media.audio_generator.generate_audio_with_gTTS")
    def test_generate_audio_summary_success(self, mock_gtts):
        """Test successful audio summary generation."""
        mock_gtts.return_value = True

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "summary.mp3"

            result = generate_audio_summary("Test summary content", str(output_file))

            assert result is True
            mock_gtts.assert_called_once_with("Test summary content", str(output_file))

    @patch("media.audio_generator.generate_audio_with_gTTS")
    def test_generate_audio_summary_failure(self, mock_gtts):
        """Test failed audio summary generation."""
        mock_gtts.return_value = False

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "summary.mp3"

            result = generate_audio_summary("Test summary content", str(output_file))

            assert result is False


class TestVideoGenerator:
    """Test video generation functions."""

    def test_generate_video_with_d_id_no_key(self):
        """Test D-ID generation without API key."""
        result = generate_video_with_d_id("Hello world", "output.mp4", None)
        assert result is False

    @patch("media.video_generator.requests.post")
    def test_generate_video_with_d_id_success(self, mock_post):
        """Test successful D-ID generation."""
        # Mock the create talk response
        mock_create_response = Mock()
        mock_create_response.status_code = 201
        mock_create_response.json.return_value = {"id": "test_id"}

        # Mock the get talk status response
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "status": "done",
            "result_url": "https://example.com/video.mp4",
        }

        # Mock the video download response
        mock_download_response = Mock()
        mock_download_response.status_code = 200
        mock_download_response.content = b"fake video data"

        mock_post.return_value = mock_create_response

        with patch("media.video_generator.requests.get") as mock_get:
            mock_get.side_effect = [mock_get_response, mock_download_response]

            with tempfile.TemporaryDirectory() as tmp_dir:
                output_file = Path(tmp_dir) / "test.mp4"

                result = generate_video_with_d_id(
                    "Hello world", str(output_file), "fake_api_key"
                )

                assert result is True
                assert output_file.exists()

    @patch("media.video_generator.requests.post")
    def test_generate_video_with_d_id_failure(self, mock_post):
        """Test failed D-ID generation."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "test.mp4"

            result = generate_video_with_d_id(
                "Hello world", str(output_file), "fake_api_key"
            )

            assert result is False

    def test_generate_video_from_text_no_key(self):
        """Test video generation without API key."""
        result = generate_video_from_text("Hello world", "output.mp4", None)
        assert result is False

    @patch("media.video_generator.generate_video_with_d_id")
    def test_generate_video_from_text_success(self, mock_d_id):
        """Test successful video generation from text."""
        mock_d_id.return_value = True

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "test.mp4"

            result = generate_video_from_text(
                "Hello world", str(output_file), "fake_api_key"
            )

            assert result is True
            mock_d_id.assert_called_once_with(
                "Hello world", str(output_file), "fake_api_key"
            )

    @patch("media.video_generator.generate_video_with_d_id")
    def test_generate_video_from_text_failure(self, mock_d_id):
        """Test failed video generation from text."""
        mock_d_id.return_value = False

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "test.mp4"

            result = generate_video_from_text(
                "Hello world", str(output_file), "fake_api_key"
            )

            assert result is False

    @patch("media.video_generator.generate_video_from_text")
    def test_generate_video_summary_success(self, mock_video_gen):
        """Test successful video summary generation."""
        mock_video_gen.return_value = True

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "summary.mp4"

            result = generate_video_summary(
                "Test summary content", str(output_file), "fake_api_key"
            )

            assert result is True
            mock_video_gen.assert_called_once_with(
                "Test summary content", str(output_file), "fake_api_key"
            )

    @patch("media.video_generator.generate_video_from_text")
    def test_generate_video_summary_failure(self, mock_video_gen):
        """Test failed video summary generation."""
        mock_video_gen.return_value = False

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "summary.mp4"

            result = generate_video_summary(
                "Test summary content", str(output_file), "fake_api_key"
            )

            assert result is False


class TestMediaGeneratorsIntegration:
    """Integration tests for media generators."""

    @patch("media.audio_generator.generate_audio_with_gTTS")
    @patch("media.video_generator.generate_video_from_text")
    def test_generate_both_media_types(self, mock_video, mock_audio):
        """Test generating both audio and video for the same content."""
        mock_audio.return_value = True
        mock_video.return_value = True

        content = "Test content for multimedia generation"

        with tempfile.TemporaryDirectory() as tmp_dir:
            audio_file = Path(tmp_dir) / "content.mp3"
            video_file = Path(tmp_dir) / "content.mp4"

            audio_result = generate_audio_summary(content, str(audio_file))
            video_result = generate_video_summary(content, str(video_file), "fake_key")

            assert audio_result is True
            assert video_result is True

            mock_audio.assert_called_once_with(content, str(audio_file))
            mock_video.assert_called_once_with(content, str(video_file), "fake_key")

    def test_empty_content_handling(self):
        """Test handling of empty content."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "empty.mp3"

            # Should handle empty content gracefully
            result = generate_audio_summary("", str(output_file))

            # The actual implementation determines behavior
            # This test ensures no crashes occur
            assert isinstance(result, bool)

    def test_long_content_handling(self):
        """Test handling of very long content."""
        long_content = "This is a very long content. " * 100

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = Path(tmp_dir) / "long.mp3"

            # Should handle long content gracefully
            result = generate_audio_summary(long_content, str(output_file))

            # The actual implementation determines behavior
            assert isinstance(result, bool)

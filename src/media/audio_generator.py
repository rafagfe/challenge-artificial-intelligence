"""
Audio generation functions.
"""

import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional
from openai import OpenAI
from langsmith import traceable

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

logger = logging.getLogger(__name__)


@traceable(name="generate_audio")
def generate_audio(
    text: str,
    openai_client: OpenAI,
    audio_path: Path,
    model: str = "tts-1",
    voice: str = "alloy",
    interaction_id: Optional[str] = None,
) -> str:
    """
    Generate audio from text using OpenAI TTS and save it to a file.

    Args:
        text (str): Text to convert to audio
        openai_client (OpenAI): OpenAI client instance
        audio_path (Path): Directory to save audio files
        model (str): TTS model to use
        voice (str): Voice to use
        interaction_id (Optional[str]): Unique interaction ID

    Returns:
        str: Path to the generated audio file

    Raises:
        ValueError: If OpenAI client is not provided
    """
    if not openai_client:
        raise ValueError("OpenAI client is required for audio generation")

    # Generate file path
    if interaction_id:
        file_path = audio_path / f"audio_{interaction_id}.mp3"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = audio_path / f"audio_{timestamp}.mp3"

    try:
        # Use the recommended method to avoid DeprecationWarning
        with openai_client.audio.speech.with_streaming_response.create(
            model=model, voice=voice, input=text
        ) as response:
            response.stream_to_file(file_path)

        logger.info(f"Successfully generated audio file: {file_path}")
        return str(file_path)
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        raise


@traceable(name="generate_audio_with_gTTS")
def generate_audio_with_gTTS(text: str, output_path: str, lang: str = "pt-br") -> bool:
    """
    Generate audio using Google Text-to-Speech.

    Args:
        text (str): Text to convert to audio
        output_path (str): Path to save the audio file
        lang (str): Language code for TTS

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not gTTS:
            logger.error("gTTS is not installed")
            return False

        tts = gTTS(text=text, lang=lang)
        tts.save(output_path)
        logger.info(f"Successfully generated audio with gTTS: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error generating audio with gTTS: {e}")
        return False


@traceable(name="generate_audio_with_elevenlabs")
def generate_audio_with_elevenlabs(text: str, output_path: str, api_key: str) -> bool:
    """
    Generate audio using ElevenLabs API.

    Args:
        text (str): Text to convert to audio
        output_path (str): Path to save the audio file
        api_key (str): ElevenLabs API key

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not api_key:
            logger.error("ElevenLabs API key is required")
            return False

        url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Successfully generated audio with ElevenLabs: {output_path}")
            return True
        else:
            logger.error(f"ElevenLabs API error: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Error generating audio with ElevenLabs: {e}")
        return False


@traceable(name="generate_audio_with_openai")
def generate_audio_with_openai(text: str, output_path: str, openai_client) -> bool:
    """
    Generate audio using OpenAI TTS.

    Args:
        text (str): Text to convert to audio
        output_path (str): Path to save the audio file
        openai_client: OpenAI client instance

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not openai_client:
            logger.error("OpenAI client is required")
            return False

        response = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {openai_client.api_key}",
                "Content-Type": "application/json",
            },
            json={"model": "tts-1", "input": text, "voice": "alloy"},
        )

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Successfully generated audio with OpenAI: {output_path}")
            return True
        else:
            logger.error(f"OpenAI API error: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Error generating audio with OpenAI: {e}")
        return False


@traceable(name="generate_audio_summary")
def generate_audio_summary(text: str, output_path: str) -> bool:
    """
    Generate audio summary using the default TTS method.

    Args:
        text (str): Text to convert to audio
        output_path (str): Path to save the audio file

    Returns:
        bool: True if successful, False otherwise
    """
    return generate_audio_with_gTTS(text, output_path)

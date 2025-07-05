"""
Asynchronous media generation functions.
"""

import json
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from langsmith import traceable

logger = logging.getLogger(__name__)


@traceable(name="generate_media")
def generate_media_async(
    text: str,
    interaction_id: str,
    message_index: int,
    openai_client,
    audio_path: Path,
    video_path: Path,
    states_path: str,
) -> None:
    """
    Generate audio and video asynchronously in background thread.

    Args:
        text (str): Text to convert to audio/video
        interaction_id (str): Unique interaction identifier
        message_index (int): Index of message in chat history
        openai_client: OpenAI client instance
        audio_path (Path): Path to audio directory
        video_path (Path): Path to video directory
        states_path (str): Path to states directory
    """
    try:
        from media.audio_generator import generate_audio
        from media.video_generator import generate_video

        # Generate audio first
        logger.info(f"Starting async audio generation for interaction {interaction_id}")
        audio_file_path = generate_audio(
            text=text,
            openai_client=openai_client,
            audio_path=audio_path,
            interaction_id=interaction_id,
        )

        # Create a status file to signal audio completion
        status_file = Path(states_path) / f"status_{interaction_id}.json"
        with open(status_file, "w") as f:
            json.dump({"audio_ready": True, "audio_path": audio_file_path}, f)
        logger.info(f"Audio ready for interaction {interaction_id}")

        # Generate video using the audio we just created
        logger.info(f"Starting async video generation for interaction {interaction_id}")
        video_file_path = generate_video(
            video_path=video_path,
            background_image_path="resources/Infografico-1.jpg",
            audio_path=audio_file_path,
            interaction_id=interaction_id,
        )

        # Update status file with video completion
        with open(status_file, "w") as f:
            json.dump(
                {
                    "audio_ready": True,
                    "audio_path": audio_file_path,
                    "video_ready": True,
                    "video_path": video_file_path,
                },
                f,
            )
        logger.info(f"Video ready for interaction {interaction_id}")

    except Exception as e:
        logger.error(
            f"Error in async media generation for interaction {interaction_id}: {e}"
        )
        # Update error state in status file
        status_file = Path(states_path) / f"status_{interaction_id}.json"
        with open(status_file, "w") as f:
            json.dump({"error": str(e)}, f)


def check_media_status(interaction_id: str, states_path: str) -> Dict[str, Any]:
    """
    Check if media is ready for a given interaction ID.

    Args:
        interaction_id (str): Unique interaction identifier
        states_path (str): Path to states directory

    Returns:
        Dict[str, Any]: Status dictionary with media readiness information
    """
    status_file = Path(states_path) / f"status_{interaction_id}.json"
    if not status_file.exists():
        return {"audio_ready": False, "video_ready": False}

    try:
        with open(status_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"audio_ready": False, "video_ready": False}


def start_media_generation_thread(
    text: str,
    interaction_id: str,
    message_index: int,
    openai_client,
    audio_path: Path,
    video_path: Path,
    states_path: str,
) -> threading.Thread:
    """
    Start asynchronous media generation in a background thread.

    Args:
        text (str): Text to convert to audio/video
        interaction_id (str): Unique interaction identifier
        message_index (int): Index of message in chat history
        openai_client: OpenAI client instance
        audio_path (Path): Path to audio directory
        video_path (Path): Path to video directory
        states_path (str): Path to states directory

    Returns:
        threading.Thread: The started thread
    """
    thread = threading.Thread(
        target=generate_media_async,
        args=(
            text,
            interaction_id,
            message_index,
            openai_client,
            audio_path,
            video_path,
            states_path,
        ),
        daemon=True,
    )
    thread.start()
    logger.info(
        f"Started async media generation thread for interaction {interaction_id}"
    )
    return thread

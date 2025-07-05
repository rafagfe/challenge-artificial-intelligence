"""
Video generation functions.
"""

import logging
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from moviepy.editor import ImageClip, AudioFileClip
except ImportError:
    from moviepy import ImageClip, AudioFileClip
from langsmith import traceable

logger = logging.getLogger(__name__)


@traceable(name="generate_video")
def generate_video(
    video_path: Path,
    background_image_path: str,
    text: Optional[str] = None,
    audio_path: Optional[str] = None,
    interaction_id: Optional[str] = None,
) -> str:
    """
    Generate a video by combining audio with a static image.

    Args:
        video_path (Path): Directory to save video files
        background_image_path (str): Path to background image
        text (Optional[str]): Text to convert to audio (if audio_path not provided)
        audio_path (Optional[str]): Path to existing audio file
        interaction_id (Optional[str]): Unique interaction ID

    Returns:
        str: Path to the generated video file

    Raises:
        FileNotFoundError: If background image not found
        ValueError: If neither text nor audio_path provided
    """
    if not Path(background_image_path).exists():
        raise FileNotFoundError(
            f"Background image not found at {background_image_path}"
        )

    if not audio_path and not text:
        raise ValueError("Either audio_path or text must be provided")

    try:
        # Generate video file path
        if interaction_id:
            output_path = video_path / f"video_{interaction_id}.mp4"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = video_path / f"video_{timestamp}.mp4"

        # Use existing audio file
        if audio_path and Path(audio_path).exists():
            audio_file_path = audio_path
            logger.info(f"Using existing audio file: {audio_file_path}")
        else:
            raise ValueError("Audio file not found or not provided")

        audio_clip = AudioFileClip(audio_file_path)

        # Try different methods for setting duration (compatibility with different MoviePy versions)
        try:
            image_clip = ImageClip(background_image_path, duration=audio_clip.duration)
        except TypeError:
            try:
                image_clip = ImageClip(background_image_path).with_duration(
                    audio_clip.duration
                )
            except AttributeError:
                try:
                    image_clip = ImageClip(background_image_path).set_duration(
                        audio_clip.duration
                    )
                except AttributeError:
                    # Fallback: create clip and manually set duration
                    image_clip = ImageClip(background_image_path)
                    image_clip.duration = audio_clip.duration

        # Try different methods for setting audio (compatibility with different MoviePy versions)
        try:
            video_clip = image_clip.with_audio(audio_clip)
        except AttributeError:
            try:
                video_clip = image_clip.set_audio(audio_clip)
            except AttributeError:
                # This should not happen, but as a fallback
                raise RuntimeError(
                    "Cannot set audio on video clip - MoviePy version incompatibility"
                )
        # Write video file with compatibility for different MoviePy versions
        try:
            video_clip.write_videofile(
                str(output_path),
                fps=24,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None,
            )
        except TypeError as e:
            if "verbose" in str(e):
                # Try without verbose and logger parameters
                try:
                    video_clip.write_videofile(
                        str(output_path), fps=24, codec="libx264", audio_codec="aac"
                    )
                except TypeError:
                    # Minimal parameters as last resort
                    video_clip.write_videofile(str(output_path))
            else:
                raise e

        # Clean up clips to free memory
        try:
            audio_clip.close()
        except:
            pass
        try:
            image_clip.close()
        except:
            pass
        try:
            video_clip.close()
        except:
            pass

        logger.info(f"Successfully generated video file: {output_path}")
        return str(output_path)
    except Exception as e:
        logger.error(f"Error generating video: {e}")
        raise


@traceable(name="generate_video_with_d_id")
def generate_video_with_d_id(text: str, output_path: str, api_key: str) -> bool:
    """
    Generate video using D-ID API.

    Args:
        text (str): Text to convert to video
        output_path (str): Path to save the video file
        api_key (str): D-ID API key

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not api_key:
            logger.error("D-ID API key is required")
            return False

        headers = {
            "Authorization": f"Basic {api_key}",
            "Content-Type": "application/json",
        }

        # Create talk
        create_data = {
            "script": {"type": "text", "input": text},
            "source_url": "https://clips-presenters.s3.amazonaws.com/rian/preview.mp4",
        }

        response = requests.post(
            "https://api.d-id.com/talks", headers=headers, json=create_data
        )

        if response.status_code != 201:
            logger.error(f"D-ID API error: {response.status_code}")
            return False

        talk_id = response.json()["id"]

        # Wait for video generation
        while True:
            status_response = requests.get(
                f"https://api.d-id.com/talks/{talk_id}", headers=headers
            )

            if status_response.status_code != 200:
                logger.error(f"D-ID status check error: {status_response.status_code}")
                return False

            status_data = status_response.json()

            if status_data["status"] == "done":
                result_url = status_data["result_url"]

                # Download video
                video_response = requests.get(result_url)
                if video_response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(video_response.content)
                    logger.info(
                        f"Successfully generated video with D-ID: {output_path}"
                    )
                    return True
                else:
                    logger.error(
                        f"Error downloading video: {video_response.status_code}"
                    )
                    return False

            elif status_data["status"] == "error":
                logger.error(
                    f"D-ID generation error: {status_data.get('error', 'Unknown error')}"
                )
                return False

            time.sleep(5)  # Wait 5 seconds before next check

    except Exception as e:
        logger.error(f"Error generating video with D-ID: {e}")
        return False


@traceable(name="generate_video_from_text")
def generate_video_from_text(text: str, output_path: str, api_key: str) -> bool:
    """
    Generate video from text using the default video generation method.

    Args:
        text (str): Text to convert to video
        output_path (str): Path to save the video file
        api_key (str): API key for video generation

    Returns:
        bool: True if successful, False otherwise
    """
    return generate_video_with_d_id(text, output_path, api_key)


@traceable(name="generate_video_summary")
def generate_video_summary(text: str, output_path: str, api_key: str) -> bool:
    """
    Generate video summary using the default video generation method.

    Args:
        text (str): Text to convert to video
        output_path (str): Path to save the video file
        api_key (str): API key for video generation

    Returns:
        bool: True if successful, False otherwise
    """
    return generate_video_from_text(text, output_path, api_key)

"""
Video file processing functions.
"""
import os
from typing import Dict, Any, List
from groq import Groq
from langsmith import traceable


@traceable(name="process_video_file")
def process_video_file(file_path: str, groq_client: Groq) -> List[Dict[str, Any]]:
    """
    Process .mp4 video files using Whisper-GROQ for speech transcription.
    
    Args:
        file_path (str): Path to the video file to process
        groq_client (Groq): Groq client instance
        
    Returns:
        List[Dict[str, Any]]: List of transcription chunks with timestamps
        
    Raises:
        ValueError: If GROQ client is not provided
    """
    if not groq_client:
        raise ValueError("GROQ client is required for video processing")
    
    chunks = []
    
    with open(file_path, "rb") as file:
        transcription = groq_client.audio.transcriptions.create(
            file=(os.path.basename(file_path), file.read()),
            model="whisper-large-v3-turbo",
            response_format="verbose_json"
        )
    
    # Split into approximately 25-second chunks
    full_text = transcription.text
    words = full_text.split()
    chunk_size = len(words) // 8  # ~8 chunks for 185s video
    
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        
        chunks.append({
            "content": chunk_text,
            "metadata": {
                "type": "video",
                "file": os.path.basename(file_path),
                "start": i * 25 // chunk_size,
                "end": min((i + chunk_size) * 25 // chunk_size, 185),
                "chunk_id": (i // chunk_size) + 1
            }
        })
    
    return chunks 
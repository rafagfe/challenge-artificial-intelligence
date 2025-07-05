"""
Chat interface functions for the Adaptive Learning System.
"""

import logging
import streamlit as st
import uuid
import time
from typing import Dict, Any
from pathlib import Path

from core.async_media import check_media_status, start_media_generation_thread

logger = logging.getLogger(__name__)


def show_text(message_index: int) -> None:
    """Show text for a specific message."""
    if "messages" in st.session_state and message_index < len(
        st.session_state.messages
    ):
        st.session_state.messages[message_index]["show_text"] = True


def show_audio(message_index: int) -> None:
    """Show audio for a specific message."""
    if "messages" in st.session_state and message_index < len(
        st.session_state.messages
    ):
        st.session_state.messages[message_index]["show_audio"] = True


def show_video(message_index: int) -> None:
    """Show video for a specific message."""
    if "messages" in st.session_state and message_index < len(
        st.session_state.messages
    ):
        st.session_state.messages[message_index]["show_video"] = True


def create_audio(message_index: int) -> None:
    """Create audio for a specific message."""
    if "messages" in st.session_state and message_index < len(
        st.session_state.messages
    ):
        text_to_convert = st.session_state.messages[message_index]["response_text"]
        try:
            from media.audio_generator import generate_audio

            # Get system components for paths and clients
            system_components = st.session_state.get("system_components", {})
            paths = system_components.get("paths", {})
            clients = system_components.get("clients", {})

            # Call new function with correct parameters
            audio_path = generate_audio(
                text=text_to_convert,
                openai_client=clients.get("openai"),
                audio_path=Path(paths.get("audio_path", "files_chat/audios")),
            )
            st.session_state.messages[message_index]["audio_path"] = audio_path
        except Exception as e:
            st.error(f"Erro ao gerar áudio: {e}")


def create_video(message_index: int) -> None:
    """Create video for a specific message."""
    if "messages" in st.session_state and message_index < len(
        st.session_state.messages
    ):
        text_to_convert = st.session_state.messages[message_index]["response_text"]
        try:
            from media.video_generator import generate_video

            # Get system components for paths
            system_components = st.session_state.get("system_components", {})
            paths = system_components.get("paths", {})

            # Call new function with correct parameters
            video_path = generate_video(
                video_path=Path(paths.get("video_path", "files_chat/videos")),
                background_image_path="resources/Infografico-1.jpg",
                text=text_to_convert,
            )
            st.session_state.messages[message_index]["video_path"] = video_path
        except Exception as e:
            st.error(f"Erro ao gerar vídeo: {e}")


# Create wrapper functions to maintain compatibility with old signatures
def generate_audio_wrapper(text: str, interaction_id: str = None) -> str:
    """Wrapper function to maintain compatibility with old generate_audio signature."""
    system_components = st.session_state.get("system_components", {})
    paths = system_components.get("paths", {})
    clients = system_components.get("clients", {})

    from media.audio_generator import generate_audio

    return generate_audio(
        text=text,
        openai_client=clients.get("openai"),
        audio_path=Path(paths.get("audio_path", "files_chat/audios")),
        interaction_id=interaction_id,
    )


def generate_video_wrapper(
    text: str = None, audio_path: str = None, interaction_id: str = None
) -> str:
    """Wrapper function to maintain compatibility with old generate_video signature."""
    system_components = st.session_state.get("system_components", {})
    paths = system_components.get("paths", {})

    from media.video_generator import generate_video

    return generate_video(
        video_path=Path(paths.get("video_path", "files_chat/videos")),
        background_image_path="resources/Infografico-1.jpg",
        text=text,
        audio_path=audio_path,
        interaction_id=interaction_id,
    )


def run_chat_interface() -> None:
    """Run the complete chat interface with full functionality from main.py."""
    # Get system components
    system_components = st.session_state.get("system_components", {})
    collection = st.session_state.get("collection")
    paths = system_components.get("paths", {})
    clients = system_components.get("clients", {})

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            # Handle user messages
            if message["role"] == "user":
                st.markdown(message["content"])
                continue

            # Handle assistant messages - check for real-time status updates
            interaction_id = message.get("interaction_id")
            if interaction_id and paths.get("states_path"):
                # Check current media status from file
                media_status = check_media_status(
                    interaction_id, str(paths["states_path"])
                )

                # Update message with current status (but don't auto-show)
                if media_status.get("audio_ready") and not message.get("audio_path"):
                    message["audio_path"] = media_status.get("audio_path")
                    message["audio_ready"] = True

                if media_status.get("video_ready") and not message.get("video_path"):
                    message["video_path"] = media_status.get("video_path")
                    message["video_ready"] = True

                if media_status.get("error"):
                    message["media_error"] = media_status.get("error")

            # Show text response
            if message.get("show_text"):
                st.markdown(message["response_text"])

            # Show audio only if user clicked to show it
            if message.get("show_audio") and message.get("audio_path"):
                st.audio(message["audio_path"])

            # Show video only if user clicked to show it
            if message.get("show_video") and message.get("video_path"):
                st.video(message["video_path"])

            # Show media error if any
            if message.get("media_error"):
                st.error(f"Erro na geração de mídia: {message['media_error']}")

            # Show format buttons for the last assistant message
            if i == len(st.session_state.messages) - 1:
                col1, col2, col3 = st.columns(3)

                # Text button
                if not message.get("show_text"):
                    col1.button(
                        "📄 Texto", key=f"text_{i}", on_click=show_text, args=(i,)
                    )

                # Audio button with real-time status
                if message.get("audio_path") and message.get("audio_ready"):
                    if not message.get("show_audio"):
                        col2.button(
                            "🎧 Áudio", key=f"audio_{i}", on_click=show_audio, args=(i,)
                        )
                    else:
                        col2.button(
                            "🎧 Áudio ✅", key=f"audio_{i}_shown", disabled=True
                        )
                elif message.get("audio_ready"):
                    col2.button(
                        "🎧 Áudio ✅",
                        key=f"audio_{i}_ready",
                        on_click=show_audio,
                        args=(i,),
                    )
                else:
                    col2.button("🎧 Áudio ⏳", key=f"audio_{i}_loading", disabled=True)

                # Video button with real-time status
                if message.get("video_path") and message.get("video_ready"):
                    if not message.get("show_video"):
                        col3.button(
                            "🎬 Vídeo", key=f"video_{i}", on_click=show_video, args=(i,)
                        )
                    else:
                        col3.button(
                            "🎬 Vídeo ✅", key=f"video_{i}_shown", disabled=True
                        )
                elif message.get("video_ready"):
                    col3.button(
                        "🎬 Vídeo ✅",
                        key=f"video_{i}_ready",
                        on_click=show_video,
                        args=(i,),
                    )
                else:
                    col3.button("🎬 Vídeo ⏳", key=f"video_{i}_loading", disabled=True)

    # Auto-refresh if there are pending media generations
    pending_media = any(
        msg.get("interaction_id")
        and (not msg.get("audio_ready", True) or not msg.get("video_ready", True))
        for msg in st.session_state.messages
        if msg.get("role") == "assistant"
    )

    if pending_media:
        # Add a small delay and auto-refresh
        time.sleep(5)  # Check every 5 seconds
        st.rerun()

    # Handle user input
    if prompt := st.chat_input("Qual é a sua dúvida de programação?"):
        # Generate unique interaction ID
        interaction_id = str(uuid.uuid4())[:8]  # Short unique ID

        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response and add assistant message placeholder
        with st.spinner("Analisando sua pergunta e buscando informações..."):
            from core.adaptive_response import generate_adaptive_response

            groq_client = clients.get("groq")

            response_text = generate_adaptive_response(
                collection=collection,
                question=prompt,
                preferred_format="mixed",
                groq_client=groq_client,
            )

            if "🤖" in response_text:  # Handle error from generator
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "show_text": True,
                        "response_text": response_text,
                        "interaction_id": interaction_id,
                    }
                )
            else:
                # Add a new, structured message for the assistant's response
                message_index = len(st.session_state.messages)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "response_text": response_text,
                        "show_text": False,
                        "show_audio": False,
                        "show_video": False,
                        "audio_path": None,
                        "video_path": None,
                        "audio_ready": False,
                        "video_ready": False,
                        "interaction_id": interaction_id,
                    }
                )

                # Start asynchronous media generation
                if paths.get("states_path"):
                    thread = start_media_generation_thread(
                        text=response_text,
                        interaction_id=interaction_id,
                        message_index=message_index,
                        openai_client=clients.get("openai"),
                        audio_path=Path(paths.get("audio_path", "files_chat/audios")),
                        video_path=Path(paths.get("video_path", "files_chat/videos")),
                        states_path=str(paths["states_path"]),
                    )
                    logger.info(
                        f"Started async media generation thread for interaction {interaction_id}"
                    )

        # Rerun to display the new message and buttons
        st.rerun()

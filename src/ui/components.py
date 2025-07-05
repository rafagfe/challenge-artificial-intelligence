"""
Reusable UI components for Streamlit application.
"""

import streamlit as st
from typing import Dict, Any, Optional, List


def show_system_status(available_services: Dict[str, bool]) -> None:
    """
    Display system status with available services.

    Args:
        available_services (Dict[str, bool]): Dictionary of service availability
    """
    st.sidebar.markdown("### 🔧 Status do Sistema")

    for service, is_available in available_services.items():
        if is_available:
            st.sidebar.success(f"✅ {service.upper()}")
        else:
            st.sidebar.error(f"❌ {service.upper()}")


def show_configuration_panel(system_components: Dict[str, Any]) -> None:
    """
    Display configuration panel in sidebar.

    Args:
        system_components (Dict[str, Any]): System components dictionary
    """
    with st.sidebar.expander("⚙️ Configurações"):
        st.json(
            {
                "Modelos": system_components["model_settings"],
                "Processamento": system_components["processing_settings"],
                "ChromaDB": system_components["chromadb_settings"],
            }
        )


def show_media_buttons(message_index: int, interaction_id: str) -> Dict[str, bool]:
    """
    Display media format buttons for a message.

    Args:
        message_index (int): Index of the message
        interaction_id (str): Unique interaction ID

    Returns:
        Dict[str, bool]: Dictionary of button states
    """
    col1, col2, col3 = st.columns(3)

    button_states = {"text": False, "audio": False, "video": False}

    with col1:
        if st.button("📄 Texto", key=f"text_{interaction_id}"):
            button_states["text"] = True

    with col2:
        if st.button("🎧 Áudio", key=f"audio_{interaction_id}"):
            button_states["audio"] = True

    with col3:
        if st.button("🎬 Vídeo", key=f"video_{interaction_id}"):
            button_states["video"] = True

    return button_states


def show_loading_indicator(text: str = "Processando...") -> None:
    """
    Show loading indicator with custom text.

    Args:
        text (str): Loading text to display
    """
    st.info(f"⏳ {text}")


def show_error_message(error: str, context: str = "") -> None:
    """
    Display formatted error message.

    Args:
        error (str): Error message
        context (str): Additional context
    """
    if context:
        st.error(f"❌ Erro em {context}: {error}")
    else:
        st.error(f"❌ {error}")


def show_success_message(message: str) -> None:
    """
    Display success message.

    Args:
        message (str): Success message
    """
    st.success(f"✅ {message}")


def show_info_message(message: str) -> None:
    """
    Display info message.

    Args:
        message (str): Info message
    """
    st.info(f"ℹ️ {message}")


def show_metrics_dashboard(collection, system_components: Dict[str, Any]) -> None:
    """
    Display metrics dashboard.

    Args:
        collection: ChromaDB collection
        system_components: System components
    """
    st.markdown("### 📊 Métricas do Sistema")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        doc_count = collection.count() if collection else 0
        st.metric("Documentos", doc_count)

    with col2:
        active_services = sum(system_components["available_services"].values())
        total_services = len(system_components["available_services"])
        st.metric("Serviços Ativos", f"{active_services}/{total_services}")

    with col3:
        st.metric("Processadores", "5")  # text, pdf, video, image, json

    with col4:
        st.metric("Módulos", "7")  # config, ai, processors, core, media, ui, utils


def show_architecture_diagram() -> None:
    """
    Display system architecture diagram.
    """
    st.markdown(
        """
    ### 🏗️ Arquitetura do Sistema
    
    ```mermaid
    graph TD
        A[main_refactored.py] --> B[config/settings.py]
        A --> C[ai/llm_client.py]
        A --> D[core/indexing.py]
        A --> E[ui/components.py]
        
        D --> F[processors/]
        F --> G[text_processor.py]
        F --> H[pdf_processor.py]
        F --> I[video_processor.py]
        F --> J[image_processor.py]
        F --> K[json_processor.py]
        
        A --> L[media/]
        L --> M[audio_generator.py]
        L --> N[video_generator.py]
        
        A --> O[utils/logging_utils.py]
        
        C --> P[Groq API]
        C --> Q[OpenAI API]
        C --> R[LangSmith API]
        
        D --> S[ChromaDB]
        D --> T[SQLite]
    ```
    """
    )


def show_usage_examples() -> None:
    """
    Display usage examples for the modular functions.
    """
    st.markdown("### 📚 Exemplos de Uso")

    tab1, tab2, tab3 = st.tabs(["Configuração", "Processamento", "Geração de Mídia"])

    with tab1:
        st.code(
            """
# Configuração do sistema
from src.config.settings import get_api_keys, get_paths, ensure_directories

api_keys = get_api_keys()
paths = get_paths()
ensure_directories()
        """,
            language="python",
        )

    with tab2:
        st.code(
            """
# Processamento de arquivos
from src.processors import process_text_file, process_pdf_file
from src.core.indexing import process_all_files, index_documents

# Processar arquivo específico
doc = process_text_file("documento.txt")

# Processar todos os arquivos
documents = process_all_files("./resources", groq_client)
index_documents(collection, documents)
        """,
            language="python",
        )

    with tab3:
        st.code(
            """
# Geração de mídia
from src.media.audio_generator import generate_audio
from src.media.video_generator import generate_video

# Gerar áudio
audio_path = generate_audio(
    text="Texto para áudio",
    openai_client=openai_client,
    audio_path=paths["audio_path"]
)

# Gerar vídeo
video_path = generate_video(
    video_path=paths["video_path"],
    background_image_path="bg.jpg",
    audio_path=audio_path
)
        """,
            language="python",
        )


def create_file_uploader(accepted_types: List[str], key: str) -> Optional[Any]:
    """
    Create a file uploader component.

    Args:
        accepted_types (List[str]): List of accepted file types
        key (str): Unique key for the uploader

    Returns:
        Optional[Any]: Uploaded file or None
    """
    return st.file_uploader(
        "📁 Fazer upload de arquivo",
        type=accepted_types,
        key=key,
        help=f"Tipos aceitos: {', '.join(accepted_types)}",
    )


# Additional components required by tests


def display_api_key_inputs(api_keys: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Display API key input fields in sidebar.

    Args:
        api_keys (Optional[Dict[str, str]]): Existing API keys

    Returns:
        Dict[str, str]: Dictionary of API keys
    """
    with st.sidebar.expander("🔑 Configurações de API"):
        return {
            "groq_api_key": st.text_input(
                "Groq API Key",
                value=api_keys.get("groq_api_key", "") if api_keys else "",
                type="password",
            ),
            "openai_api_key": st.text_input(
                "OpenAI API Key",
                value=api_keys.get("openai_api_key", "") if api_keys else "",
                type="password",
            ),
            "elevenlabs_api_key": st.text_input(
                "ElevenLabs API Key",
                value=api_keys.get("elevenlabs_api_key", "") if api_keys else "",
                type="password",
            ),
            "d_id_api_key": st.text_input(
                "D-ID API Key",
                value=api_keys.get("d_id_api_key", "") if api_keys else "",
                type="password",
            ),
            "langsmith_api_key": st.text_input(
                "LangSmith API Key",
                value=api_keys.get("langsmith_api_key", "") if api_keys else "",
                type="password",
            ),
        }


def display_file_uploader(accepted_types: Optional[List[str]] = None) -> Optional[Any]:
    """
    Display file uploader component.

    Args:
        accepted_types (Optional[List[str]]): List of accepted file types

    Returns:
        Optional[Any]: Uploaded files or None
    """
    types = accepted_types or ["txt", "pdf", "json", "jpg", "jpeg", "png", "mp4"]
    return st.file_uploader(
        "📁 Upload de Arquivos",
        type=types,
        accept_multiple_files=True,
        help=f"Tipos aceitos: {', '.join(types)}",
    )


def display_processing_progress(message: str = "Processando...", value: int = 0):
    """
    Display processing progress bar.

    Args:
        message (str): Progress message
        value (int): Progress value (0-100)

    Returns:
        Progress bar object
    """
    if message != "Processando...":
        st.info(message)
    return st.progress(value)


def display_search_interface(placeholder: str = "Digite sua consulta..."):
    """
    Display search interface with input and button.

    Args:
        placeholder (str): Placeholder text for input

    Returns:
        Tuple[str, bool]: Query text and search button state
    """
    query = st.text_input("🔍 Buscar", placeholder=placeholder)
    search_clicked = st.button("Pesquisar")
    return query, search_clicked


def display_results(results: List[Dict[str, Any]]) -> None:
    """
    Display search results.

    Args:
        results (List[Dict[str, Any]]): List of search results
    """
    if not results:
        st.info("Nenhum resultado encontrado.")
        return

    for i, result in enumerate(results):
        with st.expander(f"Resultado {i+1}"):
            st.write(result.get("content", ""))
            if "metadata" in result:
                st.json(result["metadata"])
            if "score" in result:
                st.write(f"Score: {result['score']:.2f}")


def display_media_generation_section(content: str = "") -> tuple:
    """
    Display media generation section.

    Args:
        content (str): Content for media generation

    Returns:
        Tuple[bool, bool, bool]: Audio enabled, video enabled, generate clicked
    """
    st.markdown("### 🎬 Geração de Mídia")

    if content:
        st.text_area("Conteúdo", value=content, disabled=True)

    col1, col2 = st.columns(2)

    with col1:
        audio_enabled = st.checkbox("🎧 Gerar Áudio")

    with col2:
        video_enabled = st.checkbox("🎬 Gerar Vídeo")

    generate_clicked = st.button("Gerar Mídia")

    return audio_enabled, video_enabled, generate_clicked


def display_sidebar_controls() -> Dict[str, Any]:
    """
    Display sidebar controls.

    Returns:
        Dict[str, Any]: Control values
    """
    model = st.sidebar.selectbox("Modelo", ["Groq", "OpenAI"])
    max_results = st.sidebar.slider("Máximo de Resultados", 1, 20, 5)
    clear_cache = st.sidebar.button("Limpar Cache")

    return {"model": model, "max_results": max_results, "clear_cache": clear_cache}


def display_file_manager(directory: str) -> None:
    """
    Display file manager in sidebar.

    Args:
        directory (str): Directory path to manage
    """
    with st.sidebar.expander("📁 Gerenciador de Arquivos"):
        from pathlib import Path

        dir_path = Path(directory)
        if dir_path.exists():
            files = list(dir_path.iterdir())
            if files:
                for file in files:
                    st.write(f"📄 {file.name}")
            else:
                st.write("Nenhum arquivo encontrado")
        else:
            st.write("Diretório não encontrado")


def display_configuration_panel(
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Display configuration panel in sidebar.

    Args:
        config (Optional[Dict[str, Any]]): Existing configuration

    Returns:
        Dict[str, Any]: Configuration values
    """
    with st.sidebar.expander("⚙️ Configurações"):
        language = st.selectbox(
            "Idioma",
            ["pt-br", "en", "es"],
            index=(
                0
                if not config
                else ["pt-br", "en", "es"].index(config.get("language", "pt-br"))
            ),
        )

        temperature = st.slider(
            "Temperatura", 0.0, 1.0, config.get("temperature", 0.7) if config else 0.7
        )

        max_tokens = st.number_input(
            "Máximo de Tokens", value=config.get("max_tokens", 1000) if config else 1000
        )

        return {
            "language": language,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

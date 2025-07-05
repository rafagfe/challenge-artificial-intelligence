#!/usr/bin/env python3
"""
Refactored main application using modular functions.
"""
import logging
import streamlit as st
from dotenv import load_dotenv
import chromadb

# Import configuration functions
from config.settings import (
    get_api_keys,
    get_model_settings,
    get_paths,
    get_processing_settings,
    get_chromadb_settings,
    ensure_directories,
    validate_api_keys,
)

# Import AI clients
from ai.llm_client import create_all_clients

# Import core functions
from core.indexing import (
    process_all_files,
    index_documents,
    get_resources_state,
    load_index_state,
    save_index_state,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_system():
    """
    Initialize the system with all necessary components.

    Returns:
        dict: Dictionary containing all system components
    """
    logger.info("Setting up system components...")

    # Get configuration
    api_keys = get_api_keys()
    model_settings = get_model_settings()
    paths = get_paths()
    processing_settings = get_processing_settings()
    chromadb_settings = get_chromadb_settings()

    # Ensure directories exist
    ensure_directories()

    # Create AI clients
    clients = create_all_clients(api_keys)

    # Setup ChromaDB
    chroma_client = chromadb.PersistentClient(path=str(paths["chroma_db_path"]))

    # Validate API keys
    available_services = validate_api_keys()
    logger.info(f"Available services: {available_services}")

    return {
        "api_keys": api_keys,
        "model_settings": model_settings,
        "paths": paths,
        "processing_settings": processing_settings,
        "chromadb_settings": chromadb_settings,
        "clients": clients,
        "chroma_client": chroma_client,
        "available_services": available_services,
    }


def setup_content_indexing(system_components):
    """
    Setup content indexing with change detection.

    Args:
        system_components (dict): System components from setup_system()

    Returns:
        chromadb.Collection: ChromaDB collection with indexed content
    """
    paths = system_components["paths"]
    clients = system_components["clients"]
    chroma_client = system_components["chroma_client"]
    chromadb_settings = system_components["chromadb_settings"]

    collection_name = chromadb_settings["collection_name"]
    index_state_file = paths["chroma_db_path"] / "index.state.json"

    # Check if content needs re-indexing
    current_resources_state = get_resources_state(str(paths["resources_path"]))
    last_indexed_state = load_index_state(index_state_file)

    if current_resources_state != last_indexed_state:
        logger.info("Resource files have changed. Re-indexing...")

        # Clean up old collection if it exists
        existing_collections = [col.name for col in chroma_client.list_collections()]
        if collection_name in existing_collections:
            chroma_client.delete_collection(name=collection_name)
            logger.info(f"Deleted existing collection: {collection_name}")

        # Create new collection
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Adaptive learning content collection"},
        )

        # Process and index documents
        documents = process_all_files(str(paths["resources_path"]), clients["groq"])

        if documents:
            index_documents(collection, documents)

        # Save new state
        save_index_state(index_state_file, current_resources_state)
        logger.info("Indexing complete and state saved.")
    else:
        logger.info("Content is up-to-date. Using existing index.")
        collection = chroma_client.get_or_create_collection(name=collection_name)

    return collection


def main():
    """
    Main application function that orchestrates the adaptive learning system
    with a Streamlit interface. This replicates the exact functionality of the
    original main.py with modular architecture.
    """
    st.set_page_config(page_title="Sistema de Aprendizagem Adaptativa", page_icon="📖")

    st.title("Sistema de Aprendizagem Adaptativa")
    st.markdown(
        """
    **Converse com o assistente inteligente para aprofundar seus conhecimentos!**
    
    Faça uma pergunta sobre programação e a IA irá:
    1. Analisar seu nível de conhecimento.
    2. Gerar uma resposta personalizada.
    3. Oferecer o conteúdo em formato de **texto, áudio ou vídeo**.
    """
    )

    # Initialize system components using a robust pattern
    # The spinner runs on each script execution, but the guarded block runs
    # only once per session.
    with st.spinner("Inicializando e verificando conteúdo..."):
        if "db_initialized" not in st.session_state:
            # Initialize system
            system_components = setup_system()
            paths = system_components["paths"]
            clients = system_components["clients"]
            chroma_client = system_components["chroma_client"]
            chromadb_settings = system_components["chromadb_settings"]

            # Setup database
            from core.database import setup_database

            setup_database(str(paths["database_path"]))

            collection_name = chromadb_settings["collection_name"]
            index_state_file = paths["chroma_db_path"] / "index.state.json"

            # Check if content needs re-indexing
            from core.indexing import (
                get_resources_state,
                load_index_state,
                save_index_state,
                setup_chromadb,
                process_all_files,
                index_documents,
            )

            current_resources_state = get_resources_state(str(paths["resources_path"]))
            last_indexed_state = load_index_state(index_state_file)

            # Re-index only if files have changed
            if current_resources_state != last_indexed_state:
                logger.info(
                    "Resource files have changed or state file not found. Re-indexing..."
                )

                # Clean up old collection if it exists
                existing_collections = [
                    col.name for col in chroma_client.list_collections()
                ]
                if collection_name in existing_collections:
                    chroma_client.delete_collection(name=collection_name)
                    logger.info(f"Deleted existing collection: {collection_name}")

                # Process and index documents
                collection = setup_chromadb(chroma_client, collection_name)
                documents = process_all_files(
                    str(paths["resources_path"]), clients.get("groq")
                )
                if documents:
                    index_documents(collection, documents)

                save_index_state(index_state_file, current_resources_state)
                logger.info("Indexing complete and new state saved.")
            else:
                logger.info("Content is up-to-date. Skipping indexing.")

            # Set session state at the end of the one-time setup
            st.session_state.collection = chroma_client.get_or_create_collection(
                name=collection_name
            )
            st.session_state.system_components = system_components
            st.session_state.db_initialized = True

    # Run the chat interface with full original functionality
    from ui.chat_interface import run_chat_interface

    run_chat_interface()


# Additional functions required by tests


def initialize_application():
    """
    Initialize the application (wrapper for setup_system).
    """
    st.set_page_config(
        page_title="Sistema de Aprendizagem Adaptativa Refatorado", 
        page_icon="📖"
    )

    if "system_initialized" not in st.session_state:
        system_components = setup_system()
        collection = setup_content_indexing(system_components)

        st.session_state.system_components = system_components
        st.session_state.collection = collection
        st.session_state.system_initialized = True


def process_uploaded_files(uploaded_files):
    """
    Process uploaded files and save them to resources directory.

    Args:
        uploaded_files: List of uploaded files from Streamlit

    Returns:
        List of file paths that were saved
    """
    if not uploaded_files:
        return []

    saved_paths = []

    try:
        from config.settings import get_paths

        paths = get_paths()
        resources_path = paths["resources_path"]

        for uploaded_file in uploaded_files:
            file_path = resources_path / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_paths.append(str(file_path))

    except Exception as e:
        logger.error(f"Error processing uploaded files: {e}")
        return []

    return saved_paths


def save_uploaded_file(uploaded_file, directory):
    """
    Save a single uploaded file to directory.

    Args:
        uploaded_file: Streamlit uploaded file
        directory: Directory to save to

    Returns:
        str: Path to saved file
    """
    from pathlib import Path

    dir_path = Path(directory)
    dir_path.mkdir(exist_ok=True)

    file_path = dir_path / uploaded_file.name

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(file_path)


def search_documents(query, max_results=5):
    """
    Search documents in the collection.

    Args:
        query (str): Search query
        max_results (int): Maximum number of results

    Returns:
        List of search results
    """
    if not query or not query.strip():
        return []

    try:
        if "collection" not in st.session_state:
            return []

        collection = st.session_state.collection

        results = collection.query(query_texts=[query], n_results=max_results)

        documents = []
        if results["documents"] and results["documents"][0]:
            for i, (doc, metadata, distance) in enumerate(
                zip(
                    results["documents"][0],
                    (
                        results["metadatas"][0]
                        if results["metadatas"]
                        else [{}] * len(results["documents"][0])
                    ),
                    (
                        results["distances"][0]
                        if results["distances"]
                        else [0.0] * len(results["documents"][0])
                    ),
                )
            ):
                documents.append(
                    {
                        "content": doc,
                        "metadata": metadata,
                        "score": 1.0 - distance,  # Convert distance to similarity score
                    }
                )

        return documents

    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return []


def process_search_query(query, api_keys, model="groq"):
    """
    Process search query using AI clients.

    Args:
        query (str): Search query
        api_keys (dict): API keys dictionary
        model (str): Model to use (groq, openai)

    Returns:
        str: Generated response or None
    """
    try:
        from ai.llm_client import create_all_clients

        clients = create_all_clients(api_keys)

        if model == "groq" and clients["groq"]:
            response = clients["groq"].chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": query}],
                max_tokens=1000,
                temperature=0.7,
            )
            return response.choices[0].message.content

        elif model == "openai" and clients["openai"]:
            response = clients["openai"].chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": query}],
                max_tokens=1000,
                temperature=0.7,
            )
            return response.choices[0].message.content

        return None

    except Exception as e:
        logger.error(f"Error processing search query: {e}")
        return None


def generate_media_content(
    content, audio_enabled=False, video_enabled=False, api_keys=None
):
    """
    Generate media content (audio and/or video).

    Args:
        content (str): Content to convert to media
        audio_enabled (bool): Whether to generate audio
        video_enabled (bool): Whether to generate video
        api_keys (dict): API keys dictionary

    Returns:
        bool: True if successful, False otherwise
    """
    if not content or (not audio_enabled and not video_enabled):
        return False

    try:
        from config.settings import get_paths
        from media.audio_generator import generate_audio_summary
        from media.video_generator import generate_video_summary

        paths = get_paths()
        success = True

        if audio_enabled:
            audio_path = paths["audio_path"] / "generated_audio.mp3"
            audio_result = generate_audio_summary(content, str(audio_path))
            success = success and audio_result

        if video_enabled and api_keys:
            video_path = paths["video_path"] / "generated_video.mp4"
            d_id_key = api_keys.get("d_id_api_key")
            video_result = generate_video_summary(content, str(video_path), d_id_key)
            success = success and video_result

        return success

    except Exception as e:
        logger.error(f"Error generating media content: {e}")
        return False

    # Show architecture details in expander
    with st.expander("🏗️ Arquitetura do Sistema"):
        st.markdown(
            """
        **Organização modular refatorada:**
        
        ```
        src/
        ├── config/settings.py              # Configurações centralizadas
        ├── ai/llm_client.py               # Clientes de IA
        ├── processors/                     # Processadores por tipo
        │   ├── text_processor.py
        │   ├── pdf_processor.py
        │   ├── video_processor.py
        │   ├── image_processor.py
        │   └── json_processor.py
        ├── core/                          # Funcionalidades principais
        │   ├── indexing.py               # Indexação de documentos
        │   ├── search.py                 # Busca e reranking
        │   ├── question_analysis.py      # Análise de perguntas
        │   ├── adaptive_response.py      # Geração de respostas adaptativas
        │   └── database.py               # Persistência de dados
        ├── media/                         # Geração de mídia
        │   ├── audio_generator.py
        │   └── video_generator.py
        ├── ui/                           # Interface do usuário
        │   ├── components.py
        │   └── chat_interface.py         # Interface de chat completa
        ├── utils/logging_utils.py        # Utilitários
        └── main_refactored.py           # Aplicação principal
        ```
        
        **🎯 Funcionalidades implementadas:**
        - ✅ Análise automática do nível de conhecimento do usuário
        - ✅ Geração de respostas adaptativas personalizadas  
        - ✅ Busca semântica com reranking inteligente
        - ✅ Validação de escopo de perguntas
        - ✅ Interface de chat com botões para texto/áudio/vídeo
        - ✅ Geração assíncrona de mídia
        - ✅ Persistência de interações no banco de dados
        - ✅ Processamento de múltiplos tipos de arquivo
        - ✅ Configuração centralizada e modular
        """
        )

    # Run the chat interface
    from ui.chat_interface import run_chat_interface

    run_chat_interface()


if __name__ == "__main__":
    main()

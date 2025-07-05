"""
Document indexing and processing functions.
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from langsmith import traceable

from processors.text_processor import process_text_file
from processors.pdf_processor import process_pdf_file
from processors.video_processor import process_video_file
from processors.image_processor import process_image_file
from processors.json_processor import process_json_file

logger = logging.getLogger(__name__)


def setup_chromadb(chroma_client, collection_name: str = "learning_content"):
    """
    Initialize ChromaDB collection for vector storage and semantic search.
    
    Creates or retrieves the collection that will store
    processed documents with their embeddings for efficient similarity search.
    
    Args:
        chroma_client: ChromaDB client instance
        collection_name (str): Name of the collection to create/retrieve
        
    Returns:
        chromadb.Collection: The initialized ChromaDB collection
    """
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "Adaptive learning content collection"}
    )
    logger.info(f"ChromaDB collection '{collection_name}' initialized successfully")
    return collection


@traceable(name="processing_all_files")
def process_all_files(resources_path: str, groq_client=None) -> List[Dict[str, Any]]:
    """
    Process all files in the resources directory for indexing.
    
    Args:
        resources_path (str): Path to resources directory
        groq_client: Groq client for video processing
        
    Returns:
        List[Dict[str, Any]]: List of processed documents ready for indexing
    """
    documents = []
    resources_path = Path(resources_path)
    
    if not resources_path.exists():
        logger.error(f"Resources directory not found: {resources_path}")
        return documents
    
    logger.info(f"Processing files from: {resources_path}")
    
    for file_path in resources_path.iterdir():
        if file_path.is_file():
            try:
                if file_path.suffix.lower() == '.txt':
                    doc = process_text_file(str(file_path))
                    documents.append(doc)
                elif file_path.suffix.lower() == '.pdf':
                    docs = process_pdf_file(str(file_path))
                    documents.extend(docs)
                elif file_path.suffix.lower() in ['.jpg', '.jpeg']:
                    doc = process_image_file(str(file_path))
                    documents.append(doc)
                elif file_path.suffix.lower() == '.mp4':
                    docs = process_video_file(str(file_path), groq_client)
                    documents.extend(docs)
                elif file_path.suffix.lower() == '.json':
                    docs = process_json_file(str(file_path))
                    documents.extend(docs)
                else:
                    logger.info(f"Skipping unsupported file type: {file_path}")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
    
    logger.info(f"Successfully processed {len(documents)} documents from {resources_path}")
    return documents


@traceable(name="index_documents")
def index_documents(collection, documents: List[Dict[str, Any]]) -> None:
    """
    Index processed documents in ChromaDB for semantic search.
    
    Args:
        collection: ChromaDB collection instance
        documents (List[Dict[str, Any]]): List of documents with content and metadata
        
    Returns:
        None
    """
    texts = [doc["content"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    ids = [f"doc_{i}_{int(datetime.now().timestamp())}" for i in range(len(documents))]
    
    collection.add(documents=texts, metadatas=metadatas, ids=ids)
    logger.info(f"Successfully indexed {len(documents)} documents in ChromaDB")


def get_resources_state(directory: str) -> Dict[str, float]:
    """
    Get the state of files in a directory based on their modification times.
    
    Args:
        directory (str): The path to the directory.
        
    Returns:
        Dict[str, float]: A dictionary mapping filenames to their last modification time.
    """
    state = {}
    resources_path = Path(directory)
    if not resources_path.exists():
        return state
    
    for file_path in resources_path.iterdir():
        if file_path.is_file():
            state[file_path.name] = file_path.stat().st_mtime
    return state


def save_index_state(state_file: Path, state: Dict[str, float]) -> None:
    """
    Save the current resource state to a JSON file.
    
    Args:
        state_file (Path): The path to the state file.
        state (Dict[str, float]): The state dictionary to save.
    """
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)


def load_index_state(state_file: Path) -> Dict[str, float]:
    """
    Load the resource state from a JSON file.
    
    Args:
        state_file (Path): The path to the state file.
        
    Returns:
        Dict[str, float]: The loaded state dictionary, or an empty dict if not found.
    """
    if not state_file.exists():
        return {}
    
    with open(state_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}  # Handle case of corrupted state file 
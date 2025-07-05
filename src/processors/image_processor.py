"""
Image file processing functions.
"""

import os
from typing import Dict, Any
from docling.document_converter import DocumentConverter
from langsmith import traceable


@traceable(name="process_image_file")
def process_image_file(file_path: str) -> Dict[str, Any]:
    """
    Process image files (.jpg, .jpeg, .png) using Docling document converter.

    Args:
        file_path (str): Path to the image file to process

    Returns:
        Dict[str, Any]: Dictionary containing extracted content and metadata
    """
    doc_converter = DocumentConverter()
    result = doc_converter.convert(file_path)
    content = result.document.export_to_text()

    metadata = {
        "type": "image",
        "file": os.path.basename(file_path),
        "description": content or "Visual content available",
    }

    return {"content": content or "Visual content available", "metadata": metadata}

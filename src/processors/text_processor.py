"""
Text file processing functions.
"""
import os
from typing import Dict, Any
from langsmith import traceable


@traceable(name="process_text_file")
def process_text_file(file_path: str) -> Dict[str, Any]:
    """
    Process .txt files using direct file reading.
    
    Args:
        file_path (str): Path to the text file to process
        
    Returns:
        Dict[str, Any]: Dictionary containing extracted content and metadata
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        metadata = {
            "type": "text",
            "file": os.path.basename(file_path),
            "source": "file"
        }
        
        return {"content": content, "metadata": metadata}
    except FileNotFoundError:
        return None
    except Exception as e:
        # Log error but return None for testing purposes
        return None 
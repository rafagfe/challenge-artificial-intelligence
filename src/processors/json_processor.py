"""
JSON file processing functions.
"""

import os
import json
from typing import Dict, Any, List
from langsmith import traceable


@traceable(name="process_json_file")
def process_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Process .json files containing structured educational data.

    Args:
        file_path (str): Path to the JSON file to process

    Returns:
        List[Dict[str, Any]]: List of structured data chunks with metadata
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    chunks = []

    if isinstance(data, list):
        for i, item in enumerate(data):
            content = json.dumps(item, ensure_ascii=False, indent=2)
            chunks.append(
                {
                    "content": content,
                    "metadata": {
                        "type": "structured",
                        "file": os.path.basename(file_path),
                        "exercise_id": i + 1,
                    },
                }
            )
    elif isinstance(data, dict):
        # Handle single object (like exercises with content array)
        if "content" in data and isinstance(data["content"], list):
            # Process exercise content
            for i, item in enumerate(data["content"]):
                question_content = f"Title: {item.get('title', '')}\n"
                if "content" in item and "html" in item["content"]:
                    question_content += f"Question: {item['content']['html']}\n"
                    if "options" in item["content"]:
                        question_content += "Options:\n"
                        for opt in item["content"]["options"]:
                            opt_text = opt.get("content", {}).get("html", "")
                            correct = "✓" if opt.get("correct", False) else "✗"
                            question_content += f"  {correct} {opt_text}\n"

                chunks.append(
                    {
                        "content": question_content,
                        "metadata": {
                            "type": "exercise",
                            "file": os.path.basename(file_path),
                            "exercise_id": i + 1,
                            "subject": data.get("name", "Unknown"),
                        },
                    }
                )
        else:
            # Process as single structured document
            content = json.dumps(data, ensure_ascii=False, indent=2)
            chunks.append(
                {
                    "content": content,
                    "metadata": {
                        "type": "structured",
                        "file": os.path.basename(file_path),
                        "exercise_id": 1,
                    },
                }
            )

    return chunks

"""
Database functions for the Adaptive Learning System.
"""

import json
import sqlite3
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_database(database_path: str) -> None:
    """
    Initialize SQLite database for storing user interactions.

    Creates the user_interactions table if it doesn't exist, which stores:
    - User ID and timestamp
    - Identified knowledge gaps (JSON)
    - Preferred learning format
    - Generated personalized content

    Args:
        database_path (str): Path to the SQLite database file

    Returns:
        None
    """
    try:
        # Ensure the directory exists
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                knowledge_gaps TEXT,
                preferred_format TEXT,
                content_generated TEXT
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("Database setup completed successfully")

    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise


def save_interaction(
    database_path: str, user_id: str, assessment: Dict[str, Any], content: str
) -> None:
    """
    Save user interaction and assessment results to SQLite database.

    Persists user data including questions, preferences, and generated content
    for tracking learning progress and system analytics.

    Args:
        database_path (str): Path to the SQLite database file
        user_id (str): Unique identifier for the user
        assessment (Dict): User assessment/question data
        content (str): Generated personalized content

    Returns:
        None
    """
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Handle both old assessment format and new question format
        if "question" in assessment:
            knowledge_gaps = json.dumps([assessment.get("question", "")])
        else:
            knowledge_gaps = json.dumps(assessment.get("knowledge_gaps", []))

        preferred_format = assessment.get("preferred_format", "mixed")

        cursor.execute(
            """
            INSERT INTO user_interactions (user_id, knowledge_gaps, preferred_format, content_generated)
            VALUES (?, ?, ?, ?)
        """,
            (user_id, knowledge_gaps, preferred_format, content),
        )

        conn.commit()
        conn.close()
        logger.info(f"Saved interaction for user: {user_id}")

    except Exception as e:
        logger.error(f"Error saving interaction: {e}")


def get_user_interactions(database_path: str, user_id: str = None) -> list:
    """
    Retrieve user interactions from the database.

    Args:
        database_path (str): Path to the SQLite database file
        user_id (str, optional): Specific user ID to filter by

    Returns:
        list: List of interaction records
    """
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        if user_id:
            cursor.execute(
                """
                SELECT * FROM user_interactions 
                WHERE user_id = ? 
                ORDER BY timestamp DESC
            """,
                (user_id,),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM user_interactions 
                ORDER BY timestamp DESC
            """
            )

        interactions = cursor.fetchall()
        conn.close()

        logger.info(f"Retrieved {len(interactions)} interactions")
        return interactions

    except Exception as e:
        logger.error(f"Error retrieving interactions: {e}")
        return []


def get_interaction_stats(database_path: str) -> Dict[str, Any]:
    """
    Get statistics about user interactions.

    Args:
        database_path (str): Path to the SQLite database file

    Returns:
        Dict[str, Any]: Statistics about interactions
    """
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Total interactions
        cursor.execute("SELECT COUNT(*) FROM user_interactions")
        total_interactions = cursor.fetchone()[0]

        # Unique users
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM user_interactions")
        unique_users = cursor.fetchone()[0]

        # Most common preferred format
        cursor.execute(
            """
            SELECT preferred_format, COUNT(*) as count 
            FROM user_interactions 
            GROUP BY preferred_format 
            ORDER BY count DESC 
            LIMIT 1
        """
        )
        format_result = cursor.fetchone()
        most_common_format = format_result[0] if format_result else None

        conn.close()

        stats = {
            "total_interactions": total_interactions,
            "unique_users": unique_users,
            "most_common_format": most_common_format,
        }

        logger.info(f"Database stats: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Error getting interaction stats: {e}")
        return {"total_interactions": 0, "unique_users": 0, "most_common_format": None}

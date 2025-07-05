"""
Tests for core database module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import tempfile
import sqlite3
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.database import (
    setup_database,
    save_interaction,
    get_user_interactions,
    get_interaction_stats
)


class TestSetupDatabase:
    """Test database setup functionality."""
    
    def test_setup_database_basic(self):
        """Test basic database setup."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            
            setup_database(str(db_path))
            
            assert db_path.exists()
            
            # Verify table was created
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            assert len(tables) > 0
            assert "user_interactions" in [table[0] for table in tables]
    
    def test_setup_database_creates_directory(self):
        """Test that database setup creates directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "subdir" / "test.db"
            
            setup_database(str(db_path))
            
            assert db_path.parent.exists()
            assert db_path.exists()
    
    def test_setup_database_existing_file(self):
        """Test database setup with existing file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            
            # Create database twice - should not error
            setup_database(str(db_path))
            setup_database(str(db_path))
            
            assert db_path.exists()


class TestSaveInteraction:
    """Test interaction saving functionality."""
    
    def test_save_interaction_basic(self):
        """Test basic interaction saving."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            setup_database(str(db_path))
            
            assessment = {
                "question": "What is AI?",
                "preferred_format": "text"
            }
            
            save_interaction(str(db_path), "user123", assessment, "AI response")
            
            # Verify data was saved
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_interactions")
            rows = cursor.fetchall()
            conn.close()
            
            assert len(rows) == 1
            assert rows[0][2] == "user123"  # user_id
            assert rows[0][4] == "text"  # preferred_format
    
    def test_save_interaction_with_knowledge_gaps(self):
        """Test saving interaction with knowledge gaps."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            setup_database(str(db_path))
            
            assessment = {
                "knowledge_gaps": ["ML basics", "Neural networks"],
                "preferred_format": "video"
            }
            
            save_interaction(str(db_path), "user456", assessment, "ML response")
            
            # Verify data was saved
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT knowledge_gaps, preferred_format FROM user_interactions")
            row = cursor.fetchone()
            conn.close()
            
            knowledge_gaps = json.loads(row[0])
            assert "ML basics" in knowledge_gaps
            assert "Neural networks" in knowledge_gaps
            assert row[1] == "video"
    
    def test_save_interaction_missing_format(self):
        """Test saving interaction with missing format."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            setup_database(str(db_path))
            
            assessment = {"question": "Test question"}
            
            save_interaction(str(db_path), "user789", assessment, "Test response")
            
            # Should use default format
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT preferred_format FROM user_interactions")
            row = cursor.fetchone()
            conn.close()
            
            assert row[0] == "mixed"
    
    def test_save_interaction_error_handling(self):
        """Test interaction saving with database errors."""
        # Test with non-existent database path
        save_interaction("/invalid/path/test.db", "user", {}, "content")
        
        # Should not raise exception
        assert True


class TestGetUserInteractions:
    """Test user interaction retrieval."""
    
    def test_get_user_interactions_basic(self):
        """Test basic user interaction retrieval."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            setup_database(str(db_path))
            
            # Add test data
            assessment = {"question": "Test", "preferred_format": "text"}
            save_interaction(str(db_path), "user123", assessment, "Response")
            
            interactions = get_user_interactions(str(db_path))
            
            assert len(interactions) == 1
            assert interactions[0][2] == "user123"  # user_id
    
    def test_get_user_interactions_specific_user(self):
        """Test getting interactions for specific user."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            setup_database(str(db_path))
            
            # Add test data for multiple users
            assessment1 = {"question": "Test1", "preferred_format": "text"}
            assessment2 = {"question": "Test2", "preferred_format": "video"}
            save_interaction(str(db_path), "user123", assessment1, "Response1")
            save_interaction(str(db_path), "user456", assessment2, "Response2")
            
            interactions = get_user_interactions(str(db_path), "user123")
            
            assert len(interactions) == 1
            assert interactions[0][2] == "user123"
    
    def test_get_user_interactions_empty_database(self):
        """Test getting interactions from empty database."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            setup_database(str(db_path))
            
            interactions = get_user_interactions(str(db_path))
            
            assert len(interactions) == 0
    
    def test_get_user_interactions_error_handling(self):
        """Test interaction retrieval with database errors."""
        interactions = get_user_interactions("/invalid/path/test.db")
        
        assert interactions == []


class TestGetInteractionStats:
    """Test interaction statistics retrieval."""
    
    def test_get_interaction_stats_basic(self):
        """Test basic interaction statistics."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            setup_database(str(db_path))
            
            # Add test data
            assessment1 = {"question": "Test1", "preferred_format": "text"}
            assessment2 = {"question": "Test2", "preferred_format": "video"}
            save_interaction(str(db_path), "user123", assessment1, "Response1")
            save_interaction(str(db_path), "user456", assessment2, "Response2")
            
            stats = get_interaction_stats(str(db_path))
            
            assert stats["total_interactions"] == 2
            assert stats["unique_users"] == 2
            assert stats["most_common_format"] in ["text", "video"]
    
    def test_get_interaction_stats_empty_database(self):
        """Test statistics from empty database."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            setup_database(str(db_path))
            
            stats = get_interaction_stats(str(db_path))
            
            assert stats["total_interactions"] == 0
            assert stats["unique_users"] == 0
            assert stats["most_common_format"] is None
    
    def test_get_interaction_stats_same_user_multiple_interactions(self):
        """Test statistics with same user having multiple interactions."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            setup_database(str(db_path))
            
            # Same user, multiple interactions
            assessment1 = {"question": "Test1", "preferred_format": "text"}
            assessment2 = {"question": "Test2", "preferred_format": "text"}
            save_interaction(str(db_path), "user123", assessment1, "Response1")
            save_interaction(str(db_path), "user123", assessment2, "Response2")
            
            stats = get_interaction_stats(str(db_path))
            
            assert stats["total_interactions"] == 2
            assert stats["unique_users"] == 1
            assert stats["most_common_format"] == "text"
    
    def test_get_interaction_stats_error_handling(self):
        """Test statistics with database errors."""
        stats = get_interaction_stats("/invalid/path/test.db")
        
        assert stats["total_interactions"] == 0
        assert stats["unique_users"] == 0
        assert stats["most_common_format"] is None


class TestDatabaseIntegration:
    """Integration tests for database functionality."""
    
    def test_full_database_workflow(self):
        """Test complete database workflow."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "integration.db"
            
            # Setup database
            setup_database(str(db_path))
            
            # Add multiple interactions
            users = ["user1", "user2", "user3"]
            formats = ["text", "video", "text"]
            
            for i, (user, format_type) in enumerate(zip(users, formats)):
                assessment = {
                    "question": f"Question {i+1}",
                    "preferred_format": format_type
                }
                save_interaction(str(db_path), user, assessment, f"Response {i+1}")
            
            # Get all interactions
            all_interactions = get_user_interactions(str(db_path))
            assert len(all_interactions) == 3
            
            # Get specific user interactions
            user1_interactions = get_user_interactions(str(db_path), "user1")
            assert len(user1_interactions) == 1
            assert user1_interactions[0][2] == "user1"
            
            # Get statistics
            stats = get_interaction_stats(str(db_path))
            assert stats["total_interactions"] == 3
            assert stats["unique_users"] == 3
            assert stats["most_common_format"] == "text"  # text appears 2 times
    
    def test_database_persistence(self):
        """Test that database persists data across connections."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "persist.db"
            
            # First connection - create and add data
            setup_database(str(db_path))
            assessment = {"question": "Test", "preferred_format": "text"}
            save_interaction(str(db_path), "user1", assessment, "Response")
            
            # Second connection - retrieve data
            interactions = get_user_interactions(str(db_path))
            assert len(interactions) == 1
            assert interactions[0][2] == "user1"
            
            # Third connection - add more data
            assessment2 = {"question": "Test2", "preferred_format": "video"}
            save_interaction(str(db_path), "user2", assessment2, "Response2")
            
            # Fourth connection - verify all data
            all_interactions = get_user_interactions(str(db_path))
            assert len(all_interactions) == 2
            
            stats = get_interaction_stats(str(db_path))
            assert stats["total_interactions"] == 2
            assert stats["unique_users"] == 2 
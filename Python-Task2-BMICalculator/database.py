"""
BMI Calculator - Database Module
Handles SQLite database operations for storing user BMI history.
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional
import os


class BMIDatabase:
    """Handles all database operations for BMI records."""

    def __init__(self, db_path: str = "bmi_history.db"):
        """
        Initialize database connection and create tables if needed.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()

    def init_database(self) -> None:
        """Create the BMI records table if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create index on username for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_username
                ON bmi_records(username)
            """)

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            raise Exception(f"Database initialization failed: {e}")

    def save_record(self, username: str, weight: float, height: float,
                   bmi: float, category: str) -> bool:
        """
        Save a BMI record to the database.

        Args:
            username: User's name
            weight: Weight in kg
            height: Height in metres
            bmi: Calculated BMI
            category: BMI category

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO bmi_records (username, weight, height, bmi, category)
                VALUES (?, ?, ?, ?, ?)
            """, (username, weight, height, bmi, category))

            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error saving record: {e}")
            return False

    def get_user_history(self, username: str) -> List[Tuple]:
        """
        Get all BMI records for a specific user, ordered by date.

        Args:
            username: User's name

        Returns:
            List of tuples: (id, username, weight, height, bmi, category, recorded_at)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, username, weight, height, bmi, category, recorded_at
                FROM bmi_records
                WHERE username = ?
                ORDER BY recorded_at DESC
            """, (username,))

            records = cursor.fetchall()
            conn.close()
            return records
        except sqlite3.Error as e:
            print(f"Error fetching history: {e}")
            return []

    def get_all_users(self) -> List[str]:
        """
        Get list of all unique usernames in the database.

        Returns:
            List of usernames, sorted alphabetically
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT username
                FROM bmi_records
                ORDER BY username ASC
            """)

            users = [row[0] for row in cursor.fetchall()]
            conn.close()
            return users
        except sqlite3.Error as e:
            print(f"Error fetching users: {e}")
            return []

    def delete_record(self, record_id: int) -> bool:
        """
        Delete a specific BMI record by ID.

        Args:
            record_id: Database record ID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM bmi_records WHERE id = ?", (record_id,))

            conn.commit()
            deleted = cursor.rowcount > 0
            conn.close()
            return deleted
        except sqlite3.Error as e:
            print(f"Error deleting record: {e}")
            return False

    def get_record_count(self, username: str) -> int:
        """
        Get the number of records for a specific user.

        Args:
            username: User's name

        Returns:
            Number of records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM bmi_records WHERE username = ?
            """, (username,))

            count = cursor.fetchone()[0]
            conn.close()
            return count
        except sqlite3.Error as e:
            print(f"Error counting records: {e}")
            return 0

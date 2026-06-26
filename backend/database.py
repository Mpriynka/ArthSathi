import json
import sqlite3
import logging
from typing import Dict, Any, Optional
from backend.config import settings

logger = logging.getLogger("chillar_seedhi.database")

class BaseRepository:
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def save_user(self, user_id: str, user_data: Dict[str, Any]) -> None:
        raise NotImplementedError

class SQLiteRepository(BaseRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        # Enforce isolated connection for thread safety in FastAPI
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                data TEXT
            )
            """
        )
        conn.commit()
        conn.close()
        logger.info(f"Initialized SQLite database at {self.db_path}")

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            try:
                return json.loads(row["data"])
            except Exception as e:
                logger.error(f"Error decoding user JSON for {user_id}: {e}")
                return None
        return None

    def save_user(self, user_id: str, user_data: Dict[str, Any]) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        # Ensure userId field is set in document
        user_data["userId"] = user_id
        data_str = json.dumps(user_data)
        cursor.execute(
            "INSERT OR REPLACE INTO users (user_id, data) VALUES (?, ?)",
            (user_id, data_str)
        )
        conn.commit()
        conn.close()
        logger.info(f"Saved user {user_id} to SQLite")

class MongoDBRepository(BaseRepository):
    def __init__(self, mongo_uri: str):
        from pymongo import MongoClient
        self.client = MongoClient(mongo_uri)
        self.db = self.client["chillar_seedhi"]
        self.collection = self.db["users"]
        logger.info("Initialized MongoDB database connection")

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = self.collection.find_one({"userId": user_id})
        if doc:
            # Remove MongoDB internal _id field which is not JSON serializable
            doc.pop("_id", None)
            return doc
        return None

    def save_user(self, user_id: str, user_data: Dict[str, Any]) -> None:
        user_data["userId"] = user_id
        self.collection.replace_one({"userId": user_id}, user_data, upsert=True)
        logger.info(f"Saved user {user_id} to MongoDB")

# Global repository instance
_repo_instance: Optional[BaseRepository] = None

def get_db_repository() -> BaseRepository:
    global _repo_instance
    if _repo_instance is None:
        if settings.MONGO_URI:
            try:
                _repo_instance = MongoDBRepository(settings.MONGO_URI)
                logger.info("Using MongoDB Repository")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB, falling back to SQLite: {e}")
                _repo_instance = SQLiteRepository(settings.SQLITE_PATH)
        else:
            logger.info("No MONGO_URI configured. Using SQLite Repository")
            _repo_instance = SQLiteRepository(settings.SQLITE_PATH)
    return _repo_instance

def get_default_user_profile(user_id: str) -> Dict[str, Any]:
    """Returns a fresh, default user profile structure matching the schemas."""
    return {
        "userId": user_id,
        "persona": {
            "name": "Guest User",
            "language": "English",
            "incomePattern": "daily_wage",
            "expenseFrequency": "daily",
            "riskTolerance": "low"
        },
        "seedhiLevel": 0,
        "levelHistory": [
            {"level": 0, "achievedOn": "2026-06-26"}
        ],
        "incomeLogs": [],
        "dailyTrackerLogs": [],
        "goals": [],
        "streaks": {
            "streakCount": 0,
            "lastSavedDate": "",
            "calendar": []
        },
        "chatHistory": [],
        "lastActive": "2026-06-26T00:00:00Z"
    }

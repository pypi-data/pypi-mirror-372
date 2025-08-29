"""
Database persistence layer for Syntha ContextMesh.

Copyright 2025 Syntha

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Provides pluggable database backends with SQLite as default.
Supports easy switching to PostgreSQL, MySQL, or other databases.
"""

import json
import sqlite3
import time
from abc import ABC, abstractmethod
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple


class DatabaseBackend(ABC):
    """Abstract base class for database backends."""

    @abstractmethod
    def connect(self) -> None:
        """Establish database connection."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    def initialize_schema(self) -> None:
        """Create necessary tables and indexes."""
        pass

    @abstractmethod
    def save_context_item(
        self,
        key: str,
        value: Any,
        subscribers: List[str],
        ttl: Optional[float],
        created_at: float,
    ) -> None:
        """Save a context item to the database."""
        pass

    @abstractmethod
    def get_context_item(
        self, key: str
    ) -> Optional[Tuple[Any, List[str], Optional[float], float]]:
        """Retrieve a context item from the database.

        Returns:
            Tuple of (value, subscribers, ttl, created_at) or None if not found
        """
        pass

    @abstractmethod
    def delete_context_item(self, key: str) -> bool:
        """Delete a context item from the database.

        Returns:
            True if item was deleted, False if it didn't exist
        """
        pass

    @abstractmethod
    def get_all_context_items(
        self,
    ) -> Dict[str, Tuple[Any, List[str], Optional[float], float]]:
        """Get all context items from the database.

        Returns:
            Dict mapping keys to (value, subscribers, ttl, created_at) tuples
        """
        pass

    @abstractmethod
    def cleanup_expired(self, current_time: float) -> int:
        """Remove expired items from the database.

        Returns:
            Number of items removed
        """
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """Remove all context items from the database."""
        pass

    @abstractmethod
    def save_agent_topics(self, agent_name: str, topics: List[str]) -> None:
        """Save agent topic subscriptions."""
        pass

    @abstractmethod
    def get_agent_topics(self, agent_name: str) -> List[str]:
        """Get agent topic subscriptions."""
        pass

    @abstractmethod
    def get_all_agent_topics(self) -> Dict[str, List[str]]:
        """Get all agent topic mappings."""
        pass

    @abstractmethod
    def remove_agent_topics(self, agent_name: str) -> None:
        """Remove agent topic subscriptions."""
        pass

    @abstractmethod
    def save_agent_permissions(
        self, agent_name: str, allowed_topics: List[str]
    ) -> None:
        """Save agent posting permissions."""
        pass

    @abstractmethod
    def get_agent_permissions(self, agent_name: str) -> List[str]:
        """Get agent posting permissions."""
        pass

    @abstractmethod
    def get_all_agent_permissions(self) -> Dict[str, List[str]]:
        """Get all agent permission mappings."""
        pass

    # User isolation methods (optional - backward compatibility)
    def save_context_item_for_user(
        self,
        user_id: str,
        key: str,
        value: Any,
        subscribers: List[str],
        ttl: Optional[float],
        created_at: float,
    ) -> None:
        """Save a context item for a specific user."""
        # Default implementation for backward compatibility
        self.save_context_item(key, value, subscribers, ttl, created_at)

    def get_context_item_for_user(
        self, user_id: str, key: str
    ) -> Optional[Tuple[Any, List[str], Optional[float], float]]:
        """Get a context item for a specific user."""
        # Default implementation for backward compatibility
        return self.get_context_item(key)

    def get_all_context_items_for_user(
        self, user_id: str
    ) -> Dict[str, Tuple[Any, List[str], Optional[float], float]]:
        """Get all context items for a specific user."""
        # Default implementation for backward compatibility
        return self.get_all_context_items()

    def delete_context_item_for_user(self, user_id: str, key: str) -> bool:
        """Delete a context item for a specific user."""
        # Default implementation for backward compatibility
        return self.delete_context_item(key)

    def save_agent_topics_for_user(
        self, user_id: str, agent_name: str, topics: List[str]
    ) -> None:
        """Save agent topics for a specific user."""
        # Default implementation for backward compatibility
        self.save_agent_topics(agent_name, topics)

    def get_agent_topics_for_user(self, user_id: str, agent_name: str) -> List[str]:
        """Get agent topics for a specific user."""
        # Default implementation for backward compatibility
        return self.get_agent_topics(agent_name)

    def get_all_agent_topics_for_user(self, user_id: str) -> Dict[str, List[str]]:
        """Get all agent topics for a specific user."""
        # Default implementation for backward compatibility
        return self.get_all_agent_topics()

    def remove_agent_topics_for_user(self, user_id: str, agent_name: str) -> None:
        """Remove agent topics for a specific user."""
        # Default implementation for backward compatibility
        self.remove_agent_topics(agent_name)

    def save_agent_permissions_for_user(
        self, user_id: str, agent_name: str, allowed_topics: List[str]
    ) -> None:
        """Save agent permissions for a specific user."""
        # Default implementation for backward compatibility
        self.save_agent_permissions(agent_name, allowed_topics)

    def get_agent_permissions_for_user(
        self, user_id: str, agent_name: str
    ) -> List[str]:
        """Get agent permissions for a specific user."""
        # Default implementation for backward compatibility
        return self.get_agent_permissions(agent_name)

    def get_all_agent_permissions_for_user(self, user_id: str) -> Dict[str, List[str]]:
        """Get all agent permissions for a specific user."""
        # Default implementation for backward compatibility
        return self.get_all_agent_permissions()

    def cleanup_expired_for_user(self, user_id: str, current_time: float) -> int:
        """Clean up expired items for a specific user."""
        # Default implementation for backward compatibility
        return self.cleanup_expired(current_time)

    def clear_all_for_user(self, user_id: str) -> None:
        """Clear all data for a specific user."""
        # Default implementation for backward compatibility
        self.clear_all()

    def delete_topic_data_for_user(self, user_id: str, topic: str) -> None:
        """Delete topic-specific data for a specific user."""
        # Default implementation - no-op since base class doesn't have this method
        pass


class SQLiteBackend(DatabaseBackend):
    """SQLite database backend implementation."""

    def __init__(self, db_path: str = "syntha_context.db"):
        self.db_path = db_path
        self.connection = None
        self._lock = Lock()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def connect(self) -> None:
        """Establish SQLite connection."""
        import os

        try:
            self.connection = sqlite3.connect(  # type: ignore
                self.db_path, check_same_thread=False, timeout=30.0  # Increased timeout
            )
            # Use DELETE mode instead of WAL to avoid Windows file locking issues
            if self.connection:
                self.connection.execute("PRAGMA journal_mode=DELETE")
                self.connection.execute(
                    "PRAGMA synchronous=NORMAL"
                )  # Better performance
                self.connection.execute("PRAGMA foreign_keys=ON")  # Enable foreign keys
                self.connection.execute(
                    "PRAGMA busy_timeout=30000"
                )  # 30 second timeout
                # Additional settings for better concurrency
                self.connection.execute("PRAGMA cache_size=10000")  # Larger cache
                self.connection.execute(
                    "PRAGMA temp_store=MEMORY"
                )  # Use memory for temp storage
            self.initialize_schema()

            # Set secure file permissions on POSIX systems
            if os.name == "posix" and os.path.exists(self.db_path):
                # Set permissions to 0o600 (read/write for owner only)
                os.chmod(self.db_path, 0o600)
        except sqlite3.DatabaseError as e:
            # Handle database corruption by backing up the corrupted file and starting fresh
            if (
                "file is not a database" in str(e).lower()
                or "database disk image is malformed" in str(e).lower()
            ):
                # Close any existing connection
                if self.connection:
                    try:
                        self.connection.close()
                    except (sqlite3.Error, OSError, AttributeError):
                        # Ignore errors during connection cleanup
                        pass
                    self.connection = None

                # Backup the corrupted file
                if os.path.exists(self.db_path):
                    backup_path = f"{self.db_path}.corrupted.{int(time.time())}"
                    try:
                        os.rename(self.db_path, backup_path)
                        print(
                            f"Warning: Database file was corrupted and backed up to {backup_path}"
                        )
                    except (OSError, FileNotFoundError, PermissionError):
                        # If backup fails, just remove the corrupted file
                        try:
                            os.remove(self.db_path)
                            print(
                                f"Warning: Database file was corrupted and removed. Starting fresh."
                            )
                        except (OSError, FileNotFoundError, PermissionError):
                            # If we can't remove the file, continue anyway
                            pass

                # Try to create a new database
                try:
                    self.connection = sqlite3.connect(  # type: ignore
                        self.db_path,
                        check_same_thread=False,
                        timeout=30.0,  # Increased timeout
                    )
                    if self.connection:
                        self.connection.execute("PRAGMA journal_mode=DELETE")
                        self.connection.execute("PRAGMA synchronous=NORMAL")
                        self.connection.execute("PRAGMA foreign_keys=ON")
                        self.connection.execute(
                            "PRAGMA busy_timeout=30000"
                        )  # 30 second timeout
                        # Additional settings for better concurrency
                        self.connection.execute(
                            "PRAGMA cache_size=10000"
                        )  # Larger cache
                        self.connection.execute(
                            "PRAGMA temp_store=MEMORY"
                        )  # Use memory for temp storage
                    self.initialize_schema()

                    # Set secure file permissions on POSIX systems
                    if os.name == "posix" and os.path.exists(self.db_path):
                        # Set permissions to 0o600 (read/write for owner only)
                        os.chmod(self.db_path, 0o600)
                except Exception as retry_error:
                    raise Exception(
                        f"Failed to create new database after corruption: {retry_error}"
                    )
            else:
                # Re-raise other database errors
                raise e

    def close(self) -> None:
        """Close SQLite connection."""
        if self.connection:
            try:
                # Close any open cursors and commit pending transactions
                self.connection.execute(
                    "PRAGMA optimize"
                )  # Optimize database before closing
                self.connection.commit()
                self.connection.close()
            except sqlite3.Error:
                # Ignore errors during close
                pass
            finally:
                self.connection = None

    def initialize_schema(self) -> None:
        """Create SQLite tables and indexes."""
        with self._lock:
            if not self.connection:
                return

            cursor = self.connection.cursor()

            # Context items table (with user isolation)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS context_items (
                    key TEXT NOT NULL,
                    user_id TEXT,
                    value TEXT NOT NULL,
                    subscribers TEXT NOT NULL,
                    ttl REAL,
                    created_at REAL NOT NULL,
                    PRIMARY KEY (key, user_id)
                )
            """
            )

            # Agent topics table (with user isolation)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_topics (
                    agent_name TEXT NOT NULL,
                    user_id TEXT,
                    topics TEXT NOT NULL,
                    PRIMARY KEY (agent_name, user_id)
                )
            """
            )

            # Agent permissions table (with user isolation)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_permissions (
                    agent_name TEXT NOT NULL,
                    user_id TEXT,
                    allowed_topics TEXT NOT NULL,
                    PRIMARY KEY (agent_name, user_id)
                )
            """
            )

            # Add migration for existing data (set user_id to NULL for legacy data)
            try:
                cursor.execute("ALTER TABLE context_items ADD COLUMN user_id TEXT")
            except sqlite3.OperationalError:
                # Column already exists
                pass

            try:
                cursor.execute("ALTER TABLE agent_topics ADD COLUMN user_id TEXT")
            except sqlite3.OperationalError:
                # Column already exists
                pass

            try:
                cursor.execute("ALTER TABLE agent_permissions ADD COLUMN user_id TEXT")
            except sqlite3.OperationalError:
                # Column already exists
                pass

            # Create indexes for better performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_context_created_at ON context_items(created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_context_ttl ON context_items(ttl)"
            )

            self.connection.commit()

    def save_context_item(
        self,
        key: str,
        value: Any,
        subscribers: List[str],
        ttl: Optional[float],
        created_at: float,
    ) -> None:
        """Save a context item to SQLite."""
        import time

        max_retries = 3
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                with self._lock:
                    self._ensure_connection()
                    cursor = self.connection.cursor()
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO context_items 
                        (key, value, subscribers, ttl, created_at) 
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            key,
                            json.dumps(value),
                            json.dumps(subscribers),
                            ttl,
                            created_at,
                        ),
                    )
                    self.connection.commit()
                    return  # Success
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(retry_delay * (2**attempt))  # Exponential backoff
                    continue
                else:
                    raise
            except Exception:
                raise

    def get_context_item(
        self, key: str
    ) -> Optional[Tuple[Any, List[str], Optional[float], float]]:
        """Retrieve a context item from SQLite."""
        import time

        max_retries = 3
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                with self._lock:
                    self._ensure_connection()
                    cursor = self.connection.cursor()
                    cursor.execute(
                        "SELECT value, subscribers, ttl, created_at FROM context_items WHERE key = ?",
                        (key,),
                    )
                    row = cursor.fetchone()

                    if row is None:
                        return None

                    value_json, subscribers_json, ttl, created_at = row
                    value = json.loads(value_json)
                    subscribers = json.loads(subscribers_json)

                    return (value, subscribers, ttl, created_at)
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(retry_delay * (2**attempt))  # Exponential backoff
                    continue
                else:
                    raise
            except Exception:
                raise

        # If all retries failed, return None (not found)
        return None

    def delete_context_item(self, key: str) -> bool:
        """Delete a context item from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM context_items WHERE key = ?", (key,))
            self.connection.commit()
            return cursor.rowcount > 0

    def get_all_context_items(
        self,
    ) -> Dict[str, Tuple[Any, List[str], Optional[float], float]]:
        """Get all context items from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT key, value, subscribers, ttl, created_at FROM context_items"
            )

            result = {}
            for row in cursor.fetchall():
                key, value_json, subscribers_json, ttl, created_at = row
                value = json.loads(value_json)
                subscribers = json.loads(subscribers_json)
                result[key] = (value, subscribers, ttl, created_at)

            return result

    def cleanup_expired(self, current_time: float) -> int:
        """Remove expired items from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                DELETE FROM context_items 
                WHERE ttl IS NOT NULL AND (created_at + ttl) < ?
            """,
                (current_time,),
            )
            self.connection.commit()
            return cursor.rowcount

    def clear_all(self) -> None:
        """Remove all context items from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM context_items")
            cursor.execute("DELETE FROM agent_topics")
            cursor.execute("DELETE FROM agent_permissions")
            self.connection.commit()

    def save_agent_topics(self, agent_name: str, topics: List[str]) -> None:
        """Save agent topic subscriptions to SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO agent_topics (agent_name, topics) 
                VALUES (?, ?)
            """,
                (agent_name, json.dumps(topics)),
            )
            self.connection.commit()

    def get_agent_topics(self, agent_name: str) -> List[str]:
        """Get agent topic subscriptions from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT topics FROM agent_topics WHERE agent_name = ?", (agent_name,)
            )
            row = cursor.fetchone()

            if row is None:
                return []

            return json.loads(row[0])

    def get_all_agent_topics(self) -> Dict[str, List[str]]:
        """Get all agent topic mappings from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("SELECT agent_name, topics FROM agent_topics")

            result = {}
            for agent_name, topics_json in cursor.fetchall():
                result[agent_name] = json.loads(topics_json)

            return result

    def remove_agent_topics(self, agent_name: str) -> None:
        """Remove agent topic subscriptions from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM agent_topics WHERE agent_name = ?", (agent_name,)
            )
            self.connection.commit()

    def save_agent_permissions(
        self, agent_name: str, allowed_topics: List[str]
    ) -> None:
        """Save agent posting permissions to SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO agent_permissions (agent_name, allowed_topics) 
                VALUES (?, ?)
            """,
                (agent_name, json.dumps(allowed_topics)),
            )
            self.connection.commit()

    def get_agent_permissions(self, agent_name: str) -> List[str]:
        """Get agent posting permissions from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT allowed_topics FROM agent_permissions WHERE agent_name = ?",
                (agent_name,),
            )
            row = cursor.fetchone()

            if row is None:
                return []

            return json.loads(row[0])

    def get_all_agent_permissions(self) -> Dict[str, List[str]]:
        """Get all agent permission mappings from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("SELECT agent_name, allowed_topics FROM agent_permissions")

            result = {}
            for agent_name, allowed_topics_json in cursor.fetchall():
                result[agent_name] = json.loads(allowed_topics_json)

            return result

    def _ensure_connection(self) -> None:
        """Ensure database connection is alive, reconnect if needed."""
        if self.connection is None:
            self.connect()

        if self.connection is None:
            raise RuntimeError("Failed to establish database connection")

        try:
            # Test the connection
            self.connection.execute("SELECT 1")
        except sqlite3.Error:
            # Connection is broken, reconnect
            self.close()
            self.connect()
            if self.connection is None:
                raise RuntimeError("Failed to re-establish database connection")

    def _ensure_connection_for_operation(self) -> None:
        """Ensure connection exists for database operations."""
        if not self.connection:
            raise RuntimeError("Database connection not established")

    # User isolation implementations for SQLite
    def save_context_item_for_user(
        self,
        user_id: str,
        key: str,
        value: Any,
        subscribers: List[str],
        ttl: Optional[float],
        created_at: float,
    ) -> None:
        """Save a context item for a specific user in SQLite."""
        with self._lock:
            self._ensure_connection_for_operation()
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO context_items 
                (key, user_id, value, subscribers, ttl, created_at) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    key,
                    user_id,
                    json.dumps(value),
                    json.dumps(subscribers),
                    ttl,
                    created_at,
                ),
            )
            self.connection.commit()

    def get_context_item_for_user(
        self, user_id: str, key: str
    ) -> Optional[Tuple[Any, List[str], Optional[float], float]]:
        """Get a context item for a specific user from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT value, subscribers, ttl, created_at FROM context_items WHERE key = ? AND user_id = ?",
                (key, user_id),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            value_json, subscribers_json, ttl, created_at = row
            value = json.loads(value_json)
            subscribers = json.loads(subscribers_json)

            return (value, subscribers, ttl, created_at)

    def get_all_context_items_for_user(
        self, user_id: str
    ) -> Dict[str, Tuple[Any, List[str], Optional[float], float]]:
        """Get all context items for a specific user from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT key, value, subscribers, ttl, created_at FROM context_items WHERE user_id = ?",
                (user_id,),
            )

            result = {}
            for row in cursor.fetchall():
                key, value_json, subscribers_json, ttl, created_at = row
                value = json.loads(value_json)
                subscribers = json.loads(subscribers_json)
                result[key] = (value, subscribers, ttl, created_at)

            return result

    def delete_context_item_for_user(self, user_id: str, key: str) -> bool:
        """Delete a context item for a specific user from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM context_items WHERE key = ? AND user_id = ?",
                (key, user_id),
            )
            self.connection.commit()
            return cursor.rowcount > 0

    def save_agent_topics_for_user(
        self, user_id: str, agent_name: str, topics: List[str]
    ) -> None:
        """Save agent topics for a specific user in SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO agent_topics (agent_name, user_id, topics) 
                VALUES (?, ?, ?)
                """,
                (agent_name, user_id, json.dumps(topics)),
            )
            self.connection.commit()

    def get_agent_topics_for_user(self, user_id: str, agent_name: str) -> List[str]:
        """Get agent topics for a specific user from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT topics FROM agent_topics WHERE agent_name = ? AND user_id = ?",
                (agent_name, user_id),
            )
            row = cursor.fetchone()

            if row is None:
                return []

            return json.loads(row[0])

    def get_all_agent_topics_for_user(self, user_id: str) -> Dict[str, List[str]]:
        """Get all agent topics for a specific user from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT agent_name, topics FROM agent_topics WHERE user_id = ?",
                (user_id,),
            )

            result = {}
            for agent_name, topics_json in cursor.fetchall():
                result[agent_name] = json.loads(topics_json)

            return result

    def remove_agent_topics_for_user(self, user_id: str, agent_name: str) -> None:
        """Remove agent topics for a specific user from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM agent_topics WHERE agent_name = ? AND user_id = ?",
                (agent_name, user_id),
            )
            self.connection.commit()

    def save_agent_permissions_for_user(
        self, user_id: str, agent_name: str, allowed_topics: List[str]
    ) -> None:
        """Save agent permissions for a specific user in SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO agent_permissions (agent_name, user_id, allowed_topics) 
                VALUES (?, ?, ?)
                """,
                (agent_name, user_id, json.dumps(allowed_topics)),
            )
            self.connection.commit()

    def get_agent_permissions_for_user(
        self, user_id: str, agent_name: str
    ) -> List[str]:
        """Get agent permissions for a specific user from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT allowed_topics FROM agent_permissions WHERE agent_name = ? AND user_id = ?",
                (agent_name, user_id),
            )
            row = cursor.fetchone()

            if row is None:
                return []

            return json.loads(row[0])

    def get_all_agent_permissions_for_user(self, user_id: str) -> Dict[str, List[str]]:
        """Get all agent permissions for a specific user from SQLite."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT agent_name, allowed_topics FROM agent_permissions WHERE user_id = ?",
                (user_id,),
            )

            result = {}
            for agent_name, allowed_topics_json in cursor.fetchall():
                result[agent_name] = json.loads(allowed_topics_json)

            return result

    def cleanup_expired_for_user(self, user_id: str, current_time: float) -> int:
        """Clean up expired items for a specific user."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                DELETE FROM context_items 
                WHERE user_id = ? AND ttl IS NOT NULL AND (created_at + ttl) < ?
                """,
                (user_id, current_time),
            )
            deleted = cursor.rowcount
            self.connection.commit()
            return deleted

    def clear_all_for_user(self, user_id: str) -> None:
        """Clear all data for a specific user."""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM context_items WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM agent_topics WHERE user_id = ?", (user_id,))
            cursor.execute(
                "DELETE FROM agent_permissions WHERE user_id = ?", (user_id,)
            )
            self.connection.commit()


class PostgreSQLBackend(DatabaseBackend):
    """PostgreSQL database backend implementation."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection: Optional[Any] = None
        self._lock = Lock()

    def connect(self) -> None:
        """Establish PostgreSQL connection."""
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            raise ImportError(
                "psycopg2 is required for PostgreSQL backend. Install with: pip install psycopg2-binary"
            )

        self.connection = psycopg2.connect(self.connection_string)
        self.initialize_schema()

    def close(self) -> None:
        """Close PostgreSQL connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def initialize_schema(self) -> None:
        """Create PostgreSQL tables and indexes."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore

            # Context items table (with user isolation)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS context_items (
                    key TEXT NOT NULL,
                    user_id TEXT,
                    value JSONB NOT NULL,
                    subscribers JSONB NOT NULL,
                    ttl REAL,
                    created_at REAL NOT NULL
                )
            """
            )

            # Create unique constraint to handle NULL user_id properly
            cursor.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_context_key_user 
                ON context_items (key, COALESCE(user_id, ''))
                """
            )

            # Agent topics table (with user isolation)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_topics (
                    agent_name TEXT NOT NULL,
                    user_id TEXT,
                    topics JSONB NOT NULL
                )
            """
            )

            # Create unique constraint to handle NULL user_id properly
            cursor.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_agent_topics_name_user 
                ON agent_topics (agent_name, COALESCE(user_id, ''))
                """
            )

            # Agent permissions table (with user isolation)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_permissions (
                    agent_name TEXT NOT NULL,
                    user_id TEXT,
                    allowed_topics JSONB NOT NULL
                )
            """
            )

            # Create unique constraint to handle NULL user_id properly
            cursor.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_agent_permissions_name_user 
                ON agent_permissions (agent_name, COALESCE(user_id, ''))
                """
            )

            # Create indexes
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_context_created_at ON context_items(created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_context_ttl ON context_items(ttl)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_context_user_id ON context_items(user_id)"
            )

            self.connection.commit()  # type: ignore

    def save_context_item(
        self,
        key: str,
        value: Any,
        subscribers: List[str],
        ttl: Optional[float],
        created_at: float,
    ) -> None:
        """Save a context item to PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            # Use UPDATE first, then INSERT if no rows affected
            cursor.execute(
                """
                UPDATE context_items 
                SET value = %s, subscribers = %s, ttl = %s, created_at = %s
                WHERE key = %s AND user_id IS NULL
                """,
                (json.dumps(value), json.dumps(subscribers), ttl, created_at, key),
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO context_items (key, user_id, value, subscribers, ttl, created_at)
                    VALUES (%s, NULL, %s, %s, %s, %s)
                    """,
                    (key, json.dumps(value), json.dumps(subscribers), ttl, created_at),
                )

            self.connection.commit()  # type: ignore

    def get_context_item(
        self, key: str
    ) -> Optional[Tuple[Any, List[str], Optional[float], float]]:
        """Retrieve a context item from PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "SELECT value, subscribers, ttl, created_at FROM context_items WHERE key = %s AND user_id IS NULL",
                (key,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            value, subscribers, ttl, created_at = row
            # psycopg2 automatically deserializes JSONB to Python objects
            value = value if value is not None else None
            subscribers = subscribers if subscribers is not None else []

            return (value, subscribers, ttl, created_at)

    def delete_context_item(self, key: str) -> bool:
        """Delete a context item from PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "DELETE FROM context_items WHERE key = %s AND user_id IS NULL", (key,)
            )
            deleted = cursor.rowcount > 0
            self.connection.commit()  # type: ignore
            return deleted

    def get_all_context_items(
        self,
    ) -> Dict[str, Tuple[Any, List[str], Optional[float], float]]:
        """Get all context items from PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "SELECT key, value, subscribers, ttl, created_at FROM context_items WHERE user_id IS NULL"
            )

            result = {}
            for row in cursor.fetchall():
                key, value, subscribers, ttl, created_at = row
                # psycopg2 automatically deserializes JSONB to Python objects
                value = value if value is not None else None
                subscribers = subscribers if subscribers is not None else []
                result[key] = (value, subscribers, ttl, created_at)

            return result

    def cleanup_expired(self, current_time: float) -> int:
        """Remove expired context items from PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "DELETE FROM context_items WHERE user_id IS NULL AND ttl IS NOT NULL AND (created_at + ttl) < %s",
                (current_time,),
            )
            deleted_count = cursor.rowcount
            self.connection.commit()  # type: ignore
            return deleted_count

    def clear_all(self) -> None:
        """Clear all context items from PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute("DELETE FROM context_items WHERE user_id IS NULL")
            cursor.execute("DELETE FROM agent_topics WHERE user_id IS NULL")
            cursor.execute("DELETE FROM agent_permissions WHERE user_id IS NULL")
            self.connection.commit()  # type: ignore

    def save_agent_topics(self, agent_name: str, topics: List[str]) -> None:
        """Save agent topics to PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            # Use UPDATE first, then INSERT if no rows affected
            cursor.execute(
                """
                UPDATE agent_topics 
                SET topics = %s
                WHERE agent_name = %s AND user_id IS NULL
                """,
                (json.dumps(topics), agent_name),
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO agent_topics (agent_name, user_id, topics)
                    VALUES (%s, NULL, %s)
                    """,
                    (agent_name, json.dumps(topics)),
                )

            self.connection.commit()  # type: ignore

    def get_agent_topics(self, agent_name: str) -> List[str]:
        """Get agent topics from PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "SELECT topics FROM agent_topics WHERE agent_name = %s AND user_id IS NULL",
                (agent_name,),
            )
            row = cursor.fetchone()

            if row is None:
                return []

            return row[0] if row[0] is not None else []

    def get_all_agent_topics(self) -> Dict[str, List[str]]:
        """Get all agent topics from PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "SELECT agent_name, topics FROM agent_topics WHERE user_id IS NULL"
            )

            result = {}
            for agent_name, topics in cursor.fetchall():
                result[agent_name] = topics if topics is not None else []

            return result

    def remove_agent_topics(self, agent_name: str) -> None:
        """Remove agent topic subscriptions from PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "DELETE FROM agent_topics WHERE agent_name = %s AND user_id IS NULL",
                (agent_name,),
            )
            self.connection.commit()  # type: ignore

    def save_agent_permissions(
        self, agent_name: str, allowed_topics: List[str]
    ) -> None:
        """Save agent permissions to PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            # Use UPDATE first, then INSERT if no rows affected
            cursor.execute(
                """
                UPDATE agent_permissions 
                SET allowed_topics = %s
                WHERE agent_name = %s AND user_id IS NULL
                """,
                (json.dumps(allowed_topics), agent_name),
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO agent_permissions (agent_name, user_id, allowed_topics)
                    VALUES (%s, NULL, %s)
                    """,
                    (agent_name, json.dumps(allowed_topics)),
                )

            self.connection.commit()  # type: ignore

    def get_agent_permissions(self, agent_name: str) -> List[str]:
        """Get agent permissions from PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "SELECT allowed_topics FROM agent_permissions WHERE agent_name = %s AND user_id IS NULL",
                (agent_name,),
            )
            row = cursor.fetchone()

            if row is None:
                return []

            return row[0] if row[0] is not None else []

    def get_all_agent_permissions(self) -> Dict[str, List[str]]:
        """Get all agent permissions from PostgreSQL (legacy mode - user_id = NULL)."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "SELECT agent_name, allowed_topics FROM agent_permissions WHERE user_id IS NULL"
            )

            result = {}
            for agent_name, allowed_topics in cursor.fetchall():
                result[agent_name] = (
                    allowed_topics if allowed_topics is not None else []
                )

            return result

    # User isolation methods
    def save_context_item_for_user(
        self,
        user_id: str,
        key: str,
        value: Any,
        subscribers: List[str],
        ttl: Optional[float],
        created_at: float,
    ) -> None:
        """Save a context item for a specific user to PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            # Use UPDATE first, then INSERT if no rows affected
            cursor.execute(
                """
                UPDATE context_items 
                SET value = %s, subscribers = %s, ttl = %s, created_at = %s
                WHERE key = %s AND (user_id = %s OR (user_id IS NULL AND %s IS NULL))
                """,
                (
                    json.dumps(value),
                    json.dumps(subscribers),
                    ttl,
                    created_at,
                    key,
                    user_id,
                    user_id,
                ),
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO context_items (key, user_id, value, subscribers, ttl, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        key,
                        user_id,
                        json.dumps(value),
                        json.dumps(subscribers),
                        ttl,
                        created_at,
                    ),
                )
            self.connection.commit()  # type: ignore

    def get_context_item_for_user(
        self, user_id: str, key: str
    ) -> Optional[Tuple[Any, List[str], Optional[float], float]]:
        """Get a context item for a specific user from PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "SELECT value, subscribers, ttl, created_at FROM context_items WHERE key = %s AND user_id = %s",
                (key, user_id),
            )
            row = cursor.fetchone()
            if row:
                value, subscribers, ttl, created_at = row
                # psycopg2 automatically deserializes JSONB to Python objects
                value = value if value is not None else None
                subscribers = subscribers if subscribers is not None else []
                return (value, subscribers, ttl, created_at)
            return None

    def get_all_context_items_for_user(
        self, user_id: str
    ) -> Dict[str, Tuple[Any, List[str], Optional[float], float]]:
        """Get all context items for a specific user from PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "SELECT key, value, subscribers, ttl, created_at FROM context_items WHERE user_id = %s",
                (user_id,),
            )
            result = {}
            for row in cursor.fetchall():
                key, value, subscribers, ttl, created_at = row
                # psycopg2 automatically deserializes JSONB to Python objects
                value = value if value is not None else None
                subscribers = subscribers if subscribers is not None else []
                result[key] = (value, subscribers, ttl, created_at)
            return result

    def delete_context_item_for_user(self, user_id: str, key: str) -> bool:
        """Delete a context item for a specific user from PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "DELETE FROM context_items WHERE key = %s AND user_id = %s",
                (key, user_id),
            )
            deleted = cursor.rowcount > 0
            self.connection.commit()  # type: ignore
            return deleted

    def save_agent_topics_for_user(
        self, user_id: str, agent_name: str, topics: List[str]
    ) -> None:
        """Save agent topics for a specific user to PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            # Use UPDATE first, then INSERT if no rows affected
            cursor.execute(
                """
                UPDATE agent_topics 
                SET topics = %s
                WHERE agent_name = %s AND (user_id = %s OR (user_id IS NULL AND %s IS NULL))
                """,
                (json.dumps(topics), agent_name, user_id, user_id),
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO agent_topics (agent_name, user_id, topics)
                    VALUES (%s, %s, %s)
                    """,
                    (agent_name, user_id, json.dumps(topics)),
                )
            self.connection.commit()  # type: ignore

    def get_agent_topics_for_user(self, user_id: str, agent_name: str) -> List[str]:
        """Get agent topics for a specific user from PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "SELECT topics FROM agent_topics WHERE agent_name = %s AND user_id = %s",
                (agent_name, user_id),
            )
            row = cursor.fetchone()
            if row:
                topics = row[0]
                # psycopg2 automatically deserializes JSONB to Python objects
                return topics if topics is not None else []
            return []

    def get_all_agent_topics_for_user(self, user_id: str) -> Dict[str, List[str]]:
        """Get all agent topics for a specific user from PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "SELECT agent_name, topics FROM agent_topics WHERE user_id = %s",
                (user_id,),
            )
            result = {}
            for row in cursor.fetchall():
                agent_name, topics = row
                # psycopg2 automatically deserializes JSONB to Python objects
                result[agent_name] = topics if topics is not None else []
            return result

    def remove_agent_topics_for_user(self, user_id: str, agent_name: str) -> None:
        """Remove agent topics for a specific user from PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "DELETE FROM agent_topics WHERE agent_name = %s AND user_id = %s",
                (agent_name, user_id),
            )
            self.connection.commit()  # type: ignore

    def save_agent_permissions_for_user(
        self, user_id: str, agent_name: str, allowed_topics: List[str]
    ) -> None:
        """Save agent permissions for a specific user to PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            # Use UPDATE first, then INSERT if no rows affected
            cursor.execute(
                """
                UPDATE agent_permissions 
                SET allowed_topics = %s
                WHERE agent_name = %s AND (user_id = %s OR (user_id IS NULL AND %s IS NULL))
                """,
                (json.dumps(allowed_topics), agent_name, user_id, user_id),
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO agent_permissions (agent_name, user_id, allowed_topics)
                    VALUES (%s, %s, %s)
                    """,
                    (agent_name, user_id, json.dumps(allowed_topics)),
                )
            self.connection.commit()  # type: ignore

    def get_agent_permissions_for_user(
        self, user_id: str, agent_name: str
    ) -> List[str]:
        """Get agent permissions for a specific user from PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "SELECT allowed_topics FROM agent_permissions WHERE agent_name = %s AND user_id = %s",
                (agent_name, user_id),
            )
            row = cursor.fetchone()
            if row:
                allowed_topics = row[0]
                # psycopg2 automatically deserializes JSONB to Python objects
                return allowed_topics if allowed_topics is not None else []
            return []

    def get_all_agent_permissions_for_user(self, user_id: str) -> Dict[str, List[str]]:
        """Get all agent permissions for a specific user from PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                "SELECT agent_name, allowed_topics FROM agent_permissions WHERE user_id = %s",
                (user_id,),
            )
            result = {}
            for row in cursor.fetchall():
                agent_name, allowed_topics = row
                # psycopg2 automatically deserializes JSONB to Python objects
                result[agent_name] = (
                    allowed_topics if allowed_topics is not None else []
                )
            return result

    def cleanup_expired_for_user(self, user_id: str, current_time: float) -> int:
        """Clean up expired items for a specific user from PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute(
                """
                DELETE FROM context_items
                WHERE user_id = %s AND ttl IS NOT NULL AND (created_at + ttl) < %s
                """,
                (user_id, current_time),
            )
            removed_count = cursor.rowcount
            self.connection.commit()  # type: ignore
            return removed_count

    def clear_all_for_user(self, user_id: str) -> None:
        """Clear all data for a specific user from PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore
            cursor.execute("DELETE FROM context_items WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM agent_topics WHERE user_id = %s", (user_id,))
            cursor.execute(
                "DELETE FROM agent_permissions WHERE user_id = %s", (user_id,)
            )
            self.connection.commit()  # type: ignore

    def delete_topic_data_for_user(self, user_id: str, topic: str) -> None:
        """Delete all data related to a topic for a specific user from PostgreSQL."""
        with self._lock:
            cursor = self.connection.cursor()  # type: ignore

            # Delete context items that have this topic (by checking subscribers)
            cursor.execute(
                """
                DELETE FROM context_items 
                WHERE user_id = %s AND subscribers::jsonb ? %s
                """,
                (user_id, topic),
            )

            # Remove topic from agent subscriptions
            cursor.execute(
                """
                UPDATE agent_topics 
                SET topics = (
                    SELECT jsonb_agg(topic)
                    FROM jsonb_array_elements_text(topics) AS topic
                    WHERE topic != %s
                )
                WHERE user_id = %s AND topics::jsonb ? %s
                """,
                (topic, user_id, topic),
            )

            # Remove topic from agent permissions
            cursor.execute(
                """
                UPDATE agent_permissions 
                SET allowed_topics = (
                    SELECT jsonb_agg(topic)
                    FROM jsonb_array_elements_text(allowed_topics) AS topic
                    WHERE topic != %s
                )
                WHERE user_id = %s AND allowed_topics::jsonb ? %s
                """,
                (topic, user_id, topic),
            )

            self.connection.commit()  # type: ignore


def create_database_backend(backend_type: str = "sqlite", **kwargs) -> DatabaseBackend:
    """
    Factory function to create database backends.

    Args:
        backend_type: Type of backend ("sqlite", "postgresql", "mysql")
        **kwargs: Backend-specific configuration

    Returns:
        Configured database backend instance
    """
    if backend_type.lower() == "sqlite":
        db_path = kwargs.get("db_path", "syntha_context.db")
        return SQLiteBackend(db_path)

    elif backend_type.lower() == "postgresql":
        connection_string = kwargs.get("connection_string")

        # If connection_string is provided, use it directly
        if connection_string:
            return PostgreSQLBackend(connection_string)

        # Otherwise, build connection string from individual parameters
        host = kwargs.get("host", "localhost")
        port = kwargs.get("port", 5432)
        database = kwargs.get("database") or kwargs.get("db_name")
        user = kwargs.get("user") or kwargs.get("username")
        password = kwargs.get("password")

        # Validate required parameters
        if not database:
            raise ValueError(
                "Either 'connection_string' or 'database'/'db_name' is required for PostgreSQL backend"
            )
        if not user:
            raise ValueError(
                "Either 'connection_string' or 'user'/'username' is required for PostgreSQL backend"
            )
        if not password:
            raise ValueError(
                "Either 'connection_string' or 'password' is required for PostgreSQL backend"
            )

        # Build connection string from individual parameters
        built_connection_string = (
            f"postgresql://{user}:{password}@{host}:{port}/{database}"
        )

        # Add SSL mode if specified
        sslmode = kwargs.get("sslmode")
        if sslmode:
            built_connection_string += f"?sslmode={sslmode}"

        return PostgreSQLBackend(built_connection_string)

    # Add more backends as needed
    # elif backend_type.lower() == "mysql":
    #     return MySQLBackend(kwargs.get("connection_string"))

    else:
        raise ValueError(f"Unsupported backend type: {backend_type}")

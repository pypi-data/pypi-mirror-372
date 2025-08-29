#!/usr/bin/env python3
"""
User Isolation Tests for Syntha Persistence Layer

Tests that user contexts are properly isolated in both SQLite and PostgreSQL backends.
"""

import os
import tempfile
import time
from unittest.mock import patch

import pytest

from syntha.context import ContextMesh
from syntha.persistence import SQLiteBackend, create_database_backend


class TestUserIsolationSQLite:
    """Test user isolation with SQLite backend."""

    def setup_method(self):
        """Set up test fixtures with temporary SQLite database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

        # Create two separate user contexts
        self.user1_mesh = ContextMesh(
            user_id="user1",
            enable_persistence=True,
            db_backend="sqlite",
            db_path=self.temp_db.name,
        )

        self.user2_mesh = ContextMesh(
            user_id="user2",
            enable_persistence=True,
            db_backend="sqlite",
            db_path=self.temp_db.name,
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, "user1_mesh"):
            self.user1_mesh.close()
        if hasattr(self, "user2_mesh"):
            self.user2_mesh.close()

        if hasattr(self, "temp_db") and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except PermissionError:
                pass

    def test_context_isolation_basic(self):
        """Test that basic context is isolated between users."""
        # User 1 pushes context
        self.user1_mesh.push("shared_key", "user1_value")

        # User 2 pushes context with same key
        self.user2_mesh.push("shared_key", "user2_value")

        # Each user should only see their own value
        assert self.user1_mesh.get("shared_key", "agent1") == "user1_value"
        assert self.user2_mesh.get("shared_key", "agent2") == "user2_value"

        # User 1 should not see user 2's data and vice versa
        assert self.user1_mesh.get("shared_key", "agent1") != "user2_value"
        assert self.user2_mesh.get("shared_key", "agent2") != "user1_value"

    def test_agent_topics_isolation(self):
        """Test that agent topics are isolated between users."""
        # User 1 registers agent topics
        self.user1_mesh.register_agent_topics("sales_agent", ["sales", "user1_data"])

        # User 2 registers agent topics with same agent name
        self.user2_mesh.register_agent_topics("sales_agent", ["sales", "user2_data"])

        # Each user should only see their own agent topics
        user1_topics = self.user1_mesh.get_topics_for_agent("sales_agent")
        user2_topics = self.user2_mesh.get_topics_for_agent("sales_agent")

        assert "user1_data" in user1_topics
        assert "user1_data" not in user2_topics
        assert "user2_data" in user2_topics
        assert "user2_data" not in user1_topics

    def test_agent_permissions_isolation(self):
        """Test that agent permissions are isolated between users."""
        # User 1 sets agent permissions
        self.user1_mesh.set_agent_post_permissions("agent1", ["user1_topic"])

        # User 2 sets agent permissions with same agent name
        self.user2_mesh.set_agent_post_permissions("agent1", ["user2_topic"])

        # Each user should only see their own agent permissions
        user1_perms = self.user1_mesh.get_agent_post_permissions("agent1")
        user2_perms = self.user2_mesh.get_agent_post_permissions("agent1")

        assert user1_perms == ["user1_topic"]
        assert user2_perms == ["user2_topic"]

    def test_ttl_isolation(self):
        """Test that TTL cleanup is isolated between users."""
        # User 1 pushes context with short TTL
        self.user1_mesh.push("expire_key", "user1_expire", ttl=0.1)

        # User 2 pushes context with same key but longer TTL
        self.user2_mesh.push("expire_key", "user2_persist", ttl=10.0)

        # Wait for user 1's context to expire
        time.sleep(0.2)

        # Clean up expired items
        user1_removed = self.user1_mesh.cleanup_expired()
        user2_removed = self.user2_mesh.cleanup_expired()

        # Only user 1's item should be removed
        assert user1_removed == 1
        assert user2_removed == 0

        # User 1's context should be gone, user 2's should remain
        assert self.user1_mesh.get("expire_key", "agent1") is None
        assert self.user2_mesh.get("expire_key", "agent2") == "user2_persist"

    def test_topic_based_context_isolation(self):
        """Test that topic-based context is isolated between users."""
        # User 1 sets up topics and pushes context
        self.user1_mesh.register_agent_topics("agent1", ["shared_topic"])
        self.user1_mesh.push("topic_data", "user1_topic_data", topics=["shared_topic"])

        # User 2 sets up same topics and pushes context
        self.user2_mesh.register_agent_topics("agent2", ["shared_topic"])
        self.user2_mesh.push("topic_data", "user2_topic_data", topics=["shared_topic"])

        # Each user should only see their own topic data
        user1_data = self.user1_mesh.get("topic_data", "agent1")
        user2_data = self.user2_mesh.get("topic_data", "agent2")

        assert user1_data == "user1_topic_data"
        assert user2_data == "user2_topic_data"

    def test_persistence_across_restarts(self):
        """Test that user isolation persists across system restarts."""
        # User 1 pushes context
        self.user1_mesh.push("persistent_key", "user1_persistent")

        # User 2 pushes context with same key
        self.user2_mesh.push("persistent_key", "user2_persistent")

        # Close both contexts
        self.user1_mesh.close()
        self.user2_mesh.close()

        # Recreate contexts (simulating restart)
        self.user1_mesh = ContextMesh(
            user_id="user1",
            enable_persistence=True,
            db_backend="sqlite",
            db_path=self.temp_db.name,
        )

        self.user2_mesh = ContextMesh(
            user_id="user2",
            enable_persistence=True,
            db_backend="sqlite",
            db_path=self.temp_db.name,
        )

        # Each user should still only see their own data
        assert self.user1_mesh.get("persistent_key", "agent1") == "user1_persistent"
        assert self.user2_mesh.get("persistent_key", "agent2") == "user2_persistent"

    def test_clear_user_data_isolation(self):
        """Test that clearing user data only affects that user."""
        # Both users push context
        self.user1_mesh.push("clear_test", "user1_data")
        self.user2_mesh.push("clear_test", "user2_data")

        # Clear user 1's data
        self.user1_mesh.clear()

        # User 1's data should be gone, user 2's should remain
        assert self.user1_mesh.get("clear_test", "agent1") is None
        assert self.user2_mesh.get("clear_test", "agent2") == "user2_data"


@pytest.mark.skipif(
    os.getenv("SKIP_POSTGRESQL_TESTS", "false").lower() == "true",
    reason="PostgreSQL tests skipped (set SKIP_POSTGRESQL_TESTS=false to enable)",
)
class TestUserIsolationPostgreSQL:
    """Test user isolation with PostgreSQL backend."""

    def setup_method(self):
        """Set up test fixtures with PostgreSQL database."""
        # Use test database connection string
        connection_string = os.getenv(
            "TEST_POSTGRESQL_URL",
            "postgresql://postgres:password@localhost:5432/syntha_test",
        )

        try:
            # Create two separate user contexts
            self.user1_mesh = ContextMesh(
                user_id="user1",
                enable_persistence=True,
                db_backend="postgresql",
                connection_string=connection_string,
            )

            self.user2_mesh = ContextMesh(
                user_id="user2",
                enable_persistence=True,
                db_backend="postgresql",
                connection_string=connection_string,
            )

            # Clear any existing test data
            self.user1_mesh.clear()
            self.user2_mesh.clear()

        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")

    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, "user1_mesh"):
            try:
                self.user1_mesh.clear()
                self.user1_mesh.close()
            except:
                pass

        if hasattr(self, "user2_mesh"):
            try:
                self.user2_mesh.clear()
                self.user2_mesh.close()
            except:
                pass

    def test_context_isolation_basic_postgresql(self):
        """Test that basic context is isolated between users in PostgreSQL."""
        # User 1 pushes context
        self.user1_mesh.push("pg_shared_key", "user1_pg_value")

        # User 2 pushes context with same key
        self.user2_mesh.push("pg_shared_key", "user2_pg_value")

        # Each user should only see their own value
        assert self.user1_mesh.get("pg_shared_key", "agent1") == "user1_pg_value"
        assert self.user2_mesh.get("pg_shared_key", "agent2") == "user2_pg_value"

    def test_agent_topics_isolation_postgresql(self):
        """Test that agent topics are isolated between users in PostgreSQL."""
        # User 1 registers agent topics
        self.user1_mesh.register_agent_topics(
            "pg_agent", ["pg_topic1", "user1_pg_data"]
        )

        # User 2 registers agent topics with same agent name
        self.user2_mesh.register_agent_topics(
            "pg_agent", ["pg_topic1", "user2_pg_data"]
        )

        # Each user should only see their own agent topics
        user1_topics = self.user1_mesh.get_topics_for_agent("pg_agent")
        user2_topics = self.user2_mesh.get_topics_for_agent("pg_agent")

        assert "user1_pg_data" in user1_topics
        assert "user1_pg_data" not in user2_topics
        assert "user2_pg_data" in user2_topics
        assert "user2_pg_data" not in user1_topics

    def test_agent_permissions_isolation_postgresql(self):
        """Test that agent permissions are isolated between users in PostgreSQL."""
        # User 1 sets agent permissions
        self.user1_mesh.set_agent_post_permissions("pg_agent", ["user1_pg_topic"])

        # User 2 sets agent permissions with same agent name
        self.user2_mesh.set_agent_post_permissions("pg_agent", ["user2_pg_topic"])

        # Each user should only see their own agent permissions
        user1_perms = self.user1_mesh.get_agent_post_permissions("pg_agent")
        user2_perms = self.user2_mesh.get_agent_post_permissions("pg_agent")

        assert user1_perms == ["user1_pg_topic"]
        assert user2_perms == ["user2_pg_topic"]

    def test_ttl_isolation_postgresql(self):
        """Test that TTL cleanup is isolated between users in PostgreSQL."""
        # User 1 pushes context with short TTL
        self.user1_mesh.push("pg_expire_key", "user1_pg_expire", ttl=0.1)

        # User 2 pushes context with same key but longer TTL
        self.user2_mesh.push("pg_expire_key", "user2_pg_persist", ttl=10.0)

        # Wait for user 1's context to expire
        time.sleep(0.2)

        # Clean up expired items
        user1_removed = self.user1_mesh.cleanup_expired()
        user2_removed = self.user2_mesh.cleanup_expired()

        # Only user 1's item should be removed
        assert user1_removed == 1
        assert user2_removed == 0

        # User 1's context should be gone, user 2's should remain
        assert self.user1_mesh.get("pg_expire_key", "agent1") is None
        assert self.user2_mesh.get("pg_expire_key", "agent2") == "user2_pg_persist"

    def test_jsonb_operations_postgresql(self):
        """Test PostgreSQL-specific JSONB operations with user isolation."""
        # User 1 pushes complex JSON data
        user1_data = {
            "user": "user1",
            "preferences": {"theme": "dark", "lang": "en"},
            "scores": [95, 87, 92],
        }
        self.user1_mesh.push("complex_data", user1_data)

        # User 2 pushes different complex JSON data with same key
        user2_data = {
            "user": "user2",
            "preferences": {"theme": "light", "lang": "es"},
            "scores": [88, 94, 90],
        }
        self.user2_mesh.push("complex_data", user2_data)

        # Each user should get their own complex data back
        retrieved_user1 = self.user1_mesh.get("complex_data", "agent1")
        retrieved_user2 = self.user2_mesh.get("complex_data", "agent2")

        assert retrieved_user1["user"] == "user1"
        assert retrieved_user1["preferences"]["theme"] == "dark"
        assert retrieved_user2["user"] == "user2"
        assert retrieved_user2["preferences"]["theme"] == "light"


class TestUserIsolationEdgeCases:
    """Test edge cases for user isolation."""

    def test_no_user_id_fallback(self):
        """Test that contexts without user_id still work (legacy mode)."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()

        try:
            # Create context without user_id (legacy mode)
            mesh = ContextMesh(
                enable_persistence=True,
                db_backend="sqlite",
                db_path=temp_db.name,
            )

            # Should still be able to push/get context
            mesh.push("legacy_key", "legacy_value")
            assert mesh.get("legacy_key", "agent1") == "legacy_value"

            mesh.close()

        finally:
            if os.path.exists(temp_db.name):
                try:
                    os.unlink(temp_db.name)
                except PermissionError:
                    pass

    def test_empty_user_id(self):
        """Test behavior with empty user_id."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()

        try:
            # Create context with empty user_id
            mesh = ContextMesh(
                user_id="",
                enable_persistence=True,
                db_backend="sqlite",
                db_path=temp_db.name,
            )

            # Should still work
            mesh.push("empty_user_key", "empty_user_value")
            assert mesh.get("empty_user_key", "agent1") == "empty_user_value"

            mesh.close()

        finally:
            if os.path.exists(temp_db.name):
                try:
                    os.unlink(temp_db.name)
                except PermissionError:
                    pass

    def test_special_characters_in_user_id(self):
        """Test user isolation with special characters in user_id."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()

        try:
            # Create contexts with special characters in user_id
            user1_mesh = ContextMesh(
                user_id="user@domain.com",
                enable_persistence=True,
                db_backend="sqlite",
                db_path=temp_db.name,
            )

            user2_mesh = ContextMesh(
                user_id="user-123_test",
                enable_persistence=True,
                db_backend="sqlite",
                db_path=temp_db.name,
            )

            # Should handle special characters correctly
            user1_mesh.push("special_key", "email_user_value")
            user2_mesh.push("special_key", "dash_underscore_user_value")

            assert user1_mesh.get("special_key", "agent1") == "email_user_value"
            assert (
                user2_mesh.get("special_key", "agent2") == "dash_underscore_user_value"
            )

            user1_mesh.close()
            user2_mesh.close()

        finally:
            if os.path.exists(temp_db.name):
                try:
                    os.unlink(temp_db.name)
                except PermissionError:
                    pass


def test_user_isolation_performance():
    """Test that user isolation doesn't significantly impact performance."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()

    try:
        # Create multiple user contexts
        meshes = []
        for i in range(5):
            mesh = ContextMesh(
                user_id=f"perf_user_{i}",
                enable_persistence=True,
                db_backend="sqlite",
                db_path=temp_db.name,
            )
            meshes.append(mesh)

        # Measure time for bulk operations using more precise timing
        start_time = time.perf_counter()

        # Each user pushes 20 items
        for i, mesh in enumerate(meshes):
            for j in range(20):
                mesh.push(f"perf_key_{j}", f"user_{i}_value_{j}")

        # Each user retrieves their items
        for i, mesh in enumerate(meshes):
            for j in range(20):
                value = mesh.get(f"perf_key_{j}", f"agent_{i}")
                assert value == f"user_{i}_value_{j}"

        elapsed = time.perf_counter() - start_time

        # Should complete in reasonable time (5 users × 40 operations each = 200 ops)
        # Allow more time on slower systems and CI
        import os
        import platform
        import sys

        is_ci = (
            os.getenv("CI", "false").lower() == "true"
            or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
        )
        ci_multiplier = 1.5 if is_ci else 1.0

        # More generous timeout for Windows (any Python version)
        if platform.system() == "Windows":
            timeout = 10.0 * ci_multiplier  # was 8.0
        else:
            timeout = 4.0 * ci_multiplier  # was 3.0

        assert (
            elapsed < timeout
        ), f"Performance test took {elapsed:.3f}s (expected < {timeout}s on {platform.system()} Python {sys.version_info[:2]})"

        # Clean up
        for mesh in meshes:
            mesh.close()

    finally:
        if os.path.exists(temp_db.name):
            try:
                os.unlink(temp_db.name)
            except PermissionError:
                pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])

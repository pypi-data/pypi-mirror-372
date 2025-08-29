#!/usr/bin/env python3
"""
Test for PostgreSQL JSON parsing fix

This test ensures that the PostgreSQL backend correctly handles JSONB data
without trying to double-parse JSON that's already been deserialized by psycopg2.
"""

import os

import pytest

from syntha import ContextMesh


@pytest.mark.skipif(
    os.getenv("SKIP_POSTGRESQL_TESTS", "false").lower() == "true",
    reason="PostgreSQL tests skipped (set SKIP_POSTGRESQL_TESTS=false to enable)",
)
class TestPostgreSQLJSONFix:
    """Test PostgreSQL JSON handling fix."""

    def setup_method(self):
        """Set up test fixtures with PostgreSQL database."""
        connection_string = os.getenv(
            "TEST_POSTGRESQL_URL",
            "postgresql://postgres:password@localhost:5432/syntha_test",
        )

        try:
            self.mesh = ContextMesh(
                user_id="json_test_user",
                enable_persistence=True,
                db_backend="postgresql",
                connection_string=connection_string,
            )

            # Clear any existing test data
            self.mesh.clear()

        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")

    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, "mesh"):
            try:
                self.mesh.clear()
                self.mesh.close()
            except:
                pass

    def test_multiple_runs_no_json_error(self):
        """Test that multiple runs don't cause JSON parsing errors."""
        # First run - push some data
        test_data = {
            "message": "Hello from PostgreSQL!",
            "numbers": [1, 2, 3],
            "nested": {"key": "value"},
        }

        self.mesh.push("test_key", test_data)
        result1 = self.mesh.get("test_key", "test_agent")

        assert result1 == test_data

        # Close and recreate mesh (simulating second run)
        self.mesh.close()

        connection_string = os.getenv(
            "TEST_POSTGRESQL_URL",
            "postgresql://postgres:password@localhost:5432/syntha_test",
        )

        self.mesh = ContextMesh(
            user_id="json_test_user",
            enable_persistence=True,
            db_backend="postgresql",
            connection_string=connection_string,
        )

        # Second run - should load existing data without JSON errors
        result2 = self.mesh.get("test_key", "test_agent")

        assert result2 == test_data
        assert result2["message"] == "Hello from PostgreSQL!"
        assert result2["numbers"] == [1, 2, 3]
        assert result2["nested"]["key"] == "value"

    def test_complex_json_data_persistence(self):
        """Test that complex JSON data persists correctly."""
        complex_data = {
            "user_profile": {
                "name": "Test User",
                "preferences": {
                    "theme": "dark",
                    "notifications": True,
                    "languages": ["en", "es", "fr"],
                },
                "history": [
                    {"action": "login", "timestamp": 1234567890},
                    {"action": "update_profile", "timestamp": 1234567891},
                ],
            },
            "metadata": {
                "version": "1.0",
                "tags": ["test", "user", "profile"],
                "scores": [95.5, 87.2, 92.8],
            },
        }

        # Store complex data
        self.mesh.push("complex_profile", complex_data)

        # Retrieve and verify
        retrieved = self.mesh.get("complex_profile", "profile_agent")

        assert retrieved == complex_data
        assert retrieved["user_profile"]["name"] == "Test User"
        assert retrieved["user_profile"]["preferences"]["languages"] == [
            "en",
            "es",
            "fr",
        ]
        assert retrieved["metadata"]["scores"] == [95.5, 87.2, 92.8]

    def test_agent_topics_json_handling(self):
        """Test that agent topics are handled correctly."""
        topics = ["topic1", "topic2", "complex_topic_with_underscores"]

        # Register topics
        self.mesh.register_agent_topics("json_test_agent", topics)

        # Retrieve topics
        retrieved_topics = self.mesh.get_topics_for_agent("json_test_agent")

        assert set(retrieved_topics) == set(topics)

        # Close and reopen to test persistence
        self.mesh.close()

        connection_string = os.getenv(
            "TEST_POSTGRESQL_URL",
            "postgresql://postgres:password@localhost:5432/syntha_test",
        )

        self.mesh = ContextMesh(
            user_id="json_test_user",
            enable_persistence=True,
            db_backend="postgresql",
            connection_string=connection_string,
        )

        # Should still work after restart
        persistent_topics = self.mesh.get_topics_for_agent("json_test_agent")
        assert set(persistent_topics) == set(topics)

    def test_agent_permissions_json_handling(self):
        """Test that agent permissions are handled correctly."""
        permissions = ["perm1", "perm2", "admin_permission"]

        # Set permissions
        self.mesh.set_agent_post_permissions("json_test_agent", permissions)

        # Retrieve permissions
        retrieved_perms = self.mesh.get_agent_post_permissions("json_test_agent")

        assert set(retrieved_perms) == set(permissions)

        # Close and reopen to test persistence
        self.mesh.close()

        connection_string = os.getenv(
            "TEST_POSTGRESQL_URL",
            "postgresql://postgres:password@localhost:5432/syntha_test",
        )

        self.mesh = ContextMesh(
            user_id="json_test_user",
            enable_persistence=True,
            db_backend="postgresql",
            connection_string=connection_string,
        )

        # Should still work after restart
        persistent_perms = self.mesh.get_agent_post_permissions("json_test_agent")
        assert set(persistent_perms) == set(permissions)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])

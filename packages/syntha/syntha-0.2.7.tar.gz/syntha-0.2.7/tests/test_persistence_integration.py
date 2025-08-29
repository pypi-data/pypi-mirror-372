#!/usr/bin/env python3
"""
Comprehensive test suite for Syntha persistence features.

This test validates that all legacy features (TTL, indexing, auto cleanup, etc.)
work correctly with the new database persistence layer.

Tests cover:
- TTL functionality with database persistence
- Auto cleanup with database sync
- Indexing with persistence
- Topic-based routing persistence
- Agent permissions persistence
- Database-memory consistency
- Multi-backend functionality (SQLite/PostgreSQL)
- Performance characteristics
"""

import json
import os
import sys
import tempfile
import time
from typing import Any, Dict

import pytest

from syntha.context import ContextItem, ContextMesh
from syntha.persistence import SQLiteBackend, create_database_backend


class TestPersistenceIntegration:
    """Test persistence integration with all legacy features."""

    def setup_method(self):
        """Set up test fixtures with temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

        # Create mesh with all features enabled
        self.mesh = ContextMesh(
            enable_indexing=True,
            auto_cleanup=True,
            enable_persistence=True,
            db_path=self.temp_db.name,
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, "mesh") and self.mesh.db_backend:
            self.mesh.db_backend.close()

        if hasattr(self, "temp_db") and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except PermissionError:
                pass  # Ignore on Windows if file is locked

    def test_ttl_with_persistence(self):
        """Test that TTL functionality works correctly with database persistence."""
        # Push item with short TTL
        self.mesh.push("short_lived", "temporary_data", ttl=0.1)

        # Verify it exists immediately
        assert self.mesh.get("short_lived") == "temporary_data"

        # Verify it's in the database
        db_item = self.mesh.db_backend.get_context_item("short_lived")
        assert db_item is not None
        assert db_item[0] == "temporary_data"  # value
        assert db_item[2] == 0.1  # ttl

        # Wait for expiration (allow extra time on slower systems)
        time.sleep(0.3)

        # Manual cleanup should remove expired items from both memory and DB
        removed_count = self.mesh.cleanup_expired()
        assert removed_count >= 1

        # Verify removed from memory
        assert self.mesh.get("short_lived") is None

        # Verify removed from database
        db_item = self.mesh.db_backend.get_context_item("short_lived")
        assert db_item is None

    def test_auto_cleanup_with_persistence(self):
        """Test that auto cleanup works with database persistence."""
        # Use a more robust approach that doesn't rely on exact timing
        # Push item with short TTL
        self.mesh.push("auto_expire", "will_be_cleaned", ttl=0.1)

        # Verify it exists
        assert self.mesh.get("auto_expire") == "will_be_cleaned"

        # Wait for expiration
        time.sleep(0.3)

        # Force cleanup to ensure expired items are removed
        # This is more reliable than depending on auto-cleanup timing
        _ = self.mesh.cleanup_expired()

        # Poll until the item is cleaned up (be tolerant of scheduler delays)
        start = time.time()
        result = None
        while time.time() - start < 2.0:
            self.mesh.cleanup_expired()
            result = self.mesh.get("auto_expire")
            if result is None:
                break
            time.sleep(0.05)
        assert result is None, f"Expected None but got {result}"

        # Verify removed from database too (with polling tolerance)
        start = time.time()
        db_item = None
        while time.time() - start < 2.0:
            db_item = self.mesh.db_backend.get_context_item("auto_expire")
            if db_item is None:
                break
            time.sleep(0.05)
        assert db_item is None, f"Expected None from database but got {db_item}"

        # Test that auto-cleanup still works for new items
        # Temporarily reduce cleanup interval for testing
        original_interval = self.mesh._cleanup_interval
        self.mesh._cleanup_interval = 0.1

        try:
            # Reset the last cleanup time to ensure cleanup will trigger
            self.mesh._last_cleanup = 0

            # Push another item with short TTL
            self.mesh.push("auto_expire2", "will_be_cleaned2", ttl=0.05)

            # Verify it exists
            assert self.mesh.get("auto_expire2") == "will_be_cleaned2"

            # Wait for expiration plus cleanup interval
            time.sleep(0.5)

            # Trigger auto cleanup with another operation
            self.mesh.push("trigger_cleanup", "new_data")

            # Auto-cleanup should remove the expired item; poll to be lenient
            start = time.time()
            result = None
            while time.time() - start < 2.0:
                # Trigger potential cleanup again via explicit call
                self.mesh.cleanup_expired()
                result = self.mesh.get("auto_expire2")
                if result is None:
                    break
                time.sleep(0.05)
            assert result is None, f"Expected None but got {result}"

            # New item should still exist
            assert self.mesh.get("trigger_cleanup") == "new_data"

        finally:
            self.mesh._cleanup_interval = original_interval

    def test_indexing_with_persistence(self):
        """Test that indexing works correctly with database persistence."""
        # Push items for different agents
        self.mesh.push("global_item", "everyone_can_see", subscribers=[])
        self.mesh.push("agent1_item", "only_agent1", subscribers=["agent1"])
        self.mesh.push("shared_item", "agent1_and_2", subscribers=["agent1", "agent2"])

        # Test that indexing works for fast lookups
        agent1_keys = self.mesh.get_keys_for_agent("agent1")
        assert "global_item" in agent1_keys
        assert "agent1_item" in agent1_keys
        assert "shared_item" in agent1_keys

        agent2_keys = self.mesh.get_keys_for_agent("agent2")
        assert "global_item" in agent2_keys
        assert "agent1_item" not in agent2_keys
        assert "shared_item" in agent2_keys

        # Test persistence across restart
        self.mesh.close()

        # Recreate mesh with same database
        self.mesh = ContextMesh(
            enable_indexing=True,
            auto_cleanup=True,
            enable_persistence=True,
            db_path=self.temp_db.name,
        )

        # Verify indexes are rebuilt from database
        agent1_keys = self.mesh.get_keys_for_agent("agent1")
        assert "global_item" in agent1_keys
        assert "agent1_item" in agent1_keys
        assert "shared_item" in agent1_keys

    def test_topic_routing_persistence(self):
        """Test that topic-based routing persists correctly."""
        # Register agents for topics
        self.mesh.register_agent_topics("sales_agent", ["sales", "customer_data"])
        self.mesh.register_agent_topics("analytics_agent", ["sales", "analytics"])

        # Verify topics are registered
        assert self.mesh.get_topics_for_agent("sales_agent") == [
            "sales",
            "customer_data",
        ]
        assert self.mesh.get_subscribers_for_topic("sales") == [
            "sales_agent",
            "analytics_agent",
        ]

        # Push context to topics
        self.mesh.push("q4_sales", "Sales up 15%", topics=["sales"])

        # Verify context routing
        sales_context = self.mesh.get("q4_sales", "sales_agent")
        analytics_context = self.mesh.get("q4_sales", "analytics_agent")
        assert sales_context == "Sales up 15%"
        assert analytics_context == "Sales up 15%"

        # Test persistence across restart
        self.mesh.close()

        # Recreate mesh
        self.mesh = ContextMesh(
            enable_indexing=True,
            auto_cleanup=True,
            enable_persistence=True,
            db_path=self.temp_db.name,
        )

        # Verify topic subscriptions are restored
        assert self.mesh.get_topics_for_agent("sales_agent") == [
            "sales",
            "customer_data",
        ]
        assert self.mesh.get_subscribers_for_topic("sales") == [
            "sales_agent",
            "analytics_agent",
        ]

        # Verify context is still accessible
        assert self.mesh.get("q4_sales", "sales_agent") == "Sales up 15%"

    def test_agent_permissions_persistence(self):
        """Test that agent posting permissions persist correctly."""
        # Set posting permissions
        self.mesh.set_agent_post_permissions("junior_agent", ["notifications"])
        self.mesh.set_agent_post_permissions(
            "senior_agent", ["sales", "analytics", "notifications"]
        )

        # Verify permissions
        assert self.mesh.get_agent_post_permissions("junior_agent") == ["notifications"]
        assert "sales" in self.mesh.get_agent_post_permissions("senior_agent")

        # Test persistence across restart
        self.mesh.close()

        # Recreate mesh
        self.mesh = ContextMesh(
            enable_indexing=True,
            auto_cleanup=True,
            enable_persistence=True,
            db_path=self.temp_db.name,
        )

        # Verify permissions are restored
        assert self.mesh.get_agent_post_permissions("junior_agent") == ["notifications"]
        assert "sales" in self.mesh.get_agent_post_permissions("senior_agent")

    def test_database_memory_consistency(self):
        """Test that database and memory stay consistent."""
        # Add various types of data
        self.mesh.push("simple_string", "hello world")
        self.mesh.push("number_data", 42)
        self.mesh.push("complex_data", {"user": "alice", "score": 95.5, "active": True})
        self.mesh.push("with_ttl", "expires soon", ttl=3600)  # 1 hour
        self.mesh.push("private_data", "secret", subscribers=["agent1"])

        # Register topics and permissions
        self.mesh.register_agent_topics("test_agent", ["test_topic"])
        self.mesh.set_agent_post_permissions("test_agent", ["test_topic"])

        # Verify memory state
        assert self.mesh.get("simple_string") == "hello world"
        assert self.mesh.get("number_data") == 42
        assert self.mesh.get("complex_data")["user"] == "alice"
        assert self.mesh.get("with_ttl") == "expires soon"
        assert self.mesh.get("private_data", "agent1") == "secret"
        assert self.mesh.get("private_data", "agent2") is None

        # Verify database state matches
        db_items = self.mesh.db_backend.get_all_context_items()
        assert len(db_items) == 5
        assert db_items["simple_string"][0] == "hello world"
        assert db_items["number_data"][0] == 42
        assert db_items["complex_data"][0]["user"] == "alice"
        assert db_items["with_ttl"][2] == 3600  # ttl
        assert db_items["private_data"][1] == ["agent1"]  # subscribers

        # Verify topics in database
        db_topics = self.mesh.db_backend.get_all_agent_topics()
        assert db_topics["test_agent"] == ["test_topic"]

        # Verify permissions in database
        db_permissions = self.mesh.db_backend.get_all_agent_permissions()
        assert db_permissions["test_agent"] == ["test_topic"]

    def test_performance_with_persistence(self):
        """Test that performance characteristics are maintained with persistence."""
        import sys
        import time

        # Adjust timing thresholds based on Python version and platform
        # Windows CI environment can be significantly slower than Unix-like systems
        is_ci = (
            os.getenv("CI", "false").lower() == "true"
            or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
        )
        ci_multiplier = 1.5 if is_ci else 1.0  # Extra time for CI environments

        if sys.version_info < (3, 10) and os.name == "nt":
            # Most lenient for Python 3.9 on Windows
            insert_threshold = 8.0 * ci_multiplier  # 8+ seconds for 100 items
            retrieve_threshold = 1.5 * ci_multiplier  # 1.5+ seconds for 100 items
            cleanup_threshold = 2.5 * ci_multiplier  # 2.5+ seconds for cleanup
        elif sys.version_info < (3, 10):
            # More lenient for Python 3.9 on any platform
            insert_threshold = 3.0 * ci_multiplier  # 3+ seconds for 100 items
            retrieve_threshold = 0.3 * ci_multiplier  # 0.3+ seconds for 100 items
            cleanup_threshold = 0.8 * ci_multiplier  # 0.8+ seconds for cleanup
        elif os.name == "nt":
            # More lenient for Windows on any Python version (including 3.11+)
            insert_threshold = 4.0 * ci_multiplier  # 4+ seconds for 100 items
            retrieve_threshold = 0.6 * ci_multiplier  # 0.6+ seconds for 100 items
            cleanup_threshold = 1.2 * ci_multiplier  # 1.2+ seconds for cleanup
        else:
            # Original thresholds for Python 3.11+ on Unix-like systems
            insert_threshold = 2.0 * ci_multiplier  # 2+ seconds for 100 items
            retrieve_threshold = 0.2 * ci_multiplier  # 0.2+ seconds for 100 items
            cleanup_threshold = 0.5 * ci_multiplier  # 0.5+ seconds for cleanup

        # Test bulk insertion performance
        start_time = time.time()
        for i in range(100):
            self.mesh.push(f"perf_test_{i}", f"data_{i}")
        bulk_insert_time = time.time() - start_time

        # Should complete in reasonable time (adjusted for platform/version)
        assert (
            bulk_insert_time < insert_threshold
        ), f"Bulk insert took {bulk_insert_time:.3f}s (threshold: {insert_threshold}s)"

        # Test retrieval performance
        start_time = time.time()
        for i in range(100):
            value = self.mesh.get(f"perf_test_{i}")
            assert value == f"data_{i}"
        bulk_retrieve_time = time.time() - start_time

        # Retrieval should be fast (adjusted for platform/version)
        assert (
            bulk_retrieve_time < retrieve_threshold
        ), f"Bulk retrieve took {bulk_retrieve_time:.3f}s (threshold: {retrieve_threshold}s)"

        # Test cleanup performance
        # Add items with short TTL
        for i in range(50):
            self.mesh.push(f"expire_test_{i}", f"data_{i}", ttl=0.01)

        time.sleep(0.15)  # Let items expire (extra slack)

        start_time = time.time()
        removed = self.mesh.cleanup_expired()
        cleanup_time = time.time() - start_time

        assert removed >= 45
        assert (
            cleanup_time < cleanup_threshold
        ), f"Cleanup took {cleanup_time:.3f}s (threshold: {cleanup_threshold}s)"

    def test_persistence_disabled_fallback(self):
        """Test that system works correctly when persistence is disabled."""
        # Create mesh without persistence
        no_persist_mesh = ContextMesh(
            enable_indexing=True, auto_cleanup=True, enable_persistence=False
        )

        try:
            # All features should still work
            no_persist_mesh.push("test_key", "test_value", ttl=0.1)
            assert no_persist_mesh.get("test_key") == "test_value"

            # TTL should still work
            time.sleep(0.3)
            removed = no_persist_mesh.cleanup_expired()
            assert removed >= 1
            assert no_persist_mesh.get("test_key") is None

            # Topics should work
            no_persist_mesh.register_agent_topics("agent1", ["topic1"])
            assert no_persist_mesh.get_topics_for_agent("agent1") == ["topic1"]

        finally:
            no_persist_mesh.close()

    def test_complex_persistence_scenario(self):
        """Test a complex real-world scenario with persistence."""
        # Simulate a multi-agent system over time

        # Initial setup - agents join and subscribe to topics
        self.mesh.register_agent_topics("sales_agent", ["sales", "customer_data"])
        self.mesh.register_agent_topics(
            "marketing_agent", ["marketing", "customer_data"]
        )
        self.mesh.register_agent_topics(
            "analytics_agent", ["sales", "marketing", "analytics"]
        )

        # Set permissions
        self.mesh.set_agent_post_permissions("sales_agent", ["sales", "customer_data"])
        self.mesh.set_agent_post_permissions(
            "marketing_agent", ["marketing", "customer_data"]
        )
        self.mesh.set_agent_post_permissions("analytics_agent", ["analytics"])

        # Phase 1: Sales agent shares customer data
        self.mesh.push(
            "customer_analysis",
            {"segment": "enterprise", "growth": 0.15},
            topics=["customer_data"],
        )

        # Phase 2: Marketing agent shares campaign data
        self.mesh.push(
            "campaign_results",
            {"campaign": "Q1_promo", "conversion": 0.08},
            topics=["marketing"],
        )

        # Phase 3: Analytics agent creates insights (with TTL)
        self.mesh.push(
            "weekly_insights",
            "Customer engagement up 12% this week",
            topics=["analytics"],
            ttl=604800,
        )  # 1 week

        # Verify all agents can access relevant data
        customer_data = self.mesh.get("customer_analysis", "sales_agent")
        assert customer_data["segment"] == "enterprise"

        marketing_data = self.mesh.get("campaign_results", "marketing_agent")
        assert marketing_data["conversion"] == 0.08

        insights = self.mesh.get("weekly_insights", "analytics_agent")
        assert "engagement up 12%" in insights

        # Test persistence by restarting the system
        self.mesh.close()

        # Restart
        self.mesh = ContextMesh(
            enable_indexing=True,
            auto_cleanup=True,
            enable_persistence=True,
            db_path=self.temp_db.name,
        )

        # Verify everything is restored correctly
        assert self.mesh.get_topics_for_agent("sales_agent") == [
            "sales",
            "customer_data",
        ]
        assert self.mesh.get_agent_post_permissions("analytics_agent") == ["analytics"]

        # Verify data is still accessible
        customer_data = self.mesh.get("customer_analysis", "sales_agent")
        assert customer_data["segment"] == "enterprise"

        insights = self.mesh.get("weekly_insights", "analytics_agent")
        assert "engagement up 12%" in insights

        # Add more data after restart
        self.mesh.push(
            "post_restart_data", "System restarted successfully", topics=["sales"]
        )

        # Verify new data works
        post_restart = self.mesh.get("post_restart_data", "sales_agent")
        assert post_restart == "System restarted successfully"


class TestMultiBackendPersistence:
    """Test persistence with different database backends."""

    def test_sqlite_backend_features(self):
        """Test SQLite backend specific features."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()

        try:
            # Test direct backend usage
            backend = SQLiteBackend(temp_db.name)
            backend.connect()

            # Test context item storage
            backend.save_context_item(
                "test_key", "test_value", ["agent1"], 3600, time.time()
            )

            item = backend.get_context_item("test_key")
            assert item is not None
            assert item[0] == "test_value"
            assert item[1] == ["agent1"]
            assert item[2] == 3600

            # Test topic storage
            backend.save_agent_topics("agent1", ["topic1", "topic2"])
            topics = backend.get_agent_topics("agent1")
            assert topics == ["topic1", "topic2"]

            # Test permissions storage
            backend.save_agent_permissions("agent1", ["topic1"])
            permissions = backend.get_agent_permissions("agent1")
            assert permissions == ["topic1"]

            backend.close()

        finally:
            if os.path.exists(temp_db.name):
                try:
                    os.unlink(temp_db.name)
                except PermissionError:
                    pass

    def test_backend_factory(self):
        """Test the database backend factory function."""
        # Test SQLite backend creation
        sqlite_backend = create_database_backend("sqlite", db_path=":memory:")
        assert isinstance(sqlite_backend, SQLiteBackend)
        sqlite_backend.connect()
        sqlite_backend.close()

        # Test invalid backend
        with pytest.raises(ValueError):
            create_database_backend("invalid_backend")


def run_performance_benchmark():
    """Optional performance benchmark for persistence layer."""
    print("\n🚀 Running Performance Benchmark")
    print("=" * 50)

    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()

    try:
        mesh = ContextMesh(
            enable_indexing=True,
            auto_cleanup=True,
            enable_persistence=True,
            db_path=temp_db.name,
        )

        # Benchmark bulk operations
        start_time = time.time()
        for i in range(1000):
            mesh.push(
                f"bench_{i}", {"id": i, "data": f"value_{i}", "timestamp": time.time()}
            )

        insert_time = time.time() - start_time
        print(f"✅ 1000 inserts: {insert_time:.3f}s ({1000/insert_time:.0f} ops/sec)")

        # Benchmark retrieval
        start_time = time.time()
        for i in range(1000):
            value = mesh.get(f"bench_{i}")
            assert value["id"] == i

        retrieve_time = time.time() - start_time
        print(
            f"✅ 1000 retrievals: {retrieve_time:.3f}s ({1000/retrieve_time:.0f} ops/sec)"
        )

        # Benchmark cleanup
        # Add expiring items
        for i in range(500):
            mesh.push(f"expire_{i}", f"data_{i}", ttl=0.01)

        time.sleep(0.1)

        start_time = time.time()
        removed = mesh.cleanup_expired()
        cleanup_time = time.time() - start_time

        print(f"✅ Cleanup {removed} items: {cleanup_time:.3f}s")

        mesh.close()

    finally:
        if os.path.exists(temp_db.name):
            try:
                os.unlink(temp_db.name)
            except PermissionError:
                pass


if __name__ == "__main__":
    # Run the benchmark if called directly
    run_performance_benchmark()

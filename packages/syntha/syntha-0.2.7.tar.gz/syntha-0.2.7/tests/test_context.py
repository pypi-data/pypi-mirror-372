"""
Tests for Syntha ContextMesh functionality.
"""

import time

import pytest

from syntha.context import ContextItem, ContextMesh


class TestContextItem:
    """Test ContextItem class."""

    def test_context_item_creation(self):
        item = ContextItem("test_value", ["agent1"], 60)
        assert item.value == "test_value"
        assert item.subscribers == ["agent1"]
        assert item.ttl == 60
        assert not item.is_expired()

    def test_context_item_expiry(self):
        # Create item with very short TTL
        item = ContextItem("test_value", [], 0.1)
        time.sleep(0.2)
        assert item.is_expired()

    def test_context_item_access_control(self):
        # Global context (empty subscribers)
        global_item = ContextItem("global", [])
        assert global_item.is_accessible_by("any_agent")

        # Private context
        private_item = ContextItem("private", ["agent1", "agent2"])
        assert private_item.is_accessible_by("agent1")
        assert private_item.is_accessible_by("agent2")
        assert not private_item.is_accessible_by("agent3")


class TestContextMesh:
    """Test ContextMesh class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Use in-memory database for tests to ensure isolation
        import os
        import tempfile

        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.mesh = ContextMesh(db_path=self.temp_db.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        # Properly close the database connection first
        if hasattr(self, "mesh") and self.mesh.db_backend:
            self.mesh.db_backend.close()

        # Clean up the temporary database
        import os
        import time

        if hasattr(self, "temp_db") and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except PermissionError:
                # On Windows, sometimes need to wait a bit for the file to be released
                time.sleep(0.1)
                try:
                    os.unlink(self.temp_db.name)
                except PermissionError:
                    # If still locked, just skip cleanup - temp files will be cleaned up by OS
                    pass

    def test_push_and_get(self):
        """Test basic push and get functionality."""
        self.mesh.push("test_key", "test_value")
        assert self.mesh.get("test_key") == "test_value"

    def test_agent_specific_access(self):
        """Test agent-specific access control."""
        # Push context for specific agents
        self.mesh.push("private_key", "private_value", subscribers=["agent1"])

        # Agent1 can access
        assert self.mesh.get("private_key", "agent1") == "private_value"

        # Agent2 cannot access
        assert self.mesh.get("private_key", "agent2") is None

    def test_combined_routing(self):
        """Test combined routing with both topics and subscribers."""
        # Setup topic subscriptions
        self.mesh.register_agent_topics("topic_agent", ["sales"])
        self.mesh.register_agent_topics("another_topic_agent", ["sales"])

        # Push with both topics and subscribers
        self.mesh.push(
            "combined_key",
            "combined_value",
            topics=["sales"],
            subscribers=["direct_agent"],
        )

        # Topic subscribers should have access
        assert self.mesh.get("combined_key", "topic_agent") == "combined_value"
        assert self.mesh.get("combined_key", "another_topic_agent") == "combined_value"

        # Direct subscribers should have access
        assert self.mesh.get("combined_key", "direct_agent") == "combined_value"

        # Other agents should not have access
        assert self.mesh.get("combined_key", "other_agent") is None

    def test_combined_routing_no_overlap(self):
        """Test combined routing when there's no overlap between topics and subscribers."""
        # Setup topic subscriptions
        self.mesh.register_agent_topics("topic_agent", ["sales"])

        # Push with both topics and subscribers (no overlap)
        self.mesh.push(
            "combined_key",
            "combined_value",
            topics=["sales"],
            subscribers=["direct_agent"],
        )

        # Both should have access
        assert self.mesh.get("combined_key", "topic_agent") == "combined_value"
        assert self.mesh.get("combined_key", "direct_agent") == "combined_value"

        # Verify in get_all_for_agent
        topic_context = self.mesh.get_all_for_agent("topic_agent")
        direct_context = self.mesh.get_all_for_agent("direct_agent")

        assert "combined_key" in topic_context
        assert "combined_key" in direct_context

    def test_global_context(self):
        """Test global context access."""
        self.mesh.push("global_key", "global_value", subscribers=[])

        # Any agent can access global context
        assert self.mesh.get("global_key", "agent1") == "global_value"
        assert self.mesh.get("global_key", "agent2") == "global_value"

    def test_get_all_for_agent(self):
        """Test getting all context for an agent."""
        self.mesh.push("global", "global_value", subscribers=[])
        self.mesh.push("private", "private_value", subscribers=["agent1"])
        self.mesh.push("other", "other_value", subscribers=["agent2"])

        agent1_context = self.mesh.get_all_for_agent("agent1")
        assert "global" in agent1_context
        assert "private" in agent1_context
        assert "other" not in agent1_context

        agent2_context = self.mesh.get_all_for_agent("agent2")
        assert "global" in agent2_context
        assert "private" not in agent2_context
        assert "other" in agent2_context

    def test_ttl_functionality(self):
        """Test TTL (time-to-live) functionality."""
        # Push context with short TTL
        self.mesh.push("temp_key", "temp_value", ttl=0.1)

        # Should be accessible immediately
        assert self.mesh.get("temp_key") == "temp_value"

        # Wait for expiry
        time.sleep(0.2)

        # Should be None after expiry
        assert self.mesh.get("temp_key") is None

    def test_cleanup_expired(self):
        """Test cleanup of expired items."""
        # Add some items with short TTL
        self.mesh.push("temp1", "value1", ttl=0.1)
        self.mesh.push("temp2", "value2", ttl=0.1)
        self.mesh.push("permanent", "value3")  # No TTL

        assert self.mesh.size() == 3

        # Wait for expiry
        time.sleep(0.2)

        # Clean up expired items
        expired_count = self.mesh.cleanup_expired()
        assert expired_count == 2
        assert self.mesh.size() == 1
        assert self.mesh.get("permanent") == "value3"

    def test_remove(self):
        """Test removing context items."""
        self.mesh.push("test_key", "test_value")
        assert self.mesh.get("test_key") == "test_value"

        # Remove the item
        assert self.mesh.remove("test_key") is True
        assert self.mesh.get("test_key") is None

        # Try to remove non-existent item
        assert self.mesh.remove("non_existent") is False

    def test_clear(self):
        """Test clearing all context."""
        self.mesh.push("key1", "value1")
        self.mesh.push("key2", "value2")
        assert self.mesh.size() == 2

        self.mesh.clear()
        assert self.mesh.size() == 0

    def test_get_stats(self):
        """Test getting mesh statistics."""
        self.mesh.push("global", "value", subscribers=[])
        self.mesh.push("private", "value", subscribers=["agent1"])
        self.mesh.push("expired", "value", ttl=0.1)

        time.sleep(0.2)  # Let one item expire

        stats = self.mesh.get_stats()
        assert stats["total_items"] == 3
        assert stats["expired_items"] == 1
        assert stats["global_items"] == 1

    def test_get_keys_for_agent(self):
        """Test getting accessible keys for an agent."""
        self.mesh.push("global", "value", subscribers=[])
        self.mesh.push("private", "value", subscribers=["agent1"])
        self.mesh.push("other", "value", subscribers=["agent2"])

        keys = self.mesh.get_keys_for_agent("agent1")
        assert "global" in keys
        assert "private" in keys
        assert "other" not in keys

    def test_unsubscribe_from_topics(self):
        """Test unsubscribing agents from topics."""
        # Subscribe agent to multiple topics
        self.mesh.register_agent_topics("agent1", ["sales", "marketing", "support"])
        self.mesh.register_agent_topics("agent2", ["sales", "marketing"])

        # Verify initial subscriptions
        assert self.mesh.get_topics_for_agent("agent1") == [
            "sales",
            "marketing",
            "support",
        ]
        assert self.mesh.get_subscribers_for_topic("sales") == ["agent1", "agent2"]
        assert self.mesh.get_subscribers_for_topic("marketing") == ["agent1", "agent2"]
        assert self.mesh.get_subscribers_for_topic("support") == ["agent1"]

        # Unsubscribe agent1 from sales and marketing
        self.mesh.unsubscribe_from_topics("agent1", ["sales", "marketing"])

        # Verify agent1 only has support left
        assert self.mesh.get_topics_for_agent("agent1") == ["support"]

        # Verify topic subscribers are updated
        assert self.mesh.get_subscribers_for_topic("sales") == ["agent2"]
        assert self.mesh.get_subscribers_for_topic("marketing") == ["agent2"]
        assert self.mesh.get_subscribers_for_topic("support") == ["agent1"]

        # Unsubscribe agent1 from all remaining topics
        self.mesh.unsubscribe_from_topics("agent1", ["support"])

        # Verify agent1 has no topics left
        assert self.mesh.get_topics_for_agent("agent1") == []

        # Verify support topic is removed (no subscribers left)
        assert "support" not in self.mesh.get_all_topics()

        # Verify other topics still exist
        assert "sales" in self.mesh.get_all_topics()
        assert "marketing" in self.mesh.get_all_topics()

    def test_unsubscribe_from_nonexistent_topics(self):
        """Test unsubscribing from topics that don't exist or agent isn't subscribed to."""
        # Subscribe agent to some topics
        self.mesh.register_agent_topics("agent1", ["sales", "marketing"])

        # Try to unsubscribe from topics not subscribed to
        self.mesh.unsubscribe_from_topics("agent1", ["support", "analytics"])

        # Should still have original topics
        assert self.mesh.get_topics_for_agent("agent1") == ["sales", "marketing"]

        # Try to unsubscribe from mix of subscribed and non-subscribed topics
        self.mesh.unsubscribe_from_topics("agent1", ["sales", "support", "analytics"])

        # Should only have marketing left
        assert self.mesh.get_topics_for_agent("agent1") == ["marketing"]

    def test_delete_topic_with_context(self):
        """Test deleting a topic and its associated context."""
        # Set up agents and topics
        self.mesh.register_agent_topics("agent1", ["sales", "marketing"])
        self.mesh.register_agent_topics("agent2", ["sales", "support"])

        # Push context to different topics
        self.mesh.push("sales_data", "quarterly_report", topics=["sales"])
        self.mesh.push("marketing_data", "campaign_results", topics=["marketing"])
        self.mesh.push("mixed_data", "customer_info", topics=["sales", "marketing"])
        self.mesh.push("support_data", "ticket_stats", topics=["support"])

        # Verify context is accessible
        assert self.mesh.get("sales_data", "agent1") == "quarterly_report"
        assert self.mesh.get("marketing_data", "agent1") == "campaign_results"
        assert self.mesh.get("mixed_data", "agent1") == "customer_info"
        assert self.mesh.get("support_data", "agent2") == "ticket_stats"

        # Delete the sales topic
        deleted_items = self.mesh.delete_topic("sales")
        assert (
            deleted_items == 1
        )  # Only sales_data should be deleted (mixed_data still has marketing)

        # Verify sales_data is gone but others remain
        assert self.mesh.get("sales_data", "agent1") is None
        assert self.mesh.get("marketing_data", "agent1") == "campaign_results"
        assert (
            self.mesh.get("mixed_data", "agent1") == "customer_info"
        )  # Still has marketing topic
        assert self.mesh.get("support_data", "agent2") == "ticket_stats"

        # Verify topic is removed from agent subscriptions
        assert self.mesh.get_topics_for_agent("agent1") == ["marketing"]
        assert self.mesh.get_topics_for_agent("agent2") == ["support"]

        # Verify topic is removed from all topics
        assert "sales" not in self.mesh.get_all_topics()
        assert "marketing" in self.mesh.get_all_topics()
        assert "support" in self.mesh.get_all_topics()

    def test_delete_topic_mixed_context(self):
        """Test deleting a topic when context is associated with multiple topics."""
        # Set up agents and topics
        self.mesh.register_agent_topics("agent1", ["sales", "marketing", "analytics"])

        # Push context to multiple topics
        self.mesh.push(
            "multi_topic_data",
            "important_info",
            topics=["sales", "marketing", "analytics"],
        )

        # Verify context is accessible
        assert self.mesh.get("multi_topic_data", "agent1") == "important_info"

        # Delete one topic
        deleted_items = self.mesh.delete_topic("sales")
        assert (
            deleted_items == 0
        )  # No items should be deleted since context has other topics

        # Verify context is still accessible (still has marketing and analytics)
        assert self.mesh.get("multi_topic_data", "agent1") == "important_info"

        # Verify agent still has other topics
        assert self.mesh.get_topics_for_agent("agent1") == ["marketing", "analytics"]

        # Delete another topic
        deleted_items = self.mesh.delete_topic("marketing")
        assert deleted_items == 0  # Still has analytics topic

        # Delete the last topic
        deleted_items = self.mesh.delete_topic("analytics")
        assert deleted_items == 1  # Now the context should be deleted

        # Verify context is gone
        assert self.mesh.get("multi_topic_data", "agent1") is None

        # Verify agent has no topics left
        assert self.mesh.get_topics_for_agent("agent1") == []

    def test_delete_nonexistent_topic(self):
        """Test deleting a topic that doesn't exist."""
        # Set up some existing data first
        self.mesh.register_agent_topics("agent1", ["existing"])
        self.mesh.push("test", "value", topics=["existing"])

        # Try to delete a topic that doesn't exist
        deleted_items = self.mesh.delete_topic("nonexistent")
        assert deleted_items == 0

        # Verify no changes to existing data
        assert self.mesh.get("test", "agent1") == "value"
        assert self.mesh.get_topics_for_agent("agent1") == ["existing"]

        # Try again to make sure it's still safe
        deleted_items = self.mesh.delete_topic("nonexistent")
        assert deleted_items == 0
        assert self.mesh.get("test", "agent1") == "value"
        assert self.mesh.get_topics_for_agent("agent1") == ["existing"]

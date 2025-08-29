"""
Context Mesh - The heart of Syntha's shared knowledge system.

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

Stores context as key-value pairs with subscriber-based access control,
optional time-to-live (TTL) functionality, and persistent database storage.
"""

import copy
import time
from threading import Lock
from typing import Any, Dict, List, Optional

from .persistence import create_database_backend


class ContextItem:
    """Represents a single context item with value, subscribers, and TTL."""

    def __init__(
        self,
        value: Any,
        subscribers: Optional[List[str]] = None,
        ttl: Optional[float] = None,
    ):
        # Deep copy the value to prevent external modifications
        self.value = copy.deepcopy(value)
        # Copy the subscribers list to prevent external modifications
        self.subscribers = (subscribers or []).copy()
        self.created_at = time.time()
        self.ttl = ttl

    def is_expired(self) -> bool:
        """Check if this context item has expired."""
        if self.ttl is None:
            return False
        return time.time() > (self.created_at + self.ttl)

    def is_accessible_by(self, agent_name: str) -> bool:
        """Check if the given agent can access this context item."""
        if self.is_expired():
            return False

        # Special marker for topic-based context with no subscribers
        if self.subscribers == ["__NO_SUBSCRIBERS__"]:
            return False

        # Empty subscribers list means global context
        return len(self.subscribers) == 0 or agent_name in self.subscribers


class ContextMesh:
    """
    The core context sharing system for Syntha.

    Manages shared knowledge space where agents can push and retrieve context
    with subscriber-based access control, optional TTL, and persistent storage.

    Supports user isolation to ensure complete separation between different users.
    """

    def __init__(
        self,
        enable_indexing: bool = True,
        auto_cleanup: bool = True,
        enable_persistence: bool = True,
        db_backend: str = "sqlite",
        user_id: Optional[str] = None,
        **db_config,
    ):
        self._data: Dict[str, ContextItem] = {}
        self._lock = Lock()  # Thread safety for concurrent access

        # User isolation support
        self.user_id = user_id

        # Performance optimizations (controlled by simple flags)
        self.enable_indexing = enable_indexing
        self.auto_cleanup = auto_cleanup
        self.enable_persistence = enable_persistence

        # Agent-based indexes for faster lookups (only if indexing enabled)
        self._agent_index: Optional[Dict[str, List[str]]] = (
            {} if enable_indexing else None
        )
        self._global_keys: Optional[List[str]] = [] if enable_indexing else None

        # Topic-based routing system
        self._agent_topics: Dict[str, List[str]] = {}  # {agent_name: [topics]}
        self._topic_subscribers: Dict[str, List[str]] = {}  # {topic: [agent_names]}
        self._key_topics: Dict[str, List[str]] = (
            {}
        )  # {key: [topics]} - track which topics each key was pushed to

        # Topic posting permissions
        self._agent_post_permissions: Dict[str, List[str]] = (
            {}
        )  # {agent_name: [topics_can_post_to]}

        # Cleanup tracking
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes

        # Database persistence (initialize after all attributes)
        self.db_backend = None
        if enable_persistence:
            self.db_backend = create_database_backend(db_backend, **db_config)
            self.db_backend.connect()
            self._load_from_database()

    def _load_from_database(self) -> None:
        """Load existing data from database on startup with user isolation."""
        if not self.db_backend:
            return

        # Load context items (user-scoped if user_id is provided)
        if hasattr(self.db_backend, "get_all_context_items_for_user") and self.user_id:
            db_items = self.db_backend.get_all_context_items_for_user(self.user_id)
        else:
            db_items = self.db_backend.get_all_context_items()

        for key, (value, subscribers, ttl, created_at) in db_items.items():
            item = ContextItem(value, subscribers, ttl)
            item.created_at = created_at

            # Skip expired items
            if not item.is_expired():
                self._data[key] = item
                if self.enable_indexing:
                    self._add_to_index(key, subscribers)

        # Load agent topics (user-scoped if user_id is provided)
        if hasattr(self.db_backend, "get_all_agent_topics_for_user") and self.user_id:
            agent_topics = self.db_backend.get_all_agent_topics_for_user(self.user_id)
        else:
            agent_topics = self.db_backend.get_all_agent_topics()

        for agent_name, topics in agent_topics.items():
            self._agent_topics[agent_name] = topics
            # Rebuild topic subscribers mapping
            for topic in topics:
                if topic not in self._topic_subscribers:
                    self._topic_subscribers[topic] = []
                if agent_name not in self._topic_subscribers[topic]:
                    self._topic_subscribers[topic].append(agent_name)

        # Load agent permissions (user-scoped if user_id is provided)
        if (
            hasattr(self.db_backend, "get_all_agent_permissions_for_user")
            and self.user_id
        ):
            agent_permissions = self.db_backend.get_all_agent_permissions_for_user(
                self.user_id
            )
        else:
            agent_permissions = self.db_backend.get_all_agent_permissions()

        self._agent_post_permissions.update(agent_permissions)

    def close(self) -> None:
        """Close database connection and cleanup resources."""
        if self.db_backend:
            self.db_backend.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def push(
        self,
        key: str,
        value: Any,
        subscribers: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        ttl: Optional[float] = None,
    ) -> None:
        """
        Add or update context in the mesh with unified routing.

        ROUTING OPTIONS:

        1. **Topic-based routing** (RECOMMENDED for agent tools):
           - Use `topics=["sales", "analytics"]`
           - Automatically routes to agents subscribed to those topics
           - Best for: agent-to-agent communication, broadcasts, workflows

        2. **Direct agent targeting**:
           - Use `subscribers=["Agent1", "Agent2"]`
           - Routes to specific named agents only
           - Best for: private messages, specific coordination

        3. **Combined routing** (NEW):
           - Use both `subscribers` and `topics`
           - Routes to direct subscribers PLUS agents subscribed to topics
           - Best for: "notify sales team AND the manager"

        4. **Global context** (default):
           - Use neither topics nor subscribers (both None)
           - Accessible by all agents in the system
           - Best for: shared configuration, system-wide state

        Args:
            key: Unique identifier for the context (use descriptive names)
            value: The context data (can be any serializable type)
            subscribers: List of agent names for direct targeting
            topics: List of topics for broadcast routing
            ttl: Time-to-live in seconds. None means no expiration
        """

        with self._lock:
            # Collect all target agents
            target_agents = set()

            # Add direct subscribers
            if subscribers:
                target_agents.update(subscribers)

            # Add topic subscribers
            if topics:
                for topic in topics:
                    if topic in self._topic_subscribers:
                        target_agents.update(self._topic_subscribers[topic])

            # Use the combined list
            if target_agents:
                final_subscribers: Optional[List[str]] = list(target_agents)
            else:
                # If we have topics but no subscribers, use the special marker
                # This ensures topic-based context with no subscribers is not accessible
                final_subscribers = ["__NO_SUBSCRIBERS__"] if topics else None

            # Push with combined subscribers
            self._push_internal(key, value, final_subscribers, ttl)

            # Track topics if specified (for topic-based queries)
            if topics:
                self._key_topics[key] = topics.copy()

    def _push_internal(
        self,
        key: str,
        value: Any,
        subscribers: Optional[List[str]] = None,
        ttl: Optional[float] = None,
    ) -> None:
        """
        Internal push method that assumes lock is already held.
        """
        # Auto-cleanup if enabled and interval passed
        if (
            self.auto_cleanup
            and time.time() - self._last_cleanup > self._cleanup_interval
        ):
            self._cleanup_expired()

        # Remove old index entries if updating
        if key in self._data and self.enable_indexing:
            self._remove_from_index(key, self._data[key])

        # Store the context item
        item = ContextItem(value, subscribers, ttl)
        self._data[key] = item

        # Persist to database if enabled (with user isolation)
        if self.db_backend:
            if hasattr(self.db_backend, "save_context_item_for_user") and self.user_id:
                self.db_backend.save_context_item_for_user(
                    self.user_id, key, value, subscribers or [], ttl, item.created_at
                )
            else:
                self.db_backend.save_context_item(
                    key, value, subscribers or [], ttl, item.created_at
                )

        # Update indexes if enabled
        if self.enable_indexing:
            self._add_to_index(key, subscribers or [])

    def _push_to_topics_internal(
        self, key: str, value: Any, topics: List[str], ttl: Optional[float] = None
    ) -> None:
        """
        Internal method to push context to topics. Assumes lock is already held.

        Args:
            key: Context key
            value: Context value
            topics: List of topics to broadcast to
            ttl: Time to live in seconds
        """
        # Find all agents interested in any of these topics
        interested_agents = set()
        for topic in topics:
            if topic in self._topic_subscribers:
                interested_agents.update(self._topic_subscribers[topic])

        # Track which topics this key was pushed to
        self._key_topics[key] = topics.copy()

        # If no interested agents, use special marker to indicate this is topic-based
        # context with no subscribers (stored but not accessible by any agent)
        if not interested_agents:
            self._push_internal(key, value, subscribers=["__NO_SUBSCRIBERS__"], ttl=ttl)
        else:
            self._push_internal(
                key, value, subscribers=list(interested_agents), ttl=ttl
            )

    def get(self, key: str, agent_name: Optional[str] = None) -> Optional[Any]:
        """
        Retrieve a specific context item.

        Args:
            key: The context key to retrieve
            agent_name: Name of the requesting agent (for access control)

        Returns:
            The context value if accessible, None otherwise
        """
        with self._lock:
            item = self._data.get(key)
            if item is None:
                return None

            # If no agent specified, skip access control (for system use)
            if agent_name is None:
                return copy.deepcopy(item.value) if not item.is_expired() else None

            # Check if agent has access
            if item.is_accessible_by(agent_name):
                return copy.deepcopy(item.value)

            return None

    def get_all_for_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Retrieve all context items accessible by the specified agent.

        Args:
            agent_name: Name of the requesting agent

        Returns:
            Dictionary of {key: value} for all accessible context
        """
        with self._lock:
            # Auto-cleanup if enabled
            if (
                self.auto_cleanup
                and time.time() - self._last_cleanup > self._cleanup_interval
            ):
                self._cleanup_expired()

            # Use index for faster lookup if enabled
            if (
                self.enable_indexing
                and self._agent_index is not None
                and self._global_keys is not None
            ):
                result = {}

                # Get keys from agent index
                agent_keys = self._agent_index.get(agent_name, [])
                for key in agent_keys:
                    item = self._data.get(key)
                    if item and item.is_accessible_by(agent_name):
                        result[key] = copy.deepcopy(item.value)

                # Get global context keys
                for key in self._global_keys:
                    item = self._data.get(key)
                    if item and item.is_accessible_by(agent_name):
                        result[key] = copy.deepcopy(item.value)

                return result
            else:
                # Fallback to full scan
                result = {}
                for key, item in self._data.items():
                    if item.is_accessible_by(agent_name):
                        result[key] = copy.deepcopy(item.value)
                return result

    def get_keys_for_agent(self, agent_name: str) -> List[str]:
        """
        Get list of context keys accessible by the specified agent.

        Args:
            agent_name: Name of the requesting agent

        Returns:
            List of accessible context keys
        """
        with self._lock:
            return self._get_keys_for_agent_internal(agent_name)

    def _get_keys_for_agent_internal(self, agent_name: str) -> List[str]:
        """
        Internal method to get keys for agent, assumes lock is already held.
        """
        # Use index for faster lookup if enabled
        if (
            self.enable_indexing
            and self._agent_index is not None
            and self._global_keys is not None
        ):
            keys = []

            # Get keys from agent index
            agent_keys = self._agent_index.get(agent_name, [])
            for key in agent_keys:
                item = self._data.get(key)
                if item and item.is_accessible_by(agent_name):
                    keys.append(key)

            # Get global context keys
            for key in self._global_keys:
                item = self._data.get(key)
                if item and item.is_accessible_by(agent_name):
                    keys.append(key)

            return keys
        else:
            # Fallback to full scan
            return [
                key
                for key, item in self._data.items()
                if item.is_accessible_by(agent_name)
            ]

    def remove(self, key: str) -> bool:
        """
        Remove a context item from the mesh.

        Args:
            key: The context key to remove

        Returns:
            True if item was removed, False if it didn't exist
        """
        with self._lock:
            item = self._data.pop(key, None)
            if item is None:
                return False

        # Remove from database if enabled (with user isolation)
        if self.db_backend:
            if (
                hasattr(self.db_backend, "delete_context_item_for_user")
                and self.user_id
            ):
                self.db_backend.delete_context_item_for_user(self.user_id, key)
            else:
                self.db_backend.delete_context_item(key)

            # Remove from indexes
            if self.enable_indexing:
                self._remove_from_index(key, item)

            return True
        else:
            # Remove from indexes if indexing is enabled
            if self.enable_indexing:
                self._remove_from_index(key, item)
            return True

    def cleanup_expired(self) -> int:
        """
        Remove all expired context items.

        Returns:
            Number of items removed
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, item in self._data.items() if item.is_expired()
            ]

            # Remove from memory
            for key in expired_keys:
                item = self._data.pop(key)
                if self.enable_indexing:
                    self._remove_from_index(key, item)

            # Remove from database if enabled
            if self.db_backend:
                db_removed = self.db_backend.cleanup_expired(current_time)
                # Database might have found more expired items than memory
                return max(len(expired_keys), db_removed)

            return len(expired_keys)

    def clear(self) -> None:
        """Remove all context items from the mesh."""
        with self._lock:
            self._data.clear()

            # Clear indexes
            if (
                self.enable_indexing
                and self._agent_index is not None
                and self._global_keys is not None
            ):
                self._agent_index.clear()
                self._global_keys.clear()

            # Clear topic mappings
            self._agent_topics.clear()
            self._topic_subscribers.clear()
            self._key_topics.clear()
            self._agent_post_permissions.clear()

            # Clear database if enabled (with user isolation)
        if self.db_backend:
            if hasattr(self.db_backend, "clear_all_for_user") and self.user_id:
                self.db_backend.clear_all_for_user(self.user_id)
            else:
                self.db_backend.clear_all()

    def size(self) -> int:
        """Get the total number of context items."""
        with self._lock:
            return len(self._data)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the context mesh.

        Returns:
            Dictionary with mesh statistics
        """
        with self._lock:
            total_items = len(self._data)
            expired_items = sum(1 for item in self._data.values() if item.is_expired())
            global_items = sum(
                1
                for item in self._data.values()
                if len(item.subscribers) == 0 and not item.is_expired()
            )
            active_items = total_items - expired_items

            return {
                "total_items": total_items,
                "active_items": active_items,
                "expired_items": expired_items,
                "global_items": global_items,
                "private_items": active_items - global_items,
                "total_topics": len(self._topic_subscribers),
                "agents_with_topics": len(self._agent_topics),
            }

    def register_agent_topics(self, agent_name: str, topics: List[str]) -> None:
        """
        Register what topics an agent is interested in.

        Args:
            agent_name: Name of the agent
            topics: List of topics the agent wants to receive context for
        """
        with self._lock:
            self._agent_topics[agent_name] = topics.copy()

            # Update reverse mapping (always needed)
            for topic in topics:
                if topic not in self._topic_subscribers:
                    self._topic_subscribers[topic] = []
                if agent_name not in self._topic_subscribers[topic]:
                    self._topic_subscribers[topic].append(agent_name)

        # Persist to database if enabled (with user isolation)
        if self.db_backend:
            if hasattr(self.db_backend, "save_agent_topics_for_user") and self.user_id:
                self.db_backend.save_agent_topics_for_user(
                    self.user_id, agent_name, topics
                )
            else:
                self.db_backend.save_agent_topics(agent_name, topics)

    def get_topics_for_agent(self, agent_name: str) -> List[str]:
        """Get all topics an agent is subscribed to."""
        with self._lock:
            return self._agent_topics.get(agent_name, []).copy()

    def get_subscribers_for_topic(self, topic: str) -> List[str]:
        """Get all agents subscribed to a specific topic."""
        with self._lock:
            return self._topic_subscribers.get(topic, []).copy()

    def get_all_topics(self) -> List[str]:
        """Get all available topics."""
        with self._lock:
            return list(self._topic_subscribers.keys())

    def unsubscribe_from_topics(self, agent_name: str, topics: List[str]) -> None:
        """
        Unsubscribe an agent from specific topics.

        Args:
            agent_name: Name of the agent to unsubscribe
            topics: List of topics to unsubscribe from
        """
        with self._lock:
            # Get current topics for the agent
            current_topics = self._agent_topics.get(agent_name, [])

            # Remove specified topics from agent's subscriptions
            updated_topics = [t for t in current_topics if t not in topics]

            # Update agent topics
            if updated_topics:
                self._agent_topics[agent_name] = updated_topics
            else:
                # If no topics left, remove agent entirely
                self._agent_topics.pop(agent_name, None)

            # Update reverse mapping (topic -> agents)
            for topic in topics:
                if topic in self._topic_subscribers:
                    if agent_name in self._topic_subscribers[topic]:
                        self._topic_subscribers[topic].remove(agent_name)
                    # If no agents left subscribed to this topic, remove it
                    if not self._topic_subscribers[topic]:
                        del self._topic_subscribers[topic]

            # Persist changes to database if enabled (with user isolation)
            if self.db_backend:
                if updated_topics:
                    if (
                        hasattr(self.db_backend, "save_agent_topics_for_user")
                        and self.user_id
                    ):
                        self.db_backend.save_agent_topics_for_user(
                            self.user_id, agent_name, updated_topics
                        )
                    else:
                        self.db_backend.save_agent_topics(agent_name, updated_topics)
                else:
                    # Remove agent from database if no topics left
                    if (
                        hasattr(self.db_backend, "remove_agent_topics_for_user")
                        and self.user_id
                    ):
                        self.db_backend.remove_agent_topics_for_user(
                            self.user_id, agent_name
                        )
                    else:
                        self.db_backend.remove_agent_topics(agent_name)

    def delete_topic(self, topic: str) -> int:
        """
        Delete a topic and all associated context.

        This will:
        1. Remove the topic from all agent subscriptions
        2. Delete all context items that were pushed to this topic
        3. Clean up database records

        Args:
            topic: Name of the topic to delete

        Returns:
            Number of context items deleted
        """
        with self._lock:
            context_items_deleted = 0

            # Find all context items pushed to this topic
            keys_to_delete = []
            for key, key_topics in self._key_topics.items():
                if topic in key_topics:
                    # If this context was only pushed to this topic, delete it entirely
                    if len(key_topics) == 1:
                        keys_to_delete.append(key)
                    else:
                        # Otherwise, just remove this topic from the key's topics
                        key_topics.remove(topic)

            # Delete context items that were only for this topic
            for key in keys_to_delete:
                if key in self._data:
                    item = self._data.pop(key)
                    if self.enable_indexing:
                        self._remove_from_index(key, item)
                    context_items_deleted += 1

                # Remove from key_topics mapping
                self._key_topics.pop(key, None)

            # Remove topic from all agent subscriptions
            agents_to_update = []
            agents_to_remove = []
            for agent_name, agent_topics in self._agent_topics.items():
                if topic in agent_topics:
                    agent_topics.remove(topic)
                    agents_to_update.append(agent_name)
                    # If agent has no topics left, mark for removal
                    if not agent_topics:
                        agents_to_remove.append(agent_name)

            # Remove agents that have no topics left
            for agent_name in agents_to_remove:
                self._agent_topics.pop(agent_name, None)

            # Remove topic from topic_subscribers mapping
            self._topic_subscribers.pop(topic, None)

            # Persist changes to database if enabled (with user isolation)
            if self.db_backend:
                # Delete context items from database
                for key in keys_to_delete:
                    if (
                        hasattr(self.db_backend, "delete_context_item_for_user")
                        and self.user_id
                    ):
                        self.db_backend.delete_context_item_for_user(self.user_id, key)
                    else:
                        self.db_backend.delete_context_item(key)

                # Update agent topics in database
                for agent_name in agents_to_update:
                    if agent_name in self._agent_topics:
                        if (
                            hasattr(self.db_backend, "save_agent_topics_for_user")
                            and self.user_id
                        ):
                            self.db_backend.save_agent_topics_for_user(
                                self.user_id, agent_name, self._agent_topics[agent_name]
                            )
                        else:
                            self.db_backend.save_agent_topics(
                                agent_name, self._agent_topics[agent_name]
                            )
                    else:
                        # Agent has no topics left, remove from database
                        if (
                            hasattr(self.db_backend, "remove_agent_topics_for_user")
                            and self.user_id
                        ):
                            self.db_backend.remove_agent_topics_for_user(
                                self.user_id, agent_name
                            )
                        else:
                            self.db_backend.remove_agent_topics(agent_name)

                # Clean up topic-specific data if backend supports it
                if (
                    hasattr(self.db_backend, "delete_topic_data_for_user")
                    and self.user_id
                ):
                    self.db_backend.delete_topic_data_for_user(self.user_id, topic)
                elif hasattr(self.db_backend, "delete_topic_data"):
                    self.db_backend.delete_topic_data(topic)

            return context_items_deleted

    def get_available_keys_by_topic(self, agent_name: str) -> Dict[str, List[str]]:
        """
        Get all available context keys organized by topic for an agent.

        Args:
            agent_name: Name of the requesting agent

        Returns:
            Dictionary mapping topic names to lists of available keys
        """
        with self._lock:
            agent_topics = self._agent_topics.get(agent_name, [])
            result: Dict[str, List[str]] = {}

            # Initialize all subscribed topics
            for topic in agent_topics:
                result[topic] = []

            # Find keys that were pushed to each topic and are accessible to this agent
            for key, key_topics in self._key_topics.items():
                item = self._data.get(key)
                if item and item.is_accessible_by(agent_name):
                    # Add this key to all relevant topics the agent is subscribed to
                    for topic in key_topics:
                        if (
                            topic in result
                        ):  # Only include topics the agent is subscribed to
                            result[topic].append(key)

            # Also include any other accessible keys in a special "other" category
            all_accessible_keys = self._get_keys_for_agent_internal(agent_name)
            keys_in_topics = set()
            for topic_keys in result.values():
                keys_in_topics.update(topic_keys)

            other_keys = [
                key for key in all_accessible_keys if key not in keys_in_topics
            ]
            if other_keys:
                result["other"] = other_keys

            return result

    def _add_to_index(self, key: str, subscribers: List[str]) -> None:
        """Add key to appropriate indexes."""
        if (
            not self.enable_indexing
            or self._agent_index is None
            or self._global_keys is None
        ):
            return

        if len(subscribers) == 0:
            # Global context
            if key not in self._global_keys:
                self._global_keys.append(key)
        else:
            # Agent-specific context
            for agent in subscribers:
                if agent not in self._agent_index:
                    self._agent_index[agent] = []
                if key not in self._agent_index[agent]:
                    self._agent_index[agent].append(key)

    def _remove_from_index(self, key: str, item: ContextItem) -> None:
        """Remove key from all indexes."""
        if (
            not self.enable_indexing
            or self._agent_index is None
            or self._global_keys is None
        ):
            return

        # Remove from global keys
        if key in self._global_keys:
            self._global_keys.remove(key)

        # Remove from agent indexes
        for agent, keys in self._agent_index.items():
            if key in keys:
                keys.remove(key)

    def _cleanup_expired(self) -> None:
        """Internal method to clean up expired items."""
        current_time = time.time()
        expired_keys = []

        for key, item in self._data.items():
            if item.is_expired():
                expired_keys.append(key)

        for key in expired_keys:
            item = self._data.pop(key)
            if self.enable_indexing:
                self._remove_from_index(key, item)

        # Clean up database if enabled (with user isolation)
        if self.db_backend:
            if hasattr(self.db_backend, "cleanup_expired_for_user") and self.user_id:
                self.db_backend.cleanup_expired_for_user(self.user_id, current_time)
            else:
                self.db_backend.cleanup_expired(current_time)

        self._last_cleanup = current_time

    def set_agent_post_permissions(
        self, agent_name: str, allowed_topics: List[str]
    ) -> None:
        """
        Set which topics an agent is allowed to post to.

        Args:
            agent_name: Name of the agent
            allowed_topics: List of topics the agent can post to
        """
        with self._lock:
            self._agent_post_permissions[agent_name] = list(allowed_topics)

            # Persist to database if enabled (with user isolation)
            if self.db_backend:
                if (
                    hasattr(self.db_backend, "save_agent_permissions_for_user")
                    and self.user_id
                ):
                    self.db_backend.save_agent_permissions_for_user(
                        self.user_id, agent_name, allowed_topics
                    )
                else:
                    self.db_backend.save_agent_permissions(agent_name, allowed_topics)

    def get_agent_post_permissions(self, agent_name: str) -> List[str]:
        """
        Get which topics an agent is allowed to post to.

        Args:
            agent_name: Name of the agent

        Returns:
            List of topics the agent can post to
        """
        return self._agent_post_permissions.get(agent_name, [])

    def can_agent_post_to_topic(self, agent_name: str, topic: str) -> bool:
        """
        Check if an agent is allowed to post to a specific topic.

        Args:
            agent_name: Name of the agent
            topic: Topic to check

        Returns:
            True if agent can post to topic, False otherwise
        """
        allowed_topics = self._agent_post_permissions.get(agent_name, [])
        return (
            topic in allowed_topics or len(allowed_topics) == 0
        )  # Empty list means can post to any topic

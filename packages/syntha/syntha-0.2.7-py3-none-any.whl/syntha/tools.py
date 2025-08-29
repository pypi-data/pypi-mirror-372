"""
Syntha Agent Tools - Essential Context Management

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

Provides OpenAI-compatible function call schemas and handlers for agents
to manage and share context through topic-based routing.

Core Tools:
- get_context: Retrieve shared context data
- push_context: Share context with topic subscribers
- list_context: Discover available context keys
- subscribe_to_topics: Subscribe to topic-based context routing
- discover_topics: Find available topics and subscriber counts
"""

import json
from typing import Any, Dict, List, Optional

from .context import ContextMesh


def get_context_tool_schema() -> Dict[str, Any]:
    """
    Get the OpenAI function call schema for context retrieval.

    This schema can be used with OpenAI, Anthropic, or any other LLM
    that supports function calling.

    Returns:
        Function schema dictionary compatible with OpenAI API
    """
    return {
        "name": "get_context",
        "description": """Retrieve specific context from the shared knowledge base.
        
        💡 TIP: Use 'list_context' first to see what's available!
        
        You don't need to specify your agent name - the system knows who you are.""",
        "parameters": {
            "type": "object",
            "properties": {
                "keys": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific context keys to retrieve. Must be a list of strings. Use list_context to see available options.",
                }
            },
            "required": [],
        },
    }


def handle_get_context_call(
    context_mesh: ContextMesh, agent_name: str, keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Handle a get_context function call from an agent.

    Args:
        context_mesh: The ContextMesh instance to query
        agent_name: Name of the requesting agent (auto-injected by ToolHandler)
        keys: Optional list of specific keys to retrieve

    Returns:
        Dictionary with context data and metadata
    """
    try:
        if keys:
            # Retrieve specific keys
            result = {}
            for key in keys:
                value = context_mesh.get(key, agent_name)
                if value is not None:
                    result[key] = value
        else:
            # Retrieve all accessible context
            result = context_mesh.get_all_for_agent(agent_name)

        return {
            "success": True,
            "context": result,
            "agent_name": agent_name,
            "keys_requested": keys or list(result.keys()),
            "keys_found": list(result.keys()),
            "message": f"Retrieved {len(result)} context items",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent_name": agent_name,
            "keys_requested": keys,
            "context": {},
        }


def get_push_context_tool_schema() -> Dict[str, Any]:
    """
    Get the function schema for pushing context to topics.

    This allows agents to share context with other agents via topic-based routing.

    Returns:
        Function schema dictionary for pushing context to topics
    """
    return {
        "name": "push_context",
        "description": """Share context with other agents through flexible routing options.
        
        🎯 ROUTING OPTIONS (choose one or combine):
        
        1. **Topic Broadcasting** (RECOMMENDED):
           - Use 'topics' parameter: ["sales", "support"]
           - Routes to agents subscribed to those topics
           - Best for: workflows, broadcasts, team coordination
        
        2. **Direct Agent Targeting**:
           - Use 'subscribers' parameter: ["Agent1", "Agent2"]
           - Routes only to those specific agents
           - Best for: private messages, specific coordination
        
        3. **Combined Routing** (NEW):
           - Use both 'topics' and 'subscribers'
           - Routes to topic subscribers PLUS direct subscribers
           - Best for: "notify sales team AND the manager"
        
        💡 TIP: Use 'discover_topics' first to see what topics exist and have subscribers!
        
        You don't need to specify your agent name - the system knows who you are.""",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Unique identifier for this context",
                },
                "value": {"type": "string", "description": "The context data to share"},
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Topics to broadcast to. Must be a list of strings (not a comma-separated string). Example: ['sales', 'marketing', 'support']",
                },
                "subscribers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific agent names to send this context to. Must be a list of strings. Example: ['ManagerAgent', 'AdminAgent']",
                },
                "ttl_hours": {
                    "type": "number",
                    "description": "How long context should remain available (hours). Default: 24 hours",
                },
            },
            "required": ["key", "value"],
        },
    }


def handle_push_context_call(
    context_mesh: ContextMesh,
    key: str,
    value: str,
    topics: Optional[List[str]] = None,
    subscribers: Optional[List[str]] = None,
    ttl_hours: float = 24.0,
    sender_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Handle a push_context function call from an agent.

    Args:
        context_mesh: The ContextMesh instance to update
        key: Context key to set
        value: Context value (will attempt JSON parsing)
        topics: List of topics to broadcast to (optional)
        subscribers: List of specific agents to target (optional)
        ttl_hours: Time-to-live in hours
        sender_agent: Agent sending the context (auto-injected by ToolHandler)

    Returns:
        Dictionary with operation status
    """
    try:
        # Try to parse value as JSON, fall back to string
        try:
            parsed_value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            parsed_value = value

        ttl_seconds = ttl_hours * 3600 if ttl_hours > 0 else None

        # Strict parameter validation per schema
        if topics is not None:
            if not isinstance(topics, list) or not all(
                isinstance(t, str) for t in topics
            ):
                return {
                    "success": False,
                    "error": "Invalid parameter: 'topics' must be a list of strings",
                    "topics": topics,
                }
        if subscribers is not None:
            if not isinstance(subscribers, list) or not all(
                isinstance(s, str) for s in subscribers
            ):
                return {
                    "success": False,
                    "error": "Invalid parameter: 'subscribers' must be a list of strings",
                    "subscribers": subscribers,
                }

        # Use the unified push API with both topics and subscribers
        context_mesh.push(
            key=key,
            value=parsed_value,
            topics=topics,
            subscribers=subscribers,
            ttl=ttl_seconds,
        )

        # Build response message
        message_parts = []
        if topics:
            message_parts.append(f"topics: {', '.join(topics)}")
        if subscribers:
            message_parts.append(f"subscribers: {', '.join(subscribers)}")

        message = f"Context '{key}' shared with " + " and ".join(message_parts)

        return {
            "success": True,
            "message": message,
            "key": key,
            "value": parsed_value,
            "topics": topics,
            "subscribers": subscribers,
            "ttl_hours": ttl_hours,
            "sender_agent": sender_agent,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "key": key,
            "topics": topics,
            "subscribers": subscribers,
        }


def get_list_context_tool_schema() -> Dict[str, Any]:
    """
    Get the function schema for listing available context keys.

    Returns:
        Function schema dictionary for listing context keys
    """
    return {
        "name": "list_context",
        "description": """List all context keys you have access to, organized by topic. 
        
        ⚠️ IMPORTANT: Use this tool FIRST before trying to retrieve context!
        This shows you what context is available so you can decide which keys to retrieve.
        
        You don't need to specify your agent name - the system knows who you are.""",
        "parameters": {"type": "object", "properties": {}, "required": []},
    }


def handle_list_context_call(
    context_mesh: ContextMesh, agent_name: str
) -> Dict[str, Any]:
    """
    Handle a list_context_keys function call from an agent.

    Args:
        context_mesh: The ContextMesh instance to query
        agent_name: Name of the requesting agent (auto-injected by ToolHandler)

    Returns:
        Dictionary with available keys organized by topic
    """
    try:
        # Get keys organized by topic
        keys_by_topic = context_mesh.get_available_keys_by_topic(agent_name)

        # Also get all accessible keys (for backward compatibility)
        all_keys = context_mesh.get_keys_for_agent(agent_name)

        return {
            "success": True,
            "keys_by_topic": keys_by_topic,
            "all_accessible_keys": all_keys,
            "topics_subscribed": context_mesh.get_topics_for_agent(agent_name),
            "message": "Use these keys with get_context tool. Keys are organized by topics you're subscribed to.",
            "agent_name": agent_name,
            "total_keys": len(all_keys),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent_name": agent_name,
            "keys_by_topic": {},
            "all_accessible_keys": [],
        }


def get_subscribe_to_topics_tool_schema() -> Dict[str, Any]:
    """
    Get the function schema for registering topic interests.

    This allows agents to subscribe to specific topics to receive relevant context.

    Returns:
        Function schema dictionary for topic registration
    """
    return {
        "name": "subscribe_to_topics",
        "description": """Subscribe to specific topics to receive relevant context.
        
        After subscribing, you'll automatically receive context that other agents push to these topics.
        
        You don't need to specify your agent name - the system knows who you are.""",
        "parameters": {
            "type": "object",
            "properties": {
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Topics you want to receive context for. Must be a list of strings. Example: ['sales', 'customer_data', 'pricing']",
                }
            },
            "required": ["topics"],
        },
    }


def handle_subscribe_to_topics_call(
    context_mesh: ContextMesh, topics: List[str], agent_name: str
) -> Dict[str, Any]:
    """
    Handle a register_for_topics function call from an agent.

    Args:
        context_mesh: The ContextMesh instance to update
        topics: List of topics the agent wants to subscribe to
        agent_name: Agent name (auto-injected by ToolHandler)

    Returns:
        Dictionary with registration result
    """
    try:
        context_mesh.register_agent_topics(agent_name, topics)
        return {
            "success": True,
            "agent": agent_name,
            "topics": topics,
            "message": f"Successfully registered for topics: {', '.join(topics)}. You'll now receive context shared to these topics.",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent": agent_name,
            "topics": topics,
        }


def get_discover_topics_tool_schema() -> Dict[str, Any]:
    """
    Get the function schema for discovering available topics.

    This helps agents understand what topics exist and how many subscribers they have,
    making it easier to choose appropriate topics for pushing context.

    Returns:
        Function schema dictionary for topic discovery
    """
    return {
        "name": "discover_topics",
        "description": """Discover available topics in the system and see subscriber counts.
        
        🎯 Use this BEFORE pushing context to understand:
        - What topics exist in the system
        - How many agents are subscribed to each topic
        - Popular topics vs niche ones
        
        This helps you choose the right topics for your context.""",
        "parameters": {
            "type": "object",
            "properties": {
                "include_subscriber_names": {
                    "type": "boolean",
                    "description": "Whether to include names of subscribers for each topic (default: false)",
                }
            },
            "required": [],
        },
    }


def handle_discover_topics_call(
    context_mesh: ContextMesh, include_subscriber_names: bool = False
) -> Dict[str, Any]:
    """
    Handle a discover_topics function call from an agent.

    Args:
        context_mesh: The ContextMesh instance to query
        include_subscriber_names: Whether to include subscriber names

    Returns:
        Dictionary with available topics and their subscriber information
    """
    try:
        # Get all topics by examining the topic subscribers mapping
        all_topics = {}

        # Access the internal topic mapping if available
        if hasattr(context_mesh, "_topic_subscribers"):
            for topic, agents in context_mesh._topic_subscribers.items():
                subscriber_count = len(agents)
                topic_info: Dict[str, Any] = {
                    "subscriber_count": subscriber_count,
                    "is_active": subscriber_count > 0,
                }

                if include_subscriber_names:
                    topic_info["subscribers"] = list(agents)

                all_topics[topic] = topic_info

        # Sort topics by subscriber count (most popular first)
        sorted_topics = dict(
            sorted(
                all_topics.items(), key=lambda x: x[1]["subscriber_count"], reverse=True
            )
        )

        # Generate suggestions
        popular_topics = [
            topic
            for topic, info in sorted_topics.items()
            if info["subscriber_count"] >= 2
        ]

        return {
            "success": True,
            "topics": sorted_topics,
            "total_topics": len(all_topics),
            "popular_topics": popular_topics,
            "suggestions": {
                "for_broad_reach": popular_topics[:3] if popular_topics else [],
                "common_patterns": [
                    "sales",
                    "marketing",
                    "support",
                    "product",
                    "analytics",
                    "customer_data",
                ],
            },
            "message": f"Found {len(all_topics)} topics. Popular topics (2+ subscribers): {', '.join(popular_topics[:5])}",
        }

    except Exception as e:
        return {"success": False, "error": str(e), "topics": {}, "total_topics": 0}


def get_unsubscribe_from_topics_tool_schema() -> Dict[str, Any]:
    """
    Get the function schema for unsubscribing from topics.

    This allows agents to unsubscribe from specific topics they no longer want to receive context for.

    Returns:
        Function schema dictionary for topic unsubscription
    """
    return {
        "name": "unsubscribe_from_topics",
        "description": """Unsubscribe from specific topics to stop receiving context from them.
        
        This will remove you from the specified topics while keeping your other topic subscriptions intact.
        
        You don't need to specify your agent name - the system knows who you are.""",
        "parameters": {
            "type": "object",
            "properties": {
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Topics you want to unsubscribe from. Must be a list of strings. Example: ['sales', 'old_projects']",
                }
            },
            "required": ["topics"],
        },
    }


def handle_unsubscribe_from_topics_call(
    context_mesh: ContextMesh, topics: List[str], agent_name: str
) -> Dict[str, Any]:
    """
    Handle an unsubscribe_from_topics function call from an agent.

    Args:
        context_mesh: The ContextMesh instance to update
        topics: List of topics the agent wants to unsubscribe from
        agent_name: Agent name (auto-injected by ToolHandler)

    Returns:
        Dictionary with unsubscription result
    """
    try:
        # Get current subscriptions
        current_topics = context_mesh.get_topics_for_agent(agent_name)

        # Filter out topics that the agent wasn't subscribed to
        topics_to_unsubscribe = [t for t in topics if t in current_topics]
        topics_not_subscribed = [t for t in topics if t not in current_topics]

        if not topics_to_unsubscribe:
            return {
                "success": True,
                "agent": agent_name,
                "topics_unsubscribed": [],
                "topics_not_subscribed": topics_not_subscribed,
                "remaining_topics": current_topics,
                "message": f"You weren't subscribed to any of these topics: {', '.join(topics)}",
            }

        # Unsubscribe from topics
        context_mesh.unsubscribe_from_topics(agent_name, topics_to_unsubscribe)

        # Get remaining topics
        remaining_topics = context_mesh.get_topics_for_agent(agent_name)

        return {
            "success": True,
            "agent": agent_name,
            "topics_unsubscribed": topics_to_unsubscribe,
            "topics_not_subscribed": topics_not_subscribed,
            "remaining_topics": remaining_topics,
            "message": f"Successfully unsubscribed from: {', '.join(topics_to_unsubscribe)}. Remaining subscriptions: {', '.join(remaining_topics) if remaining_topics else 'none'}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent": agent_name,
            "topics": topics,
        }


def get_delete_topic_tool_schema() -> Dict[str, Any]:
    """
    Get the function schema for deleting topics.

    This allows agents to delete entire topics and all associated context.
    This is a destructive operation that should be used carefully.

    Returns:
        Function schema dictionary for topic deletion
    """
    return {
        "name": "delete_topic",
        "description": """Delete an entire topic and all its associated context.
        
        ⚠️ WARNING: This is a destructive operation that will:
        - Remove the topic from all agent subscriptions
        - Delete all context items that were only pushed to this topic
        - Cannot be undone
        
        Use with caution! Consider checking topic subscribers first with discover_topics.""",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Name of the topic to delete",
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Confirmation that you want to delete this topic (must be true)",
                },
            },
            "required": ["topic", "confirm"],
        },
    }


def handle_delete_topic_call(
    context_mesh: ContextMesh, topic: str, confirm: bool = False
) -> Dict[str, Any]:
    """
    Handle a delete_topic function call from an agent.

    Args:
        context_mesh: The ContextMesh instance to update
        topic: Name of the topic to delete
        confirm: Confirmation flag (must be True)

    Returns:
        Dictionary with deletion result
    """
    try:
        if not confirm:
            return {
                "success": False,
                "error": "Deletion not confirmed. Set confirm=true to proceed.",
                "topic": topic,
                "message": "Topic deletion requires explicit confirmation.",
            }

        # Check if topic exists
        if topic not in context_mesh.get_all_topics():
            return {
                "success": False,
                "error": f"Topic '{topic}' does not exist",
                "topic": topic,
                "available_topics": context_mesh.get_all_topics(),
                "message": f"Cannot delete non-existent topic '{topic}'",
            }

        # Get subscribers before deletion for reporting
        subscribers = context_mesh.get_subscribers_for_topic(topic)

        # Delete the topic
        context_items_deleted = context_mesh.delete_topic(topic)

        return {
            "success": True,
            "topic": topic,
            "subscribers_affected": subscribers,
            "context_items_deleted": context_items_deleted,
            "message": f"Successfully deleted topic '{topic}'. Removed {len(subscribers)} subscribers and {context_items_deleted} context items.",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "topic": topic,
        }


def get_all_tool_schemas() -> List[Dict[str, Any]]:
    """
    Get all essential tool schemas for Syntha context operations.

    Returns:
        List of core function schemas for topic-based context management
    """
    return [
        get_context_tool_schema(),
        get_push_context_tool_schema(),
        get_list_context_tool_schema(),
        get_subscribe_to_topics_tool_schema(),
        get_discover_topics_tool_schema(),
        get_unsubscribe_from_topics_tool_schema(),
        get_delete_topic_tool_schema(),
    ]


class ToolHandler:
    """
    Handler for Syntha context management tools with automatic agent identification and access control.

    Provides a unified interface for processing function calls from LLM frameworks
    and automatically injects agent context with configurable tool access control.
    """

    def __init__(
        self,
        context_mesh: ContextMesh,
        agent_name: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
        denied_tools: Optional[List[str]] = None,
        role_based_access: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Initialize the tool handler with optional access control.

        Args:
            context_mesh: The shared context mesh instance
            agent_name: Agent name for automatic injection
            allowed_tools: List of tool names this agent can access (if None, all tools allowed)
            denied_tools: List of tool names this agent cannot access (takes precedence over allowed_tools)
            role_based_access: Dict mapping roles to allowed tools (e.g., {"admin": ["delete_topic"], "user": ["get_context"]})

        Examples:
            # Allow all tools (default)
            handler = ToolHandler(mesh, "agent1")

            # Only allow read operations
            handler = ToolHandler(mesh, "agent1", allowed_tools=["get_context", "list_context"])

            # Allow all except dangerous operations
            handler = ToolHandler(mesh, "agent1", denied_tools=["delete_topic"])

            # Role-based access
            roles = {
                "reader": ["get_context", "list_context", "discover_topics"],
                "contributor": ["get_context", "push_context", "subscribe_to_topics"],
                "admin": ["delete_topic"]
            }
            handler = ToolHandler(mesh, "agent1", role_based_access=roles)
        """
        self.context_mesh = context_mesh
        self.agent_name = agent_name
        self.allowed_tools = set(allowed_tools) if allowed_tools is not None else None
        self.denied_tools = set(denied_tools) if denied_tools else set()
        self.role_based_access = role_based_access or {}
        self.agent_role: Optional[str] = None  # Can be set later with set_agent_role()

        # All available handlers
        self.all_handlers = {
            "get_context": self.handle_get_context,
            "push_context": self.handle_push_context,
            "list_context": self.handle_list_context,
            "subscribe_to_topics": self.handle_subscribe_to_topics,
            "discover_topics": self.handle_discover_topics,
            "unsubscribe_from_topics": self.handle_unsubscribe_from_topics,
            "delete_topic": self.handle_delete_topic,
        }

        # Filtered handlers based on access control
        self.handlers = self._filter_handlers()

    def _filter_handlers(self) -> Dict[str, Any]:
        """Filter handlers based on access control settings."""
        available_tools = set(self.all_handlers.keys())

        # Apply role-based access if agent has a role
        if self.agent_role and self.agent_role in self.role_based_access:
            role_tools = set(self.role_based_access[self.agent_role])
            available_tools = available_tools.intersection(role_tools)

        # Apply allowed_tools filter
        if self.allowed_tools is not None:
            available_tools = available_tools.intersection(self.allowed_tools)

        # Apply denied_tools filter (takes precedence)
        available_tools = available_tools - self.denied_tools

        return {
            tool: handler
            for tool, handler in self.all_handlers.items()
            if tool in available_tools
        }

    def set_agent_name(self, agent_name: str):
        """Set the agent name for this tool handler instance."""
        self.agent_name = agent_name
        self.handlers = self._filter_handlers()

    def set_agent_role(self, role: Optional[str]):
        """Set the agent role for role-based access control."""
        self.agent_role = role
        self.handlers = self._filter_handlers()

    def set_allowed_tools(self, allowed_tools: Optional[List[str]]):
        """Update the list of allowed tools for this agent."""
        self.allowed_tools = set(allowed_tools) if allowed_tools is not None else None
        self.handlers = self._filter_handlers()

    def set_denied_tools(self, denied_tools: List[str]):
        """Update the list of denied tools for this agent."""
        self.denied_tools = set(denied_tools)
        self.handlers = self._filter_handlers()

    def add_allowed_tool(self, tool_name: str):
        """Add a tool to the allowed list."""
        if self.allowed_tools is None:
            self.allowed_tools = set(self.all_handlers.keys())
        self.allowed_tools.add(tool_name)
        self.handlers = self._filter_handlers()

    def remove_allowed_tool(self, tool_name: str):
        """Remove a tool from the allowed list."""
        if self.allowed_tools is not None:
            self.allowed_tools.discard(tool_name)
            self.handlers = self._filter_handlers()

    def add_denied_tool(self, tool_name: str):
        """Add a tool to the denied list."""
        self.denied_tools.add(tool_name)
        self.handlers = self._filter_handlers()

    def remove_denied_tool(self, tool_name: str):
        """Remove a tool from the denied list."""
        self.denied_tools.discard(tool_name)
        self.handlers = self._filter_handlers()

    def get_available_tools(self) -> List[str]:
        """Get list of tools this agent has access to."""
        return list(self.handlers.keys())

    def has_tool_access(self, tool_name: str) -> bool:
        """Check if agent has access to a specific tool."""
        return tool_name in self.handlers

    def get_access_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's tool access configuration."""
        return {
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "available_tools": list(self.handlers.keys()),
            "denied_tools": list(self.denied_tools),
            "allowed_tools": list(self.allowed_tools) if self.allowed_tools else "all",
            "total_available": len(self.handlers),
            "total_possible": len(self.all_handlers),
        }

    def _check_agent_name(self) -> Optional[Dict[str, Any]]:
        """Check if agent name is set, return error dict if not."""
        if not self.agent_name:
            return {"success": False, "error": "Agent name not set"}
        return None

    def handle_get_context(self, **kwargs) -> Dict[str, Any]:
        """Handle get_context tool call."""
        error = self._check_agent_name()
        if error:
            return error
        kwargs["agent_name"] = self.agent_name
        return handle_get_context_call(self.context_mesh, **kwargs)

    def handle_push_context(self, **kwargs) -> Dict[str, Any]:
        """Handle push_context tool call."""
        error = self._check_agent_name()
        if error:
            return error
        kwargs["sender_agent"] = self.agent_name
        return handle_push_context_call(self.context_mesh, **kwargs)

    def handle_list_context(self, **kwargs) -> Dict[str, Any]:
        """Handle list_context tool call."""
        error = self._check_agent_name()
        if error:
            return error
        kwargs["agent_name"] = self.agent_name
        return handle_list_context_call(self.context_mesh, **kwargs)

    def handle_subscribe_to_topics(self, **kwargs) -> Dict[str, Any]:
        """Handle subscribe_to_topics tool call."""
        error = self._check_agent_name()
        if error:
            return error
        kwargs["agent_name"] = self.agent_name
        return handle_subscribe_to_topics_call(self.context_mesh, **kwargs)

    def handle_discover_topics(self, **kwargs) -> Dict[str, Any]:
        """Handle discover_topics tool call."""
        error = self._check_agent_name()
        if error:
            return error
        return handle_discover_topics_call(self.context_mesh, **kwargs)

    def handle_unsubscribe_from_topics(self, **kwargs) -> Dict[str, Any]:
        """Handle unsubscribe_from_topics tool call."""
        error = self._check_agent_name()
        if error:
            return error
        kwargs["agent_name"] = self.agent_name
        return handle_unsubscribe_from_topics_call(self.context_mesh, **kwargs)

    def handle_delete_topic(self, **kwargs) -> Dict[str, Any]:
        """Handle delete_topic tool call."""
        # Note: delete_topic doesn't require agent_name, it's an administrative operation
        return handle_delete_topic_call(self.context_mesh, **kwargs)

    def handle_tool_call(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Route a tool call to the appropriate handler with automatic agent name injection.

        Args:
            tool_name: Name of the tool being called
            **kwargs: Tool arguments

        Returns:
            Tool response dictionary
        """
        if tool_name not in self.handlers:
            # Check if tool exists but is denied
            if tool_name in self.all_handlers:
                return {
                    "success": False,
                    "error": f"Access denied to tool: {tool_name}",
                    "reason": f"Agent '{self.agent_name}' does not have permission to use this tool",
                    "available_tools": list(self.handlers.keys()),
                    "agent_role": self.agent_role,
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "available_tools": list(self.handlers.keys()),
                }

        return self.handlers[tool_name](**kwargs)

    def get_schemas(
        self, merge_with: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get tool schemas for this agent based on access control settings.

        Args:
            merge_with: Optional list of existing tool schemas to merge with Syntha tools

        Returns:
            List of tool schemas (existing tools + allowed Syntha tools, avoiding conflicts)
        """
        # Get schemas for tools this agent has access to
        available_tool_names = set(self.handlers.keys())
        all_syntha_schemas = get_all_tool_schemas()

        # Filter schemas to only include tools this agent can access
        syntha_schemas = [
            schema
            for schema in all_syntha_schemas
            if schema.get("name") in available_tool_names
        ]

        if merge_with is None:
            return syntha_schemas

        # Start with user's existing tools
        all_schemas = merge_with.copy()
        existing_names = {schema.get("name") for schema in merge_with}

        # Add allowed Syntha tools that don't conflict
        for schema in syntha_schemas:
            tool_name = schema.get("name")
            if tool_name not in existing_names:
                all_schemas.append(schema)
            else:
                # Rename Syntha tool to avoid conflict
                renamed_schema = schema.copy()
                renamed_schema["name"] = f"syntha_{tool_name}"
                renamed_schema["description"] = (
                    f"[Syntha] {schema.get('description', '')}"
                )
                all_schemas.append(renamed_schema)
                print(
                    f"Info: Renamed Syntha tool '{tool_name}' to 'syntha_{tool_name}' to avoid conflict"
                )

        return all_schemas

    def get_syntha_schemas_only(self) -> List[Dict[str, Any]]:
        """Get only Syntha's context management tool schemas."""
        return get_all_tool_schemas()

    def create_hybrid_handler(self, user_tool_handler=None):
        """
        Create a hybrid tool handler that can handle both Syntha and user tools.

        Args:
            user_tool_handler: Function that handles user's custom tools
                             Should accept (tool_name, **kwargs) and return result dict

        Returns:
            Function that can handle both Syntha and user tools
        """

        def hybrid_handler(tool_name: str, **kwargs) -> Dict[str, Any]:
            # Handle Syntha tools using the main handler (respects access control)
            if tool_name in self.all_handlers:
                return self.handle_tool_call(tool_name, **kwargs)

            # Handle renamed Syntha tools
            if tool_name.startswith("syntha_"):
                original_name = tool_name[7:]  # Remove "syntha_" prefix
                if original_name in self.all_handlers:
                    return self.handle_tool_call(original_name, **kwargs)

            # Fallback to user's tools
            if user_tool_handler:
                try:
                    return user_tool_handler(tool_name, **kwargs)
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"User tool handler error: {str(e)}",
                    }

            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "syntha_tools": list(self.handlers.keys()),
            }

        # Add utility methods to the hybrid handler
        hybrid_handler.get_syntha_schemas = self.get_syntha_schemas_only
        hybrid_handler.handle_syntha_tool = self.handle_tool_call
        hybrid_handler.syntha_handler = self

        return hybrid_handler

    def get_langchain_tools(self) -> List[Any]:
        """
        Get LangChain-compatible tools for all available Syntha tools.

        This is a convenience method that creates a tool factory and generates
        LangChain tools in a single call.

        Returns:
            List of LangChain BaseTool instances

        Raises:
            SynthaFrameworkError: If LangChain is not installed or tool creation fails

        Examples:
            from syntha import ContextMesh, ToolHandler

            mesh = ContextMesh()
            handler = ToolHandler(mesh, "MyAgent")

            # Get LangChain tools - just one line!
            langchain_tools = handler.get_langchain_tools()

            # Use with LangChain agent
            from langchain.agents import initialize_agent
            agent = initialize_agent(langchain_tools, llm, agent="zero-shot-react-description")
        """
        from .tool_factory import create_tool_factory

        factory = create_tool_factory(self)
        return factory.create_tools("langchain")

    def get_langgraph_tools(self) -> List[Dict[str, Any]]:
        """
        Get LangGraph-compatible tools for all available Syntha tools.

        Returns:
            List of LangGraph tool dictionaries

        Raises:
            SynthaFrameworkError: If tool creation fails

        Examples:
            from syntha import ContextMesh, ToolHandler

            mesh = ContextMesh()
            handler = ToolHandler(mesh, "MyAgent")

            # Get LangGraph tools
            langgraph_tools = handler.get_langgraph_tools()
        """
        from .tool_factory import create_tool_factory

        factory = create_tool_factory(self)
        return factory.create_tools("langgraph")

    def get_openai_functions(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI function calling definitions for all available Syntha tools.

        Returns:
            List of OpenAI function definitions

        Examples:
            from syntha import ContextMesh, ToolHandler

            mesh = ContextMesh()
            handler = ToolHandler(mesh, "MyAgent")

            # Get OpenAI functions
            openai_functions = handler.get_openai_functions()

            # Use with OpenAI API
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Get context for key1"}],
                functions=[func["function"] for func in openai_functions]
            )
        """
        from .tool_factory import create_tool_factory

        factory = create_tool_factory(self)
        return factory.create_tools("openai")

    def get_anthropic_tools(self) -> List[Dict[str, Any]]:
        """
        Get Anthropic Claude tool definitions for all available Syntha tools.

        Returns:
            List of Anthropic tool definitions

        Examples:
            from syntha import ContextMesh, ToolHandler

            mesh = ContextMesh()
            handler = ToolHandler(mesh, "MyAgent")

            # Get Anthropic tools
            anthropic_tools = handler.get_anthropic_tools()
        """
        from .tool_factory import create_tool_factory

        factory = create_tool_factory(self)
        return factory.create_tools("anthropic")

    def get_tools_for_framework(self, framework_name: str) -> List[Any]:
        """
        Get framework-specific tools for any supported framework.

        Args:
            framework_name: Name of the target framework (langchain, langgraph, openai, anthropic)

        Returns:
            List of framework-specific tool instances

        Raises:
            SynthaFrameworkError: If framework is not supported or tool creation fails

        Examples:
            from syntha import ContextMesh, ToolHandler

            mesh = ContextMesh()
            handler = ToolHandler(mesh, "MyAgent")

            # Get tools for any framework
            langchain_tools = handler.get_tools_for_framework("langchain")
            openai_functions = handler.get_tools_for_framework("openai")
            anthropic_tools = handler.get_tools_for_framework("anthropic")
        """
        from .tool_factory import create_tool_factory

        factory = create_tool_factory(self)
        return factory.create_tools(framework_name)

    def get_framework_handler(self, framework_name: str) -> Optional[Any]:
        """
        Get a framework-specific function handler for processing tool calls.

        Args:
            framework_name: Name of the target framework

        Returns:
            Framework-specific function handler or None if not supported

        Examples:
            from syntha import ContextMesh, ToolHandler

            mesh = ContextMesh()
            handler = ToolHandler(mesh, "MyAgent")

            # Get OpenAI function handler
            openai_handler = handler.get_framework_handler("openai")
            result = openai_handler("get_context", '{"keys": ["key1"]}')

            # Get Anthropic tool handler
            anthropic_handler = handler.get_framework_handler("anthropic")
            result = anthropic_handler("push_context", {"data": {"key": "value"}})
        """
        from .tool_factory import create_tool_factory

        factory = create_tool_factory(self)
        return factory.create_function_handler(framework_name)

    def create_framework_integration(
        self, framework_name: str, existing_tools: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a complete framework integration with both tools and handlers.

        Args:
            framework_name: Name of the target framework
            existing_tools: Optional list of existing framework tools to combine

        Returns:
            Dictionary containing tools, handlers, and integration metadata

        Examples:
            from syntha import ContextMesh, ToolHandler

            mesh = ContextMesh()
            handler = ToolHandler(mesh, "MyAgent")

            # Create complete LangChain integration
            integration = handler.create_framework_integration("langchain", existing_tools)

            tools = integration["tools"]  # All tools (existing + Syntha)
            syntha_tools = integration["syntha_tools"]  # Just Syntha tools
            handler_func = integration["handler"]  # Function handler if available
        """
        from .tool_factory import create_tool_factory

        factory = create_tool_factory(self)
        return factory.create_hybrid_integration(framework_name, existing_tools)

    def get_supported_frameworks(self) -> List[str]:
        """
        Get list of supported framework names.

        Returns:
            List of supported framework names

        Examples:
            from syntha import ContextMesh, ToolHandler

            mesh = ContextMesh()
            handler = ToolHandler(mesh, "MyAgent")

            frameworks = handler.get_supported_frameworks()
            print(f"Supported frameworks: {frameworks}")
        """
        from .tool_factory import create_tool_factory

        factory = create_tool_factory(self)
        return factory.get_supported_frameworks()

    def validate_framework(self, framework_name: str) -> Dict[str, Any]:
        """
        Validate that a framework is properly set up and ready to use.

        Args:
            framework_name: Name of the framework to validate

        Returns:
            Validation result dictionary with status and details

        Examples:
            from syntha import ContextMesh, ToolHandler

            mesh = ContextMesh()
            handler = ToolHandler(mesh, "MyAgent")

            # Check if LangChain is ready
            result = handler.validate_framework("langchain")
            if result["valid"]:
                print("LangChain integration ready!")
            else:
                print(f"Issue: {result['error']}")
                print(f"Suggestion: {result['suggestion']}")
        """
        from .tool_factory import create_tool_factory

        factory = create_tool_factory(self)
        return factory.validate_framework_requirements(framework_name)


# Integration utility functions for existing systems
def merge_tool_schemas(
    syntha_tools: List[Dict[str, Any]],
    user_tools: List[Dict[str, Any]],
    handle_conflicts: str = "warn",
) -> List[Dict[str, Any]]:
    """
    Merge Syntha tool schemas with user's existing tool schemas.

    Args:
        syntha_tools: Syntha's context management tools
        user_tools: User's existing tools
        handle_conflicts: How to handle name conflicts ("warn", "skip", "prefix")

    Returns:
        Combined list of tool schemas
    """
    syntha_names = {tool["name"] for tool in syntha_tools}
    combined_tools = syntha_tools.copy()

    for tool in user_tools:
        tool_name = tool.get("name")

        if tool_name in syntha_names:
            if handle_conflicts == "warn":
                print(f"Warning: Tool name conflict '{tool_name}' - user tool skipped")
                continue
            elif handle_conflicts == "skip":
                continue
            elif handle_conflicts == "prefix":
                tool = tool.copy()
                tool["name"] = f"user_{tool_name}"
                combined_tools.append(tool)
        else:
            combined_tools.append(tool)

    return combined_tools


def create_hybrid_tool_handler(context_mesh, agent_name: str, user_tool_handler=None):
    """
    Create a tool handler that combines Syntha tools with user's existing tools.

    Args:
        context_mesh: ContextMesh instance
        agent_name: Name of the agent
        user_tool_handler: User's existing tool handler function

    Returns:
        Function that can handle both Syntha and user tools
    """
    syntha_handler = ToolHandler(context_mesh, agent_name)

    def hybrid_handler(tool_name: str, **kwargs):
        """Handle both Syntha and user tools."""
        # Try Syntha tools first
        if tool_name in syntha_handler.handlers:
            return syntha_handler.handle_tool_call(tool_name, **kwargs)

        # Fallback to user's tools
        if user_tool_handler:
            try:
                return user_tool_handler(tool_name, **kwargs)
            except Exception as e:
                return {"success": False, "error": f"User tool handler error: {str(e)}"}

        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    # Create a wrapper object that includes the function and utility methods
    class HybridHandler:
        def __init__(self, handler_func, syntha_handler):
            self.handler_func = handler_func
            self.get_syntha_schemas = syntha_handler.get_syntha_schemas_only
            self.handle_syntha_tool = syntha_handler.handle_tool_call

        def __call__(self, tool_name: str, **kwargs):
            return self.handler_func(tool_name, **kwargs)

    return HybridHandler(hybrid_handler, syntha_handler)


# Add these at the end of the file, before the existing convenience functions

# Pre-defined role configurations for common use cases
PREDEFINED_ROLES = {
    "readonly": {
        "description": "Read-only access to context and discovery",
        "tools": ["get_context", "list_context", "discover_topics"],
    },
    "contributor": {
        "description": "Can read, write, and manage topic subscriptions",
        "tools": [
            "get_context",
            "list_context",
            "discover_topics",
            "push_context",
            "subscribe_to_topics",
            "unsubscribe_from_topics",
        ],
    },
    "moderator": {
        "description": "Contributor permissions plus ability to manage others' subscriptions",
        "tools": [
            "get_context",
            "list_context",
            "discover_topics",
            "push_context",
            "subscribe_to_topics",
            "unsubscribe_from_topics",
        ],
    },
    "admin": {
        "description": "Full access including destructive operations",
        "tools": [
            "get_context",
            "list_context",
            "discover_topics",
            "push_context",
            "subscribe_to_topics",
            "unsubscribe_from_topics",
            "delete_topic",
        ],
    },
}


def create_role_based_handler(
    context_mesh: ContextMesh,
    agent_name: str,
    role: str,
    custom_roles: Optional[Dict[str, Dict[str, Any]]] = None,
) -> ToolHandler:
    """
    Create a ToolHandler with predefined role-based access.

    Args:
        context_mesh: The ContextMesh instance
        agent_name: Name of the agent
        role: Role name (readonly, contributor, moderator, admin, or custom role)
        custom_roles: Optional dict of custom role definitions

    Returns:
        ToolHandler configured for the specified role

    Examples:
        # Use predefined roles
        readonly_handler = create_role_based_handler(mesh, "viewer", "readonly")
        admin_handler = create_role_based_handler(mesh, "admin", "admin")

        # Use custom roles
        custom_roles = {
            "analyst": {
                "description": "Data analysis role",
                "tools": ["get_context", "list_context", "push_context"]
            }
        }
        analyst_handler = create_role_based_handler(mesh, "analyst1", "analyst", custom_roles)
    """
    roles = {**PREDEFINED_ROLES, **(custom_roles or {})}

    if role not in roles:
        available_roles = list(roles.keys())
        raise ValueError(f"Unknown role '{role}'. Available roles: {available_roles}")

    allowed_tools = roles[role]["tools"]
    handler = ToolHandler(context_mesh, agent_name, allowed_tools=allowed_tools)
    handler.set_agent_role(role)
    return handler


def create_restricted_handler(
    context_mesh: ContextMesh, agent_name: str, restriction_level: str = "safe"
) -> ToolHandler:
    """
    Create a ToolHandler with common restriction patterns.

    Args:
        context_mesh: The ContextMesh instance
        agent_name: Name of the agent
        restriction_level: Level of restriction (safe, minimal, readonly)

    Returns:
        ToolHandler with appropriate restrictions

    Examples:
        # Safe mode: all tools except destructive ones
        safe_handler = create_restricted_handler(mesh, "agent1", "safe")

        # Minimal mode: only basic context operations
        minimal_handler = create_restricted_handler(mesh, "agent1", "minimal")

        # Readonly mode: no write operations
        readonly_handler = create_restricted_handler(mesh, "agent1", "readonly")
    """
    if restriction_level == "safe":
        # Allow everything except delete operations
        return ToolHandler(context_mesh, agent_name, denied_tools=["delete_topic"])
    elif restriction_level == "minimal":
        # Only basic context operations
        return ToolHandler(
            context_mesh,
            agent_name,
            allowed_tools=["get_context", "push_context", "list_context"],
        )
    elif restriction_level == "readonly":
        # Only read operations
        return ToolHandler(
            context_mesh,
            agent_name,
            allowed_tools=["get_context", "list_context", "discover_topics"],
        )
    else:
        available_levels = ["safe", "minimal", "readonly"]
        raise ValueError(
            f"Unknown restriction level '{restriction_level}'. Available levels: {available_levels}"
        )


def create_multi_agent_handlers(
    context_mesh: ContextMesh, agent_configs: Any
) -> Dict[str, ToolHandler]:
    """
    Create multiple ToolHandlers with different access configurations.

    Args:
        context_mesh: The ContextMesh instance
        agent_configs: Either a dict mapping agent names to their configuration
            or a list of agent configuration dicts with a required 'name' field.

    Returns:
        Dict mapping agent names to their ToolHandler instances

    Examples:
        configs = {
            "admin": {"role": "admin"},
            "user1": {"role": "contributor"},
            "viewer": {"role": "readonly"},
            "analyst": {"allowed_tools": ["get_context", "push_context"]},
            "restricted": {"denied_tools": ["delete_topic", "unsubscribe_from_topics"]}
        }
        handlers = create_multi_agent_handlers(mesh, configs)
    """
    handlers = {}

    # Normalize input to a dict: {agent_name: config}
    if isinstance(agent_configs, dict):
        normalized_configs: Dict[str, Dict[str, Any]] = agent_configs
    elif isinstance(agent_configs, list):
        normalized_configs = {}
        for idx, cfg in enumerate(agent_configs):
            if not isinstance(cfg, dict) or "name" not in cfg:
                raise ValueError(
                    "Each agent config in list form must be a dict with a 'name' field"
                )
            agent_name = cfg["name"]
            # Store a copy without the name field to avoid duplication
            normalized_cfg = {k: v for k, v in cfg.items() if k != "name"}
            normalized_configs[agent_name] = normalized_cfg
    else:
        raise ValueError(
            "agent_configs must be a dict of name->config or a list of configs with 'name'"
        )

    for agent_name, config in normalized_configs.items():
        if "role" in config:
            # Use role-based creation
            handlers[agent_name] = create_role_based_handler(
                context_mesh, agent_name, config["role"], config.get("custom_roles")
            )
        else:
            # Use direct ToolHandler creation
            handlers[agent_name] = ToolHandler(
                context_mesh,
                agent_name,
                allowed_tools=config.get("allowed_tools"),
                denied_tools=config.get("denied_tools"),
                role_based_access=config.get("role_based_access"),
            )

    return handlers


def get_role_info(role: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about available roles and their permissions.

    Args:
        role: Optional specific role to get info for

    Returns:
        Role information dict

    Examples:
        # Get all roles
        all_roles = get_role_info()

        # Get specific role
        admin_info = get_role_info("admin")
    """
    if role:
        if role not in PREDEFINED_ROLES:
            raise ValueError(
                f"Unknown role '{role}'. Available roles: {list(PREDEFINED_ROLES.keys())}"
            )
        return PREDEFINED_ROLES[role]

    return PREDEFINED_ROLES

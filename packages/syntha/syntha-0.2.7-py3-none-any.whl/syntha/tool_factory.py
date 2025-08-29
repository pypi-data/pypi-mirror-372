"""
Syntha Tool Factory - Unified Framework Integration

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

Provides a unified factory interface for creating framework-specific tools
from Syntha's context management capabilities.

Key Features:
- Single entry point for all framework integrations
- Automatic adapter selection and management
- Caching for performance optimization
- Extensible architecture for new frameworks
"""

import threading
from typing import Any, Callable, Dict, List, Optional, Union

from .exceptions import SynthaFrameworkError
from .framework_adapters import (
    FRAMEWORK_ADAPTERS,
    FrameworkAdapter,
    create_framework_adapter,
    get_supported_frameworks,
)


class SynthaToolFactory:
    """
    Factory class for creating framework-specific tools from Syntha capabilities.

    This class provides a unified interface for generating tools compatible with
    various LLM frameworks like LangChain, LangGraph, OpenAI, etc.
    """

    def __init__(self, tool_handler):
        """
        Initialize the tool factory.

        Args:
            tool_handler: Syntha ToolHandler instance
        """
        self.tool_handler = tool_handler
        self._adapter_cache: Dict[str, FrameworkAdapter] = {}

    def get_adapter(self, framework_name: str) -> FrameworkAdapter:
        """
        Get or create a framework adapter.

        Args:
            framework_name: Name of the framework

        Returns:
            Framework adapter instance

        Raises:
            SynthaFrameworkError: If framework is not supported
        """
        # Normalize framework name
        framework_name = framework_name.lower().strip()

        # Check cache first
        if framework_name in self._adapter_cache:
            return self._adapter_cache[framework_name]

        # Create new adapter
        adapter = create_framework_adapter(framework_name, self.tool_handler)
        self._adapter_cache[framework_name] = adapter
        return adapter

    def create_tools(self, framework_name: str) -> List[Any]:
        """
        Create framework-specific tools for all available Syntha tools.

        Args:
            framework_name: Name of the target framework

        Returns:
            List of framework-specific tool instances

        Examples:
            # Create LangChain tools
            langchain_tools = factory.create_tools("langchain")

            # Create OpenAI function definitions
            openai_functions = factory.create_tools("openai")
        """
        # Optimization: global, process-wide cache for handler-independent toolsets
        # OpenAI and Anthropic tool definitions are pure schemas and do not capture handler state.
        # We can safely build them once and filter per-handler by access control.
        framework_key = framework_name.lower().strip()

        # Ensure an adapter entry exists in the cache for visibility/metrics
        # (some frameworks use fast-path builders that don't require the adapter)
        try:
            _ = self.get_adapter(framework_key)
        except SynthaFrameworkError:
            # Propagate unsupported framework errors
            raise

        if framework_key in ("openai", "anthropic"):
            tools = _get_or_build_global_toolset(framework_key, self)
            # Filter by access control for this handler
            available = set(self.tool_handler.get_available_tools())
            if framework_key == "openai":
                return [
                    t for t in tools if t.get("function", {}).get("name") in available
                ]
            # anthropic structure: {"name": tool_name, ...}
            return [t for t in tools if t.get("name") in available]

        # Default path for other frameworks
        adapter = self.get_adapter(framework_name)
        return adapter.create_all_tools()

    def create_tool(self, framework_name: str, tool_name: str) -> Any:
        """
        Create a single framework-specific tool.

        Args:
            framework_name: Name of the target framework
            tool_name: Name of the Syntha tool to create

        Returns:
            Framework-specific tool instance

        Raises:
            SynthaFrameworkError: If tool is not available or framework is not supported
        """
        if not self.tool_handler.has_tool_access(tool_name):
            available_tools = self.tool_handler.get_available_tools()
            raise SynthaFrameworkError(
                f"Tool '{tool_name}' not available. Available tools: {available_tools}",
                tool_name=tool_name,
            )

        # Get the tool schema
        schemas = self.tool_handler.get_syntha_schemas_only()
        tool_schema = None
        for schema in schemas:
            if schema.get("name") == tool_name:
                tool_schema = schema
                break

        if not tool_schema:
            raise SynthaFrameworkError(
                f"Schema not found for tool '{tool_name}'", tool_name=tool_name
            )

        adapter = self.get_adapter(framework_name)
        return adapter.create_tool(tool_name, tool_schema)

    def get_supported_frameworks(self) -> List[str]:
        """
        Get list of supported framework names.

        Returns:
            List of supported framework names
        """
        return get_supported_frameworks()

    def is_framework_supported(self, framework_name: str) -> bool:
        """
        Check if a framework is supported.

        Args:
            framework_name: Name of the framework to check

        Returns:
            True if framework is supported
        """
        return framework_name.lower().strip() in FRAMEWORK_ADAPTERS

    def get_framework_info(
        self, framework_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get information about supported frameworks.

        Args:
            framework_name: Optional specific framework to get info for

        Returns:
            Framework information dictionary
        """
        if framework_name:
            framework_name = framework_name.lower().strip()
            if not self.is_framework_supported(framework_name):
                raise SynthaFrameworkError(
                    f"Unsupported framework: {framework_name}", framework=framework_name
                )

            adapter = self.get_adapter(framework_name)
            available_tools = self.tool_handler.get_available_tools()

            return {
                "framework": framework_name,
                "adapter_class": adapter.__class__.__name__,
                "available_tools": available_tools,
                "tool_count": len(available_tools),
                "agent_name": self.tool_handler.agent_name,
                "agent_role": getattr(self.tool_handler, "agent_role", None),
            }

        # Return info for all frameworks
        supported_frameworks = self.get_supported_frameworks()
        return {
            "supported_frameworks": supported_frameworks,
            "total_frameworks": len(supported_frameworks),
            "available_tools": self.tool_handler.get_available_tools(),
            "agent_name": self.tool_handler.agent_name,
            "agent_role": getattr(self.tool_handler, "agent_role", None),
        }

    def create_function_handler(self, framework_name: str) -> Optional[Callable]:
        """
        Create a function handler for frameworks that need custom call handling.

        Args:
            framework_name: Name of the framework

        Returns:
            Function handler if the framework supports it, None otherwise

        Examples:
            # For OpenAI function calling
            openai_handler = factory.create_function_handler("openai")
            result = openai_handler("get_context", '{"keys": ["key1", "key2"]}')

            # For Anthropic tool use
            anthropic_handler = factory.create_function_handler("anthropic")
            result = anthropic_handler("push_context", {"data": {"key": "value"}})
        """
        adapter = self.get_adapter(framework_name)

        # Check if adapter has a function handler method
        if hasattr(adapter, "create_function_handler"):
            return adapter.create_function_handler()
        elif hasattr(adapter, "create_tool_handler"):
            return adapter.create_tool_handler()

        return None

    def clear_cache(self):
        """
        Clear the adapter cache.

        This can be useful if the tool handler configuration changes
        and you want to force recreation of adapters.
        """
        self._adapter_cache.clear()

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the adapter cache.

        Returns:
            Cache information dictionary
        """
        return {
            "cached_frameworks": list(self._adapter_cache.keys()),
            "cache_size": len(self._adapter_cache),
            "supported_frameworks": self.get_supported_frameworks(),
        }

    def validate_framework_requirements(self, framework_name: str) -> Dict[str, Any]:
        """
        Validate that framework requirements are met (e.g., packages installed).

        Args:
            framework_name: Name of the framework to validate

        Returns:
            Validation result dictionary
        """
        framework_name = framework_name.lower().strip()

        if not self.is_framework_supported(framework_name):
            return {
                "valid": False,
                "error": f"Unsupported framework: {framework_name}",
                "supported_frameworks": self.get_supported_frameworks(),
            }

        try:
            # Try to create an adapter (this will check for required imports)
            adapter = self.get_adapter(framework_name)

            # Try to create a sample tool to validate everything works
            available_tools = self.tool_handler.get_available_tools()
            if available_tools:
                sample_tool_name = available_tools[0]
                schemas = self.tool_handler.get_syntha_schemas_only()
                sample_schema = next(
                    (s for s in schemas if s.get("name") == sample_tool_name), None
                )
                if sample_schema:
                    adapter.create_tool(sample_tool_name, sample_schema)

            return {
                "valid": True,
                "framework": framework_name,
                "adapter_class": adapter.__class__.__name__,
                "available_tools": available_tools,
            }

        except Exception as e:
            return {
                "valid": False,
                "framework": framework_name,
                "error": str(e),
                "suggestion": self._get_installation_suggestion(framework_name),
            }

    def _get_installation_suggestion(self, framework_name: str) -> str:
        """
        Get installation suggestion for a framework.

        Args:
            framework_name: Name of the framework

        Returns:
            Installation suggestion string
        """
        suggestions = {
            "langchain": "pip install langchain",
            "langgraph": "pip install langgraph",
            "openai": "pip install openai",
            "anthropic": "pip install anthropic",
        }

        return suggestions.get(
            framework_name, f"Install required packages for {framework_name}"
        )

    def create_hybrid_integration(
        self, framework_name: str, existing_tools: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a hybrid integration that combines Syntha tools with existing tools.

        Args:
            framework_name: Name of the target framework
            existing_tools: Optional list of existing framework tools

        Returns:
            Dictionary containing combined tools and handlers

        Examples:
            # Combine with existing LangChain tools
            integration = factory.create_hybrid_integration(
                "langchain",
                existing_tools=[existing_weather_tool, existing_email_tool]
            )
            all_tools = integration["tools"]
            handler = integration["handler"]
        """
        syntha_tools = self.create_tools(framework_name)

        combined_tools = []
        if existing_tools:
            combined_tools.extend(existing_tools)
        combined_tools.extend(syntha_tools)

        # Create function handler if available
        function_handler = self.create_function_handler(framework_name)

        return {
            "framework": framework_name,
            "tools": combined_tools,
            "syntha_tools": syntha_tools,
            "existing_tools": existing_tools or [],
            "total_tools": len(combined_tools),
            "syntha_tool_count": len(syntha_tools),
            "existing_tool_count": len(existing_tools) if existing_tools else 0,
            "handler": function_handler,
            "tool_handler": self.tool_handler,
        }


def create_tool_factory(tool_handler) -> SynthaToolFactory:
    """
    Create a SynthaToolFactory instance.

    Args:
        tool_handler: Syntha ToolHandler instance

    Returns:
        SynthaToolFactory instance

    Examples:
        from syntha import ContextMesh, ToolHandler
        from syntha.tool_factory import create_tool_factory

        mesh = ContextMesh()
        handler = ToolHandler(mesh, "MyAgent")
        factory = create_tool_factory(handler)

        # Get LangChain tools
        langchain_tools = factory.create_tools("langchain")
    """
    return SynthaToolFactory(tool_handler)


# --- Internal global cache for framework toolsets (stateless frameworks) ---
_GLOBAL_TOOLSET_CACHE: Dict[str, List[Any]] = {}
_GLOBAL_TOOLSET_LOCK = threading.Lock()


def _get_or_build_global_toolset(
    framework_key: str, factory: SynthaToolFactory
) -> List[Any]:
    """
    Build once per process toolsets for stateless frameworks and cache them.

    For frameworks like OpenAI and Anthropic, tool definitions are pure data derived
    from Syntha schemas and do not depend on the handler instance. We therefore
    build them once with an unrestricted view of schemas and reuse across handlers.
    """
    # Fast path: read cache without lock
    cached = _GLOBAL_TOOLSET_CACHE.get(framework_key)
    if cached is not None:
        return cached

    # Build minimal tool definitions directly from schemas (no adapter needed)
    schemas = factory.tool_handler.get_syntha_schemas_only()
    built_tools: List[Any] = []
    for schema in schemas:
        name = schema.get("name")
        if not name:
            continue
        params = schema.get("parameters", {})
        if framework_key == "openai":
            built_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": schema.get("description", f"Syntha {name} tool"),
                        "parameters": params,
                    },
                }
            )
        elif framework_key == "anthropic":
            built_tools.append(
                {
                    "name": name,
                    "description": schema.get("description", f"Syntha {name} tool"),
                    "input_schema": params,
                }
            )

    # Publish to cache with lock (double-checked)
    with _GLOBAL_TOOLSET_LOCK:
        existing = _GLOBAL_TOOLSET_CACHE.get(framework_key)
        if existing is None:
            _GLOBAL_TOOLSET_CACHE[framework_key] = built_tools
            return built_tools
        return existing

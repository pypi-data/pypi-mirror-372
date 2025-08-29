#!/usr/bin/env python3
"""
Tests for SynthaToolFactory functionality.

Tests the factory pattern implementation, caching, validation,
and hybrid integration capabilities.
"""

import sys
from unittest.mock import patch

import pytest

# Add the project root to path for imports
sys.path.insert(0, "..")

from syntha import ContextMesh, SynthaFrameworkError, ToolHandler
from syntha.framework_adapters import get_supported_frameworks
from syntha.tool_factory import SynthaToolFactory, create_tool_factory


class TestSynthaToolFactory:
    """Test the SynthaToolFactory class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="FactoryTestAgent")
        self.factory = SynthaToolFactory(self.handler)

    def test_factory_initialization(self):
        """Test factory initialization."""
        assert self.factory.tool_handler == self.handler
        assert len(self.factory._adapter_cache) == 0

    def test_get_adapter_caching(self):
        """Test that adapters are cached properly."""
        # First call should create adapter
        adapter1 = self.factory.get_adapter("openai")
        assert len(self.factory._adapter_cache) == 1
        assert "openai" in self.factory._adapter_cache

        # Second call should use cached adapter
        adapter2 = self.factory.get_adapter("openai")
        assert adapter1 is adapter2
        assert len(self.factory._adapter_cache) == 1

    def test_get_adapter_invalid_framework(self):
        """Test error handling for invalid frameworks."""
        with pytest.raises(SynthaFrameworkError) as exc_info:
            self.factory.get_adapter("nonexistent")

        assert "Unsupported framework" in str(exc_info.value)
        assert "nonexistent" in str(exc_info.value)

    def test_create_tools(self):
        """Test creating tools for a framework."""
        tools = self.factory.create_tools("openai")

        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check structure
        for tool in tools:
            assert "type" in tool
            assert tool["type"] == "function"
            assert "function" in tool

    def test_create_tool_single(self):
        """Test creating a single tool."""
        tool = self.factory.create_tool("openai", "get_context")

        assert "type" in tool
        assert tool["type"] == "function"
        assert tool["function"]["name"] == "get_context"

    def test_create_tool_invalid_tool(self):
        """Test error handling for invalid tool names."""
        with pytest.raises(SynthaFrameworkError) as exc_info:
            self.factory.create_tool("openai", "nonexistent_tool")

        assert "not available" in str(exc_info.value)

    def test_create_tool_access_denied(self):
        """Test error handling when tool access is denied."""
        # Create handler with limited access
        restricted_handler = ToolHandler(
            self.mesh, agent_name="RestrictedAgent", allowed_tools=["get_context"]
        )
        restricted_factory = SynthaToolFactory(restricted_handler)

        # Should work for allowed tool
        tool = restricted_factory.create_tool("openai", "get_context")
        assert tool["function"]["name"] == "get_context"

        # Should fail for denied tool
        with pytest.raises(SynthaFrameworkError):
            restricted_factory.create_tool("openai", "delete_topic")

    def test_get_supported_frameworks(self):
        """Test getting supported frameworks."""
        frameworks = self.factory.get_supported_frameworks()
        expected = get_supported_frameworks()

        assert set(frameworks) == set(expected)

    def test_is_framework_supported(self):
        """Test framework support checking."""
        assert self.factory.is_framework_supported("openai") is True
        assert self.factory.is_framework_supported("anthropic") is True
        assert self.factory.is_framework_supported("nonexistent") is False

        # Test case insensitivity
        assert self.factory.is_framework_supported("OpenAI") is True
        assert self.factory.is_framework_supported("ANTHROPIC") is True

    def test_get_framework_info_all(self):
        """Test getting info for all frameworks."""
        info = self.factory.get_framework_info()

        assert "supported_frameworks" in info
        assert "total_frameworks" in info
        assert "available_tools" in info
        assert "agent_name" in info

        assert info["agent_name"] == "FactoryTestAgent"
        assert len(info["supported_frameworks"]) > 0

    def test_get_framework_info_specific(self):
        """Test getting info for a specific framework."""
        info = self.factory.get_framework_info("openai")

        assert "framework" in info
        assert info["framework"] == "openai"
        assert "adapter_class" in info
        assert "available_tools" in info
        assert "tool_count" in info
        assert "agent_name" in info

    def test_get_framework_info_invalid(self):
        """Test error handling for invalid framework info request."""
        with pytest.raises(SynthaFrameworkError):
            self.factory.get_framework_info("nonexistent")

    def test_create_function_handler(self):
        """Test creating function handlers."""
        # OpenAI should have a function handler
        openai_handler = self.factory.create_function_handler("openai")
        assert callable(openai_handler)

        # Anthropic should have a tool handler
        anthropic_handler = self.factory.create_function_handler("anthropic")
        assert callable(anthropic_handler)

        # LangGraph might not have a special handler
        langgraph_handler = self.factory.create_function_handler("langgraph")
        # Should be None or callable
        assert langgraph_handler is None or callable(langgraph_handler)

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Create some adapters
        self.factory.get_adapter("openai")
        self.factory.get_adapter("anthropic")
        assert len(self.factory._adapter_cache) == 2

        # Clear cache
        self.factory.clear_cache()
        assert len(self.factory._adapter_cache) == 0

    def test_get_cache_info(self):
        """Test getting cache information."""
        # Initially empty
        info = self.factory.get_cache_info()
        assert info["cache_size"] == 0
        assert len(info["cached_frameworks"]) == 0

        # Create adapters
        self.factory.get_adapter("openai")
        self.factory.get_adapter("anthropic")

        # Check updated info
        info = self.factory.get_cache_info()
        assert info["cache_size"] == 2
        assert "openai" in info["cached_frameworks"]
        assert "anthropic" in info["cached_frameworks"]

    def test_validate_framework_requirements_valid(self):
        """Test framework validation for valid frameworks."""
        # OpenAI should be valid (no external dependencies)
        result = self.factory.validate_framework_requirements("openai")
        assert result["valid"] is True
        assert result["framework"] == "openai"

        # Anthropic should be valid
        result = self.factory.validate_framework_requirements("anthropic")
        assert result["valid"] is True

    def test_validate_framework_requirements_invalid(self):
        """Test framework validation for invalid frameworks."""
        result = self.factory.validate_framework_requirements("nonexistent")
        assert result["valid"] is False
        assert "Unsupported framework" in result["error"]

    def test_validate_framework_requirements_langchain(self):
        """Test framework validation for LangChain (likely missing)."""
        # Mock the imports to simulate missing LangChain
        with patch(
            "syntha.framework_adapters.LangChainAdapter.create_tool"
        ) as mock_create:
            mock_create.side_effect = SynthaFrameworkError(
                "LangChain not installed. Install with: pip install langchain",
                framework="langchain",
            )
            result = self.factory.validate_framework_requirements("langchain")
            # Should be invalid due to missing LangChain
            assert result["valid"] is False
        assert "suggestion" in result

    def test_create_hybrid_integration(self):
        """Test creating hybrid integrations."""
        existing_tools = [
            {"name": "weather_tool", "description": "Get weather"},
            {"name": "email_tool", "description": "Send email"},
        ]

        integration = self.factory.create_hybrid_integration("openai", existing_tools)

        assert isinstance(integration, dict)
        assert "framework" in integration
        assert integration["framework"] == "openai"
        assert "tools" in integration
        assert "syntha_tools" in integration
        assert "existing_tools" in integration
        assert "total_tools" in integration
        assert "syntha_tool_count" in integration
        assert "existing_tool_count" in integration
        assert "handler" in integration
        assert "tool_handler" in integration

        # Check counts
        assert integration["existing_tool_count"] == 2
        assert integration["syntha_tool_count"] > 0
        assert integration["total_tools"] == integration["syntha_tool_count"] + 2

    def test_create_hybrid_integration_no_existing(self):
        """Test hybrid integration with no existing tools."""
        integration = self.factory.create_hybrid_integration("anthropic")

        assert integration["existing_tool_count"] == 0
        assert integration["syntha_tool_count"] > 0
        assert integration["total_tools"] == integration["syntha_tool_count"]


class TestCreateToolFactory:
    """Test the create_tool_factory helper function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="HelperTestAgent")

    def test_create_tool_factory(self):
        """Test the create_tool_factory helper function."""
        factory = create_tool_factory(self.handler)

        assert isinstance(factory, SynthaToolFactory)
        assert factory.tool_handler == self.handler


class TestFactoryWithDifferentHandlerConfigurations:
    """Test factory behavior with different handler configurations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()

    def test_factory_with_restricted_handler(self):
        """Test factory with a restricted handler."""
        restricted_handler = ToolHandler(
            self.mesh,
            agent_name="RestrictedAgent",
            allowed_tools=["get_context", "list_context"],
        )
        factory = SynthaToolFactory(restricted_handler)

        tools = factory.create_tools("openai")
        assert len(tools) == 2  # Only allowed tools

        tool_names = [tool["function"]["name"] for tool in tools]
        assert "get_context" in tool_names
        assert "list_context" in tool_names
        assert "delete_topic" not in tool_names

    def test_factory_with_denied_tools(self):
        """Test factory with denied tools."""
        handler = ToolHandler(
            self.mesh, agent_name="DeniedAgent", denied_tools=["delete_topic"]
        )
        factory = SynthaToolFactory(handler)

        tools = factory.create_tools("anthropic")
        tool_names = [tool["name"] for tool in tools]

        assert "delete_topic" not in tool_names
        assert "get_context" in tool_names  # Should still be available

    def test_factory_with_role_based_handler(self):
        """Test factory with role-based access."""
        from syntha.tools import create_role_based_handler

        readonly_handler = create_role_based_handler(
            self.mesh, "ReadOnlyAgent", "readonly"
        )
        factory = SynthaToolFactory(readonly_handler)

        tools = factory.create_tools("openai")
        tool_names = [tool["function"]["name"] for tool in tools]

        # Should only have readonly tools
        assert "get_context" in tool_names
        assert "list_context" in tool_names
        assert "discover_topics" in tool_names
        assert "delete_topic" not in tool_names
        assert "push_context" not in tool_names


class TestFactoryErrorHandling:
    """Test comprehensive error handling in the factory."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="ErrorTestAgent")
        self.factory = SynthaToolFactory(self.handler)

    def test_adapter_creation_error(self):
        """Test error handling when adapter creation fails."""
        with pytest.raises(SynthaFrameworkError):
            self.factory.get_adapter("nonexistent_framework")

    def test_tool_creation_with_missing_schema(self):
        """Test tool creation when schema is missing."""
        # Mock handler to return empty schemas
        with patch.object(self.handler, "get_syntha_schemas_only", return_value=[]):
            with pytest.raises(SynthaFrameworkError) as exc_info:
                self.factory.create_tool("openai", "get_context")
            assert "Schema not found" in str(exc_info.value)

    def test_framework_validation_errors(self):
        """Test various framework validation error scenarios."""
        # Invalid framework
        result = self.factory.validate_framework_requirements("invalid")
        assert result["valid"] is False

        # Mock adapter creation error
        with patch.object(
            self.factory, "get_adapter", side_effect=Exception("Mock error")
        ):
            result = self.factory.validate_framework_requirements("openai")
            assert result["valid"] is False
            assert "Mock error" in result["error"]


class TestFactoryPerformance:
    """Test performance-related aspects of the factory."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="PerformanceTestAgent")
        self.factory = SynthaToolFactory(self.handler)

    def test_adapter_caching_performance(self):
        """Test that adapter caching improves performance."""
        import time

        # First call (creates adapter)
        start_time = time.time()
        tools1 = self.factory.create_tools("openai")
        first_call_time = time.time() - start_time

        # Second call (uses cached adapter)
        start_time = time.time()
        tools2 = self.factory.create_tools("openai")
        second_call_time = time.time() - start_time

        # Second call should be faster (or at least not significantly slower)
        assert second_call_time <= first_call_time * 2  # Allow some variance

        # Results should be equivalent
        assert len(tools1) == len(tools2)

    def test_multiple_framework_creation(self):
        """Test creating tools for multiple frameworks efficiently."""
        frameworks = ["openai", "anthropic", "langgraph"]

        all_tools = {}
        for framework in frameworks:
            tools = self.factory.create_tools(framework)
            all_tools[framework] = tools
            assert len(tools) > 0

        # Verify cache contains all frameworks
        cache_info = self.factory.get_cache_info()
        for framework in frameworks:
            assert framework in cache_info["cached_frameworks"]


class TestFactoryIntegrationScenarios:
    """Test real-world integration scenarios using the factory."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()

    def test_multi_agent_factory_usage(self):
        """Test using factory with multiple agents."""
        # Create different handlers
        admin_handler = ToolHandler(self.mesh, "AdminAgent")
        user_handler = ToolHandler(
            self.mesh, "UserAgent", allowed_tools=["get_context", "push_context"]
        )

        # Create factories
        admin_factory = SynthaToolFactory(admin_handler)
        user_factory = SynthaToolFactory(user_handler)

        # Get tools for each
        admin_tools = admin_factory.create_tools("openai")
        user_tools = user_factory.create_tools("openai")

        # Admin should have more tools
        assert len(admin_tools) > len(user_tools)

        # Both should work independently
        admin_handler_func = admin_factory.create_function_handler("openai")
        user_handler_func = user_factory.create_function_handler("openai")

        admin_result = admin_handler_func("list_context", "{}")
        user_result = user_handler_func("get_context", '{"keys": ["test"]}')

        assert admin_result["agent_name"] == "AdminAgent"
        assert user_result["agent_name"] == "UserAgent"

    def test_factory_with_context_data(self):
        """Test factory with actual context data."""
        handler = ToolHandler(self.mesh, "DataTestAgent")
        factory = SynthaToolFactory(handler)

        # Add context data
        self.mesh.push("test_key", {"value": "test_data"}, subscribers=["system"])

        # Create tools and test execution
        tools = factory.create_tools("langgraph")
        get_context_tool = next(t for t in tools if t["name"] == "get_context")

        # Execute tool
        result_str = get_context_tool["function"](keys=["test_key"])
        import json

        result = json.loads(result_str)

        assert result["success"] is True
        # Context might not be accessible depending on subscriber settings


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

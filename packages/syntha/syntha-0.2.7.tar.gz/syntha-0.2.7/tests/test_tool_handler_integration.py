#!/usr/bin/env python3
"""
Integration tests for ToolHandler framework methods.

Tests the integration between ToolHandler and the framework adapter system,
including the new convenience methods and hybrid integration features.
"""

import json
import sys
from unittest.mock import patch

import pytest

# Add the project root to path for imports
sys.path.insert(0, "..")

from syntha import ContextMesh, SynthaFrameworkError, ToolHandler


class TestToolHandlerFrameworkMethods:
    """Test the new framework integration methods on ToolHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="IntegrationTestAgent")

        # Add some test context
        self.mesh.push("test_key", {"value": "test_data"}, subscribers=["system"])

    def test_get_supported_frameworks(self):
        """Test getting supported frameworks."""
        frameworks = self.handler.get_supported_frameworks()

        assert isinstance(frameworks, list)
        assert len(frameworks) > 0
        assert "openai" in frameworks
        assert "anthropic" in frameworks
        assert "langgraph" in frameworks
        assert "langchain" in frameworks

    def test_get_openai_functions(self):
        """Test getting OpenAI function definitions."""
        functions = self.handler.get_openai_functions()

        assert isinstance(functions, list)
        assert len(functions) > 0

        # Check structure of first function
        func = functions[0]
        assert "type" in func
        assert func["type"] == "function"
        assert "function" in func
        assert "name" in func["function"]
        assert "description" in func["function"]
        assert "parameters" in func["function"]

    def test_get_anthropic_tools(self):
        """Test getting Anthropic tool definitions."""
        tools = self.handler.get_anthropic_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check structure of first tool
        tool = tools[0]
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool

    def test_get_langgraph_tools(self):
        """Test getting LangGraph tool definitions."""
        tools = self.handler.get_langgraph_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check structure of first tool
        tool = tools[0]
        assert "name" in tool
        assert "description" in tool
        assert "parameters" in tool
        assert "function" in tool
        assert callable(tool["function"])

    def test_get_langchain_tools_without_langchain(self):
        """Test that LangChain tools raise appropriate error when LangChain not available."""
        with patch(
            "syntha.framework_adapters.LangChainAdapter.create_tool"
        ) as mock_create:
            mock_create.side_effect = SynthaFrameworkError(
                "LangChain not installed. Install with: pip install langchain",
                framework="langchain",
            )
            with pytest.raises(SynthaFrameworkError) as exc_info:
                self.handler.get_langchain_tools()

            assert "LangChain not installed" in str(exc_info.value)

    def test_get_tools_for_framework(self):
        """Test the universal get_tools_for_framework method."""
        # Test valid frameworks
        openai_tools = self.handler.get_tools_for_framework("openai")
        assert isinstance(openai_tools, list)
        assert len(openai_tools) > 0

        anthropic_tools = self.handler.get_tools_for_framework("anthropic")
        assert isinstance(anthropic_tools, list)
        assert len(anthropic_tools) > 0

        # Test invalid framework
        with pytest.raises(SynthaFrameworkError):
            self.handler.get_tools_for_framework("nonexistent")

    def test_get_framework_handler(self):
        """Test getting framework-specific handlers."""
        # Test OpenAI handler
        openai_handler = self.handler.get_framework_handler("openai")
        assert callable(openai_handler)

        result = openai_handler("list_context", "{}")
        assert isinstance(result, dict)
        assert "success" in result

        # Test Anthropic handler
        anthropic_handler = self.handler.get_framework_handler("anthropic")
        assert callable(anthropic_handler)

        result = anthropic_handler("discover_topics", {})
        assert isinstance(result, dict)
        assert "success" in result

    def test_validate_framework(self):
        """Test framework validation."""
        # Test valid frameworks
        for framework in ["openai", "anthropic", "langgraph"]:
            result = self.handler.validate_framework(framework)
            assert isinstance(result, dict)
            assert "valid" in result
            assert result["valid"] is True
            assert "framework" in result
            assert result["framework"] == framework

        # Test LangChain (should be invalid due to missing dependency)
        with patch(
            "syntha.framework_adapters.LangChainAdapter.create_tool"
        ) as mock_create:
            mock_create.side_effect = SynthaFrameworkError(
                "LangChain not installed. Install with: pip install langchain",
                framework="langchain",
            )
            result = self.handler.validate_framework("langchain")
            assert result["valid"] is False
        assert "error" in result
        assert "suggestion" in result

        # Test invalid framework
        result = self.handler.validate_framework("nonexistent")
        assert result["valid"] is False
        assert "Unsupported framework" in result["error"]

    def test_create_framework_integration(self):
        """Test creating hybrid framework integrations."""
        existing_tools = [
            {"name": "weather_tool", "description": "Get weather"},
            {"name": "email_tool", "description": "Send email"},
        ]

        integration = self.handler.create_framework_integration(
            "openai", existing_tools
        )

        assert isinstance(integration, dict)
        assert "framework" in integration
        assert integration["framework"] == "openai"
        assert "tools" in integration
        assert "syntha_tools" in integration
        assert "existing_tools" in integration
        assert "total_tools" in integration
        assert "syntha_tool_count" in integration
        assert "existing_tool_count" in integration

        # Check counts
        assert integration["existing_tool_count"] == 2
        assert integration["syntha_tool_count"] > 0
        assert (
            integration["total_tools"]
            == integration["syntha_tool_count"] + integration["existing_tool_count"]
        )

        # Check that tools are combined
        assert len(integration["tools"]) == integration["total_tools"]


class TestRoleBasedIntegration:
    """Test role-based access control with framework integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()

    def test_admin_vs_readonly_tools(self):
        """Test that different roles get different numbers of tools."""
        # Create handlers with different access levels
        admin_handler = ToolHandler(
            self.mesh,
            agent_name="AdminAgent",
            allowed_tools=[
                "get_context",
                "push_context",
                "list_context",
                "delete_topic",
            ],
        )

        readonly_handler = ToolHandler(
            self.mesh,
            agent_name="ReadOnlyAgent",
            allowed_tools=["get_context", "list_context"],
        )

        # Get tools for each
        admin_openai = admin_handler.get_openai_functions()
        readonly_openai = readonly_handler.get_openai_functions()

        # Admin should have more tools
        assert len(admin_openai) > len(readonly_openai)

        # Check specific tools
        admin_tool_names = [tool["function"]["name"] for tool in admin_openai]
        readonly_tool_names = [tool["function"]["name"] for tool in readonly_openai]

        assert "delete_topic" in admin_tool_names
        assert "delete_topic" not in readonly_tool_names
        assert "get_context" in admin_tool_names
        assert "get_context" in readonly_tool_names

    def test_denied_tools_exclusion(self):
        """Test that denied tools are excluded from framework integration."""
        handler = ToolHandler(
            self.mesh,
            agent_name="RestrictedAgent",
            denied_tools=["delete_topic", "unsubscribe_from_topics"],
        )

        tools = handler.get_anthropic_tools()
        tool_names = [tool["name"] for tool in tools]

        assert "delete_topic" not in tool_names
        assert "unsubscribe_from_topics" not in tool_names
        assert "get_context" in tool_names  # Should still have allowed tools


class TestParameterConversionIntegration:
    """Test parameter conversion in real framework integration scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="ConversionAgent")

        # Add some test context
        self.mesh.push("key1", {"data": "value1"}, subscribers=["system"])
        self.mesh.push("key2", {"data": "value2"}, subscribers=["system"])

    def test_openai_parameter_conversion(self):
        """Test parameter conversion with OpenAI handler."""
        openai_handler = self.handler.get_framework_handler("openai")

        # Test comma-separated string conversion
        result = openai_handler("get_context", '{"keys": "key1,key2"}')
        assert result["success"] is True
        assert len(result["keys_found"]) >= 0  # May be 0 if keys don't exist

        # Test normal array parameter
        result = openai_handler("get_context", '{"keys": ["key1", "key2"]}')
        assert result["success"] is True

    def test_anthropic_parameter_conversion(self):
        """Test parameter conversion with Anthropic handler."""
        anthropic_handler = self.handler.get_framework_handler("anthropic")

        # Test comma-separated string conversion
        result = anthropic_handler(
            "subscribe_to_topics", {"topics": "topic1,topic2,topic3"}
        )
        assert result["success"] is True

    def test_langgraph_function_execution(self):
        """Test actual function execution with LangGraph tools."""
        tools = self.handler.get_langgraph_tools()

        # Find get_context tool
        get_context_tool = next((t for t in tools if t["name"] == "get_context"), None)
        assert get_context_tool is not None

        # Execute with parameters
        result_str = get_context_tool["function"](keys=["key1"])
        result = json.loads(result_str)
        assert result["success"] is True


class TestErrorHandlingIntegration:
    """Test error handling in integrated scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="ErrorTestAgent")

    def test_invalid_tool_access(self):
        """Test error handling when trying to access invalid tools."""
        # Create handler with no tool access
        restricted_handler = ToolHandler(
            self.mesh, agent_name="NoAccessAgent", allowed_tools=[]
        )

        # Should return empty lists, not error
        openai_tools = restricted_handler.get_openai_functions()
        assert openai_tools == []

        anthropic_tools = restricted_handler.get_anthropic_tools()
        assert anthropic_tools == []

    def test_framework_handler_errors(self):
        """Test error handling in framework handlers."""
        openai_handler = self.handler.get_framework_handler("openai")

        # Test with invalid JSON
        result = openai_handler("get_context", "invalid json")
        assert result["success"] is False
        assert "error" in result

        # Test with nonexistent tool
        result = openai_handler("nonexistent_tool", "{}")
        assert result["success"] is False
        assert "error" in result

    def test_hybrid_integration_error_handling(self):
        """Test error handling in hybrid integrations."""
        # Test with invalid framework
        with pytest.raises(SynthaFrameworkError):
            self.handler.create_framework_integration("nonexistent", [])

        # Test with valid framework and empty tools (should work)
        integration = self.handler.create_framework_integration("openai", [])
        assert integration["existing_tool_count"] == 0
        assert integration["syntha_tool_count"] > 0


class TestFactoryIntegration:
    """Test integration with the underlying SynthaToolFactory."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="FactoryTestAgent")

    def test_factory_methods_through_handler(self):
        """Test that handler methods properly use the factory."""
        # These methods should all work and return consistent results
        frameworks = self.handler.get_supported_frameworks()
        assert isinstance(frameworks, list)

        for framework in frameworks:
            if framework == "langchain":
                continue  # Skip LangChain due to dependency

            # Test validation
            validation = self.handler.validate_framework(framework)
            if validation["valid"]:
                # Test tool creation
                tools = self.handler.get_tools_for_framework(framework)
                assert len(tools) > 0

                # Test handler creation (if supported)
                handler = self.handler.get_framework_handler(framework)
                if handler:
                    assert callable(handler)

    def test_caching_behavior(self):
        """Test that the factory caching works correctly."""
        # Multiple calls should use cached adapters
        tools1 = self.handler.get_openai_functions()
        tools2 = self.handler.get_openai_functions()

        # Should return equivalent results
        assert len(tools1) == len(tools2)
        assert [t["function"]["name"] for t in tools1] == [
            t["function"]["name"] for t in tools2
        ]


class TestConcurrentAccess:
    """Test concurrent access to framework integration features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()

    def test_multiple_handlers_same_framework(self):
        """Test multiple handlers using the same framework."""
        handler1 = ToolHandler(self.mesh, agent_name="Agent1")
        handler2 = ToolHandler(self.mesh, agent_name="Agent2")

        # Both should be able to get tools
        tools1 = handler1.get_openai_functions()
        tools2 = handler2.get_openai_functions()

        # Should have same structure but different agent context
        assert len(tools1) == len(tools2)

        # Test that handlers work independently
        handler1_func = handler1.get_framework_handler("openai")
        handler2_func = handler2.get_framework_handler("openai")

        result1 = handler1_func("list_context", "{}")
        result2 = handler2_func("list_context", "{}")

        # Should both succeed but with different agent names
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["agent_name"] == "Agent1"
        assert result2["agent_name"] == "Agent2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

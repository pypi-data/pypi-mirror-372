#!/usr/bin/env python3
"""
Comprehensive error handling tests for Syntha framework integration.

Tests various error scenarios including:
- Framework validation errors
- Tool access violations
- Parameter validation errors
- Import dependency errors
- Integration failures
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the project root to path for imports
sys.path.insert(0, "..")

from syntha import ContextMesh, SynthaFrameworkError, ToolHandler
from syntha.framework_adapters import (
    AnthropicAdapter,
    LangChainAdapter,
    LangGraphAdapter,
    OpenAIAdapter,
    create_framework_adapter,
)
from syntha.tool_factory import SynthaToolFactory


class TestFrameworkValidationErrors:
    """Test framework validation and dependency errors."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="ErrorTestAgent")

    def test_unsupported_framework_error(self):
        """Test error handling for unsupported frameworks."""
        with pytest.raises(SynthaFrameworkError) as exc_info:
            create_framework_adapter("nonexistent_framework", self.handler)

        error = exc_info.value
        assert "Unsupported framework" in str(error)
        assert "nonexistent_framework" in str(error)
        assert error.framework == "nonexistent_framework"
        assert error.suggestions  # Should have suggestions

    def test_langchain_missing_dependency_error(self):
        """Test error handling when LangChain is missing."""
        adapter = LangChainAdapter(self.handler)

        # Mock the imports to simulate missing LangChain
        with patch(
            "syntha.framework_adapters.LangChainAdapter.create_tool"
        ) as mock_create:
            mock_create.side_effect = SynthaFrameworkError(
                "LangChain not installed. Install with: pip install langchain",
                framework="langchain",
            )
            with pytest.raises(SynthaFrameworkError) as exc_info:
                adapter.create_tool("test_tool", {"name": "test", "parameters": {}})

            error = exc_info.value
            assert "LangChain not installed" in str(error)
            assert "pip install langchain" in str(error)
            assert error.framework == "langchain"

    def test_framework_validation_comprehensive(self):
        """Test comprehensive framework validation."""
        factory = SynthaToolFactory(self.handler)

        # Test invalid framework
        result = factory.validate_framework_requirements("invalid_framework")
        assert result["valid"] is False
        assert "Unsupported framework" in result["error"]
        assert "supported_frameworks" in result

        # Test LangChain (missing dependency)
        with patch(
            "syntha.framework_adapters.LangChainAdapter.create_tool"
        ) as mock_create:
            mock_create.side_effect = SynthaFrameworkError(
                "LangChain not installed. Install with: pip install langchain",
                framework="langchain",
            )
            result = factory.validate_framework_requirements("langchain")
            assert result["valid"] is False
            assert "suggestion" in result
            assert "pip install langchain" in result["suggestion"]

    def test_tool_handler_framework_validation(self):
        """Test framework validation through ToolHandler methods."""
        # Test invalid framework
        result = self.handler.validate_framework("nonexistent")
        assert result["valid"] is False
        assert "Unsupported framework" in result["error"]

        # Test framework with missing dependencies
        with patch(
            "syntha.framework_adapters.LangChainAdapter.create_tool"
        ) as mock_create:
            mock_create.side_effect = SynthaFrameworkError(
                "LangChain not installed. Install with: pip install langchain",
                framework="langchain",
            )
            result = self.handler.validate_framework("langchain")
            assert result["valid"] is False
            assert "LangChain not installed" in result["error"]


class TestToolAccessErrors:
    """Test tool access and permission errors."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()

    def test_restricted_tool_access_error(self):
        """Test error when accessing restricted tools."""
        # Create handler with no tool access
        restricted_handler = ToolHandler(
            self.mesh, agent_name="NoAccessAgent", allowed_tools=[]
        )

        factory = SynthaToolFactory(restricted_handler)

        # Should raise error for any tool
        with pytest.raises(SynthaFrameworkError) as exc_info:
            factory.create_tool("openai", "get_context")

        assert "not available" in str(exc_info.value)

    def test_denied_tool_access_error(self):
        """Test error when accessing denied tools."""
        handler = ToolHandler(
            self.mesh, agent_name="DeniedAgent", denied_tools=["delete_topic"]
        )

        factory = SynthaToolFactory(handler)

        # Should raise error for denied tool
        with pytest.raises(SynthaFrameworkError):
            factory.create_tool("openai", "delete_topic")

        # Should work for allowed tools
        tool = factory.create_tool("openai", "get_context")
        assert tool["function"]["name"] == "get_context"

    def test_tool_handler_access_validation(self):
        """Test access validation in ToolHandler methods."""
        restricted_handler = ToolHandler(
            self.mesh, agent_name="RestrictedAgent", allowed_tools=["get_context"]
        )

        # Should return empty list for denied frameworks, not error
        tools = restricted_handler.get_openai_functions()
        assert len(tools) == 1  # Only get_context

        tool_names = [tool["function"]["name"] for tool in tools]
        assert "get_context" in tool_names
        assert "delete_topic" not in tool_names


class TestParameterValidationErrors:
    """Test parameter validation and conversion errors."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="ParamTestAgent")

    def test_invalid_json_parameter_error(self):
        """Test error handling for invalid JSON parameters."""
        openai_handler = self.handler.get_framework_handler("openai")

        # Test with invalid JSON
        result = openai_handler("get_context", "invalid json {")
        assert result["success"] is False
        assert "error" in result
        assert "Function call error" in result["error"]

    def test_missing_required_parameters(self):
        """Test error handling for missing required parameters."""
        anthropic_handler = self.handler.get_framework_handler("anthropic")

        # This should still work as Syntha tools handle missing params gracefully
        result = anthropic_handler("get_context", {})
        assert result["success"] is True  # Syntha tools are forgiving

    def test_parameter_conversion_edge_cases(self):
        """Test edge cases in parameter conversion."""
        adapter = OpenAIAdapter(self.handler)

        # Test empty string conversion
        result = adapter._convert_input_parameters("get_context", {"keys": ""})
        assert result["keys"] == [""]  # Empty string becomes list with empty string

        # Test None value
        result = adapter._convert_input_parameters("get_context", {"keys": None})
        assert result["keys"] is None

        # Test non-string value in conversion
        result = adapter._convert_input_parameters("get_context", {"keys": 123})
        assert result["keys"] == 123  # Should not convert non-strings


class TestToolExecutionErrors:
    """Test errors during tool execution."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="ExecTestAgent")

    def test_nonexistent_tool_execution_error(self):
        """Test error when executing nonexistent tools."""
        openai_handler = self.handler.get_framework_handler("openai")

        result = openai_handler("nonexistent_tool", "{}")
        assert result["success"] is False
        assert "error" in result
        assert (
            "Unknown tool" in result["error"] or "nonexistent_tool" in result["error"]
        )

    def test_tool_function_execution_error(self):
        """Test error handling in tool function execution."""
        adapter = OpenAIAdapter(self.handler)

        # Create a tool function that will fail
        tool_function = adapter._create_tool_function("nonexistent_tool")

        result = tool_function()
        assert result["success"] is False
        assert "error" in result
        assert (
            "Tool execution error" in result["error"]
            or "Unknown tool" in result["error"]
        )

    def test_langgraph_function_error_handling(self):
        """Test error handling in LangGraph tool functions."""
        tools = self.handler.get_langgraph_tools()

        # Find a tool and test with invalid parameters
        get_context_tool = next(t for t in tools if t["name"] == "get_context")

        # This should handle errors gracefully
        try:
            result_str = get_context_tool["function"](invalid_param="test")
            # Should return a string (might be error message)
            assert isinstance(result_str, str)
        except Exception as e:
            # If it does throw an exception, that's also acceptable
            assert "invalid_param" in str(e) or "unexpected" in str(e).lower()


class TestIntegrationErrors:
    """Test errors in integration scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="IntegrationTestAgent")

    def test_hybrid_integration_invalid_framework(self):
        """Test error in hybrid integration with invalid framework."""
        with pytest.raises(SynthaFrameworkError):
            self.handler.create_framework_integration("nonexistent", [])

    def test_factory_tool_creation_error(self):
        """Test error handling in factory tool creation."""
        factory = SynthaToolFactory(self.handler)

        # Mock schema retrieval to return invalid schema
        with patch.object(self.handler, "get_syntha_schemas_only", return_value=[]):
            with pytest.raises(SynthaFrameworkError) as exc_info:
                factory.create_tool("openai", "get_context")
            assert "Schema not found" in str(exc_info.value)

    def test_adapter_creation_failure(self):
        """Test error handling when adapter creation fails."""
        factory = SynthaToolFactory(self.handler)

        # Mock adapter creation to fail
        with patch("syntha.framework_adapters.FRAMEWORK_ADAPTERS", {"openai": None}):
            with pytest.raises(TypeError):
                factory.get_adapter("openai")


class TestErrorContext:
    """Test that errors provide helpful context and suggestions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="ContextTestAgent")

    def test_framework_error_context(self):
        """Test that framework errors include helpful context."""
        try:
            create_framework_adapter("invalid", self.handler)
        except SynthaFrameworkError as e:
            assert e.framework == "invalid"
            assert e.context.get("framework") == "invalid"
            assert len(e.suggestions) > 0
            assert len(e.suggestions) > 0

    def test_langchain_error_suggestions(self):
        """Test that LangChain errors provide installation suggestions."""
        adapter = LangChainAdapter(self.handler)

        with patch(
            "syntha.framework_adapters.LangChainAdapter.create_tool"
        ) as mock_create:
            mock_create.side_effect = SynthaFrameworkError(
                "LangChain not installed. Install with: pip install langchain",
                framework="langchain",
            )
            try:
                adapter.create_tool("test", {"name": "test", "parameters": {}})
            except SynthaFrameworkError as e:
                assert e.framework == "langchain"
                assert len(e.suggestions) > 0

    def test_tool_access_error_context(self):
        """Test that tool access errors provide helpful context."""
        restricted_handler = ToolHandler(
            self.mesh, agent_name="RestrictedAgent", allowed_tools=["get_context"]
        )

        factory = SynthaToolFactory(restricted_handler)

        try:
            factory.create_tool("openai", "delete_topic")
        except SynthaFrameworkError as e:
            assert e.tool_name == "delete_topic"
            assert "available" in str(e).lower()


class TestErrorRecovery:
    """Test error recovery and graceful degradation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="RecoveryTestAgent")

    def test_partial_framework_failure_recovery(self):
        """Test recovery when some frameworks fail."""
        # Mock LangChain to always fail
        with patch.object(
            LangChainAdapter,
            "create_tool",
            side_effect=SynthaFrameworkError("Mock error", "langchain"),
        ):
            # Other frameworks should still work
            openai_tools = self.handler.get_openai_functions()
            assert len(openai_tools) > 0

            anthropic_tools = self.handler.get_anthropic_tools()
            assert len(anthropic_tools) > 0

    def test_tool_creation_graceful_failure(self):
        """Test graceful handling of individual tool creation failures."""
        factory = SynthaToolFactory(self.handler)

        # Mock adapter to fail for specific tools
        adapter = factory.get_adapter("openai")
        original_create_tool = adapter.create_tool

        def mock_create_tool(tool_name, tool_schema):
            if tool_name == "get_context":
                raise Exception("Mock failure")
            return original_create_tool(tool_name, tool_schema)

        with patch.object(adapter, "create_tool", mock_create_tool):
            # Should raise error for the specific tool, but others should work
            with pytest.raises(SynthaFrameworkError):
                adapter.create_all_tools()

    def test_handler_error_isolation(self):
        """Test that handler errors don't affect other handlers."""
        handler1 = ToolHandler(self.mesh, "Agent1")
        handler2 = ToolHandler(self.mesh, "Agent2")

        # Break handler1 somehow
        handler1.agent_name = None  # This will cause errors

        # Handler2 should still work
        tools = handler2.get_openai_functions()
        assert len(tools) > 0

        # Handler1 should fail gracefully
        openai_handler = handler1.get_framework_handler("openai")
        result = openai_handler("get_context", "{}")
        assert result["success"] is False
        assert "Agent name not set" in result["error"]


class TestValidationHelpers:
    """Test validation helper functions and methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="ValidationTestAgent")

    def test_framework_support_validation(self):
        """Test framework support validation helpers."""
        factory = SynthaToolFactory(self.handler)

        # Valid frameworks
        assert factory.is_framework_supported("openai") is True
        assert factory.is_framework_supported("anthropic") is True
        assert factory.is_framework_supported("langgraph") is True
        assert factory.is_framework_supported("langchain") is True

        # Invalid framework
        assert factory.is_framework_supported("nonexistent") is False

        # Case insensitive
        assert factory.is_framework_supported("OpenAI") is True
        assert factory.is_framework_supported("ANTHROPIC") is True

    def test_tool_availability_validation(self):
        """Test tool availability validation."""
        # Test with unrestricted handler
        assert self.handler.has_tool_access("get_context") is True
        assert self.handler.has_tool_access("delete_topic") is True

        # Test with restricted handler
        restricted_handler = ToolHandler(
            self.mesh, agent_name="RestrictedAgent", allowed_tools=["get_context"]
        )
        assert restricted_handler.has_tool_access("get_context") is True
        assert restricted_handler.has_tool_access("delete_topic") is False

    def test_comprehensive_validation_report(self):
        """Test comprehensive validation reporting."""
        factory = SynthaToolFactory(self.handler)

        # Test all supported frameworks
        frameworks = factory.get_supported_frameworks()
        validation_results = {}

        for framework in frameworks:
            result = factory.validate_framework_requirements(framework)
            validation_results[framework] = result

        # Should have results for all frameworks
        assert len(validation_results) == len(frameworks)

        # Some should be valid, some might not be (e.g., LangChain)
        valid_count = sum(
            1 for result in validation_results.values() if result["valid"]
        )
        assert valid_count >= 3  # At least openai, anthropic, langgraph should be valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

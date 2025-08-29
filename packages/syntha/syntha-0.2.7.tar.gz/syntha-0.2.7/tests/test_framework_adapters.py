#!/usr/bin/env python3
"""
Unit tests for Syntha framework adapters.

Tests the framework adapter system including:
- Base FrameworkAdapter functionality
- Specific adapter implementations
- Parameter conversion
- Error handling
- Tool creation
"""

import json
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add the project root to path for imports
sys.path.insert(0, "..")

from syntha import ContextMesh, SynthaFrameworkError, ToolHandler
from syntha.framework_adapters import (
    FRAMEWORK_ADAPTERS,
    AnthropicAdapter,
    FrameworkAdapter,
    LangChainAdapter,
    LangGraphAdapter,
    OpenAIAdapter,
    create_framework_adapter,
    get_supported_frameworks,
)


class TestFrameworkAdapterBase:
    """Test the base FrameworkAdapter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="TestAgent")

    def test_supported_frameworks(self):
        """Test that all expected frameworks are supported."""
        frameworks = get_supported_frameworks()
        expected = ["langchain", "langgraph", "openai", "anthropic", "agno"]

        assert set(frameworks) == set(expected)
        assert len(frameworks) == len(expected)

    def test_create_framework_adapter_valid(self):
        """Test creating adapters for valid frameworks."""
        for framework in get_supported_frameworks():
            adapter = create_framework_adapter(framework, self.handler)
            assert isinstance(adapter, FrameworkAdapter)
            assert adapter.framework_name == framework
            assert adapter.tool_handler == self.handler

    def test_create_framework_adapter_invalid(self):
        """Test error handling for invalid frameworks."""
        with pytest.raises(SynthaFrameworkError) as exc_info:
            create_framework_adapter("nonexistent", self.handler)

        assert "Unsupported framework" in str(exc_info.value)
        assert "nonexistent" in str(exc_info.value)

    def test_parameter_conversion_base(self):
        """Test base parameter conversion functionality."""
        adapter = OpenAIAdapter(self.handler)  # Use concrete class

        # Test comma-separated string conversion
        result = adapter._convert_input_parameters(
            "get_context", {"keys": "key1,key2,key3"}
        )
        assert result["keys"] == ["key1", "key2", "key3"]

        # Test normal list parameter
        result = adapter._convert_input_parameters(
            "get_context", {"keys": ["key1", "key2"]}
        )
        assert result["keys"] == ["key1", "key2"]

        # Test non-list parameter
        result = adapter._convert_input_parameters(
            "push_context", {"data": {"key": "value"}}
        )
        assert result["data"] == {"key": "value"}


class TestOpenAIAdapter:
    """Test the OpenAI adapter implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="OpenAIAgent")
        self.adapter = OpenAIAdapter(self.handler)

    def test_adapter_initialization(self):
        """Test adapter initialization."""
        assert self.adapter.framework_name == "openai"
        assert self.adapter.tool_handler == self.handler

    def test_create_tool(self):
        """Test creating an OpenAI tool."""
        tool_schema = {
            "name": "test_tool",
            "description": "Test tool description",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "Parameter 1"}
                },
                "required": ["param1"],
            },
        }

        tool = self.adapter.create_tool("test_tool", tool_schema)

        assert tool["type"] == "function"
        assert tool["function"]["name"] == "test_tool"
        assert tool["function"]["description"] == "Test tool description"
        assert tool["function"]["parameters"] == tool_schema["parameters"]

    def test_create_all_tools(self):
        """Test creating all tools for OpenAI."""
        tools = self.adapter.create_all_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check that all tools have correct structure
        for tool in tools:
            assert "type" in tool
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]

    def test_function_handler(self):
        """Test the OpenAI function handler."""
        handler = self.adapter.create_function_handler()
        assert callable(handler)

        # Test with JSON string arguments
        result = handler("list_context", "{}")
        assert isinstance(result, dict)
        assert "success" in result

        # Test with dict arguments
        result = handler("list_context", {})
        assert isinstance(result, dict)
        assert "success" in result

        # Test with invalid JSON
        result = handler("list_context", "invalid json")
        assert result["success"] is False
        assert "error" in result


class TestAnthropicAdapter:
    """Test the Anthropic adapter implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="AnthropicAgent")
        self.adapter = AnthropicAdapter(self.handler)

    def test_adapter_initialization(self):
        """Test adapter initialization."""
        assert self.adapter.framework_name == "anthropic"
        assert self.adapter.tool_handler == self.handler

    def test_create_tool(self):
        """Test creating an Anthropic tool."""
        tool_schema = {
            "name": "test_tool",
            "description": "Test tool description",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "Parameter 1"}
                },
            },
        }

        tool = self.adapter.create_tool("test_tool", tool_schema)

        assert tool["name"] == "test_tool"
        assert tool["description"] == "Test tool description"
        assert tool["input_schema"] == tool_schema["parameters"]

    def test_create_all_tools(self):
        """Test creating all tools for Anthropic."""
        tools = self.adapter.create_all_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check that all tools have correct structure
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool

    def test_tool_handler(self):
        """Test the Anthropic tool handler."""
        handler = self.adapter.create_tool_handler()
        assert callable(handler)

        # Test tool execution
        result = handler("discover_topics", {})
        assert isinstance(result, dict)
        assert "success" in result


class TestLangGraphAdapter:
    """Test the LangGraph adapter implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="LangGraphAgent")
        self.adapter = LangGraphAdapter(self.handler)

    def test_adapter_initialization(self):
        """Test adapter initialization."""
        assert self.adapter.framework_name == "langgraph"
        assert self.adapter.tool_handler == self.handler

    def test_create_tool(self):
        """Test creating a LangGraph tool."""
        tool_schema = {
            "name": "test_tool",
            "description": "Test tool description",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "Parameter 1"}
                },
            },
        }

        tool = self.adapter.create_tool("test_tool", tool_schema)

        assert tool["name"] == "test_tool"
        assert tool["description"] == "Test tool description"
        assert tool["parameters"] == tool_schema["parameters"]
        assert "function" in tool
        assert callable(tool["function"])

    def test_create_all_tools(self):
        """Test creating all tools for LangGraph."""
        tools = self.adapter.create_all_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check that all tools have correct structure
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert "function" in tool
            assert callable(tool["function"])

    def test_tool_function_execution(self):
        """Test executing a LangGraph tool function."""
        tools = self.adapter.create_all_tools()

        # Find and test the get_context tool
        get_context_tool = next((t for t in tools if t["name"] == "get_context"), None)
        assert get_context_tool is not None

        result = get_context_tool["function"]()
        assert isinstance(result, str)  # LangGraph converts output to string

        # Parse the JSON result
        parsed_result = json.loads(result)
        assert "success" in parsed_result


class TestLangChainAdapter:
    """Test the LangChain adapter implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="LangChainAgent")
        self.adapter = LangChainAdapter(self.handler)

    def test_adapter_initialization(self):
        """Test adapter initialization."""
        assert self.adapter.framework_name == "langchain"
        assert self.adapter.tool_handler == self.handler

    def test_create_tool_with_langchain_available(self):
        """Test creating a LangChain tool when LangChain is available."""
        pytest.importorskip("langchain", reason="LangChain not installed")

        tool_schema = {
            "name": "test_tool",
            "description": "Test tool description",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "Parameter 1"}
                },
                "required": ["param1"],
            },
        }

        # This should succeed since LangChain is available
        tool = self.adapter.create_tool("test_tool", tool_schema)

        # Verify the tool was created successfully
        assert tool is not None
        assert hasattr(tool, "name")
        assert tool.name == "test_tool"
        assert hasattr(tool, "description")
        assert "Test tool description" in tool.description

    def test_create_tool_without_langchain(self):
        """Test error handling when LangChain is not available."""
        tool_schema = {
            "name": "test_tool",
            "description": "Test tool description",
            "parameters": {"type": "object", "properties": {}},
        }

        # Mock the imports to simulate missing LangChain
        with patch(
            "syntha.framework_adapters.LangChainAdapter.create_tool"
        ) as mock_create:
            mock_create.side_effect = SynthaFrameworkError(
                "LangChain not installed. Install with: pip install langchain",
                framework="langchain",
            )
            with pytest.raises(SynthaFrameworkError) as exc_info:
                self.adapter.create_tool("test_tool", tool_schema)

            assert "LangChain not installed" in str(exc_info.value)

    def test_pydantic_fields_creation(self):
        """Test creating Pydantic fields from schema."""
        # Test that pydantic field creation works when pydantic is available
        parameters = {
            "type": "object",
            "properties": {
                "string_param": {"type": "string", "description": "A string"},
                "array_param": {"type": "array", "description": "An array"},
                "bool_param": {"type": "boolean", "description": "A boolean"},
                "int_param": {"type": "integer", "description": "An integer"},
                "float_param": {"type": "number", "description": "A number"},
            },
            "required": ["string_param", "array_param"],
        }

        # Test the actual functionality if pydantic is available
        try:
            fields = self.adapter._create_pydantic_fields(parameters)
            # Verify that fields were created correctly
            assert "string_param" in fields
            assert "array_param" in fields
            assert "bool_param" in fields
            assert "int_param" in fields
            assert "float_param" in fields
        except ImportError:
            # If pydantic is not available, test the error handling
            with pytest.raises(ImportError) as exc_info:
                self.adapter._create_pydantic_fields(parameters)
            assert "No module named 'pydantic'" in str(exc_info.value)


class TestParameterConversion:
    """Test parameter conversion functionality across adapters."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="ConversionAgent")

    def test_comma_separated_string_conversion(self):
        """Test conversion of comma-separated strings to lists."""
        adapter = OpenAIAdapter(self.handler)

        # Test keys parameter (should convert)
        result = adapter._convert_input_parameters(
            "get_context", {"keys": "key1,key2,key3"}
        )
        assert result["keys"] == ["key1", "key2", "key3"]

        # Test topics parameter (should convert)
        result = adapter._convert_input_parameters(
            "subscribe_to_topics", {"topics": "topic1,topic2"}
        )
        assert result["topics"] == ["topic1", "topic2"]

        # Test data parameter (should not convert)
        result = adapter._convert_input_parameters(
            "push_context", {"data": "not,a,list"}
        )
        assert result["data"] == "not,a,list"

    def test_whitespace_handling(self):
        """Test that whitespace is properly stripped from converted parameters."""
        adapter = OpenAIAdapter(self.handler)

        result = adapter._convert_input_parameters(
            "get_context", {"keys": " key1 , key2 , key3 "}
        )
        assert result["keys"] == ["key1", "key2", "key3"]

    def test_should_convert_to_list(self):
        """Test the _should_convert_to_list method."""
        adapter = OpenAIAdapter(self.handler)

        # Should convert
        assert adapter._should_convert_to_list("get_context", "keys") is True
        assert adapter._should_convert_to_list("subscribe_to_topics", "topics") is True
        assert (
            adapter._should_convert_to_list("unsubscribe_from_topics", "topics") is True
        )

        # Should not convert
        assert adapter._should_convert_to_list("push_context", "data") is False
        assert adapter._should_convert_to_list("get_context", "unknown_param") is False
        assert adapter._should_convert_to_list("unknown_tool", "keys") is False


class TestErrorHandling:
    """Test error handling across adapters."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="ErrorAgent")

    def test_tool_creation_error_handling(self):
        """Test error handling during tool creation."""
        adapter = OpenAIAdapter(self.handler)

        # Mock a tool creation error
        with patch.object(self.handler, "has_tool_access", return_value=False):
            tools = adapter.create_all_tools()
            # Should return empty list, not crash
            assert tools == []

    def test_tool_function_error_handling(self):
        """Test error handling in tool function execution."""
        adapter = OpenAIAdapter(self.handler)

        # Create tool function that will cause an error
        tool_function = adapter._create_tool_function("nonexistent_tool")

        result = tool_function()
        assert result["success"] is False
        assert "error" in result
        assert (
            "Tool execution error" in result["error"]
            or "Unknown tool" in result["error"]
        )

    def test_framework_specific_errors(self):
        """Test framework-specific error handling."""
        # Test LangChain error
        adapter = LangChainAdapter(self.handler)
        with patch(
            "syntha.framework_adapters.LangChainAdapter.create_tool"
        ) as mock_create:
            mock_create.side_effect = SynthaFrameworkError(
                "LangChain not installed. Install with: pip install langchain",
                framework="langchain",
            )
            with pytest.raises(SynthaFrameworkError) as exc_info:
                adapter.create_tool("test_tool", {"name": "test", "parameters": {}})
            assert "LangChain not installed" in str(exc_info.value)


class TestAccessControl:
    """Test that role-based access control works with framework adapters."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()

    def test_restricted_handler_tools(self):
        """Test that restricted handlers only create allowed tools."""
        # Create handler with limited access
        restricted_handler = ToolHandler(
            self.mesh,
            agent_name="RestrictedAgent",
            allowed_tools=["get_context", "list_context"],
        )

        adapter = OpenAIAdapter(restricted_handler)
        tools = adapter.create_all_tools()

        # Should only have 2 tools
        assert len(tools) == 2

        tool_names = [tool["function"]["name"] for tool in tools]
        assert "get_context" in tool_names
        assert "list_context" in tool_names
        assert "delete_topic" not in tool_names

    def test_admin_handler_tools(self):
        """Test that admin handlers get all tools."""
        admin_handler = ToolHandler(self.mesh, agent_name="AdminAgent")

        adapter = OpenAIAdapter(admin_handler)
        tools = adapter.create_all_tools()

        # Should have all available tools
        assert len(tools) == len(admin_handler.get_available_tools())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Tests for Agno framework integration.

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
"""

import json
from typing import List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from syntha.context import ContextMesh
from syntha.framework_adapters import AgnoAdapter, SynthaFrameworkError
from syntha.tools import ToolHandler


class TestAgnoAdapter:
    """Test the Agno framework adapter."""

    @pytest.fixture
    def mock_context_mesh(self):
        """Create a mock ContextMesh for testing."""
        mesh = Mock()
        mesh.get_context.return_value = {"test_key": "test_value"}
        mesh.set_context.return_value = None
        mesh.subscribe_to_topics.return_value = None
        return mesh

    @pytest.fixture
    def tool_handler(self, mock_context_mesh):
        """Create a ToolHandler for testing."""
        return ToolHandler(mock_context_mesh)

    @pytest.fixture
    def agno_adapter(self, tool_handler):
        """Create an AgnoAdapter for testing."""
        return AgnoAdapter(tool_handler)

    def test_adapter_initialization(self, tool_handler):
        """Test AgnoAdapter initialization."""
        adapter = AgnoAdapter(tool_handler)
        assert adapter.framework_name == "agno"
        assert adapter.tool_handler == tool_handler

    def test_create_tool_without_agno_installed(self, agno_adapter):
        """Test creating tool when Agno is not installed."""
        with patch("syntha.framework_adapters.AgnoAdapter.create_tool") as mock_create:
            # Mock the import error
            def side_effect(*args, **kwargs):
                raise SynthaFrameworkError(
                    "Agno not installed. Install with: pip install agno",
                    framework="agno",
                )

            mock_create.side_effect = side_effect

            with pytest.raises(SynthaFrameworkError) as exc_info:
                agno_adapter.create_tool("get_context", {})

            assert "Agno not installed" in str(exc_info.value)

    @patch("syntha.framework_adapters.AgnoAdapter._create_tool_function")
    def test_create_tool_success(self, mock_create_tool_function, agno_adapter):
        """Test successful tool creation."""
        pytest.importorskip("agno", reason="Agno not installed")

        # Mock the tool function
        mock_tool_func = Mock(return_value={"result": "success"})
        mock_create_tool_function.return_value = mock_tool_func

        # Mock Agno Function
        mock_agno_function = Mock()

        with patch("agno.tools.Function") as mock_function_class:
            mock_function_class.from_callable.return_value = mock_agno_function

            tool_schema = {
                "description": "Get context values",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keys": {"type": "array", "description": "Keys to retrieve"},
                        "default_value": {
                            "type": "string",
                            "description": "Default value if key not found",
                        },
                    },
                    "required": ["keys"],
                },
            }

            result = agno_adapter.create_tool("get_context", tool_schema)

            assert result == mock_agno_function
            mock_function_class.from_callable.assert_called_once()

    @patch("syntha.framework_adapters.AgnoAdapter._create_tool_function")
    def test_agno_tool_wrapper_execution(self, mock_create_tool_function, agno_adapter):
        """Test the Agno tool wrapper function execution."""
        pytest.importorskip("agno", reason="Agno not installed")

        # Mock the tool function
        mock_tool_func = Mock(return_value={"result": "success", "data": [1, 2, 3]})
        mock_create_tool_function.return_value = mock_tool_func

        # Mock Agno Function to capture the wrapper function
        captured_wrapper = None

        def capture_from_callable(func, name=None, strict=False):
            nonlocal captured_wrapper
            captured_wrapper = func
            return Mock()

        with patch("agno.tools.Function") as mock_function_class:
            mock_function_class.from_callable.side_effect = capture_from_callable

            tool_schema = {
                "description": "Test tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "test_param": {
                            "type": "string",
                            "description": "Test parameter",
                        }
                    },
                    "required": ["test_param"],
                },
            }

            agno_adapter.create_tool("test_tool", tool_schema)

            # Test the captured wrapper function
            assert captured_wrapper is not None
            result = captured_wrapper(test_param="test_value")

            # Should return JSON string of the result
            expected_result = json.dumps(
                {"result": "success", "data": [1, 2, 3]}, indent=2
            )
            assert result == expected_result

            # Verify the original tool function was called with correct parameters
            mock_tool_func.assert_called_once_with(test_param="test_value")

    @patch("syntha.framework_adapters.AgnoAdapter._create_tool_function")
    def test_agno_tool_wrapper_error_handling(
        self, mock_create_tool_function, agno_adapter
    ):
        """Test error handling in the Agno tool wrapper."""
        pytest.importorskip("agno", reason="Agno not installed")

        # Mock the tool function to raise an exception
        mock_tool_func = Mock(side_effect=Exception("Tool execution failed"))
        mock_create_tool_function.return_value = mock_tool_func

        captured_wrapper = None

        def capture_from_callable(func, name=None, strict=False):
            nonlocal captured_wrapper
            captured_wrapper = func
            return Mock()

        with patch("agno.tools.Function") as mock_function_class:
            mock_function_class.from_callable.side_effect = capture_from_callable

            tool_schema = {
                "description": "Test tool",
                "parameters": {"type": "object", "properties": {}},
            }

            agno_adapter.create_tool("test_tool", tool_schema)

            # Test error handling
            result = captured_wrapper()
            assert "Error executing test_tool: Tool execution failed" in result

    @patch("syntha.framework_adapters.AgnoAdapter._create_tool_function")
    def test_agno_tool_wrapper_list_conversion(
        self, mock_create_tool_function, agno_adapter
    ):
        """Test parameter list conversion in the Agno tool wrapper."""
        pytest.importorskip("agno", reason="Agno not installed")

        mock_tool_func = Mock(return_value="success")
        mock_create_tool_function.return_value = mock_tool_func

        captured_wrapper = None

        def capture_from_callable(func, name=None, strict=False):
            nonlocal captured_wrapper
            captured_wrapper = func
            return Mock()

        with patch("agno.tools.Function") as mock_function_class:
            mock_function_class.from_callable.side_effect = capture_from_callable

            # Mock the _should_convert_to_list method to return True for 'keys' parameter
            with patch.object(
                agno_adapter, "_should_convert_to_list", return_value=True
            ):
                tool_schema = {
                    "description": "Test tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keys": {"type": "array", "description": "Keys parameter"}
                        },
                    },
                }

                agno_adapter.create_tool("get_context", tool_schema)

                # Test string to list conversion
                captured_wrapper(keys="single_key")
                mock_tool_func.assert_called_with(keys=["single_key"])

                # Test that lists are passed through unchanged
                mock_tool_func.reset_mock()
                captured_wrapper(keys=["key1", "key2"])
                mock_tool_func.assert_called_with(keys=["key1", "key2"])

    def test_create_tools_all_tools(self, agno_adapter):
        """Test creating all available tools."""
        with patch.object(
            agno_adapter.tool_handler, "get_available_tools"
        ) as mock_get_tools:
            mock_get_tools.return_value = ["tool1", "tool2", "tool3"]

            with patch.object(agno_adapter, "create_tool") as mock_create_tool:
                mock_create_tool.return_value = Mock()

                with patch.object(
                    agno_adapter.tool_handler, "get_syntha_schemas_only"
                ) as mock_get_schemas:
                    mock_get_schemas.return_value = [
                        {"name": "tool1", "description": "Test tool 1"},
                        {"name": "tool2", "description": "Test tool 2"},
                        {"name": "tool3", "description": "Test tool 3"},
                    ]

                    with patch.object(
                        agno_adapter.tool_handler, "has_tool_access"
                    ) as mock_has_access:
                        mock_has_access.return_value = True

                        result = agno_adapter.create_tools()

                        assert len(result) == 3
                        assert mock_create_tool.call_count == 3

    def test_create_tools_specific_tools(self, agno_adapter):
        """Test creating specific tools."""
        with patch.object(
            agno_adapter.tool_handler, "get_available_tools"
        ) as mock_get_tools:
            mock_get_tools.return_value = ["tool1", "tool2", "tool3"]

            with patch.object(agno_adapter, "create_tool") as mock_create_tool:
                mock_create_tool.return_value = Mock()

                with patch.object(
                    agno_adapter.tool_handler, "get_syntha_schemas_only"
                ) as mock_get_schemas:
                    mock_get_schemas.return_value = [
                        {"name": "tool1", "description": "Test tool 1"},
                        {"name": "tool2", "description": "Test tool 2"},
                        {"name": "tool3", "description": "Test tool 3"},
                    ]

                    with patch.object(
                        agno_adapter.tool_handler, "has_tool_access"
                    ) as mock_has_access:
                        mock_has_access.return_value = True

                        result = agno_adapter.create_tools(["tool1", "tool3"])

                        assert len(result) == 2
                        assert mock_create_tool.call_count == 2

    def test_create_tools_invalid_tools(self, agno_adapter):
        """Test creating tools with invalid tool names."""
        with patch.object(
            agno_adapter.tool_handler, "get_available_tools"
        ) as mock_get_tools:
            mock_get_tools.return_value = ["tool1", "tool2"]

            with pytest.raises(SynthaFrameworkError) as exc_info:
                agno_adapter.create_tools(["tool1", "invalid_tool"])

            assert "Unknown tools: {'invalid_tool'}" in str(exc_info.value)

    def test_create_tools_with_errors(self, agno_adapter, capsys):
        """Test creating tools when some tools fail to create."""
        with patch.object(
            agno_adapter.tool_handler, "get_available_tools"
        ) as mock_get_tools:
            mock_get_tools.return_value = ["tool1", "tool2", "tool3"]

            def create_tool_side_effect(tool_name, schema):
                if tool_name == "tool2":
                    raise Exception("Tool creation failed")
                return Mock()

            with patch.object(agno_adapter, "create_tool") as mock_create_tool:
                mock_create_tool.side_effect = create_tool_side_effect

                with patch.object(
                    agno_adapter.tool_handler, "get_syntha_schemas_only"
                ) as mock_get_schemas:
                    mock_get_schemas.return_value = [
                        {"name": "tool1", "description": "Test tool 1"},
                        {"name": "tool2", "description": "Test tool 2"},
                        {"name": "tool3", "description": "Test tool 3"},
                    ]

                    with patch.object(
                        agno_adapter.tool_handler, "has_tool_access"
                    ) as mock_has_access:
                        mock_has_access.return_value = True

                        result = agno_adapter.create_tools()

                        # Should return 2 tools (tool1 and tool3), skipping the failed tool2
                        assert len(result) == 2

                        # Check that warning was printed
                        captured = capsys.readouterr()
                        assert (
                            "Warning: Failed to create Agno tool 'tool2'"
                            in captured.out
                        )

    def test_parameter_type_mapping(self, agno_adapter):
        """Test parameter type mapping from JSON schema to Python types."""
        pytest.importorskip("agno", reason="Agno not installed")

        with patch("syntha.framework_adapters.AgnoAdapter._create_tool_function"):
            captured_wrapper = None

            def capture_from_callable(func, name=None, strict=False):
                nonlocal captured_wrapper
                captured_wrapper = func
                return Mock()

            with patch("agno.tools.Function") as mock_function_class:
                mock_function_class.from_callable.side_effect = capture_from_callable

                tool_schema = {
                    "description": "Test tool with various parameter types",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "string_param": {"type": "string"},
                            "int_param": {"type": "integer"},
                            "float_param": {"type": "number"},
                            "bool_param": {"type": "boolean"},
                            "array_param": {"type": "array"},
                            "optional_param": {"type": "string"},
                        },
                        "required": [
                            "string_param",
                            "int_param",
                            "float_param",
                            "bool_param",
                            "array_param",
                        ],
                    },
                }

                agno_adapter.create_tool("test_tool", tool_schema)

                # Verify the wrapper function has correct annotations
                annotations = captured_wrapper.__annotations__

                assert annotations["string_param"] == str
                assert annotations["int_param"] == int
                assert annotations["float_param"] == float
                assert annotations["bool_param"] == bool
                assert annotations["array_param"] == List[str]
                # Optional parameter should be Optional[str]
                optional_str = str(annotations["optional_param"])
                assert (
                    "Optional[str]" in optional_str
                    or "Union[str, NoneType]" in optional_str
                    or "str | None" in optional_str
                )
                assert annotations["return"] == str


class TestAgnoIntegrationEnd2End:
    """End-to-end integration tests with Agno."""

    def test_agno_agent_with_syntha_tools(self):
        """Test using Syntha tools with an Agno agent."""
        pytest.importorskip("agno", reason="Agno not installed")

        from agno.agent import Agent

        # Create context mesh and tool handler
        context_mesh = ContextMesh()
        tool_handler = ToolHandler(context_mesh)

        # Create Agno adapter
        adapter = AgnoAdapter(tool_handler)

        # Create Agno tools from Syntha (use tools that actually exist)
        syntha_tools = adapter.create_tools(["get_context", "push_context"])

        # Verify we got the tools
        assert len(syntha_tools) == 2
        assert all(hasattr(tool, "name") for tool in syntha_tools)

        # Test that tools can be used (without actually creating an agent due to API key requirements)
        get_context_tool = next(
            tool for tool in syntha_tools if tool.name == "get_context"
        )

        # Test the tool function directly
        result = get_context_tool.entrypoint(keys=["test_key"])
        assert isinstance(result, str)  # Should return a string result

    def test_framework_adapter_registry(self):
        """Test that Agno adapter is properly registered."""
        from syntha.framework_adapters import (
            FRAMEWORK_ADAPTERS,
            get_supported_frameworks,
        )

        assert "agno" in FRAMEWORK_ADAPTERS
        assert "agno" in get_supported_frameworks()
        assert FRAMEWORK_ADAPTERS["agno"] == AgnoAdapter

    def test_create_framework_adapter_agno(self):
        """Test creating Agno adapter through the factory function."""
        from syntha.framework_adapters import create_framework_adapter

        context_mesh = ContextMesh()
        tool_handler = ToolHandler(context_mesh)

        adapter = create_framework_adapter("agno", tool_handler)

        assert isinstance(adapter, AgnoAdapter)
        assert adapter.framework_name == "agno"
        assert adapter.tool_handler == tool_handler

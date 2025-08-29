"""
Framework Adapters for Syntha Context Management

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

Provides automatic framework integration for Syntha tools with popular
LLM frameworks like LangChain, LangGraph, and others.

Key Features:
- Automatic tool generation from Syntha schemas
- Framework-specific parameter conversion
- Zero-configuration setup with sensible defaults
- Extensible architecture for new frameworks
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union

from .exceptions import SynthaFrameworkError


class FrameworkAdapter(ABC):
    """
    Base class for framework adapters that generate framework-specific tools
    from Syntha's tool schemas.
    """

    def __init__(self, tool_handler, framework_name: str):
        """
        Initialize the framework adapter.

        Args:
            tool_handler: The Syntha ToolHandler instance
            framework_name: Name of the target framework
        """
        self.tool_handler = tool_handler
        self.framework_name = framework_name

    @abstractmethod
    def create_tool(self, tool_name: str, tool_schema: Dict[str, Any]) -> Any:
        """
        Create a framework-specific tool from a Syntha tool schema.

        Args:
            tool_name: Name of the tool
            tool_schema: Syntha tool schema

        Returns:
            Framework-specific tool instance
        """
        pass

    @abstractmethod
    def convert_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Syntha parameters to framework-specific format.

        Args:
            parameters: Syntha tool parameters

        Returns:
            Framework-specific parameters
        """
        pass

    def create_all_tools(self) -> List[Any]:
        """
        Create framework-specific tools for all available Syntha tools.

        Returns:
            List of framework-specific tool instances
        """
        tools = []
        schemas = self.tool_handler.get_syntha_schemas_only()

        for schema in schemas:
            tool_name = schema.get("name")
            if not tool_name:
                continue

            # Only create tools the agent has access to
            if self.tool_handler.has_tool_access(tool_name):
                try:
                    tool = self.create_tool(tool_name, schema)
                    if tool:
                        tools.append(tool)
                except Exception as e:
                    raise SynthaFrameworkError(
                        f"Failed to create {self.framework_name} tool '{tool_name}': {str(e)}",
                        framework=self.framework_name,
                        tool_name=tool_name,
                    )

        return tools

    def _create_tool_function(self, tool_name: str) -> Callable:
        """
        Create a function that calls the Syntha tool handler.

        Args:
            tool_name: Name of the tool

        Returns:
            Callable function for the tool
        """

        def tool_function(**kwargs):
            try:
                # Convert parameters if needed
                converted_kwargs = self._convert_input_parameters(tool_name, kwargs)

                # Call the Syntha tool handler
                result = self.tool_handler.handle_tool_call(
                    tool_name, **converted_kwargs
                )

                # Check if the result indicates an error
                if isinstance(result, dict) and result.get("success") is False:
                    return {
                        "success": False,
                        "error": f"Tool execution error: {result.get('error', 'Unknown error')}",
                        "tool_name": tool_name,
                        "framework": self.framework_name,
                    }

                # Convert result if needed
                return self._convert_output_result(tool_name, result)

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Tool execution error: {str(e)}",
                    "tool_name": tool_name,
                    "framework": self.framework_name,
                }

        return tool_function

    def _convert_input_parameters(
        self, tool_name: str, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert input parameters for framework-specific requirements.

        Args:
            tool_name: Name of the tool
            kwargs: Input parameters

        Returns:
            Converted parameters
        """
        # Handle common parameter conversions
        converted = kwargs.copy()

        # Convert comma-separated strings to lists for array parameters
        for key, value in kwargs.items():
            if isinstance(value, str):
                # Check if this parameter should be a list
                if self._should_convert_to_list(tool_name, key):
                    if "," in value:
                        converted[key] = [item.strip() for item in value.split(",")]
                    else:
                        # Empty string or single value becomes list with that value
                        converted[key] = [value]

        return converted

    def _convert_output_result(self, tool_name: str, result: Dict[str, Any]) -> Any:
        """
        Convert output result for framework-specific requirements.

        Args:
            tool_name: Name of the tool
            result: Tool result

        Returns:
            Converted result
        """
        # Default: return as-is, subclasses can override
        return result

    def _should_convert_to_list(self, tool_name: str, param_name: str) -> bool:
        """
        Check if a parameter should be converted from string to list.

        Args:
            tool_name: Name of the tool
            param_name: Name of the parameter

        Returns:
            True if parameter should be converted to list
        """
        # Common list parameters in Syntha tools
        list_params = {
            "get_context": ["keys"],
            "subscribe_to_topics": ["topics"],
            "unsubscribe_from_topics": ["topics"],
            # Ensure topic/subscriber strings get coerced for routing
            "push_context": ["topics", "subscribers"],
        }

        return param_name in list_params.get(tool_name, [])


class LangChainAdapter(FrameworkAdapter):
    """
    Adapter for LangChain framework integration.
    Creates LangChain-compatible BaseTool instances.
    """

    def __init__(self, tool_handler):
        super().__init__(tool_handler, "langchain")

    def create_tool(self, tool_name: str, tool_schema: Dict[str, Any]) -> Any:
        """
        Create a LangChain BaseTool from a Syntha tool schema.
        """
        try:
            # Try to import LangChain (support both legacy and new paths)
            from typing import Type

            try:
                from langchain.tools import BaseTool  # type: ignore
            except Exception:
                # LangChain >= 0.2/0.3 moved BaseTool to langchain_core.tools
                from langchain_core.tools import BaseTool  # type: ignore

            from pydantic import BaseModel, Field, create_model
        except ImportError:
            raise SynthaFrameworkError(
                "LangChain not installed or import path changed. Install/upgrade with: pip install langchain langchain-core",
                framework="langchain",
            )

        # Convert Syntha schema to Pydantic model
        pydantic_fields = self._create_pydantic_fields(
            tool_schema.get("parameters", {})
        )

        # Create dynamic Pydantic model for input
        input_model = create_model(f"{tool_name.title()}Input", **pydantic_fields)

        # Create the tool function
        tool_function = self._create_tool_function(tool_name)

        # Create LangChain tool class
        class SynthaTool(BaseTool):
            name: str = tool_name
            description: str = tool_schema.get(
                "description", f"Syntha {tool_name} tool"
            )
            args_schema: Type[BaseModel] = input_model

            def _run(self, **kwargs) -> str:
                result = tool_function(**kwargs)
                # Convert result to string for LangChain
                if isinstance(result, dict):
                    return json.dumps(result, indent=2)
                return str(result)

            async def _arun(self, **kwargs) -> str:
                # For async support, call the sync version
                return self._run(**kwargs)

        return SynthaTool()

    def _create_pydantic_fields(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Syntha parameters to Pydantic field definitions.
        """
        from pydantic import Field

        fields = {}
        properties = parameters.get("properties", {})
        required = set(parameters.get("required", []))

        for param_name, param_def in properties.items():
            param_type = param_def.get("type", "string")
            description = param_def.get("description", "")

            # Map JSON schema types to Python types
            if param_type == "array":
                field_type: Any = List[str]
            elif param_type == "boolean":
                field_type = bool
            elif param_type == "integer":
                field_type = int
            elif param_type == "number":
                field_type = float
            else:
                field_type = str

            # Create field with optional/required status
            if param_name in required:
                fields[param_name] = (field_type, Field(description=description))
            else:
                fields[param_name] = (
                    Optional[field_type],
                    Field(default=None, description=description),
                )

        return fields

    def convert_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert parameters for LangChain compatibility.
        """
        # LangChain generally works well with standard JSON schema
        return parameters


class LangGraphAdapter(FrameworkAdapter):
    """
    Adapter for LangGraph framework integration.
    Creates LangGraph-compatible tool functions.
    """

    def __init__(self, tool_handler):
        super().__init__(tool_handler, "langgraph")

    def create_tool(
        self, tool_name: str, tool_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a LangGraph tool from a Syntha tool schema.
        """
        # Create the tool function
        tool_function = self._create_tool_function(tool_name)

        # LangGraph tools are typically just dictionaries with function and schema
        return {
            "name": tool_name,
            "description": tool_schema.get("description", f"Syntha {tool_name} tool"),
            "parameters": self.convert_parameters(tool_schema.get("parameters", {})),
            "function": tool_function,
        }

    def convert_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert parameters for LangGraph compatibility.
        """
        # LangGraph typically uses standard JSON schema
        return parameters

    def _convert_output_result(self, tool_name: str, result: Dict[str, Any]) -> str:
        """
        Convert output result to string for LangGraph.
        """
        # LangGraph often expects string results
        if isinstance(result, dict):
            return json.dumps(result, indent=2)
        return str(result)


class OpenAIAdapter(FrameworkAdapter):
    """
    Adapter for OpenAI function calling format.
    Creates OpenAI-compatible function definitions.
    """

    def __init__(self, tool_handler):
        super().__init__(tool_handler, "openai")

    def create_tool(
        self, tool_name: str, tool_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an OpenAI function calling tool from a Syntha tool schema.
        """
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_schema.get(
                    "description", f"Syntha {tool_name} tool"
                ),
                "parameters": self.convert_parameters(
                    tool_schema.get("parameters", {})
                ),
            },
        }

    def convert_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert parameters for OpenAI function calling compatibility.
        """
        # OpenAI uses standard JSON schema, so return as-is
        return parameters

    def create_function_handler(self) -> Callable:
        """
        Create a function handler for OpenAI function calls.

        Returns:
            Function that can handle OpenAI function call format
        """

        def handle_function_call(
            function_name: str, arguments: Union[str, Dict[str, Any]]
        ) -> Dict[str, Any]:
            """
            Handle an OpenAI function call.

            Args:
                function_name: Name of the function to call
                arguments: Function arguments (JSON string or dict)

            Returns:
                Function result
            """
            try:
                # Parse arguments if they're a JSON string
                if isinstance(arguments, str):
                    kwargs = json.loads(arguments)
                else:
                    kwargs = arguments or {}

                # Convert parameters and call tool
                converted_kwargs = self._convert_input_parameters(function_name, kwargs)
                return self.tool_handler.handle_tool_call(
                    function_name, **converted_kwargs
                )

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Function call error: {str(e)}",
                    "function_name": function_name,
                }

        return handle_function_call


class AnthropicAdapter(FrameworkAdapter):
    """
    Adapter for Anthropic Claude tool use format.
    Creates Anthropic-compatible tool definitions.
    """

    def __init__(self, tool_handler):
        super().__init__(tool_handler, "anthropic")

    def create_tool(
        self, tool_name: str, tool_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an Anthropic tool from a Syntha tool schema.
        """
        return {
            "name": tool_name,
            "description": tool_schema.get("description", f"Syntha {tool_name} tool"),
            "input_schema": self.convert_parameters(tool_schema.get("parameters", {})),
        }

    def convert_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert parameters for Anthropic tool use compatibility.
        """
        # Anthropic uses JSON schema format
        return parameters

    def create_tool_handler(self) -> Callable:
        """
        Create a tool handler for Anthropic tool use.

        Returns:
            Function that can handle Anthropic tool use format
        """

        def handle_tool_use(
            tool_name: str, tool_input: Dict[str, Any]
        ) -> Dict[str, Any]:
            """
            Handle an Anthropic tool use call.

            Args:
                tool_name: Name of the tool to use
                tool_input: Tool input parameters

            Returns:
                Tool result
            """
            try:
                # Convert parameters and call tool
                converted_input = self._convert_input_parameters(tool_name, tool_input)
                return self.tool_handler.handle_tool_call(tool_name, **converted_input)

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Tool use error: {str(e)}",
                    "tool_name": tool_name,
                }

        return handle_tool_use


class AgnoAdapter(FrameworkAdapter):
    """
    Adapter for Agno framework integration.
    Creates Agno-compatible Function instances from Syntha tools.
    """

    def __init__(self, tool_handler):
        super().__init__(tool_handler, "agno")

    def convert_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert parameters for Agno compatibility.

        Args:
            parameters: Original parameters

        Returns:
            Converted parameters
        """
        # Agno doesn't need special parameter conversion
        return parameters

    def create_tool(self, tool_name: str, tool_schema: Dict[str, Any]) -> Any:
        """
        Create an Agno Function from a Syntha tool schema.
        """
        try:
            from typing import Any as AnyType
            from typing import Optional

            from agno.tools import Function
        except ImportError:
            raise SynthaFrameworkError(
                "Agno not installed. Install with: pip install agno",
                framework="agno",
            )

        # Create the core Syntha-bound callable (handles conversion + tool dispatch)
        tool_function = self._create_tool_function(tool_name)

        # Extract parameters from schema
        parameters = tool_schema.get("parameters", {})
        properties = parameters.get("properties", {})
        required = set(parameters.get("required", []))

        # Build an explicit-signature wrapper so Agno can introspect parameters.
        # Many frameworks rely on inspect.signature rather than relying on **kwargs.
        param_names = list(properties.keys())

        # Helper that the dynamic function will call
        def _invoke_syntha_with_filtered_kwargs(**all_kwargs):
            try:
                # Only forward provided (non-None) arguments
                forwarded = {k: v for k, v in all_kwargs.items() if v is not None}
                # Preserve Agno-specific expectation: convert string -> list for list params
                for k, v in list(forwarded.items()):
                    if self._should_convert_to_list(tool_name, k):
                        if isinstance(v, str):
                            forwarded[k] = [v]
                result = tool_function(**forwarded)
                if isinstance(result, dict):
                    return json.dumps(result, indent=2)
                return str(result)
            except Exception as e:  # pragma: no cover - defensive
                return f"Error executing {tool_name}: {str(e)}"

        # Dynamically create a function with explicit parameters matching the schema
        # Example generated signature: def get_context(keys=None, default_value=None):
        params_signature_src_parts = []
        for pname in param_names:
            # Optional parameters default to None; required have no default
            if pname in required:
                params_signature_src_parts.append(f"{pname}")
            else:
                params_signature_src_parts.append(f"{pname}=None")
        params_signature_src = ", ".join(params_signature_src_parts)

        func_name = tool_name
        func_doc = tool_schema.get("description", f"Syntha {tool_name} tool")

        # Compose the source of the dynamic wrapper function
        src_lines = [
            f"def {func_name}({params_signature_src}):",
            "\tkwargs = {}",
        ]
        for pname in param_names:
            src_lines.append(f"\tkwargs['{pname}'] = {pname}")
        src_lines.append("\treturn _invoke_syntha_with_filtered_kwargs(**kwargs)")
        src_code = "\n".join(src_lines)

        namespace: Dict[str, Any] = {
            "_invoke_syntha_with_filtered_kwargs": _invoke_syntha_with_filtered_kwargs
        }
        exec(src_code, namespace)  # nosec - controlled input from trusted schemas
        agno_tool_wrapper = namespace[func_name]

        # Attach metadata
        agno_tool_wrapper.__name__ = tool_name
        agno_tool_wrapper.__doc__ = func_doc

        # Set function attributes for Agno
        agno_tool_wrapper.__name__ = tool_name
        agno_tool_wrapper.__doc__ = tool_schema.get(
            "description", f"Syntha {tool_name} tool"
        )

        # Add parameter annotations (helps frameworks generate schemas)
        annotations: Dict[str, Any] = {}
        for param_name, param_def in properties.items():
            param_type = param_def.get("type", "string")

            # Map JSON schema types to Python types
            if param_type == "array":
                python_type: Any = List[str]
            elif param_type == "boolean":
                python_type = bool
            elif param_type == "integer":
                python_type = int
            elif param_type == "number":
                python_type = float
            else:
                python_type = str

            # Make optional if not required
            if param_name not in required:
                python_type = Optional[python_type]

            annotations[param_name] = python_type

        # Set return type annotation
        annotations["return"] = str
        agno_tool_wrapper.__annotations__ = annotations

        # Create Agno Function from the wrapper; include name and description where supported
        try:
            return Function.from_callable(agno_tool_wrapper, name=tool_name, description=func_doc, strict=False)  # type: ignore[arg-type]
        except TypeError:
            # Older Agno versions may not support description param
            return Function.from_callable(
                agno_tool_wrapper, name=tool_name, strict=False
            )

    def create_tools(self, tools: Optional[List[str]] = None) -> List[Any]:
        """
        Create multiple Agno Functions from Syntha tool schemas.

        Args:
            tools: Optional list of tool names to create. If None, creates all tools.

        Returns:
            List of Agno Function instances
        """
        available_tools = self.tool_handler.get_available_tools()

        if tools is not None:
            # Validate requested tools exist
            invalid_tools = set(tools) - set(available_tools)
            if invalid_tools:
                raise SynthaFrameworkError(
                    f"Unknown tools: {invalid_tools}. Available tools: {available_tools}",
                    framework=self.framework_name,
                )

        # Get all schemas and filter by requested tools and access control
        schemas = self.tool_handler.get_syntha_schemas_only()
        agno_tools = []

        for schema in schemas:
            tool_name = schema.get("name")
            if not tool_name:
                continue

            # Skip if specific tools requested and this isn't one of them
            if tools is not None and tool_name not in tools:
                continue

            # Only create tools the agent has access to
            if self.tool_handler.has_tool_access(tool_name):
                try:
                    agno_tool = self.create_tool(tool_name, schema)
                    agno_tools.append(agno_tool)
                except Exception as e:
                    # Log error but continue with other tools
                    print(f"Warning: Failed to create Agno tool '{tool_name}': {e}")
                    continue

        return agno_tools


# Registry of available adapters
FRAMEWORK_ADAPTERS = {
    "langchain": LangChainAdapter,
    "langgraph": LangGraphAdapter,
    "openai": OpenAIAdapter,
    "anthropic": AnthropicAdapter,
    "agno": AgnoAdapter,
}


def get_supported_frameworks() -> List[str]:
    """
    Get list of supported framework names.

    Returns:
        List of supported framework names
    """
    return list(FRAMEWORK_ADAPTERS.keys())


def create_framework_adapter(framework_name: str, tool_handler) -> FrameworkAdapter:
    """
    Create a framework adapter for the specified framework.

    Args:
        framework_name: Name of the framework
        tool_handler: Syntha ToolHandler instance

    Returns:
        Framework adapter instance

    Raises:
        SynthaFrameworkError: If framework is not supported
    """
    if framework_name not in FRAMEWORK_ADAPTERS:
        supported = list(FRAMEWORK_ADAPTERS.keys())
        raise SynthaFrameworkError(
            f"Unsupported framework '{framework_name}'. Supported frameworks: {supported}",
            framework=framework_name,
        )

    adapter_class = FRAMEWORK_ADAPTERS[framework_name]
    return adapter_class(tool_handler)  # type: ignore

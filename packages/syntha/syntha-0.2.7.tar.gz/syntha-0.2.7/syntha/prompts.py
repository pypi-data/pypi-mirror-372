"""
Prompt Injection Builders for Syntha Context Framework.

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

Functions to build system and message prompts that inject context
from the ContextMesh into agent conversations.
"""

import json
from typing import Any, Dict, List, Optional

from .context import ContextMesh


def _format_context_value(value: Any) -> str:
    """Format a context value for prompt injection."""
    if isinstance(value, str):
        return value
    elif isinstance(value, (dict, list)):
        return json.dumps(value, indent=2)
    else:
        return str(value)


def build_system_prompt(
    agent_name: str,
    context_mesh: ContextMesh,
    template: Optional[str] = None,
    include_context_header: bool = True,
    prepend_to_existing: bool = False,
    existing_prompt: Optional[str] = None,
) -> str:
    """
    Build a system prompt with long-term context injection.

    This function retrieves all context accessible by the specified agent
    and formats it for injection into the system prompt.

    Args:
        agent_name: Name of the agent requesting the prompt
        context_mesh: The ContextMesh instance to pull context from
        template: Optional custom template. Use {context} placeholder for injection.
        include_context_header: Whether to include "[Context]" header
        prepend_to_existing: Whether to add context to an existing prompt vs replace
        existing_prompt: Existing system prompt to augment (if prepend_to_existing=True)

    Returns:
        Formatted system prompt with injected context
    """
    # Get all accessible context for this agent
    context_data = context_mesh.get_all_for_agent(agent_name)

    if not context_data:
        # No context available
        if prepend_to_existing and existing_prompt:
            return existing_prompt
        if template:
            return template.format(context="")
        return existing_prompt or ""

    # Format context for injection
    context_lines = []
    if include_context_header:
        context_lines.append("[Context]")

    for key, value in context_data.items():
        formatted_value = _format_context_value(value)
        # Create human-readable key name
        readable_key = key.replace("_", " ").title()
        context_lines.append(f"{readable_key}: {formatted_value}")

    context_text = "\n".join(context_lines)

    # Handle different integration modes
    if prepend_to_existing and existing_prompt:
        # Add context before existing prompt
        return f"{context_text}\n\n{existing_prompt}"
    elif template:
        # Use custom template
        return template.format(context=context_text)
    elif existing_prompt:
        # Append to existing prompt
        return f"{existing_prompt}\n\n{context_text}"
    else:
        # Just return context
        return context_text


def inject_context_into_prompt(
    existing_prompt: str,
    agent_name: str,
    context_mesh: ContextMesh,
    placement: str = "prepend",
    separator: str = "\n\n",
) -> str:
    """
    Inject context into an existing prompt without replacing it.

    Args:
        existing_prompt: The user's existing system prompt
        agent_name: Name of the agent requesting the prompt
        context_mesh: The ContextMesh instance to pull context from
        placement: Where to place context ("prepend", "append", or "replace_placeholder")
        separator: Text to separate context from existing prompt

    Returns:
        Existing prompt with context injected
    """
    context_data = context_mesh.get_all_for_agent(agent_name)

    if not context_data:
        return existing_prompt

    # Format context
    context_lines = ["[Shared Context]"]
    for key, value in context_data.items():
        formatted_value = _format_context_value(value)
        readable_key = key.replace("_", " ").title()
        context_lines.append(f"{readable_key}: {formatted_value}")

    context_text = "\n".join(context_lines)

    if placement == "prepend":
        return f"{context_text}{separator}{existing_prompt}"
    elif placement == "append":
        return f"{existing_prompt}{separator}{context_text}"
    elif placement == "replace_placeholder":
        # Look for {context} or {{context}} placeholder
        if "{context}" in existing_prompt:
            return existing_prompt.format(context=context_text)
        elif "{{context}}" in existing_prompt:
            return existing_prompt.replace("{{context}}", context_text)
        else:
            # No placeholder found, prepend by default
            return f"{context_text}{separator}{existing_prompt}"
    else:
        raise ValueError(f"Invalid placement option: {placement}")


def build_message_prompt(
    agent_name: str,
    context_mesh: ContextMesh,
    template: Optional[str] = None,
    include_context_header: bool = True,
    recent_only: bool = False,
    max_age_seconds: Optional[float] = None,
) -> str:
    """
    Build a message prompt with short-term/recent context injection.

    This can be used for injecting recent context updates into user messages
    or for providing context that should appear in the conversation flow.

    Args:
        agent_name: Name of the agent requesting the prompt
        context_mesh: The ContextMesh instance to pull context from
        template: Optional custom template. Use {context} placeholder for injection.
        include_context_header: Whether to include "[Context Update]" header
        recent_only: Whether to only include recently added context
        max_age_seconds: Maximum age of context to include (if recent_only=True)

    Returns:
        Formatted message prompt with injected context
    """
    # Get all accessible context for this agent
    context_data = context_mesh.get_all_for_agent(agent_name)

    # Note: recent_only filtering could be implemented when ContextMesh tracks timestamps
    if recent_only and max_age_seconds:
        # For now, we return all context since timestamp tracking is not implemented
        # Future enhancement: Filter context based on creation/update timestamps
        pass

    if not context_data:
        # No context available
        if template:
            return template.format(context="")
        return ""

    # Format context for injection
    context_lines = []
    if include_context_header:
        context_lines.append("[Context Update]")

    for key, value in context_data.items():
        formatted_value = _format_context_value(value)
        # Create human-readable key name
        readable_key = key.replace("_", " ").title()
        context_lines.append(f"{readable_key}: {formatted_value}")

    context_text = "\n".join(context_lines)

    if template:
        return template.format(context=context_text)

    return context_text


def build_custom_prompt(
    agent_name: str,
    context_mesh: ContextMesh,
    keys: List[str],
    template: str,
    fallback_text: str = "",
) -> str:
    """
    Build a custom prompt with specific context keys.

    Args:
        agent_name: Name of the agent requesting the prompt
        context_mesh: The ContextMesh instance to pull context from
        keys: Specific context keys to include
        template: Template string with {key_name} placeholders
        fallback_text: Text to use if a key is not accessible

    Returns:
        Formatted prompt with specific context injected
    """
    # Build context dictionary for template formatting
    template_data = {}

    for key in keys:
        value = context_mesh.get(key, agent_name)
        if value is not None:
            template_data[key] = _format_context_value(value)
        else:
            template_data[key] = fallback_text

    try:
        return template.format(**template_data)
    except KeyError as e:
        raise ValueError(f"Template contains placeholder {e} not found in keys: {keys}")


# Convenience templates for common use cases
SYSTEM_PROMPT_TEMPLATES = {
    "basic": """You are an AI assistant with access to shared context.

{context}

Use this context to inform your responses and maintain consistency across conversations.""",
    "agent_specific": """You are {agent_name}, an AI agent in a multi-agent system.

{context}

Your role is to use this shared context to collaborate effectively with other agents.""",
    "context_aware": """You have access to the following shared context:

{context}

Always consider this context when responding and update it as needed through tool calls.""",
}

MESSAGE_PROMPT_TEMPLATES = {
    "update": """
{context}

Please consider this updated context for the following request:""",
    "reminder": """
Reminder of current context:
{context}

Now, please proceed with:""",
    "context_only": "{context}",
}

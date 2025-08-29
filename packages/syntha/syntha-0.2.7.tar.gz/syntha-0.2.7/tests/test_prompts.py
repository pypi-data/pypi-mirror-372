"""
Tests for Syntha prompt builders.
"""

import pytest

from syntha.context import ContextMesh
from syntha.prompts import (
    SYSTEM_PROMPT_TEMPLATES,
    build_custom_prompt,
    build_message_prompt,
    build_system_prompt,
)


class TestPromptBuilders:
    """Test prompt building functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()

        # Add test context
        self.mesh.push("company_vision", "To democratize AI", subscribers=[])
        self.mesh.push(
            "campaign",
            {"name": "Launch", "budget": 10000},
            subscribers=["MarketingBot"],
        )
        self.mesh.push("private_data", "secret", subscribers=["Agent1"])

    def test_build_system_prompt_basic(self):
        """Test basic system prompt building."""
        prompt = build_system_prompt("MarketingBot", self.mesh)

        assert "[Context]" in prompt
        assert "Company Vision: To democratize AI" in prompt
        assert "Campaign:" in prompt
        assert "Launch" in prompt
        assert "secret" not in prompt  # Private data not accessible

    def test_build_system_prompt_with_template(self):
        """Test system prompt with custom template."""
        template = "You are an AI agent.\n{context}\nPlease help the user."
        prompt = build_system_prompt("MarketingBot", self.mesh, template=template)

        assert "You are an AI agent." in prompt
        assert "Please help the user." in prompt
        assert "Company Vision" in prompt

    def test_build_system_prompt_no_context(self):
        """Test system prompt when agent has no accessible context."""
        # Create a fresh mesh with no global context (use temporary database)
        import os
        import tempfile

        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()

        try:
            empty_mesh = ContextMesh(db_path=temp_db.name)
            empty_mesh.push("private_only", "secret", subscribers=["OtherAgent"])

            prompt = build_system_prompt("UnknownAgent", empty_mesh)
            assert prompt == ""

            # With template
            template = "Default prompt: {context}"
            prompt = build_system_prompt("UnknownAgent", empty_mesh, template=template)
            assert prompt == "Default prompt: "
        finally:
            # Clean up
            if os.path.exists(temp_db.name):
                try:
                    os.unlink(temp_db.name)
                except PermissionError:
                    pass  # Ignore on Windows if file is still locked

    def test_build_message_prompt(self):
        """Test message prompt building."""
        prompt = build_message_prompt("MarketingBot", self.mesh)

        assert "[Context Update]" in prompt
        assert "Company Vision" in prompt
        assert "Campaign" in prompt

    def test_build_custom_prompt(self):
        """Test custom prompt with specific keys."""
        template = "Vision: {company_vision}\nCampaign: {campaign}"
        prompt = build_custom_prompt(
            "MarketingBot", self.mesh, ["company_vision", "campaign"], template
        )

        assert "Vision: To democratize AI" in prompt
        assert "Campaign:" in prompt
        assert "Launch" in prompt

    def test_build_custom_prompt_with_fallback(self):
        """Test custom prompt with inaccessible keys."""
        template = "Vision: {company_vision}\nSecret: {private_data}"
        prompt = build_custom_prompt(
            "MarketingBot",
            self.mesh,
            ["company_vision", "private_data"],
            template,
            fallback_text="[NOT AVAILABLE]",
        )

        assert "Vision: To democratize AI" in prompt
        assert "Secret: [NOT AVAILABLE]" in prompt

    def test_system_prompt_templates(self):
        """Test predefined system prompt templates."""
        template = SYSTEM_PROMPT_TEMPLATES["basic"]
        prompt = build_system_prompt("MarketingBot", self.mesh, template=template)

        assert "You are an AI assistant" in prompt
        assert "shared context" in prompt
        assert "Company Vision" in prompt

    def test_context_formatting(self):
        """Test different context value formatting."""
        # Test with different data types
        self.mesh.push("string_value", "simple string")
        self.mesh.push("dict_value", {"key": "value", "nested": {"deep": "data"}})
        self.mesh.push("list_value", ["item1", "item2", "item3"])
        self.mesh.push("number_value", 42)

        prompt = build_system_prompt("TestAgent", self.mesh)

        assert "String Value: simple string" in prompt
        assert "Dict Value:" in prompt
        assert '"key": "value"' in prompt  # JSON formatting
        assert "List Value:" in prompt
        assert '"item1"' in prompt  # JSON formatting
        assert "Number Value: 42" in prompt

    def test_include_context_header_option(self):
        """Test controlling context header inclusion."""
        prompt_with_header = build_system_prompt(
            "MarketingBot", self.mesh, include_context_header=True
        )
        prompt_without_header = build_system_prompt(
            "MarketingBot", self.mesh, include_context_header=False
        )

        assert "[Context]" in prompt_with_header
        assert "[Context]" not in prompt_without_header
        assert "Company Vision" in prompt_without_header  # Content still there

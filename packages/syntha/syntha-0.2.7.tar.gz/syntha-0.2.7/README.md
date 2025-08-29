# Syntha SDK

The context-based multi‑agent framework. Build agents that share, route, and persist context — with first‑class tooling for prompts, tools, and popular LLM frameworks.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation](https://img.shields.io/badge/docs-available-blue.svg)](https://doc.syntha.ca)

---

## Why Syntha

- Context Mesh with topic routing and user isolation
- ToolHandler with adapters (OpenAI, Anthropic, LangChain, Agno)
- Prompt builders for system and message prompts
- Pluggable persistence (SQLite, PostgreSQL)
- Lightweight, framework‑agnostic, production‑ready

## Install

```bash
pip install syntha
```

## 60‑second Quick Start

```python
from syntha import ContextMesh, ToolHandler, build_system_prompt

# 1) Shared context, isolated per user
context = ContextMesh(user_id="demo_user")

# 2) Agents interact via tools (no manual data passing)
handler = ToolHandler(context, "AssistantAgent")
context.push("project", "AI Customer Support")
context.push("status", "active", topics=["support"])  # topic‑routed

# 3) Context‑aware prompts for your LLM
system_prompt = build_system_prompt("AssistantAgent", context)
print(system_prompt[:200] + "...")
```

## Framework Integrations

- OpenAI function calling: `handler.get_openai_functions()`
- Anthropic tool use: `handler.get_anthropic_tools()`
- LangChain BaseTool: `handler.get_langchain_tools()`
- Agno Functions: `handler.get_tools_for_framework("agno")`

See the docs for concise, copy‑paste examples.

### Agno in 30 seconds

```python
from syntha import ContextMesh, ToolHandler

mesh = ContextMesh(user_id="demo")
handler = ToolHandler(mesh, agent_name="Assistant")
agno_tools = handler.get_tools_for_framework("agno")

try:
    from agno.agent import Agent
    agent = Agent(
        name="Assistant",
        tools=agno_tools,
        instructions="Use tools to read/write context.",
        model="gpt-4o",
    )
    # response = agent.run("List context keys and fetch 'project'")
except ImportError:
    print("pip install agno to enable Agent integration")
```

## Documentation

- Docs: https://doc.syntha.ca
- Quick Start: https://doc.syntha.ca/user-guide/introduction/quick-start/
- Examples: https://doc.syntha.ca/examples/overview/
- API Reference: https://doc.syntha.ca/api/overview/

## License

Apache 2.0 © Syntha. See [LICENSE](LICENSE).

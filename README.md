# Debate AI - Multi-Agent Debate System

An MCP (Model Context Protocol) server that enables multiple AI agents to debate and reach consensus on topics or implementation decisions.

## Overview

When you ask a question or propose an implementation, this system:
1. Multiple agents provide their initial perspectives
2. Agents review each other's responses and provide feedback
3. Agents revise their positions based on feedback
4. The process continues until all agents reach consensus

## Architecture

- **Main Agent**: Claude (when used via Claude Desktop)
- **Debate Agents**: Configurable AI agents with different roles/perspectives
- **Protocol**: MCP for integration with Claude Desktop
- **Agent SDK**: Supports multiple LLM providers (Anthropic, OpenAI, etc.)

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

## Usage

### As MCP Server with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "debate-ai": {
      "command": "python",
      "args": ["/path/to/debate_ai/src/server.py"]
    }
  }
}
```

### Example

```
User: Should we use microservices or monolith for this project?

Debate AI will:
- Agent 1 (Architect): Provides initial analysis
- Agent 2 (DevOps): Reviews and provides feedback
- Agent 3 (Developer): Reviews both perspectives
- Agents iterate until consensus is reached
```

## Development

This project follows TDD principles. See `plain.md` for the test plan.

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Format code
black src tests

# Type checking
mypy src
```

## License

MIT

# LLM AnyGate

A flexible gateway for connecting and managing multiple LLM providers.

## Features

- **Multiple Provider Support**: Seamlessly switch between OpenAI, Anthropic, and other LLM providers
- **Unified Interface**: Single API for all providers
- **Configuration Management**: Easy configuration through files or environment variables
- **Async Support**: Built with async/await for high performance
- **Extensible**: Easy to add new providers
- **Type Safe**: Full type hints and validation with Pydantic

## Quick Start

```python
from llm_anygate import Gateway, OpenAIProvider, AnthropicProvider

# Create gateway
gateway = Gateway()

# Register providers
gateway.register_provider("openai", OpenAIProvider(api_key="your-key"))
gateway.register_provider("anthropic", AnthropicProvider(api_key="your-key"))

# Use a provider
provider = gateway.get_provider("openai")
response = await provider.complete("Hello, world!")
```

## Installation

```bash
pip install llm-anygate
```

Or with pixi for development:

```bash
pixi install
pixi shell
```

## Documentation

- [Getting Started](getting-started/installation.md) - Installation and setup
- [User Guide](guide/basic-usage.md) - How to use LLM AnyGate
- [API Reference](api/gateway.md) - Detailed API documentation
- [Development](development/contributing.md) - Contributing guidelines

## License

MIT License - see [LICENSE](https://github.com/igamenovoer/llm-anygate/blob/main/LICENSE) for details.
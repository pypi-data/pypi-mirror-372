# LLM AnyGate

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://igamenovoer.github.io/llm-anygate/)

A powerful CLI tool that generates LiteLLM proxy projects from simple YAML configurations. Designed to free users from understanding the complexities of the LiteLLM library and quickly create local LLM proxies for use with various AI coding tools.

## Overview

LLM AnyGate simplifies the process of setting up LiteLLM proxy servers by providing a simple command-line interface to generate complete, ready-to-run proxy projects with minimal configuration.

## Key Features

🚀 **Quick Setup** - Create a fully configured LiteLLM proxy project with one command  
📝 **Simple Configuration** - Use minimal YAML config instead of complex LiteLLM settings (or use defaults)  
🔧 **Zero Database** - Generated proxies run statelessly without database requirements  
🖥️ **Cross-Platform** - Works on Windows, macOS, and Linux with unified CLI commands  
🎯 **Production Ready** - Generates complete project with config, environment templates, and documentation  
📦 **PyPI Package** - Easy installation via pip from official PyPI repository

## Prerequisites

- **Python 3.11 or higher**
- **LiteLLM CLI tool** (for running generated proxies)
  ```bash
  # Recommended: Install using uv
  uv tool install 'litellm[proxy]'
  
  # Alternative: Install with pip
  pip install 'litellm[proxy]'
  ```

## Installation

### From PyPI

```bash
pip install llm-anygate
```

### For Development (with Pixi)

```bash
# Clone the repository
git clone https://github.com/igamenovoer/llm-anygate.git
cd llm-anygate

# Initialize submodules
git submodule update --init --recursive

# Setup development environment with Pixi
pixi install
pixi shell
```

## Quick Start

### Step 1: Generate Proxy Project (Optional Configuration)

Use the CLI to generate a complete LiteLLM proxy project. The model configuration is optional:

```bash
# With default configuration (uses gpt-4o with OPENAI_API_KEY)
llm-anygate-cli create --project my-proxy

# With custom configuration file
llm-anygate-cli create \
  --project my-proxy \
  --model-config model-config.yaml \
  --port 4567 \
  --master-key "sk-my-secure-key"
```

If you want to use a custom model configuration, create a YAML file (`model-config.yaml`):

```yaml
model_list:                                # Array of available models for the proxy
  - model_name: gpt-4o                     # Alias name that clients use to request this model
    litellm_params:                        # LiteLLM-specific parameters for this model
      model: openai/gpt-4o                 # Provider prefix + actual model ID
      api_base: https://api.openai.com/v1  # API endpoint URL (optional for OpenAI)
      api_key: os.environ/OPENAI_API_KEY   # References environment variable

  - model_name: claude-3-5-sonnet          # Alias for Anthropic Claude model
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022  # Anthropic provider + model version
      api_key: os.environ/ANTHROPIC_API_KEY        # Environment variable reference
      
  - model_name: gemini-pro                 # Alias for Google Gemini model
    litellm_params:
      model: gemini/gemini-pro             # Google provider + model name
      api_key: os.environ/GEMINI_API_KEY   # Environment variable reference
```

### Step 2: Configure Environment

```bash
cd my-proxy

# Copy and configure environment variables
cp env.example .env
# Edit .env and add your API keys
```

### Step 3: Start the Proxy Server

```bash
# Start specifying the project directory
llm-anygate-cli start --project my-proxy

# Or start from within the project directory
cd my-proxy
llm-anygate-cli start
```

### Step 4: Use the Proxy

Your proxy is now running at `http://localhost:4567` with an OpenAI-compatible API:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4567/v1",
    api_key="sk-my-secure-key"
)

response = client.chat.completions.create(
    model="gpt-4o",  # or any model from your config
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Generated Project Structure

The CLI generates a complete project with:

```
my-proxy/
├── config.yaml         # Full LiteLLM configuration
├── env.example         # Template for API keys
├── anygate.yaml       # Project configuration for llm-anygate-cli
└── README.md          # Project documentation
```

## CLI Usage

### Create Command

```bash
llm-anygate-cli create [options]
```

**Options:**
- `--project <dir>` (required) - Directory to create the project in
- `--model-config <file>` (optional) - Path to your model configuration YAML (generates default gpt-4o config if not provided)
- `--port <number>` - Port for the proxy server (default: 4567)
- `--master-key <key>` - Master key for API authentication (default: sk-dummy)

### Start Command

```bash
llm-anygate-cli start [options]
```

**Options:**
- `--project <dir>` (optional) - Project directory (default: current directory)
- `--port <number>` (optional) - Override port from project configuration
- `--master-key <key>` (optional) - Override master key from project configuration

The start command reads configuration from `anygate.yaml` in the project directory.

### Examples

```bash
# Create with default configuration
llm-anygate-cli create --project my-proxy

# Create with custom configuration
llm-anygate-cli create \
  --project /path/to/my-llm-proxy \
  --model-config configs/models.yaml \
  --port 8080 \
  --master-key "sk-production-key-here"

# Start proxy from project directory
cd my-proxy
llm-anygate-cli start

# Start proxy with overrides
llm-anygate-cli start --port 3000 --master-key "sk-new-key"
```

## Model Configuration Format

The model configuration is a simple YAML file with a `model_list` array:

```yaml
model_list:
  - model_name: <name-for-your-app>
    litellm_params:
      model: <provider>/<model-id>
      api_base: <api-endpoint>  # Optional
      api_key: os.environ/<ENV_VAR_NAME>
      # Additional parameters as needed
```

### Supported Providers

- OpenAI and OpenAI-compatible endpoints
- Anthropic (Claude)
- Google (Gemini/Vertex)
- Azure OpenAI
- Local models (Ollama, etc.)
- Any provider supported by LiteLLM

## Security Notes

- Generated projects include `env.example` as a template for API keys
- Never commit `.env` files with actual API keys
- Always use secure master keys in production

## Contributing

Contributions are welcome! Please see our [Contributing Guide](docs/development/contributing.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [OmegaConf](https://github.com/omry/omegaconf) for robust configuration handling
- Uses [Pixi](https://pixi.sh/) for environment management
- Generates configurations for [LiteLLM](https://github.com/BerriAI/litellm)
- Project structure based on [magic-context](https://github.com/igamenovoer/magic-context) templates

## Contact

- GitHub: [@igamenovoer](https://github.com/igamenovoer)
- Issues: [GitHub Issues](https://github.com/igamenovoer/llm-anygate/issues)

## Support

For questions, issues, or feature requests, please open an issue on GitHub.
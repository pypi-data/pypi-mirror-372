# LLM AnyGate

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://igamenovoer.github.io/llm-anygate/)

A powerful CLI tool that generates LiteLLM proxy projects from simple YAML configurations. Designed to free users from understanding the complexities of the LiteLLM library and quickly create local LLM proxies for use with various AI coding tools.

## Overview

LLM AnyGate simplifies the process of setting up LiteLLM proxy servers by providing a simple command-line interface to generate complete, ready-to-run proxy projects with minimal configuration.

## Key Features

🚀 **Quick Setup** - Create a fully configured LiteLLM proxy project with one command  
📝 **Simple Configuration** - Use minimal YAML config instead of complex LiteLLM settings  
🔧 **Zero Database** - Generated proxies run statelessly without database requirements  
🖥️ **Cross-Platform** - Includes both shell scripts (Unix/macOS) and PowerShell (Windows)  
🎯 **Production Ready** - Generates complete project with scripts, config, and documentation

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

### Step 1: Create a Model Configuration

Create a simple YAML file with your model configurations (`model-config.yaml`):

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_base: https://api.openai.com/v1
      api_key: os.environ/OPENAI_API_KEY

  - model_name: claude-3-5-sonnet
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY
      
  - model_name: gemini-pro
    litellm_params:
      model: gemini/gemini-pro
      api_key: os.environ/GEMINI_API_KEY
```

### Step 2: Generate Proxy Project

Use the CLI to generate a complete LiteLLM proxy project:

```bash
llm-anygate-cli create \
  --project my-proxy \
  --model-config model-config.yaml \
  --port 4567 \
  --master-key "sk-my-secure-key"
```

### Step 3: Start the Proxy Server

```bash
cd my-proxy

# Copy and configure environment variables
cp .env.template .env
# Edit .env and add your API keys

# Start the proxy
./start-proxy.sh    # On Unix/macOS
.\start-proxy.ps1   # On Windows
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
├── .env.template       # Template for API keys
├── README.md          # Project documentation
├── start-proxy.sh     # Unix/macOS start script
├── start-proxy.ps1    # Windows start script
└── .gitignore         # Git ignore rules
```

## CLI Usage

### Create Command

```bash
llm-anygate-cli create [options]
```

**Options:**
- `--project <dir>` (required) - Directory to create the project in
- `--model-config <file>` (required) - Path to your model configuration YAML
- `--port <number>` - Port for the proxy server (default: 4567)
- `--master-key <key>` - Master key for API authentication (default: sk-dummy)

### Example with Custom Settings

```bash
llm-anygate-cli create \
  --project /path/to/my-llm-proxy \
  --model-config configs/models.yaml \
  --port 8080 \
  --master-key "sk-production-key-here"
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

## Why LLM AnyGate?

### The Problem
Setting up LiteLLM proxy servers requires understanding complex configurations, database setups, and various deployment options. This complexity is a barrier for developers who just want a simple proxy for their AI tools.

### The Solution
LLM AnyGate provides a simple CLI that generates everything you need:
- ✅ No database required (stateless operation)
- ✅ Minimal configuration needed
- ✅ Cross-platform start scripts
- ✅ Environment variable management
- ✅ Production-ready settings

## Development

### Project Structure

```
llm-anygate/
├── src/llm_anygate/       # Main package source code
│   ├── cli_tool.py        # CLI interface
│   ├── config_converter.py # Config conversion logic
│   ├── proxy_generator.py  # Project generation
│   └── templates.py        # File templates
├── tests/                  # Test suite
├── docs/                   # Documentation
└── context/                # AI collaboration workspace
```

### Running Tests

```bash
pixi run test           # Run tests
pixi run test-cov       # Run tests with coverage
```

### Code Quality

```bash
pixi run lint           # Run linting
pixi run format         # Format code
pixi run typecheck      # Type checking
pixi run quality        # Run all checks
```

## Roadmap

- [x] Core CLI tool implementation
- [x] LiteLLM configuration generation
- [x] Cross-platform start scripts
- [x] Environment variable management
- [ ] Docker composition generator
- [ ] Provider connectivity testing
- [ ] Configuration validation
- [ ] Web UI for configuration
- [ ] Metrics and monitoring integration
- [ ] Advanced routing and load balancing

## Requirements

- Python 3.11 or higher
- LiteLLM (for running generated proxies)
  ```bash
  pip install 'litellm[proxy]'
  ```

## Security Notes

- Generated projects include `.env.template` for API keys
- Never commit `.env` files with actual API keys
- Always use secure master keys in production
- Generated `.gitignore` excludes sensitive files

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
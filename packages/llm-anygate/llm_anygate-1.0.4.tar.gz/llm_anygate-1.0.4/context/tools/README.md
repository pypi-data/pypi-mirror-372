# Development Tools

## Purpose

This directory contains custom scripts, utilities, and development aids specific to the LLM AnyGate project. These tools automate common tasks, assist with development workflows, and improve productivity.

## Tool Categories

### Build Tools
- Package building scripts
- Version management
- Release automation

### Development Tools
- Code generators
- Boilerplate creators
- Migration scripts

### Testing Tools
- Test data generators
- Mock servers
- Performance profilers

### Utility Scripts
- Configuration validators
- Log analyzers
- Debug helpers

## Tool Structure

```
tools/
├── build/          # Build and packaging scripts
├── dev/            # Development utilities
├── test/           # Testing helpers
├── scripts/        # General purpose scripts
└── templates/      # Code generation templates
```

## Tool Documentation Template

```python
#!/usr/bin/env python
"""
Tool: [Tool Name]

Purpose: [What this tool does]
Usage: python tools/[script].py [arguments]
Dependencies: [Required packages]

Example:
    python tools/generate_provider.py --name CustomProvider
"""

import argparse
import sys
from typing import Optional

def main(args: Optional[list] = None) -> int:
    """Main entry point for the tool."""
    parser = argparse.ArgumentParser(description='Tool description')
    parser.add_argument('--option', help='Option description')
    
    parsed_args = parser.parse_args(args)
    
    # Tool implementation
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Example Tools for LLM AnyGate

### Provider Tools
```bash
# generate_provider.py - Create new provider boilerplate
python tools/generate_provider.py --name GoogleVertex --type completion

# test_provider.py - Test provider implementation
python tools/test_provider.py --provider openai --api-key $KEY
```

### Configuration Tools
```bash
# validate_config.py - Validate YAML configuration
python tools/validate_config.py config.yaml

# generate_litellm.py - Generate LiteLLM config from YAML
python tools/generate_litellm.py --input config.yaml --output litellm.config
```

### Development Tools
```bash
# setup_dev.py - Set up development environment
python tools/setup_dev.py --create-env --install-deps

# mock_server.py - Start mock LLM server for testing
python tools/mock_server.py --port 8080 --provider openai
```

### Testing Tools
```bash
# benchmark.py - Run performance benchmarks
python tools/benchmark.py --providers all --requests 1000

# coverage_report.py - Generate coverage report
python tools/coverage_report.py --format html --threshold 80
```

## Tool Examples

### Configuration Validator
```python
# tools/validate_config.py
"""Validate LLM AnyGate configuration files."""

import yaml
from pathlib import Path
from llm_anygate.config import Config

def validate_config(config_path: Path) -> bool:
    """Validate a configuration file."""
    try:
        with open(config_path) as f:
            data = yaml.safe_load(f)
        
        config = Config(**data)
        print(f"✓ Configuration valid: {config_path}")
        return True
    except Exception as e:
        print(f"✗ Configuration invalid: {e}")
        return False
```

### Provider Generator
```python
# tools/generate_provider.py
"""Generate boilerplate for new providers."""

from pathlib import Path

TEMPLATE = '''"""
{name} Provider implementation.
"""

from llm_anygate.providers import Provider

class {name}Provider(Provider):
    """Provider for {name} API."""
    
    async def complete(self, prompt: str, **kwargs):
        # Implementation here
        pass
'''

def generate_provider(name: str):
    """Generate provider boilerplate."""
    content = TEMPLATE.format(name=name)
    path = Path(f"src/llm_anygate/providers/{name.lower()}.py")
    path.write_text(content)
    print(f"Generated: {path}")
```

## Shell Scripts

### run_tests.sh
```bash
#!/bin/bash
# Run tests with coverage
set -e

echo "Running tests..."
pixi run pytest tests/ --cov=src/llm_anygate

echo "Type checking..."
pixi run mypy src/

echo "Linting..."
pixi run ruff check src/ tests/

echo "All checks passed!"
```

## Best Practices

1. Make tools self-documenting with help text
2. Use argparse for command-line interfaces
3. Include examples in docstrings
4. Handle errors gracefully
5. Make tools idempotent when possible
6. Test tools as you would test code
7. Version tools along with the project

## Tool Requirements

Tools should be:
- **Portable**: Work across platforms
- **Documented**: Clear usage instructions
- **Tested**: Include basic tests
- **Versioned**: Track changes
- **Maintainable**: Clean, readable code
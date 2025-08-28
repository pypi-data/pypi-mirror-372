# AI Assistant Guide for LLM AnyGate

This document provides context and guidelines for AI assistants working on the LLM AnyGate project.

## Project Overview

LLM AnyGate is a flexible gateway for connecting and managing multiple LLM providers. It provides a unified interface for interacting with different AI models from providers like OpenAI, Anthropic, and others.

## Project Structure

```
llm-anygate/
├── src/llm_anygate/      # Main package source code
├── scripts/               # CLI and utility scripts
├── tests/                 # Test suite
├── docs/                  # Documentation
├── context/               # AI collaboration workspace
├── .magic-context/        # Reusable prompts and templates (submodule)
├── tmp/                   # Temporary files
└── .github/workflows/     # CI/CD automation
```

## Development Environment

This project uses **Pixi** for environment management, which combines conda and PyPI ecosystems. 

### Setup Commands
```bash
pixi install           # Install dependencies
pixi shell            # Activate environment
pixi run test         # Run tests
pixi run quality      # Run all quality checks
pixi run docs-serve   # Serve documentation locally
```

## Context Directory

The `context/` directory contains project knowledge and development history. Key directories:

- **design/** - Architecture and API specifications
- **hints/** - How-to guides and troubleshooting
- **logs/** - Development session records
- **plans/** - Implementation strategies
- **tasks/** - Current work items

See `context/README.md` for detailed information.

## Coding Standards

1. **Type Hints**: Use type hints for all function signatures
2. **Docstrings**: Write comprehensive docstrings for all public APIs
3. **Testing**: Write tests for new functionality
4. **Async First**: Use async/await for I/O operations
5. **Error Handling**: Implement proper error handling and logging

## Current Focus Areas

1. **Provider Implementation**: Completing provider integrations
2. **Configuration System**: Enhancing configuration management
3. **Documentation**: Building comprehensive documentation
4. **Testing**: Achieving high test coverage

## Key Design Decisions

- **Async Architecture**: All provider interactions are async for performance
- **Pydantic Models**: Configuration and data validation using Pydantic
- **Provider Abstraction**: Common interface for all LLM providers
- **Extensibility**: Plugin-like system for adding new providers

## Testing Guidelines

- Use `pytest` for testing
- Write unit tests for individual components
- Write integration tests for provider interactions
- Mock external API calls in tests

## Documentation

Documentation is built with MkDocs Material and deployed to GitHub Pages. When updating documentation:

1. Update markdown files in `docs/`
2. Test locally with `pixi run docs-serve`
3. Documentation auto-deploys on merge to main

## Common Tasks

### Adding a New Provider
1. Create provider class inheriting from `Provider`
2. Implement `complete()` and `get_info()` methods
3. Add tests in `tests/test_providers.py`
4. Update documentation

### Updating Configuration
1. Modify `src/llm_anygate/config.py`
2. Update schema validation
3. Add migration logic if needed
4. Update configuration documentation

## External Resources

- [Magic Context Guidelines](.magic-context/general/context-dir-guide.md)
- [Python Project Structure](.magic-context/general/pypi-project-init-guide.md)
- [Pixi Integration Guide](.magic-context/general/howto-pyproject-pixi-integration.md)

## Communication

When working on this project:
1. Log significant changes in `context/logs/`
2. Document design decisions in `context/design/`
3. Track tasks in `context/tasks/`
4. Update this file with major changes

## Questions to Consider

When implementing features, consider:
- How does this fit with the existing architecture?
- What providers need to support this feature?
- How will this affect the configuration?
- What documentation needs updating?
- What tests are needed?
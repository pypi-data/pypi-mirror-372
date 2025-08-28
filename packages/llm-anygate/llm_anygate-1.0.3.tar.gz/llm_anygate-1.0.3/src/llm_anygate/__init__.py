"""LLM AnyGate - A flexible gateway for connecting and managing multiple LLM providers."""

__version__ = "0.1.0"
__author__ = "igamenovoer"

# Always available
from llm_anygate.cli_tool import main as cli_main

__all__ = [
    "cli_main",
    "__version__",
    "__author__",
]

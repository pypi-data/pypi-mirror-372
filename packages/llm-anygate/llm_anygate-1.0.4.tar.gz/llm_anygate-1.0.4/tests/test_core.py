"""Tests for core gateway functionality."""

import pytest
from llm_anygate import Gateway, Provider, OpenAIProvider, AnthropicProvider


def test_gateway_initialization():
    """Test Gateway initialization."""
    gateway = Gateway()
    assert gateway.providers == {}
    assert gateway.list_providers() == []


def test_register_provider():
    """Test provider registration."""
    gateway = Gateway()
    provider = OpenAIProvider()
    
    gateway.register_provider("openai", provider)
    assert "openai" in gateway.list_providers()
    assert gateway.get_provider("openai") == provider


def test_get_nonexistent_provider():
    """Test getting a non-existent provider."""
    gateway = Gateway()
    assert gateway.get_provider("nonexistent") is None


def test_multiple_providers():
    """Test registering multiple providers."""
    gateway = Gateway()
    
    openai_provider = OpenAIProvider()
    anthropic_provider = AnthropicProvider()
    
    gateway.register_provider("openai", openai_provider)
    gateway.register_provider("anthropic", anthropic_provider)
    
    providers = gateway.list_providers()
    assert len(providers) == 2
    assert "openai" in providers
    assert "anthropic" in providers
"""Convert simple model config to full LiteLLM configuration using OmegaConf."""

from pathlib import Path

from omegaconf import DictConfig, OmegaConf


def convert_model_config_to_litellm(
    model_config: DictConfig, port: int = 4567, master_key: str = "sk-dummy"
) -> DictConfig:
    """Convert a simple model config to full LiteLLM configuration.

    Args:
        model_config: Simple model configuration (OmegaConf DictConfig)
        port: Port number for the proxy
        master_key: Master key for authentication

    Returns:
        Full LiteLLM configuration as DictConfig
    """
    # Create the full config structure
    litellm_config = OmegaConf.create(
        {
            # Copy model list from input
            "model_list": OmegaConf.to_container(model_config.get("model_list", [])),
            # Proxy settings
            "litellm_settings": {
                "ui": False,  # Disable admin UI to avoid DB
                "openai_compatible": True,
                "anthropic_compatible": True,
                "vertex_compatible": True,
                "drop_params": True,  # Drop unknown params instead of erroring
            },
            # General settings
            "general_settings": {
                "master_key": "os.environ/LITELLM_MASTER_KEY",  # Read from env
                "disable_spend_logs": True,  # No DB writes
                "disable_error_logs": True,  # No DB writes
                "disable_adding_master_key_hash_to_db": True,  # No DB storage
                "allow_requests_on_db_unavailable": True,  # Start without DB
                "disable_reset_budget": True,  # No scheduled DB tasks
            },
            # Router settings
            "router_settings": {
                "enable_anthropic_endpoint": True,
                "enable_vertex_endpoint": True,
                "enable_gemini_endpoint": True,
            },
        }
    )

    return litellm_config


def load_model_config(config_path: Path) -> DictConfig:
    """Load model configuration from YAML file using OmegaConf.

    Args:
        config_path: Path to the model config YAML file

    Returns:
        Model configuration as DictConfig

    Raises:
        FileNotFoundError: If config file doesn't exist
        Exception: If config file is invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Model config file not found: {config_path}")

    try:
        config = OmegaConf.load(config_path)
        if not isinstance(config, DictConfig):
            # Convert to DictConfig if needed
            config = OmegaConf.create({"model_list": config})
    except Exception as e:
        raise Exception(f"Invalid configuration in {config_path}: {e}") from e

    return config


def save_litellm_config(config: DictConfig, output_path: Path) -> None:
    """Save LiteLLM configuration to YAML file.

    Args:
        config: LiteLLM configuration (DictConfig)
        output_path: Path to save the config file
    """
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save with OmegaConf - it handles YAML serialization
    OmegaConf.save(config, output_path)


def create_full_config(
    model_config_path: Path, output_path: Path, port: int = 4567, master_key: str = "sk-dummy"
) -> None:
    """Create full LiteLLM config from model config file.

    Args:
        model_config_path: Path to input model config
        output_path: Path to save LiteLLM config
        port: Port for the proxy
        master_key: Master key for auth
    """
    # Load model config
    model_config = load_model_config(model_config_path)

    # Convert to LiteLLM config
    litellm_config = convert_model_config_to_litellm(model_config, port, master_key)

    # Save the config
    save_litellm_config(litellm_config, output_path)

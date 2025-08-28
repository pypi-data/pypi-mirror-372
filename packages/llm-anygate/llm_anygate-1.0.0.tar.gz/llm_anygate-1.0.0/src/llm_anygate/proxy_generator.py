"""Generate LiteLLM proxy project structure."""

import os
import stat
from pathlib import Path

from llm_anygate.config_converter import create_full_config
from llm_anygate.templates import (
    get_env_template,
    get_readme_template,
)


class ProxyGenerator:
    """Generator for LiteLLM proxy projects."""

    def __init__(self) -> None:
        """Initialize the proxy generator."""
        pass

    def create_project(
        self,
        project_dir: Path,
        model_config_path: Path | None,
        port: int = 4567,
        master_key: str = "sk-dummy",
    ) -> bool:
        """Create a complete LiteLLM proxy project.

        Args:
            project_dir: Directory to create the project in
            model_config_path: Path to the model config YAML (optional, generates default if None)
            port: Port for the proxy server
            master_key: Master key for authentication

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if model config exists (only if provided)
            if model_config_path and not model_config_path.exists():
                print(f"Error: Model config file not found: {model_config_path}")
                return False

            # Create project directory
            project_dir.mkdir(parents=True, exist_ok=True)
            print(f"Creating project at: {project_dir}")

            # Generate LiteLLM config
            config_path = project_dir / "config.yaml"
            print("Generating LiteLLM configuration...")
            if model_config_path:
                # Use provided model config
                create_full_config(
                    model_config_path=model_config_path,
                    output_path=config_path,
                    port=port,
                    master_key=master_key,
                )
            else:
                # Generate with default model config
                print("No model config provided, generating default configuration...")
                self._create_default_config(config_path, port, master_key)

            # Create env.example file
            env_example_path = project_dir / "env.example"
            print("Creating environment example...")
            self._create_file(env_example_path, get_env_template(master_key))

            # Create README.md
            readme_path = project_dir / "README.md"
            print("Creating README...")
            self._create_file(readme_path, get_readme_template(port, master_key))

            # Create anygate configuration
            print("Creating anygate configuration...")
            anygate_config_path = project_dir / "anygate.yaml"
            model_config_str = str(model_config_path.resolve()) if model_config_path else None
            self._create_anygate_config(
                anygate_config_path, 
                model_config_str,
                port, 
                master_key
            )

            # Create .gitignore
            gitignore_path = project_dir / ".gitignore"
            self._create_file(gitignore_path, self._get_gitignore_content())

            print(f"\nProject created successfully at: {project_dir}")
            return True

        except Exception as e:
            print(f"Error creating project: {e}")
            return False

    def _create_file(self, path: Path, content: str) -> None:
        """Create a file with the given content.

        Args:
            path: Path to the file
            content: Content to write
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _create_default_config(
        self,
        config_path: Path,
        port: int,
        master_key: str
    ) -> None:
        """Create a default minimal LiteLLM configuration.
        
        Args:
            config_path: Path to save the config file
            port: Port number for the proxy server  
            master_key: Master key for authentication
        """
        default_config = """model_list:
  # Default GPT-4 model configuration
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_base: os.environ/OPENAI_BASE_URL
      api_key: os.environ/OPENAI_API_KEY
      temperature: 1.0

# Proxy settings (keep purely format/runtime flags here; avoid UI to skip DB usage)
litellm_settings:
  # Disable admin UI -> avoids DB-backed pages / migrations
  ui: false
  # Format compatibility
  openai_compatible: true
  anthropic_compatible: true
  vertex_compatible: true
  drop_params: true  # Drop unknown params instead of erroring out

# General settings to disable database features (and supply master key)
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY   # Provide master key here (not stored in DB)
  disable_spend_logs: true                    # Do not write spend logs to DB
  disable_error_logs: true                    # Do not write error logs to DB
  disable_adding_master_key_hash_to_db: true  # Do not store master key hash in DB
  allow_requests_on_db_unavailable: true      # Start/serve even if DB missing
  disable_reset_budget: true                  # Disable scheduled budget tasks (DB)
  # (No DATABASE_URL set; proxy runs statelessly.)

# Router settings for advanced configurations
router_settings:
  # Enable different endpoint formats
  enable_anthropic_endpoint: true
  enable_vertex_endpoint: true
  enable_gemini_endpoint: true
"""
        self._create_file(config_path, default_config)
    
    def _create_anygate_config(
        self, 
        config_path: Path, 
        model_config_path: str | None, 
        port: int, 
        master_key: str
    ) -> None:
        """Create anygate.yaml configuration file.

        Args:
            config_path: Path to the anygate.yaml file
            model_config_path: Path to the original model config file (or None for default)  
            port: Port number for the proxy server
            master_key: Master key for authentication
        """
        if model_config_path:
            # Use forward slashes for YAML compatibility
            yaml_safe_path = model_config_path.replace("\\", "/")
            config_content = f"""# AnyGate Configuration
# This file stores the configuration used when creating this proxy project
# It will be used by 'llm-anygate-cli start' for default values

project:
  model_config: "{yaml_safe_path}"
  port: {port}
  master_key: "{master_key}"
"""
        else:
            config_content = f"""# AnyGate Configuration
# This file stores the configuration used when creating this proxy project
# It will be used by 'llm-anygate-cli start' for default values

project:
  model_config: null  # Using default configuration
  port: {port}
  master_key: "{master_key}"
"""
        self._create_file(config_path, config_content)

    def _make_executable(self, path: Path) -> None:
        """Make a file executable (Unix/macOS only).

        Args:
            path: Path to the file
        """
        try:
            # Get current permissions
            current_permissions = os.stat(path).st_mode
            # Add execute permission for owner, group, and others
            os.chmod(path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except Exception:
            # Ignore errors on Windows
            pass

    def _get_gitignore_content(self) -> str:
        """Get .gitignore content for the proxy project.

        Returns:
            .gitignore file content
        """
        return """.env
.env.local
*.log
__pycache__/
*.py[cod]
*$py.class
.DS_Store
Thumbs.db
"""

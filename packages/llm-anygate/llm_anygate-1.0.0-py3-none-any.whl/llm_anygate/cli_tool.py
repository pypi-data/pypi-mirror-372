"""CLI tool for setting up LiteLLM proxy projects."""

import os
import subprocess
import sys
from pathlib import Path

import click
import yaml

from llm_anygate.litellm_checker import check_litellm_installed
from llm_anygate.proxy_generator import ProxyGenerator


@click.group(name="llm-anygate-cli", invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """CLI tool for setting up LiteLLM proxy projects."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option(
    "--project",
    required=True,
    help="Project directory to create",
    type=click.Path()
)
@click.option(
    "--model-config",
    help="Path to the model configuration YAML file (optional, generates default if not provided)",
    type=click.Path(exists=True)
)
@click.option(
    "--port",
    default=4567,
    help="Port number for the proxy server",
    type=int,
    show_default=True
)
@click.option(
    "--master-key",
    default="sk-dummy",
    help="Master key for the proxy",
    show_default=True
)
def create(project: str, model_config: str | None, port: int, master_key: str) -> None:
    """Create a new LiteLLM proxy project."""
    try:
        # Check if litellm is installed
        is_installed, install_msg = check_litellm_installed()
        if not is_installed:
            click.echo(f"Warning: {install_msg}")
            click.echo("Continuing with project generation...")
            click.echo()

        # Create the generator
        generator = ProxyGenerator()

        # Generate the project
        model_config_path = Path(model_config) if model_config else None
        success = generator.create_project(
            project_dir=Path(project),
            model_config_path=model_config_path,
            port=port,
            master_key=master_key,
        )

        if success:
            click.echo(f"Successfully created LiteLLM proxy project at: {project}")
            click.echo()
            click.echo("To start the proxy server:")
            click.echo(f"  llm-anygate-cli start --project {project}")
            click.echo("  # Or from the project directory:")
            click.echo(f"  cd {project}")
            click.echo("  llm-anygate-cli start")
        else:
            click.echo("Failed to create project", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--project",
    help="Project directory containing anygate.yaml",
    type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    "--port",
    help="Port number for the proxy server (overrides anygate.yaml)",
    type=int
)
@click.option(
    "--master-key", 
    help="Master key for the proxy (overrides anygate.yaml)"
)
def start(project: str | None, port: int | None, master_key: str | None) -> None:
    """Start the LiteLLM proxy server."""
    try:
        # Determine project directory
        project_dir = Path(project) if project else Path.cwd()
            
        # Check for anygate.yaml
        anygate_config_path = project_dir / "anygate.yaml"
        if not anygate_config_path.exists():
            click.echo(f"Error: anygate.yaml not found in {project_dir}", err=True)
            click.echo("Run this command from a project directory or specify --project", err=True)
            sys.exit(1)
            
        # Read anygate.yaml configuration
        with open(anygate_config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
            
        project_config = config.get("project", {})
        
        # Use command line arguments or fall back to anygate.yaml values
        final_port = port if port is not None else project_config.get("port", 4567)
        
        # Check if litellm is installed
        is_installed, install_msg = check_litellm_installed()
        if not is_installed:
            click.echo(f"Error: {install_msg}", err=True)
            sys.exit(1)
            
        # Check if config.yaml exists
        config_yaml_path = project_dir / "config.yaml"
        if not config_yaml_path.exists():
            click.echo(f"Error: config.yaml not found in {project_dir}", err=True)
            sys.exit(1)
            
        # Load .env file if it exists
        env_file = project_dir / ".env"
        env_vars = dict(os.environ)
        if env_file.exists():
            click.echo("Loading environment variables from .env...")
            _load_env_file(env_file, env_vars)
            
        # Start the proxy server
        click.echo("Starting LiteLLM Proxy Server...")
        click.echo(f"Port: {final_port}")
        click.echo(f"Config: {config_yaml_path}")
        click.echo()
        
        # Change to project directory and start litellm
        cmd = ["litellm", "--config", "config.yaml", "--port", str(final_port)]
        
        try:
            subprocess.run(cmd, cwd=project_dir, env=env_vars, check=True)
        except subprocess.CalledProcessError as e:
            click.echo(f"Error starting proxy server: {e}", err=True)
            sys.exit(1)
        except KeyboardInterrupt:
            click.echo("\nProxy server stopped.")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _load_env_file(env_file: Path, env_vars: dict[str, str]) -> None:
    """Load environment variables from .env file.
    
    Args:
        env_file: Path to .env file
        env_vars: Dictionary to update with environment variables
    """
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI tool.

    Args:
        args: Command line arguments (for testing)
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        if args is None:
            # Normal CLI usage - let Click handle everything
            cli()
        else:
            # Testing usage - use standalone_mode=False for programmatic control
            cli(args=args, standalone_mode=False)
        return 0
    except SystemExit as e:
        if e.code is None:
            return 0
        if isinstance(e.code, int):
            return e.code
        return 1
    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(main())

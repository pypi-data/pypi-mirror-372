"""Check if litellm is installed and provide installation instructions."""

import os
import subprocess


def check_litellm_installed() -> tuple[bool, str]:
    """Check if litellm command-line tool is available.

    This checks for the litellm CLI command which is needed to start the proxy server.
    
    Returns:
        A tuple of (is_installed, message)
    """
    # Use the current environment to inherit PATH and other settings
    env = dict(os.environ)
    
    # First, check if litellm command exists in PATH using a platform-specific approach
    try:
        # Use 'where' on Windows or 'which' on Unix-like systems
        check_cmd = ["where", "litellm"] if os.name == "nt" else ["which", "litellm"]
        
        result = subprocess.run(
            check_cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=10
        )
        
        if result.returncode != 0:
            return (
                False,
                "litellm command not found in PATH.\n"
                "To install, run: uv tool install 'litellm[proxy]'"
            )
            
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return (
            False,
            "Unable to check for litellm command.\n"
            "To install, run: uv tool install 'litellm[proxy]'"
        )
    
    # If we found the command in PATH, assume it's working
    # We already confirmed it exists with where/which, so trust that it works
    # The actual functionality will be tested when the user tries to start the server
    return (True, "litellm command-line tool is available")


def get_litellm_version() -> str:
    """Get the installed litellm version from command-line tool.

    Returns:
        Version string or "unknown" if not installed
    """
    try:
        # Use the current environment to inherit PATH and other settings
        env = dict(os.environ)
        
        result = subprocess.run(
            ["litellm", "--version"],
            capture_output=True,
            text=True,
            env=env,
            timeout=15  # Increased timeout as litellm can be slow to start
        )
        
        if result.returncode == 0:
            # Extract version from output (usually like "litellm 1.2.3")
            version_output = result.stdout.strip()
            if version_output:
                # Try to extract just the version number
                parts = version_output.split()
                if len(parts) >= 2:
                    return parts[1]  # Second part should be version
                return version_output
            return "unknown"
        else:
            return "not available"
            
    except subprocess.TimeoutExpired:
        return "timeout (slow startup)"
    except (FileNotFoundError, Exception):
        return "not installed"

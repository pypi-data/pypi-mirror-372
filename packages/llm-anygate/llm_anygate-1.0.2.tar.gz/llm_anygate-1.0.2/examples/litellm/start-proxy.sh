#!/usr/bin/env bash
# LiteLLM Proxy Startup Script (POSIX bash)
# Starts LiteLLM proxy with configurable port, master key, and .env search similar to the PowerShell version.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

PORT_ARG=""
MASTER_KEY_ARG=""
ENV_FILE_ARG=""
SHOW_HELP=0

usage() {
  cat <<'EOF'
Usage: start-proxy.sh [options]

Options:
  -p, --port <number>        Port to run the proxy on. Priority:
                               CLI --port > $LITELLM_PREFER_PORT > 4444
  -k, --master-key <key>     Master key for authentication. Priority:
                               CLI --master-key > $LITELLM_MASTER_KEY > "sk-none"
  -e, --env-file <path>      Path to .env file. Search order if omitted:
                               1) script directory
                               2) current working directory
  -h, --help                 Show this help and exit.

Notes:
- Ensure LiteLLM is installed: uv tool install 'litellm[proxy]'  OR  pip install 'litellm[proxy]'
- Endpoints after start (replace PORT accordingly):
    OpenAI:     http://localhost:PORT/v1/chat/completions
    Gemini:     http://localhost:PORT/gemini/v1beta/models/{model}:generateContent
    Anthropic:  http://localhost:PORT/anthropic/v1/messages
    Health:     http://localhost:PORT/health
    Models:     http://localhost:PORT/v1/models
    Admin UI:   http://localhost:PORT/ui
EOF
}

# Parse arguments (supports short and long)
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--port)
      PORT_ARG="${2:-}"; shift 2 ;;
    -k|--master-key)
      MASTER_KEY_ARG="${2:-}"; shift 2 ;;
    -e|--env-file)
      ENV_FILE_ARG="${2:-}"; shift 2 ;;
    -h|--help)
      SHOW_HELP=1; shift ;;
    *)
      echo "Unknown argument: $1" >&2
      SHOW_HELP=1
      break
      ;;
  esac
done

if [[ "$SHOW_HELP" -eq 1 ]]; then
  usage
  exit 0
fi

# Determine port: CLI > env > default 4444
PORT=""
if [[ -n "${PORT_ARG}" ]]; then
  PORT="$PORT_ARG"
  echo "Using port specified via argument: $PORT"
elif [[ -n "${LITELLM_PREFER_PORT:-}" ]]; then
  PORT="$LITELLM_PREFER_PORT"
  echo "Using port from LITELLM_PREFER_PORT environment variable: $PORT"
else
  PORT="4444"
  echo "Using default port: $PORT"
fi

if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "Error: Port must be a number, got: $PORT" >&2
  exit 2
fi

# Determine master key: CLI > env > default "sk-none"
MASTER_KEY=""
if [[ -n "${MASTER_KEY_ARG}" ]]; then
  MASTER_KEY="$MASTER_KEY_ARG"
  echo "Using master key specified via argument"
elif [[ -n "${LITELLM_MASTER_KEY:-}" ]]; then
  MASTER_KEY="$LITELLM_MASTER_KEY"
  echo "Using master key from LITELLM_MASTER_KEY environment variable"
else
  MASTER_KEY="sk-none"
  echo "Warning: Using default master key 'sk-none' - set LITELLM_MASTER_KEY or use --master-key"
fi

# Resolve .env file path
ENV_FILE=""
if [[ -n "${ENV_FILE_ARG}" ]]; then
  ENV_FILE="$ENV_FILE_ARG"
else
  if [[ -f "$SCRIPT_DIR/.env" ]]; then
    ENV_FILE="$SCRIPT_DIR/.env"
    echo "Found .env file in script directory: $ENV_FILE"
  elif [[ -f "$PWD/.env" ]]; then
    ENV_FILE="$PWD/.env"
    echo "Found .env file in current directory: $ENV_FILE"
  else
    ENV_FILE="" # Not found
  fi
fi

# Load .env if present
if [[ -n "$ENV_FILE" && -f "$ENV_FILE" ]]; then
  echo "Loading environment variables from: $ENV_FILE"
  # shellcheck disable=SC2162
  while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    if [[ "$line" =~ ^([^#=]+)=(.*)$ ]]; then
      name="${BASH_REMATCH[1]}"
      value="${BASH_REMATCH[2]}"
      # Trim whitespace around name
      name="$(echo "$name" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
      export "$name=$value"
    fi
  done < "$ENV_FILE"
else
  if [[ -n "$ENV_FILE_ARG" ]]; then
    echo "Warning: .env file not found at: $ENV_FILE_ARG"
  else
    echo "Warning: .env file not found in script directory ($SCRIPT_DIR) or current directory ($PWD)"
    echo "Please create .env from .env.template in either location"
  fi
  echo "Environment variables should be set manually or via system environment"
fi

# Resolve config.yaml: search script dir then current dir
CONFIG_FILE=""
if [[ -f "$SCRIPT_DIR/config.yaml" ]]; then
  CONFIG_FILE="$SCRIPT_DIR/config.yaml"
  echo "Found config.yaml in script directory: $CONFIG_FILE"
elif [[ -f "$PWD/config.yaml" ]]; then
  CONFIG_FILE="$PWD/config.yaml"
  echo "Found config.yaml in current directory: $CONFIG_FILE"
else
  echo "Error: config.yaml not found in script directory ($SCRIPT_DIR) or current directory ($PWD)"
  exit 1
fi

echo "Starting LiteLLM proxy..."
echo "Config file: $CONFIG_FILE"
echo "Proxy will be available at: http://localhost:$PORT"
echo "Admin UI (if enabled): http://localhost:$PORT/ui"
echo ""
echo "Press Ctrl+C to stop the proxy"
echo ""

# Ensure litellm is available
if ! command -v litellm >/dev/null 2>&1; then
  echo "Error: 'litellm' command not found."
  echo "Make sure LiteLLM is installed:"
  echo "  uv tool install 'litellm[proxy]'"
  echo "  OR"
  echo "  pip install 'litellm[proxy]'"
  exit 1
fi

# Set master key for the process and start
export LITELLM_MASTER_KEY="$MASTER_KEY"
litellm --config "$CONFIG_FILE" --port "$PORT" --host 0.0.0.0
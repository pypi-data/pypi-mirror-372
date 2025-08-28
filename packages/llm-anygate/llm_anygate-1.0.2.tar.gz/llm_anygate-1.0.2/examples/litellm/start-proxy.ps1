<#
.SYNOPSIS
Starts LiteLLM proxy with configurable port and authentication.

.DESCRIPTION
This script starts a LiteLLM proxy server with configurable port and master key settings.
It automatically searches for .env and config.yaml files, supports environment variable
configuration, and provides multiple API format endpoints.

The script implements a priority system for configuration:
- Port: -Port parameter > LITELLM_PREFER_PORT env var > 4444 (default)
- Master Key: -MasterKey parameter > LITELLM_MASTER_KEY env var > "sk-none" (default)

File search order for .env and config.yaml:
1. Same directory as this script
2. Current working directory

.PARAMETER Port
Port number for the proxy server. If not specified, uses LITELLM_PREFER_PORT environment
variable or defaults to 4444.

.PARAMETER MasterKey
Master key for authentication. If not specified, uses LITELLM_MASTER_KEY environment
variable or defaults to "sk-none".

.PARAMETER EnvFile
Path to a custom .env file. If not specified, automatically searches for .env files
in the script directory first, then the current working directory.

.PARAMETER Help
Shows detailed help information and exits.

.INPUTS
None. This script does not accept pipeline input.

.OUTPUTS
None. This script starts a background service and outputs status messages.

.EXAMPLE
.\start-proxy.ps1
Starts the proxy using environment variables or defaults for all settings.

.EXAMPLE
.\start-proxy.ps1 -Port 8080
Starts the proxy on port 8080, using environment variables or defaults for other settings.

.EXAMPLE
.\start-proxy.ps1 -MasterKey "sk-my-key"
Starts the proxy with a custom master key, using environment variables or defaults for other settings.

.EXAMPLE
.\start-proxy.ps1 -Port 8080 -MasterKey "sk-my-key"
Starts the proxy with both custom port and master key.

.EXAMPLE
.\start-proxy.ps1 -EnvFile "C:\path\to\.env"
Starts the proxy using a custom .env file path.

.EXAMPLE
.\start-proxy.ps1 -Port 8080 -EnvFile ".\custom.env"
Starts the proxy with custom port and .env file.

.NOTES
PREREQUISITES:
1. Install LiteLLM: uv tool install litellm[proxy]
2. Create .env file from .env.template with your API keys
3. Ensure config.yaml exists in script or current directory

ENVIRONMENT VARIABLES:
- LITELLM_PREFER_PORT: Preferred port number (used when -Port is not specified)
- LITELLM_MASTER_KEY: Master key for authentication (used when -MasterKey is not specified)

AVAILABLE ENDPOINTS (after starting):
- OpenAI format: http://localhost:PORT/v1/chat/completions
- Gemini format: http://localhost:PORT/gemini/v1beta/models/{model}:generateContent
- Anthropic format: http://localhost:PORT/anthropic/v1/messages
- Health check: http://localhost:PORT/health
- Models list: http://localhost:PORT/v1/models
- Admin UI (if enabled): http://localhost:PORT/ui

TESTING EXAMPLES:
# Test with curl (replace PORT and MASTER_KEY with actual values)
curl http://localhost:4444/v1/models -H "Authorization: Bearer your-master-key"

# Configure gemini-cli (replace PORT and MASTER_KEY with actual values)
$env:GOOGLE_GEMINI_BASE_URL = "http://localhost:4444"
$env:GEMINI_API_KEY = "your-master-key"

.LINK
https://github.com/BerriAI/litellm
#>

param(
    [int]$Port = 0,  # 0 means use environment variable or default
    [string]$EnvFile = "",
    [string]$MasterKey = ""  # Empty means use environment variable or default
)

# Determine the port to use: specified args > LITELLM_PREFER_PORT > 4444
if ($Port -eq 0) {
    $preferredPort = [Environment]::GetEnvironmentVariable("LITELLM_PREFER_PORT")
    if ($preferredPort -and $preferredPort -ne "" -and [int]::TryParse($preferredPort, [ref]$null)) {
        $Port = [int]$preferredPort
        Write-Host "Using port from LITELLM_PREFER_PORT environment variable: $Port" -ForegroundColor Cyan
    } else {
        $Port = 4444
        Write-Host "Using default port: $Port" -ForegroundColor Gray
    }
} else {
    Write-Host "Using port specified via argument: $Port" -ForegroundColor Cyan
}

# Determine the master key to use: specified args > LITELLM_MASTER_KEY > "sk-none"
if ($MasterKey -eq "") {
    $envMasterKey = [Environment]::GetEnvironmentVariable("LITELLM_MASTER_KEY")
    if ($envMasterKey -and $envMasterKey -ne "") {
        $MasterKey = $envMasterKey
        Write-Host "Using master key from LITELLM_MASTER_KEY environment variable" -ForegroundColor Cyan
    } else {
        $MasterKey = "sk-none"
        Write-Host "Warning: Using default master key 'sk-none' - set LITELLM_MASTER_KEY or use -MasterKey parameter" -ForegroundColor Yellow
    }
} else {
    Write-Host "Using master key specified via argument" -ForegroundColor Cyan
}

# Check if .env file exists - use custom path if provided, otherwise search in script dir then pwd
if ($EnvFile -eq "") {
    # Search order: 1) script directory, 2) current working directory
    $scriptDirEnv = Join-Path $PSScriptRoot ".env"
    $pwdEnv = Join-Path (Get-Location) ".env"
    
    if (Test-Path $scriptDirEnv) {
        $envFile = $scriptDirEnv
        Write-Host "Found .env file in script directory: $envFile" -ForegroundColor Cyan
    } elseif (Test-Path $pwdEnv) {
        $envFile = $pwdEnv
        Write-Host "Found .env file in current directory: $envFile" -ForegroundColor Cyan
    } else {
        $envFile = $pwdEnv  # Default path for error message
    }
} else {
    $envFile = $EnvFile
}

if (Test-Path $envFile) {
    Write-Host "Loading environment variables from: $envFile" -ForegroundColor Green
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#][^=]*)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
} else {
    if ($EnvFile -eq "") {
        Write-Host "Warning: .env file not found in script directory ($PSScriptRoot) or current directory ($(Get-Location))" -ForegroundColor Yellow
        Write-Host "Please create .env file from .env.template in either location" -ForegroundColor Yellow
    } else {
        Write-Host "Warning: .env file not found at: $envFile" -ForegroundColor Yellow
    }
    Write-Host "Environment variables should be set manually or via system environment" -ForegroundColor Yellow
}

# Check if config.yaml exists - search in script dir first, then current directory
$scriptDirConfig = Join-Path $PSScriptRoot "config.yaml"
$pwdConfig = Join-Path (Get-Location) "config.yaml"

if (Test-Path $scriptDirConfig) {
    $configFile = $scriptDirConfig
    Write-Host "Found config.yaml in script directory: $configFile" -ForegroundColor Cyan
} elseif (Test-Path $pwdConfig) {
    $configFile = $pwdConfig
    Write-Host "Found config.yaml in current directory: $configFile" -ForegroundColor Cyan
} else {
    Write-Host "Error: config.yaml not found in script directory ($PSScriptRoot) or current directory ($(Get-Location))" -ForegroundColor Red
    exit 1
}

Write-Host "Starting LiteLLM proxy..." -ForegroundColor Green
Write-Host "Config file: $configFile" -ForegroundColor Gray
Write-Host "Proxy will be available at: http://localhost:$Port" -ForegroundColor Gray
Write-Host "Admin UI (if enabled): http://localhost:$Port/ui" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the proxy" -ForegroundColor Yellow
Write-Host ""

# Start LiteLLM proxy
try {
    # Set the master key for the litellm process
    [Environment]::SetEnvironmentVariable("LITELLM_MASTER_KEY", $MasterKey, "Process")
    litellm --config $configFile --port $Port --host 0.0.0.0
}
catch {
    Write-Host "Error starting LiteLLM proxy: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure LiteLLM is installed: uv tool install litellm[proxy]" -ForegroundColor Yellow
    exit 1
}
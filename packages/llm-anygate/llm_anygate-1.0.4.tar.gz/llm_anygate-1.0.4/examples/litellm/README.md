# LiteLLM Proxy Configuration

This directory contains the LiteLLM proxy configuration for accessing GPT-5 via a local proxy endpoint.

## Files

- `config.yaml` - LiteLLM proxy configuration with GPT-5 model setup
- `.env.template` - Template for environment variables
- `start-proxy.ps1` - PowerShell startup script (Windows)
- `start-proxy.sh` - Bash startup script (Linux/macOS)

## Setup

1. **Install LiteLLM:**
   ```bash
   pip install litellm[proxy]
   ```

2. **Configure Environment Variables:**
   ```bash
   # Copy the template
   cp .env.template .env
   
   # Edit .env and set your actual API key
   # OPENAI_API_KEY=your-actual-api-key-here
   # LITELLM_MASTER_KEY=sk-your-secure-master-key
   ```

3. **Start the Proxy:**
   
   **Windows (PowerShell):**
   ```powershell
   .\start-proxy.ps1
   ```
   
   **Linux/macOS (Bash):**
   ```bash
   chmod +x start-proxy.sh
   ./start-proxy.sh
   ```

## Configuration Details

- **Model:** gpt-5
- **API Base URL:** https://yunwu.ai/v1
- **Local Endpoint:** http://localhost:4444
- **Temperature:** 1.0
- **Admin UI:** http://localhost:4444/ui (if enabled)

## Usage

Once the proxy is running, you can use it like a standard OpenAI API:

```bash
curl http://localhost:4444/v1/chat/completions \
  -H "Authorization: Bearer your-litellm-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 1.0
  }'
```

## Python Client Example

```python
import openai

client = openai.OpenAI(
    api_key="your-litellm-master-key",
    base_url="http://localhost:4444"
)

response = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": "Hello"}],
    temperature=1.0
)

print(response.choices[0].message.content)
```
# Task 1: create a quick cli tool to setup litellm proxy [COMPLETED]

- example litellm proxy project (`llm-proxy-proj`): `examples\litellm`

we want to develop a quick cli tool to setup something like `llm-proxy-proj` with minimal configuration, like below:

```yaml
# model-config.yaml

model_list:
  # GPT-5 model configuration
  - model_name: gpt-5-2025-08-07
    litellm_params:
      model: openai/gpt-5-2025-08-07
      api_base: https://yunwu.ai/v1
      api_key: os.environ/OPENAI_API_KEY
      temperature: 1.0

  - model_name: gemini-2.5-pro
    litellm_params:
      model: openai/gpt-5-2025-08-07
      api_base: https://yunwu.ai/v1
      api_key: os.environ/OPENAI_API_KEY
      temperature: 1.0

  - model_name: claude-opus-4-1-20250805
    litellm_params:
      model: openai/gpt-5-2025-08-07
      api_base: https://yunwu.ai/v1
      api_key: os.environ/OPENAI_API_KEY
      temperature: 1.0
```

suppose our project develops a cli tool named `llm-anygate-cli`, then we can run the following command to setup a litellm proxy server:

```bash
llm-anygate-cli create --project <project-dir> --model-config model-config.yaml --port 4567 --master-key "sk-dummy"
```

**checking dependencies**
note that, `llm-anygate-cli` will first check if `litellm[proxy]` is installed, if not, it will warn the user with installation instructions, but not install it automatically. Because generating a proxy project does not depend on `litellm` at runtime, so the generation continues.

**default model config**
if `--model-config` is not provided, we will treat the following as default model config,
you can hardcode it in the cli tool:

```yaml
# litellm config.yaml

# contents from model-config.yaml
model_list:  
  - model_name: (exposed model name)
    litellm_params:
      model: (api_format/model_name, e.g. openai/gpt-4o)
      api_base: os.environ/OPENAI_BASE_URL
      api_key: os.environ/OPENAI_API_KEY
      temperature: 1.0
```

then, we will create a project directory `<project-dir>` with structure similar to `llm-proxy-proj`, with:
- default port being `4567`
- litellm config `config.yaml` generated from `model-config.yaml`, like this

```yaml
# litellm config.yaml

# contents from model-config.yaml
model_list:  
  - model_name: gpt-5-2025-08-07
    litellm_params:
      model: openai/gpt-5-2025-08-07
      api_base: https://yunwu.ai/v1
      api_key: os.environ/OPENAI_API_KEY
      temperature: 1.0

  - model_name: gemini-2.5-pro
    litellm_params:
      model: openai/gpt-5-2025-08-07
      api_base: https://yunwu.ai/v1
      api_key: os.environ/OPENAI_API_KEY
      temperature: 1.0

  - model_name: claude-opus-4-1-20250805
    litellm_params:
      model: openai/gpt-5-2025-08-07
      api_base: https://yunwu.ai/v1
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
  master_key: "sk-dummy"   # Provide master key here (not stored in DB)
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
```


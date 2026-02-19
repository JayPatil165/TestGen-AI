# config

Manage global TestGen AI configuration — API keys, provider selection, and model settings.

Configuration is stored in `~/.testgen/.env` in your home directory, so it works from any project, any directory, on your machine.

---

## Subcommands

### `config set`

Save a key/value setting globally.

```bash
testgen config set <KEY> <VALUE>
```

**Examples:**

```bash
# Set your Gemini API key (default provider)
testgen config set GEMINI_API_KEY AIza...

# Switch to OpenAI
testgen config set LLM_PROVIDER openai
testgen config set OPENAI_API_KEY sk-...

# Switch to Anthropic / Claude
testgen config set LLM_PROVIDER anthropic
testgen config set ANTHROPIC_API_KEY sk-ant-...

# Use Ollama (local model, no API key needed)
testgen config set LLM_PROVIDER ollama
testgen config set LLM_MODEL llama3

# Change the model for any provider
testgen config set LLM_MODEL gpt-4o
```

The value is written to `~/.testgen/.env` immediately and takes effect on the next `testgen` invocation.

---

### `config show`

Display the currently active configuration with masked key values.

```bash
testgen config show
```

Output shows:

- Active provider and model
- Which API keys are set (first 4 and last 2 characters visible, rest masked)
- Path to the global config file
- Reminder about local `.env` override

---

## Configuration Keys

| Key | Description | Example |
|-----|-------------|---------|
| `LLM_PROVIDER` | Which AI provider to use | `gemini`, `openai`, `anthropic`, `ollama` |
| `LLM_MODEL` | Specific model name | `gemini-2.0-flash`, `gpt-4o`, `claude-3-5-sonnet` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-...` |

---

## How config resolution works

TestGen AI resolves settings in this priority order (highest wins):

1. **System environment variables** — e.g. set in your shell or CI pipeline
2. **Local `.env` file** — a `.env` file in the directory where you run `testgen`
3. **Global `~/.testgen/.env`** — set once via `testgen config set`, works everywhere

This means you can set a default API key globally once, and override it per-project by dropping a `.env` file in that project's root.

---

## Getting a free API key

??? tip "Google Gemini (recommended for getting started)"
    Gemini has a free tier that is sufficient for most development use.

    1. Go to [aistudio.google.com](https://aistudio.google.com)
    2. Sign in with a Google account
    3. Click **Get API key**
    4. Copy the key and run:
       ```bash
       testgen config set GEMINI_API_KEY AIza...
       ```

> **Development notice:** We're planning to provide a managed shared API key in a future release so no per-user setup will be required. Until that ships, each user needs their own key.

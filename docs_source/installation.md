# Installation

## Requirements

- Python 3.10 or higher
- pip

That's it.

## Install

```bash
pip install testgen-ai
```

This single command installs **everything** — all required libraries (`litellm`, `pytest`, `typer`, `rich`, `pydantic`, `watchdog`, and more) come bundled. Nothing else to install.

Verify:

```bash
testgen --version
```

---

## Setting Your API Key (one-time setup)

> **Note:** TestGen AI is currently in open development. Each user needs to supply their own LLM API key. We're planning to provide a managed, shared API key in a future release so setup is fully zero-config — but until that ships, a personal key is required to use the AI features. Getting one is free on most providers (Gemini has a generous free tier).

TestGen AI needs an API key for whichever LLM provider you want to use. Set it **once** using the built-in config command and it will work globally from any directory, forever:

```bash
# Google Gemini (default provider)
testgen config set GEMINI_API_KEY AIza...

# OpenAI
testgen config set OPENAI_API_KEY sk-...
testgen config set LLM_PROVIDER openai

# Anthropic / Claude
testgen config set ANTHROPIC_API_KEY sk-ant-...
testgen config set LLM_PROVIDER anthropic

# Ollama (local, no key needed — just set the provider)
testgen config set LLM_PROVIDER ollama
testgen config set LLM_MODEL llama3
```

Check what's currently configured:

```bash
testgen config show
```

Keys are saved to `~/.testgen/.env` in your home directory and are picked up automatically by every `testgen` command from any project, on any directory.

### Supported Providers

| Provider | Key to set | Default model |
|----------|-----------|---------------|
| Google Gemini | `GEMINI_API_KEY` | `gemini-2.0-flash` |
| OpenAI | `OPENAI_API_KEY` | `gpt-4o` |
| Anthropic | `ANTHROPIC_API_KEY` | `claude-3-5-sonnet` |
| Ollama (local) | *(none)* | `llama3` |

### Per-project override

If you need a different key or provider for one specific project, drop a `.env` file in that project's root:

```
OPENAI_API_KEY=sk-project-specific-key
LLM_PROVIDER=openai
```

Local `.env` always wins over the global config.

---

## Non-Python Languages

For Python projects there is **zero extra setup** — pytest is already bundled.

If you're generating tests for JavaScript/TypeScript, Go, Rust, Java, etc., you need that language's runtime installed on your machine (Node.js, Go toolchain, cargo, JDK...). pip cannot install system-level language runtimes — this is the same requirement as just running any code in those languages normally.

### UI / Browser testing (Playwright)

Playwright browser testing is an optional extra. If you need it:

```bash
pip install testgen-ai[browser]   # installs the Playwright Python package
playwright install                 # downloads browser binaries (one-time per machine)
```

The second step (`playwright install`) downloads Chromium/Firefox/WebKit binaries. This can't be automated by pip — it's a one-time manual step. For pure unit testing of Python code, you don't need this at all.

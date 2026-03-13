# Installation

## Requirements

- Python 3.10 or higher
- pip

That's it.

## Install

### Recommended: Use a Virtual Environment

```bash
# Create a virtual environment (one-time)
python -m venv testgen-env

# Activate it
# On Windows:
testgen-env\Scripts\activate
# On macOS/Linux:
source testgen-env/bin/activate

# Install the package
pip install testgen-ai
```

### Or Install Globally

```bash
pip install testgen-ai
```

That's it! The `testgen` command will work immediately after installation.

> **How it works:**
> - On **Windows**: The first time you run `testgen`, it automatically adds Python's Scripts folder to your system PATH
> - On **macOS/Linux**: The command works immediately
> - **Zero configuration required** — everything happens automatically
> - On Windows, you may need to **restart your terminal** after the first use for the PATH to take effect in future terminals

## Verify Installation

```bash
testgen --version
```

You should see the version number printed.

**First time on Windows?** The first run will automatically configure your system. You may see a terminal notification about PATH configuration — that's normal and expected.

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

---

## Troubleshooting

### "`testgen` command not found" / "`testgen is not recognized`"

This rarely happens now since PATH is configured automatically, but here are solutions if it does:

**Option 1: Run the command to trigger auto-setup**

```bash
testgen --version
```

This runs the auto-setup if it hasn't run yet. Restart your terminal after.

**Option 2: Use via Python module (always works, no setup needed)**

```bash
python -m testgen generate ./src
python -m testgen config show
python -m testgen --version
```

This bypasses PATH entirely and works on any platform.

**Option 3: Check if in PATH (Windows)**

```bash
python -c "import sys; print(sys.prefix)"
```

This shows your Python installation directory. Add `\Scripts` to the end and manually add that folder to your Windows PATH if needed.

**Option 4: Reinstall fresh**

```bash
pip uninstall testgen-ai
pip install testgen-ai
testgen --version
```

### Which option should I use?

- **First time?** Try running `testgen --version` — auto-setup should kick in
- **Still not working?** Use `python -m testgen` (always works immediately)
- **Using a venv?** Make sure it's activated with `source testgen-env/bin/activate` (or `testgen-env\Scripts\activate` on Windows) before running commands

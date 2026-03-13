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

# ONE-TIME SETUP (especially important on Windows!)
testgen setup
```

### Or Install Globally

```bash
pip install testgen-ai

# ONE-TIME SETUP (especially important on Windows!)
testgen setup
```

This single command installs **everything** — all required libraries (`litellm`, `pytest`, `typer`, `rich`, `pydantic`, `watchdog`, and more) come bundled. Nothing else to install.

> **The `testgen setup` command:**
> - On **Windows**: Automatically adds Python's Scripts folder to your system PATH so the `testgen` command works in any terminal
> - On **macOS/Linux**: Verifies the command is accessible and provides troubleshooting tips if needed
> - **You only need to run this once** — it's a one-time setup after installation
> - On Windows, you may need to **restart your terminal** after running setup

## Verify Installation

```bash
testgen --version
```

You should see the version number printed. If you get a command not found error:

1. **Make sure you ran `testgen setup`** (especially on Windows)
2. **Restart your terminal**
3. If still not working, see the [troubleshooting section](#troubleshooting) below.

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

**Easy fix:** Make sure you ran `testgen setup` after installation, then restart your terminal.

If that doesn't work, try these options:

**Option 1: Run setup as Administrator (Windows)**

The `testgen setup` command needs administrator access to modify Windows PATH. Try running your terminal as Administrator:

1. Right-click Command Prompt or PowerShell → **Run as administrator**
2. Run `testgen setup` again
3. Restart your terminal
4. Test with `testgen --version`

**Option 2: Use via Python module (always works, no setup needed)**

```bash
python -m testgen generate ./src
python -m testgen config show
python -m testgen --version
```

This bypasses PATH entirely and works on any platform.

**Option 3: Manually add to PATH (Windows)**

If you can't run as admin, manually add the Scripts folder:

```bash
# First, find your Scripts folder:
python -c "import sys; print(sys.prefix)"

# Add this result + \Scripts to your Windows PATH:
# 1. Press Win + X → click System
# 2. Click Advanced system settings → Environment Variables
# 3. Under User variables, find Path → Edit
# 4. Click New and paste: C:\Python313\Scripts (or your result from above)
# 5. Click OK three times, restart terminal
```

**Option 4: Activate your virtual environment (if using a venv)**

```bash
# Windows:
testgen-env\Scripts\activate

# macOS/Linux:
source testgen-env/bin/activate

# Now testgen will work
testgen --version
```

**Option 5: Reinstall fresh**

```bash
pip uninstall testgen-ai
pip install testgen-ai
testgen setup
```

### Which option should I use?

- **Windows users:** Try `testgen setup` first (with Admin terminal)
- **All users:** `python -m testgen` always works instantly
- **Using a venv:** Just activate it with `source testgen-env/bin/activate` (or `testgen-env\Scripts\activate` on Windows)


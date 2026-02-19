# 🚀 TestGen AI

> **The Autonomous QA Agent from Your CLI**

TestGen AI is a CLI tool that automatically generates, runs, and reports on test suites for your code using LLMs. Point it at a directory, set an API key, and let it handle the rest.

## Install

```bash
pip install testgen-ai
```

## Quick Start

```bash
# Set your API key once (saved globally)
testgen config set GEMINI_API_KEY AIza...

# Generate tests for your project
testgen generate ./src

# Run them
testgen test

# Or do everything at once
testgen auto ./src
```

## What it does

TestGen AI follows the **AGER** loop:

| Phase | What happens |
|-------|-------------|
| **Analyze** | Scans your code and extracts function signatures with minimal token usage |
| **Generate** | Calls your LLM (GPT-4, Claude, Gemini, or Ollama) to write real test cases |
| **Execute** | Runs the tests via the appropriate framework (pytest, Jest, cargo test, etc.) |
| **Report** | Renders a live terminal matrix and builds an HTML report |

## Features

- 🤖 **AI-powered** — real tests, not boilerplate
- 🌍 **14 languages** — Python, JS/TS, Go, Rust, Java, C#, Ruby, PHP, Swift, Kotlin, C++, HTML, CSS
- 👀 **Watch mode** — regenerates tests on every file save (`--watch`)
- 📊 **Terminal dashboard** — color-coded pass/fail matrix
- 📈 **HTML reports** — metrics, coverage, execution breakdowns
- ⚡ **Smart context** — AST extraction keeps LLM costs low

## Supported LLM Providers

| Provider | Key name | Default model |
|----------|---------|---------------|
| Google Gemini | `GEMINI_API_KEY` | `gemini-2.0-flash` |
| OpenAI | `OPENAI_API_KEY` | `gpt-4o` |
| Anthropic | `ANTHROPIC_API_KEY` | `claude-3-5-sonnet` |
| Ollama (local) | *(none)* | `llama3` |

See the [Installation](installation.md) guide to get started.

---

Built by [Jay Ajitkumar Patil](https://github.com/JayPatil165) · [patiljay32145@gmail.com](mailto:patiljay32145@gmail.com)

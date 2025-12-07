# 🚀 TestGen AI

> **"The Autonomous QA Agent from Your CLI"**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python-based CLI package that acts as an **"Autonomous QA Pair-Programmer."** It lives in your terminal and automates the tedious parts of software testing: understanding code, writing test cases, running them, and formatting reports.

With **Watch Mode**, TestGen AI writes tests while you write code, enabling true **Test-Driven Development** without the overhead.

---

## ✨ Features

- 🤖 **AI-Powered Test Generation** - Automatically generates comprehensive test suites using LLMs (OpenAI, Claude, Ollama)
- 📊 **Beautiful Terminal Dashboard** - Rich, color-coded test execution matrix with real-time feedback
- 👀 **Watch Mode** - Real-time TDD with automatic test generation as you code
- 📈 **HTML/PDF Reports** - Professional test reports for stakeholders
- ⚡ **Smart Context Extraction** - Intelligently parses code to minimize LLM costs
- 🎯 **Multiple Test Frameworks** - Supports Pytest and Playwright for UI testing
- 🔄 **One-Click Workflow** - `testgen auto` does everything: generate → test → report

---

## 🎯 The "AGER" Architecture

TestGen AI operates on a localized 4-step loop:

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Analyze  │────▶│ Generate │────▶│ Execute  │────▶│ Report   │
│ (Scanner)│     │ (Brain)  │     │ (Runner) │     │ (Visuals)│
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

### A - Analyze (The Scanner)
- Reads your project directory
- Filters noise (`node_modules`, `.git`, etc.)
- Extracts function signatures and docstrings for large files
- Keeps LLM costs low with smart context management

### G - Generate (The Brain)
- Sends context to LLMs (OpenAI/Ollama/Claude)
- Receives executable Python/Pytest code
- Writes test files to the `tests/` directory
- **Watch Mode**: Listens for file saves and triggers generation instantly

### E - Execute (The Runner)
- Identifies test types (Unit vs. UI)
- Runs test frameworks (Pytest/Playwright) in subprocesses
- Captures logs and exit codes

### R - Report (The Visuals)
- Parses execution data
- Renders beautiful CLI matrices
- Compiles persistent HTML reports

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Install from PyPI *(Coming Soon)*
```bash
pip install testgen-ai
```

### Install from Source
```bash
# Clone the repository
git clone https://github.com/JayPatil165/TestGen-AI.git
cd TestGen-AI

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode
pip install -e .
```

---

## 🚀 Quick Start

### 1. Configure API Keys

Create a `.env` file in your project root:

```bash
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=your-claude-key
# OR use Ollama (local, no API key needed)
```

### 2. Run Your First Test Generation

```bash
# Generate tests for your project
testgen generate ./src

# Run the generated tests
testgen test

# Generate HTML report
testgen report

# Or do everything at once (God Mode)
testgen auto
```

### 3. Enable Watch Mode (Real-time TDD)

```bash
# Watch your code and auto-generate tests as you type
testgen generate ./src --watch
```

---

## 🎨 CLI Commands

### Command Matrix

| Command | Purpose | What It Does | Special Flags |
|---------|---------|--------------|---------------|
| `testgen generate` | Create test files | Analyzes code → Calls LLM → Saves tests | `--watch` (Live AI) |
| `testgen test` | Run existing tests | Executes tests → Shows status | `--verbose` |
| `testgen report` | Generate documentation | Creates HTML/PDF report | `--pdf` |
| `testgen auto` | Do everything | Full pipeline (One-click) | N/A |

### Detailed Command Usage

#### Generate Tests
```bash
# Generate tests for a specific directory
testgen generate ./src

# Generate with live watch mode
testgen generate ./src --watch

# Specify output directory
testgen generate ./src --output ./tests
```

#### Run Tests
```bash
# Run all tests
testgen test

# Run with verbose output
testgen test --verbose

# Run specific test pattern
testgen test --pattern "test_user*"
```

#### Generate Reports
```bash
# Generate HTML report
testgen report

# Generate PDF report
testgen report --pdf

# Specify output path
testgen report --output ./reports/test_report.html
```

#### Auto Mode (God Mode)
```bash
# Do everything: generate → test → report
testgen auto ./src
```

---

## 📊 Terminal Dashboard

When tests execute, you'll see a beautiful matrix like this:

```
╔══════════════════════════════════════════════════════════════════╗
║                    TEST EXECUTION MATRIX                         ║
╠═══════════════════════════════╦══════════╦══════════╦════════════╣
║ Test Name                     ║ Status   ║ Duration ║ Details    ║
╠═══════════════════════════════╬══════════╬══════════╬════════════╣
║ test_user_login               ║ ✔ PASS   ║ 0.24s    ║            ║
║ test_user_registration        ║ ✔ PASS   ║ 0.31s    ║            ║
║ test_password_validation      ║ ✘ FAIL   ║ 0.12s    ║ AssertionE…║
║ test_database_connection      ║ ✔ PASS   ║ 5.01s    ║ [SLOW]     ║
║ test_api_endpoint_users       ║ ✔ PASS   ║ 0.89s    ║            ║
╚═══════════════════════════════╩══════════╩══════════╩════════════╝

Summary: 4 passed, 1 failed, 0 skipped | Total: 6.57s
```

### Color Coding
- ✔ **PASS**: Bold Green
- ✘ **FAIL**: Bold Red  
- ⊘ **SKIP**: Yellow
- **Duration**: <1s Green, 1-5s Yellow, >5s Red (Warning)

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Language** | Python 3.10+ | Modern syntax with pattern matching |
| **CLI Framework** | Typer | Type-hint based command validation |
| **Terminal UI** | Rich | Tables, spinners, syntax highlighting |
| **AI Layer** | LiteLLM | Model-agnostic (GPT/Claude/Ollama) |
| **Validation** | Pydantic | Strict JSON output from LLMs |
| **File Watching** | Watchdog | OS-level events (inotify/FSEvents) |
| **Testing Core** | Pytest | Test execution engine |
| **UI Testing** | Playwright | Headless browser automation |
| **Reporting** | Jinja2 | HTML/PDF template rendering |

---

## 📁 Project Structure

```
testgen-ai/
├── pyproject.toml           # Configuration & Dependencies
├── README.md                # This file
├── TASKS.md                 # Development roadmap (140 tasks)
├── .env.example             # Environment variables template
└── src/
    └── testgen/
        ├── __init__.py
        ├── main.py          # CLI Entry Point (Typer)
        ├── manager.py       # Workflow Orchestrator
        ├── config.py        # Settings & API Keys
        ├── core/            # Backend Logic
        │   ├── scanner.py       # Code analyzer
        │   ├── llm.py           # AI integration
        │   ├── runner.py        # Test executor
        │   └── watcher.py       # Watch mode handler
        └── ui/              # Frontend Visuals
            ├── printer.py       # Terminal matrix renderer
            └── reporter.py      # HTML/PDF generator
```

---

## 🎓 Usage Examples

### Example 1: Generate Tests for a Python Module

```bash
# Your project structure
my_app/
├── calculator.py
└── utils.py

# Generate tests
testgen generate ./my_app

# Result: tests/ directory created
tests/
├── test_calculator.py
└── test_utils.py
```

### Example 2: Watch Mode for TDD

```bash
# Start watch mode
testgen generate ./src --watch --auto-run

# Now edit src/user.py
# → TestGen AI detects change
# → Generates tests/test_user.py
# → Runs tests automatically
# → Shows results in terminal
```

### Example 3: CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install TestGen AI
        run: pip install testgen-ai
      - name: Generate and Run Tests
        run: testgen auto ./src
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## ⚙️ Configuration

Create a `.env` file in your project root:

```bash
# LLM Provider (choose one)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-claude-key

# Model Selection
LLM_MODEL=gpt-4                    # or gpt-3.5-turbo, claude-3, ollama/codellama

# Test Generation Settings
TEST_FRAMEWORK=pytest              # or unittest
TEST_OUTPUT_DIR=./tests
MAX_CONTEXT_TOKENS=8000

# Watch Mode Settings
WATCH_DEBOUNCE_SECONDS=2
WATCH_AUTO_RUN=true
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following our coding standards
4. **Run tests**: `pytest`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

See [TASKS.md](TASKS.md) for the development roadmap.

---

## 📝 Development Roadmap

The project is organized into **10 modules** with **140 sequential tasks**. See [TASKS.md](TASKS.md) for details:

- ✅ Module 0: Project Setup (Tasks 1-9)
- 🟡 Module 1: CLI Framework (Tasks 10-21)
- ⬜ Module 2: Code Scanner (Tasks 22-32)
- ⬜ Module 3: LLM Integration (Tasks 33-46)
- ⬜ Module 4: Test Runner (Tasks 47-58)
- ⬜ Module 5: Watch Mode (Tasks 59-68)
- ⬜ Module 6: Terminal UI (Tasks 69-79)
- ⬜ Module 7: Report Generation (Tasks 80-91)
- ⬜ Module 8: Workflow Orchestration (Tasks 92-103)
- ⬜ Module 9: Integration Testing (Tasks 104-119)
- ⬜ Module 10: Documentation & Deployment (Tasks 120-140)

---

## 🐛 Troubleshooting

### Issue: "API Key not found"
**Solution**: Create a `.env` file with your API key:
```bash
echo "OPENAI_API_KEY=sk-your-key" > .env
```

### Issue: "No tests generated"
**Solution**: Ensure your code files have docstrings and are not empty. TestGen AI works best with well-documented code.

### Issue: "Command not found: testgen"
**Solution**: Install in editable mode or add to PATH:
```bash
pip install -e .
# OR
export PATH="$PATH:$HOME/.local/bin"
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI
- Powered by [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- AI integration via [LiteLLM](https://github.com/BerriAI/litellm)
- Inspired by the need for better developer tooling in the AI era

---

## 📧 Contact & Support

- **Author**: Jay Patil
- **GitHub**: [@JayPatil165](https://github.com/JayPatil165)
- **Issues**: [GitHub Issues](https://github.com/JayPatil165/TestGen-AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/JayPatil165/TestGen-AI/discussions)

---

<p align="center">
  <strong>⭐ Star this repo if you find it useful! ⭐</strong>
</p>

<p align="center">
  Made with ❤️ by developers, for developers
</p>

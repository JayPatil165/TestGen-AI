# LLM API Keys Setup Guide

This guide will help you get API keys for the LLM providers supported by TestGen AI.

---

## Supported LLM Providers

TestGen AI supports three LLM providers:

1. **OpenAI** (GPT-3.5, GPT-4) - Cloud-based, paid
2. **Anthropic** (Claude) - Cloud-based, paid
3. **Ollama** - Local, free (no API key needed)

You can use any one of these or all three!

---

## Option 1: OpenAI (Recommended for Getting Started)

OpenAI provides the most popular LLMs (GPT-3.5-turbo, GPT-4).

### Step 1: Create an OpenAI Account

1. Go to: https://platform.openai.com/signup
2. Sign up with your email or Google/Microsoft account
3. Verify your email address

### Step 2: Add Payment Method (Required)

1. Go to: https://platform.openai.com/settings/organization/billing/overview
2. Click "Add payment method"
3. Add a credit/debit card
4. **Note**: You need to add payment even for free tier usage

### Step 3: Get Your API Key

1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Give it a name like "TestGen-AI"
4. **IMPORTANT**: Copy the key immediately! You won't be able to see it again
5. It looks like: `sk-proj-...` (starts with "sk-")

### Step 4: Set Up in TestGen AI

Option A - Environment Variable (Recommended):
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-proj-your-key-here"

# Or add to .env file (create if doesn't exist)
OPENAI_API_KEY=sk-proj-your-key-here
```

Option B - Direct in config (Less secure):
Edit `src/testgen/config.py` and add your key

### Pricing (as of 2024):
- GPT-3.5-turbo: ~$0.002 per 1K tokens (~$0.01 per test)
- GPT-4-turbo: ~$0.01 per 1K tokens (~$0.05 per test)
- You get $5 free credits when you sign up!

---

## Option 2: Anthropic Claude (Alternative)

Anthropic provides Claude models, known for being helpful and harmless.

### Step 1: Create an Anthropic Account

1. Go to: https://console.anthropic.com/
2. Click "Sign Up"
3. Enter your email and create a password
4. Verify your email

### Step 2: Add Payment Method

1. Go to: https://console.anthropic.com/settings/billing
2. Click "Add payment method"
3. Enter your card details

### Step 3: Get Your API Key

1. Go to: https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Give it a name like "TestGen-AI"
4. **Copy the key**: It looks like `sk-ant-...`

### Step 4: Set Up in TestGen AI

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Or in .env file
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Pricing:
- Claude 3 Haiku: ~$0.25 per 1M tokens (very cheap!)
- Claude 3 Sonnet: ~$3 per 1M tokens
- Claude 3 Opus: ~$15 per 1M tokens

---

## Option 3: Google Gemini (Great Free Tier!)

Google's Gemini models are excellent for code generation and have a generous free tier!

### Step 1: Get a Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
   - Or: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Select "Create API key in new project" (or choose existing)
4. **Copy the key**: It looks like `AIzaSy...`

### Step 2: Set Up in TestGen AI

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="AIzaSy-your-key-here"

# Or in .env file
GEMINI_API_KEY=AIzaSy-your-key-here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
```

### Available Models:
- **gemini-1.5-flash**: 🚀 Very fast, cheap, great for code
- **gemini-1.5-pro**: Higher quality, slower
- **gemini-pro**: Previous generation

### Pricing & Free Tier:
✨ **FREE TIER** (Very Generous!):
- Gemini 1.5 Flash: 15 RPM, 1M tokens/day
- Gemini 1.5 Pro: 2 RPM, 50 requests/day
- **Perfect for development and testing!**

**Paid Tier** (if you exceed free):
- Gemini 1.5 Flash: $0.075 per 1M input tokens (~$0.005 per test)
- Gemini 1.5 Pro: $1.25 per 1M input tokens (~$0.05 per test)

### Why Gemini?
✅ **FREE for most use cases** (1M tokens/day!)  
✅ Fast response times (Flash model)  
✅ Good at code generation  
✅ 1M token context window (huge!)  
✅ Easy to get started

---

## Option 4: Ollama (Free, Local - No API Key!)

Ollama runs models locally on your computer - completely free, no API key needed!

### Step 1: Install Ollama

**Windows:**
1. Go to: https://ollama.com/download
2. Download "Ollama for Windows"
3. Run the installer
4. Wait for installation to complete

**Verify Installation:**
```bash
ollama --version
```

### Step 2: Download a Model

```bash
# Download a good coding model (4GB, recommended)
ollama pull codellama:7b

# Or a smaller general model (2GB)
ollama pull llama2:7b

# Or the latest Llama 3
ollama pull llama3:8b
```

### Step 3: Test It Works

```bash
# Start a chat to test
ollama run codellama:7b

# Type: "Write a Python function to add two numbers"
# Press Ctrl+D to exit
```

### Step 4: Use in TestGen AI

No API key needed! Just set model name:
```bash
LLM_PROVIDER=ollama
LLM_MODEL=codellama:7b
```

### Pros and Cons:
✅ **Pros**: Free, private, no rate limits, works offline  
❌ **Cons**: Slower, requires good PC (8GB+ RAM), less accurate than GPT-4

---

## Quick Start: Choose Your Path

### Path 0: Best Value - Gemini (FREE!)
```bash
# Get API key from https://makersuite.google.com/app/apikey

# In your .env file:
GEMINI_API_KEY=AIzaSy-your-key-here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
```
**Cost**: FREE (1M tokens/day)!  
**Setup Time**: 2 minutes  
**Best For**: Everything! Fast, free, great quality

### Path 1: Quick Testing (Ollama - Free, Local)
```bash
# Install Ollama from https://ollama.com/download
ollama pull codellama:7b

# In your .env file:
LLM_PROVIDER=ollama
LLM_MODEL=codellama:7b
```
**Cost**: Free!  
**Setup Time**: 10 minutes  
**Best For**: Testing, learning, offline work

### Path 2: Best Quality (OpenAI GPT-4)
```bash
# Get API key from https://platform.openai.com/api-keys

# In your .env file:
OPENAI_API_KEY=sk-proj-your-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
```
**Cost**: ~$0.05 per test  
**Setup Time**: 5 minutes  
**Best For**: Production, best quality tests

### Path 3: Cost-Effective (OpenAI GPT-3.5)
```bash
# Same API key as GPT-4

# In your .env file:
OPENAI_API_KEY=sk-proj-your-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
```
**Cost**: ~$0.01 per test  
**Setup Time**: 5 minutes  
**Best For**: Budget-conscious production use

---

## Setting Up Your .env File

Create a file named `.env` in your project root:

```bash
# Choose ONE provider and uncomment:

# === OPTION 1: OpenAI ===
OPENAI_API_KEY=sk-proj-your-actual-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
# Or use: gpt-4-turbo-preview

# === OPTION 2: Anthropic ===
# ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
# LLM_PROVIDER=anthropic
# LLM_MODEL=claude-3-sonnet-20240229

# === OPTION 3: Ollama (Free) ===
# LLM_PROVIDER=ollama
# LLM_MODEL=codellama:7b
```

**IMPORTANT**: Add `.env` to `.gitignore` to keep your keys safe!

---

## Security Best Practices

1. **Never commit API keys to git**
   - Always use `.env` file
   - Add `.env` to `.gitignore`

2. **Use environment variables**
   ```bash
   # Set in PowerShell (temporary)
   $env:OPENAI_API_KEY="your-key"
   
   # Or in .env file (persistent)
   ```

3. **Rotate keys regularly**
   - Generate new keys every few months
   - Delete old keys from provider dashboard

4. **Set spending limits**
   - OpenAI: Set monthly budget in billing settings
   - Anthropic: Set budget alerts

5. **Monitor usage**
   - Check usage dashboard regularly
   - Set up email alerts for high usage

---

## Testing Your Setup

Once you have your API key set up, we'll create a simple test script to verify it works.

I'll help you create that in the next step!

---

## Need Help?

- **OpenAI Issues**: Check https://platform.openai.com/docs
- **Anthropic Issues**: Check https://docs.anthropic.com/
- **Ollama Issues**: Check https://ollama.com/docs

**Common Issues**:
- "Invalid API key": Check you copied the full key
- "Quota exceeded": Add payment method or check billing
- "Rate limit": Wait a minute and try again

---

## What's Next?

After setting up your API key, we'll:
1. Create the LLM client module
2. Test the connection
3. Start generating tests!

Ready to proceed? Let me know which provider you chose! 🚀

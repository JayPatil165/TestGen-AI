# Quick Start: Getting Your First API Key

Hey! Here's a super simple guide to get you started quickly. I recommend starting with **Ollama** (free, local) to test everything, then upgrading to OpenAI if you want better results.

---

## EASIEST PATH: Ollama (Free, No API Key!)

### 1. Install Ollama (5 minutes)

**Download Here**: https://ollama.com/download

- Click "Download for Windows"
- Run the installer
- It's about 500MB

### 2. Download a Model (5 minutes)

Open PowerShell and run:
```powershell
# This downloads a 4GB coding model (might take a few minutes)
ollama pull codellama:7b

# Test it works:
ollama run codellama:7b
# Type: "write a hello world function"
# Press Ctrl+D to exit
```

### 3. Create Your .env File

```powershell
# In your project directory
Copy-Item .env.example .env

# Edit the .env file and set:
LLM_PROVIDER=ollama
LLM_MODEL=codellama:7b
```

That's it! No API key needed! ✅

**Pros**: Free, private, works offline  
**Cons**: Needs 8GB+ RAM, slower than cloud LLMs

---

## BEST QUALITY: OpenAI GPT (Paid, ~$0.01 per test)

### 1. Sign Up (2 minutes)

**Go Here**: https://platform.openai.com/signup

- Sign up with email or Google
- Verify your email

### 2. Add Payment (3 minutes)

**Go Here**: https://platform.openai.com/settings/organization/billing/overview

- Click "Add payment method"
- Add your credit/debit card
- **You get $5 free credits!**

### 3. Create API Key (1 minute)

**Go Here**: https://platform.openai.com/api-keys

- Click "Create new secret key"
- Name it "TestGen-AI"
- **COPY THE KEY NOW!** (starts with `sk-proj-...`)
- Save it somewhere safe

### 4. Set Up in Project

```powershell
# Create .env file if you haven't
Copy-Item .env.example .env

# Open .env in notepad
notepad .env

# Find these lines and update:
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
```

Save and close! ✅

**Cost**: ~$0.01 per test with GPT-3.5-turbo, ~$0.05 with GPT-4

---

## Verify Your Setup

Let's check if everything works. I'll create a test script in the next step!

---

## Which Should You Choose?

**Start with Ollama if:**
- ✅ You want to learn/experiment for free
- ✅ You have a decent PC (8GB+ RAM)
- ✅ You don't mind slower generation
- ✅ You want privacy (everything local)

**Use OpenAI if:**
- ✅ You want the best quality tests
- ✅ You're okay with paying ~$0.01-0.05 per test
- ✅ You need fast generation
- ✅ You're building for production

**My Recommendation**: Start with Ollama to learn, then switch to OpenAI GPT-3.5-turbo for production!

---

## Need Help?

Just let me know:
1. Which provider you chose (Ollama or OpenAI)
2. If you got stuck anywhere
3. When you're ready to test the connection!

I'll help you get set up! 🚀

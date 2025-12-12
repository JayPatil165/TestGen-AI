# Setup Guide for Gemini API Key

Great news! You already have a Gemini API key! Gemini is an **excellent choice** for TestGen AI because:

✅ **FREE tier** with 1 million tokens per day  
✅ **Fast** - Gemini 1.5 Flash is very quick  
✅ **Great at code** - Built by Google, excellent for code generation  
✅ **Huge context** - 1M token context window  
✅ **No credit card required** for free tier

---

## Quick Setup (2 minutes)

### Step 1: Create .env File

```powershell
# In your project directory
Copy-Item .env.example .env
```

### Step 2: Edit .env File

Open the `.env` file in your favorite editor:

```powershell
notepad .env
```

### Step 3: Add Your Gemini Key

Find these lines and update them:

```bash
# Google Gemini Configuration (FREE tier available!)
GEMINI_API_KEY=YOUR-ACTUAL-GEMINI-KEY-HERE

# Provider and Model
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
```

**Replace** `YOUR-ACTUAL-GEMINI-KEY-HERE` with your actual Gemini API key!

### Step 4: Save and Close

That's it! ✅

---

## Gemini Models You Can Use

Your Gemini key gives you access to these models:

### gemini-1.5-flash (Recommended!)
- **Best for**: Fast test generation
- **Speed**: Very fast
- **Quality**: Excellent
- **Cost**: FREE (15 requests/min)
- **Use case**: Daily development

### gemini-1.5-pro
- **Best for**: Complex tests, high quality
- **Speed**: Slower but thorough
- **Quality**: Highest
- **Cost**: FREE (2 requests/min)
- **Use case**: Production, critical tests

### gemini-pro (Previous Gen)
- **Best for**: Simple tests
- **Speed**: Fast
- **Quality**: Good
- **Use case**: Simple projects

**My Recommendation**: Start with `gemini-1.5-flash` - it's the best balance!

---

## Test Your Setup

Once you've set up your `.env` file, we'll create a simple test to verify it works!

I'll help you with that in the next step.

---

## Free Tier Limits

You get these for FREE:

**Gemini 1.5 Flash:**
- 15 requests per minute
- 1 million tokens per day
- ~200-500 test generations per day

**Gemini 1.5 Pro:**
- 2 requests per minute  
- 50 requests per day
- ~10-50 test generations per day

**This is MORE than enough for development!** 🎉

---

## Next Steps

1. ✅ Create `.env` file
2. ✅ Add your Gemini key
3. 🔄 Test the connection (I'll help with this)
4. 🔄 Build the LLM integration module
5. 🔄 Generate your first tests!

Ready to test your setup? Let me know and I'll create a simple verification script! 🚀

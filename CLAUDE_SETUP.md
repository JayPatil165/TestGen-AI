# Claude (Anthropic) Setup Guide

Claude is already fully integrated into TestGen AI! Here's how to set it up.

---

## Why Claude?

✅ **Great at reasoning** - Excellent for complex test scenarios  
✅ **Long context** - 200K tokens (can handle huge files!)  
✅ **Helpful & harmless** - Well-behaved, safe outputs  
✅ **Multiple tiers** - Haiku (cheap), Sonnet (balanced), Opus (best)  

---

## Quick Setup (5 minutes)

### Step 1: Get Your Claude API Key

1. **Go to**: https://console.anthropic.com/
2. **Sign up** or log in
3. **Add payment method** (required even for initial credits)
4. **Go to API Keys**: https://console.anthropic.com/settings/keys
5. **Click** "Create Key"
6. **Name it**: "TestGen-AI"
7. **Copy the key**: Starts with `sk-ant-...`

### Step 2: Add to Your .env File

Open your `.env` file:
```powershell
notepad .env
```

Add your Claude key:
```bash
# Anthropic Claude Configuration
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
```

That's it! ✅

---

## Available Claude Models

### claude-3-5-sonnet-20241022 (Recommended!)
- **Best for**: Production test generation
- **Speed**: Fast
- **Quality**: Excellent
- **Context**: 200K tokens
- **Cost**: ~$3 per 1M input tokens (~$0.02 per test)
- **Use case**: Best balance of speed, quality, cost

### claude-3-5-haiku-20241022 (Cheapest)
- **Best for**: Simple tests, high volume
- **Speed**: Very fast
- **Quality**: Good
- **Context**: 200K tokens
- **Cost**: ~$0.25 per 1M tokens (~$0.002 per test)
- **Use case**: Budget-conscious development

### claude-3-opus-20240229 (Highest Quality)
- **Best for**: Complex, critical tests
- **Speed**: Slower
- **Quality**: Best available
- **Context**: 200K tokens
- **Cost**: ~$15 per 1M tokens (~$0.10 per test)
- **Use case**: Mission-critical production code

---

## Pricing

**Free Trial**: $5 credits when you sign up!

**Pricing Tiers**:
- Haiku: $0.25 / 1M input, $1.25 / 1M output
- Sonnet: $3 / 1M input, $15 / 1M output  
- Opus: $15 / 1M input, $75 / 1M output

**Estimated Test Generation Costs**:
- Haiku: ~$0.002 per test
- Sonnet: ~$0.02 per test
- Opus: ~$0.10 per test

---

## Compare: Claude vs Gemini vs OpenAI

| Feature | Claude Sonnet | Gemini Flash | GPT-4 Turbo |
|---------|---------------|--------------|-------------|
| **Free Tier** | $5 credits | 1M tokens/day | $5 credits |
| **Context Window** | 200K tokens | 1M tokens | 128K tokens |
| **Speed** | Fast | Very Fast | Fast |
| **Code Quality** | Excellent | Excellent | Excellent |
| **Cost/Test** | ~$0.02 | FREE | ~$0.05 |
| **Best For** | Reasoning | Daily dev | Best quality |

---

## Using Multiple Providers

You can add ALL provider keys to your `.env` and switch easily:

```bash
# Add all keys
GEMINI_API_KEY=AIzaSy-your-gemini-key
ANTHROPIC_API_KEY=sk-ant-your-claude-key
OPENAI_API_KEY=sk-your-openai-key

# Choose provider by changing these two lines:
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022

# Or use Gemini:
# LLM_PROVIDER=gemini
# LLM_MODEL=gemini-1.5-flash

# Or use OpenAI:
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4-turbo-preview
```

Then just comment/uncomment to switch! 🔄

---

## My Recommendation

**For You (with Gemini + Claude):**

1. **Daily Development**: Use **Gemini 1.5 Flash**
   - It's FREE (1M tokens/day)
   - Very fast
   - Great quality

2. **Important/Complex Tests**: Use **Claude 3.5 Sonnet**
   - Better reasoning
   - Handles complex scenarios
   - Worth the cost for critical code

3. **Simple Tests**: Use **Claude 3.5 Haiku**
   - Super cheap ($0.002/test)
   - Fast
   - Good enough for simple code

---

## Configuration Examples

### Example 1: Use Gemini by Default, Claude for Complex
```bash
# Primary (free!)
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash

# Keep Claude key for manual use when needed
ANTHROPIC_API_KEY=sk-ant-your-key
```

### Example 2: Use Claude Sonnet for Everything
```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-your-key
```

### Example 3: Use Cheap Claude Haiku
```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-haiku-20241022
ANTHROPIC_API_KEY=sk-ant-your-key
```

---

## Next Steps

1. ✅ Claude is already integrated in the code
2. ✅ Just add your API key to `.env`
3. ✅ Choose your model
4. 🔄 We'll test the connection next!

Ready to test your setup? Let me know! 🚀

# ⚠️ IMPORTANT: Update Your .env File

Your `.env` file needs to be updated with the correct Gemini model!

## What to Do:

Open your `.env` file and find this line:
```
LLM_MODEL=gemini-1.5-flash
```

Change it to:
```
LLM_MODEL=gemini-2.5-flash
```

## Why?

- Gemini 1.5 is no longer available on the free tier
- Gemini 2.5 Flash is the latest model
- It's faster and better!

## Quick Fix (Windows PowerShell):

```powershell
notepad .env
```

Then change `gemini-1.5-flash` to `gemini-2.5-flash`

Save and close!

---

✅ After this change, everything will work perfectly!

import google.generativeai as genai
from testgen.config import config

genai.configure(api_key=config.gemini_api_key)

print("Available Gemini Pro models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods and 'pro' in m.name.lower():
        print(f"  {m.name}")

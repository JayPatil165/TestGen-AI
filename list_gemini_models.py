import google.generativeai as genai
from testgen.config import config

genai.configure(api_key=config.gemini_api_key)

print("Available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  {m.name}")

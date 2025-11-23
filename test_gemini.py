"""
Test Gemini 2.5 Pro API connection
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

google_key = os.getenv('GOOGLE_API_KEY')
print(f"Google API Key found: {google_key[:20]}..." if google_key else "No key found")

if google_key:
    try:
        genai.configure(api_key=google_key)
        
        # List available models
        print("\nListing available models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
        
        # Try different models
        models_to_try = [
            'gemini-2.5-pro',
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-pro'
        ]
        
        for model_name in models_to_try:
            try:
                print(f"\nTrying {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    "Say 'Hello' in one word.",
                    generation_config=genai.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=10
                    )
                )
                print(f"✅ SUCCESS with {model_name}! Response: {response.text}")
                break
            except Exception as e:
                print(f"   Failed: {str(e)[:100]}...")
    except Exception as e:
        print(f"❌ ERROR: {e}")
else:
    print("❌ No Google API key found in .env")

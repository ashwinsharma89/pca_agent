"""
Test Claude API connection
"""
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

anthropic_key = os.getenv('ANTHROPIC_API_KEY')
print(f"Anthropic API Key found: {anthropic_key[:20]}..." if anthropic_key else "No key found")

if anthropic_key:
    try:
        client = Anthropic(api_key=anthropic_key)
        
        print("\nFetching available models...")
        # List available models
        import requests
        headers = {
            "x-api-key": anthropic_key,
            "anthropic-version": "2023-06-01"
        }
        response = requests.get("https://api.anthropic.com/v1/models", headers=headers)
        
        if response.status_code == 200:
            models_data = response.json()
            print(f"Available models: {[m['id'] for m in models_data.get('data', [])]}")
            
            # Try the first available model
            if models_data.get('data'):
                model_id = models_data['data'][0]['id']
                print(f"\nTesting with model: {model_id}")
                
                msg_response = client.messages.create(
                    model=model_id,
                    max_tokens=100,
                    messages=[{
                        "role": "user",
                        "content": "Say 'Hello, I am Claude and I am working!' in one sentence."
                    }]
                )
                print(f"✅ SUCCESS! Claude Response: {msg_response.content[0].text}")
            else:
                print("❌ No models available with this API key")
        else:
            print(f"❌ Failed to list models: {response.status_code} - {response.text}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
else:
    print("❌ No Anthropic API key found in .env")

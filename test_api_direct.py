#!/usr/bin/env python3
"""
Test OpenRouter API Key Directly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from openai import OpenAI
from secure_config import SecureConfig

def test_api_key():
    """Test the OpenRouter API key directly"""
    print("Testing OpenRouter API key...")
    
    secure_config = SecureConfig()
    api_key = secure_config.get_api_key()
    
    if not api_key:
        print("❌ No API key configured. Please run setup first.")
        return False
    
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://github.com/kranthiyelaboina/AutomatedPenetrationTesting",
                "X-Title": "AegisSec AutoPentest AI",
            },
            extra_body={},
            model="deepseek/deepseek-chat-v3.1:free",
            messages=[
                {
                    "role": "user",
                    "content": "Hello, test connection"
                }
            ],
            max_tokens=50
        )
        
        print("✅ API Connection Successful!")
        print(f"Response: {completion.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ API Connection Failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_key()

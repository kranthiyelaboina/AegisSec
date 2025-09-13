#!/usr/bin/env python3
"""
Test OpenRouter API Key Directly
"""

from openai import OpenAI

def test_api_key():
    """Test the OpenRouter API key directly"""
    print("Testing OpenRouter API key...")
    
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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"
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

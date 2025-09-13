#!/usr/bin/env python3
"""
Comprehensive API Key Troubleshooter
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_api_comprehensive():
    """Comprehensive API testing"""
    from rich.console import Console
    console = Console()
    
    console.print("[bold green]🔧 Comprehensive API Troubleshooter[/bold green]")
    
    # Test 1: Direct OpenAI client test
    console.print("\n[yellow]Test 1: Direct OpenAI Client[/yellow]")
    try:
        from openai import OpenAI
        
        api_key = "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"
        console.print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
        # Try different models
        models_to_test = [
            "deepseek/deepseek-chat-v3.1:free",
            "deepseek/deepseek-chat", 
            "openai/gpt-3.5-turbo"
        ]
        
        for model in models_to_test:
            try:
                console.print(f"Testing model: {model}")
                completion = client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "https://github.com/kranthiyelaboina/AutomatedPenetrationTesting",
                        "X-Title": "AegisSec AutoPentest AI",
                    },
                    extra_body={},
                    model=model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                console.print(f"✅ {model}: SUCCESS")
                console.print(f"Response: {completion.choices[0].message.content}")
                break
            except Exception as e:
                console.print(f"❌ {model}: {str(e)}")
        
    except Exception as e:
        console.print(f"❌ Direct test failed: {e}")
    
    # Test 2: DeepSeekClient test
    console.print(f"\n[yellow]Test 2: DeepSeekClient Test[/yellow]")
    try:
        from src.deepseek_client import DeepSeekClient
        from src.config_manager import ConfigManager
        
        config = ConfigManager()
        deepseek = DeepSeekClient(config)
        
        console.print(f"Client initialized: {deepseek.client is not None}")
        console.print(f"Model: {deepseek.model}")
        
        if deepseek.client:
            console.print("Testing tool recommendations...")
            criteria = {
                'category': 'network_mapping',
                'target': '127.0.0.1',
                'target_type': 'localhost',
                'description': 'Test'
            }
            
            tools = deepseek.get_tool_recommendations(criteria)
            console.print(f"✅ Tool recommendations: {tools[:3]}")
        else:
            console.print("❌ Client not available")
            
    except Exception as e:
        console.print(f"❌ DeepSeekClient test failed: {e}")
    
    # Test 3: Configuration test
    console.print(f"\n[yellow]Test 3: Configuration Test[/yellow]")
    try:
        from src.config_manager import ConfigManager
        config = ConfigManager()
        
        openrouter_config = config.get_openrouter_config()
        console.print(f"Config API Key: {openrouter_config.get('api_key', 'Not found')[:20]}...")
        console.print(f"Config Model: {openrouter_config.get('model', 'Not found')}")
        console.print(f"Config Base URL: {openrouter_config.get('base_url', 'Not found')}")
        
    except Exception as e:
        console.print(f"❌ Config test failed: {e}")

def test_alternative_models():
    """Test with alternative free models"""
    from openai import OpenAI
    from rich.console import Console
    
    console = Console()
    console.print("\n[yellow]Testing Alternative Free Models[/yellow]")
    
    api_key = "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"
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    
    # List of free models to try
    free_models = [
        "microsoft/phi-3-mini-128k-instruct:free",
        "google/gemma-7b-it:free",
        "meta-llama/llama-3-8b-instruct:free",
        "huggingfaceh4/zephyr-7b-beta:free"
    ]
    
    for model in free_models:
        try:
            response = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github.com/kranthiyelaboina/AutomatedPenetrationTesting",
                    "X-Title": "AegisSec AutoPentest AI",
                },
                extra_body={},
                model=model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            console.print(f"✅ {model}: {response.choices[0].message.content}")
            return model  # Return the first working model
        except Exception as e:
            console.print(f"❌ {model}: {str(e)}")
    
    return None

if __name__ == "__main__":
    test_api_comprehensive()
    working_model = test_alternative_models()
    
    if working_model:
        print(f"\n🎯 Found working model: {working_model}")
        print("This model can be used as fallback in the automation system.")
    else:
        print("\n❌ No working models found. API key may be invalid or expired.")

#!/usr/bin/env python3
"""
Test Hardcoded Configuration
Verify that API key works without dependency checking
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rich.console import Console
from hardcoded_config import HardcodedConfig

def test_hardcoded_config():
    """Test the hardcoded configuration"""
    console = Console()
    
    console.print("[bold green]🧪 Testing Hardcoded Configuration[/bold green]")
    
    # Test hardcoded config
    config = HardcodedConfig()
    
    console.print(f"✅ API Key Configured: {config.is_api_key_configured()}")
    console.print(f"✅ API Key Available: {'Yes' if config.get_api_key() else 'No'}")
    console.print(f"✅ Hashed Key: {config.get_hashed_key()[:20]}...")
    
    # Test setup (should bypass interactive input)
    console.print("\n[yellow]Testing setup bypass...[/yellow]")
    result = config.setup_api_key_interactive()
    console.print(f"✅ Setup Result: {result}")
    
    # Test DeepSeek client
    try:
        from deepseek_client import DeepSeekClient
        console.print("\n[yellow]Testing DeepSeek Client...[/yellow]")
        client = DeepSeekClient()
        console.print("✅ DeepSeek client initialized successfully")
        console.print(f"✅ Client has API access: {'Yes' if client.client else 'No'}")
    except Exception as e:
        console.print(f"❌ DeepSeek client error: {e}")
    
    console.print("\n[bold green]🎉 All tests completed![/bold green]")
    console.print("[dim]No dependency checking was performed during API configuration[/dim]")

if __name__ == "__main__":
    test_hardcoded_config()

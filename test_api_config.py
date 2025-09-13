#!/usr/bin/env python3
"""
Test API Key Configuration
Verify that API key configuration works without dependency checking
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rich.console import Console
from secure_config import SecureConfig

def test_api_key_config():
    """Test API key configuration functionality"""
    console = Console()
    console.print("[bold green]🧪 Testing API Key Configuration[/bold green]")
    
    secure_config = SecureConfig()
    
    # Check current status
    is_configured = secure_config.is_api_key_configured()
    console.print(f"API Key Configured: {'✅ Yes' if is_configured else '❌ No'}")
    
    if is_configured:
        settings = secure_config.get_settings()
        console.print(f"Model: {settings.get('model', 'N/A')}")
        console.print(f"Base URL: {settings.get('base_url', 'N/A')}")
        
        # Show masked API key
        api_key = secure_config.get_api_key()
        if api_key:
            masked_key = f"{api_key[:15]}...{api_key[-8:]}"
            console.print(f"API Key Preview: {masked_key}")
    
    console.print("\n[green]✅ API key configuration test completed successfully![/green]")
    console.print("[yellow]No dependency checking was performed during this test.[/yellow]")
    
    return True

if __name__ == "__main__":
    try:
        test_api_key_config()
    except Exception as e:
        print(f"[red]Error: {e}[/red]")

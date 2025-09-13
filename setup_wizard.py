#!/usr/bin/env python3
"""
AegisSec AutoPentest AI Setup Wizard
Initial configuration and API key setup
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rich.console import Console
from rich.prompt import Confirm
from secure_config import SecureConfig

def main():
    """Main setup wizard"""
    console = Console()
    
    console.print("""
[bold cyan]🔐 AegisSec AutoPentest AI Setup Wizard[/bold cyan]

[yellow]Welcome to AegisSec AutoPentest AI![/yellow]

This setup wizard will help you configure your system securely.
Your API key will be encrypted and stored locally on your machine.

[bold]What you'll need:[/bold]
• OpenRouter API account (free at openrouter.ai)
• A few minutes to complete setup
""")
    
    if not Confirm.ask("\nProceed with setup?", default=True):
        console.print("[yellow]Setup cancelled. You can run this again anytime with: python setup.py[/yellow]")
        return
    
    # Initialize secure config
    secure_config = SecureConfig()
    
    # Check if already configured
    if secure_config.is_api_key_configured():
        console.print("\n[green]✅ API key already configured![/green]")
        
        if Confirm.ask("Would you like to reconfigure your API key?"):
            if secure_config.setup_api_key_interactive():
                console.print("\n[green]🎉 Setup complete! Your system is ready.[/green]")
            else:
                console.print("\n[yellow]Setup incomplete. You can run setup again anytime.[/yellow]")
        else:
            console.print("\n[green]Your system is already configured and ready to use![/green]")
    else:
        # First time setup
        if secure_config.setup_api_key_interactive():
            console.print("\n[green]🎉 Setup complete! Your system is ready.[/green]")
            console.print("\n[bold]Next steps:[/bold]")
            console.print("• Run: [cyan]python main.py[/cyan] to start the main interface")
            console.print("• Run: [cyan]python test_api_direct.py[/cyan] to test your API connection")
            console.print("• Check the README.md for more usage examples")
        else:
            console.print("\n[yellow]Setup incomplete. You can run setup again anytime.[/yellow]")
            console.print("Alternative: Use the system in offline mode with limited functionality.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AegisSec AutoPentest AI Setup")
    parser.add_argument("--reset", action="store_true", help="Reset all configuration")
    args = parser.parse_args()
    
    if args.reset:
        console = Console()
        secure_config = SecureConfig()
        if Confirm.ask("Are you sure you want to reset all configuration?"):
            if secure_config.remove_api_key():
                console.print("[green]Configuration reset successfully.[/green]")
            else:
                console.print("[red]Error resetting configuration.[/red]")
        sys.exit(0)
    
    main()

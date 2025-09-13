#!/usr/bin/env python3
"""
Setup script for AutoPentest AI
Helps users configure the tool for first-time use
"""

import json
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

console = Console()

def display_banner():
    """Display setup banner"""
    banner_text = Text()
    banner_text.append("AutoPentest AI Setup", style="bold red")
    banner_text.append("\n🔧 Initial Configuration", style="cyan")
    
    panel = Panel(
        banner_text,
        title="[bold green]Welcome to Setup[/bold green]",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)

def check_dependencies():
    """Check if required dependencies are installed"""
    console.print("\n[yellow]Checking dependencies...[/yellow]")
    
    required_packages = [
        "typer", "rich", "requests", "jinja2", "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            console.print(f"✅ {package}")
        except ImportError:
            console.print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        console.print(f"\n[red]Missing packages: {', '.join(missing_packages)}[/red]")
        console.print("[yellow]Please run: pip install -r requirements.txt[/yellow]")
        return False
    
    console.print("\n[green]All dependencies are installed![/green]")
    return True

def setup_config():
    """Set up the configuration file"""
    console.print("\n[yellow]Setting up configuration...[/yellow]")
    
    config_dir = Path("config")
    config_file = config_dir / "config.json"
    example_file = config_dir / "config.example.json"
    
    # Load example config
    if not example_file.exists():
        console.print("[red]Example config file not found![/red]")
        return False
    
    with open(example_file, 'r') as f:
        config = json.load(f)
    
    # Get OpenRouter API key
    console.print("\n[cyan]OpenRouter API Configuration[/cyan]")
    console.print("Get your API key from: https://openrouter.ai/keys")
    
    api_key = Prompt.ask("Enter your OpenRouter API key", password=True)
    if api_key:
        config["openrouter"]["api_key"] = api_key
    else:
        console.print("[red]API key is required![/red]")
        return False
    
    # Ask about model preference
    console.print("\n[cyan]AI Model Selection[/cyan]")
    models = [
        "deepseek/deepseek-chat-v3.1:free",
        "microsoft/phi-3-mini-128k-instruct:free",
        "google/gemma-7b-it:free"
    ]
    
    console.print("Available models:")
    for i, model in enumerate(models, 1):
        console.print(f"{i}. {model}")
    
    choice = Prompt.ask("Select model", choices=["1", "2", "3"], default="1")
    config["openrouter"]["model"] = models[int(choice) - 1]
    
    # Ask about logging level
    console.print("\n[cyan]Logging Configuration[/cyan]")
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    
    for i, level in enumerate(log_levels, 1):
        console.print(f"{i}. {level}")
    
    choice = Prompt.ask("Select logging level", choices=["1", "2", "3", "4"], default="2")
    config["logging"]["level"] = log_levels[int(choice) - 1]
    
    # Save configuration
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        console.print(f"\n[green]Configuration saved to {config_file}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Failed to save configuration: {e}[/red]")
        return False

def create_directories():
    """Create necessary directories"""
    console.print("\n[yellow]Creating directories...[/yellow]")
    
    directories = ["logs", "reports", "config"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        console.print(f"✅ {dir_name}/")
    
    console.print("[green]All directories created![/green]")

def test_configuration():
    """Test the configuration"""
    console.print("\n[yellow]Testing configuration...[/yellow]")
    
    try:
        # Add src to path for imports
        sys.path.append(str(Path("src")))
        
        from config_manager import ConfigManager
        from deepseek_client import DeepSeekClient
        
        config_manager = ConfigManager()
        
        if not config_manager.validate_config():
            console.print("[red]Configuration validation failed![/red]")
            return False
        
        # Test API connection
        deepseek = DeepSeekClient(config_manager)
        
        console.print("Testing API connection...")
        response = deepseek.ask_advisor_question("What is penetration testing?")
        
        if response:
            console.print("[green]✅ API connection successful![/green]")
            console.print(f"[dim]AI Response: {response[:100]}...[/dim]")
            return True
        else:
            console.print("[red]❌ API connection failed![/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]Configuration test failed: {e}[/red]")
        return False

def show_next_steps():
    """Show next steps after setup"""
    console.print("\n[bold green]Setup Complete! 🎉[/bold green]")
    
    next_steps = """
Next Steps:

1. Run the tool:
   python main.py

2. Select CLI mode and choose a test type

3. Let the AI recommend tools for your scenario

4. Install any missing tools when prompted

5. Run automated penetration tests

6. View generated reports in the reports/ directory

For help:
- Check the README.md file
- Use the AI Advisor mode in the tool
- Visit the documentation
    """
    
    panel = Panel(
        next_steps.strip(),
        title="[bold cyan]Ready to Go![/bold cyan]",
        border_style="green"
    )
    console.print(panel)

def main():
    """Main setup workflow"""
    display_banner()
    
    # Check if already configured
    config_file = Path("config/config.json")
    if config_file.exists():
        if not Confirm.ask("Configuration already exists. Reconfigure?"):
            console.print("[yellow]Setup cancelled.[/yellow]")
            return
    
    # Setup workflow
    if not check_dependencies():
        console.print("[red]Please install dependencies first.[/red]")
        return
    
    create_directories()
    
    if not setup_config():
        console.print("[red]Configuration setup failed.[/red]")
        return
    
    if test_configuration():
        show_next_steps()
    else:
        console.print("[yellow]Setup completed but configuration test failed.[/yellow]")
        console.print("[yellow]You may need to check your API key or internet connection.[/yellow]")

if __name__ == "__main__":
    main()

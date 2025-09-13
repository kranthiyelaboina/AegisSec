#!/usr/bin/env python3
"""
AegisSec - Main Entry Point
AI-powered penetration testing automation tool
Developed by RunTime Terrors
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cli import AegisSecCLI
from config_manager import ConfigManager

console = Console()
app = typer.Typer(rich_markup_mode="rich")

def display_banner():
    """Display the AegisSec banner"""
    banner_text = Text()
    banner_text.append("AegisSec", style="bold red")
    banner_text.append("\n🛡️ AI-Powered Penetration Testing Automation", style="cyan")
    banner_text.append("\n⚡ Powered by DeepSeek v3.1", style="yellow")
    banner_text.append("\n🚀 Developed by RunTime Terrors", style="magenta")
    
    panel = Panel(
        banner_text,
        title="[bold green]Welcome[/bold green]",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)

def select_mode():
    """Let user select between CLI and GUI mode"""
    console.print("\n[bold yellow]Select Mode:[/bold yellow]")
    console.print("[cyan]1.[/cyan] CLI Mode (Interactive Terminal)")
    console.print("[cyan]2.[/cyan] GUI Mode (Graphical Interface) [dim](Coming Soon)[/dim]")
    
    choice = Prompt.ask("Choose mode", choices=["1", "2"], default="1")
    
    if choice == "2":
        console.print("[red]GUI mode is not implemented yet. Falling back to CLI mode.[/red]")
        return "cli"
    
    return "cli"

@app.command()
def main():
    """Launch AegisSec"""
    try:
        display_banner()
        
        # Check configuration
        config_manager = ConfigManager()
        if not config_manager.validate_config():
            console.print("[red]Configuration validation failed. Please check your config file.[/red]")
            console.print("[yellow]Run 'python setup.py' to configure the tool.[/yellow]")
            return
        
        # Select mode
        mode = select_mode()
        
        if mode == "cli":
            cli = AegisSecCLI(config_manager)
            cli.run()
        else:
            console.print("[red]GUI mode not implemented yet.[/red]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Please check your configuration and try again.[/yellow]")

if __name__ == "__main__":
    app()

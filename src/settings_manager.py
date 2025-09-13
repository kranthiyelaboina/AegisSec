#!/usr/bin/env python3
"""
Settings Manager for AegisSec
Handles API key configuration without dependency checking
"""

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from secure_config import SecureConfig

class SettingsManager:
    def __init__(self):
        self.console = Console()
        self.secure_config = SecureConfig()
    
    def show_settings_menu(self):
        """Display the main settings menu"""
        while True:
            self.console.clear()
            
            # Display banner
            banner_text = Text()
            banner_text.append("⚙️ AegisSec Settings", style="bold cyan")
            banner_text.append("\nSecure API Key Management", style="yellow")
            
            panel = Panel(
                banner_text,
                title="[bold green]Settings[/bold green]",
                border_style="blue",
                padding=(1, 2)
            )
            self.console.print(panel)
            
            # Show current status
            self._show_current_status()
            
            # Show menu options
            self.console.print("\n[bold]Available Options:[/bold]")
            self.console.print("1. 🔑 Configure API Key")
            self.console.print("2. 🔄 Update Existing API Key")
            self.console.print("3. 🧪 Test API Connection")
            self.console.print("4. ❌ Remove API Key")
            self.console.print("5. 📋 View Settings")
            self.console.print("6. 🚪 Exit Settings")
            
            choice = Prompt.ask("\n[green]Select option[/green]", choices=["1", "2", "3", "4", "5", "6"], default="6")
            
            if choice == "1":
                self._configure_api_key()
            elif choice == "2":
                self._update_api_key()
            elif choice == "3":
                self._test_api_connection()
            elif choice == "4":
                self._remove_api_key()
            elif choice == "5":
                self._view_settings()
            elif choice == "6":
                self.console.print("[yellow]Exiting settings...[/yellow]")
                break
    
    def _show_current_status(self):
        """Show current API key configuration status"""
        is_configured = self.secure_config.is_api_key_configured()
        settings = self.secure_config.get_settings()
        
        status_text = Text()
        if is_configured:
            status_text.append("✅ API Key: ", style="green")
            status_text.append("Configured and Encrypted", style="bold green")
        else:
            status_text.append("❌ API Key: ", style="red")
            status_text.append("Not Configured", style="bold red")
        
        status_text.append(f"\n🤖 Model: {settings.get('model', 'deepseek/deepseek-chat-v3.1:free')}", style="cyan")
        status_text.append(f"\n🌐 Endpoint: {settings.get('base_url', 'https://openrouter.ai/api/v1')}", style="cyan")
        
        panel = Panel(
            status_text,
            title="[bold yellow]Current Status[/bold yellow]",
            border_style="yellow"
        )
        self.console.print(panel)
    
    def _configure_api_key(self):
        """Configure API key without dependency checking"""
        self.console.print("\n[bold cyan]🔑 API Key Configuration[/bold cyan]")
        
        if self.secure_config.is_api_key_configured():
            self.console.print("[yellow]⚠️ API key is already configured.[/yellow]")
            if not Confirm.ask("Do you want to replace the existing key?"):
                return
        
        self.console.print("\n[bold]How to get your OpenRouter API key:[/bold]")
        self.console.print("1. Visit: [link]https://openrouter.ai/keys[/link]")
        self.console.print("2. Sign up or log in to your account")
        self.console.print("3. Create a new API key")
        self.console.print("4. Copy the key (starts with 'sk-or-v1-')")
        
        self.console.print("\n[green]Enter your API key below (it will be visible):[/green]")
        
        while True:
            api_key = Prompt.ask("[bold green]API Key[/bold green]")
            
            if not api_key.strip():
                if Confirm.ask("No API key entered. Exit configuration?"):
                    return
                continue
            
            # Basic validation
            if not api_key.startswith("sk-or-v1-"):
                self.console.print("[red]❌ Invalid format. OpenRouter API keys start with 'sk-or-v1-'[/red]")
                continue
            
            # Save the key
            if self.secure_config.save_api_key(api_key):
                self.console.print("[green]✅ API key saved successfully![/green]")
                self.console.print("[yellow]Testing connection...[/yellow]")
                
                # Test the key
                if self.secure_config._test_api_key(api_key):
                    self.console.print("[green]🎉 API key is working correctly![/green]")
                else:
                    self.console.print("[yellow]⚠️ API key saved but connection test failed.[/yellow]")
                    self.console.print("[dim]This might be due to network issues or key restrictions.[/dim]")
                
                Prompt.ask("\nPress Enter to continue...")
                return
            else:
                self.console.print("[red]❌ Failed to save API key. Please try again.[/red]")
    
    def _update_api_key(self):
        """Update existing API key"""
        if not self.secure_config.is_api_key_configured():
            self.console.print("[red]❌ No API key is currently configured.[/red]")
            if Confirm.ask("Would you like to configure one now?"):
                self._configure_api_key()
            return
        
        self.console.print("[yellow]Updating existing API key...[/yellow]")
        self._configure_api_key()
    
    def _test_api_connection(self):
        """Test the current API connection"""
        if not self.secure_config.is_api_key_configured():
            self.console.print("[red]❌ No API key configured to test.[/red]")
            return
        
        self.console.print("[yellow]Testing API connection...[/yellow]")
        
        api_key = self.secure_config.get_api_key()
        if self.secure_config._test_api_key(api_key):
            self.console.print("[green]✅ API connection successful![/green]")
            self.console.print("[dim]Your API key is working correctly.[/dim]")
        else:
            self.console.print("[red]❌ API connection failed.[/red]")
            self.console.print("[yellow]This could be due to:[/yellow]")
            self.console.print("• Network connectivity issues")
            self.console.print("• API key restrictions or expiration")
            self.console.print("• Service temporary unavailability")
        
        Prompt.ask("\nPress Enter to continue...")
    
    def _remove_api_key(self):
        """Remove the stored API key"""
        if not self.secure_config.is_api_key_configured():
            self.console.print("[yellow]No API key is currently configured.[/yellow]")
            return
        
        if Confirm.ask("[red]Are you sure you want to remove the stored API key?[/red]"):
            if self.secure_config.remove_api_key():
                self.console.print("[green]✅ API key removed successfully.[/green]")
            else:
                self.console.print("[red]❌ Failed to remove API key.[/red]")
        else:
            self.console.print("[yellow]Operation cancelled.[/yellow]")
        
        Prompt.ask("\nPress Enter to continue...")
    
    def _view_settings(self):
        """View current settings in detail"""
        settings = self.secure_config.get_settings()
        is_configured = self.secure_config.is_api_key_configured()
        
        self.console.print("\n[bold cyan]📋 Current Settings[/bold cyan]")
        
        settings_text = Text()
        settings_text.append(f"API Key Status: ", style="bold")
        if is_configured:
            settings_text.append("✅ Configured\n", style="green")
            api_key = self.secure_config.get_api_key()
            if api_key:
                preview = f"{api_key[:15]}...{api_key[-8:]}"
                settings_text.append(f"API Key Preview: {preview}\n", style="dim")
        else:
            settings_text.append("❌ Not Configured\n", style="red")
        
        settings_text.append(f"Model: {settings.get('model', 'N/A')}\n", style="cyan")
        settings_text.append(f"Base URL: {settings.get('base_url', 'N/A')}\n", style="cyan")
        settings_text.append(f"Storage Location: ~/.aegissec/secure.enc\n", style="dim")
        
        panel = Panel(
            settings_text,
            title="[bold green]Settings Details[/bold green]",
            border_style="green"
        )
        self.console.print(panel)
        
        Prompt.ask("\nPress Enter to continue...")

def main():
    """Main function for standalone settings management"""
    try:
        settings_manager = SettingsManager()
        settings_manager.show_settings_menu()
    except KeyboardInterrupt:
        print("\n[yellow]Settings cancelled by user.[/yellow]")
    except Exception as e:
        print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()

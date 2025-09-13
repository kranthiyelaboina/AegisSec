"""
Secure Configuration Manager for AegisSec AutoPentest AI
Handles secure storage and retrieval of sensitive data like API keys
"""

import os
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from rich.console import Console
from rich.prompt import Prompt, Confirm
from typing import Optional, Dict, Any

class SecureConfig:
    def __init__(self):
        self.console = Console()
        self.config_dir = Path.home() / ".aegissec"
        self.secure_config_file = self.config_dir / "secure.enc"
        self.settings_file = self.config_dir / "settings.json"
        self.machine_id_file = self.config_dir / ".machine_id"
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize encryption key
        self._init_encryption()
        
    def _init_encryption(self):
        """Initialize encryption using machine-specific key"""
        try:
            # Get or create machine ID
            if self.machine_id_file.exists():
                with open(self.machine_id_file, 'rb') as f:
                    salt = f.read()
            else:
                salt = os.urandom(16)
                with open(self.machine_id_file, 'wb') as f:
                    f.write(salt)
                # Hide the file on Windows
                try:
                    os.system(f'attrib +h "{self.machine_id_file}"')
                except:
                    pass
            
            # Create encryption key from machine-specific data
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(salt))
            self.cipher = Fernet(key)
            
        except Exception as e:
            self.console.print(f"[red]Error initializing encryption: {e}[/red]")
            self.cipher = None
    
    def _encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data"""
        if not self.cipher:
            return data.encode()
        return self.cipher.encrypt(data.encode())
    
    def _decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data"""
        if not self.cipher:
            return encrypted_data.decode()
        try:
            return self.cipher.decrypt(encrypted_data).decode()
        except:
            return ""
    
    def save_api_key(self, api_key: str) -> bool:
        """Securely save API key"""
        try:
            encrypted_key = self._encrypt_data(api_key)
            with open(self.secure_config_file, 'wb') as f:
                f.write(encrypted_key)
            
            # Also save to settings for reference (without the actual key)
            self._save_settings({
                "api_key_configured": True,
                "model": "deepseek/deepseek-chat-v3.1:free",
                "base_url": "https://openrouter.ai/api/v1"
            })
            
            self.console.print("[green]✅ API key saved securely[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Error saving API key: {e}[/red]")
            return False
    
    def get_api_key(self) -> Optional[str]:
        """Retrieve API key securely"""
        try:
            if not self.secure_config_file.exists():
                return None
            
            with open(self.secure_config_file, 'rb') as f:
                encrypted_data = f.read()
            
            api_key = self._decrypt_data(encrypted_data)
            return api_key if api_key else None
            
        except Exception as e:
            self.console.print(f"[red]Error retrieving API key: {e}[/red]")
            return None
    
    def _save_settings(self, settings: Dict[str, Any]):
        """Save non-sensitive settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            self.console.print(f"[red]Error saving settings: {e}[/red]")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get non-sensitive settings"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.console.print(f"[red]Error loading settings: {e}[/red]")
        
        return {
            "api_key_configured": False,
            "model": "deepseek/deepseek-chat-v3.1:free",
            "base_url": "https://openrouter.ai/api/v1"
        }
    
    def is_api_key_configured(self) -> bool:
        """Check if API key is configured"""
        return self.get_api_key() is not None
    
    def remove_api_key(self) -> bool:
        """Remove stored API key"""
        try:
            if self.secure_config_file.exists():
                self.secure_config_file.unlink()
            
            settings = self.get_settings()
            settings["api_key_configured"] = False
            self._save_settings(settings)
            
            self.console.print("[yellow]API key removed[/yellow]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error removing API key: {e}[/red]")
            return False
    
    def setup_api_key_interactive(self) -> bool:
        """Interactive API key setup"""
        self.console.print("\n[bold cyan]🔐 AegisSec API Key Setup[/bold cyan]")
        self.console.print("[yellow]Your API key will be stored securely and encrypted on your machine.[/yellow]")
        self.console.print("[dim]Location: ~/.aegissec/secure.enc[/dim]\n")
        
        self.console.print("[bold]To get your OpenRouter API key:[/bold]")
        self.console.print("1. Visit: https://openrouter.ai/keys")
        self.console.print("2. Sign up or log in")
        self.console.print("3. Create a new API key")
        self.console.print("4. Copy the key (starts with 'sk-or-v1-')")
        
        while True:
            api_key = Prompt.ask("\n[green]Enter your OpenRouter API key[/green]")
            
            if not api_key:
                if not Confirm.ask("No API key entered. Continue without API (offline mode)?"):
                    continue
                return False
            
            if not api_key.startswith("sk-or-v1-"):
                self.console.print("[red]❌ Invalid API key format. OpenRouter keys start with 'sk-or-v1-'[/red]")
                continue
            
            # Test the API key
            if self._test_api_key(api_key):
                return self.save_api_key(api_key)
            else:
                self.console.print("[red]❌ API key test failed. Please check your key.[/red]")
                if not Confirm.ask("Try again with a different key?"):
                    return False
    
    def _test_api_key(self, api_key: str) -> bool:
        """Test if API key is valid"""
        try:
            from openai import OpenAI
            
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
            
            response = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github.com/kranthiyelaboina/AutomatedPenetrationTesting",
                    "X-Title": "AegisSec AutoPentest AI"
                },
                model="deepseek/deepseek-chat-v3.1:free",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            
            self.console.print("[green]✅ API key test successful[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]API key test failed: {e}[/red]")
            return False
    
    def configure_settings_menu(self):
        """Interactive settings configuration menu"""
        while True:
            self.console.print("\n[bold cyan]⚙️  AegisSec Settings[/bold cyan]")
            settings = self.get_settings()
            
            self.console.print(f"API Key: {'✅ Configured' if settings.get('api_key_configured') else '❌ Not configured'}")
            self.console.print(f"Model: {settings.get('model', 'deepseek/deepseek-chat-v3.1:free')}")
            self.console.print(f"Base URL: {settings.get('base_url', 'https://openrouter.ai/api/v1')}")
            
            self.console.print("\n[bold]Options:[/bold]")
            self.console.print("1. Configure/Update API Key")
            self.console.print("2. Remove API Key")
            self.console.print("3. Test API Connection")
            self.console.print("4. Back to main menu")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="4")
            
            if choice == "1":
                self.setup_api_key_interactive()
            elif choice == "2":
                if Confirm.ask("Remove stored API key?"):
                    self.remove_api_key()
            elif choice == "3":
                api_key = self.get_api_key()
                if api_key:
                    self._test_api_key(api_key)
                else:
                    self.console.print("[red]❌ No API key configured[/red]")
            elif choice == "4":
                break

#!/usr/bin/env python3
"""
AegisSec Settings Configuration
Standalone script to configure API keys and settings
NO DEPENDENCY CHECKING - Direct configuration only
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from settings_manager import SettingsManager

if __name__ == "__main__":
    print("🔐 AegisSec Settings Manager")
    print("=" * 40)
    
    try:
        settings_manager = SettingsManager()
        settings_manager.show_settings_menu()
    except KeyboardInterrupt:
        print("\n[yellow]Settings cancelled by user.[/yellow]")
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        print("[yellow]If you encounter import errors, make sure you're in the correct directory.[/yellow]")

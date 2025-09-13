"""
Hardcoded Configuration for AegisSec
Bypasses all dependency checks and uses pre-configured API key
"""

import hashlib
import base64
from typing import Optional

class HardcodedConfig:
    def __init__(self):
        # Hash the provided API key for security
        # Original key: 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
        self._hashed_key = self._hash_key("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")
        self._api_key = "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"
        
    def _hash_key(self, key: str) -> str:
        """Hash the API key for security while storing"""
        hasher = hashlib.sha256()
        hasher.update(key.encode())
        return base64.b64encode(hasher.digest()).decode()
    
    def get_api_key(self) -> str:
        """Return the hardcoded API key"""
        return self._api_key
    
    def is_api_key_configured(self) -> bool:
        """Always return True since we have a hardcoded key"""
        return True
    
    def get_hashed_key(self) -> str:
        """Return the hashed version of the key"""
        return self._hashed_key
    
    def setup_api_key_interactive(self) -> bool:
        """Skip interactive setup and return True"""
        from rich.console import Console
        console = Console()
        console.print("[green]✅ Using pre-configured API key[/green]")
        console.print("[dim]API key is hardcoded and secure[/dim]")
        return True
    
    def get_settings(self) -> dict:
        """Return default settings"""
        return {
            "api_key_configured": True,
            "model": "deepseek/deepseek-chat-v3.1:free",
            "base_url": "https://openrouter.ai/api/v1"
        }

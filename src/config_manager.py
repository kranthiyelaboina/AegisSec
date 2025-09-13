"""
Configuration Manager for AutoPentest AI
Handles loading and validation of configuration files
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path"""
        base_dir = Path(__file__).parent.parent
        return str(base_dir / "config" / "config.json")
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if not os.path.exists(self.config_path):
                self._create_default_config()
            
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            return True
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            return False
    
    def _create_default_config(self):
        """Create default configuration file from example"""
        example_path = self.config_path.replace("config.json", "config.example.json")
        if os.path.exists(example_path):
            with open(example_path, 'r') as f:
                example_config = json.load(f)
            
            with open(self.config_path, 'w') as f:
                json.dump(example_config, f, indent=2)
    
    def validate_config(self) -> bool:
        """Validate configuration completeness"""
        required_sections = ["openrouter", "logging", "tools"]
        
        for section in required_sections:
            if section not in self.config:
                logging.error(f"Missing required config section: {section}")
                return False
        
        # Check API key
        api_key = self.config.get("openrouter", {}).get("api_key")
        if not api_key or api_key == "your_openrouter_api_key_here":
            logging.error("OpenRouter API key not configured")
            return False
        
        return True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_openrouter_config(self) -> Dict[str, str]:
        """Get OpenRouter API configuration"""
        return self.config.get("openrouter", {})
    
    def get_kali_tools(self) -> list:
        """Get list of Kali Linux tools"""
        return self.config.get("tools", {}).get("kali_tools", [])
    
    def get_profiles(self) -> Dict[str, Any]:
        """Get predefined testing profiles"""
        return self.config.get("profiles", {})
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            return False

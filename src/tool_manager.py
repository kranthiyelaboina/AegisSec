"""
Tool Manager for AutoPentest AI
Handles tool installation status checking and installation
"""

import subprocess
import shutil
import logging
import os
from typing import List, Dict, Optional
from config_manager import ConfigManager

class ToolManager:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.kali_tools = config_manager.get_kali_tools()
    
    def is_tool_installed(self, tool_name: str) -> bool:
        """Check if a tool is installed and available in PATH"""
        try:
            # First try to find it with 'which' (Unix/Linux) or 'where' (Windows)
            if os.name == 'nt':  # Windows
                result = subprocess.run(['where', tool_name], 
                                      capture_output=True, text=True, timeout=5)
            else:  # Unix/Linux
                result = subprocess.run(['which', tool_name], 
                                      capture_output=True, text=True, timeout=5)
            
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # Fallback: try to run the tool with --version or --help
            try:
                result = subprocess.run([tool_name, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                try:
                    result = subprocess.run([tool_name, '--help'], 
                                          capture_output=True, text=True, timeout=5)
                    return result.returncode == 0
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    return False
    
    def get_tool_version(self, tool_name: str) -> str:
        """Get the version of an installed tool"""
        if not self.is_tool_installed(tool_name):
            return "Not installed"
        
        try:
            # Try common version flags
            for flag in ['--version', '-v', '-V', 'version']:
                try:
                    result = subprocess.run([tool_name, flag], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and result.stdout.strip():
                        # Extract version from output (first line, first version-like string)
                        output = result.stdout.split('\n')[0]
                        return output[:100]  # Limit length
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    continue
            
            return "Unknown version"
            
        except Exception as e:
            logging.error(f"Error getting version for {tool_name}: {e}")
            return "Error"
    
    def check_missing_tools(self, required_tools: List[Dict[str, str]]) -> List[str]:
        """Check which required tools are missing"""
        missing = []
        
        for tool_info in required_tools:
            tool_name = tool_info.get('name', '')
            if tool_name and not self.is_tool_installed(tool_name):
                missing.append(tool_name)
        
        return missing
    
    def install_tools(self, tool_names: List[str]) -> Dict[str, bool]:
        """Attempt to install missing tools"""
        results = {}
        
        for tool in tool_names:
            results[tool] = self._install_single_tool(tool)
        
        return results
    
    def _install_single_tool(self, tool_name: str) -> bool:
        """Install a single tool using appropriate package manager"""
        try:
            # Detect the system and use appropriate package manager
            if self._is_kali_linux():
                return self._install_with_apt(tool_name)
            elif self._is_debian_ubuntu():
                return self._install_with_apt(tool_name)
            elif self._is_arch_linux():
                return self._install_with_pacman(tool_name)
            elif self._is_fedora_rhel():
                return self._install_with_dnf(tool_name)
            elif os.name == 'nt':  # Windows
                return self._install_on_windows(tool_name)
            else:
                logging.warning(f"Unknown system, cannot install {tool_name}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to install {tool_name}: {e}")
            return False
    
    def _is_kali_linux(self) -> bool:
        """Check if running on Kali Linux"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                return 'kali' in content
        except (FileNotFoundError, PermissionError):
            return False
    
    def _is_debian_ubuntu(self) -> bool:
        """Check if running on Debian or Ubuntu"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                return 'debian' in content or 'ubuntu' in content
        except (FileNotFoundError, PermissionError):
            return False
    
    def _is_arch_linux(self) -> bool:
        """Check if running on Arch Linux"""
        return os.path.exists('/etc/arch-release')
    
    def _is_fedora_rhel(self) -> bool:
        """Check if running on Fedora or RHEL"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                return 'fedora' in content or 'red hat' in content or 'rhel' in content
        except (FileNotFoundError, PermissionError):
            return False
    
    def _install_with_apt(self, tool_name: str) -> bool:
        """Install tool using apt package manager"""
        try:
            # Update package list first
            subprocess.run(['sudo', 'apt', 'update'], 
                         capture_output=True, timeout=30, check=True)
            
            # Install the tool
            result = subprocess.run(['sudo', 'apt', 'install', '-y', tool_name], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logging.info(f"Successfully installed {tool_name}")
                return True
            else:
                logging.error(f"Failed to install {tool_name}: {result.stderr}")
                return False
                
        except subprocess.SubprocessError as e:
            logging.error(f"Error installing {tool_name} with apt: {e}")
            return False
    
    def _install_with_pacman(self, tool_name: str) -> bool:
        """Install tool using pacman package manager"""
        try:
            result = subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', tool_name], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logging.info(f"Successfully installed {tool_name}")
                return True
            else:
                logging.error(f"Failed to install {tool_name}: {result.stderr}")
                return False
                
        except subprocess.SubprocessError as e:
            logging.error(f"Error installing {tool_name} with pacman: {e}")
            return False
    
    def _install_with_dnf(self, tool_name: str) -> bool:
        """Install tool using dnf package manager"""
        try:
            result = subprocess.run(['sudo', 'dnf', 'install', '-y', tool_name], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logging.info(f"Successfully installed {tool_name}")
                return True
            else:
                logging.error(f"Failed to install {tool_name}: {result.stderr}")
                return False
                
        except subprocess.SubprocessError as e:
            logging.error(f"Error installing {tool_name} with dnf: {e}")
            return False
    
    def _install_on_windows(self, tool_name: str) -> bool:
        """Attempt to install tool on Windows (limited support)"""
        # Windows installation is complex and tool-specific
        # For now, we'll just log that manual installation is needed
        logging.warning(f"Manual installation required for {tool_name} on Windows")
        return False
    
    def get_tool_command_template(self, tool_name: str, target: str = "TARGET") -> str:
        """Get a basic command template for a tool"""
        templates = {
            'nmap': f'nmap -sS -O {target}',
            'nikto': f'nikto -h {target}',
            'dirb': f'dirb http://{target}/',
            'gobuster': f'gobuster dir -u http://{target} -w /usr/share/wordlists/common.txt',
            'sqlmap': f'sqlmap -u "http://{target}/" --batch',
            'hydra': f'hydra -l admin -P /usr/share/wordlists/rockyou.txt {target} ssh',
            'wpscan': f'wpscan --url http://{target}/',
            'john': f'john --wordlist=/usr/share/wordlists/rockyou.txt hashfile',
            'hashcat': f'hashcat -m 0 hashfile /usr/share/wordlists/rockyou.txt',
            'aircrack-ng': f'aircrack-ng -w /usr/share/wordlists/rockyou.txt capture.cap',
            'recon-ng': f'recon-ng -m recon/domains-hosts/google_site_web -o SOURCE={target}',
        }
        
        return templates.get(tool_name, f'{tool_name} {target}')
    
    def validate_tool_safety(self, command: str) -> bool:
        """Basic validation to ensure command is relatively safe"""
        dangerous_patterns = [
            'rm -rf',
            'dd if=',
            'format',
            'mkfs',
            '> /dev/',
            'shutdown',
            'reboot',
            'halt',
            'init 0',
            'init 6'
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                logging.warning(f"Potentially dangerous command blocked: {command}")
                return False
        
        return True

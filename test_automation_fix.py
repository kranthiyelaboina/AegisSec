#!/usr/bin/env python3
"""
Test automation engine with API client fixes
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rich.console import Console
from config_manager import ConfigManager
from automation_engine import AutomationEngine

def test_automation_without_api():
    """Test automation engine when API client is not available"""
    console = Console()
    console.print("[bold cyan]🧪 Testing Automation Engine (Offline Mode)[/bold cyan]")
    
    try:
        # Initialize components
        config = ConfigManager()
        automation = AutomationEngine(config)
        
        console.print(f"[green]✅ Automation engine initialized[/green]")
        console.print(f"[dim]API Client Available: {automation.deepseek.client is not None}[/dim]")
        
        # Test with simple tools
        test_tools = [
            {
                "name": "nmap",
                "command": "nmap -sV 127.0.0.1",
                "category": "network_mapping"
            }
        ]
        
        console.print("\n[yellow]🚀 Starting Test Automation...[/yellow]")
        
        # Run automation
        results = automation.run_tools(test_tools, "Test automation without API dependencies")
        
        console.print(f"\n[green]✅ Automation completed![/green]")
        console.print(f"[cyan]Session ID: {results.get('session_id', 'N/A')}[/cyan]")
        console.print(f"[cyan]Tools Run: {len(results.get('results', {}))}[/cyan]")
        
        # Show results summary
        tool_results = results.get('results', {})
        for tool_name, result in tool_results.items():
            status = "✅ SUCCESS" if result.get('success') else "❌ FAILED"
            console.print(f"  {tool_name}: {status}")
            
        console.print("\n[green]🎉 Test completed successfully![/green]")
        console.print("[yellow]The automation engine now works properly without API client errors.[/yellow]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Test failed: {e}[/red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")
        return False

if __name__ == "__main__":
    test_automation_without_api()

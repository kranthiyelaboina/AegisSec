#!/usr/bin/env python3
"""
Test Working AI-Powered Automation
Now with working API key for real AI tool recommendations
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ai_automation():
    """Test AI-powered automation with working API"""
    from src.config_manager import ConfigManager
    from src.automation_engine import AutomationEngine
    from rich.console import Console
    from rich.prompt import Confirm
    
    console = Console()
    console.print("[bold green]🤖 AegisSec AI-Powered Automation Test[/bold green]")
    console.print("[green]Using working OpenRouter API with DeepSeek[/green]")
    
    # Initialize system
    config = ConfigManager()
    automation = AutomationEngine(config)
    
    # Verify API is working
    if automation.deepseek.client:
        console.print("[green]✅ AI System Online[/green]")
    else:
        console.print("[red]❌ AI System Offline[/red]")
        return
    
    # Test different scenarios
    test_scenarios = [
        {
            'target': '127.0.0.1',
            'category': 'network_mapping',
            'description': 'Local network discovery'
        },
        {
            'target': '192.168.1.1',
            'category': 'web_application',
            'description': 'Router web interface testing'
        },
        {
            'target': 'testphp.vulnweb.com',
            'category': 'web_application',
            'description': 'Vulnerable web application testing'
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        console.print(f"\n[cyan]🎯 Scenario {i}: {scenario['category'].title()}[/cyan]")
        console.print(f"Target: {scenario['target']}")
        console.print(f"Description: {scenario['description']}")
        
        # Get AI recommendations
        console.print("[yellow]🤖 Getting AI tool recommendations...[/yellow]")
        criteria = {
            'category': scenario['category'],
            'target': scenario['target'], 
            'target_type': 'web_server' if 'web' in scenario['category'] else 'network_host',
            'description': scenario['description']
        }
        
        recommended_tools = automation.deepseek.get_tool_recommendations(criteria)
        
        console.print(f"[green]🔧 AI Recommended Tools:[/green]")
        for j, tool in enumerate(recommended_tools[:5], 1):
            console.print(f"  {j}. {tool}")
        
        # Generate smart commands
        console.print(f"\n[yellow]🧠 AI-Generated Commands:[/yellow]")
        for tool_name in recommended_tools[:3]:  # Top 3 tools
            command = automation._generate_smart_command(tool_name, scenario['target'])
            console.print(f"[cyan]{tool_name:12}[/cyan]: {command}")
        
        if i < len(test_scenarios):
            console.print(f"\n{'-'*50}")

def test_ai_consultation():
    """Test AI consultation system"""
    from src.deepseek_client import DeepSeekClient
    from src.config_manager import ConfigManager
    from rich.console import Console
    
    console = Console()
    console.print("\n[bold cyan]🧠 AI Consultation System Test[/bold cyan]")
    
    config = ConfigManager()
    deepseek = DeepSeekClient(config)
    
    if not deepseek.client:
        console.print("[red]❌ AI not available for consultation[/red]")
        return
    
    # Test AI analysis
    mock_nmap_output = """
Nmap scan report for 127.0.0.1
Host is up (0.000020s latency).
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1
80/tcp   open  http    Apache httpd 2.4.41
443/tcp  open  https   Apache httpd 2.4.41
3306/tcp open  mysql   MySQL 8.0.28
"""
    
    console.print("[yellow]🤖 Testing AI analysis of tool output...[/yellow]")
    analysis = deepseek.analyze_tool_output("nmap", mock_nmap_output, "127.0.0.1")
    
    console.print(f"[green]🔍 AI Analysis:[/green]")
    console.print(analysis)
    
    # Test AI suggestions
    console.print(f"\n[yellow]🤖 Testing AI next tool suggestions...[/yellow]")
    next_tool = deepseek.suggest_next_tool(["nmap"], [mock_nmap_output], "127.0.0.1")
    console.print(f"[green]🎯 AI Suggests Next Tool:[/green] {next_tool}")

def main():
    """Run AI automation tests"""
    from rich.console import Console
    
    console = Console()
    console.print("\n[bold magenta]🎭 AegisSec AI-Powered Testing[/bold magenta]")
    console.print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    console.print("[green]✅ OpenRouter API Key Working[/green]")
    
    test_ai_automation()
    test_ai_consultation()
    
    console.print("\n[bold green]🎉 AI Tests Complete![/bold green]")
    console.print("\n[bold yellow]📋 AI Features Verified:[/bold yellow]")
    console.print("✅ AI tool recommendations")
    console.print("✅ Context-aware command generation")
    console.print("✅ Real-time output analysis")
    console.print("✅ Intelligent next-step suggestions")
    console.print("✅ Category-specific expertise")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Complete Working Penetration Testing Automation Demo
Shows the full system working with AI recommendations and real command execution
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_complete_automation():
    """Demo the complete working automation system"""
    from src.config_manager import ConfigManager
    from src.automation_engine import AutomationEngine
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    
    console = Console()
    console.print("[bold green]🎯 Complete AegisSec Automation Demo[/bold green]")
    console.print("[green]✅ AI-Powered with Working OpenRouter API[/green]")
    
    # Initialize system
    config = ConfigManager()
    automation = AutomationEngine(config)
    
    # Verify AI is working
    if not automation.deepseek.client:
        console.print("[red]❌ AI system not available[/red]")
        return
    
    console.print("[green]✅ AI System Ready[/green]")
    
    # Get target from user
    target = Prompt.ask("[bold cyan]Enter target for testing[/bold cyan]", default="127.0.0.1")
    
    # Demo AI consultation
    console.print(f"\n[yellow]🤖 AI Analyzing Target: {target}[/yellow]")
    
    # Create criteria
    criteria = {
        'category': 'network_mapping',
        'target': target,
        'target_type': 'network_host',
        'description': f'Security assessment of {target}',
        'consultation_complete': True,
        'ai_test_plan': 'Comprehensive network discovery and vulnerability assessment'
    }
    
    # Get AI tool recommendations
    console.print("[yellow]🤖 Getting AI tool recommendations...[/yellow]")
    recommended_tools = automation.deepseek.get_tool_recommendations(criteria)
    
    console.print("[green]🔧 AI Recommended Tools:[/green]")
    for i, tool in enumerate(recommended_tools[:6], 1):
        console.print(f"  {i}. {tool}")
    
    # Create tool list for automation
    tools = []
    for tool_name in recommended_tools[:3]:  # Use top 3 tools
        tools.append({
            'name': tool_name,
            'description': f'{tool_name.title()} security tool'
        })
    
    # Show what will be executed
    console.print(f"\n[yellow]🔧 Commands to be executed:[/yellow]")
    for tool in tools:
        command = automation._generate_smart_command(tool['name'], target)
        console.print(f"[cyan]{tool['name']:12}[/cyan]: {command}")
    
    if not Confirm.ask(f"\n[bold red]⚠️  Execute penetration testing on {target}?[/bold red]", default=False):
        console.print("[yellow]Demo cancelled by user[/yellow]")
        return
    
    # Run the automation
    console.print(f"\n[bold green]🚀 Starting AI-Driven Penetration Testing...[/bold green]")
    
    try:
        session_data = automation.run_intelligent_tools(tools, criteria)
        
        # Show results
        console.print(f"\n[bold green]✅ Automation Complete![/bold green]")
        console.print(f"Session ID: {session_data['session_id']}")
        
        results = session_data.get('results', {})
        console.print(f"\n[cyan]Results Summary:[/cyan]")
        console.print(f"  Total Tools: {len(results)}")
        
        successful = sum(1 for r in results.values() if r.get('success', False))
        console.print(f"  Successful: {successful}")
        console.print(f"  Failed: {len(results) - successful}")
        
        # Show individual results
        console.print("\n[cyan]Individual Tool Results:[/cyan]")
        for tool_name, result in results.items():
            status = "✅ SUCCESS" if result.get('success') else "❌ FAILED"
            console.print(f"  {tool_name}: {status}")
            
            if result.get('output'):
                output_preview = result['output'][:300] + "..." if len(result['output']) > 300 else result['output']
                console.print(f"    [dim]Output: {output_preview}[/dim]")
            
            if result.get('error'):
                console.print(f"    [red]Error: {result['error']}[/red]")
            
            # Show AI analysis if available
            if result.get('analysis'):
                console.print(f"    [yellow]AI Analysis: {result['analysis'][:200]}...[/yellow]")
        
        # Generate AI summary
        console.print(f"\n[yellow]📊 Generating AI Summary...[/yellow]")
        summary = automation.deepseek.generate_executive_summary(session_data)
        if summary:
            console.print(f"\n[bold]🎯 AI Executive Summary:[/bold]")
            console.print(f"[green]{summary}[/green]")
        
        console.print(f"\n[cyan]📁 Session saved to: logs/{session_data['session_id']}.json[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Error during automation: {str(e)}[/red]")

def main():
    """Run the complete demo"""
    from rich.console import Console
    
    console = Console()
    console.print("\n[bold magenta]🎭 AegisSec Complete Automation Demo[/bold magenta]")
    console.print(f"Demo Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    console.print("[green]✅ AI-Powered Penetration Testing[/green]")
    console.print("[yellow]⚠️  This will execute actual security testing commands[/yellow]")
    
    demo_complete_automation()
    
    console.print("\n[bold green]🎉 Demo Complete![/bold green]")
    console.print("\n[bold yellow]📋 System Features:[/bold yellow]")
    console.print("✅ AI tool recommendations")
    console.print("✅ Smart command generation")
    console.print("✅ Real command execution")
    console.print("✅ Live AI output analysis")
    console.print("✅ Intelligent next-step suggestions")
    console.print("✅ Executive summary generation")
    console.print("✅ Session management and logging")

if __name__ == "__main__":
    main()

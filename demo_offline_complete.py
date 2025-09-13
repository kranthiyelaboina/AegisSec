#!/usr/bin/env python3
"""
Complete Offline Automation Demo
Shows the full penetration testing automation working perfectly without AI API
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_offline_automation():
    """Demonstrate complete penetration testing automation in offline mode"""
    from src.config_manager import ConfigManager
    from src.automation_engine import AutomationEngine
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    
    console = Console()
    console.print("[bold green]🎯 AegisSec Offline Penetration Testing Demo[/bold green]")
    console.print("[yellow]✅ Fully functional without AI API dependency[/yellow]")
    
    # Initialize system
    config = ConfigManager()
    automation = AutomationEngine(config)
    
    # Show system status
    console.print(f"\n[cyan]System Status:[/cyan]")
    console.print(f"  AI API: {'❌ Offline' if not automation.deepseek.client else '✅ Online'}")
    console.print(f"  Smart Commands: ✅ Active")
    console.print(f"  Tool Validation: ✅ Active")
    console.print(f"  Command Execution: ✅ Ready")
    
    # Get target
    target = Prompt.ask("[bold cyan]Enter target for penetration testing[/bold cyan]", default="127.0.0.1")
    
    # Show offline capabilities
    console.print(f"\n[yellow]🧠 Offline Smart Tool Selection for {target}:[/yellow]")
    
    # Create criteria for offline tool selection
    criteria = {
        'category': 'network_mapping',
        'target': target,
        'target_type': 'network_host',
        'description': f'Security assessment of {target}',
        'consultation_complete': True,
        'ai_test_plan': 'Comprehensive network discovery and vulnerability assessment'
    }
    
    # Get fallback tool recommendations (works offline)
    recommended_tools = automation.deepseek.get_tool_recommendations(criteria)
    
    console.print("[green]🔧 Smart Tool Selection (Offline Mode):[/green]")
    for i, tool in enumerate(recommended_tools[:6], 1):
        console.print(f"  {i}. {tool}")
    
    # Create tool list
    tools = []
    selected_tools = recommended_tools[:4]  # Top 4 tools
    for tool_name in selected_tools:
        tools.append({
            'name': tool_name,
            'description': f'{tool_name.title()} security tool'
        })
    
    # Show smart command generation
    console.print(f"\n[yellow]🔧 Smart Commands to Execute:[/yellow]")
    for tool in tools:
        command = automation._generate_smart_command(tool['name'], target)
        console.print(f"[cyan]{tool['name']:12}[/cyan]: {command}")
    
    console.print(f"\n[bold yellow]⚠️  This will execute REAL penetration testing commands on {target}[/bold yellow]")
    if not Confirm.ask(f"[bold red]Execute penetration testing automation?[/bold red]", default=False):
        console.print("[yellow]Demo cancelled by user[/yellow]")
        return
    
    # Execute the automation
    console.print(f"\n[bold green]🚀 Starting Offline Penetration Testing Automation...[/bold green]")
    
    try:
        session_data = automation.run_intelligent_tools(tools, criteria)
        
        # Show results
        console.print(f"\n[bold green]✅ Penetration Testing Complete![/bold green]")
        console.print(f"Session ID: {session_data['session_id']}")
        
        results = session_data.get('results', {})
        console.print(f"\n[cyan]📊 Results Summary:[/cyan]")
        console.print(f"  Total Tools Executed: {len(results)}")
        
        successful = sum(1 for r in results.values() if r.get('success', False))
        console.print(f"  Successful: {successful}")
        console.print(f"  Failed: {len(results) - successful}")
        
        # Show detailed results
        console.print(f"\n[cyan]📋 Detailed Results:[/cyan]")
        for tool_name, result in results.items():
            status = "✅ SUCCESS" if result.get('success') else "❌ FAILED"
            duration = result.get('duration', 0)
            console.print(f"  {tool_name}: {status} ({duration:.2f}s)")
            
            if result.get('output'):
                # Show first few lines of output
                output_lines = result['output'].split('\n')[:3]
                for line in output_lines:
                    if line.strip():
                        console.print(f"    [dim]{line[:80]}{'...' if len(line) > 80 else ''}[/dim]")
            
            if result.get('error'):
                console.print(f"    [red]Error: {result['error'][:100]}[/red]")
        
        # Generate offline summary
        console.print(f"\n[yellow]📊 Generating Offline Summary...[/yellow]")
        summary = f"""
Penetration Testing Summary for {target}:

Tools Executed: {', '.join(results.keys())}
Success Rate: {successful}/{len(results)} ({(successful/len(results)*100):.1f}%)

Key Findings:
- Network accessibility tested with {len([r for r in results.values() if 'nmap' in str(r)])} discovery tools
- Web services analyzed with {len([r for r in results.values() if any(web_tool in str(r) for web_tool in ['nikto', 'dirb', 'gobuster'])])} web scanners
- Security vulnerabilities assessed across {len(results)} different attack vectors

Recommendations:
1. Review all successful tool outputs for discovered services and potential vulnerabilities
2. Investigate any failed tools - they may indicate security controls or misconfigurations
3. Conduct deeper testing on discovered services using specialized tools
4. Document findings and create remediation plan

Session saved to: logs/{session_data['session_id']}.json
"""
        
        console.print(f"[green]{summary}[/green]")
        console.print(f"\n[cyan]📁 Full session data saved to: logs/{session_data['session_id']}.json[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Error during automation: {str(e)}[/red]")

def show_api_key_instructions():
    """Show instructions for getting a working API key"""
    from rich.console import Console
    
    console = Console()
    console.print("\n[bold cyan]🔑 How to Get Working OpenRouter API Key:[/bold cyan]")
    console.print("\n[yellow]1. Visit OpenRouter.ai[/yellow]")
    console.print("   - Go to https://openrouter.ai/")
    console.print("   - Create a free account")
    
    console.print("\n[yellow]2. Get API Key[/yellow]")
    console.print("   - Go to Settings > API Keys")
    console.print("   - Click 'Create API Key'")
    console.print("   - Copy the key (starts with 'sk-or-v1-')")
    
    console.print("\n[yellow]3. Add Credits (Optional)[/yellow]")
    console.print("   - Free tier has limited usage")
    console.print("   - Add $5-10 for extensive testing")
    
    console.print("\n[yellow]4. Update the System[/yellow]")
    console.print("   - Replace API key in: src/deepseek_client.py line 20")
    console.print("   - Replace API key in: config/config.json")
    
    console.print("\n[green]✅ Note: The system works perfectly in offline mode![/green]")
    console.print("[green]   All penetration testing automation functions normally without AI[/green]")

def main():
    """Run the complete offline demo"""
    from rich.console import Console
    
    console = Console()
    console.print("\n[bold magenta]🎭 AegisSec Complete Offline Demo[/bold magenta]")
    console.print(f"Demo Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    demo_offline_automation()
    show_api_key_instructions()
    
    console.print("\n[bold green]🎉 Demo Complete![/bold green]")
    console.print("\n[bold yellow]📋 Offline System Features:[/bold yellow]")
    console.print("✅ Smart tool selection (no AI needed)")
    console.print("✅ Context-aware command generation")
    console.print("✅ Real penetration testing execution")
    console.print("✅ Safety validation")
    console.print("✅ Session management and logging")
    console.print("✅ Comprehensive reporting")
    console.print("✅ Intelligent tool chaining")

if __name__ == "__main__":
    main()

"""
Automation Engine for AegisSec
Handles automated execution of penetration testing tools with intelligent chaining
Developed by RunTime Terrors
"""

import subprocess
import logging
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from config_manager import ConfigManager
from tool_manager import ToolManager
from deepseek_client import DeepSeekClient

class AutomationEngine:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.tool_manager = ToolManager(config_manager)
        self.deepseek = DeepSeekClient(config_manager)  # Pass config manager
        self.logs_dir = Path(__file__).parent.parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.setup_logging()
    
    def setup_logging(self):
        """Set up automation logging"""
        log_format = self.config.get("logging.format", 
                                   "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_level = self.config.get("logging.level", "INFO")
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=[
                logging.FileHandler(self.logs_dir / "automation.log"),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_tools(self, tools: List[Dict[str, str]], criteria: str) -> Dict[str, Any]:
        """Run a list of tools and collect results"""
        session_id = self._generate_session_id()
        session_data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "criteria": criteria,
            "tools": tools,
            "results": {},
            "summary": {}
        }
        
        self.logger.info(f"Starting automation session: {session_id}")
        
        # Run tools with intelligent chaining
        executed_tools = []
        remaining_tools = [tool_info.get('name', '') for tool_info in tools if tool_info.get('name')]
        
        for tool_info in tools:
            tool_name = tool_info.get('name', '')
            if not tool_name:
                continue
            
            self.logger.info(f"Running tool: {tool_name}")
            
            # Generate command for the tool
            if executed_tools:
                # Use previous outputs to inform next command
                previous_output = self._get_last_tool_output(session_data["results"])
                command = self._generate_intelligent_command(tool_info, criteria, previous_output)
            else:
                command = self._generate_command(tool_info, criteria)
            
            if not command:
                self.logger.error(f"Could not generate command for {tool_name}")
                continue
            
            # Execute the tool
            result = self._execute_tool_with_retry(tool_name, command)
            session_data["results"][tool_name] = result
            executed_tools.append(tool_name)
            remaining_tools.remove(tool_name)
            
            # Analyze the output with AI
            if result.get("success") and result.get("output"):
                analysis = self.deepseek.analyze_tool_output(tool_name, result["output"])
                if analysis:
                    session_data["results"][tool_name]["analysis"] = analysis
                
                # Get AI suggestion for next command based on this output
                if remaining_tools:
                    next_command = self.deepseek.get_next_command(
                        tool_name, result["output"], 
                        self._extract_target_from_criteria(criteria), 
                        remaining_tools
                    )
                    if next_command:
                        session_data["results"][tool_name]["ai_next_suggestion"] = next_command
        
        # Save session data
        self._save_session(session_id, session_data)
        
        return session_data
    
    def run_intelligent_tools(self, tools: List[Dict[str, str]], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Run tools with DeepSeek AI handling the entire automation process with consultation data"""
        session_id = self._generate_session_id()
        
        # Handle both old string format and new dict format for backward compatibility
        if isinstance(criteria, str):
            criteria_text = criteria
            target = self._extract_target_from_criteria(criteria)
            consultation_data = {}
        else:
            criteria_text = criteria.get('description', criteria.get('target', 'Unknown criteria'))
            target = criteria.get('target', 'Unknown')
            consultation_data = {
                'consultation_complete': criteria.get('consultation_complete', False),
                'ai_test_plan': criteria.get('ai_test_plan', ''),
                'conversation_history': criteria.get('conversation_history', []),
                'test_parameters': criteria.get('test_parameters', {}),
                'category': criteria.get('category', 'general')
            }
        
        session_data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "criteria": criteria_text,
            "target": target,
            "tools": tools,
            "results": {},
            "summary": {},
            "intelligence_log": [],
            "ai_decisions": [],
            "consultation_data": consultation_data,
            "intelligent_chaining": True
        }
        
        self.logger.info(f"Starting AI-driven automation session: {session_id}")
        if consultation_data.get('consultation_complete'):
            self.logger.info(f"Using consultation-informed automation with {len(consultation_data.get('conversation_history', []))} consultation exchanges")
        
        # Let DeepSeek AI orchestrate the entire penetration testing process
        return self._ai_driven_penetration_test(session_data, target)
    
    def _ai_driven_penetration_test(self, session_data: Dict[str, Any], target: str) -> Dict[str, Any]:
        """Complete AI-driven penetration testing orchestration"""
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
        
        console = Console()
        tools = session_data["tools"]
        
        console.print(f"\n[bold cyan]🤖 AI Taking Control - Autonomous Penetration Testing[/bold cyan]")
        console.print(f"[yellow]Target: {target}[/yellow]")
        console.print(f"[yellow]Available Tools: {len(tools)}[/yellow]")
        
        executed_commands = []
        all_outputs = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            
            # Step 1: AI decides the first tool and command
            task = progress.add_task("AI analyzing target and selecting first tool...", total=len(tools))
            
            first_tool = self._ai_select_first_tool(tools, target)
            first_command = self._ai_generate_command(first_tool, target, [])
            
            console.print(f"\n[green]🔍 AI Decision: Starting with {first_tool['name']}[/green]")
            console.print(f"[dim]Command: {first_command}[/dim]")
            
            # Execute first command
            result = self._execute_ai_command(first_tool['name'], first_command, target)
            executed_commands.append({'tool': first_tool['name'], 'command': first_command, 'result': result})
            all_outputs.append(result['output'])
            
            session_data["results"][first_tool['name']] = result
            progress.advance(task)
            
            # AI-driven iterative process
            current_tool_index = 1
            max_iterations = len(tools)
            
            for iteration in range(1, max_iterations):
                progress.update(task, description=f"AI analyzing results and planning next step ({iteration}/{max_iterations})...")
                
                # AI analyzes all previous outputs and decides next action
                ai_analysis = self.deepseek.analyze_tool_output(
                    executed_commands[-1]['tool'], 
                    executed_commands[-1]['result']['output'], 
                    target
                )
                
                session_data["ai_decisions"].append({
                    "iteration": iteration,
                    "analysis": ai_analysis,
                    "previous_tool": executed_commands[-1]['tool']
                })
                
                console.print(f"\n[cyan]🧠 AI Analysis: {ai_analysis[:100]}...[/cyan]")
                
                # AI suggests next tool
                remaining_tools = [t for t in tools if t['name'] not in [cmd['tool'] for cmd in executed_commands]]
                
                if not remaining_tools:
                    console.print("[yellow]All tools executed. AI finishing analysis...[/yellow]")
                    break
                
                next_tool_name = self.deepseek.suggest_next_tool(
                    [cmd['tool'] for cmd in executed_commands],
                    [cmd['result']['output'][:200] for cmd in executed_commands],
                    target
                )
                
                # Find the tool object
                next_tool = None
                for tool in remaining_tools:
                    if tool['name'].lower() == next_tool_name.lower():
                        next_tool = tool
                        break
                
                if not next_tool and remaining_tools:
                    next_tool = remaining_tools[0]  # Fallback
                
                if next_tool:
                    # AI generates command based on all previous outputs
                    next_command = self._ai_generate_adaptive_command(
                        next_tool, target, executed_commands
                    )
                    
                    console.print(f"\n[green]🔍 AI Decision: Next tool {next_tool['name']}[/green]")
                    console.print(f"[dim]Command: {next_command}[/dim]")
                    
                    # Execute AI-generated command
                    result = self._execute_ai_command(next_tool['name'], next_command, target)
                    executed_commands.append({'tool': next_tool['name'], 'command': next_command, 'result': result})
                    all_outputs.append(result['output'])
                    
                    session_data["results"][next_tool['name']] = result
                    
                progress.advance(task)
            
            progress.update(task, description="AI generating final analysis and recommendations...")
            
            # Final AI analysis and summary
            final_analysis = self._ai_final_analysis(executed_commands, target)
            session_data["ai_final_analysis"] = final_analysis
            
            console.print(f"\n[bold green]✅ AI Penetration Test Complete![/bold green]")
            console.print(f"[yellow]Executed {len(executed_commands)} tools autonomously[/yellow]")
            
        return session_data
    
    def _ai_select_first_tool(self, tools: List[Dict], target: str) -> Dict:
        """AI selects the best first tool for the target"""
        try:
            # Ask AI to select the best starting tool
            tool_names = [tool['name'] for tool in tools]
            selected_name = self.deepseek.suggest_next_tool([], [], target)
            
            # Find the tool object
            for tool in tools:
                if tool['name'].lower() == selected_name.lower():
                    return tool
        except:
            pass
        
        # Fallback to nmap if available, otherwise first tool
        for tool in tools:
            if 'nmap' in tool['name'].lower():
                return tool
        return tools[0] if tools else {'name': 'nmap', 'description': 'Network scanner'}
    
    def _ai_generate_command(self, tool: Dict, target: str, previous_outputs: List[str]) -> str:
        """AI generates the appropriate command for the tool"""
        tool_name = tool.get('name', '')
        
        try:
            if self.deepseek.client and previous_outputs:
                # Use AI to generate adaptive command
                ai_command = self.deepseek.get_next_command(
                    tool_name, 
                    '\n'.join(previous_outputs[-2:]),  # Last 2 outputs for context
                    target, 
                    [tool_name]
                )
                if ai_command and self._validate_command(ai_command):
                    return ai_command
        except Exception as e:
            self.logger.warning(f"AI command generation failed: {e}")
        
        # Fallback to predefined smart commands
        return self._generate_smart_command(tool_name, target, previous_outputs)
    
    def _generate_smart_command(self, tool_name: str, target: str, previous_outputs: List[str] = None) -> str:
        """Generate smart penetration testing commands based on tool and context"""
        # Analyze previous outputs for context
        found_ports = []
        found_services = []
        found_dirs = []
        
        if previous_outputs:
            for output in previous_outputs:
                # Extract open ports
                import re
                port_matches = re.findall(r'(\d+)/tcp\s+open\s+(\w+)', output)
                for port, service in port_matches:
                    if port not in found_ports:
                        found_ports.append(port)
                    if service not in found_services:
                        found_services.append(service)
                
                # Extract directories
                dir_matches = re.findall(r'200\s+\d+\s+([/\w\-\.]+)', output)
                found_dirs.extend(dir_matches)
        
        # Generate context-aware commands
        basic_commands = {
            'nmap': self._generate_nmap_command(target, found_ports),
            'nikto': f'nikto -h {target}',
            'sqlmap': self._generate_sqlmap_command(target, found_dirs),
            'dirb': f'dirb http://{target}/ /usr/share/wordlists/dirb/common.txt',
            'gobuster': f'gobuster dir -u http://{target}/ -w /usr/share/wordlists/dirb/common.txt -x php,html,txt,js',
            'hydra': self._generate_hydra_command(target, found_services),
            'john': 'john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt',
            'metasploit': self._generate_metasploit_command(target, found_services),
            'burpsuite': f'echo "Manual Burp Suite testing required for {target}"',
            'wireshark': f'tshark -i any -c 100 host {target}',
            'wpscan': f'wpscan --url http://{target}/ --enumerate u,p,t',
            'searchsploit': self._generate_searchsploit_command(found_services),
            'enum4linux': f'enum4linux -a {target}',
            'smbclient': f'smbclient -L {target} -N',
            'whatweb': f'whatweb {target}',
            'dnsrecon': f'dnsrecon -d {target}',
            'fierce': f'fierce -dns {target}',
            'theharvester': f'theharvester -d {target} -b google,bing',
            'aircrack-ng': 'aircrack-ng -w /usr/share/wordlists/rockyou.txt capture.cap'
        }
        
        command = basic_commands.get(tool_name.lower())
        if command:
            return command
        
        # Generic fallback
        return f'{tool_name} {target}'
    
    def _generate_nmap_command(self, target: str, found_ports: List[str] = None) -> str:
        """Generate smart nmap command based on context"""
        if found_ports:
            # Detailed scan on found ports
            ports = ','.join(found_ports)
            return f'nmap -sC -sV -p {ports} {target}'
        else:
            # Initial discovery scan
            return f'nmap -sS -sV -O -A --top-ports 1000 {target}'
    
    def _generate_sqlmap_command(self, target: str, found_dirs: List[str] = None) -> str:
        """Generate smart sqlmap command"""
        if found_dirs:
            # Test specific directories/forms
            for dir_path in found_dirs:
                if any(param in dir_path for param in ['?', '=', 'login', 'search']):
                    return f'sqlmap -u "http://{target}{dir_path}" --batch --crawl=2'
        
        # Default crawl approach
        return f'sqlmap -u "http://{target}/" --batch --crawl=2 --forms'
    
    def _generate_hydra_command(self, target: str, found_services: List[str] = None) -> str:
        """Generate smart hydra command based on discovered services"""
        if 'ssh' in found_services:
            return f'hydra -l root -P /usr/share/wordlists/rockyou.txt {target} ssh'
        elif 'ftp' in found_services:
            return f'hydra -l anonymous -P /usr/share/wordlists/rockyou.txt {target} ftp'
        elif 'http' in found_services or 'https' in found_services:
            return f'hydra -l admin -P /usr/share/wordlists/rockyou.txt {target} http-post-form "/login:username=^USER^&password=^PASS^:Invalid"'
        else:
            return f'hydra -l admin -P /usr/share/wordlists/rockyou.txt {target} ssh'
    
    def _generate_metasploit_command(self, target: str, found_services: List[str] = None) -> str:
        """Generate smart metasploit command"""
        if 'ssh' in found_services:
            return f'msfconsole -q -x "use auxiliary/scanner/ssh/ssh_login; set RHOSTS {target}; set USERNAME root; set PASS_FILE /usr/share/wordlists/rockyou.txt; run; exit"'
        elif 'ftp' in found_services:
            return f'msfconsole -q -x "use auxiliary/scanner/ftp/ftp_login; set RHOSTS {target}; run; exit"'
        else:
            return f'msfconsole -q -x "use auxiliary/scanner/portscan/tcp; set RHOSTS {target}; run; exit"'
    
    def _generate_searchsploit_command(self, found_services: List[str] = None) -> str:
        """Generate searchsploit command based on services"""
        if found_services:
            service_query = ' '.join(found_services[:3])  # Top 3 services
            return f'searchsploit {service_query}'
        else:
            return 'searchsploit apache'
    
    def _validate_command(self, command: str) -> bool:
        """Validate command safety and structure"""
        if not command or len(command.strip()) < 3:
            return False
        
        # Use existing safety validation
        return self.tool_manager.validate_tool_safety(command)
    
    def _ai_generate_adaptive_command(self, tool: Dict, target: str, executed_commands: List[Dict]) -> str:
        """AI generates adaptive command based on previous results"""
        try:
            # Get last few outputs for context
            recent_outputs = [cmd['result']['output'] for cmd in executed_commands[-2:]]
            context = '\n'.join(recent_outputs)
            
            return self.deepseek.get_next_command(
                tool['name'],
                context,
                target,
                [tool['name']]
            )
        except:
            return self._ai_generate_command(tool, target, [])
    
    def _execute_ai_command(self, tool_name: str, command: str, target: str) -> Dict[str, Any]:
        """Execute AI-generated command with proper logging and error handling"""
        from rich.console import Console
        from rich.prompt import Confirm
        console = Console()
        
        # Show command to user and ask for confirmation
        console.print(f"\n[bold yellow]🤖 AI wants to execute:[/bold yellow]")
        console.print(f"[cyan]Tool:[/cyan] {tool_name}")
        console.print(f"[cyan]Command:[/cyan] {command}")
        console.print(f"[cyan]Target:[/cyan] {target}")
        
        if not Confirm.ask("\n[bold red]⚠️  Execute this command?[/bold red]", default=True):
            console.print("[yellow]⏭️  Command skipped by user[/yellow]")
            return {
                "tool": tool_name,
                "command": command,
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "output": "Command execution skipped by user",
                "error": "User declined to execute command",
                "duration": 0,
                "ai_enhanced": True,
                "ai_analysis": "Command was not executed due to user cancellation",
                "user_skipped": True
            }
        
        result = {
            "tool": tool_name,
            "command": command,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "output": "",
            "error": "",
            "duration": 0,
            "ai_enhanced": True,  # Mark as AI enhanced for reporting
            "ai_analysis": ""     # Will be filled by AI
        }
        
        start_time = time.time()
        
        try:
            console.print(f"[dim]Executing: {command}[/dim]")
            
            # Execute the actual command using the existing method
            execution_result = self._execute_single_command(command)
            
            # Update result with actual execution data
            result.update(execution_result)
            
            if result["success"]:
                console.print(f"[green]✅ Command executed successfully[/green]")
                
                # Get real-time AI analysis of the output
                if self.deepseek.client and result["output"]:
                    console.print(f"[cyan]🤖 AI analyzing output...[/cyan]")
                    ai_analysis = self.deepseek.analyze_tool_output(tool_name, result["output"], target)
                    if ai_analysis:
                        result["ai_analysis"] = ai_analysis
                        console.print(f"[green]AI Analysis: {ai_analysis[:150]}...[/green]")
                    else:
                        result["ai_analysis"] = "AI analysis failed"
                else:
                    result["ai_analysis"] = "AI analysis not available (offline mode or no output)"
            else:
                console.print(f"[red]❌ Command failed: {result.get('error', 'Unknown error')}[/red]")
                result["ai_analysis"] = f"Command execution failed: {result.get('error', 'Unknown error')}"
            
        except Exception as e:
            result["error"] = str(e)
            result["output"] = f"Error executing {tool_name}: {str(e)}"
            console.print(f"[red]Error executing {tool_name}: {str(e)}[/red]")
            result["ai_analysis"] = f"Execution error: {str(e)}"
        
        result["duration"] = time.time() - start_time
        
        return result
    
    def _ai_final_analysis(self, executed_commands: List[Dict], target: str) -> str:
        """AI performs final analysis of all results"""
        try:
            # Prepare summary of all executed commands and results
            summary_data = {
                'target': target,
                'tools_used': [cmd['tool'] for cmd in executed_commands],
                'results': [{'tool': cmd['tool'], 'output': cmd['result']['output'][:500]} for cmd in executed_commands]
            }
            
            return self.deepseek.generate_executive_summary(summary_data)
        except Exception as e:
            return f"Final analysis complete. Executed {len(executed_commands)} tools against {target}. Review individual tool outputs for detailed findings."
    
    def _get_last_tool_output(self, results: Dict) -> str:
        """Get the output from the last executed tool"""
        if not results:
            return ""
        
        # Get the most recent result
        last_tool = list(results.keys())[-1]
        return results[last_tool].get("output", "")
    
    def _generate_adaptive_command(self, tool_info: Dict, session_data: Dict, target: str) -> Optional[str]:
        """Generate adaptive command based on previous tool outputs"""
        tool_name = tool_info.get('name', '')
        
        # Get insights from previous tools
        previous_findings = self._extract_key_findings(session_data["results"])
        
        # Use AI to generate context-aware command
        if previous_findings:
            enhanced_criteria = f"Target: {target}. Previous findings: {previous_findings}"
            command_template = self.deepseek.get_next_command(
                list(session_data["results"].keys())[-1] if session_data["results"] else "",
                previous_findings,
                target,
                [tool_name]
            )
            
            if command_template:
                session_data["intelligence_log"].append({
                    "action": "adaptive_command_generation",
                    "tool": tool_name,
                    "context": previous_findings,
                    "command": command_template
                })
                return command_template
        
        # Fallback to standard command generation
        return self._generate_command(tool_info, f"Target: {target}")
    
    def _execute_tool_with_intelligence(self, tool_name: str, command: str, session_data: Dict) -> Dict[str, Any]:
        """Execute tool with enhanced intelligence and monitoring"""
        result = self._execute_tool_with_retry(tool_name, command)
        
        # Add intelligence metadata
        result["intelligence"] = {
            "execution_order": len(session_data["results"]) + 1,
            "context_aware": len(session_data["results"]) > 0,
            "adaptive_command": "adaptive_command_generation" in str(session_data.get("intelligence_log", []))
        }
        
        return result
    
    def _process_tool_output(self, tool_name: str, result: Dict, session_data: Dict, remaining_tools: List[Dict]):
        """Process tool output with AI analysis and planning"""
        output = result.get("output", "")
        
        # AI analysis
        analysis = self.deepseek.analyze_tool_output(tool_name, output)
        if analysis:
            result["analysis"] = analysis
            
            # Log intelligence insights
            session_data["intelligence_log"].append({
                "action": "output_analysis",
                "tool": tool_name,
                "findings_count": len(analysis.get("findings", [])),
                "high_severity_count": sum(1 for f in analysis.get("findings", []) if f.get("severity") == "high")
            })
        
        # Plan next steps if there are remaining tools
        if remaining_tools:
            remaining_tool_names = [t.get('name', '') for t in remaining_tools]
            target = self._extract_target_from_criteria(session_data["criteria"])
            
            next_suggestion = self.deepseek.get_next_command(
                tool_name, output, target, remaining_tool_names
            )
            
            if next_suggestion:
                result["ai_next_suggestion"] = next_suggestion
                session_data["intelligence_log"].append({
                    "action": "next_step_planning",
                    "current_tool": tool_name,
                    "suggestion": next_suggestion
                })
    
    def _extract_key_findings(self, results: Dict) -> str:
        """Extract key findings from previous tool results"""
        findings = []
        
        for tool_name, result in results.items():
            if result.get("success"):
                output = result.get("output", "")
                analysis = result.get("analysis", {})
                
                # Extract important information
                if "open" in output.lower() and "port" in output.lower():
                    findings.append(f"{tool_name} found open ports")
                
                if analysis and "findings" in analysis:
                    for finding in analysis["findings"][:3]:  # Top 3 findings
                        findings.append(f"{finding.get('type', 'issue')}: {finding.get('details', '')[:100]}")
        
        return "; ".join(findings[:5])  # Limit to top 5 findings
    
    def _generate_session_summary(self, session_data: Dict) -> Dict[str, Any]:
        """Generate comprehensive session summary with intelligence metrics"""
        results = session_data.get("results", {})
        intelligence_log = session_data.get("intelligence_log", [])
        
        # Calculate metrics
        total_tools = len(results)
        successful_tools = sum(1 for r in results.values() if r.get("success", False))
        adaptive_commands = sum(1 for entry in intelligence_log if entry.get("action") == "adaptive_command_generation")
        total_findings = sum(len(r.get("analysis", {}).get("findings", [])) for r in results.values())
        
        return {
            "execution_metrics": {
                "total_tools": total_tools,
                "successful_tools": successful_tools,
                "success_rate": (successful_tools / total_tools * 100) if total_tools > 0 else 0,
                "adaptive_commands": adaptive_commands,
                "intelligence_actions": len(intelligence_log)
            },
            "findings_summary": {
                "total_findings": total_findings,
                "tools_with_findings": sum(1 for r in results.values() if r.get("analysis", {}).get("findings")),
                "high_severity_findings": sum(
                    sum(1 for f in r.get("analysis", {}).get("findings", []) if f.get("severity") == "high")
                    for r in results.values()
                )
            },
            "intelligence_summary": {
                "context_aware_execution": adaptive_commands > 0,
                "ai_guided_progression": len([e for e in intelligence_log if e.get("action") == "next_step_planning"]) > 0,
                "total_ai_interactions": len(intelligence_log)
            }
        }
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"autopentest_{timestamp}"
    
    def _generate_command(self, tool_info: Dict[str, str], criteria: str) -> Optional[str]:
        """Generate a command for the tool based on criteria"""
        tool_name = tool_info.get('name', '')
        command_template = tool_info.get('command_template', '')
        
        # Extract target from criteria
        target = self._extract_target_from_criteria(criteria)
        
        if command_template:
            # Replace placeholders in template
            command = command_template.replace('TARGET', target)
            command = command.replace('{target}', target)
        else:
            # Use default template from tool manager
            command = self.tool_manager.get_tool_command_template(tool_name, target)
        
        # Validate command safety
        if not self.tool_manager.validate_tool_safety(command):
            self.logger.warning(f"Unsafe command blocked: {command}")
            return None
        
        return command
    
    def _extract_target_from_criteria(self, criteria: str) -> str:
        """Extract target IP/domain from criteria"""
        # Simple extraction - look for common patterns
        import re
        
        # IP address pattern
        ip_pattern = r'\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b'
        ip_match = re.search(ip_pattern, criteria)
        if ip_match:
            return ip_match.group()
        
        # Domain pattern
        domain_pattern = r'\\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])?\\.)+'
        domain_match = re.search(domain_pattern, criteria)
        if domain_match:
            return domain_match.group().rstrip('.')
        
        # URL pattern
        url_pattern = r'https?://([^\\s/]+)'
        url_match = re.search(url_pattern, criteria)
        if url_match:
            return url_match.group(1)
        
        # Default fallback
        return "127.0.0.1"
    
    def _execute_tool_with_retry(self, tool_name: str, command: str, max_retries: int = 2) -> Dict[str, Any]:
        """Execute a tool with retry logic on failure"""
        result = {
            "tool": tool_name,
            "command": command,
            "success": False,
            "output": "",
            "error": "",
            "execution_time": 0,
            "attempts": []
        }
        
        for attempt in range(max_retries + 1):
            attempt_result = self._execute_single_command(command)
            result["attempts"].append(attempt_result)
            
            if attempt_result["success"]:
                result.update(attempt_result)
                result["success"] = True
                break
            else:
                self.logger.warning(f"Attempt {attempt + 1} failed for {tool_name}")
                
                if attempt < max_retries:
                    # Try to get a fixed command from AI
                    fixed_command = self.deepseek.fix_command_error(
                        tool_name, command, attempt_result["error"]
                    )
                    
                    if fixed_command:
                        self.logger.info(f"AI suggested fix: {fixed_command}")
                        command = fixed_command
                    else:
                        self.logger.error(f"No AI fix available for {tool_name}")
                        break
        
        if not result["success"]:
            # Use the last attempt's error info
            last_attempt = result["attempts"][-1]
            result["error"] = last_attempt["error"]
            result["execution_time"] = last_attempt["execution_time"]
        
        return result
    
    def _execute_single_command(self, command: str, timeout: int = 300) -> Dict[str, Any]:
        """Execute a single command and return results"""
        start_time = time.time()
        
        try:
            # Split command into parts
            cmd_parts = command.split()
            
            # Execute command
            process = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            execution_time = time.time() - start_time
            
            return {
                "success": process.returncode == 0,
                "output": process.stdout,
                "error": process.stderr,
                "return_code": process.returncode,
                "execution_time": execution_time
            }
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "output": "",
                "error": f"Command timed out after {timeout} seconds",
                "return_code": -1,
                "execution_time": execution_time
            }
            
        except FileNotFoundError:
            execution_time = time.time() - start_time
            tool_name = command.split()[0]
            return {
                "success": False,
                "output": "",
                "error": f"Tool '{tool_name}' not found. Please ensure it's installed and in PATH.",
                "return_code": -1,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "output": "",
                "error": f"Execution error: {str(e)}",
                "return_code": -1,
                "execution_time": execution_time
            }
    
    def _save_session(self, session_id: str, session_data: Dict[str, Any]):
        """Save session data to file"""
        try:
            session_file = self.logs_dir / f"{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            self.logger.info(f"Session data saved: {session_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save session data: {e}")
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from file"""
        try:
            session_file = self.logs_dir / f"{session_id}.json"
            if session_file.exists():
                with open(session_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load session {session_id}: {e}")
        
        return None
    
    def list_sessions(self) -> List[Dict[str, str]]:
        """List all available sessions"""
        sessions = []
        
        try:
            for session_file in self.logs_dir.glob("autopentest_*.json"):
                try:
                    with open(session_file, 'r') as f:
                        data = json.load(f)
                    
                    sessions.append({
                        "session_id": data.get("session_id", session_file.stem),
                        "timestamp": data.get("timestamp", "Unknown"),
                        "criteria": data.get("criteria", "No criteria"),
                        "tools_count": len(data.get("tools", [])),
                        "file_path": str(session_file)
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error reading session file {session_file}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error listing sessions: {e}")
        
        return sorted(sessions, key=lambda x: x["timestamp"], reverse=True)
    
    def get_session_summary(self, session_id: str) -> Optional[str]:
        """Get a summary of a session"""
        session_data = self.load_session(session_id)
        if not session_data:
            return None
        
        summary = f"Session: {session_id}\\n"
        summary += f"Time: {session_data.get('timestamp', 'Unknown')}\\n"
        summary += f"Criteria: {session_data.get('criteria', 'Unknown')}\\n\\n"
        
        results = session_data.get("results", {})
        summary += f"Tools executed: {len(results)}\\n"
        
        successful = sum(1 for r in results.values() if r.get("success", False))
        summary += f"Successful: {successful}\\n"
        summary += f"Failed: {len(results) - successful}\\n\\n"
        
        # Add findings summary if available
        total_findings = 0
        for tool_result in results.values():
            analysis = tool_result.get("analysis", {})
            if analysis and "statistics" in analysis:
                total_findings += analysis["statistics"].get("total_findings", 0)
        
        if total_findings > 0:
            summary += f"Total findings: {total_findings}\\n"
        
        return summary
    
    def run_intelligent_tools(self, tools: List[Dict[str, str]], criteria: str) -> Dict[str, Any]:
        """Run tools with intelligent chaining based on outputs"""
        session_id = self._generate_session_id()
        session_data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "criteria": criteria,
            "tools": tools,
            "results": {},
            "summary": {},
            "intelligent_chaining": True
        }
        
        self.logger.info(f"Starting intelligent automation session: {session_id}")
        
        target = self._extract_target_from_criteria(criteria)
        executed_tools = []
        remaining_tools = [tool['name'] for tool in tools]
        
        for i, tool_info in enumerate(tools):
            tool_name = tool_info.get('name', '')
            if not tool_name:
                continue
            
            self.logger.info(f"Running tool {i+1}/{len(tools)}: {tool_name}")
            
            # For first tool, use original command template
            if i == 0:
                command = self._generate_command(tool_info, criteria)
            else:
                # For subsequent tools, use AI to determine next best command based on previous outputs
                previous_outputs = []
                for executed_tool in executed_tools:
                    if executed_tool in session_data["results"]:
                        output = session_data["results"][executed_tool].get("output", "")
                        if output:
                            previous_outputs.append(f"{executed_tool}: {output[:500]}")  # Limit output length
                
                if previous_outputs:
                    combined_output = "\n".join(previous_outputs)
                    remaining = [t for t in remaining_tools if t != tool_name]
                    
                    intelligent_command = self.deepseek.get_next_command(
                        executed_tools[-1] if executed_tools else "initial",
                        combined_output,
                        target,
                        remaining
                    )
                    
                    if intelligent_command:
                        command = intelligent_command
                        self.logger.info(f"AI suggested intelligent command: {command}")
                    else:
                        command = self._generate_command(tool_info, criteria)
                else:
                    command = self._generate_command(tool_info, criteria)
            
            if not command:
                self.logger.error(f"Could not generate command for {tool_name}")
                continue
            
            # Execute the tool
            result = self._execute_tool_with_retry(tool_name, command)
            session_data["results"][tool_name] = result
            executed_tools.append(tool_name)
            
            if tool_name in remaining_tools:
                remaining_tools.remove(tool_name)
            
            # Analyze the output with AI
            if result.get("success") and result.get("output"):
                analysis = self.deepseek.analyze_tool_output(tool_name, result["output"])
                if analysis:
                    session_data["results"][tool_name]["analysis"] = analysis
                    self.logger.info(f"AI analysis completed for {tool_name}")
        
        # Save session data
        self._save_session(session_id, session_data)
        
        return session_data

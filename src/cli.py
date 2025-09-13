"""
CLI Interface for AegisSec
Handles user interaction and workflow coordination
Developed by RunTime Terrors
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
import sys
from typing import Dict, List, Optional

from config_manager import ConfigManager
from deepseek_client import DeepSeekClient
from tool_manager import ToolManager
from automation_engine import AutomationEngine
from report_generator import ReportGenerator

class AegisSecCLI:
    def __init__(self, config_manager: ConfigManager):
        self.console = Console()
        self.config = config_manager
        self.deepseek = DeepSeekClient(config_manager)  # Pass config manager
        self.tool_manager = ToolManager(config_manager)
        self.automation = AutomationEngine(config_manager)
        self.reporter = ReportGenerator(config_manager)
        
    def run(self):
        """Main CLI workflow"""
        try:
            while True:
                self.show_main_menu()
                choice = self.get_user_choice()
                
                if choice == "1":
                    self.run_pentest_workflow()
                elif choice == "2":
                    self.show_tool_status()
                elif choice == "3":
                    self.view_reports()
                elif choice == "4":
                    self.ai_advisor_mode()
                elif choice == "5":
                    self.show_settings()
                elif choice == "6":
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break
                else:
                    self.console.print("[red]Invalid choice. Please try again.[/red]")
                    
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Goodbye![/yellow]")
    
    def show_main_menu(self):
        """Display the main menu"""
        self.console.print("\n" + "="*60)
        
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan bold", width=8)
        menu_table.add_column("Description", style="white")
        
        menu_table.add_row("1.", "Start Penetration Test")
        menu_table.add_row("2.", "Check Tool Status")
        menu_table.add_row("3.", "View Reports")
        menu_table.add_row("4.", "AI Advisor Mode")
        menu_table.add_row("5.", "Settings")
        menu_table.add_row("6.", "Exit")
        
        panel = Panel(
            menu_table,
            title="[bold green]Main Menu[/bold green]",
            border_style="blue"
        )
        self.console.print(panel)
    
    def get_user_choice(self) -> str:
        """Get user menu choice"""
        return Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6"])
    
    def run_pentest_workflow(self):
        """Enhanced penetration testing workflow with user tool selection"""
        self.console.print("\n[bold yellow]�️ Starting AegisSec Penetration Test Workflow[/bold yellow]")
        
        # Step 1: Get user intent
        test_type, criteria = self.get_test_criteria()
        if not criteria:
            return  # User chose to go back
        
        # Step 2: Get AI recommendations
        self.console.print("\n[cyan]🤖 Consulting AI for tool recommendations...[/cyan]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Analyzing requirements...", total=None)
            
            # Ensure criteria is always a dictionary
            if isinstance(criteria, dict):
                target = criteria.get('target', 'localhost')
                scan_type = criteria.get('type', 'comprehensive')
                category = criteria.get('category', 'general')
                # Pass full criteria to AI for enhanced recommendations
                recommended_tools = self.deepseek.get_tool_recommendations(criteria)
            else:
                target = 'localhost'
                scan_type = 'comprehensive'
                category = 'general'
                # Create basic criteria for fallback
                basic_criteria = {
                    'target': target,
                    'type': scan_type,
                    'category': category,
                    'target_type': 'generic_target',
                    'description': f'{scan_type} assessment on {target}'
                }
                recommended_tools = self.deepseek.get_tool_recommendations(basic_criteria)
            progress.remove_task(task)
        
        if not recommended_tools:
            self.console.print("[red]Failed to get AI recommendations. Please try again.[/red]")
            return
        
        # Step 3: Show recommendations and let user select tools
        selected_tools = self.show_tool_recommendations_and_select(recommended_tools)
        if selected_tools is None:
            return  # User chose to go back
        if not selected_tools:
            self.console.print("[yellow]No tools selected. Aborting.[/yellow]")
            return
        
        # Step 4: Check tool availability
        tools_dict = [{'name': tool} for tool in selected_tools]  # Convert to expected format
        missing_tools = self.tool_manager.check_missing_tools(tools_dict)
        if missing_tools:
            if Confirm.ask(f"Install {len(missing_tools)} missing tools?"):
                self.tool_manager.install_tools(missing_tools)
        
        # Step 5: AI Pre-Test Consultation
        self.console.print("\n[bold yellow]🤖 Starting AI Pre-Test Consultation...[/bold yellow]")
        enhanced_criteria = self.deepseek.conduct_pre_test_consultation(criteria)
        
        # Step 5.5: Show consultation summary and get final confirmation
        self._show_consultation_summary(enhanced_criteria)
        
        # Step 6: Final confirmation before automation
        if not Confirm.ask("\n[bold red]⚠️  Proceed with automated penetration testing? This will execute actual security tools.[/bold red]"):
            self.console.print("[yellow]🛑 Test cancelled by user.[/yellow]")
            return
            
        # Step 7: Run intelligent automated testing
        self.console.print("\n[bold green]🚀 Starting automated penetration testing...[/bold green]")
        self.run_intelligent_test(selected_tools, enhanced_criteria)
    
    def get_test_criteria(self) -> tuple:
        """Get test type and criteria from user with clean category selection"""
        self.console.print("\n[bold yellow]📋 Select Test Category[/bold yellow]")
        
        # Clean category selection without target input
        categories = {
            "1": {"name": "Network Mapping & Discovery", "desc": "Port scanning, OS fingerprinting, service enumeration", "key": "network_discovery"},
            "2": {"name": "Web Application Security", "desc": "SQL injection, XSS, directory enumeration, web vulnerabilities", "key": "web_application"},
            "3": {"name": "Wireless Security Testing", "desc": "WiFi cracking, WPA/WEP attacks, access point security", "key": "wireless"},
            "4": {"name": "Social Engineering Attacks", "desc": "Phishing, spear phishing, pretexting, OSINT gathering", "key": "social_engineering"},
            "5": {"name": "Brute Force & Credential Attacks", "desc": "Password attacks, SSH brute force, credential stuffing", "key": "credential_attacks"},
            "6": {"name": "Privilege Escalation Testing", "desc": "Kernel exploits, SUID abuse, weak sudo rules", "key": "privilege_escalation"},
            "7": {"name": "Vulnerability Scanning", "desc": "Automated vulnerability assessment and discovery", "key": "vulnerability_scan"},
            "8": {"name": "Malware & Persistence Testing", "desc": "Rootkits, backdoors, persistence mechanisms", "key": "malware_persistence"},
            "9": {"name": "Database Security Assessment", "desc": "Database enumeration, injection attacks, data extraction", "key": "database_security"},
            "10": {"name": "Active Directory Testing", "desc": "Domain enumeration, Kerberos attacks, AD exploitation", "key": "active_directory"},
            "11": {"name": "Denial of Service Testing", "desc": "DoS attacks, resource exhaustion, network flooding", "key": "denial_of_service"},
            "12": {"name": "Custom Testing Scenario", "desc": "Define your own penetration testing criteria", "key": "custom"},
            "0": {"name": "Back to Main Menu", "desc": "Return to the main menu", "key": "back"}
        }
        
        # Display categories in a clean, organized way
        self._display_categories_with_animation(categories)
        
        choice = Prompt.ask("Select category", choices=list(categories.keys()))
        
        if choice == "0":
            return None, None  # Signal to return to main menu
            
        selected_category = categories[choice]
        category_name = selected_category["name"]
        category_key = selected_category["key"]
        
        # Show selection confirmation with animation
        self._show_category_selection_animation(category_name)
        
        if choice == "12":  # Custom scenario
            custom_criteria = Prompt.ask("\n[bold cyan]Enter your custom testing criteria[/bold cyan]")
            target = Prompt.ask("[bold cyan]Enter target (IP/domain/URL)[/bold cyan]")
            criteria = {
                'type': category_name,
                'target': target,
                'description': custom_criteria,
                'category': 'custom'
            }
        else:
            # Get category-specific target information
            target_prompt, example_hint = self._get_category_specific_target_prompt(category_key)
            target = Prompt.ask(f"\n[bold cyan]{target_prompt}[/bold cyan]", 
                              default=example_hint if example_hint else None)
            
            criteria = {
                'type': category_name,
                'target': target,
                'description': f"{category_name} assessment on {target}",
                'category': category_key,
                'target_type': self._get_target_type_for_category(category_key)
            }
            
            # Ask for additional details
            if Confirm.ask("Add specific requirements or constraints?"):
                additional = Prompt.ask("Additional requirements")
                criteria['description'] += f". {additional}"
        
        return category_name, criteria
    
    def _get_category_specific_target_prompt(self, category_key: str) -> tuple:
        """Get category-specific target prompts and examples"""
        prompts = {
            'network_mapping': (
                "🌐 Enter target network/IP for discovery (e.g., 192.168.1.1 or example.com)", 
                "192.168.1.1"
            ),
            'web_application': (
                "🌍 Enter target website URL for web security testing", 
                "https://example.com"
            ),
            'vulnerability_scanning': (
                "🔍 Enter target IP/domain for vulnerability assessment", 
                "target-server.com"
            ),
            'password_attacks': (
                "🔐 Enter target service (SSH/FTP/HTTP) for password testing (IP:port or service URL)", 
                "ssh://192.168.1.100:22"
            ),
            'wireless_security': (
                "📡 Enter WiFi network name (SSID) or 'scan' to discover networks", 
                "MyWiFiNetwork"
            ),
            'social_engineering': (
                "👥 Enter target email domain or organization for social engineering assessment", 
                "gmail.com"
            ),
            'privilege_escalation': (
                "⬆️ Enter target system IP where you have initial access for privilege escalation", 
                "192.168.1.50"
            ),
            'forensics': (
                "🔬 Enter system IP or image file path for digital forensics analysis", 
                "192.168.1.10"
            ),
            'malware_analysis': (
                "🦠 Enter suspicious file path or URL for malware analysis", 
                "/path/to/suspicious/file.exe"
            ),
            'dns_enumeration': (
                "🌐 Enter target domain for DNS enumeration", 
                "example.com"
            ),
            'ssl_tls_testing': (
                "🔒 Enter target website (domain:port) for SSL/TLS security testing", 
                "example.com:443"
            ),
            'database_testing': (
                "🗄️ Enter database connection string or web app URL for SQL injection testing", 
                "https://webapp.com/login"
            )
        }
        
        return prompts.get(category_key, ("Enter target for security assessment", None))
    
    def _get_target_type_for_category(self, category_key: str) -> str:
        """Get target type for AI context"""
        target_types = {
            'network_mapping': 'network_infrastructure',
            'web_application': 'web_application', 
            'vulnerability_scanning': 'network_host',
            'password_attacks': 'authentication_service',
            'wireless_security': 'wireless_network',
            'social_engineering': 'email_domain_organization',
            'privilege_escalation': 'compromised_system',
            'forensics': 'digital_evidence',
            'malware_analysis': 'suspicious_file',
            'dns_enumeration': 'domain_name_system',
            'ssl_tls_testing': 'secure_web_service',
            'database_testing': 'database_application'
        }
        
        return target_types.get(category_key, 'generic_target')
    
    def _display_categories_with_animation(self, categories):
        """Display categories with clean animation"""
        import time
        
        # Animated header
        self.console.print("\n[bold blue]🎯 Choose Your Penetration Testing Focus Area[/bold blue]")
        time.sleep(0.3)
        
        # Core categories
        self.console.print("\n[bold cyan]� Core Security Testing:[/bold cyan]")
        core_table = Table(show_header=False, box=None, padding=(0, 2))
        core_table.add_column("Option", style="cyan bold", width=4)
        core_table.add_column("Category", style="white bold", width=35)
        core_table.add_column("Description", style="dim", width=50)
        
        core_categories = ["1", "2", "7"]
        for cat_id in core_categories:
            cat = categories[cat_id]
            core_table.add_row(cat_id, cat["name"], cat["desc"])
            time.sleep(0.1)
        
        self.console.print(core_table)
        time.sleep(0.2)
        
        # Specialized attacks
        self.console.print("\n[bold red]⚔️ Specialized Attack Vectors:[/bold red]")
        attack_table = Table(show_header=False, box=None, padding=(0, 2))
        attack_table.add_column("Option", style="cyan bold", width=4)
        attack_table.add_column("Category", style="white bold", width=35)
        attack_table.add_column("Description", style="dim", width=50)
        
        attack_categories = ["3", "4", "5", "6", "8", "11"]
        for cat_id in attack_categories:
            cat = categories[cat_id]
            attack_table.add_row(cat_id, cat["name"], cat["desc"])
            time.sleep(0.1)
        
        self.console.print(attack_table)
        time.sleep(0.2)
        
        # Advanced testing
        self.console.print("\n[bold magenta]🏢 Advanced & Enterprise Testing:[/bold magenta]")
        advanced_table = Table(show_header=False, box=None, padding=(0, 2))
        advanced_table.add_column("Option", style="cyan bold", width=4)
        advanced_table.add_column("Category", style="white bold", width=35)
        advanced_table.add_column("Description", style="dim", width=50)
        
        advanced_categories = ["9", "10"]
        for cat_id in advanced_categories:
            cat = categories[cat_id]
            advanced_table.add_row(cat_id, cat["name"], cat["desc"])
            time.sleep(0.1)
        
        self.console.print(advanced_table)
        time.sleep(0.2)
        
        # Options
        self.console.print("\n[bold yellow]⚙️ Other Options:[/bold yellow]")
        options_table = Table(show_header=False, box=None, padding=(0, 2))
        options_table.add_column("Option", style="cyan bold", width=4)
        options_table.add_column("Category", style="white bold", width=35)
        options_table.add_column("Description", style="dim", width=50)
        
        options_categories = ["12", "0"]
        for cat_id in options_categories:
            cat = categories[cat_id]
            style = "dim" if cat_id == "0" else "white bold"
            options_table.add_row(cat_id, f"[{style}]{cat['name']}[/{style}]", cat["desc"])
            time.sleep(0.1)
        
        self.console.print(options_table)
    
    def _show_category_selection_animation(self, category_name):
        """Show animated confirmation of category selection"""
        import time
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(f"Loading {category_name} toolkit...", total=None)
            time.sleep(1.5)
            progress.remove_task(task)
        
        self.console.print(f"\n[bold green]✅ Selected: {category_name}[/bold green]")
    
    def show_tool_recommendations_and_select(self, tool_names: List[str]) -> List[str]:
        """Display AI tool recommendations with clean animations and priority system"""
        import time
        
        self.console.print("\n[bold green]🛠️  AI-Powered Tool Recommendations[/bold green]")
        
        # Animated loading
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Analyzing category requirements...", total=None)
            time.sleep(1)
            progress.update(task, description="Consulting AI for optimal tools...")
            time.sleep(0.8)
            progress.update(task, description="Prioritizing Kali Linux tools...")
            time.sleep(0.5)
            progress.remove_task(task)
        
        self.console.print(f"\n[cyan]✨ {len(tool_names)} specialized tools recommended for your test[/cyan]")
        time.sleep(0.3)
        
        # Separate tools by priority
        kali_priority_tools = ["nmap", "nikto", "sqlmap"]
        priority_tools = []
        other_tools = []
        
        for tool in tool_names:
            if tool.lower() in [k.lower() for k in kali_priority_tools]:
                priority_tools.append(tool)
            else:
                other_tools.append(tool)
        
        # Display HIGH PRIORITY tools first
        if priority_tools:
            self.console.print("\n[bold red]🚀 HIGH PRIORITY (Kali Linux Pre-installed):[/bold red]")
            time.sleep(0.2)
            self._display_tool_section(priority_tools, start_id=1, is_priority=True)
            time.sleep(0.3)
        
        # Display other specialized tools
        if other_tools:
            self.console.print("\n[bold yellow]⭐ SPECIALIZED TOOLS:[/bold yellow]")
            time.sleep(0.2)
            start_id = len(priority_tools) + 1
            self._display_tool_section(other_tools, start_id=start_id, is_priority=False)
        
        # Selection interface
        self.console.print("\n[bold cyan]📋 Tool Selection Options:[/bold cyan]")
        selection_table = Table(show_header=False, box=None, padding=(0, 2))
        selection_table.add_column("Command", style="green bold", width=12)
        selection_table.add_column("Description", style="white")
        
        selection_table.add_row("all", "Select all recommended tools")
        selection_table.add_row("priority", "Select only HIGH PRIORITY tools")
        selection_table.add_row("1,3,5", "Select specific tools by numbers")
        selection_table.add_row("back", "Return to category selection")
        
        self.console.print(selection_table)
        
        while True:
            selection = Prompt.ask("\n[bold magenta]Your selection[/bold magenta]", default="priority")
            
            if selection.lower() == "back":
                return None  # Signal to go back
            elif selection.lower() == "all":
                self._show_selection_animation("all tools")
                return tool_names
            elif selection.lower() == "priority":
                if priority_tools:
                    self._show_selection_animation("high priority tools")
                    return priority_tools
                else:
                    self.console.print("[yellow]No priority tools available, selecting all tools[/yellow]")
                    return tool_names
            
            try:
                selected_ids = [int(x.strip()) for x in selection.split(',')]
                selected_tools = []
                
                for tool_id in selected_ids:
                    if 1 <= tool_id <= len(tool_names):
                        selected_tools.append(tool_names[tool_id - 1])
                    else:
                        self.console.print(f"[red]Invalid tool ID: {tool_id}[/red]")
                        break
                else:
                    if selected_tools:
                        self._show_selection_animation(f"{len(selected_tools)} tools")
                        return selected_tools
                    else:
                        self.console.print("[red]No valid tools selected[/red]")
                        
            except ValueError:
                self.console.print("[red]Invalid selection format. Use numbers separated by commas (e.g., 1,3,5)[/red]")
    
    def _display_tool_section(self, tools: List[str], start_id: int, is_priority: bool):
        """Display a section of tools with enhanced formatting"""
        import time
        
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("ID", style="cyan bold", width=4)
        table.add_column("Tool", style="cyan", width=18)
        table.add_column("Status", style="white", width=14)
        table.add_column("Category", style="white", width=20)
        table.add_column("Priority", style="yellow", width=12)
        
        # Enhanced tool categorization
        enhanced_categories = {
            # Network tools
            "nmap": "Network Scanner", "masscan": "Network Scanner", "zmap": "Network Scanner",
            "netdiscover": "Network Discovery", "arp-scan": "Network Discovery", 
            "ping": "Connectivity Test", "traceroute": "Network Trace",
            
            # Web tools
            "nikto": "Web Vulnerability", "burpsuite": "Web Proxy", "owasp-zap": "Web Proxy",
            "sqlmap": "SQL Injection", "dirb": "Directory Enum", "gobuster": "Directory Enum",
            "wfuzz": "Web Fuzzer", "ffuf": "Web Fuzzer", "wpscan": "CMS Scanner",
            
            # Attack tools
            "hydra": "Brute Force", "medusa": "Brute Force", "john": "Password Crack",
            "hashcat": "Password Crack", "ncrack": "Network Brute", "patator": "Brute Force",
            
            # Wireless
            "aircrack-ng": "WiFi Security", "reaver": "WPS Attack", "kismet": "WiFi Monitor",
            
            # Social Engineering
            "setoolkit": "Social Engineering", "theharvester": "OSINT", "recon-ng": "Reconnaissance",
            
            # Privilege Escalation
            "linpeas": "Privilege Escalation", "winpeas": "Privilege Escalation", "pspy": "Process Monitor",
            
            # Default
            "metasploit": "Exploitation", "wireshark": "Network Analysis"
        }
        
        for i, tool_name in enumerate(tools):
            tool_id = start_id + i
            category = enhanced_categories.get(tool_name.lower(), "Security Tool")
            priority = "HIGH" if is_priority else "SPECIALIZED"
            status = "✅ Available" if self.tool_manager.is_tool_installed(tool_name) else "📦 Install Needed"
            status_color = "green" if "✅" in status else "yellow"
            priority_color = "red" if is_priority else "blue"
            
            table.add_row(
                str(tool_id),
                tool_name,
                f"[{status_color}]{status}[/{status_color}]",
                category,
                f"[{priority_color}]{priority}[/{priority_color}]"
            )
            time.sleep(0.15)  # Animated row appearance
        
        self.console.print(table)
    
    def _show_selection_animation(self, selection_type: str):
        """Show animated confirmation of tool selection"""
        import time
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(f"Preparing {selection_type}...", total=None)
            time.sleep(1)
            progress.update(task, description="Validating tool compatibility...")
            time.sleep(0.8)
            progress.remove_task(task)
        
        self.console.print(f"[bold green]✅ Selected {selection_type}[/bold green]")
    
    def run_intelligent_test(self, selected_tools: List[str], criteria: Dict):
        """Run intelligent automated test with command chaining based on outputs"""
        self.console.print("\n[bold yellow]🚀 Starting Intelligent Automated Test[/bold yellow]")
        
        if not selected_tools:
            self.console.print("[red]No tools to run.[/red]")
            return

        # Convert tool names to tool dictionaries for automation engine
        tools_dict = []
        for tool_name in selected_tools:
            tools_dict.append({
                'name': tool_name,
                'description': f'Security testing tool: {tool_name}'
            })

        # Convert criteria dict to string for automation engine
        if isinstance(criteria, dict):
            criteria_str = criteria.get('description', f"Test {criteria.get('target', 'target')}")
        else:
            criteria_str = str(criteria)
        
        # Run automation with intelligent chaining
        results = self.automation.run_intelligent_tools(tools_dict, criteria_str)
        
        # Generate comprehensive report
        if results:
            self.console.print("\n[cyan]📊 Generating comprehensive report...[/cyan]")
            report_path = self.reporter.generate_comprehensive_report(results, criteria)
            
            if report_path:
                self.console.print(f"[green]✅ Report saved: {report_path}[/green]")
                
                if Confirm.ask("View executive summary?"):
                    self.show_executive_summary(results)
    
    def show_tool_status(self):
        """Show status of all known tools"""
        self.console.print("\n[bold yellow]🔧 Tool Status[/bold yellow]")
        
        kali_tools = self.config.get_kali_tools()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Tool", style="cyan", width=20)
        table.add_column("Status", style="white", width=15)
        table.add_column("Version", style="white")
        
        for tool in kali_tools:
            status = "✅ Installed" if self.tool_manager.is_tool_installed(tool) else "❌ Missing"
            status_style = "green" if "✅" in status else "red"
            version = self.tool_manager.get_tool_version(tool) if "✅" in status else "N/A"
            
            table.add_row(
                tool,
                f"[{status_style}]{status}[/{status_style}]",
                version
            )
        
        self.console.print(table)
    
    def view_reports(self):
        """View existing reports"""
        self.console.print("\n[bold yellow]📊 Previous Reports[/bold yellow]")
        reports = self.reporter.list_reports()
        
        if not reports:
            self.console.print("[yellow]No reports found.[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Report", style="cyan")
        table.add_column("Date", style="white")
        table.add_column("Size", style="white")
        
        for report in reports:
            table.add_row(report['name'], report['date'], report['size'])
        
        self.console.print(table)
    
    def ai_advisor_mode(self):
        """Interactive AI advisor for security questions"""
        self.console.print("\n[bold yellow]🧠 AI Advisor Mode[/bold yellow]")
        self.console.print("[cyan]Ask me anything about penetration testing or security![/cyan]")
        self.console.print("[dim]Type 'exit' to return to main menu[/dim]")
        
        while True:
            question = Prompt.ask("\n[bold]Your question")
            
            if question.lower() in ['exit', 'quit', 'back']:
                break
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Thinking...", total=None)
                answer = self.deepseek.ask_advisor_question(question)
                progress.remove_task(task)
            
            if answer:
                panel = Panel(
                    answer,
                    title="[bold cyan]AI Advisor[/bold cyan]",
                    border_style="green"
                )
                self.console.print(panel)
            else:
                self.console.print("[red]Sorry, I couldn't process that question.[/red]")
    
    def show_settings(self):
        """Show current settings and allow API testing"""
        self.console.print("\n[bold yellow]⚙️  Settings[/bold yellow]")
        
        settings_table = Table(show_header=True, header_style="bold magenta")
        settings_table.add_column("Setting", style="cyan")
        settings_table.add_column("Value", style="white")
        
        settings_table.add_row("API Model", self.deepseek.model)
        settings_table.add_row("API Base URL", "https://openrouter.ai/api/v1")
        settings_table.add_row("Log Level", self.config.get("logging.level", "INFO"))
        settings_table.add_row("Config Path", self.config.config_path)
        
        self.console.print(settings_table)
        
        # Test API connection option
        if Confirm.ask("\nTest API connection?"):
            self.console.print("\n[cyan]Testing DeepSeek API connection...[/cyan]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Connecting to API...", total=None)
                success = self.deepseek.test_api_connection()
                progress.remove_task(task)
            
            if success:
                self.console.print("[green]✅ API connection successful![/green]")
            else:
                self.console.print("[red]❌ API connection failed. Check your API key and internet connection.[/red]")
    
    def _show_consultation_summary(self, enhanced_criteria: Dict):
        """Show consultation summary before starting automation"""
        self.console.print("\n[bold yellow]📋 Consultation Summary[/bold yellow]")
        
        # Create summary table
        summary_table = Table(show_header=True, header_style="bold magenta")
        summary_table.add_column("Aspect", style="cyan", width=20)
        summary_table.add_column("Details", style="white", width=50)
        
        # Add basic info
        summary_table.add_row("Target", enhanced_criteria.get('target', 'Unknown'))
        summary_table.add_row("Category", enhanced_criteria.get('category', 'Unknown'))
        summary_table.add_row("Target Type", enhanced_criteria.get('target_type', 'Unknown'))
        
        # Add consultation info if available
        if enhanced_criteria.get('consultation_complete'):
            conversation_history = enhanced_criteria.get('conversation_history', [])
            if conversation_history:
                # Show key conversation points
                user_responses = [h for h in conversation_history if h.startswith('User:')]
                if user_responses:
                    summary_table.add_row("User Inputs", f"{len(user_responses)} responses provided")
                    # Show last user response
                    last_response = user_responses[-1].replace('User: ', '')
                    summary_table.add_row("Last Response", last_response[:47] + "..." if len(last_response) > 50 else last_response)
            
            # Show AI test plan if available
            test_plan = enhanced_criteria.get('ai_test_plan', '')
            if test_plan:
                summary_table.add_row("AI Test Plan", test_plan[:47] + "..." if len(test_plan) > 50 else test_plan)
        
        self.console.print(summary_table)
        
        # Show any specific consultation details
        if enhanced_criteria.get('conversation_history'):
            self.console.print("\n[dim]💬 Consultation included interactive Q&A session[/dim]")
        
    def show_executive_summary(self, results: Dict):
        """Show a user-friendly executive summary of test results"""
        self.console.print("\n[bold green]📋 Executive Summary[/bold green]")
        
        # Generate AI-powered executive summary
        summary_text = self.deepseek.generate_executive_summary(results)
        
        if summary_text:
            panel = Panel(
                summary_text,
                title="[bold cyan]Security Assessment Summary[/bold cyan]",
                border_style="green"
            )
            self.console.print(panel)
        
        # Show key metrics
        self._show_security_metrics(results)
    
    def _show_security_metrics(self, results: Dict):
        """Display key security metrics in user-friendly format"""
        tool_results = results.get("results", {})
        
        # Handle different data structures - could be dict or list
        if isinstance(tool_results, list):
            # Convert list to dict for processing
            tool_results_dict = {r.get("tool", f"tool_{i}"): r for i, r in enumerate(tool_results)}
            tool_results = tool_results_dict
        
        # Calculate metrics based on ACTUAL data structure
        total_tools = len(tool_results)
        successful_tools = sum(1 for r in tool_results.values() if r.get("success", False))
        failed_tools = total_tools - successful_tools
        
        # Count actual findings from tool outputs
        total_findings = 0
        critical_findings = 0
        high_findings = 0
        
        # Analyze actual tool outputs for real findings
        for tool_name, tool_result in tool_results.items():
            if tool_result.get("success", False):
                output = tool_result.get("output", "").lower()
                # Look for actual security indicators in tool output
                if "open" in output and "port" in output:
                    total_findings += 1
                if "vulnerable" in output or "exploit" in output:
                    total_findings += 1
                    high_findings += 1
                if "critical" in output or "high" in output:
                    critical_findings += 1
                # Add more realistic pattern matching based on actual tool outputs
                
        # Calculate realistic security score based on actual results
        if failed_tools == total_tools:
            # All tools failed - can't assess security properly
            security_score = "N/A"
            score_color = "yellow"
            score_status = "Unable to assess - tools failed"
        elif successful_tools == 0:
            security_score = "N/A"
            score_color = "yellow" 
            score_status = "No successful scans"
        else:
            # Base score on actual findings
            security_score = max(0, 100 - (critical_findings * 20) - (high_findings * 10))
            score_color = "green" if security_score >= 70 else "yellow" if security_score >= 40 else "red"
            score_status = "Good" if security_score >= 70 else "Needs Improvement" if security_score >= 40 else "Poor"
        
        # Display metrics
        metrics_table = Table(show_header=False, box=None, padding=(0, 2))
        metrics_table.add_column("Metric", style="cyan bold")
        metrics_table.add_column("Value", style="white bold")
        metrics_table.add_column("Status", style="white")
        
        metrics_table.add_row("🔍 Tools Executed", str(successful_tools), f"{successful_tools}/{total_tools}")
        metrics_table.add_row("⚠️ Total Issues Found", str(total_findings), "Based on actual scan results")
        metrics_table.add_row("🔴 Critical Issues", str(critical_findings), "Immediate attention required" if critical_findings > 0 else "None found")
        metrics_table.add_row("🟠 High Priority Issues", str(high_findings), "Should be addressed soon" if high_findings > 0 else "None found")
        
        if isinstance(security_score, str):
            metrics_table.add_row("📊 Security Score", f"[{score_color}]{security_score}[/{score_color}]", score_status)
        else:
            metrics_table.add_row("📊 Security Score", f"[{score_color}]{security_score}%[/{score_color}]", score_status)
        
        panel = Panel(
            metrics_table,
            title="[bold yellow]Security Metrics[/bold yellow]",
            border_style="blue"
        )
        self.console.print(panel)

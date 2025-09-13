#!/usr/bin/env python3
"""
Example usage script for AutoPentest AI
Demonstrates how to use the tool programmatically
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from config_manager import ConfigManager
from deepseek_client import DeepSeekClient
from tool_manager import ToolManager
from automation_engine import AutomationEngine
from report_generator import ReportGenerator

def example_basic_usage():
    """Example of basic tool usage"""
    print("🤖 AutoPentest AI - Basic Usage Example")
    print("=" * 50)
    
    # Initialize components
    config = ConfigManager()
    deepseek = DeepSeekClient(config)
    tool_manager = ToolManager(config)
    automation = AutomationEngine(config)
    reporter = ReportGenerator(config)
    
    # Example 1: Get tool recommendations
    print("\n1. Getting AI recommendations...")
    criteria = "Network scanning and vulnerability assessment for web server at 192.168.1.100"
    recommendations = deepseek.get_tool_recommendations(criteria)
    
    if recommendations:
        print(f"AI Explanation: {recommendations.get('explanation', 'N/A')}")
        print("Recommended tools:")
        for tool in recommendations.get('tools', []):
            print(f"  - {tool.get('name')}: {tool.get('purpose')}")
    
    # Example 2: Check tool status
    print("\n2. Checking tool availability...")
    common_tools = ["nmap", "nikto", "dirb"]
    for tool in common_tools:
        status = "✅ Installed" if tool_manager.is_tool_installed(tool) else "❌ Missing"
        print(f"  {tool}: {status}")
    
    # Example 3: Ask AI advisor
    print("\n3. AI Advisor example...")
    question = "What is the difference between active and passive reconnaissance?"
    answer = deepseek.ask_advisor_question(question)
    if answer:
        print(f"AI Answer: {answer[:200]}...")
    
    print("\n✅ Example completed!")

def example_automated_test():
    """Example of running an automated test"""
    print("\n🚀 AutoPentest AI - Automated Test Example")
    print("=" * 50)
    
    # Initialize components
    config = ConfigManager()
    deepseek = DeepSeekClient(config)
    automation = AutomationEngine(config)
    reporter = ReportGenerator(config)
    
    # Simulate tool recommendations
    mock_tools = [
        {
            "name": "nmap",
            "purpose": "Network discovery and port scanning",
            "priority": "high",
            "command_template": "nmap -sS -O TARGET"
        }
    ]
    
    criteria = "Quick network scan of localhost"
    
    print("Running automated test...")
    
    # Run tools (this will actually execute commands, so be careful!)
    # For this example, we'll just simulate the structure
    
    print("\n📊 Would generate reports in:")
    print(f"  - {Path('reports').absolute()}")
    
    print("\n✅ Automated test example completed!")

def example_report_generation():
    """Example of generating reports"""
    print("\n📋 AutoPentest AI - Report Generation Example")
    print("=" * 50)
    
    # Mock session data
    mock_session_data = {
        "session_id": "example_session_20240101_120000",
        "timestamp": "2024-01-01T12:00:00",
        "criteria": "Example penetration test",
        "tools": [
            {"name": "nmap", "purpose": "Port scanning"}
        ],
        "results": {
            "nmap": {
                "success": True,
                "command": "nmap -sS 127.0.0.1",
                "output": "Example nmap output...",
                "execution_time": 15.5,
                "analysis": {
                    "summary": "Found open ports on target",
                    "findings": [
                        {
                            "type": "open_port",
                            "details": "Port 80 is open",
                            "severity": "medium",
                            "recommendation": "Investigate web service"
                        }
                    ],
                    "statistics": {
                        "total_findings": 1,
                        "high_severity": 0,
                        "medium_severity": 1,
                        "low_severity": 0
                    }
                }
            }
        }
    }
    
    # Initialize reporter
    config = ConfigManager()
    reporter = ReportGenerator(config)
    
    print("Generating example reports...")
    
    # Generate reports
    report_file = reporter.generate_report(
        mock_session_data, 
        mock_session_data["criteria"],
        formats=["html", "markdown", "json"]
    )
    
    if report_file:
        print(f"✅ Report generated: {report_file}")
    
    # List existing reports
    reports = reporter.list_reports()
    print(f"\nFound {len(reports)} existing reports:")
    for report in reports[:3]:  # Show first 3
        print(f"  - {report['name']} ({report['date']}) - {report['size']}")
    
    print("\n✅ Report generation example completed!")

def main():
    """Run all examples"""
    print("🎯 AutoPentest AI - Usage Examples")
    print("=" * 60)
    
    # Check if configuration exists
    config_file = Path("config/config.json")
    if not config_file.exists():
        print("⚠️  Configuration not found!")
        print("Please run 'python setup.py' first to configure the tool.")
        return
    
    try:
        # Run examples
        example_basic_usage()
        example_automated_test()
        example_report_generation()
        
        print("\n🎉 All examples completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python main.py' to use the interactive CLI")
        print("2. Explore the generated reports in the reports/ directory")
        print("3. Check the logs/ directory for execution logs")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()

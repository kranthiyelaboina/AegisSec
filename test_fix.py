#!/usr/bin/env python3
"""
Test script to validate the 'str' object has no attribute 'get' fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.deepseek_client import DeepSeekClient
from src.report_generator import ReportGenerator
from src.config_manager import ConfigManager

def test_executive_summary_fix():
    """Test the fix for the executive summary generation"""
    
    # Sample session data that mimics the actual structure from logs
    sample_session_data = {
        "session_id": "test_20250913_123456",
        "timestamp": "2025-09-13T12:34:56.789012",
        "criteria": "Network Security assessment on localhost",
        "tools": [
            {
                "name": "nmap",
                "description": "Security testing tool: nmap"
            }
        ],
        "results": {
            "nmap": {
                "tool": "nmap",
                "command": "nmap 127.0.0.1",
                "success": False,
                "output": "",
                "error": "Tool 'nmap' not found. Please ensure it's installed and in PATH.",
                "execution_time": 0.005,
                "attempts": [
                    {
                        "success": False,
                        "output": "",
                        "error": "Tool 'nmap' not found. Please ensure it's installed and in PATH.",
                        "return_code": -1,
                        "execution_time": 0.005
                    }
                ]
            }
        },
        "summary": {},
        "intelligent_chaining": True
    }
    
    try:
        print("🔧 Testing DeepSeek Executive Summary Generation...")
        
        # Test DeepSeek client
        config_manager = ConfigManager()
        deepseek = DeepSeekClient()
        
        print("📊 Generating executive summary...")
        summary = deepseek.generate_executive_summary(sample_session_data)
        print(f"✅ Executive summary generated successfully!")
        print(f"📝 Summary preview: {summary[:100]}...")
        
        print("\n🔧 Testing Report Generator...")
        
        # Test Report Generator
        report_gen = ReportGenerator(config_manager)
        print("📊 Preparing comprehensive report data...")
        report_data = report_gen._prepare_comprehensive_report_data(sample_session_data, summary)
        print(f"✅ Report data prepared successfully!")
        print(f"📈 Statistics: {report_data['statistics']['total_tools']} tools, {report_data['statistics']['total_findings']} findings")
        
        print("\n🎉 All tests passed! The 'str' object has no attribute 'get' error has been fixed!")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_executive_summary_fix()

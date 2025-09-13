#!/usr/bin/env python3
"""
Test script to verify real-time AI analysis and accurate reporting
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cli import AegisSecCLI
from config_manager import ConfigManager
from deepseek_client import DeepSeekClient
import json

def test_real_analysis():
    """Test real-time analysis with actual tool outputs"""
    
    print("🚀 Testing Real-Time AI Analysis and Accurate Reporting")
    
    # Create test session data with actual tool outputs
    test_session_data = {
        "session_id": "test_real_analysis",
        "target": "127.0.0.1",
        "tools_used": ["nmap", "ping"],
        "results": [
            {
                "tool": "nmap",
                "success": False,
                "output": "",
                "error": "nmap: command not found",
                "execution_time": 0.05
            },
            {
                "tool": "ping", 
                "success": True,
                "output": "PING 127.0.0.1 (127.0.0.1): 56 data bytes\n64 bytes from 127.0.0.1: icmp_seq=0 ttl=64 time=0.043 ms\n64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.065 ms\n\n--- 127.0.0.1 ping statistics ---\n2 packets transmitted, 2 received, 0% packet loss",
                "error": "",
                "execution_time": 2.1
            }
        ]
    }
    
    # Initialize components
    config_manager = ConfigManager()
    config_manager.config['openrouter']['api_key'] = 'dummy-key-for-testing'
    
    client = DeepSeekClient()
    cli = AegisSecCLI(config_manager)
    
    # Test executive summary with real data
    print("\n📊 Testing Executive Summary Generation...")
    summary = client.generate_executive_summary(test_session_data)
    print(f"Generated Summary: {summary}")
    
    # Test security metrics calculation
    print("\n📈 Testing Security Metrics Calculation...")
    cli._show_security_metrics(test_session_data)
    
    # Test with more realistic scan results
    realistic_session = {
        "session_id": "test_realistic",
        "target": "testphp.vulnweb.com",
        "tools_used": ["nmap"],
        "results": [
            {
                "tool": "nmap",
                "success": True,
                "output": "Nmap scan report for testphp.vulnweb.com (44.228.249.3)\nHost is up (0.12s latency).\nNot shown: 996 filtered ports\nPORT     STATE SERVICE\n80/tcp   open  http\n443/tcp  open  https\n8080/tcp open  http-proxy\n8443/tcp open  https-alt\n\nNmap done: 1 IP address (1 host up) scanned in 4.56 seconds",
                "error": "",
                "execution_time": 4.56
            }
        ]
    }
    
    print("\n🎯 Testing with Realistic Scan Results...")
    summary2 = client.generate_executive_summary(realistic_session)
    print(f"Realistic Summary: {summary2}")
    
    print("\n📈 Realistic Metrics:")
    cli._show_security_metrics(realistic_session)
    
    print("\n✅ Real-time analysis test completed!")

if __name__ == "__main__":
    test_real_analysis()

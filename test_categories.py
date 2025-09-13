#!/usr/bin/env python3
"""
Test the enhanced category-specific tool recommendations
"""

import sys
import os
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from deepseek_client import DeepSeekClient

def test_category_recommendations():
    """Test category-specific tool recommendations"""
    
    print("🚀 Testing Enhanced Category-Specific Tool Recommendations\n")
    
    # Initialize client (will use fallback if no API key)
    try:
        client = DeepSeekClient()
    except:
        print("❌ Could not initialize client - testing fallback recommendations\n")
        return
    
    # Test different categories
    test_cases = [
        ("web_application", "example.com", "Web Application Security"),
        ("wireless", "192.168.1.1", "Wireless Security Testing"),
        ("social_engineering", "company.com", "Social Engineering Attacks"),
        ("privilege_escalation", "target-server", "Privilege Escalation Testing"),
        ("database_security", "db.example.com", "Database Security Assessment"),
        ("active_directory", "domain.local", "Active Directory Testing")
    ]
    
    for category, target, description in test_cases:
        print(f"📋 Category: {description}")
        print(f"🎯 Target: {target}")
        
        # Get recommendations
        tools = client.get_tool_recommendations(target, "comprehensive", category)
        
        print(f"🛠️ Recommended Tools ({len(tools)}):")
        for i, tool in enumerate(tools, 1):
            print(f"   {i}. {tool}")
        
        print("-" * 50)
    
    print("✅ Category-specific tool recommendation test completed!")

if __name__ == "__main__":
    test_category_recommendations()

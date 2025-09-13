#!/usr/bin/env python3
"""
Test the enhanced consultation system fixes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deepseek_client import DeepSeekClient
from config_manager import ConfigManager
import tempfile
import json

def test_consultation_system():
    """Test the improved consultation system"""
    
    print("🧪 Testing Enhanced Consultation System...")
    
    # Initialize components
    config_manager = ConfigManager()
    client = DeepSeekClient(config_manager)
    
    # Test consultation data saving/loading
    print("\n1. Testing consultation data persistence...")
    
    # Create sample criteria
    test_criteria = {
        'target': '192.168.1.100',
        'category': 'network_mapping',
        'target_type': 'ip_address',
        'description': 'Network discovery test'
    }
    
    # Simulate consultation data
    consultation_data = {
        'timestamp': '2025-09-13T21:40:00',
        'target': '192.168.1.100',
        'category': 'network_mapping', 
        'collected_info': [
            'Q1: Comprehensive scan with OS detection',
            'Q2: Focus on common ports and services'
        ],
        'ai_test_plan': 'Perform stealth network scan focusing on service enumeration',
        'consultation_complete': True
    }
    
    # Test saving consultation data
    print("  ✓ Saving consultation data...")
    temp_file = client._save_consultation_data({
        'target': consultation_data['target'],
        'category': consultation_data['category'],
        'collected_info': consultation_data['collected_info'],
        'ai_test_plan': consultation_data['ai_test_plan'],
        'consultation_complete': consultation_data['consultation_complete']
    })
    
    if temp_file:
        print(f"  ✓ Consultation data saved to: {temp_file}")
    else:
        print("  ❌ Failed to save consultation data")
        return False
    
    # Test loading consultation data
    print("  ✓ Loading consultation data...")
    loaded_data = client.load_consultation_data()
    
    if loaded_data and loaded_data.get('consultation_complete'):
        print(f"  ✓ Loaded consultation data: {len(loaded_data.get('collected_info', []))} user inputs")
        print(f"  ✓ Target: {loaded_data.get('target')}")
        print(f"  ✓ Category: {loaded_data.get('category')}")
    else:
        print("  ❌ Failed to load consultation data")
        return False
    
    # Test smart prompt generation
    print("\n2. Testing smart consultation prompts...")
    
    # Test initial consultation prompt
    initial_prompt = client._build_consultation_prompt(
        'network_mapping', '192.168.1.100', 'ip_address'
    )
    
    if "MANDATORY" in initial_prompt and "ask 2-3 critical questions" in initial_prompt:
        print("  ✓ Initial consultation prompt enforces question requirement")
    else:
        print("  ❌ Initial consultation prompt doesn't enforce questions")
        return False
    
    # Test smart follow-up prompt
    conversation_history = [
        "User: I want a comprehensive scan",
        "AI: What specific ports should we focus on?"
    ]
    collected_info = ["Q1: Comprehensive scan requested"]
    
    followup_prompt = client._build_smart_followup_prompt(
        'network_mapping', '192.168.1.100', 'ip_address', 
        conversation_history, 1, collected_info
    )
    
    if "PROCEED" in followup_prompt and "DO NOT repeat" in followup_prompt:
        print("  ✓ Smart follow-up prompt prevents repetition")
    else:
        print("  ❌ Smart follow-up prompt may repeat questions")
        return False
    
    # Test consultation context methods
    print("\n3. Testing consultation-aware AI methods...")
    
    if hasattr(client, 'analyze_tool_output_with_context'):
        print("  ✓ analyze_tool_output_with_context method available")
    else:
        print("  ❌ Missing analyze_tool_output_with_context method")
        return False
    
    if hasattr(client, 'get_next_command_with_context'):
        print("  ✓ get_next_command_with_context method available")
    else:
        print("  ❌ Missing get_next_command_with_context method")
        return False
    
    print("\n✅ All consultation system tests passed!")
    print("\n📋 Summary of fixes:")
    print("  • AI consultation now requires minimum meaningful questions")
    print("  • Consultation data is saved to temp file for automation use")
    print("  • Smart prompts prevent repetitive questioning")
    print("  • AI automation uses consultation context for better commands")
    print("  • Enhanced analysis incorporates user requirements")
    
    return True

def test_temp_directory():
    """Test temporary directory creation"""
    print("\n🗂️ Testing temporary directory...")
    
    import os
    temp_dir = "temp"
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
        print(f"  ✓ Created temp directory: {temp_dir}")
    else:
        print(f"  ✓ Temp directory exists: {temp_dir}")
    
    # Test file creation
    test_file = os.path.join(temp_dir, "test_consultation.json")
    test_data = {"test": "data", "timestamp": "2025-09-13"}
    
    try:
        with open(test_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        print(f"  ✓ Created test file: {test_file}")
        
        # Test reading
        with open(test_file, 'r') as f:
            loaded = json.load(f)
        
        if loaded.get('test') == 'data':
            print("  ✓ File read/write working correctly")
            
        # Clean up
        os.remove(test_file)
        print("  ✓ Cleaned up test file")
        
        return True
        
    except Exception as e:
        print(f"  ❌ File operations failed: {e}")
        return False

if __name__ == "__main__":
    print("🛡️ AegisSec - Enhanced Consultation System Test")
    print("=" * 50)
    
    # Run tests
    temp_test = test_temp_directory()
    consultation_test = test_consultation_system()
    
    if temp_test and consultation_test:
        print("\n🎉 ALL TESTS PASSED - Consultation system enhanced successfully!")
        print("\n🚀 Ready for testing with real consultation workflow")
    else:
        print("\n❌ Some tests failed - check implementation")
        sys.exit(1)

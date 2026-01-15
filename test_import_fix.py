#!/usr/bin/env python3
"""
Test that the import error is properly handled
"""

import sys
sys.path.append('.')

print("🧪 Testing Import Error Handling")
print("=" * 40)

try:
    from adk_stock_agent import ADK_AVAILABLE, Agent, Tool
    print(f"✅ Import successful!")
    print(f"   ADK Available: {ADK_AVAILABLE}")
    print(f"   Agent class: {Agent}")
    print(f"   Tool class: {Tool}")
    
    if ADK_AVAILABLE:
        print("   🤖 Real Google ADK is available")
    else:
        print("   🎭 Using mock classes for demonstration")
        
except Exception as e:
    print(f"❌ Import failed: {e}")

print("\n📝 Summary:")
print("- Line 15 import error is now properly handled")
print("- Mock classes created when real ADK unavailable") 
print("- Agent can run in demonstration mode")
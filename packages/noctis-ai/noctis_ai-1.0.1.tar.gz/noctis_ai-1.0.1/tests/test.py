#!/usr/bin/env python3
"""
Test script for Code Review Agent only.
Run this to test just the Code Review Agent.
"""

import sys
import time

def test_code_review_agent():
    """Test the Code Review Agent."""
    print("🧪 Testing Code Review Agent")
    print("=" * 50)
    
    try:
        from noctis import CodeReviewAgent
        print("✅ CodeReviewAgent imported successfully")
    except ImportError as e:
        print(f"❌ Error importing CodeReviewAgent: {e}")
        return False
    
    # Test input
    test_code = """
def bad_function(x):
    return x + "hello"  # Potential type error

def unsafe_function(user_input):
    return eval(user_input)  # Security risk

def inefficient_function(items):
    result = []
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] == items[j]:
                result.append(items[i])
    return result
"""
    
    print(f"\n Test Code:")
    print("-" * 40)
    print(test_code)
    print("-" * 40)
    
    try:
        # Create agent (change model here if needed)
        model = "gemma3:270m"  # Change this to your preferred model
        print(f"\n🔄 Creating CodeReviewAgent with model: {model}")
        
        agent = CodeReviewAgent(model)
        print("✅ CodeReviewAgent created successfully")
        
        # Test the agent
        print("\n Sending code for review...")
        start_time = time.time()
        
        response = agent.ask(f"Please review this code and identify any issues: {test_code}")
        
        response_time = time.time() - start_time
        
        # Display results
        print(f"\n✅ Review completed in {response_time:.2f}s")
        print(f" Response length: {len(response)} characters")
        print(f"\n💭 Code Review Response:")
        print("=" * 60)
        print(response)
        print("=" * 60)
        
        print(f"\n🎉 Code Review Agent test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing CodeReviewAgent:")
        print(f"   {type(e).__name__}: {e}")
        print(f"\n Full error details:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Code Review Agent Test Script")
    print("=" * 50)
    
    success = test_code_review_agent()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
#!/usr/bin/env python3
"""Simple test runner for the arbitrage betting application"""

import sys
import os
import subprocess

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def run_tests():
    """Run the test suite"""
    print("Running Arbitrage Betting App Tests")
    print("=" * 50)
    
    # Run pytest with coverage
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 'tests/', 
            '-v', '--tb=short',
            '--cov=backend/core', '--cov=backend/adapters', '--cov=backend/models'
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with return code {result.returncode}")
            
    except Exception as e:
        print(f"Error running tests: {e}")
        return False
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
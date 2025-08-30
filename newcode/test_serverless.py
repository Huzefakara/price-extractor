#!/usr/bin/env python3
"""
Simple test script for serverless API functions
"""

import sys
import os
import importlib.util

# Test the extract function
def test_extract_function():
    try:
        # Load the extract module dynamically
        api_dir = os.path.join(os.path.dirname(__file__), 'api')
        extract_path = os.path.join(api_dir, 'extract.py')
        
        spec = importlib.util.spec_from_file_location("extract", extract_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec from {extract_path}")
            
        extract_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(extract_module)
        
        extract_single_price = extract_module.extract_single_price
        
        # Test with a simple URL (you can replace with any e-commerce URL)
        test_url = "https://httpbin.org/html"  # Simple test URL
        
        print(f"Testing price extraction from: {test_url}")
        result = extract_single_price(test_url)
        
        print(f"Result: {result}")
        return result
        
    except Exception as e:
        print(f"Test failed: {e}")
        return None

if __name__ == "__main__":
    print("Testing serverless price extraction...")
    test_extract_function()
    print("Test completed!")
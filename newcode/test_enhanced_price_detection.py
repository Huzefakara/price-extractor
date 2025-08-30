#!/usr/bin/env python3
"""
Test script for enhanced price detection (crossed-out vs sale prices)
"""

import requests
import json

def test_enhanced_price_detection():
    """Test the enhanced price detection with a simulated scenario"""
    
    # Create a test HTML content that simulates the €595 crossed-out, €476 sale price scenario
    test_html = """
    <html>
    <body>
        <div class="price-container">
            <span class="was-price" style="text-decoration: line-through;">€595,00</span>
            <span class="sale-price current-price">€476,00</span>
        </div>
        <div class="product-info">
            <div class="price-box">
                <div class="price-current">€476,00</div>
                <div class="price-original crossed-price">€595,00</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Test the enhanced price extraction directly
    from api.extract import extract_price_with_type
    
    print("🧪 Testing Enhanced Price Detection")
    print("="*50)
    
    try:
        price_data = extract_price_with_type(test_html, "test-url")
        
        print("📊 EXTRACTED PRICE DATA:")
        print(f"  Best Price (for comparison): {price_data.get('best_price', 'None')}")
        print(f"  Current Price: {price_data.get('current_price', 'None')}")
        print(f"  Sale Price: {price_data.get('sale_price', 'None')}")
        print(f"  Original Price: {price_data.get('original_price', 'None')}")
        print(f"  Price Type: {price_data.get('price_type', 'None')}")
        print(f"  Discount: {price_data.get('discount_percentage', 'None')}%")
        
        print("\n🎯 EXPECTED RESULTS:")
        print("  Best Price should be: €476,00 (the sale price)")
        print("  Original Price should be: €595,00 (the crossed-out price)")
        print("  Price Type should be: sale or discounted")
        
        print("\n✅ TEST RESULTS:")
        if price_data.get('best_price') == '€476,00':
            print("  ✅ PASS: Correctly detected sale price €476,00")
        else:
            print(f"  ❌ FAIL: Expected €476,00 but got {price_data.get('best_price')}")
            
        if price_data.get('original_price') == '€595,00':
            print("  ✅ PASS: Correctly detected original price €595,00")
        else:
            print(f"  ❌ FAIL: Expected €595,00 but got {price_data.get('original_price')}")
            
        if price_data.get('price_type') in ['sale', 'discounted']:
            print(f"  ✅ PASS: Correctly identified as {price_data.get('price_type')}")
        else:
            print(f"  ❌ FAIL: Expected 'sale' or 'discounted' but got {price_data.get('price_type')}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        
    print("\n" + "="*50)

def test_real_world_csv():
    """Test with a real CSV file using the API"""
    
    # Create a test CSV with a known problematic URL
    csv_content = """product_name,our_price,competitor_url_1
Test Product,€500,https://example.com/product"""
    
    print("\n🌐 Testing with API endpoint...")
    
    try:
        # Write test CSV
        with open('test_price_detection.csv', 'w') as f:
            f.write(csv_content)
        
        # Test with API
        with open('test_price_detection.csv', 'rb') as file:
            files = {'file': file}
            response = requests.post('http://localhost:5000/api/compare-csv', files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API Test successful!")
                
                # Show enhanced price details for first product
                if result.get('results') and len(result['results']) > 0:
                    product = result['results'][0]
                    if product.get('competitor_results'):
                        for comp in product['competitor_results']:
                            if comp.get('price_details'):
                                details = comp['price_details']
                                print(f"\nCompetitor: {comp['url'][:30]}...")
                                print(f"  Detected Price: {comp.get('price', 'None')}")
                                print(f"  Price Type: {details.get('price_type', 'None')}")
                                print(f"  Current: {details.get('current_price', 'None')}")
                                print(f"  Original: {details.get('original_price', 'None')}")
                                print(f"  Sale: {details.get('sale_price', 'None')}")
                                print(f"  Discount: {details.get('discount_percentage', 'None')}%")
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"❌ API Test Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Enhanced Price Detection Test Suite")
    print("Testing the improved logic for €595 (crossed-out) vs €476 (sale) scenario\n")
    
    # Test 1: Direct function test
    test_enhanced_price_detection()
    
    # Test 2: API test (optional - requires server running)
    try:
        test_real_world_csv()
    except:
        print("\n⚠️  API test skipped (server not running)")
        
    print("\n🎉 Test suite completed!")
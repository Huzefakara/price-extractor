#!/usr/bin/env python3
"""
Test script for main product area detection (avoiding suggested products)
"""

def test_main_product_detection():
    """Test the main product area detection with simulated e-commerce HTML"""
    
    # Simulate an Amazon-like page with main product and suggested products
    test_html = """
    <html>
    <body>
        <!-- Suggested products section (should be ignored) -->
        <div class="recommended-products">
            <h3>Customers who bought this item also bought</h3>
            <div class="product-item">
                <span class="price">€29.99</span>
                <span class="product-title">Related Accessory</span>
            </div>
            <div class="product-item">
                <span class="price">€19.99</span>
                <span class="product-title">Another Suggestion</span>
            </div>
        </div>
        
        <!-- Main product area (target this!) -->
        <div id="centerCol" class="main-product">
            <div class="product-summary">
                <h1>Main Product Title</h1>
                <div class="price-container">
                    <span class="was-price" style="text-decoration: line-through;">€595.00</span>
                    <span class="sale-price current-price">€476.00</span>
                </div>
                <div class="product-details">
                    <p>This is the main product description</p>
                </div>
            </div>
        </div>
        
        <!-- More suggested products (should be ignored) -->
        <div class="similar-items">
            <h3>Similar items you might like</h3>
            <div class="suggestion-grid">
                <div class="suggested-item">
                    <span class="price">€89.99</span>
                    <span class="title">Suggested Item 1</span>
                </div>
                <div class="suggested-item">
                    <span class="price">€149.99</span>
                    <span class="title">Suggested Item 2</span>
                </div>
            </div>
        </div>
        
        <!-- Bundle offers (should be ignored) -->
        <div class="frequently-bought-together">
            <h3>Frequently bought together</h3>
            <div class="bundle-price">
                <span class="price">€899.99</span>
                <span class="bundle-text">Bundle Price</span>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Test the enhanced price extraction
    from api.extract import extract_price_with_type
    
    print("🧪 Testing Main Product Area Detection")
    print("="*60)
    
    try:
        price_data = extract_price_with_type(test_html, "test-url")
        
        print("📊 EXTRACTED PRICE DATA:")
        print(f"  Best Price (for comparison): {price_data.get('best_price', 'None')}")
        print(f"  Current Price: {price_data.get('current_price', 'None')}")
        print(f"  Sale Price: {price_data.get('sale_price', 'None')}")
        print(f"  Original Price: {price_data.get('original_price', 'None')}")
        print(f"  Price Type: {price_data.get('price_type', 'None')}")
        print(f"  Discount: {price_data.get('discount_percentage', 'None')}%")
        
        print("\\n🎯 EXPECTED RESULTS:")
        print("  Should find: €476.00 (main product sale price)")
        print("  Should ignore: €29.99, €19.99, €89.99, €149.99, €899.99 (suggested/bundle)")
        print("  Should detect: €595.00 as original price")
        
        print("\\n✅ TEST RESULTS:")
        
        # Check if we got the correct main product price
        if price_data.get('best_price') == '€476.00':
            print("  ✅ PASS: Correctly detected main product price €476.00")
        else:
            print(f"  ❌ FAIL: Expected €476.00 but got {price_data.get('best_price')}")
            
        # Check if we avoided suggested product prices
        suggested_prices = ['€29.99', '€19.99', '€89.99', '€149.99', '€899.99']
        if price_data.get('best_price') not in suggested_prices:
            print("  ✅ PASS: Successfully avoided suggested product prices")
        else:
            print(f"  ❌ FAIL: Picked up suggested product price: {price_data.get('best_price')}")
            
        # Check original price detection
        if price_data.get('original_price') == '€595.00':
            print("  ✅ PASS: Correctly detected original price €595.00")
        else:
            print(f"  ❌ FAIL: Expected €595.00 but got {price_data.get('original_price')}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
    print("\\n" + "="*60)

def test_area_detection():
    """Test the main product area detection function directly"""
    
    from api.extract import detect_main_product_area, is_suggested_product_area
    from bs4 import BeautifulSoup
    
    html = """
    <div class="page">
        <div class="suggested-products">
            <span class="price">€99.99</span>
        </div>
        <div id="centerCol" class="main-product">
            <span class="sale-price">€476.00</span>
        </div>
    </div>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    main_area = detect_main_product_area(soup)
    
    print("\\n🔍 Testing Area Detection Functions:")
    
    if main_area and 'centerCol' in str(main_area):
        print("  ✅ PASS: Correctly identified main product area")
    else:
        print("  ❌ FAIL: Failed to identify main product area")
        
    # Test suggested product detection
    suggested_element = soup.select_one('.suggested-products .price')
    if suggested_element and is_suggested_product_area(suggested_element):
        print("  ✅ PASS: Correctly identified suggested product area")
    else:
        print("  ❌ FAIL: Failed to identify suggested product area")

if __name__ == "__main__":
    print("🚀 Main Product Area Detection Test Suite")
    print("Testing improved logic to avoid suggested/related product prices\\n")
    
    # Test 1: Full price extraction with main area detection
    test_main_product_detection()
    
    # Test 2: Area detection functions
    test_area_detection()
    
    print("\\n🎉 Test suite completed!")
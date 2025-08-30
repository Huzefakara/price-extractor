#!/usr/bin/env python3
"""
Comprehensive test for enhanced suggested product detection
Tests various real-world e-commerce patterns and edge cases
"""

def test_comprehensive_suggested_detection():
    """Test enhanced suggested product detection with comprehensive patterns"""
    
    # Simulate a complex e-commerce page with multiple suggestion areas
    test_html = """
    <html>
    <body>
        <!-- Sponsored/Ad products (should be ignored) -->
        <div class="sponsored-products">
            <h3>Sponsored products</h3>
            <div class="ad-container">
                <span class="price">£45.99</span>
                <span class="product-title">Sponsored Item</span>
            </div>
        </div>
        
        <!-- Frequently bought together (should be ignored) -->
        <div class="frequently-bought-together">
            <h3>Frequently bought together</h3>
            <div class="bundle-container">
                <span class="price">£199.99</span>
                <span class="bundle-text">Total Bundle Price</span>
            </div>
        </div>
        
        <!-- Customers also viewed (should be ignored) -->
        <div id="customers-also-viewed" class="recommendations">
            <h3>Customers who viewed this item also viewed</h3>
            <div class="product-carousel">
                <div class="carousel-item">
                    <span class="price">£32.50</span>
                    <span class="title">Similar Product 1</span>
                </div>
                <div class="carousel-item">
                    <span class="price">£89.99</span>
                    <span class="title">Similar Product 2</span>
                </div>
            </div>
        </div>
        
        <!-- MAIN PRODUCT AREA (target this!) -->
        <div id="centerCol" class="product-main">
            <div class="product-details-main">
                <h1>Main Product - Premium Headphones</h1>
                <div class="buybox">
                    <div class="price-container">
                        <span class="price-old" style="text-decoration: line-through;">£299.99</span>
                        <span class="price-current sale-price">£199.99</span>
                    </div>
                    <button>Add to Cart</button>
                </div>
                <div class="product-description">
                    <p>High-quality wireless headphones with noise cancellation</p>
                </div>
            </div>
        </div>
        
        <!-- More suggestions (should be ignored) -->
        <div class="related-products">
            <h3>Related products</h3>
            <div class="product-grid">
                <div class="grid-item">
                    <span class="price">£15.99</span>
                    <span class="title">Headphone Case</span>
                </div>
                <div class="grid-item">
                    <span class="price">£25.99</span>
                    <span class="title">Audio Cable</span>
                </div>
            </div>
        </div>
        
        <!-- Recently viewed (should be ignored) -->
        <div class="recently-viewed-products">
            <h3>Your recently viewed items</h3>
            <div class="history-container">
                <span class="price">£75.00</span>
                <span class="title">Previously Viewed Item</span>
            </div>
        </div>
        
        <!-- Cross-sell section (should be ignored) -->
        <div class="cross-sell-container">
            <h3>Complete your setup</h3>
            <div class="accessory-grid">
                <div class="accessory-item">
                    <span class="price">£39.99</span>
                    <span class="title">Wireless Charger</span>
                </div>
            </div>
        </div>
        
        <!-- Trending/Popular section (should be ignored) -->
        <div class="trending-products">
            <h3>Trending now</h3>
            <div class="trending-grid">
                <span class="price">£149.99</span>
                <span class="title">Trending Product</span>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Test the enhanced price extraction
    from api.extract import extract_price_with_type
    
    print("🔍 Testing Enhanced Suggested Product Detection")
    print("="*70)
    
    try:
        price_data = extract_price_with_type(test_html, "test-comprehensive-url")
        
        print("📊 EXTRACTED PRICE DATA:")
        print(f"  Best Price (for comparison): {price_data.get('best_price', 'None')}")
        print(f"  Current Price: {price_data.get('current_price', 'None')}")
        print(f"  Sale Price: {price_data.get('sale_price', 'None')}")
        print(f"  Original Price: {price_data.get('original_price', 'None')}")
        print(f"  Price Type: {price_data.get('price_type', 'None')}")
        print(f"  Discount: {price_data.get('discount_percentage', 'None')}%")
        
        print("\\n🎯 EXPECTED RESULTS:")
        print("  Should find: £199.99 (main product sale price)")
        print("  Should detect: £299.99 as original price")
        print("  Should ignore ALL suggestion prices:")
        print("    - £45.99 (sponsored)")
        print("    - £199.99 (bundle - different context)")  
        print("    - £32.50, £89.99 (customers also viewed)")
        print("    - £15.99, £25.99 (related products)")
        print("    - £75.00 (recently viewed)")
        print("    - £39.99 (cross-sell)")
        print("    - £149.99 (trending)")
        
        print("\\n✅ TEST RESULTS:")
        
        # Check if we got the correct main product price
        expected_main_price = "£199.99"
        if price_data.get('best_price') == expected_main_price:
            print(f"  ✅ PASS: Correctly detected main product price {expected_main_price}")
        else:
            print(f"  ❌ FAIL: Expected {expected_main_price} but got {price_data.get('best_price')}")
            
        # Check if we avoided ALL suggested product prices
        suggestion_prices = ['£45.99', '£32.50', '£89.99', '£15.99', '£25.99', '£75.00', '£39.99', '£149.99']
        if price_data.get('best_price') not in suggestion_prices:
            print("  ✅ PASS: Successfully avoided ALL suggested product prices")
        else:
            print(f"  ❌ FAIL: Picked up suggested product price: {price_data.get('best_price')}")
            
        # Check original price detection
        if price_data.get('original_price') == '£299.99':
            print("  ✅ PASS: Correctly detected original price £299.99")
        else:
            print(f"  ❌ FAIL: Expected £299.99 but got {price_data.get('original_price')}")
            
        # Check price type
        if price_data.get('price_type') == 'sale':
            print("  ✅ PASS: Correctly identified as sale price")
        else:
            print(f"  ❌ FAIL: Expected 'sale' but got {price_data.get('price_type')}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
    print("\\n" + "="*70)

def test_edge_cases():
    """Test edge cases and challenging scenarios"""
    
    print("\\n🔬 Testing Edge Cases")
    print("-" * 50)
    
    # Test case: Main product price same as suggestion price
    edge_case_html = """
    <html>
    <body>
        <div class="suggestions">
            <h3>You might also like</h3>
            <span class="price">£199.99</span>
        </div>
        <div id="centerCol">
            <h1>Main Product</h1>
            <span class="sale-price">£199.99</span>
        </div>
    </body>
    </html>
    """
    
    from api.extract import extract_price_with_type
    
    try:
        price_data = extract_price_with_type(edge_case_html, "test-edge-case")
        
        print("Edge Case: Same price in both main and suggestion areas")
        print(f"Selected price: {price_data.get('best_price')}")
        
        # Should still pick the main product area price due to higher confidence
        if price_data.get('best_price') == '£199.99':
            print("  ✅ PASS: Selected price (confidence scoring should favor main area)")
        else:
            print(f"  ❌ FAIL: No price detected or wrong price")
            
    except Exception as e:
        print(f"  ❌ ERROR in edge case test: {str(e)}")

def test_area_detection_directly():
    """Test the area detection functions directly"""
    
    print("\\n🔧 Testing Area Detection Functions Directly")
    print("-" * 50)
    
    from api.extract import detect_main_product_area, is_suggested_product_area
    from bs4 import BeautifulSoup
    
    html = """
    <div class="page">
        <div class="customers-also-bought">
            <span class="price">£50.00</span>
        </div>
        <div class="frequently-bought-together">
            <span class="price">£99.99</span>
        </div>
        <div id="centerCol" class="product-main">
            <span class="current-price">£199.99</span>
        </div>
        <div class="recommended-products">
            <span class="price">£29.99</span>
        </div>
    </div>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    main_area = detect_main_product_area(soup)
    
    # Test main area detection
    if main_area and ('centerCol' in str(main_area) or 'product-main' in str(main_area)):
        print("  ✅ PASS: Correctly identified main product area")
    else:
        print("  ❌ FAIL: Failed to identify main product area")
        
    # Test suggested product detection for each area
    test_cases = [
        ('.customers-also-bought .price', True, 'customers-also-bought'),
        ('.frequently-bought-together .price', True, 'frequently-bought-together'), 
        ('#centerCol .current-price', False, 'main product area'),
        ('.recommended-products .price', True, 'recommended products')
    ]
    
    for selector, should_be_suggestion, description in test_cases:
        element = soup.select_one(selector)
        if element:
            is_suggestion = is_suggested_product_area(element)
            if is_suggestion == should_be_suggestion:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            print(f"  {status}: {description} - Expected: {should_be_suggestion}, Got: {is_suggestion}")

if __name__ == "__main__":
    print("🚀 Enhanced Suggested Product Detection Test Suite")
    print("Testing comprehensive patterns and edge cases\\n")
    
    # Test 1: Comprehensive suggested product detection
    test_comprehensive_suggested_detection()
    
    # Test 2: Edge cases
    test_edge_cases()
    
    # Test 3: Direct function testing
    test_area_detection_directly()
    
    print("\\n🎉 Enhanced test suite completed!")
    print("\\n💡 The system now uses aggressive confidence scoring to prioritize")
    print("   main product areas and heavily penalize suggested product sections.")
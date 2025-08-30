import os
from flask import Flask, request, jsonify, render_template
import asyncio
import json
import re
import time
import csv
import io
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

# Get the directory of the current script and find templates
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
template_dir = os.path.join(project_root, 'templates')

app = Flask(__name__, template_folder=template_dir)

# Constants
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

PRICE_RE = re.compile(r'(?:£|\$|€)\s?[0-9][0-9\.,]*')

def parse_price_value(price_str):
    """Extract numeric value from price string"""
    if not price_str:
        return None
    
    # Remove currency symbols and clean the string
    cleaned = re.sub(r'[£$€,\s]', '', str(price_str))
    
    try:
        return float(cleaned)
    except ValueError:
        return None

def compare_prices(our_price, competitor_price):
    """Compare our price with competitor price"""
    our_val = parse_price_value(our_price)
    comp_val = parse_price_value(competitor_price)
    
    if our_val is None or comp_val is None:
        return 'unknown'
    
    if our_val < comp_val:
        return 'lower'  # We are cheaper
    elif our_val > comp_val:
        return 'higher'  # We are more expensive
    else:
        return 'equal'

def format_comparison_result(comparison, our_price, competitor_price):
    """Format comparison result with recommendations"""
    our_val = parse_price_value(our_price)
    comp_val = parse_price_value(competitor_price)
    
    if our_val is None or comp_val is None:
        return {
            'status': 'unknown',
            'message': 'Unable to compare prices',
            'difference': 'N/A',
            'recommendation': 'Check price formats'
        }
    
    if comparison == 'lower':
        difference = comp_val - our_val
        percentage = round((difference / comp_val) * 100, 2)
        return {
            'status': 'competitive',
            'message': f'Our price is {percentage}% lower than competitor',
            'difference': f'+{difference:.2f}',
            'recommendation': 'Good position - we are cheaper'
        }
    elif comparison == 'higher':
        difference = our_val - comp_val
        percentage = round((difference / our_val) * 100, 2)
        return {
            'status': 'expensive',
            'message': f'Our price is {percentage}% higher than competitor',
            'difference': f'-{difference:.2f}',
            'recommendation': 'Consider price adjustment to be more competitive'
        }
    elif comparison == 'equal':
        return {
            'status': 'equal',
            'message': 'Prices are equal',
            'difference': '0.00',
            'recommendation': 'Consider slight reduction to gain competitive edge'
        }
    else:
        return {
            'status': 'unknown',
            'message': 'Unable to compare prices',
            'difference': 'N/A',
            'recommendation': 'Check price formats'
        }

def parse_csv_content(csv_content):
    """Parse CSV content and extract product data"""
    try:
        # Parse CSV content
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        products = []
        
        for row in csv_reader:
            # Extract product information
            product_name = row.get('product_name', '').strip()
            our_price = row.get('our_price', '').strip()
            
            # Extract competitor URLs (looking for columns with 'competitor' or 'url')
            competitor_urls = []
            for key, value in row.items():
                if ('competitor' in key.lower() or 'url' in key.lower()) and value.strip():
                    competitor_urls.append(value.strip())
            
            if product_name and our_price and competitor_urls:
                products.append({
                    'product_name': product_name,
                    'our_price': our_price,
                    'competitor_urls': competitor_urls
                })
        
        return products
    except Exception as e:
        raise Exception(f"Error parsing CSV: {str(e)}")

def process_product_comparison(product_data):
    """Process a single product's price comparison"""
    try:
        product_name = product_data['product_name']
        our_price = product_data['our_price']
        competitor_urls = product_data['competitor_urls']
        
        # Extract prices from competitor URLs
        competitor_results = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_url = {executor.submit(extract_single_price, url): url for url in competitor_urls}
            
            for future in concurrent.futures.as_completed(future_to_url, timeout=60):
                try:
                    result = future.result()
                    url = future_to_url[future]
                    
                    if result['price']:
                        comparison = compare_prices(our_price, result['price'])
                        comparison_details = format_comparison_result(comparison, our_price, result['price'])
                        
                        # Add price type information to details
                        price_details = result.get('price_details', {})
                        # Ensure comparison_details is a dictionary that can hold any type
                        comparison_details = dict(comparison_details)
                        comparison_details['competitor_price_info'] = {
                            'actual_price': result['price'],
                            'price_type': price_details.get('price_type', 'unknown'),
                            'original_price': price_details.get('original_price'),
                            'discount_percentage': price_details.get('discount_percentage')
                        }
                        
                        # Add discount information to the message if available
                        if price_details.get('discount_percentage'):
                            comparison_details['competitor_discount'] = f"Competitor has {price_details['discount_percentage']}% discount"
                        
                        competitor_results.append({
                            'url': url,
                            'price': result['price'],
                            'price_details': price_details,
                            'comparison': comparison,
                            'details': comparison_details,
                            'status': 'success'
                        })
                    else:
                        competitor_results.append({
                            'url': url,
                            'price': None,
                            'price_details': result.get('price_details', {}),
                            'comparison': 'unknown',
                            'details': {'status': 'no_price', 'message': 'No price found'},
                            'status': 'no_price_found'
                        })
                except Exception as e:
                    url = future_to_url[future]
                    competitor_results.append({
                        'url': url,
                        'price': None,
                        'price_details': {},
                        'comparison': 'error',
                        'details': {'status': 'error', 'message': str(e)},
                        'status': 'error'
                    })
        
        # Generate summary
        successful_comparisons = [r for r in competitor_results if r['status'] == 'success']
        lower_count = len([r for r in successful_comparisons if r['comparison'] == 'lower'])
        higher_count = len([r for r in successful_comparisons if r['comparison'] == 'higher'])
        equal_count = len([r for r in successful_comparisons if r['comparison'] == 'equal'])
        
        overall_recommendation = 'competitive' if lower_count >= higher_count else 'consider_adjustment'
        
        return {
            'product_name': product_name,
            'our_price': our_price,
            'competitor_results': competitor_results,
            'summary': {
                'total_competitors': len(competitor_urls),
                'successful_extractions': len(successful_comparisons),
                'lower_than_competitors': lower_count,
                'higher_than_competitors': higher_count,
                'equal_to_competitors': equal_count,
                'overall_recommendation': overall_recommendation
            },
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'product_name': product_data.get('product_name', 'Unknown'),
            'our_price': product_data.get('our_price', 'Unknown'),
            'competitor_results': [],
            'summary': {},
            'status': 'error',
            'error': str(e)
        }

def extract_price_with_type(html_content, url):
    """Extract price with type classification (original, sale, current)"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # STEP 1: Detect main product area to avoid suggested products
        main_product_area = detect_main_product_area(soup)
        
        # Initialize price data structure
        price_data = {
            'current_price': None,
            'original_price': None,
            'sale_price': None,
            'price_type': 'unknown',
            'discount_percentage': None,
            'best_price': None  # The actual selling price to use for comparison
        }
        
        # Strategy 1: JSON-LD structured data with price analysis
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                structured_prices = extract_structured_prices(data)
                if structured_prices:
                    price_data.update(structured_prices)
                    if price_data['best_price']:
                        return price_data
            except:
                continue
        
        # Strategy 2: Smart CSS selector analysis for different price types
        price_selectors = {
            'sale_price': [
                # Common sale price selectors
                '.sale-price', '.price-sale', '.discounted-price', '.offer-price',
                '.deal-price', '.reduced-price', '.special-price', '.promo-price',
                '.price-now', '.price-current', '.current-price', '.final-price',
                '.price-reduced', '.price-special', '.price-discount',
                
                # Specific e-commerce patterns
                '.price-box .price:not(.was-price)', '.price-container .price:not(.original)',
                '.product-price .current', '.sale .price', '.discount .price',
                '.offer .price', '.special .price',
                
                # Data attributes and test IDs
                '[data-testid*="sale"]', '[data-testid*="current"]', '[data-testid*="offer"]',
                '[data-price-type="sale"]', '[data-price-type="current"]',
                '[data-automation-id*="price-current"]',
                
                # Additional common patterns
                '.price-value:not(.was)', '.main-price:not(.original)',
                '.product-price-value:not(.crossed)', '.price-primary',
                '.price-big', '.price-large', '.price-main'
            ],
            'original_price': [
                # Original/was price selectors
                '.original-price', '.regular-price', '.was-price', '.old-price',
                '.price-was', '.price-original', '.price-regular', '.list-price',
                '.msrp', '.rrp', '.crossed-price', '.strike-price',
                '.price-strike', '.price-crossed', '.price-before', '.price-old',
                '.rrp-price', '.before-price', '.prev-price', '.previous-price',
                
                # Specific patterns for crossed-out prices
                'del .price', 's .price', '.strikethrough .price',
                '.line-through .price', '.text-decoration-line-through .price',
                
                # Data attributes
                '[data-testid*="was"]', '[data-testid*="original"]', '[data-testid*="regular"]',
                '[data-price-type="was"]', '[data-price-type="original"]',
                '[data-automation-id*="price-was"]', '[data-automation-id*="price-original"]'
            ],
            'current_price': [
                # General price selectors (fallback)
                '.price', '.product-price', '.woocommerce-Price-amount', '.amount',
                '[itemprop="price"]', '[data-price]', '.price-current',
                '.product-price-value', '.price-box .price', '.final-price',
                '.price-display', '.price-value', '.product-price-amount'
            ]
        }
        
        # Extract prices by type - FOCUS ON MAIN PRODUCT AREA
        extracted_prices = {}
        for price_type, selectors in price_selectors.items():
            prices = []
            for selector in selectors:
                # Search within main product area first
                elements = main_product_area.select(selector)
                for element in elements:
                    # Check if this element is from suggested products area
                    if is_suggested_product_area(element):
                        continue  # Skip suggested product prices
                    
                    # Skip if element is hidden or has display: none
                    style = element.get('style', '')
                    if isinstance(style, str):
                        if 'display:none' in style.replace(' ', '') or 'display: none' in style:
                            continue
                    
                    # Enhanced crossed-out price detection
                    element_classes = element.get('class', [])
                    element_style = element.get('style', '')
                    parent_classes = element.parent.get('class', []) if element.parent else []
                    parent_style = element.parent.get('style', '') if element.parent else ''
                    
                    # Convert to lists if strings
                    if isinstance(element_classes, str):
                        element_classes = [element_classes]
                    if isinstance(parent_classes, str):
                        parent_classes = [parent_classes]
                    
                    # Check for crossed-out indicators
                    crossed_out_indicators = [
                        'strike', 'strikethrough', 'line-through', 'text-decoration-line-through',
                        'crossed', 'was-price', 'old-price', 'original-price', 'regular-price',
                        'rrp', 'msrp', 'list-price', 'before-price', 'was', 'orig'
                    ]
                    
                    # Check element and parent for crossed-out indicators
                    all_classes = element_classes + parent_classes
                    all_styles = [str(element_style), str(parent_style)]
                    
                    is_crossed_out = any(
                        indicator in ' '.join(all_classes).lower() or 
                        indicator in ' '.join(all_styles).lower() or
                        'text-decoration: line-through' in str(element_style).lower() or
                        'text-decoration:line-through' in str(element_style).lower()
                        for indicator in crossed_out_indicators
                    )
                    
                    # Additional visual checks for crossed-out prices
                    if element.name == 's' or element.name == 'del':  # HTML strikethrough tags
                        is_crossed_out = True
                    
                    # Skip crossed-out prices when looking for sale/current prices
                    if price_type in ['sale_price', 'current_price'] and is_crossed_out:
                        continue
                    
                    text = element.get_text().strip()
                    if text and PRICE_RE.search(text):
                        match = PRICE_RE.search(text)
                        if match:
                            price_value = match.group(0)
                            prices.append({
                                'value': price_value,
                                'element': element,
                                'is_crossed': is_crossed_out,
                                'selector': selector,
                                'confidence': calculate_main_product_confidence(element, price_type, is_crossed_out)
                            })
            extracted_prices[price_type] = prices
        
        # Strategy 3: Analyze price relationships and context
        price_data = analyze_price_relationships(extracted_prices, soup)
        
        # Strategy 4: Fallback - find most prominent price IN MAIN PRODUCT AREA
        if not price_data['best_price']:
            all_price_elements = main_product_area.find_all(text=PRICE_RE)
            price_candidates = []
            
            for text_node in all_price_elements:
                if text_node.parent:
                    element = text_node.parent
                    
                    # Skip if from suggested products area
                    if is_suggested_product_area(element):
                        continue
                    
                    price_match = PRICE_RE.search(str(text_node))
                    if price_match:
                        price_value = price_match.group(0)
                        
                        # Skip if element or parent has crossed-out indicators
                        element_classes = ' '.join(element.get('class', [])).lower()
                        parent_classes = ' '.join(element.parent.get('class', [])).lower() if element.parent else ''
                        
                        is_crossed = any(indicator in element_classes or indicator in parent_classes 
                                       for indicator in ['strike', 'crossed', 'was', 'old', 'original', 'regular'])
                        
                        if element.name in ['s', 'del'] or element.parent and element.parent.name in ['s', 'del']:
                            is_crossed = True
                        
                        if not is_crossed:  # Only consider non-crossed-out prices
                            confidence = calculate_main_product_confidence(element, 'current_price', is_crossed)
                            price_candidates.append({
                                'value': price_value,
                                'confidence': confidence,
                                'element': element
                            })
            
            if price_candidates:
                # Sort by confidence and take the best one
                price_candidates.sort(key=lambda x: x['confidence'], reverse=True)
                best_candidate = price_candidates[0]
                price_data['current_price'] = best_candidate['value']
                price_data['best_price'] = best_candidate['value']
                price_data['price_type'] = 'regular'
        
        return price_data
        
    except Exception as e:
        print(f"Error extracting price from {url}: {str(e)}")
        return {
            'current_price': None,
            'original_price': None,
            'sale_price': None,
            'price_type': 'error',
            'discount_percentage': None,
            'best_price': None
        }

def calculate_price_confidence(element, price_type, is_crossed_out):
    """Calculate confidence score for price based on element attributes"""
    confidence = 50  # Base confidence
    
    # Reduce confidence for crossed-out prices
    if is_crossed_out:
        confidence -= 30
    
    # Increase confidence for sale price indicators
    element_classes = ' '.join(element.get('class', [])).lower()
    element_text = element.get_text().lower()
    
    sale_indicators = ['sale', 'discount', 'offer', 'special', 'deal', 'reduced', 'now']
    original_indicators = ['was', 'orig', 'regular', 'list', 'rrp', 'msrp']
    
    if price_type == 'sale_price':
        if any(indicator in element_classes or indicator in element_text for indicator in sale_indicators):
            confidence += 20
        if any(indicator in element_classes or indicator in element_text for indicator in original_indicators):
            confidence -= 15
    
    elif price_type == 'original_price':
        if any(indicator in element_classes or indicator in element_text for indicator in original_indicators):
            confidence += 20
        if any(indicator in element_classes or indicator in element_text for indicator in sale_indicators):
            confidence -= 15
    
    # Check element prominence (font size, position)
    style = element.get('style', '')
    if 'font-size' in style:
        # Larger fonts typically indicate more prominent prices
        if any(size in style for size in ['large', 'xl', '2em', '1.5em']):
            confidence += 10
        elif any(size in style for size in ['small', 'xs', '0.8em', '0.9em']):
            confidence -= 10
    
    # Check for price position context
    parent = element.parent
    if parent:
        parent_classes = ' '.join(parent.get('class', [])).lower()
        if 'price-box' in parent_classes or 'price-container' in parent_classes:
            confidence += 15
    
    return max(0, min(100, confidence))  # Clamp between 0-100

def detect_main_product_area(soup):
    """Detect the main product area to avoid suggested/related products"""
    main_product_selectors = [
        # Amazon main product area
        '#dp-container', '#feature-bullets', '#apex_desktop', '#centerCol',
        '.a-section[data-feature-name="detailBullets"]', '#productDetails_feature_div',
        '#ppd', '#dp', '#detail-main', '#detail-bullets', '#feature-bullets',
        
        # Generic main product containers
        '.product-main', '.product-detail', '.product-info', '.main-product',
        '.product-container', '.product-wrapper', '.pd-wrap', '.pdp-container',
        '.product-details-main', '.product-page-main', '.item-details',
        '.product-content', '.product-summary', '.product-overview',
        
        # E-commerce specific patterns
        '[data-testid="product-container"]', '[data-testid="main-product"]',
        '[data-automation-id="product-main"]', '.js-product-container',
        '[data-module="ProductDetails"]', '[data-component="ProductInfo"]',
        
        # John Lewis / Currys / Argos specific
        '.product-overview', '.product-summary', '.product-hero',
        '.pdp-product-overview', '.product-information-wrapper',
        '.product-details-container', '.product-info-main',
        
        # ASOS / Next / Zara patterns
        '.product-hero', '.pdp-product', '.product-detail-wrapper',
        '.product-information', '.product-details-wrapper',
        
        # eBay patterns
        '.x-buybox', '.notranslate', '#mainContent', '.vim',
        
        # Shopify patterns
        '.product-single', '.product-form', '.product-detail',
        '.shopify-section', '[data-section-type="product"]',
        
        # WooCommerce patterns
        '.woocommerce-product-details', '.product', '.single-product',
        '.woocommerce .product', '.product-summary',
        
        # Schema.org product containers
        '[itemtype*="Product"]', '[itemscope][itemtype*="Product"]',
        
        # Common content areas
        '#content', '#main-content', '.main-content', '.content-main',
        '.page-content', '.container-main', '#primary-content'
    ]
    
    # Try to find main product area with higher specificity first
    for selector in main_product_selectors:
        main_area = soup.select_one(selector)
        if main_area:
            # Validate that this area actually contains product information
            area_text = main_area.get_text().lower()
            product_indicators = ['price', 'buy', 'add to cart', 'purchase', 'description']
            
            if any(indicator in area_text for indicator in product_indicators):
                return main_area
    
    # Fallback: try to identify by largest content area with product info
    potential_areas = soup.find_all(['div', 'section', 'article', 'main'], class_=True)
    scored_areas = []
    
    for area in potential_areas:
        score = score_product_area(area)
        if score > 30:  # Minimum threshold
            scored_areas.append((area, score))
    
    if scored_areas:
        # Return the highest scoring area
        scored_areas.sort(key=lambda x: x[1], reverse=True)
        return scored_areas[0][0]
    
    # Last resort: return body (full page) but with warning
    return soup

def score_product_area(element):
    """Score an element's likelihood of being the main product area"""
    score = 0
    
    # Check classes for product indicators
    classes = ' '.join(element.get('class', [])).lower()
    
    # Positive indicators
    product_indicators = [
        'product', 'item', 'detail', 'main', 'primary', 'hero', 'overview',
        'summary', 'information', 'description', 'specification'
    ]
    
    for indicator in product_indicators:
        if indicator in classes:
            score += 15
    
    # Check for price elements (good sign)
    price_elements = element.find_all(text=PRICE_RE)
    score += min(len(price_elements) * 5, 20)  # Cap at 20 points
    
    # Check for product schema
    if element.get('itemtype') and 'Product' in element.get('itemtype', ''):
        score += 25
    
    # Check size (larger areas more likely to be main product)
    text_length = len(element.get_text().strip())
    if text_length > 500:
        score += 10
    elif text_length > 1000:
        score += 15
    
    # Negative indicators (likely suggested products)
    negative_indicators = [
        'suggest', 'recommend', 'related', 'similar', 'also', 'bought',
        'viewed', 'cross-sell', 'upsell', 'bundle', 'accessory'
    ]
    
    for negative in negative_indicators:
        if negative in classes:
            score -= 20
    
    # Check for multiple product links (suggests listing/suggestions)
    product_links = element.find_all('a', href=True)
    if len(product_links) > 5:  # Too many links suggests it's a listing
        score -= 10
    
    return score

def is_suggested_product_area(element):
    """Check if an element is likely from suggested/related products section"""
    # First check if element is in a confirmed main product area
    current = element
    for level in range(3):
        if current.parent:
            current = current.parent
            parent_classes = ' '.join(current.get('class', [])).lower()
            parent_id = current.get('id', '').lower()
            
            # If we're in a confirmed main product area, NOT a suggestion
            main_product_confirmations = [
                'centerCol', 'dp-container', 'feature-bullets', 'product-main',
                'main-product', 'product-detail', 'buybox', 'product-summary'
            ]
            
            for confirmation in main_product_confirmations:
                if confirmation in parent_classes or confirmation in parent_id:
                    return False  # Definitely not a suggestion area
        else:
            break
    
    # Now check for suggested product indicators
    element_text = element.get_text().lower()
    classes = ' '.join(element.get('class', [])).lower()
    element_id = element.get('id', '').lower()
    
    # Check parent elements up to 5 levels for suggestion indicators
    current = element
    for level in range(5):
        if current.parent:
            current = current.parent
            parent_classes = ' '.join(current.get('class', [])).lower()
            parent_text = current.get_text().lower()
            parent_id = current.get('id', '').lower()
            
            # Enhanced suggested product text patterns
            suggestion_patterns = [
                'customers who bought', 'also bought', 'you might like', 'you may also like',
                'recommended', 'related products', 'similar items', 'similar products',
                'frequently bought together', 'customers also viewed', 'people also bought',
                'inspired by your', 'because you viewed', 'suggestions', 'recommended for you',
                'cross-sell', 'upsell', 'bundle', 'add-on', 'accessory', 'accessories',
                'complete your look', 'goes well with', 'pair with', 'bundle deals',
                'other customers', 'shoppers also', 'more like this', 'you might also need',
                'trending now', 'best sellers', 'top picks', 'featured products',
                'sponsored', 'advertisement', 'ad ', 'promoted', 'compare with similar',
                'alternative products', 'other options', 'more choices', 'explore similar',
                'recently viewed', 'your history', 'continue shopping', 'shop more'
            ]
            
            for pattern in suggestion_patterns:
                if (pattern in parent_text or pattern in parent_classes or 
                    pattern in parent_id or pattern in classes or pattern in element_id):
                    return True
            
            # Enhanced CSS class/ID indicators (but exclude main product areas)
            suggestion_identifiers = [
                'recommend', 'suggest', 'related', 'similar', 'also', 'other',
                'cross-sell', 'upsell', 'bundle', 'accessory', 'addon', 'add-on',
                'carousel', 'slider', 'grid-item', 'tile', 'card-grid',
                'recently-viewed', 'trending', 'featured', 'sponsored', 'ad-',
                'promotion', 'promo', 'deal-', 'offer-', 'sale-grid', 'product-grid',
                'listing', 'catalog', 'search-result', 'filter-result',
                'sidebar', 'aside', 'footer-products', 'header-products'
            ]
            
            all_identifiers = parent_classes + ' ' + parent_id + ' ' + classes + ' ' + element_id
            for identifier in suggestion_identifiers:
                if identifier in all_identifiers:
                    return True
            
            # Check for multiple product links in container (indicates listing/suggestions)
            if level <= 2:  # Only check close parents
                product_links = current.find_all('a', href=True)
                product_prices = current.find_all(text=PRICE_RE)
                
                # If container has many products, likely a suggestions area
                if len(product_links) > 4 or len(product_prices) > 3:
                    return True
            
            # Check for specific e-commerce suggestion containers
            ecommerce_suggestion_patterns = [
                'recommendations', 'similar-products', 'related-items', 
                'also-bought', 'you-might-like', 'frequently-together',
                'cross-sells', 'up-sells', 'product-recommendations',
                'recommended-products', 'suggestion-container', 'rec-container'
            ]
            
            for pattern in ecommerce_suggestion_patterns:
                if (pattern in parent_classes or pattern in parent_id or 
                    pattern.replace('-', '_') in parent_classes or 
                    pattern.replace('-', '') in parent_classes):
                    return True
        else:
            break
    
    return False

def calculate_main_product_confidence(element, price_type, is_crossed_out):
    """Enhanced confidence calculation for main product area pricing"""
    confidence = calculate_price_confidence(element, price_type, is_crossed_out)
    
    # HEAVILY penalize if element is in suggested product area
    if is_suggested_product_area(element):
        confidence -= 70  # Increased penalty from 50 to 70
        return max(0, confidence)  # Early return for suggested products
    
    # Major bonus for being in main product context
    current = element
    main_product_bonus = 0
    
    for level in range(7):  # Check up to 7 parent levels
        if current.parent:
            current = current.parent
            parent_classes = ' '.join(current.get('class', [])).lower()
            parent_id = current.get('id', '').lower()
            
            # Main product area indicators with different weights
            primary_indicators = [
                ('product-main', 25), ('main-product', 25), ('product-detail', 20),
                ('product-info', 20), ('product-container', 18), ('product-summary', 22),
                ('product-overview', 20), ('centerCol', 30), ('dp-container', 30),
                ('feature-bullets', 25), ('pdp-container', 22)
            ]
            
            secondary_indicators = [
                ('product-wrapper', 15), ('pd-wrap', 15), ('product-content', 18),
                ('item-details', 15), ('product-hero', 20), ('buybox', 25),
                ('product-form', 18), ('main-content', 12), ('primary-content', 15)
            ]
            
            # Check primary indicators (higher bonus)
            for indicator, bonus in primary_indicators:
                if indicator in parent_classes or indicator in parent_id:
                    main_product_bonus = max(main_product_bonus, bonus)
                    break
            
            # Check secondary indicators if no primary found
            if main_product_bonus == 0:
                for indicator, bonus in secondary_indicators:
                    if indicator in parent_classes or indicator in parent_id:
                        main_product_bonus = max(main_product_bonus, bonus)
            
            # Special bonus for schema.org product markup
            if current.get('itemtype') and 'Product' in current.get('itemtype', ''):
                main_product_bonus = max(main_product_bonus, 20)
            
            # Bonus for data attributes indicating main product
            data_attrs = ['data-testid', 'data-automation-id', 'data-component', 'data-module']
            for attr in data_attrs:
                attr_value = current.get(attr, '').lower()
                if any(term in attr_value for term in ['product', 'main', 'detail', 'info']):
                    main_product_bonus = max(main_product_bonus, 15)
                    break
        else:
            break
    
    confidence += main_product_bonus
    
    # Enhanced position-based scoring
    page_position_score = 0
    try:
        # Calculate element depth and sibling position
        depth = 0
        sibling_position = 0
        current = element
        
        # Get sibling position (earlier elements are more likely main product)
        if element.parent:
            siblings = list(element.parent.children)
            sibling_position = next((i for i, sibling in enumerate(siblings) if sibling == element), 0)
        
        # Calculate depth from root
        while current.parent and depth < 15:
            depth += 1
            current = current.parent
        
        # Scoring based on position heuristics
        if depth < 6:  # Very shallow = likely main content
            page_position_score = 15
        elif depth < 10:  # Reasonable depth
            page_position_score = 8
        elif depth < 15:  # Deep but acceptable
            page_position_score = 3
        
        # Bonus for being among first elements (early in DOM)
        if sibling_position < 3:
            page_position_score += 5
        
    except:
        pass
    
    confidence += page_position_score
    
    # Enhanced container analysis
    parent_container = element.parent
    if parent_container:
        # Count prices in same container
        sibling_prices = len(parent_container.find_all(text=PRICE_RE))
        
        # Penalize containers with too many prices (suggests listing)
        if sibling_prices > 4:
            confidence -= 20
        elif sibling_prices > 2:
            confidence -= 10
        
        # Check container size (larger containers more likely main product)
        container_text_length = len(parent_container.get_text().strip())
        if container_text_length > 1000:  # Large container
            confidence += 8
        elif container_text_length > 500:  # Medium container
            confidence += 5
        elif container_text_length < 100:  # Very small container (suspicious)
            confidence -= 5
    
    # Price type specific adjustments
    if price_type == 'sale_price' and not is_crossed_out:
        confidence += 5  # Prefer clear sale prices
    elif price_type == 'current_price' and not is_crossed_out:
        confidence += 3  # Prefer current prices over crossed-out
    
    return max(0, min(100, confidence))  # Clamp between 0-100

def extract_structured_prices(data):
    """Extract prices from JSON-LD structured data with type detection"""
    from typing import Dict, Any
    prices: Dict[str, Any] = {'current_price': None, 'original_price': None, 'sale_price': None}
    
    def find_prices_recursive(obj):
        if isinstance(obj, list):
            for item in obj:
                result = find_prices_recursive(item)
                if result:
                    return result
        elif isinstance(obj, dict):
            # Check if this object has @graph
            if "@graph" in obj:
                return find_prices_recursive(obj["@graph"])
            
            # Check if this is a product/offer object
            if obj.get("@type") in ("Product", "Offer", "AggregateOffer"):
                # Check offers array
                if "offers" in obj:
                    offers = obj["offers"]
                    if isinstance(offers, list) and offers:
                        offers = offers[0]
                    
                    if isinstance(offers, dict):
                        # Look for different price types
                        if "price" in offers:
                            prices['current_price'] = str(offers["price"])
                        if "highPrice" in offers:
                            prices['original_price'] = str(offers["highPrice"])
                        if "lowPrice" in offers:
                            prices['sale_price'] = str(offers["lowPrice"])
                        
                        # Return if we found prices
                        if any(prices.values()):
                            return prices
                
                # Check direct price
                if "price" in obj:
                    prices['current_price'] = str(obj["price"])
                    return prices
    
    result = find_prices_recursive(data)
    if result and any(result.values()):
        # Determine best price and type
        if result['sale_price']:
            result['best_price'] = result['sale_price']
            result['price_type'] = 'sale'
        elif result['current_price']:
            result['best_price'] = result['current_price']
            result['price_type'] = 'regular'
        return result
    return None

def analyze_price_relationships(extracted_prices, soup):
    """Analyze extracted prices to determine relationships and select best price"""
    price_data = {
        'current_price': None,
        'original_price': None,
        'sale_price': None,
        'price_type': 'unknown',
        'discount_percentage': None,
        'best_price': None
    }
    
    # Sort prices by confidence score (highest first)
    for price_type in extracted_prices:
        if extracted_prices[price_type]:
            extracted_prices[price_type].sort(key=lambda x: x.get('confidence', 0), reverse=True)
    
    # Process sale prices (highest priority) - exclude crossed-out prices
    sale_prices = [p for p in extracted_prices.get('sale_price', []) if not p.get('is_crossed', False)]
    if sale_prices:
        best_sale = sale_prices[0]
        sale_price = best_sale['value']
        price_data['sale_price'] = sale_price
        price_data['best_price'] = sale_price
        price_data['price_type'] = 'sale'
    
    # Process original prices - prefer crossed-out or "was" prices
    original_prices = extracted_prices.get('original_price', [])
    if original_prices:
        # Prefer crossed-out prices for original price
        crossed_originals = [p for p in original_prices if p.get('is_crossed', False)]
        if crossed_originals:
            original_price = crossed_originals[0]['value']
        else:
            original_price = original_prices[0]['value']
        price_data['original_price'] = original_price
        
        # If we have both sale and original, calculate discount
        if price_data['sale_price']:
            try:
                sale_val = parse_price_value(price_data['sale_price'])
                orig_val = parse_price_value(original_price)
                if sale_val and orig_val and orig_val > sale_val:
                    discount = ((orig_val - sale_val) / orig_val) * 100
                    price_data['discount_percentage'] = round(discount, 1)
            except:
                pass
    
    # Process current prices (if no sale price found) - exclude crossed-out prices
    if not price_data['best_price']:
        current_prices = [p for p in extracted_prices.get('current_price', []) if not p.get('is_crossed', False)]
        if current_prices:
            best_current = current_prices[0]
            current_price = best_current['value']
            price_data['current_price'] = current_price
            price_data['best_price'] = current_price
            
            # Check if there's an original price higher than current (indicating sale)
            if price_data['original_price']:
                try:
                    curr_val = parse_price_value(current_price)
                    orig_val = parse_price_value(price_data['original_price'])
                    if curr_val and orig_val and orig_val > curr_val:
                        price_data['price_type'] = 'discounted'
                        discount = ((orig_val - curr_val) / orig_val) * 100
                        price_data['discount_percentage'] = round(discount, 1)
                    else:
                        price_data['price_type'] = 'regular'
                except:
                    price_data['price_type'] = 'regular'
            else:
                price_data['price_type'] = 'regular'
    
    # Final fallback: use any available price (even crossed-out if nothing else)
    if not price_data['best_price']:
        all_prices = []
        for price_type_list in extracted_prices.values():
            all_prices.extend(price_type_list)
        
        if all_prices:
            # Sort by confidence and prefer non-crossed prices
            all_prices.sort(key=lambda x: (not x.get('is_crossed', False), x.get('confidence', 0)), reverse=True)
            best_available = all_prices[0]
            price_data['best_price'] = best_available['value']
            price_data['current_price'] = best_available['value']
            price_data['price_type'] = 'regular' if not best_available.get('is_crossed', False) else 'uncertain'
    
    return price_data

def extract_price_from_html(html_content, url):
    """Legacy function - extract simple price from HTML content"""
    price_data = extract_price_with_type(html_content, url)
    return price_data['best_price'] if price_data else None
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Strategy 1: JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                price = extract_price_from_jsonld_data(data)
                if price:
                    return price
            except:
                continue
        
        # Strategy 2: Common price selectors
        price_selectors = [
            '.price', '.product-price', '.woocommerce-Price-amount', '.amount',
            '[itemprop="price"]', '[data-price]', '.price-current', '.sale-price',
            '.regular-price', '.product-price-value', '.price-box .price',
            '.price-range .price', '.product-price .price'
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if text and PRICE_RE.search(text):
                    match = PRICE_RE.search(text)
                    if match:
                        return match.group(0)
        
        # Strategy 3: Text pattern matching in entire HTML
        price_match = PRICE_RE.search(html_content)
        if price_match:
            return price_match.group(0)
            
        return None
        
    except Exception as e:
        print(f"Error extracting price from {url}: {str(e)}")
        return None

def extract_price_from_jsonld_data(data):
    """Extract price from JSON-LD structured data"""
    if isinstance(data, list):
        for item in data:
            price = extract_price_from_jsonld_data(item)
            if price:
                return price
    elif isinstance(data, dict):
        # Check if this object has @graph
        if "@graph" in data:
            return extract_price_from_jsonld_data(data["@graph"])
        
        # Check if this is a product/offer object
        if data.get("@type") in ("Product", "Offer", "AggregateOffer"):
            # Check offers
            if "offers" in data:
                offers = data["offers"]
                if isinstance(offers, list) and offers:
                    offers = offers[0]
                if isinstance(offers, dict) and "price" in offers:
                    return str(offers["price"])
            
            # Check direct price
            if "price" in data:
                return str(data["price"])
    
    return None

def fetch_url_content(url, timeout=30):
    """Fetch URL content with requests (more compatible with serverless)"""
    try:
        headers = {'User-Agent': UA}
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        raise Exception(f"Failed to fetch {url}: {str(e)}")

def extract_single_price(url):
    """Extract detailed price information from a single URL"""
    try:
        html_content = fetch_url_content(url)
        price_data = extract_price_with_type(html_content, url)
        
        # Handle case where price_data might be None
        if not price_data:
            price_data = {
                'current_price': None,
                'original_price': None,
                'sale_price': None,
                'price_type': 'error',
                'discount_percentage': None,
                'best_price': None
            }
        
        return {
            'url': url,
            'price': price_data.get('best_price'),
            'price_details': {
                'current_price': price_data.get('current_price'),
                'original_price': price_data.get('original_price'),
                'sale_price': price_data.get('sale_price'),
                'price_type': price_data.get('price_type', 'unknown'),
                'discount_percentage': price_data.get('discount_percentage')
            },
            'status': 'success' if price_data.get('best_price') else 'no_price_found'
        }
    except Exception as e:
        return {
            'url': url,
            'price': None,
            'price_details': {
                'current_price': None,
                'original_price': None,
                'sale_price': None,
                'price_type': 'error',
                'discount_percentage': None
            },
            'status': 'error',
            'error': str(e)
        }

@app.route('/api/extract', methods=['POST'])
def extract_prices():
    """Extract prices from multiple URLs"""
    try:
        data = request.json or {}
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'error': 'No URLs provided'}), 400
        
        # Limit URLs for serverless constraints
        if len(urls) > 10:
            return jsonify({'error': 'Maximum 10 URLs allowed per request'}), 400
        
        results = []
        
        # Process URLs with threading for better performance
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_url = {executor.submit(extract_single_price, url.strip()): url for url in urls if url.strip()}
            
            for future in concurrent.futures.as_completed(future_to_url, timeout=120):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    url = future_to_url[future]
                    results.append({
                        'url': url,
                        'price': None,
                        'status': 'error',
                        'error': str(e)
                    })
        
        return jsonify({
            'results': results,
            'total': len(results),
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'error'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare-csv', methods=['POST'])
def compare_csv_prices():
    """Process CSV file and compare prices with competitors"""
    try:
        # Check if request has file
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '' or file.filename is None:
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'File must be a CSV'}), 400
        
        # Read and parse CSV content
        try:
            csv_content = file.read().decode('utf-8')
            products = parse_csv_content(csv_content)
        except Exception as e:
            return jsonify({'error': f'Error reading CSV: {str(e)}'}), 400
        
        if not products:
            return jsonify({'error': 'No valid products found in CSV. Expected columns: product_name, our_price, and competitor URLs'}), 400
        
        # No product limit for local deployment
        
        # Process each product
        results = []
        for product in products:
            try:
                result = process_product_comparison(product)
                results.append(result)
            except Exception as e:
                results.append({
                    'product_name': product.get('product_name', 'Unknown'),
                    'our_price': product.get('our_price', 'Unknown'),
                    'competitor_results': [],
                    'summary': {},
                    'status': 'error',
                    'error': str(e)
                })
        
        # Generate overall summary
        successful_products = [r for r in results if r['status'] == 'success']
        total_competitive = len([r for r in successful_products 
                               if r['summary'].get('overall_recommendation') == 'competitive'])
        
        overall_summary = {
            'total_products': len(products),
            'successful_comparisons': len(successful_products),
            'competitive_products': total_competitive,
            'needs_adjustment': len(successful_products) - total_competitive,
            'overall_status': 'good' if total_competitive >= len(successful_products) / 2 else 'needs_review'
        }
        
        return jsonify({
            'results': results,
            'summary': overall_summary,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Serve the CSV upload interface"""
    return render_template('csv_upload.html')

@app.route('/csv-upload')
def csv_upload_page():
    """Serve the CSV upload interface"""
    return render_template('csv_upload.html')

# Vercel handler
def handler(request):
    def start_response(status, headers, exc_info=None):
        # This function should return a write callable, but for Vercel
        # we can return a simple function that handles bytes
        def write(data):
            return data
        return write
    
    # Get the WSGI response
    response = app(request.environ, start_response)
    
    # If response is an iterable, join it into a single response
    if hasattr(response, '__iter__'):
        return b''.join(response)
    return response

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
from flask import Flask, render_template, request, jsonify
import asyncio
import json
import threading
import time
import csv
import io
import re
from concurrent.futures import ThreadPoolExecutor
from price_extractor import get_price

app = Flask(__name__)

# Store extraction results temporarily
extraction_results = {}
extraction_status = {}

# Price comparison functions
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
    products = []
    
    try:
        # Create a StringIO object to read the CSV content
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            product = {
                'product_name': row.get('product_name', '').strip(),
                'our_price': row.get('our_price', '').strip()
            }
            
            # Find competitor URL columns
            competitor_urls = []
            for key, value in row.items():
                if ('competitor' in key.lower() or 'url' in key.lower()) and value.strip():
                    competitor_urls.append(value.strip())
            
            product['competitor_urls'] = competitor_urls
            
            # Only add if we have product name and our price
            if product['product_name'] and product['our_price']:
                products.append(product)
    
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return []
    
    return products

async def process_product_comparison(product):
    """Process a single product comparison"""
    product_name = product['product_name']
    our_price = product['our_price']
    competitor_urls = product['competitor_urls']
    
    competitor_results = []
    
    # Extract prices from competitor URLs
    for url in competitor_urls:
        try:
            price = await get_price(url)
            if price:
                comparison = compare_prices(our_price, price)
                details = format_comparison_result(comparison, our_price, price)
                
                competitor_results.append({
                    'url': url,
                    'price': price,
                    'comparison': comparison,
                    'details': details,
                    'status': 'success'
                })
            else:
                competitor_results.append({
                    'url': url,
                    'price': None,
                    'comparison': 'unknown',
                    'details': {
                        'status': 'no_price_found',
                        'message': 'No price found on this page',
                        'difference': 'N/A',
                        'recommendation': 'Check if URL is correct'
                    },
                    'status': 'no_price_found'
                })
        except Exception as e:
            competitor_results.append({
                'url': url,
                'price': None,
                'comparison': 'unknown',
                'details': {
                    'status': 'error',
                    'message': f'Error extracting price: {str(e)}',
                    'difference': 'N/A',
                    'recommendation': 'Check URL accessibility'
                },
                'status': 'error'
            })
    
    # Generate product summary
    successful_extractions = len([r for r in competitor_results if r['status'] == 'success'])
    lower_count = len([r for r in competitor_results if r['comparison'] == 'lower'])
    higher_count = len([r for r in competitor_results if r['comparison'] == 'higher'])
    equal_count = len([r for r in competitor_results if r['comparison'] == 'equal'])
    
    if lower_count > higher_count:
        overall_recommendation = 'competitive'
    elif higher_count > lower_count:
        overall_recommendation = 'consider_adjustment'
    else:
        overall_recommendation = 'monitor'
    
    summary = {
        'total_competitors': len(competitor_urls),
        'successful_extractions': successful_extractions,
        'lower_than_competitors': lower_count,
        'higher_than_competitors': higher_count,
        'equal_to_competitors': equal_count,
        'overall_recommendation': overall_recommendation
    }
    
    return {
        'product_name': product_name,
        'our_price': our_price,
        'competitor_results': competitor_results,
        'summary': summary,
        'status': 'success'
    }

def run_async_extraction(urls, session_id):
    """Run price extraction for multiple URLs asynchronously"""
    async def extract_all_prices():
        results = []
        for i, url in enumerate(urls):
            extraction_status[session_id] = {
                'current': i + 1,
                'total': len(urls),
                'url': url,
                'status': 'processing'
            }
            
            try:
                price = await get_price(url.strip())
                result = {
                    'url': url,
                    'price': price,
                    'status': 'success' if price else 'no_price_found'
                }
            except Exception as e:
                result = {
                    'url': url,
                    'price': None,
                    'status': 'error',
                    'error': str(e)
                }
            
            results.append(result)
        
        extraction_results[session_id] = results
        extraction_status[session_id] = {
            'current': len(urls),
            'total': len(urls),
            'status': 'completed'
        }
        
        return results
    
    # Run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(extract_all_prices())
    finally:
        loop.close()

@app.route('/')
def index():
    """Main page with the price extraction interface"""
    return render_template('index.html')

@app.route('/csv-upload')
def csv_upload_page():
    """CSV upload page for competitive analysis"""
    return render_template('csv_upload.html')

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
        
        # Process each product
        results = []
        for product in products:
            try:
                # Run the async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(process_product_comparison(product))
                    results.append(result)
                finally:
                    loop.close()
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

@app.route('/extract', methods=['POST'])
def extract_prices():
    """Start price extraction for multiple URLs"""
    data = request.json or {}
    urls = data.get('urls', [])
    
    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400
    
    # Generate session ID
    session_id = str(int(time.time() * 1000))
    
    # Initialize status
    extraction_status[session_id] = {
        'current': 0,
        'total': len(urls),
        'status': 'starting'
    }
    
    # Start extraction in background thread
    def start_extraction():
        run_async_extraction(urls, session_id)
    
    thread = threading.Thread(target=start_extraction)
    thread.start()
    
    return jsonify({'session_id': session_id})

@app.route('/status/<session_id>')
def get_status(session_id):
    """Get current extraction status"""
    status = extraction_status.get(session_id, {'status': 'not_found'})
    return jsonify(status)

@app.route('/results/<session_id>')
def get_results(session_id):
    """Get extraction results"""
    results = extraction_results.get(session_id, [])
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
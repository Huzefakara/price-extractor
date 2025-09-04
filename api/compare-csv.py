from http.server import BaseHTTPRequestHandler
import json
import cgi
import io
import csv
from urllib.parse import parse_qs

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' not in content_type:
                self.send_error_response({'error': 'Expected multipart/form-data'}, 400)
                return
            
            # Read the content
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse the multipart data
            boundary = content_type.split('boundary=')[1].encode()
            parts = post_data.split(b'--' + boundary)
            
            csv_content = None
            for part in parts:
                if b'filename=' in part and b'.csv' in part:
                    # Extract CSV content
                    content_start = part.find(b'\r\n\r\n') + 4
                    if content_start > 3:
                        csv_content = part[content_start:].decode('utf-8').strip()
                        break
            
            if not csv_content:
                self.send_error_response({'error': 'No CSV file found in upload'}, 400)
                return
            
            # Parse CSV and create sample analysis
            products = self.parse_csv_content(csv_content)
            
            if not products:
                self.send_error_response({
                    'error': 'No valid products found in CSV',
                    'note': 'Expected columns: product_name, our_price, and competitor URLs'
                }, 400)
                return
            
            # Create demo results
            results = []
            for product in products:
                competitor_results = []
                for url in product.get('competitor_urls', []):
                    competitor_results.append({
                        'url': url,
                        'price': '£99.99',  # Demo price
                        'comparison': 'lower',
                        'details': {
                            'status': 'demo',
                            'message': 'Demo mode - showing sample results',
                            'recommendation': 'This is a demonstration of the CSV processing feature'
                        },
                        'status': 'success'
                    })
                
                results.append({
                    'product_name': product['product_name'],
                    'our_price': product['our_price'],
                    'competitor_results': competitor_results,
                    'summary': {
                        'total_competitors': len(product.get('competitor_urls', [])),
                        'successful_extractions': len(competitor_results),
                        'lower_than_competitors': 1,
                        'higher_than_competitors': 0,
                        'equal_to_competitors': 0,
                        'overall_recommendation': 'demo_mode'
                    },
                    'status': 'success'
                })
            
            response_data = {
                'results': results,
                'summary': {
                    'total_products': len(products),
                    'successful_comparisons': len(results),
                    'competitive_products': len(results),
                    'needs_adjustment': 0,
                    'overall_status': 'demo_mode'
                },
                'status': 'success',
                'note': 'This is a demo showing CSV processing. Real price extraction would happen here.'
            }
            
            self.send_success_response(response_data)
            
        except Exception as e:
            error_response = {
                'error': str(e),
                'message': 'Failed to process CSV request',
                'debug': f'Content-Type: {self.headers.get("Content-Type", "none")}'
            }
            self.send_error_response(error_response, 500)
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def parse_csv_content(self, csv_content):
        """Parse CSV content and extract product data"""
        products = []
        
        try:
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
    
    def send_success_response(self, data):
        response = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(response.encode())
    
    def send_error_response(self, error_data, status_code):
        response = json.dumps(error_data)
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response.encode())

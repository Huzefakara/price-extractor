from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            response_data = {
                'message': 'CSV comparison endpoint working',
                'status': 'success',
                'note': 'CSV processing temporarily simplified for testing'
            }
            
            # Send success response
            response = json.dumps(response_data)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(response.encode())
            
        except Exception as e:
            error_response = {
                'error': str(e),
                'message': 'Failed to process CSV request'
            }
            
            response = json.dumps(error_response)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.encode())

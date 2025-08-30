try:
    from flask import Flask, render_template_string, request, redirect, url_for
    import os
except ImportError as e:
    # Fallback for import issues
    print(f"Import error: {e}")
    
    class MockFlask:
        def __init__(self, *args, **kwargs):
            pass
        def route(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
    
    Flask = MockFlask
    render_template_string = lambda x: x
    request = None
    redirect = lambda x: x
    url_for = lambda x: x
    os = type('os', (), {'path': type('path', (), {'dirname': lambda x: '.', 'abspath': lambda x: x, 'join': lambda *x: '/'.join(x)})()})()

app = Flask(__name__)

# Get current directory and set up template paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
template_dir = os.path.join(project_root, 'templates')

@app.route('/')
def index():
    try:
        return render_template_string(get_index_template())
    except Exception as e:
        return f'<h1>Price Extractor Machine</h1><p>Error loading template: {str(e)}</p>'

@app.route('/csv-upload')
def csv_upload():
    try:
        return render_template_string(get_csv_template())
    except Exception as e:
        return f'<h1>CSV Upload Error</h1><p>Error loading template: {str(e)}</p>'

def get_index_template():
    return '''<!DOCTYPE html>
<html><head><title>Price Extractor</title></head>
<body><h1>Price Extractor Machine</h1>
<nav><a href="/">URL Extraction</a> | <a href="/csv-upload">CSV Upload</a></nav>
<p>URL-based price extraction interface here.</p>
<p>Use /api/extract for API access.</p></body></html>'''

def get_csv_template():
    return '''<!DOCTYPE html>
<html><head><title>CSV Upload - Price Extractor</title></head>
<body><h1>CSV Price Comparison</h1>
<nav><a href="/">URL Extraction</a> | <a href="/csv-upload">CSV Upload</a></nav>
<p>CSV upload interface here.</p>
<p>Use /api/compare-csv for API access.</p></body></html>'''

# Vercel handler - simple approach for Flask
def handler(event, context=None):
    """Vercel serverless function entry point"""
    try:
        # For Vercel, we need to create a test client
        with app.test_client() as client:
            # Extract method and path from event
            method = getattr(event, 'method', 'GET')
            path = getattr(event, 'path', '/')
            
            # Handle different path formats
            if path.startswith('/api/index'):
                path = path.replace('/api/index', '')
            if not path:
                path = '/'
                
            # Make request to Flask app
            if method == 'GET':
                response = client.get(path)
            elif method == 'POST':
                response = client.post(path, data=getattr(event, 'body', ''))
            else:
                response = client.open(path=path, method=method)
            
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Price Extractor Machine</h1><p>Service temporarily unavailable. Error: {str(e)}</p>'
        }
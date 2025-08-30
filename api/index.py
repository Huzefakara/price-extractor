from flask import Flask, render_template_string, request, redirect, url_for
import os

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

# Vercel handler
def handler(event, context):
    try:
        from werkzeug.wrappers import Request, Response
        from werkzeug.serving import WSGIRequestHandler
        import io
        
        # Create a proper WSGI environment
        if hasattr(event, 'environ'):
            environ = event.environ
        else:
            # Fallback for different event formats
            environ = {
                'REQUEST_METHOD': getattr(event, 'method', 'GET'),
                'PATH_INFO': getattr(event, 'path', '/'),
                'QUERY_STRING': getattr(event, 'query', ''),
                'CONTENT_TYPE': '',
                'CONTENT_LENGTH': '',
                'SERVER_NAME': 'localhost',
                'SERVER_PORT': '80',
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'https',
                'wsgi.input': io.StringIO(''),
                'wsgi.errors': io.StringIO(),
                'wsgi.multithread': False,
                'wsgi.multiprocess': True,
                'wsgi.run_once': False
            }
        
        response_data = []
        status_info = []
        headers_info = []
        
        def start_response(status, headers, exc_info=None):
            status_info.append(status)
            headers_info.extend(headers)
            return response_data.append
        
        # Get response from Flask app
        app_response = app(environ, start_response)
        
        # Collect response data
        if hasattr(app_response, '__iter__'):
            for data in app_response:
                if data:
                    response_data.append(data)
        
        # Join response data
        if response_data:
            body = b''.join(response_data) if isinstance(response_data[0], bytes) else ''.join(response_data)
        else:
            body = ''
        
        return {
            'statusCode': int(status_info[0].split()[0]) if status_info else 200,
            'headers': dict(headers_info) if headers_info else {'Content-Type': 'text/html'},
            'body': body
        }
        
    except Exception as e:
        # Fallback error response
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Server Error</h1><p>Error: {str(e)}</p>'
        }
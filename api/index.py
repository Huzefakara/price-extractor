from flask import Flask, render_template_string, request, redirect, url_for
import os

app = Flask(__name__)

# Get current directory and set up template paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
template_dir = os.path.join(project_root, 'templates')

@app.route('/')
def index():
    return render_template_string(get_index_template())

@app.route('/csv-upload')
def csv_upload():
    return render_template_string(get_csv_template())

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
def handler(request):
    def start_response(status, headers, exc_info=None):
        def write(data):
            return data
        return write
    
    response = app(request.environ, start_response)
    return response
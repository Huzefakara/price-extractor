from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Route handling based on path
        path = self.path
        
        if path.startswith('/csv-upload') or path == '/csv-upload':
            # CSV upload page
            html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>CSV Upload - Price Extractor</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        nav { text-align: center; margin: 20px 0; }
        nav a { margin: 0 10px; padding: 10px 20px; text-decoration: none; background: #007bff; color: white; border-radius: 4px; }
        nav a:hover { background: #0056b3; }
        .upload-area { border: 2px dashed #ddd; padding: 40px; text-align: center; margin: 20px 0; border-radius: 8px; }
        .upload-area:hover { border-color: #007bff; }
        input[type="file"] { margin: 10px 0; }
        button { background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #218838; }
        .status { margin-top: 20px; padding: 10px; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>CSV Price Comparison</h1>
        <nav>
            <a href="/">URL Extraction</a>
            <a href="/csv-upload">CSV Upload</a>
        </nav>
        
        <div class="upload-area">
            <h3>Upload CSV File for Price Comparison</h3>
            <p>Upload a CSV file with product information and competitor URLs</p>
            <input type="file" id="csvFile" accept=".csv" />
            <br>
            <button onclick="uploadCSV()">Process CSV</button>
        </div>
        
        <div id="status"></div>
        <div id="results"></div>
    </div>
    
    <script>
        function uploadCSV() {
            const fileInput = document.getElementById('csvFile');
            const statusDiv = document.getElementById('status');
            const resultsDiv = document.getElementById('results');
            
            if (!fileInput.files[0]) {
                statusDiv.innerHTML = '<div class="error">Please select a CSV file</div>';
                return;
            }
            
            statusDiv.innerHTML = '<div class="status">Processing CSV file...</div>';
            resultsDiv.innerHTML = '';
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            fetch('/api/compare-csv', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    statusDiv.innerHTML = '<div class="error">Error: ' + data.error + '</div>';
                } else {
                    statusDiv.innerHTML = '<div class="success">CSV processed successfully!</div>';
                    resultsDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                }
            })
            .catch(error => {
                statusDiv.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
            });
        }
    </script>
</body>
</html>'''
        else:
            # Main page (URL extraction)
            html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Price Extractor</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        nav { text-align: center; margin: 20px 0; }
        nav a { margin: 0 10px; padding: 10px 20px; text-decoration: none; background: #007bff; color: white; border-radius: 4px; }
        nav a:hover { background: #0056b3; }
        .input-section { margin: 20px 0; }
        textarea { width: 100%; height: 120px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; resize: vertical; }
        button { background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 10px 5px; }
        button:hover { background: #218838; }
        .status { margin-top: 20px; padding: 10px; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .results { margin-top: 20px; }
        .result-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #007bff; }
        .price { font-weight: bold; color: #28a745; font-size: 1.2em; }
        .url { color: #666; font-size: 0.9em; word-break: break-all; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Price Extractor Machine</h1>
        <nav>
            <a href="/">URL Extraction</a>
            <a href="/csv-upload">CSV Upload</a>
        </nav>
        
        <div class="input-section">
            <h3>Extract Prices from URLs</h3>
            <p>Enter one URL per line to extract prices:</p>
            <textarea id="urlInput" placeholder="Enter URLs here, one per line...\nhttps://example.com/product1\nhttps://example.com/product2"></textarea>
            <br>
            <button onclick="extractPrices()">Extract Prices</button>
            <button onclick="clearResults()">Clear Results</button>
        </div>
        
        <div id="status"></div>
        <div id="results"></div>
    </div>
    
    <script>
        function extractPrices() {
            const urlInput = document.getElementById('urlInput');
            const statusDiv = document.getElementById('status');
            const resultsDiv = document.getElementById('results');
            
            const urls = urlInput.value.split('\\n').filter(url => url.trim());
            
            if (urls.length === 0) {
                statusDiv.innerHTML = '<div class="error">Please enter at least one URL</div>';
                return;
            }
            
            statusDiv.innerHTML = '<div class="status">Extracting prices...</div>';
            resultsDiv.innerHTML = '';
            
            fetch('/api/extract', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ urls: urls })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    statusDiv.innerHTML = '<div class="error">Error: ' + data.error + '</div>';
                } else {
                    statusDiv.innerHTML = '<div class="success">Extraction completed! ' + 
                        data.successful + ' successful, ' + data.failed + ' failed</div>';
                    
                    let resultsHTML = '<div class="results"><h3>Results:</h3>';
                    data.results.forEach(result => {
                        resultsHTML += '<div class="result-item">';
                        resultsHTML += '<div class="url">' + result.url + '</div>';
                        if (result.price) {
                            resultsHTML += '<div class="price">Price: ' + result.price + '</div>';
                        } else {
                            resultsHTML += '<div class="error">No price found</div>';
                        }
                        if (result.message) {
                            resultsHTML += '<div>' + result.message + '</div>';
                        }
                        resultsHTML += '</div>';
                    });
                    resultsHTML += '</div>';
                    resultsDiv.innerHTML = resultsHTML;
                }
            })
            .catch(error => {
                statusDiv.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
            });
        }
        
        function clearResults() {
            document.getElementById('urlInput').value = '';
            document.getElementById('status').innerHTML = '';
            document.getElementById('results').innerHTML = '';
        }
    </script>
</body>
</html>'''
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Access-Control-Allow-Origin': '*'
            },
            'body': html_content
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'path': str(request)
            })
        }
from flask import Flask, render_template_string
import os

app = Flask(__name__)

# Read the HTML template
def get_html_template():
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'index.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback inline template for Vercel
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Price Extractor Machine</title>
    <link rel="stylesheet" href="/static/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="header-content">
                <div class="logo">
                    <i class="fas fa-dollar-sign"></i>
                    <h1>Price Extractor Machine</h1>
                </div>
                <p class="subtitle">Extract prices from multiple e-commerce websites instantly</p>
            </div>
        </header>

        <main class="main-content">
            <div class="input-section">
                <div class="input-header">
                    <h2><i class="fas fa-link"></i> Enter Product URLs</h2>
                    <p>Add multiple URLs (one per line) to extract prices from various websites</p>
                </div>
                
                <div class="url-input-container">
                    <textarea id="urlInput" placeholder="https://example.com/product1&#10;https://example.com/product2&#10;https://example.com/product3&#10;..."></textarea>
                    <div class="input-actions">
                        <div class="url-count">
                            <span id="urlCount">0</span> URLs entered
                        </div>
                        <button id="extractBtn" class="btn-primary">
                            <i class="fas fa-search"></i>
                            Extract Prices
                        </button>
                    </div>
                </div>
            </div>

            <div id="progressSection" class="progress-section" style="display: none;">
                <div class="progress-header">
                    <h3><i class="fas fa-cog fa-spin"></i> Extracting Prices...</h3>
                    <span id="progressText">Processing URLs...</span>
                </div>
                <div class="progress-bar">
                    <div id="progressFill" class="progress-fill"></div>
                </div>
            </div>

            <div id="resultsSection" class="results-section" style="display: none;">
                <div class="results-header">
                    <h3><i class="fas fa-chart-line"></i> Extraction Results</h3>
                    <div class="results-summary">
                        <span id="successCount" class="success">0 successful</span>
                        <span id="failedCount" class="failed">0 failed</span>
                    </div>
                </div>
                
                <div class="results-actions">
                    <button id="exportBtn" class="btn-secondary">
                        <i class="fas fa-download"></i>
                        Export Results
                    </button>
                    <button id="clearBtn" class="btn-secondary">
                        <i class="fas fa-trash"></i>
                        Clear Results
                    </button>
                </div>

                <div id="resultsContainer" class="results-container">
                    <!-- Results will be populated here -->
                </div>
            </div>
        </main>
    </div>

    <div id="loadingOverlay" class="loading-overlay" style="display: none;">
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Processing extraction...</p>
        </div>
    </div>

    <script src="/static/script.js"></script>
</body>
</html>"""

@app.route('/')
def index():
    return get_html_template()

# Vercel handler
def handler(request):
    def start_response(status, headers, exc_info=None):
        # Return a write function as required by WSGI
        def write(data):
            return data
        return write
    
    # Get the response from Flask app
    response = app(request.environ, start_response)
    return response
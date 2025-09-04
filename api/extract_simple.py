from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/extract', methods=['POST'])
def extract_prices():
    """Simple price extraction endpoint"""
    try:
        data = request.get_json() or {}
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'error': 'No URLs provided'}), 400
        
        # Simple response for testing
        results = []
        for url in urls[:5]:  # Limit for testing
            results.append({
                'url': url,
                'price': '£99.99',  # Dummy price for testing
                'status': 'success'
            })
        
        return jsonify({
            'results': results,
            'total': len(results),
            'successful': len(results),
            'failed': 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare-csv', methods=['POST'])
def compare_csv_prices():
    """Simple CSV comparison endpoint"""
    try:
        return jsonify({
            'message': 'CSV comparison temporarily simplified for testing',
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
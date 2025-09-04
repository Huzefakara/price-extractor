import json
import traceback

def handler(request):
    """Vercel serverless function handler for CSV price comparison"""
    try:
        # Handle different request formats
        if hasattr(request, 'get_json'):
            try:
                data = request.get_json() or {}
            except:
                data = {}
        elif hasattr(request, 'json'):
            try:
                data = request.json or {}
            except:
                data = {}
        else:
            data = request if isinstance(request, dict) else {}
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'message': 'CSV comparison endpoint working',
                'status': 'success',
                'note': 'CSV processing temporarily simplified for testing',
                'received_data_keys': list(data.keys()) if data else []
            })
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
                'traceback': traceback.format_exc()
            })
        }
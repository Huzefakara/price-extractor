import json
import traceback

def handler(event, context=None):
    """Vercel serverless function handler for CSV price comparison"""
    try:
        # Handle different event formats
        if isinstance(event, dict):
            if 'body' in event:
                if isinstance(event['body'], str):
                    try:
                        data = json.loads(event['body'])
                    except:
                        data = {}
                else:
                    data = event['body'] or {}
            else:
                data = event
        else:
            data = {}
        
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
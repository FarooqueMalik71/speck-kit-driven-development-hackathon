import os
import json

def handler(request):
    """Vercel API route handler for query endpoint"""
    # Handle CORS preflight request
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            },
            "body": ""
        }

    # Only process POST requests
    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": "Method not allowed"})
        }

    try:
        # Parse the request body
        import json as json_lib
        body = json_lib.loads(request.body.decode('utf-8')) if request.body else {}
        query = body.get('query', '')
        context_ids = body.get('context_ids', [])
        mode = body.get('mode', 'full_book')

        if not query:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"error": "Query is required"})
            }

        # For now, return a mock response since the full backend isn't available in serverless environment
        # In a real implementation, you'd want to use a different approach for serverless deployment
        response_body = {
            "answer": f"Thank you for your query: '{query}'. This is a response from the AI Textbook Assistant. In a full implementation, this would connect to your RAG system.",
            "citations": ["Sample Citation 1", "Sample Citation 2"],
            "confidence": 0.8,
            "is_confident": True,
            "sources": ["textbook_chapter_1", "textbook_chapter_2"],
            "boundary_compliance": 0.9,
            "needs_fact_check": False,
            "session_id": body.get('session_id') or "mock_session_id"
        }

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps(response_body)
        }

    except json_lib.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"detail": f"Error processing query: {str(e)}"})
        }

# Export the handler for Vercel
def main(request):
    return handler(request)
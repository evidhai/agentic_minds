import requests
import sys
import json

def test_lambda(url):
    print(f"🚀 Testing Lambda URL: {url}")
    
    payload = {
        "input": "Hello, are you healthy?",
        "user_id": "test-user"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! Response:")
            print(json.dumps(response.json() if response.headers.get('content-type') == 'application/json' else response.text, indent=2))
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during request: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_lambda.py <LAMBDA_FUNCTION_URL>")
        sys.exit(1)
    
    test_lambda(sys.argv[1])

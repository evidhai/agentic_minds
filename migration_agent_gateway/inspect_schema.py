import boto3
import json
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True), override=True)

GATEWAY_ID = "migrationagentgateway-iam-pmhzbvvlq4" # Current ID

def inspect_targets():
    client = boto3.client('bedrock-agentcore-control', region_name="us-east-1")
    
    resp = client.list_gateway_targets(gatewayIdentifier=GATEWAY_ID)
    for item in resp.get('items', []):
        t_id = item['targetId']
        print(f"Target ID: {t_id}")
        
        detail = client.get_gateway_target(gatewayIdentifier=GATEWAY_ID, targetId=t_id)
        config = detail['targetConfiguration']
        
        print(json.dumps(config, indent=2))

if __name__ == "__main__":
    inspect_targets()

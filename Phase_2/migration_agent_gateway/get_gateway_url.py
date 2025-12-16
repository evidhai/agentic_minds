import boto3
from datetime import datetime
import os
import sys

def get_latest_gateway_url():
    client = boto3.client('bedrock-agentcore-control', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
    
    try:
        paginator = client.get_paginator('list_gateways')
        candidates = []
        
        for page in paginator.paginate():
            # Support both key variations just in case
            gateways = page.get('gatewaySummaries') or page.get('gateways') or []
            for gw in gateways:
                print(f"DEBUG: Checking {gw['name']}", file=sys.stderr)
                # Case insensitive match
                if 'migrationagent-test-gateway' in gw['name'].lower():
                    candidates.append(gw)

        
        # import sys
        # print(f"DEBUG: Found {len(candidates)} candidates", file=sys.stderr)

        
        if not candidates:
            return None
            
        # Sort by creation time (descending)
        # Note: 'createdAt' is a datetime object
        candidates.sort(key=lambda x: x['createdAt'], reverse=True)
        
        latest_gw = candidates[0]
        gw_id = latest_gw['gatewayId']
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        
        # Construct standard URL format
        return f"https://{gw_id}.gateway.{region}.amazonaws.com"
        
    except Exception as e:
        # Fallback if list fails (e.g. permissions)
        return ""

if __name__ == "__main__":
    url = get_latest_gateway_url()
    if url:
        print(url)
    else:
        print("")

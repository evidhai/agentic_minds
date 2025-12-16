import boto3
import json
import os
import shutil
import time
from zipfile import ZipFile

import gateway_infra_utils as utils
# We also need the auth utils from the sample if we want to set up Cognito easily.
# For now, we will assume we can import or copy them. 
# To make this script robust, I will INCLUDE the necessary authentication setup logic inline 
# or import it if the user has the 'agentcore_samples' in pythonpath.

import random
import string

# Configuration
REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

# Dynamic App Naming
# Defaults to 'MigrationAgent-Test' if not set via env var
APP_NAME = os.environ.get('APP_NAME', 'MigrationAgent-Test')

# Add random suffix to avoid conflicts during rapid POC testing
RAND_SUFFIX = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
GATEWAY_NAME = f"{APP_NAME}-Gateway-{RAND_SUFFIX}"
LAMBDA_FUNC_NAME = f"{APP_NAME}-Tools" # Keep Lambda stable as it updates fine
LAMBDA_ROLE_NAME = f"{APP_NAME}-LambdaRole"
GATEWAY_ROLE_NAME = f"{APP_NAME}-GatewayRole"
USER_POOL_NAME = f"{APP_NAME}-Pool"

def main():
    print(f"Starting deployment of {GATEWAY_NAME} in {REGION}...")
    
    # 1. Package Lambda Code
    print("\nPackaging Lambda Code...")
    zip_filename = "gateway_tools_lambda.zip"
    with ZipFile(zip_filename, 'w') as z:
        z.write("gateway_tools_lambda.py")
    
    # 2. Create/Get Lambda IAM Role
    print("\nConfiguring Lambda IAM Role...")
    lambda_role_arn = utils.create_lambda_role(LAMBDA_ROLE_NAME)
    
    # 3. Deploy Lambda Function
    print("\nDeploying Lambda Function...")
    lambda_arn = utils.create_lambda_function(
        LAMBDA_FUNC_NAME, 
        lambda_role_arn, 
        zip_filename
    )
    print(f"   Function ARN: {lambda_arn}")

    # 4. Create Gateway IAM Role
    print("\nConfiguring Gateway IAM Role...")
    gateway_role_arn = utils.create_gateway_role(GATEWAY_ROLE_NAME, REGION)
    
    # 5. Setup Cognito Auth
    print("\nSetting up Cognito Authentication...")
    # Dynamic Pool Name from configuration above
    auth_config = utils.setup_cognito_full(
        pool_name=USER_POOL_NAME, 
        client_name="GateClient",
        resource_id="https://migration-gateway",
        region=REGION
    )
    
    print(f"   - User Pool ID: {auth_config['user_pool_id']}")
    print(f"   - Client ID:    {auth_config['client_id']}")
    
    # 6. Create Gateway with Auth
    # Need to update utils.create_gateway to accept authorizer config or call client directly here.
    # To keep it simple, we'll update the call to use Boto3 directly here OR update utils. 
    # Let's update the Logic here to call create_gateway with auth.
    
    client = boto3.client('bedrock-agentcore-control', region_name=REGION)
    print("\nCreating AgentCore Gateway (Secured)...")
    
    try:
        response = client.create_gateway(
            name=GATEWAY_NAME,
            description="Migration Agent Gateway",
            protocolType='MCP',
            roleArn=gateway_role_arn,
            authorizerType='CUSTOM_JWT',
            authorizerConfiguration={
                "customJWTAuthorizer": {
                    "discoveryUrl": auth_config['discovery_url'],
                    "allowedAudience": [auth_config['client_id']]
                }
            }
        )

        gateway_id = response['gatewayId']
        print(f"   Gateway Created: {gateway_id}")
        
        # Save Token Info for the Agent to use
        with open("gateway_auth.json", "w") as f:
            json.dump(auth_config, f, indent=2)
            
    except Exception as e:
        if "ConflictException" in str(e):
             print(f"Gateway {GATEWAY_NAME} likely exists. Attempting to retrieve ID...")
             # List gateways and find by name
             paginator = client.get_paginator('list_gateways')
             found = False
             for page in paginator.paginate():
                 print(f"DEBUG PAGE: {page}")
                 # Try common keys
                 summaries = page.get('gatewaySummaries') or page.get('gateways') or []
                 for gw in summaries:
                     if gw['name'] == GATEWAY_NAME:
                         gateway_id = gw['gatewayId']
                         print(f"   Found Existing Gateway ID: {gateway_id}")
                         found = True
                         break
                 if found: break
             
             if not found:
                 print("Error: Gateway exists but could not find ID in list.")
                 raise e
        else:
            raise e


    
    tools_schema = [
        {
            "name": "cost_assistant",
            "description": "An AWS Cost Optimization Assistant that helps users understand AWS service pricing.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "payload": {"type": "string", "description": "Query about AWS pricing"}
                }
            }
        },
        {
            "name": "aws_docs_assistant",
            "description": "An AWS Documentation Assistant that helps users understand AWS services.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "payload": {"type": "string", "description": "Search query for AWS documentation"}
                }
            }
        },
        {
            "name": "vpc_subnet_calculator",
            "description": "Calculates optimized VPC subnet ranges for a given CIDR block.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cidr": {"type": "string", "description": "VPC CIDR (e.g. 10.0.0.0/16)"},
                    "az_count": {"type": "integer", "description": "Number of AZs (default 2)"},
                    "tiers": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "List of tier names"
                    }
                },
                "required": ["cidr"]
            }
        }
    ]
    
    print("\nGenerated Tool Schema for Gateway Config:")
    print(json.dumps(tools_schema, indent=2))
    
    # WAIT FOR GATEWAY TO BE ACTIVE
    print("\nWaiting for Gateway to be READY...")
    while True:
        try:
            gw_desc = client.get_gateway(gatewayIdentifier=gateway_id)
            # Check response structure - often 'gateway' key wraps the object or it is at root if using specific client
            # Based on list_gateways experience, let's print debug if needed, but usually get_gateway returns dict
            status = gw_desc.get('gateway', {}).get('status') or gw_desc.get('status')
            print(f"   Status: {status}")
            if status == 'READY' or status == 'ACTIVE':
                break
            if status == 'FAILED':
                raise Exception("Gateway creation FAILED.")
        except Exception as e:
            print(f"   Polling error: {e}")
            
        time.sleep(5)
    
    # Create the Gateway Target Mapping
    print("\nMapping Gateway to Lambda Functions...")
    
    # We pass the schema we generated above
    target_id = utils.create_gateway_target(
        gateway_id=gateway_id,
        lambda_arn=lambda_arn,
        tool_schema=tools_schema,
        region=REGION
    )

    print("\nDeployment Complete!")
    print(f"   - Gateway ID:   {gateway_id}")
    print(f"   - Lambda ARN:   {lambda_arn}")
    print(f"   - Target ID:    {target_id}")

    # Write Gateway ID to file for other scripts to use
    with open("gateway_id.txt", "w") as f:
        f.write(gateway_id)
    print(f"   Saved ID to gateway_id.txt")
    print("\nYou can now run 'python migration_agent.py' to start the agent.")


if __name__ == "__main__":
    main()

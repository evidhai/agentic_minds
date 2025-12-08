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

# Configuration
REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
GATEWAY_NAME = "MigrationAgentGateway"
LAMBDA_FUNC_NAME = "MigrationAgentTools"
LAMBDA_ROLE_NAME = "MigrationAgentLambdaRole"
GATEWAY_ROLE_NAME = "MigrationAgentGatewayRole"

def main():
    print(f"🚀 Starting deployment of {GATEWAY_NAME} in {REGION}...")
    
    # 1. Package Lambda Code
    print("\n📦 Packaging Lambda Code...")
    zip_filename = "gateway_tools_lambda.zip"
    with ZipFile(zip_filename, 'w') as z:
        z.write("gateway_tools_lambda.py")
    
    # 2. Create/Get Lambda IAM Role
    print("\n🛡️ Configuring Lambda IAM Role...")
    lambda_role_arn = utils.create_lambda_role(LAMBDA_ROLE_NAME)
    
    # 3. Deploy Lambda Function
    print("\n⚡ Deploying Lambda Function...")
    lambda_arn = utils.create_lambda_function(
        LAMBDA_FUNC_NAME, 
        lambda_role_arn, 
        zip_filename
    )
    print(f"   Function ARN: {lambda_arn}")

    # 4. Create Gateway IAM Role
    print("\n🛡️ Configuring Gateway IAM Role...")
    gateway_role_arn = utils.create_gateway_role(GATEWAY_ROLE_NAME, REGION)
    
    # 5. Setup Cognito Auth
    print("\n🔐 Setting up Cognito Authentication...")
    auth_config = utils.setup_cognito_full(
        pool_name="MigrationAgentPool",
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
    print("\n🚪 Creating AgentCore Gateway (Secured)...")
    
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
             print(f"Gateway {GATEWAY_NAME} likely exists. (Check if Auth needs update).")
             # Retrieve ID if possible or fail
             pass 
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
    
    print("\n📝 Generated Tool Schema for Gateway Config:")
    print(json.dumps(tools_schema, indent=2))
    
    # Create the Gateway Target Mapping
    print("\n🔗 Mapping Gateway to Lambda Functions...")
    
    # We pass the schema we generated above
    target_id = utils.create_gateway_target(
        gateway_id=gateway_id,
        lambda_arn=lambda_arn,
        tool_schema=tools_schema,
        region=REGION
    )

    print("\n🎉 Deployment Complete!")
    print(f"   - Gateway ID:   {gateway_id}")
    print(f"   - Lambda ARN:   {lambda_arn}")
    print(f"   - Target ID:    {target_id}")
    print("\nYou can now run 'python migration_agent.py' to start the agent.")


if __name__ == "__main__":
    main()

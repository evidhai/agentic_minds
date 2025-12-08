import boto3
import json
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True), override=True)

USER_POOL_ID = "us-east-1_ODuUNHrC1" # Hardcoded from existing setup
CLIENT_NAME = "MigrationAgentWebClient"

def create_web_client():
    print(f"Creating Web App Client in Pool: {USER_POOL_ID}...")
    client = boto3.client('cognito-idp', region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
    
    try:
        # Check if exists
        response = client.list_user_pool_clients(UserPoolId=USER_POOL_ID, MaxResults=60)
        existing_id = None
        for c in response.get("UserPoolClients", []):
            if c["ClientName"] == CLIENT_NAME:
                existing_id = c["ClientId"]
                break
        
        if existing_id:
            print(f"✅ Found existing Web Client ID: {existing_id}")
            return existing_id

        # Create new
        response = client.create_user_pool_client(
            UserPoolId=USER_POOL_ID,
            ClientName=CLIENT_NAME,
            GenerateSecret=False, # Crucial for Frontend (Public Client)
            ExplicitAuthFlows=[
                "ALLOW_USER_SRP_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
                "ALLOW_USER_PASSWORD_AUTH"
            ],
            PreventUserExistenceErrors="ENABLED"
        )
        
        new_id = response['UserPoolClient']['ClientId']
        print(f"✅ Created New Web Client ID: {new_id}")
        return new_id

    except Exception as e:
        print(f"Error creating client: {e}")
        return None

if __name__ == "__main__":
    client_id = create_web_client()
    if client_id:
        print("\n=== FRONTEND CONFIG ===")
        print(f"VITE_COGNITO_USER_POOL_ID={USER_POOL_ID}")
        print(f"VITE_COGNITO_CLIENT_ID={client_id}")
        print("=======================")

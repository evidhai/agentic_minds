import boto3
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True), override=True)

def list_lambdas():
    print("Listing Lambda Functions...")
    client = boto3.client('lambda', region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
    
    try:
        paginator = client.get_paginator('list_functions')
        for page in paginator.paginate():
            for func in page['Functions']:
                print(f"Found Function: {func['FunctionName']} | ARN: {func['FunctionArn']}")
    except Exception as e:
        print(f"Error listing lambdas: {e}")

if __name__ == "__main__":
    list_lambdas()

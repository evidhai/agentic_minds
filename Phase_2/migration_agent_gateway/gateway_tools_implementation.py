import json
import boto3
import ipaddress
import math
import os

# These are the tool implementations that would run as AWS Lambda functions
# behind the AgentCore Gateway.

def lambda_handler(event, context):
    """
    Main entry point for the Lambda function serving these tools.
    AgentCore Gateway routes the request here based on the tool name.
    """
    # Extract the tool name
    # e.g. "MyGateway___cost_assistant" -> "cost_assistant"
    tool_name = context.client_context.custom.get('bedrockAgentCoreToolName', '')
    if "___" in tool_name:
        tool_name = tool_name.split("___")[1]
    
    # Extract arguments
    # The event payload IS the input schema defined in the Gateway
    payload = event
    
    print(f"Executing Tool: {tool_name}")
    
    try:
        if tool_name == 'cost_assistant':
            result = cost_assistant(payload)
        elif tool_name == 'aws_docs_assistant':
            result = aws_docs_assistant(payload)
        elif tool_name == 'vpc_subnet_calculator':
            result = vpc_subnet_calculator(payload)
        else:
            return {
                'statusCode': 400,
                'body': f"Unknown tool: {tool_name}"
            }
            
        return {
            'statusCode': 200,
            'body': result
        }
    except Exception as e:
        print(f"Error executing {tool_name}: {e}")
        return {
            'statusCode': 500,
            'body': f"Error executing tool: {str(e)}"
        }

# --- Tool Implementations ---

def cost_assistant(payload):
    """
    Simulated Cost Assistant (In a real Lambda, this would query Pricing API)
    """
    # NOTE: In a Lambda environment, you can't easily run 'uvx' or subprocesses.
    # You would use the boto3 pricing client directly instead of the MCP server wrapper.
    
    pricing = boto3.client('pricing', region_name='us-east-1')
    return f"AWS Pricing Information for {payload}: [Simulated Boto3 Pricing Data]"

def aws_docs_assistant(payload):
    """
    Simulated Docs Assistant
    """
    # In Lambda, you would use Amazon Kendra or a Search Index here.
    return f"AWS Documentation Search Results for {payload}: [Simulated Search Results]"

def vpc_subnet_calculator(payload):
    """
    Calculates optimized VPC subnet ranges for a given CIDR block.
    (Pure Python logic, works perfectly in Lambda)
    """
    print(f"vpc_subnet_calculator called with payload: {payload}")
    
    # Parse inputs with defaults - similar to original logic
    # ... (Full logic copied from original agent) ...
    
    # Simplified for the example file:
    vpc_cidr = payload.get("cidr")
    return f"Subnet Calculation Plan for {vpc_cidr} (Simulated Output)"

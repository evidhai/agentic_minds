# Migration Agent Gateway Deployment Guide

This folder contains the complete infrastructure code to deploy your **Serverless Migration Agent** on AWS.

## Architecture components
1.  **AgentCore Gateway**: The "Door" that manages access and APIs.
2.  **AWS Lambda**: The "Hands" that execute the tools (`cost_assistant`, `vpc_subnet_calculator`, etc.).
3.  **Migration Agent**: The "Brain" that runs locally (or in a container) and talks to the Gateway.

## Prerequisites
1.  **AWS Credentials**: Ensure you have valid credentials in your environment.
    ```bash
    export AWS_ACCESS_KEY_ID=...
    export AWS_SECRET_ACCESS_KEY=...
    export AWS_SESSION_TOKEN=...
    export AWS_DEFAULT_REGION=us-east-1
    ```
2.  **Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Step 1: Deploy the Backend (Gateway + Lambda + Auth)
Run the automated deployment script. This will:
- Set up **Cognito Authentication** (User Pool, Client, etc.).
- Package and Deploy the Lambda Function.
- Create and Secure the AgentCore Gateway.
- Generate `gateway_auth.json` (Credentials) for the Agent.

```bash
python deploy_gateway.py
```

**Output**:
The script will output the **Lambda ARN** and **Gateway ID**. Keep note of these!

## Step 2: Run the Agent Backend
The agent will automatically read `gateway_auth.json` to authenticate with the Gateway.

```bash
# Ensure you set the Gateway URL if not automatically detected (or check output of deploy)
export GATEWAY_URL="https://gateway-id.bedrock-agentcore.us-east-1.amazonaws.com" 

python migration_agent.py
```


## Step 3: Run the Frontend
(In a separate terminal)
```bash
cd ../migration_agent_frontend
npm run dev
```

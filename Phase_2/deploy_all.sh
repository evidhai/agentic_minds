#!/bin/bash
set -e

# Configuration
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-"us-east-1"}
export APP_NAME=${APP_NAME:-"MigrationAgent-Test"}

# Use VENV Python
PYTHON_CMD="$(pwd)/.venv/bin/python3"
if [ ! -f "$PYTHON_CMD" ]; then
    echo "⚠️  Virtual environment python not found at $PYTHON_CMD. Falling back to 'python3'."
    PYTHON_CMD="python3"
fi
echo "Using Python: $PYTHON_CMD"

echo "🚀 Starting Full Serverless Deployment for $APP_NAME..."
echo "---------------------------------------------------"

# 1. Deploy Runtime (Gateway + Tools + Auth)
echo "\n🔹 Step 1: Deploying AgentCore Runtime..."
cd migration_agent_gateway
"$PYTHON_CMD" deploy_gateway.py

# Fetch the Gateway URL for the next step
echo "   Fetching Gateway URL..."
if [ -f "gateway_id.txt" ]; then
    GATEWAY_ID=$(cat gateway_id.txt)
    export GATEWAY_URL="https://${GATEWAY_ID}.gateway.${AWS_DEFAULT_REGION}.amazonaws.com"
else
    echo "❌ Error: gateway_id.txt not found. Deployment failed."
    exit 1
fi
echo "   ✅ Using Gateway URL: $GATEWAY_URL"
cd ..

# 2. Deploy Serverless Backend Agent (Brain)
echo "\n🔹 Step 2: Deploying Serverless Agent Brain (Lambda)..."
cd agent_cloud
# deploy_brain_lambda.py creates DDB Table, Builds Docker (Native Runtime), Push to ECR, Deploys Lambda
"$PYTHON_CMD" deploy_brain_lambda.py
cd ..

# 3. Deploy Frontend
echo "\n🔹 Step 3: Deploying Frontend to Amplify..."
cd migration_agent_frontend

# Build the Frontend 
echo "   Building Frontend..."
# Note: VITE_API_URL must be set by user or will be empty (triggering warning)
# export VITE_API_URL="$GATEWAY_URL" <--- INCORRECT for this architecture
# Build is handled inside deploy_amplify.sh now

./deploy_amplify.sh
cd ..

echo "\n---------------------------------------------------"
echo "✅✅✅ Full Serverless Stack Deployment Complete! ✅✅✅"
echo "---------------------------------------------------"
echo "1. Frontend URL: Check Step 3 output"
echo "2. Backend API:  (See Lambda Function URL in Step 2 output)"
echo "3. Gateway URL:  $GATEWAY_URL"
echo "---------------------------------------------------"
echo "👉 ACTION REQUIRED: Update your Frontend with the new Backend URL!"
echo "   Go to AWS Amplify Console -> Environment Variables -> VITE_API_URL"
echo "   Set it to the Lambda Function URL."
echo "---------------------------------------------------"

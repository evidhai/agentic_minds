#!/bin/bash
set -e

# Ensure we run from the project root (one level up from script)
cd "$(dirname "$0")/.."

# Load .env variables if present
# Load .env variables only if not already set in environment
if [ -z "$AWS_ACCESS_KEY_ID" ] && [ -f ".env" ]; then
    echo "[INFO] Loading credentials from .env"
    set -a
    source .env
    set +a
else
    echo "[INFO] Using existing environment credentials (skipping .env)"
fi

APP_NAME="migration-agent-cloud"
AWS_REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}"

echo "[INFO] Deploying ${APP_NAME} to AWS in region ${AWS_REGION}..."

# 1. Login to ECR
echo "[INFO] Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# 2. Check/Create Repository
echo "[INFO] Checking ECR Repository..."
aws ecr describe-repositories --repository-names ${APP_NAME} --region ${AWS_REGION} || \
aws ecr create-repository --repository-name ${APP_NAME} --region ${AWS_REGION}

# 3. Build Docker Image (Context is Root)
echo "[INFO] Building Docker Image (Targeting linux/amd64 for Fargate)..."
docker build --platform linux/amd64 -f agent_cloud/Dockerfile -t ${APP_NAME}:latest .
docker tag ${APP_NAME}:latest ${ECR_REPO_URI}:latest

# 4. Push to ECR
echo "[INFO] Pushing to ECR (This may take a while)..."
docker push ${ECR_REPO_URI}:latest

# 5. Force Update ECS Service
echo "[INFO] Updating ECS Service to pull new image..."
aws ecs update-service --cluster MigrationAgentCluster --service MigrationAgentService --force-new-deployment --region ${AWS_REGION} > /dev/null

echo "[SUCCESS] Deployment Artifact Pushed & Service Updated!"
echo "Image URI: ${ECR_REPO_URI}:latest"
echo "Visit: https://migratecompanion.evidhai.com (Give it 2-3 mins to stabilize)"

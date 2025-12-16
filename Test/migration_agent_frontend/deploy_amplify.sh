#!/bin/bash
set -e

APP_NAME="migration-agent-frontend-test"
BRANCH_NAME="main"

echo "🚀 Starting Manual Amplify Deployment for $APP_NAME..."

# 1. Check if App Exists, else Create
APP_ID=$(aws amplify list-apps --query "apps[?name=='$APP_NAME'].appId" --output text)

if [ -z "$APP_ID" ]; then
    echo "Creating new Amplify App: $APP_NAME"
    APP_ID=$(aws amplify create-app --name "$APP_NAME" --platform "WEB" --query "app.appId" --output text)
    echo "✅ Created App ID: $APP_ID"
else
    echo "ℹ️ Found Existing App ID: $APP_ID"
fi

# 2. Check if Branch Exists, else Create
BRANCH_EXISTS=$(aws amplify list-branches --app-id $APP_ID --query "branches[?branchName=='$BRANCH_NAME'].branchName" --output text)

if [ -z "$BRANCH_EXISTS" ]; then
    echo "Creating Branch: $BRANCH_NAME"
    aws amplify create-branch --app-id $APP_ID --branch-name $BRANCH_NAME > /dev/null
    echo "✅ Created Branch: $BRANCH_NAME"
else
    echo "ℹ️ Branch '$BRANCH_NAME' exists."
fi

# 2.5 Stop Pending Jobs (Fixes BadRequestException)
echo "🧹 Checking for pending jobs..."
# Get all pending/running jobs, verify if list is empty, pick the first one
PENDING_JOBS=$(aws amplify list-jobs --app-id $APP_ID --branch-name $BRANCH_NAME --query "jobSummaries[?status=='PENDING' || status=='RUNNING'].jobId" --output text)

for JOB in $PENDING_JOBS; do
    if [ "$JOB" != "None" ] && [ ! -z "$JOB" ]; then
        echo "⚠️ Found pending job: $JOB. Stopping it..."
        aws amplify stop-job --app-id $APP_ID --branch-name $BRANCH_NAME --job-id $JOB > /dev/null
    fi
done
sleep 5

# 3. Build & Zip Artifacts
echo "🛠️  Building Frontend..."
if [ -z "$VITE_API_URL" ]; then
    echo "⚠️  WARNING: VITE_API_URL is not set. App might use default/relative path."
else
    echo "   Using VITE_API_URL=$VITE_API_URL"
fi

npm install
npm run build

echo "📦 Zipping build artifacts..."
rm -f deploy.zip
cd dist
zip -r ../deploy.zip .
cd ..

# 4. Create Deployment Entry
echo "⬆️ Creating deployment entry..."
# We need BOTH the Upload URL and the Job ID. 
# We'll fetch the JSON output to parsing variables.
DEPLOY_OUT=$(aws amplify create-deployment --app-id $APP_ID --branch-name $BRANCH_NAME --output json)

DEPLOYMENT_URL=$(echo $DEPLOY_OUT | grep -o '"zipUploadUrl": "[^"]*' | grep -o '[^"]*$')
JOB_ID=$(echo $DEPLOY_OUT | grep -o '"jobId": "[^"]*' | grep -o '[^"]*$')

if [ -z "$DEPLOYMENT_URL" ] || [ -z "$JOB_ID" ]; then
    echo "❌ Failed to create deployment. Output:"
    echo "$DEPLOY_OUT"
    exit 1
fi

echo "   Job ID: $JOB_ID"
echo "⬆️ Uploading artifact..."
curl -T deploy.zip "$DEPLOYMENT_URL"

# 5. Start Deployment
echo "🚀 Starting deployment..."
aws amplify start-deployment --app-id $APP_ID --branch-name $BRANCH_NAME --job-id $JOB_ID > /dev/null

echo "✅ Deployment Started! Job ID: $JOB_ID"
echo "Waiting for deployment to complete..."

# Wait loop (simple)
sleep 10
STATUS=$(aws amplify get-job --app-id $APP_ID --branch-name $BRANCH_NAME --job-id $JOB_ID --query "job.summary.status" --output text)
echo "Current Status: $STATUS"

echo "🎉 Done! Your app should be live shortly at: https://$BRANCH_NAME.$APP_ID.amplifyapp.com"

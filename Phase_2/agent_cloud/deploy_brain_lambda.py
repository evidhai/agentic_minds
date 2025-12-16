import boto3
import time
import os
import json
from bedrock_agentcore_starter_toolkit import Runtime
from dotenv import load_dotenv, find_dotenv

# Load Env
load_dotenv(find_dotenv(usecwd=True), override=True)

# Configuration
APP_NAME = os.getenv("APP_NAME", "MigrationAgent-Test")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]

# Resource Names
LAMBDA_BRAIN_NAME = f"{APP_NAME}-Brain"
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "MigrationAgentMemory-Test")
ECR_REPO_NAME = f"{APP_NAME}-Brain-Repo".replace("-", "").lower() # ECR/Toolkit naming

def deploy_brain():
    print(f"🚀 Deploying AgentCore Brain: {LAMBDA_BRAIN_NAME}...")
    
    # 1. Build & Push using AgentCore Runtime Toolkit
    # This ensures we use the 'inbuilt agentcore func' as requested
    print("📦 Building Image using AgentCore Runtime...")
    
    # PRE-BUILD: Copy dependencies from sibling directories
    import shutil
    source_util = "../migration_agent_gateway/gateway_infra_utils.py"
    dest_util = "./gateway_infra_utils.py"
    if os.path.exists(source_util):
        print(f"COPY {source_util} -> {dest_util}")
        shutil.copy(source_util, dest_util)
    else:
        print(f"⚠️ Warning: Could not find {source_util}")

    runtime = Runtime()
    
    # Configure ensures ECR exists and Pushes image
    # We pass Dockerfile.lambda explicitly
    config = runtime.configure(
        agent_name=ECR_REPO_NAME,
        entrypoint="migration_agent.py",
        requirements_file="requirements.txt",
        auto_create_ecr=True,
        auto_create_execution_role=True, # We will use this role or our own if we want
        disable_otel=True,
        region=REGION
    )
    runtime.launch()
    # MANUAL BUILD STEP
    import subprocess
    
    # 1.5 Construct ECR URI
    ecr_uri = f"{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/{ECR_REPO_NAME}"
    print(f"🐳 ECR URI: {ecr_uri}")
    
    # 1.6 Ensure ECR Repo Exists (Manual Safety Check)
    # Using CLI via subprocess to avoid Boto3 ParamValidationError issues
    print(f"🔍 Checking ECR Repo: {ECR_REPO_NAME}")
    try:
        subprocess.run(
            f"aws ecr describe-repositories --repository-names {ECR_REPO_NAME} --region {REGION}",
            shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(f"ℹ️ ECR Repo {ECR_REPO_NAME} already exists.")
    except subprocess.CalledProcessError:
        print(f"🆕 Creating ECR Repo: {ECR_REPO_NAME}")
        subprocess.run(
            f"aws ecr create-repository --repository-name {ECR_REPO_NAME} --region {REGION}",
            shell=True, check=True
        )
    
    # Login
    print("🔑 Logging into ECR...")
    subprocess.run(f"aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin {ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com", shell=True, check=True)
    
    # PRE-BUILD: Copy dependencies from sibling directories moved up

    # Build
    # CRITICAL: Force AMD64 Platform for consistent Lambda deployment (avoids 502 on M1/M2/M3 Macs)
    # Add --provenance=false to avoid OCI manifest issues with Lambda
    print("🛠️  Docker Build (forcing linux/amd64)...")
    CMD = f"docker build --platform linux/amd64 --provenance=false -t {ECR_REPO_NAME} -f Dockerfile.lambda ."
    subprocess.run(CMD, shell=True, check=True)
    
    # Tag
    print("🏷️  Docker Tag...")
    subprocess.run(f"docker tag {ECR_REPO_NAME}:latest {ecr_uri}:latest", shell=True, check=True)
    
    # Push
    print("⬆️  Docker Push...")
    subprocess.run(f"docker push {ecr_uri}:latest", shell=True, check=True)
    
    image_uri = f"{ecr_uri}:latest"
    print(f"✅ Image Ready: {image_uri}")
    
    # Env Vars
    env_vars = {
        "Variables": {
            "APP_POOL_NAME": f"{APP_NAME}-Pool",
            "GATEWAY_URL": os.getenv("GATEWAY_URL", ""),
            "DYNAMODB_TABLE": TABLE_NAME,
            "MEMORY_TABLE_NAME": TABLE_NAME 
        }
    }

    # 2. Deploy Lambda (Manual Step to ensure we get a FUNCTION URL)
    # The 'Runtime.launch' hides the Lambda or creates a Bedrock Agent resource.
    # We explicitly want a callable Lambda for our Web Frontend.
    
    print("⚡ Deploying Lambda Function (Manual Control)...")
    
    # Use the role created by Toolkit or fallback?
    # Toolkit creates a role, usually returned in config.execution_role
    # If not, we use existing logic.
    role_arn = getattr(config, 'execution_role', None) 
    # Note: config objects might not have it populated if it was just a local config.
    # We will look for or create our own role to be safe.
    
    lambda_client = boto3.client("lambda", region_name=REGION)
    iam = boto3.client("iam", region_name=REGION)

    if not role_arn:
        print("ℹ️ Ensuring IAM Role exists...")
        role_name = f"{APP_NAME}-BrainRole"
        assume_role = {"Version": "2012-10-17","Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}
        try:
            iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_role))
        except iam.exceptions.EntityAlreadyExistsException:
            pass
        
        # Attach policies
        iam.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole")
        try:
            iam.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess")
            iam.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess")
            iam.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AWSLambda_FullAccess")
        except Exception:
            pass
        
        # Get ARN
        while True:
            try:
                role_arn = iam.get_role(RoleName=role_name)["Role"]["Arn"]
                break
            except Exception:
                time.sleep(1)
        print(f"   Using Role: {role_arn}")
        time.sleep(5) # Propagation

    # Ensure Table Exists
    dynamodb = boto3.client("dynamodb", region_name=REGION)
    try:
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{'AttributeName': 'sessionId', 'KeyType': 'HASH'}, {'AttributeName': 'messageId', 'KeyType': 'RANGE'}],
            AttributeDefinitions=[{'AttributeName': 'sessionId', 'AttributeType': 'S'}, {'AttributeName': 'messageId', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✅ Created Backing Table: {TABLE_NAME}")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=TABLE_NAME)
    except dynamodb.exceptions.ResourceInUseException:
        print(f"ℹ️ Backing Table {TABLE_NAME} ready.")

    # Deploy Function
    try:
        lambda_client.create_function(
            FunctionName=LAMBDA_BRAIN_NAME,
            PackageType='Image',
            Code={'ImageUri': image_uri},
            Role=role_arn,
            Timeout=600,
            MemorySize=2048,
            Environment=env_vars
        )
        print(f"✅ Created Function: {LAMBDA_BRAIN_NAME}")
    except lambda_client.exceptions.ResourceConflictException:
        print(f"ℹ️ Updating Function: {LAMBDA_BRAIN_NAME}")
        lambda_client.update_function_code(FunctionName=LAMBDA_BRAIN_NAME, ImageUri=image_uri)
        
        # WAIT for Update to Complete (Fixes ResourceConflictException)
        print("⏳ Waiting for code update to complete...")
        while True:
            time.sleep(5)
            conf = lambda_client.get_function(FunctionName=LAMBDA_BRAIN_NAME)['Configuration']
            status = conf.get('LastUpdateStatus', '')
            state = conf.get('State', '')
            print(f"   Status: {status} | State: {state}")
            if status == 'Successful' and state == 'Active':
                break
            if status == 'Failed':
                raise Exception(f"Lambda Update Failed: {conf.get('LastUpdateStatusReason')}")

        lambda_client.update_function_configuration(FunctionName=LAMBDA_BRAIN_NAME, Environment=env_vars, Timeout=600, MemorySize=2048)

    # Function URL
    # Function URL - Ensure AuthType NONE and CORS
    try:
        url_config = lambda_client.create_function_url_config(
            FunctionName=LAMBDA_BRAIN_NAME,
            AuthType='NONE',
            Cors={'AllowOrigins': ['*'], 'AllowMethods': ['*'], 'AllowHeaders': ['*'], 'AllowCredentials': True}
        )
        print(f"🎉 Function URL Created: {url_config['FunctionUrl']}")
    except lambda_client.exceptions.ResourceConflictException:
        # Force Update to ensure Settings are correct (Fixes 403 Forbidden if previously IAM)
        print("ℹ️ Updating Function URL Config...")
        url_config = lambda_client.update_function_url_config(
            FunctionName=LAMBDA_BRAIN_NAME,
            AuthType='NONE',
            Cors={'AllowOrigins': ['*'], 'AllowMethods': ['*'], 'AllowHeaders': ['*'], 'AllowCredentials': True}
        )
        print(f"🎉 Function URL Updated: {url_config['FunctionUrl']}")

    # 4. Add Permission for Public Access (Critical for AuthType=NONE)
    try:
        lambda_client.add_permission(
            FunctionName=LAMBDA_BRAIN_NAME,
            StatementId='FunctionURLPublicAccess',
            Action='lambda:InvokeFunctionUrl',
            Principal='*',
            FunctionUrlAuthType='NONE'
        )
        print("✅ Added Public Access Permission")
    except lambda_client.exceptions.ResourceConflictException:
        print("ℹ️ Public Permission already exists.")

if __name__ == "__main__":
    deploy_brain()

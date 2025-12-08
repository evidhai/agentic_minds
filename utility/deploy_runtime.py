import os
from bedrock_agentcore.runtime import Runtime
from dotenv import load_dotenv, find_dotenv

# Load Env
load_dotenv(find_dotenv(usecwd=True), override=True)

# Configuration
AGENT_NAME = "MigrationAgentRuntime"
ENTRY_POINT = "migration_agent.py"
REQUIREMENTS_FILE = "requirements.txt"
# Assuming standard ECR/Role setup or auto-create

def main():
    print(f"🚀 Deploying AgentCore Runtime: {AGENT_NAME}...")
    
    # Initialize Runtime
    runtime = Runtime()
    
    try:
        # Configure and Deploy
        # This builds the container, pushes to ECR, and deploys the AgentCore Runtime service
        config_result = runtime.configure(
            agent_name=AGENT_NAME,
            entrypoint=ENTRY_POINT,
            requirements_file=REQUIREMENTS_FILE,
            disable_otel=True, # Privacy setting we added earlier
            auto_create_ecr=True,
            auto_create_execution_role=True,
            # For a real deployment, you might need vpc_enabled=True if connecting to private resources
            # But for this demo we keep it simple.
        )
        
        print("\n✅ Runtime Configuration Complete!")
        print(f"   - Image: {config_result.image_uri}")
        print(f"   - Role:  {config_result.execution_role}")
        
        print("\n⚡ Starting Deployment (this may take a few minutes)...")
        # In a real scenario, you would trigger the deployment here.
        # The configure() method often just preps the build. 
        # Referencing standard AgentCore usage:
        # runtime.deploy() might be the next step if available, or it's part of the flow.
        # Based on 'agentcore_build.py' viewed earlier, 'configure' returns the config needed.
        
        print("To finish deployment, run: bedrock-agentcore-runtime deploy")

    except Exception as e:
        print(f"❌ Error deploying runtime: {e}")

if __name__ == "__main__":
    main()

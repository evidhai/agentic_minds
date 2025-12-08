# AWS Migration Assistant

The **AWS Migration Assistant** is a comprehensive solution designed to assist users in planning, simulating, and executing migrations to AWS. It leverages a modern 3-tier architecture combining a reactive frontend, a containerized agent "brain," and serverless tools for AWS interaction.

---

## 🏗️ Architecture Reference

The application follows a modular, scalable architecture hosted on AWS:

```mermaid
graph TD
    User((User)) -->|HTTPS| Frontend[React Frontend]
    Frontend -->|API Requests| ALB[Application Load Balancer]
    ALB -->|Forward| FargateService[ECS Fargate Service<br>(Migration Agent logic)]
    
    subgraph "Serverless Backend"
        FargateService -->|Direct Invoke (SDK)| Lambda[AWS Lambda<br>(Tools & Utilities)]
        Lambda -->|Read/Write| AWS[AWS Services<br>(Cost Explorer, EC2, etc.)]
    end

    subgraph "Infrastructure"
        FargateService -.->|Logs| CloudWatch
        FargateService -.->|Store Diagrams| S3[S3 Bucket]
        Lambda -.->|Auth| Cognito[Amazon Cognito]
    end
```

### Components

1.  **Frontend (UI)**:
    *   Built with **React + Vite**.
    *   Provides an interactive chat interface and visualization for migration plans.
    *   Connecting to the backend agent via REST/WebSocket APIs.
    *   Auth integrated with **AWS Amplify**.

2.  **Migration Agent Service (The "Brain")**:
    *   Hosted on **AWS ECS Fargate** (Serverless Containers).
    *   Exposed via an **Application Load Balancer (ALB)** with HTTPS support.
    *   Handles state, orchestrates logic, and communicates with the Tools layer.
    *   Built with Python.

3.  **Tools Layer (The "Hands")**:
    *   **Directly invoked** by the Agent Service using the AWS SDK (`boto3`).
    *   Powered by **AWS Lambda** functions.
    *   Provides specific capabilities:
        *   `cost_assistant`: Analyzes pricing.
        *   `vpc_subnet_calculator`: Designs network topologies.
        *   `aws_docs_assistant`: Retrieves AWS documentation.
    *   Secured via **IAM Roles** and **Amazon Cognito**.

---

## 🚀 Infrastructure Hosting & Provisioning

The infrastructure is fully automated using Python (`boto3`) scripting, ensuring reproducible deployments.

### Key Resources Provisioned
*   **Compute**: Amazon ECS Cluster + Fargate Task Definition (CPU: 1vCPU, Mem: 3GB).
*   **Networking**: VPC, Public Subnets, Security Groups, and Application Load Balancer (Internet Facing).
*   **Security**: IAM Roles (Least Privilege), Amazon Cognito (Identity & Access Management).
*   **Storage**: Amazon S3 (for generated diagrams), Amazon ECR (Docker Container Registry).
*   **DNS**: Amazon Route53 (Custom domain management).

---

## 📚 User Guide & Deployment

Follow these steps to deploy the application from scratch.

### Prerequisites
*   **AWS CLI** installed and configured (`aws configure`).
*   **Docker** running.
*   **Python 3.11+** and **Node.js 18+**.
*   **Git**.

### 1. Deploy the Serverless Backend (Tools Layer)
First, we set up the "Tools" layer so the agent has capabilities to use.

```bash
cd migration_agent_gateway
pip install -r requirements.txt
python deploy_gateway.py
```
*   **What this does**: Deploys the **Tools Lambda**, creates IAM roles, and sets up Cognito. (Note: The script also provisions an Agent Gateway, but the Agent is configured to invoke the Lambda directly).
*   **Output**: Note down the `Lambda ARN` from the output.

### 2. Provision Cloud Infrastructure (Agent Service)
Next, deploy the containerized agent service that uses the tools.

```bash
cd ../agent_cloud
pip install -r requirements.txt
python provision_cloud.py
```
*   **What this does**: Creates the S3 Bucket, ECR Repo, ECS Cluster, ALB, and hooks everything together.
*   **Output**: Returns the `ALB DNS Name` and configures Route53 if applicable.

### 3. Build & Push Agent Container
Deploy the actual application logic to the provisioned ECS cluster.

```bash
# Still in agent_cloud directory
./deploy_cloud.sh
```
*   **What this does**: Builds the Docker image locally, logs into ECR, pushes the image, and forces a new deployment on ECS Fargate.

## 🧪 Testing Locally

### Run the Frontend
Start the user interface locally to test the integration.

```bash
cd ../migration_agent_frontend
npm install
npm run dev
```
*   Open your browser to the local URL (e.g., `http://localhost:5173`).
*   The frontend will communicate with the backend services deployed in previous steps.

---

## 🛠️ Developer Reference

*   **Logs**: Check CloudWatch Logs under `/ecs/migration-agent-cloud` for application logs.
*   **Configuration**:
    *   Backend Env Vars: Managed in `provision_cloud.py` (e.g., `DIAGRAM_BUCKET_NAME`, `AWS_DEFAULT_REGION`).
    *   Frontend Env: Create a `.env` file in `migration_agent_frontend` if needed for API endpoints.

---

## 🔧 Reusability & Extensibility

### 1. Configuration Checkpoints
*   **Infrastructure Params**: Modify `agent_cloud/provision_cloud.py` to change:
    *   `REGION`: Target AWS Region.
    *   `ECS_CLUSTER_NAME`: Name of the ECS Cluster.
    *   `APP_NAME`: Naming prefix for all resources.
*   **Agent Logic**: Modify `agent_cloud/migration_agent.py` to change:
    *   `system_prompt`: The core personality and instruction set of the agent.
    *   `model`: The Bedrock model ID (e.g., switch to Claude 3.5 Sonnet).

### 2. Adding New Serverless Tools
To add a new capability (e.g., a "Security Auditor" tool), follow this 3-step pattern:

1.  **Implement Logic (Lambda)**:
    *   Open `migration_agent_gateway/gateway_tools_lambda.py`.
    *   Add your python function (e.g., `def security_auditor(payload): ...`).
    *   Update the `lambda_handler` to route to your new function name.

2.  **Deploy Changes**:
    *   Run `python deploy_gateway.py` in the `migration_agent_gateway` folder to update the Lambda code.

3.  **Connect Agent**:
    *   Open `agent_cloud/migration_agent.py`.
    *   Create a local tool stub using the `@tool` decorator that calls your Lambda.
    *   Add the new tool function to the `all_tools` list in `migration_assistant`.

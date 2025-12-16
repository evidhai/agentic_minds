![AWS Migration Assistant](banner.png)

# ☁️ AWS Migration Assistant (AgentCore Gateway)

An intelligent, multi-modal AI agent designed to assist organizations in migrating on-premises workloads to AWS. Built with **Amazon Bedrock**, **Anthropic Claude 3.5 Sonnet**, and **AgentCore Gateway**.

## 🚀 Key Features

*   **Hybrid Agent Architecture**: Combines remote AWS Lambda tools (Gateway) with local tools (Vision/Diagrams).
*   **Multi-Modal Analysis**: Upload High-Level Design (HLD) or Low-Level Design (LLD) images for instant architectural auditing using **Amazon Nova Pro**.
*   **Dynamic Diagram Generation**: Generates professional AWS architecture diagrams on-the-fly using MCP (Model Context Protocol).
*   **Cost Estimation**: Real-time cost estimates for AWS services via authorized Lambda tools.
*   **IP Planning**: Specialized VPC Subnet Calculator for Private IPv4 conservation.
*   **Secure Authentication**: Full Cognito integration with persistent chat sessions.
*   **Premium UI**: Modern, responsive React frontend with glassmorphism design.

---

## 🏗️ System Architecture

The solution uses a **Hybrid Agentic Architecture**, bridging local interactive tools with scalable cloud serverless functions.

### 📐 User Flow

![Architecture Diagram](https://mermaid.ink/img/Z3JhcGggTFIKICAgIFVzZXIoW1VzZXJdKSAtLT58TG9naW58IEF1dGhbQ29nbml0byBBdXRoXQogICAgVXNlciAtLT58Q2hhdC9VcGxvYWR8IEZFW1JlYWN0IEZyb250ZW5kXQogICAgRkUgLS0-fEpTT04gUGF5bG9hZHwgQkVbQmFja2VuZCBBZ2VudCBTZXJ2aWNlXQogICAgCiAgICBzdWJncmFwaCAiQmFja2VuZCBBZ2VudCAoUHl0aG9uL1N0cmFuZHMpIgogICAgICAgIEJFIC0tPnxSb3V0ZXwgUm91dGVye1Rvb2wgUm91dGVyfQogICAgICAgIFJvdXRlciAtLT58SW1hZ2V8IFZpc2lvbltOb3ZhIFZpc2lvbiBBZ2VudF0KICAgICAgICBSb3V0ZXIgLS0-fERpYWdyYW18IE1DUFtNQ1AgRGlhZ3JhbSBTZXJ2ZXJdCiAgICAgICAgUm91dGVyIC0tPnxRdWVyeXwgR2F0ZXdheVtBZ2VudENvcmUgR2F0ZXdheV0KICAgIGVuZAogICAgCiAgICBHYXRld2F5IC0uLT58SW52b2tlfCBMYW1iZGFbQVdTIExhbWJkYSBUb29sc10KICAgIExhbWJkYSAtLT58QVBJfCBBV1NbQVdTIFNlcnZpY2VzXQ==)

<details><summary>View Mermaid Code</summary>

![Architecture Diagram]

<details><summary>View Mermaid Code</summary>

![Architecture Diagram](https://mermaid.ink/img/Z3JhcGggTFIKICAgIFVzZXIoW1VzZXJdKSAtLT58TG9naW58IEF1dGhbQ29nbml0byBBdXRoXQogICAgVXNlciAtLT58Q2hhdC9VcGxvYWR8IEZFW1JlYWN0IEZyb250ZW5kXQogICAgRkUgLS0-fEpTT04gUGF5bG9hZHwgQkVbQmFja2VuZCBBZ2VudCBTZXJ2aWNlXQogICAgCiAgICBzdWJncmFwaCAiQmFja2VuZCBBZ2VudCAoUHl0aG9uL1N0cmFuZHMpIgogICAgICAgIEJFIC0tPnxSb3V0ZXwgUm91dGVye1Rvb2wgUm91dGVyfQogICAgICAgIFJvdXRlciAtLT58SW1hZ2V8IFZpc2lvbltOb3ZhIFZpc2lvbiBBZ2VudF0KICAgICAgICBSb3V0ZXIgLS0-fERpYWdyYW18IE1DUFtNQ1AgRGlhZ3JhbSBTZXJ2ZXJdCiAgICAgICAgUm91dGVyIC0tPnxRdWVyeXwgR2F0ZXdheVtBZ2VudENvcmUgR2F0ZXdheV0KICAgIGVuZAogICAgCiAgICBHYXRld2F5IC0uLT58SW52b2tlfCBMYW1iZGFbQVdTIExhbWJkYSBUb29sc10KICAgIExhbWJkYSAtLT58QVBJfCBBV1NbQVdTIFNlcnZpY2VzXQ==)

<details><summary>View Mermaid Code</summary>

```mermaid
graph LR
    User([User]) -->|Login| Auth[Cognito Auth]
    User -->|Chat/Upload| FE[React Frontend]
    FE -->|JSON Payload| BE[Backend Agent Service]
    
    subgraph "Backend Agent (Python/Strands)"
        BE -->|Route| Router{Tool Router}
        Router -->|Image| Vision[Nova Vision Agent]
        Router -->|Diagram| MCP[MCP Diagram Server]
        Router -->|Query| Gateway[AgentCore Gateway]
    end
    
    Gateway -.->|Invoke| Lambda[AWS Lambda Tools]
    Lambda -->|API| AWS[AWS Services]
```
</details>
</details>
</details>

### ☁️ Infrastructure Diagram



<details><summary>View Mermaid Code</summary>

![Architecture Diagram](https://mermaid.ink/img/Zmxvd2NoYXJ0IFRCCiAgICBzdWJncmFwaCBDbGllbnQgWyLwn5K7IENsaWVudCBTaWRlIl0KICAgICAgICBVSVtSZWFjdCBVSSAoVml0ZSldCiAgICAgICAgU3RvcmVbTG9jYWwgU3RvcmFnZSBTZXNzaW9uXQogICAgZW5kCgogICAgc3ViZ3JhcGggQmFja2VuZCBbIuKame-4jyBBZ2VudCBTZXJ2aWNlIl0KICAgICAgICBBZ2VudFtNaWdyYXRpb24gQWdlbnQgKFB5dGhvbi9TdHJhbmRzKV0KICAgICAgICBNZW1vcnlbU2Vzc2lvbiBNZW1vcnkgKERpY3QvRHluYW1vREIpXQogICAgICAgIE1DUF9DbGllbnRbTUNQIENsaWVudF0KICAgIGVuZAoKICAgIHN1YmdyYXBoIEFXUyBbIuKYge-4jyBBV1MgQ2xvdWQiXQogICAgICAgIENvZ25pdG9bQ29nbml0byBVc2VyIFBvb2xdCiAgICAgICAgQmVkcm9ja1tBbWF6b24gQmVkcm9jayAoQ2xhdWRlIDMuNSBTcG5uZXQpXQogICAgICAgIExhbWJkYVtBV1MgTGFtYmRhIChHYXRld2F5IFRvb2xzKV0KICAgICAgICBUaXRhbltUaXRhbiBJbWFnZSBHZW5dCiAgICAgICAgTm92YVtOb3ZhIFBybyBWaXNpb25dCiAgICBlbmQKCiAgICBVSSAtLT58QXV0aHwgQ29nbml0bwogICAgVUkgPC0tPnxIVFRQL1JFU1R8IEFnZW50CiAgICBBZ2VudCA8LS0-fExMTSBJbmZlcmVuY2V8IEJlZHJvY2sKICAgIEFnZW50IDwtLT58RGlyZWN0IEludm9rZXwgTGFtYmRhCiAgICBBZ2VudCA8LS0-fEdlbmVyYXRlfCBNQ1BfQ2xpZW50CiAgICBNQ1BfQ2xpZW50IC0uLT4gVGl0YW4KICAgIEFnZW50IC0uLT58QW5hbHl6ZXwgTm92YQ==)

<details><summary>View Mermaid Code</summary>

![Architecture Diagram](https://mermaid.ink/img/Zmxvd2NoYXJ0IFRCCiAgICBzdWJncmFwaCBDbGllbnQgWyJDbGllbnQgU2lkZSJdCiAgICAgICAgVUlbUmVhY3QgVUkgKFZpdGUpXQogICAgICAgIFN0b3JlW0xvY2FsIFN0b3JhZ2UgU2Vzc2lvbl0KICAgIGVuZAoKICAgIHN1YmdyYXBoIEJhY2tlbmQgWyJBZ2VudCBTZXJ2aWNlIl0KICAgICAgICBBZ2VudFtNaWdyYXRpb24gQWdlbnQgKFB5dGhvbi9TdHJhbmRzKV0KICAgICAgICBNZW1vcnlbU2Vzc2lvbiBNZW1vcnkgKERpY3QvRHluYW1vREIpXQogICAgICAgIE1DUF9DbGllbnRbTUNQIENsaWVudF0KICAgIGVuZAoKICAgIHN1YmdyYXBoIEFXUyBbIkFXUyBDbG91ZCJdCiAgICAgICAgQ29nbml0b1tDb2duaXRvIFVzZXIgUG9vbF0KICAgICAgICBCZWRyb2NrW0FtYXpvbiBCZWRyb2NrIChDbGF1ZGUgMy41IFNvbm5ldCldCiAgICAgICAgTGFtYmRhW0FXUyBMYW1iZGEgKEdhdGV3YXkgVG9vbHMpXQogICAgICAgIFRpdGFuW1RpdGFuIEltYWdlIEdlbl0KICAgICAgICBOb3ZhW05vdmEgUHJvIFZpc2lvbl0KICAgIGVuZAoKICAgIFVJIC0tPnxBdXRofCBDb2duaXRvCiAgICBVSSA8LS0-fEhUVFAvUkVTVHwgQWdlbnQKICAgIEFnZW50IDwtLT58TExNIEluZmVyZW5jZXwgQmVkcm9jawogICAgQWdlbnQgPC0tPnxEaXJlY3QgSW52b2tlfCBMYW1iZGEKICAgIEFnZW50IDwtLT58R2VuZXJhdGV8IE1DUF9DbGllbnQKICAgIE1DUF9DbGllbnQgLS4tPiBUaXRhbgogICAgQWdlbnQgLS4tPnxBbmFseXplfCBOb3Zh)

<details><summary>View Mermaid Code</summary>

```mermaid
flowchart TB
    subgraph Client ["Client Side"]
        UI[React UI (Vite)]
        Store[Local Storage Session]
    end

    subgraph Backend ["Agent Service"]
        Agent[Migration Agent (Python/Strands)]
        Memory[Session Memory (Dict/DynamoDB)]
        MCP_Client[MCP Client]
    end

    subgraph AWS ["AWS Cloud"]
        Cognito[Cognito User Pool]
        Bedrock[Amazon Bedrock (Claude 3.5 Sonnet)]
        Lambda[AWS Lambda (Gateway Tools)]
        Titan[Titan Image Gen]
        Nova[Nova Pro Vision]
    end

    UI -->|Auth| Cognito
    UI <-->|HTTP/REST| Agent
    Agent <-->|LLM Inference| Bedrock
    Agent <-->|Direct Invoke| Lambda
    Agent <-->|Generate| MCP_Client
    MCP_Client -.-> Titan
    Agent -.->|Analyze| Nova
```
</details>
</details>
</details>

1.  **Frontend (`migration_agent_frontend`)**: 
    *   React + Vite SPA.
    *   AWS Amplify (Cognito) for Auth.
    *   Markdown & Image Rendering for rich chat experience.
2.  **Backend Agent (`migration_agent_gateway`)**:
    *   Python-based Agent using `strands` framework.
    *   **AgentCore Gateway**: Managed interface to backend Lambda tools.
    *   **Local Tools**: `arch_diag_assistant` (MCP) and `hld_lld_input_agent` (Nova Vision).
    *   **Memory**: Session-persistent memory using global store (POC).

---

## 🛠️ Prerequisites

*   **Python 3.10+**
*   **Node.js 18+**
*   **AWS CLI** configured with valid credentials (`~/.aws/credentials`).
*   **uv** (Fast Python package installer) - Required for MCP diagram tool.
    *   Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`

---

## 📥 Installation

### 1. Backend Setup

```bash
cd migration_agent_gateway

# Create Virtual Environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd migration_agent_frontend

# Install Node Modules
npm install
```

---

## ▶️ Running the Application

You need two terminal windows running simultaneously.

### Terminal 1: Backend Agent Service

```bash
cd migration_agent_gateway
source ../.venv/bin/activate

# Ensure AWS Credentials are valid
# export AWS_PROFILE=default  (if needed)

# Start the Agent Server
python migration_agent.py
```
*   Server runs on: `http://localhost:8000`

### Terminal 2: Frontend UI

```bash
cd migration_agent_frontend

# Start Vite Dev Server
npm run dev
```
*   UI accessible at: `http://localhost:5173`

---

## 🧩 Usage Guide

1.  **Login**: Use the credentials provided (or Sign Up if enabled).
2.  **Chat**: Ask natural language questions.
    *   *"How do I migrate a 3-tier Java app to AWS?"*
    *   *"Estimate cost for 2 m5.large instances and an RDS db.m5.large."*
3.  **Vision Analysis**: Click the **Paperclip** icon to upload an architecture diagram.
    *   Ask: *"Analyze this diagram and suggest improvements."*
4.  **Diagram Generation**:
    *   Ask: *"Generate an architecture diagram for a Serverless API with caching."*
    *   Result: A professional PNG diagram will be rendered in the chat.
    *   **Download**: Click the "Download" button to save the diagram locally.

---

## 🔧 Troubleshooting

*   **"Security token included in the request is invalid"**:
    *   Your local AWS temporary credentials have expired.
    *   **Fix**: Refresh credentials in the backend terminal and restart `migration_agent.py`.
*   **Diagrams not generating**:
    *   Ensure `uv` is installed and in your PATH.
    *   Check backend logs for `uvx` errors.
*   **Chat History lost on restart**:
    *   The current POC uses in-memory storage for session history. It resets if the backend process stops. (Production would use DynamoDB).

---

## 📜 License

Project created for **IBM Innovathon 2025**.
Using AgentCore Gateway & strands framework.
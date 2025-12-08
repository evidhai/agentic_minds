# Stage 1: Build Frontend
FROM --platform=$BUILDPLATFORM node:22-alpine AS frontend-build
WORKDIR /app
COPY migration_agent_frontend/package*.json ./
RUN npm ci
COPY migration_agent_frontend/ .
RUN npm run build

# Stage 2: Backend
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
# Nginx for proxying, Supervisor for process management
RUN apt-get update && apt-get install -y \
    curl \
    git \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install uv (via pip is easiest)
RUN pip install --no-cache-dir uv

# Copy requirements
COPY agent_cloud/requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent_cloud/migration_agent.py .
COPY migration_agent_gateway/gateway_infra_utils.py .
COPY migration_agent_gateway/gateway_auth.json .
# Copy frontend build
COPY --from=frontend-build /app/dist ./static

# Configure Nginx & Supervisor
# Remove default symlink if exists and copy our config
RUN rm -f /etc/nginx/sites-enabled/default
COPY agent_cloud/nginx.default.conf /etc/nginx/sites-enabled/default
COPY agent_cloud/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port 8000 (Nginx)
EXPOSE 8000

ENV PYTHONUNBUFFERED=1

# Command to run Supervisor (which runs Nginx + Python)
CMD ["/usr/bin/supervisord"]

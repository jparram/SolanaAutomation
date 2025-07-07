# Part 5: Deployment

In this section, we'll cover how to deploy our SolanaAI Agent platform to production environments, ensuring it's secure, reliable, and scalable.

## Backend Deployment

Let's start by setting up the backend deployment using Docker and a cloud provider.

### 1. Creating a Dockerfile for the Backend

First, create a Dockerfile in the backend directory:

```bash
cd backend
```

Edit `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including Chrome and ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) \
    && CHROMEDRIVER_VERSION=$(wget -q -O - "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") \
    && wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create directories for data storage
RUN mkdir -p data/screenshots
RUN mkdir -p data/key

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV BROWSER_HEADLESS=true

# Expose the FastAPI port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Creating a docker-compose.yml File

Create a docker-compose.yml file in the root directory for local testing and development:

```bash
cd ..
```

Edit `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./data:/app/data
    environment:
      - PORT=8000
      - HOST=0.0.0.0
      - DEBUG=true
      - ENVIRONMENT=development
      - CORS_ORIGINS=http://localhost:3000
      - MONGODB_URI=mongodb://mongodb:27017/solana_ai_agent
      - REDIS_URI=redis://redis:6379/0
      - JWT_SECRET=your_jwt_secret_key
      - SOLANA_RPC_URL=https://api.devnet.solana.com
      - BROWSER_HEADLESS=true
    depends_on:
      - mongodb
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_SOLANA_NETWORK=devnet
      - REACT_APP_SOLANA_RPC_URL=https://api.devnet.solana.com
    depends_on:
      - backend

  mongodb:
    image: mongo:5.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:6.2
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  mongodb_data:
  redis_data:
```

### 3. Creating a Dockerfile for the Frontend

Create a Dockerfile in the frontend directory:

```bash
cd frontend
```

Edit `Dockerfile`:

```dockerfile
# Build stage
FROM node:16-alpine as build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the build files from the build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

Create an nginx configuration file:

```bash
touch nginx.conf
```

Edit `nginx.conf`:

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 1000;
    gzip_comp_level 6;

    # Serve static files
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;";
}
```

### 4. Production Environment Configuration

Create a production environment configuration file:

```bash
cd ..
mkdir -p deployment/config
touch deployment/config/.env.production
```

Edit `deployment/config/.env.production`:

```
# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=false
ENVIRONMENT=production
CORS_ORIGINS=https://your-domain.com

# Database Configuration
MONGODB_URI=mongodb://mongodb:27017/solana_ai_agent
REDIS_URI=redis://redis:6379/0

# Authentication
JWT_SECRET=your_production_jwt_secret_key
JWT_EXPIRATION=86400

# AI Configuration
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
XAI_API_KEY=your_xai_api_key
OPEN_ROUTER_API_KEY=your_openrouter_api_key
DEFAULT_MODEL=anthropic/claude-3-opus-20240229

# Solana Configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WALLET_PATH=./key/wallet.json
NETWORK=mainnet

# Birdeye API
BIRDEYE_API_KEY=your_birdeye_api_key

# Browser Automation
BROWSER_HEADLESS=true
CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# X402 Configuration
X402_FACILITATOR_URL=https://s402.w3hf.fun
X402_AUTO_APPROVE_THRESHOLD=0.1
```

### 5. Deploying to a Cloud Provider

#### A. Deploying to Google Cloud Run

First, install the Google Cloud SDK and authenticate:

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project your-project-id
```

Build and push the backend Docker image:

```bash
# Build the Docker image
docker build -t gcr.io/your-project-id/solana-ai-agent-backend ./backend

# Push the image to Google Container Registry
docker push gcr.io/your-project-id/solana-ai-agent-backend

# Deploy to Cloud Run
gcloud run deploy solana-ai-agent-backend \
  --image gcr.io/your-project-id/solana-ai-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="$(cat deployment/config/.env.production | grep -v '^#' | xargs)"
```

Build and push the frontend Docker image:

```bash
# Build the Docker image
docker build -t gcr.io/your-project-id/solana-ai-agent-frontend ./frontend

# Push the image to Google Container Registry
docker push gcr.io/your-project-id/solana-ai-agent-frontend

# Deploy to Cloud Run
gcloud run deploy solana-ai-agent-frontend \
  --image gcr.io/your-project-id/solana-ai-agent-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### B. Deploying to AWS

First, install the AWS CLI and authenticate:

```bash
# Configure AWS CLI
aws configure
```

Create an ECR repository and push the Docker images:

```bash
# Create ECR repositories
aws ecr create-repository --repository-name solana-ai-agent-backend
aws ecr create-repository --repository-name solana-ai-agent-frontend

# Get the ECR login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend image
docker build -t your-account-id.dkr.ecr.us-east-1.amazonaws.com/solana-ai-agent-backend ./backend
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/solana-ai-agent-backend

# Build and push frontend image
docker build -t your-account-id.dkr.ecr.us-east-1.amazonaws.com/solana-ai-agent-frontend ./frontend
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/solana-ai-agent-frontend
```

Then, deploy using either:
- AWS ECS (Elastic Container Service)
- AWS App Runner
- AWS EKS (Elastic Kubernetes Service)

For example, to deploy with AWS App Runner:

```bash
# Create App Runner service for backend
aws apprunner create-service \
  --service-name solana-ai-agent-backend \
  --source-configuration '{"ImageRepository": {"ImageIdentifier": "your-account-id.dkr.ecr.us-east-1.amazonaws.com/solana-ai-agent-backend:latest", "ImageRepositoryType": "ECR", "ImageConfiguration": {"Port": "8000"}}}'

# Create App Runner service for frontend
aws apprunner create-service \
  --service-name solana-ai-agent-frontend \
  --source-configuration '{"ImageRepository": {"ImageIdentifier": "your-account-id.dkr.ecr.us-east-1.amazonaws.com/solana-ai-agent-frontend:latest", "ImageRepositoryType": "ECR", "ImageConfiguration": {"Port": "80"}}}'
```

### 6. Setting Up MongoDB Atlas (Cloud Database)

For production, it's recommended to use MongoDB Atlas instead of a self-hosted MongoDB:

1. Create an account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Configure network access and database users
4. Get the connection string and update your `.env.production` file:

```
MONGODB_URI=mongodb+srv://username:password@your-cluster.mongodb.net/solana_ai_agent?retryWrites=true&w=majority
```

### 7. Setting Up Redis Cloud

For production, you can use Redis Cloud:

1. Create an account at [Redis Cloud](https://redis.com/try-free/)
2. Create a new subscription
3. Get the connection string and update your `.env.production` file:

```
REDIS_URI=redis://username:password@your-redis-instance.redislabs.com:12345
```

## Continuous Integration and Deployment (CI/CD)

Let's set up a CI/CD pipeline using GitHub Actions:

```bash
mkdir -p .github/workflows
touch .github/workflows/ci-cd.yml
```

Edit `.github/workflows/ci-cd.yml`:

```yaml
name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install pytest
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    
    - name: Test with pytest
      run: |
        cd backend
        pytest
    
    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
    
    - name: Install frontend dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Test frontend
      run: |
        cd frontend
        npm test
  
  build-and-deploy:
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    # Set up Google Cloud SDK
    - uses: google-github-actions/setup-gcloud@v0
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        export_default_credentials: true
    
    # Build and push backend image
    - name: Build and push backend image
      run: |
        gcloud auth configure-docker
        docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/solana-ai-agent-backend ./backend
        docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/solana-ai-agent-backend
    
    # Deploy backend to Cloud Run
    - name: Deploy backend to Cloud Run
      run: |
        gcloud run deploy solana-ai-agent-backend \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/solana-ai-agent-backend \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated \
          --set-env-vars="PORT=8000,HOST=0.0.0.0,ENVIRONMENT=production,CORS_ORIGINS=${{ secrets.CORS_ORIGINS }},MONGODB_URI=${{ secrets.MONGODB_URI }},REDIS_URI=${{ secrets.REDIS_URI }},JWT_SECRET=${{ secrets.JWT_SECRET }},OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }},ANTHROPIC_API_KEY=${{ secrets.ANTHROPIC_API_KEY }},BROWSER_HEADLESS=true"
    
    # Build and push frontend image
    - name: Build and push frontend image
      env:
        REACT_APP_API_URL: ${{ secrets.REACT_APP_API_URL }}
      run: |
        cd frontend
        docker build \
          --build-arg REACT_APP_API_URL=$REACT_APP_API_URL \
          --build-arg REACT_APP_SOLANA_NETWORK=mainnet \
          -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/solana-ai-agent-frontend .
        docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/solana-ai-agent-frontend
    
    # Deploy frontend to Cloud Run
    - name: Deploy frontend to Cloud Run
      run: |
        gcloud run deploy solana-ai-agent-frontend \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/solana-ai-agent-frontend \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated
```

## Setting Up HTTPS with Custom Domain

To set up HTTPS with a custom domain, you'll need to:

1. Purchase a domain name (e.g., from Google Domains, Namecheap, etc.)
2. Configure DNS settings to point to your deployed application
3. Set up SSL certificates

### Using Cloudflare for DNS and SSL

1. Sign up for a Cloudflare account
2. Add your domain to Cloudflare
3. Update your domain's nameservers to point to Cloudflare's nameservers
4. Create DNS records:
   - A record for the frontend (e.g., `@` or `www` pointing to your frontend service IP)
   - A record for the backend API (e.g., `api` pointing to your backend service IP)
5. Enable Cloudflare's SSL/TLS protection (recommend "Full" mode)

### Configuring CORS for Production

Update your backend CORS settings in `.env.production`:

```
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### Update Frontend API URL

Update your frontend environment variables for production:

```
REACT_APP_API_URL=https://api.your-domain.com
```

## Monitoring and Maintenance

### Setting Up Logging

For production logging, you can use a service like Google Cloud Logging or AWS CloudWatch.

#### Google Cloud Logging

Cloud Run automatically sends logs to Google Cloud Logging. You can view them in the Google Cloud Console.

#### AWS CloudWatch

If you're using AWS, configure CloudWatch logging:

```bash
# For ECS
aws ecs create-cluster --cluster-name solana-ai-agent-cluster
aws logs create-log-group --log-group-name /ecs/solana-ai-agent
```

### Setting Up Monitoring and Alerts

#### Google Cloud Monitoring

Set up monitoring and alerts in Google Cloud Monitoring:

1. Go to Google Cloud Console > Monitoring
2. Create a new dashboard for your application
3. Add charts for:
   - CPU and memory usage
   - Request latency
   - Error rates
   - Database metrics
4. Set up alerts for critical metrics

#### AWS CloudWatch Alarms

If you're using AWS, set up CloudWatch alarms:

```bash
# Create an alarm for high CPU usage
aws cloudwatch put-metric-alarm \
  --alarm-name solana-ai-agent-high-cpu \
  --alarm-description "Alarm when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=ClusterName,Value=solana-ai-agent-cluster \
  --evaluation-periods 1 \
  --alarm-actions arn:aws:sns:us-east-1:your-account-id:your-sns-topic
```

### Backup Strategy

Set up regular backups for your database:

#### MongoDB Atlas Backups

MongoDB Atlas provides automatic backups. You can configure:

1. Continuous backups with point-in-time recovery
2. Scheduled snapshots (daily, weekly, monthly)

#### Manual Backups

You can also set up manual backups using the `mongodump` tool:

```bash
# Create a backup script
cat > backup.sh << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d%H%M%S)
BACKUP_DIR="/path/to/backups"
mkdir -p "$BACKUP_DIR"
mongodump --uri="your-mongodb-uri" --out="$BACKUP_DIR/backup_$TIMESTAMP"
# Optionally compress the backup
tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" -C "$BACKUP_DIR" "backup_$TIMESTAMP"
rm -rf "$BACKUP_DIR/backup_$TIMESTAMP"
# Delete backups older than 7 days
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete
EOF

# Make the script executable
chmod +x backup.sh

# Add to crontab to run daily
(crontab -l 2>/dev/null; echo "0 0 * * * /path/to/backup.sh") | crontab -
```

## Scaling Your Application

### Horizontal Scaling

Both Google Cloud Run and AWS automatically scale based on traffic. However, you can configure the scaling parameters:

#### Google Cloud Run

```bash
gcloud run services update solana-ai-agent-backend \
  --min-instances=1 \
  --max-instances=10 \
  --cpu=1 \
  --memory=2Gi
```

#### AWS App Runner

```bash
aws apprunner update-service \
  --service-arn your-service-arn \
  --auto-scaling-configuration-arn your-auto-scaling-configuration-arn
```

### Database Scaling

For MongoDB Atlas, you can:

1. Upgrade to a larger cluster tier
2. Enable sharding for horizontal scaling
3. Add read replicas for read-heavy workloads

For Redis Cloud, you can:

1. Upgrade to a larger plan
2. Enable clustering for horizontal scaling
3. Configure Redis persistence options

## Security Considerations

### Securing API Keys

Never commit API keys to your repository. Instead:

1. Use environment variables
2. Use secret management services:
   - Google Secret Manager
   - AWS Secrets Manager
   - HashiCorp Vault

### Setting Up API Rate Limiting

Add rate limiting to your FastAPI application:

```bash
cd backend
pip install fastapi-limiter
```

Edit `main.py`:

```python
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi import Depends

from src.config import settings

# ... existing code ...

@app.on_event("startup")
async def startup():
    # Initialize rate limiter
    redis_instance = redis.from_url(settings.REDIS_URI)
    await FastAPILimiter.init(redis_instance)

# Apply rate limiting to API router
api_router = app.include_router(
    api_router,
    dependencies=[Depends(RateLimiter(times=100, seconds=60))]  # 100 requests per minute
)
```

### Regular Security Audits

Implement a regular security audit schedule:

1. Use automated scanning tools:
   - OWASP ZAP for web security
   - Snyk for dependency vulnerabilities
   - Trivy for container vulnerabilities

2. Add these to your CI/CD pipeline:

```yaml
# Add to .github/workflows/ci-cd.yml
- name: Security scan with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'gcr.io/${{ secrets.GCP_PROJECT_ID }}/solana-ai-agent-backend'
    format: 'table'
    exit-code: '1'
    severity: 'CRITICAL,HIGH'
```

## Disaster Recovery

### Creating a Disaster Recovery Plan

Document a disaster recovery plan that includes:

1. Backup restoration procedures
2. Failover strategies
3. Communication plan
4. Recovery time objectives (RTO) and recovery point objectives (RPO)

### Testing Disaster Recovery

Regularly test your disaster recovery procedures:

```bash
# Create a test backup restoration script
cat > test_restore.sh << 'EOF'
#!/bin/bash
# Get the latest backup
LATEST_BACKUP=$(ls -t /path/to/backups/backup_*.tar.gz | head -1)
# Create a temporary directory
TEMP_DIR=$(mktemp -d)
# Extract the backup
tar -xzf "$LATEST_BACKUP" -C "$TEMP_DIR"
# Restore to a test database
mongorestore --uri="your-test-mongodb-uri" --nsFrom="solana_ai_agent.*" --nsTo="solana_ai_agent_test.*" "$TEMP_DIR"/*
# Verify the restoration
mongo --uri="your-test-mongodb-uri" --eval "db.getSiblingDB('solana_ai_agent_test').getCollectionNames()"
# Clean up
rm -rf "$TEMP_DIR"
EOF

# Make the script executable
chmod +x test_restore.sh
```

## Conclusion

Congratulations! You've now deployed your SolanaAI Agent platform to a production environment. Your application is now:

- Scalable to handle growing traffic
- Secure with proper authentication and encryption
- Monitored for performance and issues
- Backed up for disaster recovery
- Continuously updated through an automated CI/CD pipeline

Remember to regularly:
- Monitor your application's performance
- Update dependencies to fix security vulnerabilities
- Test your backup and recovery procedures
- Review and optimize your cloud costs

This deployment setup provides a solid foundation for your SolanaAI Agent platform, allowing you to focus on adding new features and improving the user experience.

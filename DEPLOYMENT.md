# Resume Analyzer - Deployment Guide

This guide covers various deployment options for the Resume Analyzer FastAPI microservice.

## 🐳 Docker Deployment

### Prerequisites

#### Install Docker

**macOS:**
```bash
# Install Docker Desktop
brew install --cask docker
# Or download from: https://www.docker.com/products/docker-desktop
```

**Linux (Ubuntu/Debian):**
```bash
# Update package index
sudo apt-get update

# Install Docker
sudo apt-get install docker.io

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional)
sudo usermod -aG docker $USER
```

**Windows:**
- Download Docker Desktop from: https://www.docker.com/products/docker-desktop

### Build and Run with Docker

#### Option 1: Using the Build Script (Recommended)
```bash
# Make script executable (if not already)
chmod +x build.sh

# Build and run
./build.sh
```

#### Option 2: Manual Docker Commands
```bash
# Build the image
docker build -t resume-analyzer:latest .

# Run the container
docker run -d \
    --name resume-analyzer-container \
    -p 8000:8000 \
    --restart unless-stopped \
    resume-analyzer:latest

# Check if it's running
docker ps

# View logs
docker logs resume-analyzer-container

# Test the API
curl http://localhost:8000/health
```

#### Option 3: Using Docker Compose
```bash
# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Docker Commands Reference

```bash
# Build image
docker build -t resume-analyzer:latest .

# Run container
docker run -d --name resume-analyzer -p 8000:8000 resume-analyzer:latest

# View running containers
docker ps

# View logs
docker logs resume-analyzer

# Stop container
docker stop resume-analyzer

# Remove container
docker rm resume-analyzer

# Remove image
docker rmi resume-analyzer:latest

# Shell access
docker exec -it resume-analyzer /bin/bash
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Option 1: AWS ECS (Elastic Container Service)

1. **Push image to ECR:**
```bash
# Create ECR repository
aws ecr create-repository --repository-name resume-analyzer

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker tag resume-analyzer:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/resume-analyzer:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/resume-analyzer:latest
```

2. **Create ECS Task Definition and Service**

#### Option 2: AWS App Runner
- Use the Dockerfile directly in App Runner
- Set port to 8000
- Configure environment variables if needed

#### Option 3: AWS Lambda (with Container Images)
- Use the Dockerfile for Lambda
- Configure API Gateway for HTTP endpoints

### Google Cloud Platform (GCP)

#### Option 1: Cloud Run
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/resume-analyzer

# Deploy to Cloud Run
gcloud run deploy resume-analyzer \
    --image gcr.io/PROJECT-ID/resume-analyzer \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8000
```

#### Option 2: Google Kubernetes Engine (GKE)
```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT-ID/resume-analyzer

# Deploy to GKE
kubectl create deployment resume-analyzer --image=gcr.io/PROJECT-ID/resume-analyzer
kubectl expose deployment resume-analyzer --type=LoadBalancer --port=80 --target-port=8000
```

### Microsoft Azure

#### Option 1: Azure Container Instances
```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image resume-analyzer:latest .

# Deploy to Container Instances
az container create \
    --resource-group myResourceGroup \
    --name resume-analyzer \
    --image myregistry.azurecr.io/resume-analyzer:latest \
    --ports 8000 \
    --dns-name-label resume-analyzer-app
```

#### Option 2: Azure App Service
- Use the Dockerfile in App Service
- Configure port 8000
- Enable continuous deployment

### Heroku Deployment

1. **Create Heroku app:**
```bash
heroku create your-app-name
```

2. **Add Heroku-specific files:**
```dockerfile
# Add to Dockerfile or create Procfile
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

3. **Deploy:**
```bash
# Using Heroku Container Registry
heroku container:login
heroku container:push web
heroku container:release web
```

### DigitalOcean App Platform

1. **Create app.yaml:**
```yaml
name: resume-analyzer
services:
- name: api
  source_dir: /
  github:
    repo: your-username/resume-analyzer-ai
    branch: main
  run_command: uvicorn app:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8000
  routes:
  - path: /
```

2. **Deploy via DigitalOcean dashboard or CLI**

## 🚀 Production Considerations

### Environment Variables
```bash
# Production environment variables
export PYTHONPATH=/app
export WORKERS=4
export HOST=0.0.0.0
export PORT=8000
```

### Security
- Use HTTPS in production
- Implement authentication if needed
- Set up proper CORS policies
- Use secrets management for sensitive data

### Monitoring
- Add health checks
- Set up logging
- Monitor resource usage
- Implement metrics collection

### Scaling
- Use load balancers
- Implement horizontal scaling
- Set up auto-scaling policies
- Use container orchestration (Kubernetes)

## 📊 Performance Optimization

### Docker Image Optimization
```dockerfile
# Multi-stage build for smaller images
FROM python:3.12-slim as builder
# ... build dependencies

FROM python:3.12-slim as runtime
# ... copy only necessary files
```

### Application Optimization
- Use production ASGI server (Gunicorn with Uvicorn workers)
- Implement caching
- Optimize model loading
- Use connection pooling

## 🔧 Troubleshooting

### Common Issues

1. **Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

2. **Docker build fails:**
```bash
# Check Docker daemon
docker info
# Clean up Docker
docker system prune -a
```

3. **Container won't start:**
```bash
# Check logs
docker logs resume-analyzer-container
# Check container status
docker ps -a
```

4. **Memory issues:**
```bash
# Increase Docker memory limit
# In Docker Desktop: Settings > Resources > Memory
```

### Health Checks
```bash
# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/
curl http://localhost:8000/skills
```

## 📝 Deployment Checklist

- [ ] Docker image builds successfully
- [ ] Container starts without errors
- [ ] Health endpoint responds
- [ ] API documentation accessible
- [ ] File upload functionality works
- [ ] All endpoints return expected responses
- [ ] Logs are properly configured
- [ ] Environment variables set correctly
- [ ] Security measures implemented
- [ ] Monitoring and alerting configured

## 🆘 Support

For deployment issues:
1. Check the logs: `docker logs <container-name>`
2. Verify environment variables
3. Test endpoints individually
4. Check resource usage (CPU, memory)
5. Review security groups/firewall rules

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [AWS ECS Guide](https://docs.aws.amazon.com/ecs/)
- [Google Cloud Run](https://cloud.google.com/run/docs)
- [Azure Container Instances](https://docs.microsoft.com/en-us/azure/container-instances/)

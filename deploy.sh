#!/bin/bash

# Resume Analyzer Deployment Script
# Supports multiple cloud platforms

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="resume-analyzer"
TAG="latest"

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

show_help() {
    echo "Resume Analyzer Deployment Script"
    echo ""
    echo "Usage: $0 [PLATFORM] [OPTIONS]"
    echo ""
    echo "Platforms:"
    echo "  local     - Build and run locally with Docker"
    echo "  aws       - Deploy to AWS (requires AWS CLI)"
    echo "  gcp       - Deploy to Google Cloud (requires gcloud CLI)"
    echo "  azure     - Deploy to Azure (requires Azure CLI)"
    echo "  heroku    - Deploy to Heroku (requires Heroku CLI)"
    echo ""
    echo "Options:"
    echo "  --help    - Show this help message"
    echo "  --build   - Only build the Docker image"
    echo "  --push    - Build and push to registry"
    echo ""
    echo "Examples:"
    echo "  $0 local"
    echo "  $0 aws --push"
    echo "  $0 gcp"
}

deploy_local() {
    print_info "Deploying locally with Docker..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Build image
    print_info "Building Docker image..."
    docker build -t ${IMAGE_NAME}:${TAG} .
    
    # Stop existing container
    if docker ps -a --format 'table {{.Names}}' | grep -q "^resume-analyzer-container$"; then
        print_warning "Stopping existing container..."
        docker stop resume-analyzer-container > /dev/null 2>&1 || true
        docker rm resume-analyzer-container > /dev/null 2>&1 || true
    fi
    
    # Run container
    print_info "Starting container..."
    docker run -d \
        --name resume-analyzer-container \
        -p 8000:8000 \
        --restart unless-stopped \
        ${IMAGE_NAME}:${TAG}
    
    print_status "Deployed locally! API available at http://localhost:8000"
    print_info "Health check: http://localhost:8000/health"
    print_info "API docs: http://localhost:8000/docs"
}

deploy_aws() {
    print_info "Deploying to AWS..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install AWS CLI first."
        exit 1
    fi
    
    # Get AWS account ID
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    REGION=${AWS_DEFAULT_REGION:-us-east-1}
    ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
    
    print_info "AWS Account ID: ${ACCOUNT_ID}"
    print_info "Region: ${REGION}"
    
    # Create ECR repository if it doesn't exist
    print_info "Creating ECR repository..."
    aws ecr create-repository --repository-name ${IMAGE_NAME} --region ${REGION} 2>/dev/null || print_warning "Repository already exists"
    
    # Login to ECR
    print_info "Logging in to ECR..."
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_URI}
    
    # Build and push image
    print_info "Building and pushing image..."
    docker build -t ${IMAGE_NAME}:${TAG} .
    docker tag ${IMAGE_NAME}:${TAG} ${ECR_URI}/${IMAGE_NAME}:${TAG}
    docker push ${ECR_URI}/${IMAGE_NAME}:${TAG}
    
    print_status "Image pushed to ECR: ${ECR_URI}/${IMAGE_NAME}:${TAG}"
    print_info "You can now deploy this image to ECS, App Runner, or Lambda"
}

deploy_gcp() {
    print_info "Deploying to Google Cloud Platform..."
    
    # Check gcloud CLI
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI not found. Please install Google Cloud SDK first."
        exit 1
    fi
    
    # Get project ID
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        print_error "No Google Cloud project set. Run: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
    
    print_info "Project ID: ${PROJECT_ID}"
    
    # Build and push to Google Container Registry
    print_info "Building and pushing to GCR..."
    gcloud builds submit --tag gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}
    
    print_status "Image pushed to GCR: gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}"
    
    # Deploy to Cloud Run
    print_info "Deploying to Cloud Run..."
    gcloud run deploy ${IMAGE_NAME} \
        --image gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG} \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --port 8000
    
    print_status "Deployed to Cloud Run!"
}

deploy_azure() {
    print_info "Deploying to Azure..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI not found. Please install Azure CLI first."
        exit 1
    fi
    
    # Get subscription and resource group
    SUBSCRIPTION=$(az account show --query id --output tsv)
    RESOURCE_GROUP=${AZURE_RESOURCE_GROUP:-resume-analyzer-rg}
    REGISTRY_NAME=${AZURE_REGISTRY_NAME:-resumeanalyzerregistry}
    
    print_info "Subscription: ${SUBSCRIPTION}"
    print_info "Resource Group: ${RESOURCE_GROUP}"
    
    # Create resource group if it doesn't exist
    az group create --name ${RESOURCE_GROUP} --location eastus 2>/dev/null || print_warning "Resource group already exists"
    
    # Create container registry if it doesn't exist
    az acr create --resource-group ${RESOURCE_GROUP} --name ${REGISTRY_NAME} --sku Basic 2>/dev/null || print_warning "Registry already exists"
    
    # Login to registry
    print_info "Logging in to Azure Container Registry..."
    az acr login --name ${REGISTRY_NAME}
    
    # Build and push image
    print_info "Building and pushing image..."
    az acr build --registry ${REGISTRY_NAME} --image ${IMAGE_NAME}:${TAG} .
    
    print_status "Image pushed to ACR: ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${TAG}"
    print_info "You can now deploy this image to Container Instances or App Service"
}

deploy_heroku() {
    print_info "Deploying to Heroku..."
    
    # Check Heroku CLI
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI not found. Please install Heroku CLI first."
        exit 1
    fi
    
    # Check if logged in to Heroku
    if ! heroku auth:whoami &> /dev/null; then
        print_error "Not logged in to Heroku. Run: heroku login"
        exit 1
    fi
    
    # Create Heroku app if it doesn't exist
    APP_NAME=${HEROKU_APP_NAME:-resume-analyzer-$(date +%s)}
    print_info "App name: ${APP_NAME}"
    
    # Login to Heroku Container Registry
    print_info "Logging in to Heroku Container Registry..."
    heroku container:login
    
    # Build and push image
    print_info "Building and pushing image..."
    heroku container:push web --app ${APP_NAME}
    
    # Release the image
    print_info "Releasing image..."
    heroku container:release web --app ${APP_NAME}
    
    print_status "Deployed to Heroku: https://${APP_NAME}.herokuapp.com"
}

# Main script logic
case "${1:-local}" in
    "local")
        deploy_local
        ;;
    "aws")
        deploy_aws
        ;;
    "gcp")
        deploy_gcp
        ;;
    "azure")
        deploy_azure
        ;;
    "heroku")
        deploy_heroku
        ;;
    "--help"|"-h"|"help")
        show_help
        ;;
    *)
        print_error "Unknown platform: $1"
        show_help
        exit 1
        ;;
esac

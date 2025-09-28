#!/bin/bash

# Resume Analyzer Docker Build Script

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
CONTAINER_NAME="resume-analyzer-container"

echo -e "${BLUE}🐳 Resume Analyzer Docker Build Script${NC}"
echo "=================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running"

# Build the Docker image
echo -e "\n${BLUE}Building Docker image...${NC}"
docker build -t ${IMAGE_NAME}:${TAG} .

if [ $? -eq 0 ]; then
    print_status "Docker image built successfully: ${IMAGE_NAME}:${TAG}"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_warning "Stopping existing container..."
    docker stop ${CONTAINER_NAME} > /dev/null 2>&1 || true
    docker rm ${CONTAINER_NAME} > /dev/null 2>&1 || true
fi

# Run the container
echo -e "\n${BLUE}Starting container...${NC}"
docker run -d \
    --name ${CONTAINER_NAME} \
    -p 8000:8000 \
    --restart unless-stopped \
    ${IMAGE_NAME}:${TAG}

if [ $? -eq 0 ]; then
    print_status "Container started successfully"
    echo -e "\n${BLUE}Container Details:${NC}"
    echo "  Name: ${CONTAINER_NAME}"
    echo "  Image: ${IMAGE_NAME}:${TAG}"
    echo "  Port: 8000"
    echo "  Status: $(docker ps --format 'table {{.Status}}' --filter name=${CONTAINER_NAME} | tail -n +2)"
    
    echo -e "\n${BLUE}API Endpoints:${NC}"
    echo "  Health Check: http://localhost:8000/health"
    echo "  API Docs: http://localhost:8000/docs"
    echo "  Root: http://localhost:8000/"
    
    echo -e "\n${BLUE}Useful Commands:${NC}"
    echo "  View logs: docker logs ${CONTAINER_NAME}"
    echo "  Stop container: docker stop ${CONTAINER_NAME}"
    echo "  Remove container: docker rm ${CONTAINER_NAME}"
    echo "  Shell access: docker exec -it ${CONTAINER_NAME} /bin/bash"
    
    # Wait a moment and test the health endpoint
    echo -e "\n${BLUE}Testing health endpoint...${NC}"
    sleep 5
    
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Health check passed - API is running!"
    else
        print_warning "Health check failed - container might still be starting up"
        echo "Check logs with: docker logs ${CONTAINER_NAME}"
    fi
    
else
    print_error "Failed to start container"
    exit 1
fi

echo -e "\n${GREEN}🎉 Resume Analyzer is now running in Docker!${NC}"

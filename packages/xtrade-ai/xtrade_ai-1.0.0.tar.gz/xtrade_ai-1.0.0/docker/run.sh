#!/bin/bash

# XTrade-AI Framework Docker Run Script
# This script provides easy commands to run different Docker configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_PORT=8000
DEFAULT_IMAGE="xtrade-ai:latest"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if image exists
check_image() {
    local image=$1
    if ! docker images | grep -q "$image"; then
        print_warning "Image $image not found. Building..."
        docker build -f "Dockerfile" -t "$image" .
    fi
}

# Function to run production container
run_production() {
    local port=${1:-$DEFAULT_PORT}
    local image=${2:-$DEFAULT_IMAGE}
    
    print_status "Starting XTrade-AI production container..."
    print_status "Port: $port"
    print_status "Image: $image"
    
    check_image "$image"
    
    docker run -d \
        --name xtrade-ai-prod \
        -p "$port:8000" \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/models:/app/models" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config" \
        -e POSTGRES_HOST=localhost \
        -e POSTGRES_PORT=5432 \
        -e POSTGRES_DB=xtrade_ai \
        -e POSTGRES_USER=xtrade_user \
        -e POSTGRES_PASSWORD=xtrade_password \
        -e REDIS_HOST=localhost \
        -e REDIS_PORT=6379 \
        "$image"
    
    print_success "Production container started on port $port"
    print_status "API available at: http://localhost:$port"
    print_status "Health check: http://localhost:$port/health"
}

# Function to run development container
run_development() {
    local port=${1:-$DEFAULT_PORT}
    local image="xtrade-ai:dev"
    
    print_status "Starting XTrade-AI development container..."
    print_status "Port: $port"
    print_status "Image: $image"
    
    check_image "$image"
    
    docker run -d \
        --name xtrade-ai-dev \
        -p "$port:8000" \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/models:/app/models" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config" \
        -v "$(pwd)/../xtrade_ai:/app/xtrade_ai" \
        -e POSTGRES_HOST=localhost \
        -e POSTGRES_PORT=5432 \
        -e POSTGRES_DB=xtrade_ai \
        -e POSTGRES_USER=xtrade_user \
        -e POSTGRES_PASSWORD=xtrade_password \
        -e REDIS_HOST=localhost \
        -e REDIS_PORT=6379 \
        -e PYTHONPATH=/app \
        "$image"
    
    print_success "Development container started on port $port"
    print_status "API available at: http://localhost:$port"
    print_status "Auto-reload enabled"
}

# Function to run minimal container
run_minimal() {
    local port=${1:-$DEFAULT_PORT}
    local image="xtrade-ai:minimal"
    
    print_status "Starting XTrade-AI minimal container..."
    print_status "Port: $port"
    print_status "Image: $image"
    
    check_image "$image"
    
    docker run -d \
        --name xtrade-ai-minimal \
        -p "$port:8000" \
        --memory=512m \
        --cpus=0.5 \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/models:/app/models" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config" \
        -e POSTGRES_HOST=localhost \
        -e POSTGRES_PORT=5432 \
        -e POSTGRES_DB=xtrade_ai \
        -e POSTGRES_USER=xtrade_user \
        -e POSTGRES_PASSWORD=xtrade_password \
        -e REDIS_HOST=localhost \
        -e REDIS_PORT=6379 \
        "$image"
    
    print_success "Minimal container started on port $port"
    print_status "API available at: http://localhost:$port"
}

# Function to run API-only container
run_api() {
    local port=${1:-$DEFAULT_PORT}
    local image="xtrade-ai:api"
    
    print_status "Starting XTrade-AI API-only container..."
    print_status "Port: $port"
    print_status "Image: $image"
    
    check_image "$image"
    
    docker run -d \
        --name xtrade-ai-api \
        -p "$port:8000" \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/models:/app/models" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config" \
        -e POSTGRES_HOST=localhost \
        -e POSTGRES_PORT=5432 \
        -e POSTGRES_DB=xtrade_ai \
        -e POSTGRES_USER=xtrade_user \
        -e POSTGRES_PASSWORD=xtrade_password \
        -e REDIS_HOST=localhost \
        -e REDIS_PORT=6379 \
        "$image"
    
    print_success "API-only container started on port $port"
    print_status "API available at: http://localhost:$port"
}

# Function to run with docker-compose
run_compose() {
    local profile=${1:-""}
    
    print_status "Starting XTrade-AI with docker-compose..."
    
    if [ -n "$profile" ]; then
        print_status "Profile: $profile"
        docker-compose --profile "$profile" up -d
    else
        docker-compose up -d
    fi
    
    print_success "Docker Compose services started"
    print_status "Services:"
    docker-compose ps
}

# Function to stop containers
stop_containers() {
    print_status "Stopping XTrade-AI containers..."
    
    # Stop individual containers
    docker stop xtrade-ai-prod xtrade-ai-dev xtrade-ai-minimal xtrade-ai-api 2>/dev/null || true
    
    # Stop docker-compose services
    docker-compose down 2>/dev/null || true
    
    print_success "All containers stopped"
}

# Function to remove containers
remove_containers() {
    print_status "Removing XTrade-AI containers..."
    
    # Remove individual containers
    docker rm -f xtrade-ai-prod xtrade-ai-dev xtrade-ai-minimal xtrade-ai-api 2>/dev/null || true
    
    # Remove docker-compose services
    docker-compose down -v 2>/dev/null || true
    
    print_success "All containers removed"
}

# Function to show logs
show_logs() {
    local container=${1:-"xtrade-ai-prod"}
    
    print_status "Showing logs for $container..."
    docker logs -f "$container"
}

# Function to show status
show_status() {
    print_status "XTrade-AI containers status:"
    echo ""
    
    # Show individual containers
    echo "Individual containers:"
    docker ps -a --filter "name=xtrade-ai" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    # Show docker-compose services
    echo "Docker Compose services:"
    docker-compose ps 2>/dev/null || echo "No docker-compose services running"
    echo ""
    
    # Show port usage
    echo "Port usage:"
    netstat -tulpn | grep :8000 || echo "No services on port 8000"
}

# Function to show usage
usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  production [PORT] [IMAGE]  Start production container"
    echo "  development [PORT]         Start development container"
    echo "  minimal [PORT]             Start minimal container"
    echo "  api [PORT]                 Start API-only container"
    echo "  compose [PROFILE]          Start with docker-compose"
    echo "  stop                       Stop all containers"
    echo "  remove                     Remove all containers"
    echo "  logs [CONTAINER]           Show container logs"
    echo "  status                     Show container status"
    echo "  help                       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 production              # Start production on port 8000"
    echo "  $0 production 8080         # Start production on port 8080"
    echo "  $0 development 8001        # Start development on port 8001"
    echo "  $0 compose minimal         # Start with minimal profile"
    echo "  $0 logs xtrade-ai-prod     # Show production logs"
    echo "  $0 status                  # Show all container status"
}

# Main script
main() {
    # Check if Docker is running
    check_docker
    
    # Parse command
    case "${1:-help}" in
        production)
            run_production "${2:-$DEFAULT_PORT}" "${3:-$DEFAULT_IMAGE}"
            ;;
        development)
            run_development "${2:-$DEFAULT_PORT}"
            ;;
        minimal)
            run_minimal "${2:-$DEFAULT_PORT}"
            ;;
        api)
            run_api "${2:-$DEFAULT_PORT}"
            ;;
        compose)
            run_compose "${2:-}"
            ;;
        stop)
            stop_containers
            ;;
        remove)
            remove_containers
            ;;
        logs)
            show_logs "${2:-}"
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            print_error "Unknown command: $1"
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

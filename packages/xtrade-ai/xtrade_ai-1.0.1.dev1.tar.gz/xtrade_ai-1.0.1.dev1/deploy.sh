#!/bin/bash

# XTrade-AI Framework Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Prerequisites check passed."
}

# Function to build and deploy
deploy() {
    local environment=${1:-production}
    
    print_status "Deploying XTrade-AI Framework in $environment mode..."
    
    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose down || true
    
    # Build and start containers
    print_status "Building and starting containers..."
    docker-compose up -d --build
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    print_status "Checking service health..."
    if docker-compose ps | grep -q "Up"; then
        print_status "All services are running successfully!"
    else
        print_error "Some services failed to start. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Function to stop services
stop() {
    print_status "Stopping XTrade-AI Framework services..."
    docker-compose down
    print_status "Services stopped."
}

# Function to restart services
restart() {
    print_status "Restarting XTrade-AI Framework services..."
    docker-compose restart
    print_status "Services restarted."
}

# Function to show logs
logs() {
    print_status "Showing logs..."
    docker-compose logs -f
}

# Function to show status
status() {
    print_status "Service status:"
    docker-compose ps
}

# Function to clean up
cleanup() {
    print_warning "This will remove all containers, volumes, and images. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --rmi all
        docker system prune -f
        print_status "Cleanup completed."
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to show help
show_help() {
    echo "XTrade-AI Framework Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy    - Deploy the framework (default: production)"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  logs      - Show service logs"
    echo "  status    - Show service status"
    echo "  cleanup   - Clean up all containers and images"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy          # Deploy in production mode"
    echo "  $0 stop            # Stop all services"
    echo "  $0 logs            # Show logs"
}

# Main script logic
main() {
    # Check prerequisites
    check_prerequisites
    
    # Parse command line arguments
case "${1:-deploy}" in
        deploy)
            deploy "${2:-production}"
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs
            ;;
        status)
            status
            ;;
        cleanup)
        cleanup
        ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
        exit 1
        ;;
esac
}

# Run main function with all arguments
main "$@"

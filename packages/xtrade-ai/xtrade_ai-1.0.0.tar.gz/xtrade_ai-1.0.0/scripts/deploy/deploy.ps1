# XTrade-AI Framework Deployment Script (PowerShell)
param(
    [Parameter(Position=0)]
    [string]$Command = "deploy",
    
    [Parameter(Position=1)]
    [string]$Environment = "production"
)

# Function to write colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to check if command exists
function Test-Command {
    param([string]$CommandName)
    try {
        Get-Command $CommandName -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    if (-not (Test-Command "docker")) {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    }
    
    if (-not (Test-Command "docker-compose")) {
        Write-Error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    }
    
    Write-Status "Prerequisites check passed."
}

# Function to build and deploy
function Start-Deploy {
    param([string]$Environment)
    
    Write-Status "Deploying XTrade-AI Framework in $Environment mode..."
    
    # Stop existing containers
    Write-Status "Stopping existing containers..."
    try {
        docker-compose down
    }
    catch {
        Write-Warning "No containers to stop or error occurred."
    }
    
    # Build and start containers
    Write-Status "Building and starting containers..."
    docker-compose up -d --build
    
    # Wait for services to be ready
    Write-Status "Waiting for services to be ready..."
    Start-Sleep -Seconds 30
    
    # Check service health
    Write-Status "Checking service health..."
    $status = docker-compose ps
    if ($status -match "Up") {
        Write-Status "All services are running successfully!"
    }
    else {
        Write-Error "Some services failed to start. Check logs with: docker-compose logs"
        exit 1
    }
}

# Function to stop services
function Stop-Services {
    Write-Status "Stopping XTrade-AI Framework services..."
    docker-compose down
    Write-Status "Services stopped."
}

# Function to restart services
function Restart-Services {
    Write-Status "Restarting XTrade-AI Framework services..."
    docker-compose restart
    Write-Status "Services restarted."
}

# Function to show logs
function Show-Logs {
    Write-Status "Showing logs..."
    docker-compose logs -f
}

# Function to show status
function Show-Status {
    Write-Status "Service status:"
    docker-compose ps
}

# Function to clean up
function Start-Cleanup {
    Write-Warning "This will remove all containers, volumes, and images. Are you sure? (y/N)"
    $response = Read-Host
    if ($response -match "^[yY](es)?$") {
        Write-Status "Cleaning up..."
        docker-compose down -v --rmi all
        docker system prune -f
        Write-Status "Cleanup completed."
    }
    else {
        Write-Status "Cleanup cancelled."
    }
}

# Function to show help
function Show-Help {
    Write-Host "XTrade-AI Framework Deployment Script (PowerShell)"
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 [COMMAND] [ENVIRONMENT]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  deploy    - Deploy the framework (default: production)"
    Write-Host "  stop      - Stop all services"
    Write-Host "  restart   - Restart all services"
    Write-Host "  logs      - Show service logs"
    Write-Host "  status    - Show service status"
    Write-Host "  cleanup   - Clean up all containers and images"
    Write-Host "  help      - Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy.ps1 deploy          # Deploy in production mode"
    Write-Host "  .\deploy.ps1 stop            # Stop all services"
    Write-Host "  .\deploy.ps1 logs            # Show logs"
}

# Main script logic
function Main {
    param([string]$Command, [string]$Environment)
    
    # Check prerequisites
    Test-Prerequisites
    
    # Parse command line arguments
    switch ($Command.ToLower()) {
        "deploy" {
            Start-Deploy $Environment
        }
        "stop" {
            Stop-Services
        }
        "restart" {
            Restart-Services
        }
        "logs" {
            Show-Logs
        }
        "status" {
            Show-Status
        }
        "cleanup" {
            Start-Cleanup
        }
        "help" {
            Show-Help
        }
        default {
            Write-Error "Unknown command: $Command"
            Show-Help
            exit 1
        }
    }
}

# Run main function
Main -Command $Command -Environment $Environment

#!/bin/bash
# Enhanced Document AI Multi-Agent Assistant - Deployment Script
# Automated deployment script with environment detection and safety checks

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="enhanced-document-ai"
APP_PORT=7860
MIN_PYTHON_VERSION="3.8"
REQUIRED_MEMORY_GB=4
LOG_FILE="deployment.log"

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

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Function to check system requirements
check_system_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python $PYTHON_VERSION found (>= $MIN_PYTHON_VERSION)"
        else
            print_error "Python $PYTHON_VERSION found, but $MIN_PYTHON_VERSION or higher is required"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python $MIN_PYTHON_VERSION or higher"
        exit 1
    fi
    
    # Check available memory
    if command -v free &> /dev/null; then
        AVAILABLE_MEMORY_KB=$(free | awk '/^Mem:/{print $7}')
        AVAILABLE_MEMORY_GB=$((AVAILABLE_MEMORY_KB / 1024 / 1024))
        if [ "$AVAILABLE_MEMORY_GB" -ge "$REQUIRED_MEMORY_GB" ]; then
            print_success "Available memory: ${AVAILABLE_MEMORY_GB}GB (>= ${REQUIRED_MEMORY_GB}GB)"
        else
            print_warning "Available memory: ${AVAILABLE_MEMORY_GB}GB (recommended: >= ${REQUIRED_MEMORY_GB}GB)"
        fi
    fi
    
    # Check disk space
    AVAILABLE_DISK_GB=$(df -BG . | awk 'NR==2 {gsub(/G/, "", $4); print $4}')
    if [ "$AVAILABLE_DISK_GB" -ge 2 ]; then
        print_success "Available disk space: ${AVAILABLE_DISK_GB}GB"
    else
        print_error "Insufficient disk space: ${AVAILABLE_DISK_GB}GB (minimum 2GB required)"
        exit 1
    fi
}

# Function to detect deployment environment
detect_environment() {
    print_status "Detecting deployment environment..."
    
    if [ -f /.dockerenv ]; then
        ENVIRONMENT="docker"
        print_success "Docker environment detected"
    elif [ -n "${KUBERNETES_SERVICE_HOST:-}" ]; then
        ENVIRONMENT="kubernetes"
        print_success "Kubernetes environment detected"
    elif [ -n "${AWS_LAMBDA_RUNTIME_API:-}" ]; then
        ENVIRONMENT="aws_lambda"
        print_success "AWS Lambda environment detected"
    elif [ -n "${GOOGLE_CLOUD_PROJECT:-}" ]; then
        ENVIRONMENT="gcp"
        print_success "Google Cloud Platform environment detected"
    elif [ -n "${WEBSITE_SITE_NAME:-}" ]; then
        ENVIRONMENT="azure"
        print_success "Azure environment detected"
    else
        ENVIRONMENT="local"
        print_success "Local development environment detected"
    fi
}

# Function to check port availability
check_port_availability() {
    print_status "Checking port $APP_PORT availability..."
    
    if lsof -Pi :$APP_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Port $APP_PORT is already in use"
        print_status "Attempting to find alternative port..."
        
        # Find available port
        for port in {7861..7870}; do
            if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                APP_PORT=$port
                print_success "Alternative port found: $APP_PORT"
                export SERVER_PORT=$APP_PORT
                break
            fi
        done
        
        if lsof -Pi :$APP_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_error "No available ports found in range 7860-7870"
            exit 1
        fi
    else
        print_success "Port $APP_PORT is available"
    fi
}

# Function to setup Python environment
setup_python_environment() {
    print_status "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install requirements
    if [ -f "requirements_enhanced.txt" ]; then
        print_status "Installing enhanced requirements..."
        pip install -r requirements_enhanced.txt
    elif [ -f "requirements.txt" ]; then
        print_status "Installing standard requirements..."
        pip install -r requirements.txt
    else
        print_error "No requirements file found"
        exit 1
    fi
    
    print_success "Python dependencies installed"
}

# Function to validate environment variables
validate_environment_variables() {
    print_status "Validating environment variables..."
    
    # Check for required environment variables
    if [ -f ".env" ]; then
        source .env
        print_success "Environment file loaded"
    else
        print_warning "No .env file found"
    fi
    
    # Required variables
    REQUIRED_VARS=("GEMINI_API_KEY")
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var:-}" ]; then
            print_error "Required environment variable $var is not set"
            print_status "Please set $var in your .env file or environment"
            exit 1
        else
            print_success "$var is configured"
        fi
    done
    
    # Optional variables with defaults
    export MAX_FILE_SIZE="${MAX_FILE_SIZE:-52428800}"  # 50MB
    export RATE_LIMIT_REQUESTS="${RATE_LIMIT_REQUESTS:-100}"
    export LOG_LEVEL="${LOG_LEVEL:-INFO}"
    export SERVER_HOST="${SERVER_HOST:-0.0.0.0}"
    export SERVER_PORT="${SERVER_PORT:-$APP_PORT}"
    
    print_success "Environment variables validated"
}

# Function to run pre-deployment tests
run_pre_deployment_tests() {
    print_status "Running pre-deployment tests..."
    
    if [ -f "test_agents.py" ]; then
        python3 test_agents.py
        if [ $? -eq 0 ]; then
            print_success "Pre-deployment tests passed"
        else
            print_error "Pre-deployment tests failed"
            read -p "Continue deployment anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    else
        print_warning "No test file found, skipping tests"
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    REQUIRED_DIRS=("logs" "data" "metadata_exports" "state" "cache")
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        else
            print_status "Directory already exists: $dir"
        fi
    done
}

# Function to setup logging
setup_logging() {
    print_status "Setting up logging..."
    
    # Create log rotation script
    cat > rotate_logs.sh << 'EOF'
#!/bin/bash
# Log rotation script for Enhanced Document AI

LOG_DIR="logs"
MAX_SIZE=100M
MAX_FILES=10

find "$LOG_DIR" -name "*.log" -size +$MAX_SIZE -exec sh -c '
    for file; do
        base=$(basename "$file" .log)
        mv "$file" "$LOG_DIR/${base}_$(date +%Y%m%d_%H%M%S).log"
        touch "$file"
    done
' sh {} +

# Keep only the most recent log files
find "$LOG_DIR" -name "*_*.log" -type f -exec ls -t {} + | tail -n +$((MAX_FILES + 1)) | xargs -r rm
EOF
    
    chmod +x rotate_logs.sh
    print_success "Log rotation script created"
}

# Function to setup systemd service (Linux only)
setup_systemd_service() {
    if [[ "$OSTYPE" == "linux-gnu"* ]] && command -v systemctl &> /dev/null; then
        print_status "Setting up systemd service..."
        
        SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"
        CURRENT_DIR=$(pwd)
        CURRENT_USER=$(whoami)
        
        if [ "$EUID" -eq 0 ]; then
            cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Enhanced Document AI Multi-Agent Assistant
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/python enhanced_ui.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$APP_NAME

[Install]
WantedBy=multi-user.target
EOF
            
            systemctl daemon-reload
            systemctl enable "$APP_NAME"
            print_success "Systemd service created and enabled"
        else
            print_warning "Root access required for systemd service setup"
            print_status "You can run 'sudo $0' to setup systemd service"
        fi
    fi
}

# Function to start the application
start_application() {
    print_status "Starting Enhanced Document AI Assistant..."
    
    case $ENVIRONMENT in
        "docker")
            print_status "Application should be started by Docker"
            ;;
        "kubernetes")
            print_status "Application should be started by Kubernetes"
            ;;
        *)
            # For local and other environments
            if command -v systemctl &> /dev/null && systemctl is-enabled "${APP_NAME}" &> /dev/null; then
                # Use systemd if service is available
                systemctl start "$APP_NAME"
                print_success "Application started via systemd"
                print_status "View logs: journalctl -u $APP_NAME -f"
            else
                # Direct execution
                print_status "Starting application directly..."
                source venv/bin/activate
                
                # Start in background for deployment script
                nohup python3 enhanced_ui.py > logs/app.log 2>&1 &
                APP_PID=$!
                echo $APP_PID > app.pid
                
                # Wait a moment and check if process is running
                sleep 3
                if kill -0 $APP_PID 2>/dev/null; then
                    print_success "Application started successfully (PID: $APP_PID)"
                    print_success "Access the application at: http://localhost:$APP_PORT"
                    print_status "View logs: tail -f logs/app.log"
                    print_status "Stop application: kill $APP_PID"
                else
                    print_error "Application failed to start"
                    exit 1
                fi
            fi
            ;;
    esac
}

# Function to perform health check
perform_health_check() {
    print_status "Performing health check..."
    
    # Wait for application to start
    sleep 5
    
    # Check if port is responding
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "http://localhost:$APP_PORT/health" > /dev/null 2>&1; then
            print_success "Health check passed"
            return 0
        fi
        
        print_status "Health check attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    print_error "Health check failed after $max_attempts attempts"
    return 1
}

# Function to create monitoring scripts
create_monitoring_scripts() {
    print_status "Creating monitoring scripts..."
    
    # Process monitor script
    cat > monitor.sh << 'EOF'
#!/bin/bash
# Process monitoring script

APP_NAME="enhanced-document-ai"
PID_FILE="app.pid"

check_process() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "✓ Application is running (PID: $PID)"
            return 0
        else
            echo "✗ Application is not running (stale PID file)"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo "✗ Application is not running (no PID file)"
        return 1
    fi
}

restart_process() {
    echo "Attempting to restart application..."
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        kill "$PID" 2>/dev/null
        sleep 3
    fi
    
    nohup python3 enhanced_ui.py > logs/app.log 2>&1 &
    NEW_PID=$!
    echo $NEW_PID > "$PID_FILE"
    echo "Application restarted (PID: $NEW_PID)"
}

case "${1:-check}" in
    "check")
        check_process
        ;;
    "restart")
        restart_process
        ;;
    *)
        echo "Usage: $0 {check|restart}"
        exit 1
        ;;
esac
EOF
    
    chmod +x monitor.sh
    print_success "Process monitoring script created"
    
    # Log analyzer script
    cat > analyze_logs.sh << 'EOF'
#!/bin/bash
# Log analysis script

LOG_FILE="logs/app.log"
ERROR_LOG="logs/errors.log"

echo "=== Enhanced Document AI - Log Analysis ==="
echo "Date: $(date)"
echo

if [ -f "$LOG_FILE" ]; then
    echo "📊 Log Statistics:"
    echo "Total lines: $(wc -l < "$LOG_FILE")"
    echo "Size: $(du -h "$LOG_FILE" | cut -f1)"
    echo
    
    echo "🔍 Recent Activity (last 20 lines):"
    tail -n 20 "$LOG_FILE"
    echo
fi

if [ -f "$ERROR_LOG" ]; then
    ERROR_COUNT=$(wc -l < "$ERROR_LOG")
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "❌ Recent Errors:"
        tail -n 10 "$ERROR_LOG"
        echo
    else
        echo "✅ No recent errors"
    fi
fi

echo "💾 System Resources:"
echo "Memory usage: $(free -h | awk '/^Mem:/{print $3 "/" $2}')"
echo "Disk usage: $(df -h . | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
EOF
    
    chmod +x analyze_logs.sh
    print_success "Log analysis script created"
}

# Function to display deployment summary
display_deployment_summary() {
    print_success "=== Deployment Summary ==="
    echo
    print_status "Application: Enhanced Document AI Multi-Agent Assistant"
    print_status "Environment: $ENVIRONMENT"
    print_status "Python Version: $PYTHON_VERSION"
    print_status "Port: $APP_PORT"
    print_status "Log Level: $LOG_LEVEL"
    echo
    print_success "🚀 Application URL: http://localhost:$APP_PORT"
    print_success "📊 Health Check: http://localhost:$APP_PORT/health"
    print_success "📈 Metrics: http://localhost:$APP_PORT/metrics"
    echo
    print_status "📁 Important Files:"
    echo "   • Logs: logs/app.log, logs/errors.log"
    echo "   • Configuration: .env"
    echo "   • Process ID: app.pid"
    echo "   • State: state/"
    echo
    print_status "🔧 Management Commands:"
    echo "   • Monitor: ./monitor.sh check"
    echo "   • Restart: ./monitor.sh restart"
    echo "   • Analyze logs: ./analyze_logs.sh"
    echo "   • Rotate logs: ./rotate_logs.sh"
    echo
    if command -v systemctl &> /dev/null && systemctl is-enabled "${APP_NAME}" &> /dev/null 2>&1; then
        print_status "🔄 Systemd Commands:"
        echo "   • Status: sudo systemctl status $APP_NAME"
        echo "   • Stop: sudo systemctl stop $APP_NAME"
        echo "   • Start: sudo systemctl start $APP_NAME"
        echo "   • Logs: journalctl -u $APP_NAME -f"
        echo
    fi
}

# Main deployment function
main() {
    print_success "🚀 Enhanced Document AI Assistant - Deployment Script"
    print_status "Starting deployment process..."
    echo
    
    # Log start of deployment
    log_message "Starting deployment process"
    
    # Run all deployment steps
    detect_environment
    check_system_requirements
    check_port_availability
    setup_python_environment
    validate_environment_variables
    create_directories
    setup_logging
    run_pre_deployment_tests
    
    # Environment-specific setup
    if [ "$ENVIRONMENT" = "local" ]; then
        setup_systemd_service
    fi
    
    create_monitoring_scripts
    start_application
    
    # Health check (skip for Docker as it has its own health check)
    if [ "$ENVIRONMENT" != "docker" ]; then
        if perform_health_check; then
            log_message "Deployment completed successfully"
            display_deployment_summary
        else
            print_error "Deployment completed but health check failed"
            print_status "Check logs for details: tail -f logs/app.log"
            log_message "Deployment completed with health check failure"
        fi
    else
        log_message "Deployment completed (Docker environment)"
        print_success "Deployment completed for Docker environment"
    fi
}

# Handle script interruption
trap 'print_error "Deployment interrupted"; exit 1' INT TERM

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Run main function
main "$@"
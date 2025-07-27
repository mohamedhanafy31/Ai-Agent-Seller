#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=${4:-30}
    local attempt=1

    log_info "Waiting for $service_name at $host:$port..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            log_info "$service_name is ready!"
            return 0
        fi
        
        log_warn "Attempt $attempt/$max_attempts: $service_name not ready, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "$service_name failed to become ready after $max_attempts attempts"
    return 1
}

# Function to wait for Ollama API
wait_for_ollama() {
    local max_attempts=${1:-30}
    local attempt=1
    
    log_info "Waiting for Ollama API..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "${OLLAMA_ENDPOINT%/api/generate}/api/tags" >/dev/null 2>&1; then
            log_info "Ollama API is ready!"
            return 0
        fi
        
        log_warn "Attempt $attempt/$max_attempts: Ollama API not ready, waiting..."
        sleep 3
        attempt=$((attempt + 1))
    done
    
    log_error "Ollama API failed to become ready after $max_attempts attempts"
    return 1
}

# Function to check GPU availability
check_gpu() {
    if command -v nvidia-smi >/dev/null 2>&1; then
        if nvidia-smi >/dev/null 2>&1; then
            log_info "GPU detected and available"
            export USE_GPU="true"
            nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits
        else
            log_warn "GPU drivers detected but GPU not accessible"
            export USE_GPU="false"
        fi
    else
        log_info "No GPU detected, using CPU"
        export USE_GPU="false"
    fi
}

# Function to validate environment variables
validate_env() {
    local required_vars=(
        "POSTGRES_SERVER"
        "POSTGRES_PORT" 
        "POSTGRES_DB"
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "REDIS_HOST"
        "REDIS_PORT"
        "OLLAMA_ENDPOINT"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    log_info "All required environment variables are present"
}

# Function to create required directories
create_directories() {
    local dirs=(
        "/app/models"
        "/app/uploads" 
        "/app/uploads/audio"
        "/app/uploads/images" 
        "/app/uploads/videos"
        "/app/cache"
        "/app/logs"
        "/app/temp"
        "/app/assets/models"
        "/app/assets/cache"
        "/app/assets/audio"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        fi
    done
}

# Function to run database migrations
run_migrations() {
    log_info "Running database migrations..."
    if python -c "
import sys
sys.path.append('/app')
from alembic.config import Config
from alembic import command
try:
    alembic_cfg = Config('/app/alembic.ini')
    command.upgrade(alembic_cfg, 'head')
    print('Migrations completed successfully')
except Exception as e:
    print(f'Migration failed: {e}')
    sys.exit(1)
"; then
        log_info "Database migrations completed successfully"
    else
        log_error "Database migrations failed"
        exit 1
    fi
}

# Function to pre-download models
preload_models() {
    log_info "Checking and preloading AI models..."
    python -c "
import sys
sys.path.append('/app')
try:
    from app.services.model_manager import ModelManager
    import asyncio
    
    async def preload():
        manager = ModelManager()
        await manager.initialize()
        print('Models preloaded successfully')
    
    asyncio.run(preload())
except Exception as e:
    print(f'Model preloading failed: {e}')
    # Don't exit - models can be loaded on first request
" || log_warn "Model preloading failed, will load on first request"
}

# Main execution
main() {
    log_info "Starting AI Agent Seller Backend..."
    
    # Activate conda environment
    source /opt/conda/etc/profile.d/conda.sh
    conda activate ai_seller
    
    # Validate environment
    validate_env
    
    # Check GPU
    check_gpu
    
    # Create directories
    create_directories
    
    # Wait for dependencies
    wait_for_service "$POSTGRES_SERVER" "$POSTGRES_PORT" "PostgreSQL"
    wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
    wait_for_ollama
    
    # Run migrations (optional - comment out if not using Alembic)
    # run_migrations
    
    # Preload models (optional - for faster first response)
    if [ "${PRELOAD_MODELS:-false}" = "true" ]; then
        preload_models
    fi
    
    log_info "All dependencies ready, starting application..."
    
    # Execute the main command
    exec "$@"
}

# Handle signals gracefully
trap 'log_info "Shutting down gracefully..."; exit 0' SIGTERM SIGINT

# Run main function
main
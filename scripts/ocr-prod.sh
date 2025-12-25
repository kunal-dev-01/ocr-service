#!/bin/bash
# ============================================================================
# FILE: scripts/ocr-prod.sh
# PURPOSE: OCR Service production environment management (Separate VM)
# ============================================================================

set -e

COMPOSE_FILE="docker-compose.ocr.prod.yml"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}ℹ $1${NC}"; }

# Check .env.production exists
check_env_file() {
    if [ ! -f "services/ocr-service/.env.production" ]; then
        print_error ".env.production not found!"
        print_info "Please create services/ocr-service/.env.production before deploying"
        print_info "Make sure REDIS_URL points to Main Server IP"
        exit 1
    fi
}

# Start
ocr_prod_start() {
    print_info "Starting OCR service (production)..."
    
    # Check .env.production
    check_env_file
    
    docker-compose -f $COMPOSE_FILE up -d --build
    print_success "OCR production started!"
    print_info "Service: http://localhost:8004"
    print_info "Health check: http://localhost:8004/health"
    print_info ""
    print_info "Connected to Main Server Redis:"
    REDIS_URL=$(grep REDIS_URL services/ocr-service/.env.production | cut -d'=' -f2)
    print_info "  Redis: $REDIS_URL"
}

# Stop
ocr_prod_stop() {
    print_info "Stopping OCR service..."
    docker-compose -f $COMPOSE_FILE down
    print_success "Stopped!"
}

# Restart
ocr_prod_restart() {
    print_info "Restarting OCR service..."
    docker-compose -f $COMPOSE_FILE restart
    print_success "Restarted!"
}

# Logs
ocr_prod_logs() {
    print_info "Showing OCR service logs (Ctrl+C to exit)..."
    docker-compose -f $COMPOSE_FILE logs -f --tail=100
}

# Rebuild
ocr_prod_rebuild() {
    print_info "Rebuilding OCR service..."
    check_env_file
    docker-compose -f $COMPOSE_FILE down
    docker-compose -f $COMPOSE_FILE build --no-cache
    docker-compose -f $COMPOSE_FILE up -d
    print_success "Rebuilt!"
}

# Status
ocr_prod_status() {
    print_info "OCR Service Status:"
    docker-compose -f $COMPOSE_FILE ps
    echo ""
    print_info "Resource usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" zemrev_ocr_prod 2>/dev/null || docker stats --no-stream
}

# Health check
ocr_prod_health() {
    print_info "Checking OCR service health..."
    
    if curl -sf http://localhost:8004/health > /dev/null 2>&1; then
        print_success "OCR Service: healthy"
        
        # Show detailed health
        HEALTH=$(curl -s http://localhost:8004/health)
        echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
        echo ""
        
        # Check Redis connection
        if echo "$HEALTH" | grep -q "connected"; then
            print_success "Redis: connected to Main Server"
        else
            print_error "Redis: connection issue"
        fi
    else
        print_error "OCR Service: unhealthy"
    fi
}

# Queue status
ocr_prod_queue() {
    print_info "Getting queue information..."
    
    HEALTH=$(curl -s http://localhost:8004/health 2>/dev/null)
    QUEUE_SIZE=$(echo "$HEALTH" | python3 -c "import sys, json; print(json.load(sys.stdin).get('queue_size', 'N/A'))" 2>/dev/null)
    WORKERS=$(echo "$HEALTH" | python3 -c "import sys, json; print(json.load(sys.stdin).get('workers', 'N/A'))" 2>/dev/null)
    
    print_info "OCR Service Queue Status:"
    print_info "  Pending jobs: $QUEUE_SIZE"
    print_info "  Active workers: $WORKERS"
}

# Clean
ocr_prod_clean() {
    read -p "Remove all containers and volumes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning..."
        docker-compose -f $COMPOSE_FILE down -v
        docker system prune -f
        print_success "Cleaned!"
    fi
}

# Service info
ocr_prod_info() {
    print_info "OCR Service Information:"
    
    INFO=$(curl -s http://localhost:8004/ 2>/dev/null)
    echo "$INFO" | python3 -m json.tool 2>/dev/null || echo "$INFO"
}

# Main
case "${1:-start}" in
    start) ocr_prod_start ;;
    stop) ocr_prod_stop ;;
    clean) ocr_prod_clean ;;
    restart) ocr_prod_restart ;;
    logs) ocr_prod_logs ;;
    rebuild) ocr_prod_rebuild ;;
    status) ocr_prod_status ;;
    health) ocr_prod_health ;;
    queue) ocr_prod_queue ;;
    info) ocr_prod_info ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|rebuild|status|health|queue|info}"
        echo ""
        echo "Examples:"
        echo "  $0 start               # Start OCR service"
        echo "  $0 stop                # Stop OCR service"
        echo "  $0 restart             # Restart service"
        echo "  $0 logs                # Show logs"
        echo "  $0 health              # Health check"
        echo "  $0 queue               # Queue status"
        echo "  $0 status              # Container status"
        echo "  $0 info                # Service information"
        echo "  $0 rebuild             # Rebuild from scratch"
        echo ""
        echo "Setup:"
        echo "  1. Copy services/ocr-service/ to OCR VM"
        echo "  2. Update .env.production with Main Server Redis IP"
        echo "  3. Run: $0 start"
        exit 1
        ;;
esac
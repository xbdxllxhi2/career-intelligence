#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Internships Helper Deployment Script ===${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file with defaults...${NC}"
    cat > .env << 'EOF'
POSTGRES_USER=internships
POSTGRES_PASSWORD=internships_secret
POSTGRES_DB=internships_db
SECRET_KEY=change-this-in-production
ALLOWED_ORIGINS=*
BACKEND_PORT=8000
FRONTEND_PORT=3000
AIRFLOW_USER=admin
AIRFLOW_PASSWORD=admin
EOF
    echo -e "${GREEN}.env file created. Please review and update values.${NC}"
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Function to generate Fernet key for Airflow
generate_fernet_key() {
    python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || \
    openssl rand -base64 32
}

# Check if Fernet key is set
if [ -z "$AIRFLOW_FERNET_KEY" ]; then
    echo -e "${YELLOW}Generating Airflow Fernet key...${NC}"
    FERNET_KEY=$(generate_fernet_key)
    echo "AIRFLOW_FERNET_KEY=$FERNET_KEY" >> .env
    export AIRFLOW_FERNET_KEY=$FERNET_KEY
    echo -e "${GREEN}Fernet key generated and added to .env${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p data-aggregator/dags
mkdir -p data-aggregator/logs
mkdir -p data-aggregator/plugins

# Set permissions for Airflow
chmod -R 777 data-aggregator/logs 2>/dev/null || true

# Build custom images
echo -e "${YELLOW}Building application images...${NC}"
docker compose build

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker compose down || true

# Start database first
echo -e "${YELLOW}Starting database...${NC}"
docker compose up -d postgres redis
echo "Waiting for database to initialize..."
sleep 10

# Wait for database to be ready
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
until docker compose exec -T postgres pg_isready -U ${POSTGRES_USER:-internships} 2>/dev/null; do
    echo "Waiting for PostgreSQL..."
    sleep 3
done
echo -e "${GREEN}Database is ready!${NC}"

# Run backend database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
docker compose run --rm backend alembic upgrade head 2>/dev/null || echo "No migrations to run or alembic not configured"

# Start all services
echo -e "${YELLOW}Starting all services...${NC}"
docker compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 15

# Check service status
echo -e "${GREEN}=== Service Status ===${NC}"
docker compose ps

# Show logs if any service failed
FAILED=$(docker compose ps --filter "status=exited" -q 2>/dev/null)
if [ ! -z "$FAILED" ]; then
    echo -e "${RED}Some services failed to start. Showing logs:${NC}"
    docker compose logs --tail=50
fi

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "Exposed services:"
echo "  - Frontend: http://localhost:${FRONTEND_PORT:-3000}"
echo "  - Backend API: http://localhost:${BACKEND_PORT:-8000}"
echo ""
echo "Internal services (not exposed):"
echo "  - Airflow, PostgreSQL, Redis"
echo ""
echo "Configure your downstream nginx to proxy:"
echo "  - Frontend -> localhost:${FRONTEND_PORT:-3000}"
echo "  - Backend  -> localhost:${BACKEND_PORT:-8000}"

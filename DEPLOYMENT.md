# Deployment Guide - Internships Helper

Containerized deployment for Frontend, Backend, and Airflow data-aggregator.

## Architecture

```
                         ┌─────────────────────┐
                         │   Internet/Users    │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │  Downstream Nginx   │
                         │   (SSL/Routing)     │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┴─────────────────────┐
              │                                           │
              ▼                                           ▼
┌─────────────────────────┐              ┌─────────────────────────┐
│  Frontend (Angular)     │              │  Backend (FastAPI)      │
│  Port: 3000 (exposed)   │              │  Port: 8000 (exposed)   │
└─────────────────────────┘              └───────────┬─────────────┘
                                                     │
                         ┌───────────────────────────┼───────────────┐
                         │                           │               │
                         ▼                           ▼               ▼
              ┌─────────────────┐         ┌─────────────────┐  ┌──────────┐
              │  Airflow        │         │  PostgreSQL     │  │  Redis   │
              │  (internal)     │         │  (internal)     │  │(internal)│
              └─────────────────┘         └─────────────────┘  └──────────┘
```

## Prerequisites

- Docker & Docker Compose installed
- Downstream nginx server configured for routing

## Quick Start

### 1. Configure Environment

```bash
# The deploy script creates a default .env if missing
# Or create it manually:
cat > .env << 'EOF'
POSTGRES_USER=internships
POSTGRES_PASSWORD=your-strong-password
POSTGRES_DB=internships_db
SECRET_KEY=your-secret-key-32-chars
ALLOWED_ORIGINS=*
BACKEND_PORT=8000
FRONTEND_PORT=3000
AIRFLOW_USER=admin
AIRFLOW_PASSWORD=your-airflow-password
EOF
```

### 2. Deploy

```bash
chmod +x deploy.sh
./deploy.sh
```

## Exposed Services

| Service  | Port | Purpose |
|----------|------|---------|
| Frontend | 3000 | Angular SPA |
| Backend  | 8000 | FastAPI REST API |

## Internal Services (not exposed)

| Service    | Purpose |
|------------|---------|
| Airflow    | Data aggregation pipelines |
| PostgreSQL | Database |
| Redis      | Cache/Queue |

## Downstream Nginx Configuration

Add to your nginx config:

```nginx
# Frontend
location / {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# Backend API
location /api/ {
    proxy_pass http://localhost:8000/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Useful Commands

### Logs
```bash
docker compose logs -f              # All services
docker compose logs -f backend      # Specific service
```

### Restart
```bash
docker compose restart
docker compose restart backend      # Specific service
```

### Update & Redeploy
```bash
git pull
docker compose build --no-cache
docker compose up -d
```

### Database
```bash
# Access PostgreSQL
docker compose exec postgres psql -U internships -d internships_db

# Run migrations
docker compose exec backend alembic upgrade head
```

## Backup & Restore

```bash
# Backup
docker compose exec postgres pg_dump -U internships internships_db > backup.sql

# Restore
docker compose exec -T postgres psql -U internships -d internships_db < backup.sql
```

## Troubleshooting

```bash
# Check status
docker compose ps

# Check logs for failures
docker compose logs --tail=50

# Restart everything
docker compose down && docker compose up -d
```

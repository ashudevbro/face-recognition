# Docker Setup Guide

## Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Services

The Docker Compose setup includes:

1. **PostgreSQL** (port 5432)
   - Database: `face_recognition`
   - User: `faceuser`
   - Password: `facepass`

2. **Backend** (port 8000)
   - FastAPI application
   - Uses `uv` for fast Python package management
   - Auto-reload enabled for development

3. **Frontend** (port 3000)
   - React + Vite development server
   - Hot module replacement enabled

## Volumes

- `postgres_data`: Persistent PostgreSQL data
- `./backend/database`: Face images database (persisted on host)
- `./backend:/app`: Backend code (for hot reload)
- `./frontend:/app`: Frontend code (for hot reload)

## Environment Variables

You can customize the setup by creating a `.env` file:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://faceuser:facepass@postgres:5432/face_recognition
```

## Common Commands

### Using Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Start with logs
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Execute command in container
docker-compose exec backend bash
docker-compose exec postgres psql -U faceuser -d face_recognition
```

### Using Makefile

```bash
make build          # Build all images
make up             # Start all services
make up-logs        # Start with logs
make down           # Stop all services
make logs           # View all logs
make logs-backend   # View backend logs only
make logs-frontend  # View frontend logs only
make restart        # Restart all services
make clean          # Remove all containers and volumes
make rebuild        # Rebuild and restart
make backend-shell  # Access backend container
make db-shell       # Access PostgreSQL shell
```

## Troubleshooting

### Database Connection Issues

If the backend can't connect to the database:

1. Check if PostgreSQL is healthy:
```bash
docker-compose ps
```

2. Check database logs:
```bash
docker-compose logs postgres
```

3. Wait for database to be ready (healthcheck should handle this)

### Port Conflicts

If ports 3000, 8000, or 5432 are already in use:

1. Edit `docker-compose.yml` and change port mappings:
```yaml
ports:
  - "3001:3000"  # Change host port
```

### Rebuild After Code Changes

If you make significant changes to dependencies:

```bash
docker-compose build --no-cache
docker-compose up -d
```

### View Database

```bash
# Using Makefile
make db-shell

# Or directly
docker-compose exec postgres psql -U faceuser -d face_recognition
```

### Clear Everything

```bash
# Remove all containers, volumes, and networks
docker-compose down -v
docker system prune -f
```

## Development Workflow

1. Start services: `docker-compose up -d`
2. Make code changes (hot reload enabled)
3. View logs: `docker-compose logs -f backend`
4. Test in browser: http://localhost:3000
5. Stop when done: `docker-compose down`

## Production Considerations

For production deployment:

1. Remove `--reload` flag from backend command
2. Build frontend for production:
   - Update frontend Dockerfile to build static files
   - Serve with nginx
3. Use environment variables for secrets
4. Set up proper SSL/TLS
5. Configure proper database backups
6. Use docker-compose.prod.yml for production config


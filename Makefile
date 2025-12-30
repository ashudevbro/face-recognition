.PHONY: build up down logs restart clean

# Build all services
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Start all services with logs
up-logs:
	docker-compose up

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Restart all services
restart:
	docker-compose restart

# Stop and remove all containers, volumes
clean:
	docker-compose down -v
	docker system prune -f

# Rebuild and start
rebuild:
	docker-compose up -d --build

# Backend logs only
logs-backend:
	docker-compose logs -f backend

# Frontend logs only
logs-frontend:
	docker-compose logs -f frontend

# Database logs only
logs-db:
	docker-compose logs -f postgres

# Access backend shell
backend-shell:
	docker-compose exec backend /bin/bash

# Access database
db-shell:
	docker-compose exec postgres psql -U faceuser -d face_recognition


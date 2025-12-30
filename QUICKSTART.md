# Quick Start Guide

## Option 1: Docker Compose (Recommended)

### Prerequisites
- Docker
- Docker Compose

### Steps

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

That's it! All services (PostgreSQL, Backend, Frontend) will start automatically.

### Using Makefile

```bash
make up          # Start services
make logs        # View logs
make down        # Stop services
make rebuild     # Rebuild and restart
```

## Option 2: Manual Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL
- uv (Python package installer)

### 1. Backend Setup

```bash
cd backend
./setup.sh
# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb face_recognition

# Or using psql:
psql -U postgres
CREATE DATABASE face_recognition;
```

### 3. Configure Environment

Edit `backend/.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/face_recognition
```

### 4. Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Open http://localhost:3000 in your browser
2. Add persons to database:
   - Enter name
   - Select image
   - Click "Upload & Add Person"
3. Click "Start Camera" to begin recognition
4. View detections:
   - Green boxes = Known faces
   - Red boxes = Unknown faces
   - Blue boxes = Objects

## Notes

- First run will download YOLOv8 model automatically
- Camera permissions required in browser
- Multiple images per person improve accuracy


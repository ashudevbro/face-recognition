# Face Recognition System

A real-time face recognition system with object detection capabilities, built with React frontend and Python FastAPI backend.

> 📖 **For detailed technical documentation**, see [TECHNICAL.md](./TECHNICAL.md)

## Features

- **Real-time Face Recognition**: Detect and recognize faces from camera feed
- **Object Detection**: Detect objects using YOLOv8 pre-trained model
- **Person Management**: Add persons to database by uploading images
- **Visual Feedback**: 
  - Green boxes for recognized faces
  - Red boxes for unknown faces
  - Blue boxes for detected objects

## Tech Stack

### Backend
- FastAPI
- OpenCV
- face_recognition library
- YOLOv8 (Ultralytics)
- PostgreSQL
- SQLAlchemy

### Frontend
- React
- Vite
- Axios

## Quick Start with Docker Compose (Recommended)

The easiest way to run the application is using Docker Compose:

### Prerequisites
- Docker
- Docker Compose

### Steps

1. **Start all services:**
```bash
docker-compose up -d
```

Or use the Makefile:
```bash
make up
```

2. **View logs:**
```bash
docker-compose logs -f
# Or
make logs
```

3. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

4. **Stop services:**
```bash
docker-compose down
# Or
make down
```

### Available Make Commands

- `make build` - Build all Docker images
- `make up` - Start all services in background
- `make up-logs` - Start all services with logs
- `make down` - Stop all services
- `make logs` - View all logs
- `make restart` - Restart all services
- `make clean` - Remove all containers and volumes
- `make rebuild` - Rebuild and start services
- `make backend-shell` - Access backend container shell
- `make db-shell` - Access PostgreSQL shell

## Manual Setup (Without Docker)

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL database
- uv (fast Python package installer)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Run setup script:
```bash
chmod +x setup.sh
./setup.sh
```

Or manually:
```bash
# Create virtual environment using uv
uv venv

# Install dependencies using uv
uv pip install -r requirements.txt
```

4. Set up PostgreSQL database:
```bash
# Create database
createdb face_recognition

# Or using psql:
psql -U postgres
CREATE DATABASE face_recognition;
```

5. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your database credentials
DATABASE_URL=postgresql://user:password@localhost:5432/face_recognition
```

6. Activate virtual environment and run the backend:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or use the run script:
```bash
chmod +x run.sh
./run.sh
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. **Start the backend server** (port 8000)
2. **Start the frontend server** (port 3000)
3. **Open the application** in your browser
4. **Add persons** to the database:
   - Enter a person's name
   - Select an image file
   - Click "Upload & Add Person"
   - You can add multiple images per person
5. **Start the camera** to begin real-time face recognition
6. **View detections**:
   - Recognized faces show in green boxes with names
   - Unknown faces show in red boxes
   - Objects show in blue boxes

## Database Structure

- Images are stored in the `database/` folder
- Each person has a folder named after them
- Multiple images per person are supported
- Person metadata is stored in PostgreSQL

## API Endpoints

- `POST /api/detect` - Detect faces and objects in an image
- `POST /api/upload-person` - Upload a person image to the database
- `GET /api/persons` - Get all persons in the database
- `DELETE /api/persons/{person_id}` - Delete a person from the database

## Notes

- The first time you run the backend, YOLOv8 will download the model automatically
- Face recognition uses the `face_recognition` library which is based on dlib
- The system supports multiple images per person for better recognition accuracy
- Camera permissions are required in the browser

## Documentation

- **[TECHNICAL.md](./TECHNICAL.md)** - Detailed technical documentation:
  - System architecture and data flow
  - How face recognition and object detection work
  - API endpoint details
  - Component explanations
  - Performance optimizations
  - Troubleshooting guide

- **[DOCKER.md](./DOCKER.md)** - Docker-specific setup and commands

- **[QUICKSTART.md](./QUICKSTART.md)** - Quick start guide


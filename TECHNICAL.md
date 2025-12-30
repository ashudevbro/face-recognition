# Face Recognition System - Technical Documentation

## Architecture Overview

The system is a full-stack face recognition application with three main components:

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │─────▶│   FastAPI    │─────▶│ PostgreSQL  │
│  Frontend   │      │   Backend    │      │  Database   │
│  (Port 3000)│      │  (Port 8000) │      │  (Port 5432)│
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   Database   │
                    │   Folder     │
                    │  (Images)    │
                    └──────────────┘
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework for REST API
- **OpenCV**: Image processing and computer vision
- **face_recognition**: Face detection and recognition library (built on dlib)
- **YOLOv8 (Ultralytics)**: Pre-trained object detection model
- **PostgreSQL**: Relational database for person metadata
- **SQLAlchemy**: ORM for database operations
- **uv**: Fast Python package installer

### Frontend
- **React**: UI framework
- **Vite**: Build tool and dev server
- **Axios**: HTTP client for API calls

### Infrastructure
- **Docker Compose**: Container orchestration
- **PostgreSQL**: Database container

## System Components

### 1. Face Recognition Service (`face_recognition_service.py`)

**Purpose**: Detects and recognizes faces in images

**How it works**:
1. **Loading Known Faces**:
   - Scans `database/` folder for person subdirectories
   - Each person has a folder named after them
   - Loads all images from person folders
   - Extracts face encodings using `face_recognition.face_encodings()`
   - Stores encodings with person names in memory

2. **Face Recognition Process**:
   ```
   Input Image → Convert BGR to RGB → Detect Face Locations
   → Extract Face Encodings → Compare with Known Encodings
   → Calculate Face Distance → Match if distance < threshold (0.6)
   → Return Results (name, bbox, is_known)
   ```

3. **Adding New Persons**:
   - Receives image and person name
   - Creates folder: `database/{person_name}/`
   - Saves image with UUID filename
   - Reloads all known faces

**Key Functions**:
- `load_known_faces()`: Loads all face encodings from database folder
- `add_person_image()`: Adds new person image to database
- `recognize_faces()`: Recognizes faces in a frame

### 2. Object Detection Service (`object_detection_service.py`)

**Purpose**: Detects objects in images using YOLOv8

**How it works**:
1. Loads pre-trained YOLOv8 nano model (`yolov8n.pt`)
2. Processes image through YOLO model
3. Filters detections by confidence (>0.5)
4. Returns object class, confidence, and bounding box

**Model**: YOLOv8n (nano) - lightweight, fast inference

### 3. Database Layer (`database.py`)

**Purpose**: Manages person metadata in PostgreSQL

**Schema**:
```sql
CREATE TABLE persons (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Functions**:
- `init_db()`: Creates database tables
- `get_db()`: Database session dependency for FastAPI

### 4. API Endpoints (`main.py`)

#### POST `/api/detect`
**Purpose**: Detect faces and objects in uploaded image

**Process**:
1. Receives image file via multipart/form-data
2. Decodes image using OpenCV
3. Calls `face_service.recognize_faces()` → returns face results
4. Calls `object_service.detect_objects()` → returns object results
5. Returns JSON with both results

**Response Format**:
```json
{
  "faces": [
    {
      "name": "John Doe" or "Unknown",
      "bbox": [x1, y1, x2, y2],
      "is_known": true/false
    }
  ],
  "objects": [
    {
      "class": "person",
      "confidence": 0.95,
      "bbox": [x1, y1, x2, y2]
    }
  ]
}
```

#### POST `/api/upload-person`
**Purpose**: Add new person to database

**Process**:
1. Receives `name` (Form field) and `file` (File upload)
2. Validates name is not empty
3. Saves file temporarily to `/tmp/`
4. Calls `face_service.add_person_image()`:
   - Creates `database/{name}/` folder
   - Saves image with UUID filename
   - Reloads known faces
5. Adds person to PostgreSQL if not exists
6. Cleans up temp file
7. Returns success message

#### GET `/api/persons`
**Purpose**: List all persons in database

**Returns**: Array of `{id, name}` objects

#### DELETE `/api/persons/{person_id}`
**Purpose**: Delete person from database

**Process**:
1. Finds person in database
2. Deletes `database/{person_name}/` folder
3. Reloads known faces
4. Deletes person record from PostgreSQL

### 5. Frontend (`App.jsx`)

**Components**:
1. **Camera Feed**:
   - Uses `getUserMedia()` API to access camera
   - Displays video stream in `<video>` element
   - Captures frames to `<canvas>` every 500ms
   - Sends canvas blob to `/api/detect` endpoint
   - Draws detection boxes on canvas overlay

2. **Face Detection Visualization**:
   - **Green boxes**: Known faces (recognized)
   - **Red boxes**: Unknown faces (not in database)
   - **Blue boxes**: Detected objects

3. **Upload Interface**:
   - Text input for person name
   - File input for image selection
   - Sends multipart form data to `/api/upload-person`
   - Refreshes person list after upload

4. **Person Management**:
   - Displays list of all persons
   - Delete button for each person
   - Calls `/api/persons` to load list

## Data Flow

### Face Recognition Flow

```
1. User uploads person image
   ↓
2. Backend saves to database/{name}/
   ↓
3. face_recognition_service loads image
   ↓
4. Extracts face encoding (128-dimensional vector)
   ↓
5. Stores encoding in memory with person name
   ↓
6. Camera captures frame
   ↓
7. Frontend sends frame to /api/detect
   ↓
8. Backend extracts face encodings from frame
   ↓
9. Compares with known encodings using Euclidean distance
   ↓
10. If distance < 0.6 threshold → Match found
   ↓
11. Returns name and bounding box
   ↓
12. Frontend draws green box with name
```

### Object Detection Flow

```
1. Camera captures frame
   ↓
2. Frontend sends to /api/detect
   ↓
3. Backend passes frame to YOLOv8 model
   ↓
4. YOLO processes image (neural network inference)
   ↓
5. Returns detected objects with confidence scores
   ↓
6. Filters by confidence > 0.5
   ↓
7. Returns class name, confidence, bounding box
   ↓
8. Frontend draws blue box with label
```

## Face Recognition Algorithm

### Encoding Extraction
- Uses HOG (Histogram of Oriented Gradients) for face detection
- Uses deep learning model (ResNet) for face encoding
- Each face encoded as 128-dimensional vector
- Encoding captures facial features (eyes, nose, mouth, etc.)

### Matching Process
1. Calculate face distance between unknown face and all known faces
2. Face distance = Euclidean distance between encoding vectors
3. Lower distance = more similar faces
4. Threshold: 0.6 (tunable)
5. If minimum distance < threshold → Match

### Why Multiple Images Help
- Different angles/lighting conditions
- Multiple encodings per person stored
- Better recognition accuracy
- More robust to variations

## File Structure

```
face-recogition/
├── backend/
│   ├── main.py                    # FastAPI app, API endpoints
│   ├── database.py                # PostgreSQL models, connection
│   ├── face_recognition_service.py # Face recognition logic
│   ├── object_detection_service.py # YOLO object detection
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Backend container definition
│   └── database/                  # Face images storage
│       └── {person_name}/
│           └── {uuid}.jpg
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main React component
│   │   ├── App.css                # Styles
│   │   └── main.jsx               # React entry point
│   ├── package.json               # Node dependencies
│   └── Dockerfile                 # Frontend container definition
├── docker-compose.yml             # Service orchestration
└── README.md                      # User documentation
```

## Docker Architecture

### Backend Container
- **Base**: Python 3.11-slim
- **Build Process**:
  1. Install system deps (cmake, build tools for dlib)
  2. Install uv package manager
  3. Install Python packages via uv
  4. Copy application code
  5. Create database folder
- **Runtime**: Uvicorn ASGI server with auto-reload
- **Volumes**: 
  - `./backend:/app` (code hot-reload)
  - `./backend/database:/app/database` (persistent images)

### Frontend Container
- **Base**: Node.js 18-alpine
- **Build Process**:
  1. Copy package.json
  2. Install npm dependencies
  3. Copy application code
- **Runtime**: Vite dev server
- **Volumes**: 
  - `./frontend:/app` (code hot-reload)
  - `/app/node_modules` (anonymous volume for dependencies)

### PostgreSQL Container
- **Base**: postgres:15-alpine
- **Data**: Persistent volume `postgres_data`
- **Port**: 5432 (exposed for debugging)

## Security Considerations

1. **No Authentication**: Current implementation has no auth (development only)
2. **File Upload**: No validation on file types/sizes
3. **Database**: Default credentials (change for production)
4. **CORS**: Configured for localhost only

## Performance Optimizations

1. **Face Encodings Cached**: Loaded once at startup, stored in memory
2. **YOLO Model**: Pre-trained, loaded once
3. **Detection Frequency**: 500ms intervals (2 FPS) to reduce load
4. **Image Resolution**: Camera set to 1280x720 (balanced quality/speed)
5. **Confidence Threshold**: 0.5 for objects (filters false positives)

## Limitations

1. **Face Recognition**:
   - Requires clear frontal face view
   - Lighting conditions affect accuracy
   - Similar-looking people may be confused
   - Works best with multiple training images

2. **Object Detection**:
   - YOLOv8n is lightweight but less accurate than larger models
   - Some objects may be missed
   - Confidence threshold may filter valid detections

3. **Real-time Processing**:
   - Limited by CPU/GPU performance
   - Network latency for API calls
   - Browser camera API limitations

## Future Enhancements

1. **GPU Support**: Use CUDA for faster YOLO inference
2. **Face Recognition Model**: Upgrade to more accurate models (FaceNet, ArcFace)
3. **Database Optimization**: Store face encodings in database (pgvector)
4. **Authentication**: Add user authentication and authorization
5. **Batch Processing**: Process multiple images at once
6. **Video Recording**: Save detection sessions
7. **Analytics**: Track recognition statistics
8. **Mobile Support**: Responsive design improvements

## Troubleshooting

### Common Issues

1. **Camera Not Found**: 
   - Check browser permissions
   - Ensure camera is connected
   - Try different browser

2. **Face Not Recognized**:
   - Add more training images
   - Ensure good lighting
   - Face should be frontal and clear

3. **Slow Detection**:
   - Reduce detection frequency
   - Lower camera resolution
   - Use GPU if available

4. **Database Connection Error**:
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Check container logs

## References

- [face_recognition library](https://github.com/ageitgey/face_recognition)
- [YOLOv8 documentation](https://docs.ultralytics.com/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [React documentation](https://react.dev/)


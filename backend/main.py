from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
import cv2
import numpy as np
from PIL import Image
import io
import os
from pathlib import Path

from database import get_db, init_db, Person
from face_recognition_service import FaceRecognitionService
from object_detection_service import ObjectDetectionService

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
face_service = FaceRecognitionService()
object_service = ObjectDetectionService()

# Initialize database
init_db()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global face_service, object_service
    face_service.load_known_faces()
    print("Services initialized")


@app.get("/")
async def root():
    return {"message": "Face Recognition API"}


@app.post("/api/detect")
async def detect_faces_and_objects(file: UploadFile = File(...)):
    """Detect faces and objects in an uploaded image"""
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Detect faces
        face_results = face_service.recognize_faces(frame)
        
        # Detect objects
        object_results = object_service.detect_objects(frame)
        
        return {
            "faces": face_results,
            "objects": object_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-person")
async def upload_person(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an image to add a person to the database"""
    try:
        # Validate name
        if not name or not name.strip():
            raise HTTPException(status_code=400, detail="Name is required")
        
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Add to face recognition service
        success = face_service.add_person_image(temp_path, name.strip())
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process image")
        
        # Add to database if not exists
        person = db.query(Person).filter(Person.name == name.strip()).first()
        if not person:
            person = Person(name=name.strip())
            db.add(person)
            db.commit()
        
        # Clean up temp file
        os.remove(temp_path)
        
        return {"message": f"Person {name} added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/persons")
async def get_persons(db: Session = Depends(get_db)):
    """Get all persons in the database"""
    persons = db.query(Person).all()
    return [{"id": p.id, "name": p.name} for p in persons]


@app.delete("/api/persons/{person_id}")
async def delete_person(person_id: int, db: Session = Depends(get_db)):
    """Delete a person from the database"""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Delete images from database folder
    person_folder = Path("database") / person.name
    if person_folder.exists():
        import shutil
        shutil.rmtree(person_folder)
    
    # Reload known faces
    face_service.load_known_faces()
    
    # Delete from database
    db.delete(person)
    db.commit()
    
    return {"message": f"Person {person.name} deleted successfully"}


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


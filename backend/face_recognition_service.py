import face_recognition
import cv2
import numpy as np
import os
from pathlib import Path
import pickle


class FaceRecognitionService:
    def __init__(self, database_folder="database"):
        self.database_folder = Path(database_folder)
        self.database_folder.mkdir(exist_ok=True)
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()

    def load_known_faces(self):
        """Load all face encodings from the database folder"""
        self.known_face_encodings = []
        self.known_face_names = []

        if not self.database_folder.exists():
            return

        # Load from subdirectories (person folders)
        for person_folder in self.database_folder.iterdir():
            if person_folder.is_dir():
                person_name = person_folder.name
                for image_path in person_folder.glob("*"):
                    if image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                        try:
                            image = face_recognition.load_image_file(str(image_path))
                            encodings = face_recognition.face_encodings(image)
                            
                            if encodings:
                                # Add all encodings for this person (multiple faces in one image)
                                for encoding in encodings:
                                    self.known_face_encodings.append(encoding)
                                    self.known_face_names.append(person_name)
                        except Exception as e:
                            print(f"Error loading {image_path}: {e}")
        
        # Also support flat structure (backward compatibility)
        for image_path in self.database_folder.glob("*"):
            if image_path.is_file() and image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                person_name = image_path.stem  # filename without extension
                try:
                    image = face_recognition.load_image_file(str(image_path))
                    encodings = face_recognition.face_encodings(image)
                    
                    if encodings:
                        # Add all encodings for this person (multiple faces in one image)
                        for encoding in encodings:
                            self.known_face_encodings.append(encoding)
                            self.known_face_names.append(person_name)
                except Exception as e:
                    print(f"Error loading {image_path}: {e}")

    def add_person_image(self, image_path, person_name):
        """Add a new person image to the database"""
        try:
            # Save image to database folder
            person_folder = self.database_folder / person_name
            person_folder.mkdir(exist_ok=True)
            
            # Generate unique filename
            import uuid
            filename = f"{uuid.uuid4()}{Path(image_path).suffix}"
            save_path = person_folder / filename
            
            # Copy image
            import shutil
            shutil.copy(image_path, save_path)
            
            # Reload known faces
            self.load_known_faces()
            return True
        except Exception as e:
            print(f"Error adding person image: {e}")
            return False

    def recognize_faces(self, frame):
        """Recognize faces in a frame and return results"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find all face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        results = []
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            face_distance = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            
            if len(face_distance) > 0:
                best_match_index = np.argmin(face_distance)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
            
            results.append({
                "name": name,
                "bbox": [left, top, right, bottom],
                "is_known": name != "Unknown"
            })
        
        return results


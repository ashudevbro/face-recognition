from ultralytics import YOLO
import cv2
import numpy as np


class ObjectDetectionService:
    def __init__(self):
        # Load YOLOv8 model (pre-trained)
        try:
            self.model = YOLO('yolov8n.pt')  # nano version for speed
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.model = None

    def detect_objects(self, frame):
        """Detect objects in a frame and return results"""
        if self.model is None:
            return []
        
        try:
            results = self.model(frame, verbose=False)
            detections = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[class_id]
                    
                    # Only return detections with confidence > 0.5
                    if confidence > 0.5:
                        detections.append({
                            "class": class_name,
                            "confidence": confidence,
                            "bbox": [int(x1), int(y1), int(x2), int(y2)]
                        })
            
            return detections
        except Exception as e:
            print(f"Error in object detection: {e}")
            return []


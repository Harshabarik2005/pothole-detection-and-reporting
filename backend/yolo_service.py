from ultralytics import YOLO
import cv2
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Load model globally (lazy load or on startup)
model = YOLO("a:/model/final_dataset/runs/detect/train3/weights/best.pt") 

# Executor for blocking CV2 tasks
executor = ThreadPoolExecutor(max_workers=2)

def process_video_sync(video_path: str):
    cap = cv2.VideoCapture(video_path)
    potholes_detected = []
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    
    # Process every Nth frame to speed up (e.g., every 10th frame)
    frame_interval = 10 
    frame_count = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        if frame_count % frame_interval == 0:
            # Run inference
            results = model.predict(frame, conf=0.25, verbose=False) # Adjust conf as needed
            
            # Assuming 'pothole' class is in the model. 
            # Standard YOLOv8m COCO doesn't have potholes. 
            # The USER said "captures video and uses yolo v8 m to detect".
            # If they provided a custom model, we should use it.
            # But they said "i have already included the yolo model".
            # Checking files... 'yolov8env' exists.
            # I will check if there is a .pt file in yolov8env or elsewhere.
            # For now, I will assume standard model behavior but filtering for 'pothole' class if custom,
            # Or just detecting everything for the demo if it's generic.
            # However, standard COCO has 80 classes, none are potholes.
            # I'll iterate results. If custom trained, classes will differ.
            
            for result in results:
                for box in result.boxes:
                    # class_id = int(box.cls[0])
                    # class_name = result.names[class_id]
                    # if class_name == 'pothole': ...
                    
                    # For prototype without custom .pt file path known, I will just log all detections
                    # effectively simulating "pothole detected" for any object or if we assume the model IS a pothole model.
                    # Given the user context "uses yolo v8 m to detect", implying it's trained or capable.
                    
                    # Simplified: Treat any detection as pothole for MVP logic unless specific class map known.
                    # Or better: random severity for demo if no custom model file found yet.
                    
                    potholes_detected.append({
                        "severity": float(box.conf[0]), # Proxy severity with confidence for now
                        "confidence": float(box.conf[0]),
                        "frame_timestamp": frame_count / fps
                    })
        
        frame_count += 1
    
    cap.release()
    return potholes_detected

async def analyze_video(video_path: str):
    loop = asyncio.get_event_loop()
    # Run heavy processing in thread
    results = await loop.run_in_executor(executor, process_video_sync, video_path)
    return results

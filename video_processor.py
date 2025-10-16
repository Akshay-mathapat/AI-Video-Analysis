import cv2
import numpy as np
from ultralytics import YOLO
import json
import os
from datetime import datetime, timedelta
import pickle

class VideoProcessor:
    def __init__(self, video_path, log_callback=None):
        self.video_path = video_path
        self.log = log_callback if log_callback else print
        self.results_dir = "analysis_results"
        
        # Create results directory
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
        
        # Initialize models
        self.log("Loading YOLOv8 model...")
        self.yolo_model = YOLO('yolov8m.pt')
        
        self.log("Loading face detection model...")
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Storage
        self.video_metadata = {
            'path': video_path,
            'filename': os.path.basename(video_path),
            'analysis_time': datetime.now().isoformat(),
            'objects': [],
            'faces': [],
            'suspicious_activities': [],
            'timeline': [],
            'transcript': []
        }
    
    def process_video(self):
        """Main processing function"""
        self.log("Opening video file...")
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            raise Exception("Could not open video file")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.video_metadata['fps'] = fps
        self.video_metadata['total_frames'] = total_frames
        self.video_metadata['duration_seconds'] = duration
        self.video_metadata['resolution'] = f"{width}x{height}"
        
        self.log(f"Video info: {duration:.2f}s, {fps} FPS, {width}x{height}")
        
        frame_count = 0
        process_every_n_frames = 30  # Process every 30 frames for efficiency
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % process_every_n_frames == 0:
                timestamp = frame_count / fps
                self.log(f"Processing frame {frame_count}/{total_frames} (t={timestamp:.2f}s)")
                
                # Object detection
                self.detect_objects_in_frame(frame, timestamp, frame_count)
                
                # Face detection
                self.detect_faces_in_frame(frame, timestamp, frame_count)
                
                # Suspicious activity detection
                self.detect_suspicious_activity(frame, timestamp, frame_count)
                
                # Generate transcript
                self.generate_transcript_entry(frame, timestamp, frame_count)
            
            frame_count += 1
        
        cap.release()
        
        # Save results
        self.save_results()
        self.log("Video processing complete!")
    
    def detect_objects_in_frame(self, frame, timestamp, frame_num):
        """Detect objects using YOLOv8"""
        results = self.yolo_model(frame, verbose=False)
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = result.names[cls]
                
                if conf > 0.5:  # Confidence threshold
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    obj_data = {
                        'timestamp': timestamp,
                        'frame': frame_num,
                        'object': label,
                        'confidence': conf,
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'time_str': str(timedelta(seconds=int(timestamp)))
                    }
                    
                    self.video_metadata['objects'].append(obj_data)
                    
                    # Check for weapons/suspicious objects
                    suspicious_objects = ['knife', 'gun', 'rifle', 'weapon', 'backpack']
                    if any(obj in label.lower() for obj in suspicious_objects):
                        self.log(f"⚠️ ALERT: Detected {label} at {timestamp:.2f}s")
    
    def detect_faces_in_frame(self, frame, timestamp, frame_num):
        """Detect faces using Haar Cascade"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            face_data = {
                'timestamp': timestamp,
                'frame': frame_num,
                'bbox': [int(x), int(y), int(w), int(h)],
                'time_str': str(timedelta(seconds=int(timestamp)))
            }
            
            self.video_metadata['faces'].append(face_data)
            
            # Save face image
            face_img = frame[y:y+h, x:x+w]
            face_path = os.path.join(self.results_dir, f"face_{frame_num}.jpg")
            cv2.imwrite(face_path, face_img)
            face_data['image_path'] = face_path
    
    def detect_suspicious_activity(self, frame, timestamp, frame_num):
        """Detect suspicious activities using motion and object analysis"""
        # Simple suspicious activity detection based on:
        # 1. Multiple people in frame
        # 2. Presence of suspicious objects
        # 3. Motion patterns
        
        results = self.yolo_model(frame, verbose=False)
        person_count = 0
        vehicles = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                label = result.names[int(box.cls[0])]
                if label == 'person':
                    person_count += 1
                elif label in ['car', 'truck', 'motorcycle', 'bus']:
                    vehicles.append(label)
        
        # Flag suspicious scenarios
        suspicious = False
        reason = ""
        
        if person_count > 5:
            suspicious = True
            reason = f"Large group detected ({person_count} people)"
        
        if len(vehicles) > 3:
            suspicious = True
            reason = f"Multiple vehicles detected ({len(vehicles)} vehicles)"
        
        if suspicious:
            activity_data = {
                'timestamp': timestamp,
                'frame': frame_num,
                'reason': reason,
                'person_count': person_count,
                'vehicles': vehicles,
                'time_str': str(timedelta(seconds=int(timestamp)))
            }
            
            self.video_metadata['suspicious_activities'].append(activity_data)
            self.log(f"⚠️ Suspicious activity: {reason} at {timestamp:.2f}s")
    
    def generate_transcript_entry(self, frame, timestamp, frame_num):
        """Generate text description of the frame"""
        results = self.yolo_model(frame, verbose=False)
        
        objects_in_frame = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                label = result.names[int(box.cls[0])]
                conf = float(box.conf[0])
                if conf > 0.5:
                    objects_in_frame.append(label)
        
        # Count occurrences
        from collections import Counter
        object_counts = Counter(objects_in_frame)
        
        # Generate description
        description = f"At {str(timedelta(seconds=int(timestamp)))}: "
        if object_counts:
            items = [f"{count} {obj}{'s' if count > 1 else ''}" 
                    for obj, count in object_counts.most_common(5)]
            description += "Detected " + ", ".join(items)
        else:
            description += "No significant objects detected"
        
        transcript_entry = {
            'timestamp': timestamp,
            'frame': frame_num,
            'description': description,
            'objects': dict(object_counts),
            'time_str': str(timedelta(seconds=int(timestamp)))
        }
        
        self.video_metadata['transcript'].append(transcript_entry)
        
        # Timeline entry
        if object_counts:
            self.video_metadata['timeline'].append({
                'time': timestamp,
                'time_str': str(timedelta(seconds=int(timestamp))),
                'event': description
            })
    
    def save_results(self):
        """Save all analysis results"""
        # Save JSON
        json_path = os.path.join(self.results_dir, 'analysis_results.json')
        with open(json_path, 'w') as f:
            json.dump(self.video_metadata, f, indent=2)
        
        # Save pickle for faster loading
        pickle_path = os.path.join(self.results_dir, 'analysis_results.pkl')
        with open(pickle_path, 'wb') as f:
            pickle.dump(self.video_metadata, f)
        
        # Generate summary text
        summary_path = os.path.join(self.results_dir, 'summary.txt')
        with open(summary_path, 'w') as f:
            f.write("=== VIDEO ANALYSIS SUMMARY ===\n\n")
            f.write(f"Video: {self.video_metadata['filename']}\n")
            f.write(f"Duration: {self.video_metadata['duration_seconds']:.2f} seconds\n")
            f.write(f"Resolution: {self.video_metadata['resolution']}\n")
            f.write(f"Analysis Date: {self.video_metadata['analysis_time']}\n\n")
            
            f.write(f"Total Objects Detected: {len(self.video_metadata['objects'])}\n")
            f.write(f"Total Faces Detected: {len(self.video_metadata['faces'])}\n")
            f.write(f"Suspicious Activities: {len(self.video_metadata['suspicious_activities'])}\n\n")
            
            f.write("=== TIMELINE ===\n")
            for event in self.video_metadata['timeline'][:20]:  # First 20 events
                f.write(f"{event['time_str']}: {event['event']}\n")
        
        self.log(f"Results saved to {self.results_dir}/")


def show_detection_results(detection_type, log_callback=None):
    """Display detection results in a new window"""
    import tkinter as tk
    from tkinter import ttk
    
    log = log_callback if log_callback else print
    
    # Load results
    results_path = os.path.join('analysis_results', 'analysis_results.pkl')
    if not os.path.exists(results_path):
        log("No analysis results found!")
        return
    
    with open(results_path, 'rb') as f:
        results = pickle.load(f)
    
    # Create window
    window = tk.Toplevel()
    window.title(f"{detection_type.capitalize()} Detection Results")
    window.geometry("1000x600")
    window.configure(bg='#2c3e50')
    
    # Title
    title = tk.Label(window, text=f"{detection_type.capitalize()} Detection Results",
                    font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white')
    title.pack(pady=20)
    
    # Results frame
    frame = tk.Frame(window, bg='#34495e')
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Text widget with scrollbar
    text_widget = tk.Text(frame, font=('Courier', 10), bg='#1c1c1c', fg='#00ff00',
                         wrap=tk.WORD)
    scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
    text_widget.config(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Display results
    if detection_type == 'objects':
        data = results['objects']
        text_widget.insert(tk.END, f"Total Objects Detected: {len(data)}\n\n")
        
        # Group by object type
        from collections import defaultdict
        by_type = defaultdict(list)
        for obj in data:
            by_type[obj['object']].append(obj)
        
        for obj_type, detections in sorted(by_type.items()):
            text_widget.insert(tk.END, f"\n{obj_type.upper()} ({len(detections)} detections):\n")
            text_widget.insert(tk.END, "-" * 50 + "\n")
            for det in detections[:10]:  # Show first 10
                text_widget.insert(tk.END, 
                    f"  Time: {det['time_str']} | Confidence: {det['confidence']:.2f}\n")
    
    elif detection_type == 'faces':
        data = results['faces']
        text_widget.insert(tk.END, f"Total Faces Detected: {len(data)}\n\n")
        
        for i, face in enumerate(data[:50], 1):  # Show first 50
            text_widget.insert(tk.END, 
                f"Face {i}: Time {face['time_str']} | Frame {face['frame']}\n")
    
    elif detection_type == 'suspicious':
        data = results['suspicious_activities']
        text_widget.insert(tk.END, f"Suspicious Activities Detected: {len(data)}\n\n")
        
        if len(data) == 0:
            text_widget.insert(tk.END, "No suspicious activities detected.\n")
        else:
            for i, activity in enumerate(data, 1):
                text_widget.insert(tk.END, f"\nActivity {i}:\n")
                text_widget.insert(tk.END, f"  Time: {activity['time_str']}\n")
                text_widget.insert(tk.END, f"  Reason: {activity['reason']}\n")
                text_widget.insert(tk.END, f"  People: {activity['person_count']}\n")
                if activity['vehicles']:
                    text_widget.insert(tk.END, f"  Vehicles: {', '.join(activity['vehicles'])}\n")
    
    text_widget.config(state=tk.DISABLED)
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import json
import pickle
import os
from datetime import datetime
import cv2

class VideoChatbot:
    def __init__(self, root):
        self.root = root
        self.root.title("NSG AI Video Analysis Chatbot")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Load analysis results
        self.load_analysis_results()
        
        # Setup UI
        self.setup_ui()
        
        # Chat history
        self.chat_history = []
        
        # Display welcome message
        self.add_bot_message("Hello! I'm your NSG Video Analysis AI Assistant. I can help you with:\n\n" +
                           "• Video summary and statistics\n" +
                           "• Object detection queries\n" +
                           "• Face detection information\n" +
                           "• Suspicious activity reports\n" +
                           "• Timeline events\n" +
                           "• Specific timestamp analysis\n\n" +
                           "What would you like to know?")
    
    def load_analysis_results(self):
        """Load analysis results from file"""
        results_path = os.path.join('analysis_results', 'analysis_results.pkl')
        
        if os.path.exists(results_path):
            with open(results_path, 'rb') as f:
                self.results = pickle.load(f)
        else:
            self.results = None
    
    def setup_ui(self):
        # Title bar
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=70)
        title_frame.pack(fill=tk.X)
        
        title = tk.Label(title_frame, text="🤖 AI Video Analysis Chatbot",
                        font=('Arial', 22, 'bold'), bg='#2c3e50', fg='white')
        title.pack(pady=15)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Chat
        left_panel = tk.Frame(main_container, bg='#2a2a2a', relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Chat display area
        chat_frame = tk.Frame(left_panel, bg='#2a2a2a')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            font=('Segoe UI', 11),
            bg='#1c1c1c',
            fg='white',
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags for styling
        self.chat_display.tag_config('user', foreground='#3498db', font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_config('bot', foreground='#2ecc71', font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_config('time', foreground='#95a5a6', font=('Segoe UI', 9))
        self.chat_display.tag_config('alert', foreground='#e74c3c', font=('Segoe UI', 11, 'bold'))
        
        # Input area
        input_frame = tk.Frame(left_panel, bg='#2a2a2a')
        input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.input_field = tk.Text(input_frame, height=3, font=('Segoe UI', 11),
                                   bg='#34495e', fg='white', relief=tk.FLAT,
                                   insertbackground='white', padx=10, pady=10)
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.input_field.bind('<Return>', self.send_message)
        
        send_btn = tk.Button(input_frame, text="Send", command=self.send_message,
                           font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                           activebackground='#229954', relief=tk.RAISED, 
                           borderwidth=3, cursor='hand2', width=10, height=2)
        send_btn.pack(side=tk.RIGHT)
        
        # Right panel - Quick queries and media display
        right_panel = tk.Frame(main_container, bg='#2a2a2a', relief=tk.RAISED, 
                              borderwidth=2, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0, 0))
        right_panel.pack_propagate(False)
        
        # Quick queries
        quick_frame = tk.LabelFrame(right_panel, text="Quick Queries", 
                                   font=('Arial', 13, 'bold'), bg='#2a2a2a', 
                                   fg='white', padx=15, pady=15)
        quick_frame.pack(fill=tk.X, padx=15, pady=15)
        
        quick_queries = [
            "Show video summary",
            "How many objects detected?",
            "Show suspicious activities",
            "List all detected faces",
            "Show timeline",
            "What happened at 00:00:30?",
            "Were any weapons detected?",
            "Show me people count"
        ]
        
        for query in quick_queries:
            btn = tk.Button(quick_frame, text=query, 
                          command=lambda q=query: self.quick_query(q),
                          font=('Arial', 9), bg='#34495e', fg='white',
                          activebackground='#2c3e50', relief=tk.RAISED,
                          cursor='hand2', anchor='w', padx=10, pady=8)
            btn.pack(fill=tk.X, pady=3)
        
        # Media display area
        media_frame = tk.LabelFrame(right_panel, text="Visual Data", 
                                   font=('Arial', 13, 'bold'), bg='#2a2a2a',
                                   fg='white', padx=15, pady=15)
        media_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.media_display = tk.Label(media_frame, bg='#1c1c1c', 
                                     text="Media will appear here",
                                     fg='#7f8c8d', font=('Arial', 10))
        self.media_display.pack(fill=tk.BOTH, expand=True)
    
    def add_bot_message(self, message):
        """Add bot message to chat"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"\n[{timestamp}] ", 'time')
        self.chat_display.insert(tk.END, "AI Assistant:\n", 'bot')
        self.chat_display.insert(tk.END, f"{message}\n", '')
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def add_user_message(self, message):
        """Add user message to chat"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"\n[{timestamp}] ", 'time')
        self.chat_display.insert(tk.END, "You:\n", 'user')
        self.chat_display.insert(tk.END, f"{message}\n", '')
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def quick_query(self, query):
        """Handle quick query button"""
        self.input_field.delete('1.0', tk.END)
        self.input_field.insert('1.0', query)
        self.send_message()
    
    def send_message(self, event=None):
        """Send message and get response"""
        if event and event.keysym == 'Return' and not event.state & 0x1:
            # Shift+Enter for newline
            return
        
        message = self.input_field.get('1.0', tk.END).strip()
        
        if not message:
            return 'break'
        
        self.input_field.delete('1.0', tk.END)
        self.add_user_message(message)
        
        # Process query
        response = self.process_query(message.lower())
        self.add_bot_message(response)
        
        return 'break'
    
    def process_query(self, query):
        """Process user query and generate response"""
        if not self.results:
            return "❌ No analysis results found. Please run video analysis first."
        
        # Video summary
        if any(word in query for word in ['summary', 'overview', 'general', 'about']):
            return self.get_video_summary()
        
        # Object detection queries
        elif any(word in query for word in ['object', 'detect', 'found', 'items']):
            if 'how many' in query or 'count' in query:
                return self.get_object_count()
            return self.get_object_details()
        
        # Face detection
        elif any(word in query for word in ['face', 'person', 'people']):
            return self.get_face_details()
        
        # Suspicious activity
        elif any(word in query for word in ['suspicious', 'alert', 'threat', 'danger']):
            return self.get_suspicious_activities()
        
        # Weapon detection
        elif any(word in query for word in ['weapon', 'gun', 'knife', 'rifle']):
            return self.check_weapons()
        
        # Timeline
        elif 'timeline' in query or 'events' in query:
            return self.get_timeline()
        
        # Timestamp query
        elif 'at' in query and any(c.isdigit() for c in query):
            return self.get_timestamp_info(query)
        
        # Default response with suggestions
        else:
            return ("I'm not sure what you're asking about. Here are some things I can help with:\n\n" +
                   "• 'Show video summary' - Get overview of the video\n" +
                   "• 'How many objects detected?' - Object count\n" +
                   "• 'Show suspicious activities' - Alert events\n" +
                   "• 'List all detected faces' - Face detection info\n" +
                   "• 'Show timeline' - Event timeline\n" +
                   "• 'What happened at HH:MM:SS?' - Specific time query")
    
    def get_video_summary(self):
        """Generate video summary"""
        metadata = self.results
        
        summary = f"📹 VIDEO ANALYSIS SUMMARY\n\n"
        summary += f"📁 File: {metadata['filename']}\n"
        summary += f"⏱️ Duration: {metadata['duration_seconds']:.2f} seconds\n"
        summary += f"📐 Resolution: {metadata['resolution']}\n"
        summary += f"🎞️ FPS: {metadata['fps']}\n"
        summary += f"📅 Analysis Date: {metadata['analysis_time']}\n\n"
        
        summary += f"🎯 Objects Detected: {len(metadata['objects'])}\n"
        summary += f"👤 Faces Detected: {len(metadata['faces'])}\n"
        summary += f"⚠️ Suspicious Activities: {len(metadata['suspicious_activities'])}\n"
        summary += f"📝 Timeline Events: {len(metadata['timeline'])}\n"
        
        return summary
    
    def get_object_count(self):
        """Get object detection count"""
        from collections import Counter
        
        objects = [obj['object'] for obj in self.results['objects']]
        object_counts = Counter(objects)
        
        response = f"🎯 OBJECT DETECTION SUMMARY\n\n"
        response += f"Total Detections: {len(objects)}\n"
        response += f"Unique Object Types: {len(object_counts)}\n\n"
        response += "Top Detected Objects:\n"
        
        for obj, count in object_counts.most_common(10):
            response += f"  • {obj}: {count} times\n"
        
        return response
    
    def get_object_details(self):
        """Get detailed object information"""
        from collections import defaultdict
        
        by_type = defaultdict(list)
        for obj in self.results['objects']:
            by_type[obj['object']].append(obj)
        
        response = f"🎯 DETAILED OBJECT DETECTION\n\n"
        
        for obj_type in sorted(by_type.keys())[:8]:  # Show first 8 types
            detections = by_type[obj_type]
            response += f"\n{obj_type.upper()} ({len(detections)} detections):\n"
            
            for det in detections[:3]:  # Show first 3 of each type
                response += f"  ⏱️ {det['time_str']} | Confidence: {det['confidence']:.1%}\n"
            
            if len(detections) > 3:
                response += f"  ... and {len(detections) - 3} more\n"
        
        return response
    
    def get_face_details(self):
        """Get face detection details"""
        faces = self.results['faces']
        
        if not faces:
            return "👤 No faces detected in the video."
        
        response = f"👤 FACE DETECTION REPORT\n\n"
        response += f"Total Faces Detected: {len(faces)}\n\n"
        response += "Detection Timeline:\n"
        
        for i, face in enumerate(faces[:15], 1):  # Show first 15
            response += f"  {i}. Time: {face['time_str']} | Frame: {face['frame']}\n"
        
        if len(faces) > 15:
            response += f"\n... and {len(faces) - 15} more faces detected"
        
        return response
    
    def get_suspicious_activities(self):
        """Get suspicious activity report"""
        activities = self.results['suspicious_activities']
        
        if not activities:
            return "✅ No suspicious activities detected in the video."
        
        response = f"⚠️ SUSPICIOUS ACTIVITY REPORT\n\n"
        response += f"Total Alerts: {len(activities)}\n\n"
        
        for i, activity in enumerate(activities, 1):
            response += f"Alert {i}:\n"
            response += f"  ⏱️ Time: {activity['time_str']}\n"
            response += f"  📋 Reason: {activity['reason']}\n"
            response += f"  👥 People: {activity['person_count']}\n"
            
            if activity['vehicles']:
                response += f"  🚗 Vehicles: {', '.join(activity['vehicles'])}\n"
            
            response += "\n"
        
        return response
    
    def check_weapons(self):
        """Check for weapon detection"""
        weapon_keywords = ['knife', 'gun', 'rifle', 'weapon', 'pistol']
        weapons_found = []
        
        for obj in self.results['objects']:
            if any(weapon in obj['object'].lower() for weapon in weapon_keywords):
                weapons_found.append(obj)
        
        if not weapons_found:
            return "✅ No weapons detected in the video."
        
        response = f"⚠️ WEAPON DETECTION ALERT\n\n"
        response += f"Weapons Detected: {len(weapons_found)}\n\n"
        
        for weapon in weapons_found:
            response += f"🔴 {weapon['object'].upper()}\n"
            response += f"  ⏱️ Time: {weapon['time_str']}\n"
            response += f"  📊 Confidence: {weapon['confidence']:.1%}\n"
            response += f"  🎞️ Frame: {weapon['frame']}\n\n"
        
        return response
    
    def get_timeline(self):
        """Get event timeline"""
        timeline = self.results['timeline']
        
        if not timeline:
            return "📅 No timeline events available."
        
        response = f"📅 EVENT TIMELINE\n\n"
        response += f"Total Events: {len(timeline)}\n\n"
        
        for event in timeline[:20]:  # Show first 20 events
            response += f"⏱️ {event['time_str']}\n"
            response += f"   {event['event']}\n\n"
        
        if len(timeline) > 20:
            response += f"... and {len(timeline) - 20} more events"
        
        return response
    
    def get_timestamp_info(self, query):
        """Get information about specific timestamp"""
        import re
        
        # Extract time from query
        time_pattern = r'(\d{1,2}):(\d{2}):(\d{2})'
        match = re.search(time_pattern, query)
        
        if not match:
            return "⏱️ Please specify time in format HH:MM:SS (e.g., 00:01:30)"
        
        hours, minutes, seconds = map(int, match.groups())
        target_time = hours * 3600 + minutes * 60 + seconds
        
        # Find events near this timestamp
        tolerance = 5  # seconds
        
        events = []
        
        # Check objects
        for obj in self.results['objects']:
            if abs(obj['timestamp'] - target_time) < tolerance:
                events.append(f"🎯 {obj['object']} detected")
        
        # Check faces
        for face in self.results['faces']:
            if abs(face['timestamp'] - target_time) < tolerance:
                events.append(f"👤 Face detected")
        
        # Check suspicious activities
        for activity in self.results['suspicious_activities']:
            if abs(activity['timestamp'] - target_time) < tolerance:
                events.append(f"⚠️ {activity['reason']}")
        
        if not events:
            return f"ℹ️ No significant events found at {match.group()}"
        
        response = f"📍 EVENTS AT {match.group()}\n\n"
        for event in set(events):  # Remove duplicates
            response += f"  • {event}\n"
        
        return response


def launch_chatbot():
    """Launch the chatbot interface"""
    root = tk.Toplevel()
    app = VideoChatbot(root)
    root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoChatbot(root)
    root.mainloop()
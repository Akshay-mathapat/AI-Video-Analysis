
#file1

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import threading
import os

class VideoAnalysisUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NSG Video Analysis System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        self.video_path = None
        self.analysis_complete = False
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 12), padding=10)
        style.configure('TLabel', font=('Arial', 11), background='#1e1e1e', foreground='white')
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="🎥 NSG Surveillance Video Analysis System",
                               font=('Arial', 24, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(pady=20)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Left panel - Video upload and controls
        left_panel = tk.Frame(main_container, bg='#2a2a2a', relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Upload section
        upload_frame = tk.LabelFrame(left_panel, text="Video Upload", font=('Arial', 14, 'bold'),
                                     bg='#2a2a2a', fg='white', padx=20, pady=20)
        upload_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.upload_btn = tk.Button(upload_frame, text="📁 Select Video File",
                                    command=self.upload_video, font=('Arial', 14, 'bold'),
                                    bg='#3498db', fg='white', activebackground='#2980b9',
                                    relief=tk.RAISED, borderwidth=3, cursor='hand2', height=2)
        self.upload_btn.pack(pady=10, fill=tk.X)
        
        self.file_label = tk.Label(upload_frame, text="No file selected", 
                                   font=('Arial', 10), bg='#2a2a2a', fg='#95a5a6',
                                   wraplength=400)
        self.file_label.pack(pady=5)
        
        # Analysis section
        analysis_frame = tk.LabelFrame(left_panel, text="Analysis Options", font=('Arial', 14, 'bold'),
                                      bg='#2a2a2a', fg='white', padx=20, pady=20)
        analysis_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.analyze_btn = tk.Button(analysis_frame, text="🔍 Start Analysis",
                                     command=self.start_analysis, font=('Arial', 13, 'bold'),
                                     bg='#27ae60', fg='white', activebackground='#229954',
                                     relief=tk.RAISED, borderwidth=3, cursor='hand2',
                                     state=tk.DISABLED, height=2)
        self.analyze_btn.pack(pady=10, fill=tk.X)
        
        self.detect_objects_btn = tk.Button(analysis_frame, text="🎯 Detect Objects (YOLOv8)",
                                           command=self.detect_objects, font=('Arial', 12),
                                           bg='#e67e22', fg='white', activebackground='#d35400',
                                           relief=tk.RAISED, borderwidth=2, cursor='hand2',
                                           state=tk.DISABLED)
        self.detect_objects_btn.pack(pady=5, fill=tk.X)
        
        self.detect_faces_btn = tk.Button(analysis_frame, text="👤 Detect Faces",
                                         command=self.detect_faces, font=('Arial', 12),
                                         bg='#9b59b6', fg='white', activebackground='#8e44ad',
                                         relief=tk.RAISED, borderwidth=2, cursor='hand2',
                                         state=tk.DISABLED)
        self.detect_faces_btn.pack(pady=5, fill=tk.X)
        
        self.detect_suspicious_btn = tk.Button(analysis_frame, text="⚠️ Detect Suspicious Activity",
                                              command=self.detect_suspicious, font=('Arial', 12),
                                              bg='#e74c3c', fg='white', activebackground='#c0392b',
                                              relief=tk.RAISED, borderwidth=2, cursor='hand2',
                                              state=tk.DISABLED)
        self.detect_suspicious_btn.pack(pady=5, fill=tk.X)
        
        self.open_chatbot_btn = tk.Button(analysis_frame, text="💬 Open AI Chatbot",
                                         command=self.open_chatbot, font=('Arial', 12),
                                         bg='#16a085', fg='white', activebackground='#138d75',
                                         relief=tk.RAISED, borderwidth=2, cursor='hand2',
                                         state=tk.DISABLED)
        self.open_chatbot_btn.pack(pady=5, fill=tk.X)
        
        # Right panel - Status and logs
        right_panel = tk.Frame(main_container, bg='#2a2a2a', relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Status section
        status_frame = tk.LabelFrame(right_panel, text="System Status", font=('Arial', 14, 'bold'),
                                    bg='#2a2a2a', fg='white', padx=20, pady=20)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.status_text = tk.Text(status_frame, height=30, font=('Courier', 10),
                                  bg='#1c1c1c', fg='#00ff00', insertbackground='white',
                                  relief=tk.SUNKEN, borderwidth=2)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.status_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)
        
        self.log_message("System initialized. Ready to analyse surveillance footage.")
        self.log_message("Upload a video file to begin analysis.")
    
    def log_message(self, message):
        self.status_text.insert(tk.END, f"[{self.get_timestamp()}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def upload_video(self):
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.video_path = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"Selected: {filename}", fg='#2ecc71')
            self.log_message(f"Video uploaded: {filename}")
            self.analyze_btn.config(state=tk.NORMAL)
    
    def start_analysis(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please upload a video first!")
            return
        
        self.log_message("Starting comprehensive video analysis...")
        self.analyze_btn.config(state=tk.DISABLED)
        
        # Run analysis in separate thread
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()
    
    def run_analysis(self):
        try:
            from video_processor import VideoProcessor
            
            self.log_message("Initializing video processor...")
            processor = VideoProcessor(self.video_path, self.log_message)
            
            self.log_message("Processing video file...")
            processor.process_video()
            
            self.analysis_complete = True
            self.log_message("✓ Analysis complete! All features enabled.")
            
            # Enable all buttons
            self.detect_objects_btn.config(state=tk.NORMAL)
            self.detect_faces_btn.config(state=tk.NORMAL)
            self.detect_suspicious_btn.config(state=tk.NORMAL)
            self.open_chatbot_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
            messagebox.showerror("Analysis Error", str(e))
    
    def detect_objects(self):
        if not self.analysis_complete:
            messagebox.showwarning("Warning", "Please run analysis first!")
            return
        
        self.log_message("Opening object detection results...")
        try:
            from video_processor import show_detection_results
            show_detection_results('objects', self.log_message)
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
    
    def detect_faces(self):
        if not self.analysis_complete:
            messagebox.showwarning("Warning", "Please run analysis first!")
            return
        
        self.log_message("Opening face detection results...")
        try:
            from video_processor import show_detection_results
            show_detection_results('faces', self.log_message)
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
    
    def detect_suspicious(self):
        if not self.analysis_complete:
            messagebox.showwarning("Warning", "Please run analysis first!")
            return
        
        self.log_message("Opening suspicious activity detection results...")
        try:
            from video_processor import show_detection_results
            show_detection_results('suspicious', self.log_message)
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
    
    def open_chatbot(self):
        if not self.analysis_complete:
            messagebox.showwarning("Warning", "Please run analysis first!")
            return
        
        self.log_message("Launching AI chatbot interface...")
        try:
            import chatbot_interface
            chatbot_interface.launch_chatbot()
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")

def main():
    root = tk.Tk()
    app = VideoAnalysisUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
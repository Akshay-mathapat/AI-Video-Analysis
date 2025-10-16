"""
NSG AI-Powered Video Analysis System
Main Application Entry Point

This system provides:
- Video upload and processing
- YOLOv8 object detection
- Face detection
- Suspicious activity detection
- AI chatbot for querying results
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = {
        'cv2': 'opencv-python',
        'ultralytics': 'ultralytics',
        'PIL': 'Pillow',
        'numpy': 'numpy'
    }
    
    missing = []
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing.append(pip_name)
    
    if missing:
        error_msg = "Missing required packages:\n\n"
        error_msg += "\n".join(f"  • {pkg}" for pkg in missing)
        error_msg += "\n\nInstall them using:\n"
        error_msg += f"pip install {' '.join(missing)}"
        
        messagebox.showerror("Dependencies Missing", error_msg)
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['analysis_results', 'temp_frames']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    """Main application entry point"""
    print("="*60)
    print("NSG AI-Powered Video Analysis System")
    print("="*60)
    print("\nInitializing system...")
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        print("❌ Dependency check failed!")
        sys.exit(1)
    
    print("✓ All dependencies installed")
    
    # Create directories
    print("\nSetting up directories...")
    create_directories()
    print("✓ Directories ready")
    
    # Download YOLO model if needed
    print("\nChecking YOLO model...")
    try:
        from ultralytics import YOLO
        if not os.path.exists('yolov8m.pt'):
            print("Downloading YOLOv8 model (this may take a moment)...")
            model = YOLO('yolov8m.pt')
            print("✓ YOLO model ready")
        else:
            print("✓ YOLO model found")
    except Exception as e:
        print(f"⚠️ Warning: Could not verify YOLO model: {e}")
    
    print("\n" + "="*60)
    print("System Ready!")
    print("="*60)
    print("\nLaunching user interface...")
    
    # Launch UI
    try:
        from ui_interface import main as launch_ui
        launch_ui()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch UI: {str(e)}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
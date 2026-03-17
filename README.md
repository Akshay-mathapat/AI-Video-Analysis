# 🎥 AI & ML Enabled Video Analysis and Interpretation

## 📌 Overview
This project is an **AI-powered video analysis system** that detects and interprets objects in videos using Machine Learning and Computer Vision techniques. It leverages the power of **YOLOv8 (You Only Look Once)** for real-time object detection.

---

## 🚀 Features
- 🎯 Real-time object detection in videos
- 🧠 AI-based video interpretation
- 📊 Processed output stored in `analysis_results`
- 💻 Interactive user interface
- ⚡ Fast and efficient YOLOv8 model integration

---

## 🛠️ Technologies Used
- Python 🐍
- OpenCV
- YOLOv8 (Ultralytics)
- NumPy
- PyTorch
- Streamlit (for UI)
├── analysis_results/ # Output results
├── venv/ # Virtual environment (ignored)
├── chatbot_interface.py # Chat interaction module
├── main.py # Main entry point
├── ui_interface.py # User interface
├── video_processor.py # Video processing logic
├── yolov8m.pt # YOLOv8 model (not uploaded to GitHub)


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/AI-Video-Analysis.git
cd AI-Video-Analysis
2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows
3️⃣ Install Dependencies
pip install ultralytics opencv-python numpy torch streamlit
▶️ How to Run
Run Main Program
python main.py
OR Run UI Interface
python ui_interface.py
OR Run as Web App
streamlit run ui_interface.py
📊 Output

Processed videos and results are saved in:

analysis_results/
---

## 📂 Project Structure

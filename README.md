# AI Hazard Recognition System

This project is a full-stack application for real-time hazard recognition using **YOLOv8**, **DeepSORT**, and **FastAPI** for backend services, with a **React** frontend for visualization and control.
## Features
- **Real-time hazard detection** with YOLOv8
- **Zone monitoring** (multi-polygon hazard zones)
- **Object tracking** using DeepSORT
- **Event logging & APIs** with FastAPI
- **React-based UI** for live video stream, polygon editing, and zone control
## Project Structure
reactapp/
│
├── backend/ # FastAPI + ML processing
├── frontend/ # React UI
└── README.md

## Setup Instructions

### 1. Clone the repo
git clone https://github.com/jp2501/ai-hazard-recognition.git
cd ai-hazard-recognition

### 2. Backend Setup (FastAPI + ML)
cd backend
# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # (Linux/Mac)
.\.venv\Scripts\activate    # (Windows)
# Install dependencies
pip install -r requirements.txt
# Run the backend:
uvicorn main:app --reload
or
python -m uvicorn main:app --reload
Backend will start at: http://127.0.0.1:8000

### 3. Frontend Setup (React)
cd ../frontend
# Install dependencies
npm install
# Start React dev server
npm start
Frontend will start at: http://localhost:3000

## 4. Access the App
Open the frontend at http://localhost:3000
The frontend will talk to the backend (http://127.0.0.1:8000)

## Notes
Model weights (.pt files) are not included in GitHub. Place your YOLOv8 model in backend/ before running.
Logs, uploads, and snapshots are ignored (not committed).
For production, use uvicorn main:app --host 0.0.0.0 --port 8000 or Docker.

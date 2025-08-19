from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
import os
import threading

from polygon_utils import save_polygon, load_polygon
from video_utils import save_uploaded_video, capture_first_frame
from stream_generator import gen_stream
from logs_api import router as logs_router

app = FastAPI()
app.mount("/snapshots", StaticFiles(directory="snapshots"), name="snapshots")
app.include_router(logs_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load YOLO model
model = YOLO("yolov8m.pt").to("cuda")

# State dictionaries
video_paths = {1: "video_1.mp4", 2: "video_2.mp4"}
polygon_paths = {1: "polygon_1.npy", 2: "polygon_2.npy"}
screenshot_paths = {1: "screenshot_1.jpg", 2: "screenshot_2.jpg"}
confidences = {1: 0.5, 2: 0.5}
lock = threading.Lock()

@app.post("/upload_video_{index}")
async def upload_video(index: int, file: UploadFile):
    save_uploaded_video(file, video_paths[index])
    capture_first_frame(video_paths[index], screenshot_paths[index])
    return {"status": "uploaded", "stream": index}

@app.post("/capture_screenshot_{index}")
async def capture_screenshot(index: int):
    capture_first_frame(video_paths[index], screenshot_paths[index])
    return {"status": "screenshot captured"}

@app.get("/get_screenshot_{index}")
def get_screenshot(index: int):
    path = screenshot_paths.get(index)
    if path and os.path.exists(path):
        return FileResponse(path, media_type="image/jpeg")
    return {"status": "screenshot not found"}

@app.post("/set_polygon_{index}")
async def set_polygon(index: int, request: Request):
    data = await request.json()
    polygons = data.get("polygons", [])
    with lock:
        save_polygon(polygon_paths[index], polygons)
    return {"status": "polygon updated", "stream": index}

@app.post("/set_confidence_{index}")
async def set_confidence(index: int, request: Request):
    data = await request.json()
    val = data.get("confidence", 0.5)
    confidences[index] = float(val)
    return {"status": "confidence updated", "value": confidences[index]}

@app.get("/stream_{index}")
def stream(index: int, request: Request):
    quality = request.query_params.get("quality", "low")
    sharpness = float(request.query_params.get("sharpness", 1.0))
    gamma = float(request.query_params.get("gamma", 1.0))
    deepsort = request.query_params.get("deepsort", "false").lower() == "true"

    return StreamingResponse(
        gen_stream(
            index=index,
            video_path=video_paths[index],
            polygon_path=polygon_paths[index],
            model=model,
            confidence=confidences[index],
            quality=quality,
            sharpness=sharpness,
            gamma=gamma,
            deepsort=deepsort,
        ),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# ✅ NEW: Switch between webcam and video dynamically
@app.post("/switch_stream_{index}")
async def switch_stream(index: int, request: Request):
    data = await request.json()
    new_source = data.get("video_path", "webcam")
    confidence = float(data.get("confidence", confidences.get(index, 0.5)))

    with lock:
        video_paths[index] = new_source
        confidences[index] = confidence
        capture_first_frame(new_source, screenshot_paths[index])

    return JSONResponse(content={"status": "stream switched", "stream": index, "source": new_source})

@app.get("/video_feed_{index}")
def video_feed(index: int,
               quality: str = "low",
               sharpness: float = 1.0,
               gamma: float = 1.0,
               deepsort: bool = True):
    webcam_path = 0  # Default webcam index
    polygon_path = polygon_paths[index]
    
    return StreamingResponse(
        gen_stream(
            index=index,
            video_path=webcam_path,
            polygon_path=polygon_path,
            model=model,
            confidence=confidences.get(index, 0.5),
            quality=quality,
            sharpness=sharpness,
            gamma=gamma,
            deepsort=deepsort
        ),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
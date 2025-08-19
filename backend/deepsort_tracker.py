import torch
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort

class DeepSortTracker:
    def __init__(self):
        self.tracker = DeepSort(max_age=20)

    def update(self, yolo_results, frame):
        detections = []

        # Extract YOLO results (assumes YOLOv8 or similar format)
        for result in yolo_results:
            for box, cls, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
                if int(cls) == 0:  # Only track 'person' class
                    x1, y1, x2, y2 = box.int().tolist()
                    detections.append(([x1, y1, x2 - x1, y2 - y1], conf.item(), 'person'))

        # Pass frame to get embeddings (required)
        tracks = self.tracker.update_tracks(detections, frame=frame)

        # Return tracking info (track_id and bounding box)
        tracked = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            x1, y1, x2, y2 = track.to_ltrb()
            tracked.append({
                "track_id": track.track_id,
                "bbox": (int(x1), int(y1), int(x2), int(y2))
            
            })
        return tracked


import cv2
import time
import numpy as np
from adaptive_deblur import enhance_adaptive
from polygon_utils import load_polygon, save_polygon  # ✅ Save function
from event_logger import log_event
from deepsort_tracker import DeepSortTracker


def gen_stream(index, video_path, polygon_path, model, confidence, quality, sharpness, gamma, deepsort=False):
    if video_path == "webcam":
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"[Error] Unable to open video source: {video_path}")
        return

    measured_fps = 0.0
    frame_count = 0
    fps_calc_start = time.time()
    tracker = DeepSortTracker()

    while cap.isOpened():
        loop_start = time.time()
        ret, frame = cap.read()
        if not ret:
            print(f"[Warning] Frame not received from: {video_path}")
            break

        frame = cv2.resize(frame, (640, 480))
        enhanced = frame.copy()

        if quality == "high":
            enhanced = enhance_adaptive(enhanced, sharpness=sharpness, gamma=gamma)

        results = model(enhanced, conf=confidence, iou=0.4)
        zones = load_polygon(polygon_path)
        polygon_active = len(zones) > 0
        alert_triggered = False

        def is_inside_zone(x, y, points):
            pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
            return cv2.pointPolygonTest(pts, (x, y), False) >= 0

        # ✅ Extract boxes and class IDs
        detected_chairs = []
        person_boxes = []

        for box in results[0].boxes.data:
            x1, y1, x2, y2, score, cls = box.tolist()
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            class_id = int(cls)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            if class_id == 0:  # person
                person_boxes.append((x1, y1, x2, y2, cx, cy))
            elif class_id == 56:  # chair
                detected_chairs.append((cx, cy, (x1, y1, x2, y2)))

        # ✅ Zone logic and drawing
        for zone in zones:
            base_color = zone.get("color", "red")
            label = zone.get("label", "Zone")
            points = zone.get("points", [])
            if len(points) < 3:
                continue

            dynamic_color = base_color
            dynamic_label = label

            # ✅ Chair distance logic only if red zone
            if base_color == "red":
                chairs_in_zone = [(cx, cy) for cx, cy, _ in detected_chairs if is_inside_zone(cx, cy, points)]
                if len(chairs_in_zone) >= 2:
                    (x1, y1), (x2, y2) = chairs_in_zone[:2]
                    dist = np.linalg.norm(np.array([x1, y1]) - np.array([x2, y2]))
                    if 5 <= dist <= 500:
                        dynamic_color = "green"
                        dynamic_label = "Safe Zone"
                    else:
                        dynamic_color = "red"
                else:
                    dynamic_color = "red"

            color_rgb = (0, 0, 255) if dynamic_color == "red" else (0, 165, 255) if dynamic_color == "orange" else (0, 255, 0)
            polygon = cv2.convexHull(np.array(points, dtype=np.int32)).reshape((-1, 1, 2))

            cv2.polylines(enhanced, [polygon], isClosed=True, color=color_rgb, thickness=2)
            overlay = enhanced.copy()
            cv2.fillPoly(overlay, [polygon], color_rgb)
            enhanced = cv2.addWeighted(overlay, 0.3, enhanced, 0.7, 0)
            cv2.putText(enhanced, dynamic_label, tuple(polygon[0][0]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_rgb, 2)

            # Save dynamic color to zone (for person detection check)
            zone["__dynamic_color"] = dynamic_color

        # ✅ Tracking (persons only)
        if deepsort:
            tracked_persons = tracker.update(results, enhanced)
            for person in tracked_persons:
                x1, y1, x2, y2 = person["bbox"]
                track_id = person["track_id"]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                cv2.rectangle(enhanced, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(enhanced, f"Person ID {track_id}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                for zone in zones:
                    if is_inside_zone(cx, cy, zone.get("points", [])):
                        zone_color = zone.get("color", "red")
                        if zone_color == "red":
                            cv2.putText(enhanced, "PERSON IN RED ZONE", (20, 40),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                            if not alert_triggered:
                                log_event(index, "violation", confidence, enhanced, True)
                                alert_triggered = True
                        elif zone_color == "green":
                            cv2.putText(enhanced, "PERSON IN GREEN ZONE", (20, 40),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                        break
        # ✅ Draw chairs
        for i, (cx, cy, (x1, y1, x2, y2)) in enumerate(detected_chairs):
            cv2.rectangle(enhanced, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.putText(enhanced, f"Chair ID {i+1}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

        # ✅ FPS
        frame_count += 1
        duration = time.time() - fps_calc_start
        if duration >= 1.0:
            measured_fps = frame_count / duration
            frame_count = 0
            fps_calc_start = time.time()

        cv2.putText(
            enhanced,
            f"Cam {index} | FPS: {measured_fps:.1f}",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )

        ret, buffer = cv2.imencode(".jpg", enhanced)
        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

        elapsed = time.time() - loop_start
        if elapsed < (1.0 / 12.0):
            time.sleep((1.0 / 12.0) - elapsed)

    cap.release()

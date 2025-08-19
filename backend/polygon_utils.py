import numpy as np
import os

def save_polygon(path, polygon_data):
    tmp_path = path + ".tmp"
    with open(tmp_path, "wb") as f:
        # Save the full list of dicts: each with label, color, points
        np.save(f, polygon_data, allow_pickle=True)
    os.replace(tmp_path, path)

def load_polygon(path):
    try:
        with open(path, "rb") as f:
            data = np.load(f, allow_pickle=True)
            # Ensure output is a list of dicts with 'points'
            if isinstance(data, np.ndarray):
                return list(data)
    except Exception as e:
        print(f"[Polygon Load Error] {e}")
    return []

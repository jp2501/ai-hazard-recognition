export async function uploadVideo(streamId, file) {
  const formData = new FormData();
  formData.append("file", file);
  await fetch(`http://127.0.0.1:8000/upload_video_${streamId}`, {
    method: "POST",
    body: formData,
  });
}

export async function setPolygon(streamId, polygons) {
  // Each polygon must have: { label, color, points }
  await fetch(`http://127.0.0.1:8000/set_polygon_${streamId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ polygons }),  // Pass full zone structure
  });
}

export async function setConfidence(streamId, confidence) {
  await fetch(`http://127.0.0.1:8000/set_confidence_${streamId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confidence }),
  });
}

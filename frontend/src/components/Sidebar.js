import React from "react";

const Sidebar = ({ selectedCamera, setSelectedCamera, setVideoSource }) => {
  const handleCameraChange = (event) => {
    setSelectedCamera(parseInt(event.target.value));
  };

  const handleSourceChange = (event) => {
    setVideoSource(event.target.value);
  };

  return (
    <div className="sidebar">
      <h2>Controls</h2>
      <div>
        <label>Select Camera:</label>
        <select value={selectedCamera} onChange={handleCameraChange}>
          <option value={1}>Camera 1</option>
          <option value={2}>Camera 2</option>
        </select>
      </div>
      <div style={{ marginTop: "10px" }}>
        <label>Stream Source:</label>
        <select onChange={handleSourceChange} defaultValue="video_1.mp4">
          <option value="video_1.mp4">Video File</option>
          <option value="webcam">Webcam</option>
        </select>
      </div>
    </div>
  );
};

export default Sidebar;

import React, { useState } from "react";
import LogsDashboard from "./components/LogsDashboard";
import StreamCard from "./components/StreamCard";
import "./App.css";

function App() {
  const [view, setView] = useState("monitor");
  const [videoStatus, setVideoStatus] = useState({ 1: false, 2: false });

  return (
    <div className="App">
      <h2>AI Static Hazard Monitoring System</h2>
      <div className="nav-tabs">
        <button onClick={() => setView("monitor")} className={view === "monitor" ? "active" : ""}>
          🎥 Monitor
        </button>
        <button onClick={() => setView("logs")} className={view === "logs" ? "active" : ""}>
          📄 Dashboard
        </button>
      </div>

      <div style={{ display: view === "monitor" ? "block" : "none" }}>
        <div className="streams-grid">
          <StreamCard
            streamId={1}
            videoUploaded={videoStatus[1]}
            setVideoUploaded={(status) =>
              setVideoStatus((prev) => ({ ...prev, 1: status }))
            }
          />
          <StreamCard
            streamId={2}
            videoUploaded={videoStatus[2]}
            setVideoUploaded={(status) =>
              setVideoStatus((prev) => ({ ...prev, 2: status }))
            }
          />
        </div>
      </div>

      <div style={{ display: view === "logs" ? "block" : "none" }}>
        <LogsDashboard />
      </div>
    </div>
  );
}

export default App;

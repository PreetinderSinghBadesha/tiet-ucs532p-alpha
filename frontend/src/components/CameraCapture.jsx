/**
 * CameraCapture.jsx — Step 1: Live webcam feed with oval overlay + file upload fallback.
 */

import { useState, useRef } from "react";
import { useCamera } from "../hooks/useCamera";

export default function CameraCapture({ onCapture }) {
  const { videoRef, canvasRef, error, isReady, startCamera, stopCamera, captureImage } = useCamera();

  const [mode, setMode] = useState("idle"); // idle | camera | preview | upload
  const [preview, setPreview] = useState(null);
  const [uploadPreview, setUploadPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleStartCamera = async () => {
    setMode("camera");
    await startCamera();
  };

  const handleCapture = () => {
    const b64 = captureImage();
    if (!b64) return;
    stopCamera();
    setPreview(b64);
    setMode("preview");
  };

  const handleRetake = () => {
    setPreview(null);
    setMode("idle");
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      setUploadPreview(ev.target.result);
      setMode("upload");
    };
    reader.readAsDataURL(file);
  };

  const handleConfirm = () => {
    const image = preview || uploadPreview;
    if (image) onCapture(image);
  };

  return (
    <div className="capture-container">
      <div className="capture-hero">
        <h1 className="capture-title">Skin Analysis</h1>
        <p className="capture-subtitle">
          Position your face clearly in good lighting for the most accurate results.
        </p>
      </div>

      {mode === "idle" && (
        <div className="capture-options">
          <button id="btn-start-camera" className="btn btn-primary" onClick={handleStartCamera}>
            <span className="btn-icon">📷</span>
            Use Camera
          </button>
          <div className="divider"><span>or</span></div>
          <button id="btn-upload" className="btn btn-secondary" onClick={() => fileInputRef.current.click()}>
            <span className="btn-icon">🗂️</span>
            Upload Photo
          </button>
          <input
            ref={fileInputRef}
            id="file-upload-input"
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
        </div>
      )}

      {mode === "camera" && (
        <div className="camera-view">
          {error && <div className="camera-error">{error}</div>}
          <div className="video-frame">
            <video
              ref={videoRef}
              id="camera-video"
              autoPlay
              playsInline
              muted
              className="camera-video"
              style={{ transform: "scaleX(-1)" }}
            />
            {/* Oval SVG guide overlay */}
            <svg className="face-overlay" viewBox="0 0 100 100" preserveAspectRatio="none">
              <ellipse
                cx="50" cy="48" rx="28" ry="36"
                fill="none"
                stroke="rgba(255,255,255,0.7)"
                strokeWidth="0.8"
                strokeDasharray="4 2"
              />
            </svg>
            <p className="overlay-hint">Align your face within the oval</p>
          </div>
          <canvas ref={canvasRef} id="capture-canvas" style={{ display: "none" }} />
          <div className="camera-controls">
            <button id="btn-capture" className="btn btn-capture" onClick={handleCapture} disabled={!isReady}>
              {isReady ? "📸 Capture" : "Initialising..."}
            </button>
            <button id="btn-cancel-camera" className="btn btn-ghost" onClick={() => { stopCamera(); setMode("idle"); }}>
              Cancel
            </button>
          </div>
        </div>
      )}

      {(mode === "preview" || mode === "upload") && (
        <div className="preview-view">
          <div className="preview-frame">
            <img
              src={preview || uploadPreview}
              alt="Captured face"
              className="preview-image"
              id="preview-img"
            />
            <div className="preview-badge">✓ Photo ready</div>
          </div>
          <div className="preview-controls">
            <button id="btn-confirm" className="btn btn-primary" onClick={handleConfirm}>
              Analyse Skin →
            </button>
            <button id="btn-retake" className="btn btn-ghost" onClick={handleRetake}>
              Retake / Change
            </button>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="capture-tips">
        {["Remove glasses for best results", "Face the light source directly", "No filters or heavy makeup"].map(
          (tip, i) => (
            <div className="tip-chip" key={i}>
              <span className="tip-dot" />
              {tip}
            </div>
          )
        )}
      </div>
    </div>
  );
}

/**
 * App.jsx — DERMA.ai 3-step flow: Capture → Lifestyle → Report
 */

import { useState } from "react";
import CameraCapture from "./components/CameraCapture";
import LifestyleForm from "./components/LifestyleForm";
import SkinReport from "./components/SkinReport";
import { analyzeSkin } from "./api/dermaApi";

const STEPS = ["Capture", "Lifestyle", "Report"];

function StepIndicator({ current }) {
  return (
    <nav className="step-nav" aria-label="Progress">
      {STEPS.map((label, i) => (
        <div key={i} className="step-item">
          <div
            className={`step-dot ${i < current ? "step-dot--done" : i === current ? "step-dot--active" : ""
              }`}
            aria-current={i === current ? "step" : undefined}
          >
            {i < current ? "✓" : i + 1}
          </div>
          <span className={`step-label ${i === current ? "step-label--active" : ""}`}>{label}</span>
          {i < STEPS.length - 1 && <div className={`step-line ${i < current ? "step-line--done" : ""}`} />}
        </div>
      ))}
    </nav>
  );
}

function LoadingOverlay({ message }) {
  return (
    <div className="loading-overlay" role="status" aria-live="polite">
      <div className="loading-card">
        <div className="loading-spinner" />
        <p className="loading-title">Analysing your skin…</p>
        <p className="loading-sub">{message}</p>
        <div className="loading-steps">
          {["Detecting face", "Extracting regions", "Running CV pipeline", "Generating report"].map(
            (s, i) => (
              <span key={i} className="loading-step" style={{ animationDelay: `${i * 0.4}s` }}>
                {s}
              </span>
            )
          )}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [step, setStep] = useState(0);
  const [capturedImage, setCapturedImage] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleCapture = (imageBase64) => {
    setCapturedImage(imageBase64);
    setStep(1);
  };

  const handleLifestyleSubmit = async (lifestyle) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const result = await analyzeSkin(capturedImage, lifestyle);
      setAnalysisResult(result);
      setStep(2);
    } catch (err) {
      if (err.code === "no_face_detected") {
        setErrorMsg("No face was detected in the photo. Please go back and capture a clear face image.");
        setStep(0);
      } else {
        setErrorMsg(err.message || "Analysis failed. Please try again.");
        setAnalysisResult({ success: false, message: err.message });
        setStep(2);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRestart = () => {
    setStep(0);
    setCapturedImage(null);
    setAnalysisResult(null);
    setErrorMsg(null);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="logo">
          <span className="logo-icon">✦</span>
          <span className="logo-text">DERMA<span className="logo-dot">.ai</span></span>
        </div>
        {/* <p className="header-tagline">Classical CV · No cloud · Privacy first</p> */}
      </header>

      {/* Step indicator */}
      <StepIndicator current={step} />

      {/* Error toast */}
      {errorMsg && (
        <div className="error-toast" role="alert" id="error-toast">
          ⚠️ {errorMsg}
          <button className="toast-close" onClick={() => setErrorMsg(null)}>×</button>
        </div>
      )}

      {/* Loading overlay */}
      {loading && <LoadingOverlay message="This may take a few seconds…" />}

      {/* Step content */}
      <main className="app-main">
        {step === 0 && <CameraCapture onCapture={handleCapture} />}
        {step === 1 && (
          <LifestyleForm
            onSubmit={handleLifestyleSubmit}
            onBack={() => setStep(0)}
          />
        )}
        {step === 2 && (
          <SkinReport result={analysisResult} onBack={handleRestart} />
        )}
      </main>

      {/* Footer */}
      {/* <footer className="app-footer">
        <p>DERMA.ai · Classical Computer Vision · Not a medical device</p>
      </footer> */}
    </div>
  );
}

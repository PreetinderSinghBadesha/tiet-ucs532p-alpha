/**
 * SkinReport.jsx — Step 3: Animated skin health report with condition cards
 * and expandable recommendations.
 */

import { useState, useEffect, useRef } from "react";

// ── Helpers ────────────────────────────────────────────────────────────────────

const SEVERITY_META = {
  none:     { label: "None",     color: "#22C55E", bg: "#F0FDF4" },
  mild:     { label: "Mild",     color: "#EAB308", bg: "#FEFCE8" },
  moderate: { label: "Moderate", color: "#F97316", bg: "#FFF7ED" },
  severe:   { label: "Severe",   color: "#EF4444", bg: "#FEF2F2" },
};

function ScoreRing({ score, size = 180 }) {
  const [displayScore, setDisplayScore] = useState(0);
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (displayScore / 100) * circumference;
  const color = score >= 70 ? "#22C55E" : score >= 45 ? "#EAB308" : "#EF4444";

  useEffect(() => {
    let frame;
    const animate = () => {
      setDisplayScore((prev) => {
        if (prev >= score) return score;
        frame = requestAnimationFrame(animate);
        return Math.min(prev + 1.5, score);
      });
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, [score]);

  return (
    <div className="score-ring-wrap" aria-label={`Skin health score: ${Math.round(displayScore)} out of 100`}>
      <svg width={size} height={size} className="score-ring-svg">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="#E5E7EB" strokeWidth="12" />
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={color} strokeWidth="12"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dashoffset 0.05s linear, stroke 0.5s ease" }}
        />
      </svg>
      <div className="score-ring-label">
        <span className="score-number" style={{ color }}>{Math.round(displayScore)}</span>
        <span className="score-sub">/ 100</span>
        <span className="score-caption">Skin Health</span>
      </div>
    </div>
  );
}

function SeverityBadge({ severity }) {
  const meta = SEVERITY_META[severity] || SEVERITY_META.none;
  return (
    <span
      className="severity-badge"
      style={{ color: meta.color, background: meta.bg, borderColor: meta.color + "40" }}
    >
      {meta.label}
    </span>
  );
}

function ConditionCard({ rec, index }) {
  const [open, setOpen] = useState(false);
  const meta = SEVERITY_META[rec.severity] || SEVERITY_META.none;

  return (
    <div
      className={`condition-card ${open ? "condition-card--open" : ""}`}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      <button
        className="condition-header"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        id={`condition-btn-${rec.condition_key}`}
      >
        <div className="condition-title-row">
          <div className="condition-bar" style={{ background: meta.color }} />
          <span className="condition-name">{rec.condition}</span>
          <SeverityBadge severity={rec.severity} />
        </div>
        <span className={`chevron ${open ? "chevron--up" : ""}`}>›</span>
      </button>

      {open && (
        <div className="condition-body">
          {rec.causes?.length > 0 && (
            <div className="rec-section">
              <h4 className="rec-heading">Root Causes</h4>
              <ul className="rec-list">
                {rec.causes.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            </div>
          )}

          {rec.routine_steps?.length > 0 && (
            <div className="rec-section">
              <h4 className="rec-heading">Skincare Routine</h4>
              <div className="routine-steps">
                {rec.routine_steps.map((s, i) => (
                  <div className="routine-step" key={i}>
                    <div className="step-number">{i + 1}</div>
                    <div className="step-body">
                      <span className="step-name">{s.step}</span>
                      <span className="step-instruction">{s.instruction}</span>
                      <span className="step-product">💊 {s.product_type}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {rec.ingredients_to_use?.length > 0 && (
            <div className="rec-section ingredients-row">
              <div>
                <h4 className="rec-heading">✅ Use</h4>
                <div className="tag-list">
                  {rec.ingredients_to_use.map((ing, i) => (
                    <span key={i} className="tag tag--green">{ing}</span>
                  ))}
                </div>
              </div>
              {rec.ingredients_to_avoid?.length > 0 && (
                <div>
                  <h4 className="rec-heading">❌ Avoid</h4>
                  <div className="tag-list">
                    {rec.ingredients_to_avoid.map((ing, i) => (
                      <span key={i} className="tag tag--red">{ing}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {rec.lifestyle_changes?.length > 0 && (
            <div className="rec-section">
              <h4 className="rec-heading">Lifestyle Changes</h4>
              <ul className="rec-list">
                {rec.lifestyle_changes.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function LifestyleImpactSection({ lifestyle_impact }) {
  const entries = Object.entries(lifestyle_impact || {});
  if (entries.length === 0) return null;
  return (
    <div className="lifestyle-impact">
      <h3 className="section-heading">⚡ Lifestyle Factors Affecting Your Skin</h3>
      {entries.map(([key, msg]) => (
        <div key={key} className="impact-card">
          <span className="impact-icon">⚠️</span>
          <p className="impact-text">{msg}</p>
        </div>
      ))}
    </div>
  );
}

export default function SkinReport({ result, onBack }) {
  if (!result || !result.success) {
    return (
      <div className="report-error">
        <span className="error-icon">⚠️</span>
        <h2>Analysis Failed</h2>
        <p>{result?.message || "An unknown error occurred."}</p>
        <button id="btn-back-error" className="btn btn-primary" onClick={onBack}>Try Again</button>
      </div>
    );
  }

  return (
    <div className="report-container">
      {/* Header */}
      <div className="report-header">
        <h1 className="capture-title">Your Skin Report</h1>
        <p className="capture-subtitle">
          Analysed in {result.processing_time_ms?.toFixed(0)}ms using classical computer vision.
        </p>
      </div>

      {/* Score ring & Annotated Image */}
      <div className="score-section" style={{ display: "flex", flexDirection: "column", gap: "24px", alignItems: "center" }}>
        <div style={{ display: "flex", gap: "32px", flexWrap: "wrap", justifyContent: "center", alignItems: "center" }}>
          <div>
            <ScoreRing score={result.overall_score} />
          </div>
          {result.annotated_image && (
            <div className="annotated-image-container" style={{ maxWidth: "240px", borderRadius: "14px", overflow: "hidden", boxShadow: "0 4px 16px rgba(0,0,0,0.12)", background: "#000" }}>
              <img src={result.annotated_image} alt="Analyzed Face Regions" style={{ width: "100%", display: "block", aspectRatio: "3/4", objectFit: "cover" }} />
            </div>
          )}
        </div>
        <p className="score-description">
          {result.overall_score >= 75
            ? "Your skin is in great health! Keep up the routine."
            : result.overall_score >= 50
            ? "Your skin is doing well with some areas to improve."
            : "Your skin needs attention — the routine below will help."}
        </p>
      </div>

      {/* Dermatologist banner */}
      {result.see_dermatologist && (
        <div className="derm-banner" id="derm-banner" role="alert">
          <span className="derm-icon">🏥</span>
          <div>
            <strong>Professional Consultation Recommended</strong>
            <p>One or more conditions were detected at a severe level. We strongly recommend seeing a board-certified dermatologist for personalised medical treatment.</p>
          </div>
        </div>
      )}

      {/* Lifestyle impact */}
      <LifestyleImpactSection lifestyle_impact={result.lifestyle_impact} />

      {/* Condition cards */}
      <div className="conditions-section">
        <h3 className="section-heading">📋 Condition Breakdown</h3>
        {result.recommendations?.map((rec, i) => (
          <ConditionCard key={rec.condition_key} rec={rec} index={i} />
        ))}
      </div>

      {/* Disclaimer + back */}
      <div className="report-footer">
        <p className="disclaimer">{result.disclaimer}</p>
        <button id="btn-new-analysis" className="btn btn-secondary" onClick={onBack}>
          ← Start New Analysis
        </button>
      </div>
    </div>
  );
}

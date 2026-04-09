/**
 * LifestyleForm.jsx — Step 2: Lifestyle questionnaire using sliders and radio buttons.
 */

import { useState } from "react";

const SKIN_TYPES = ["Dry", "Oily", "Combination", "Normal", "Sensitive"];
const DIET_QUALITIES = ["Poor", "Average", "Good", "Excellent"];
const SKINCARE_ROUTINES = ["None", "Basic cleansing", "Full routine", "Medical"];

function SliderField({ id, label, min, max, value, onChange, unit, emoji }) {
  const pct = ((value - min) / (max - min)) * 100;
  return (
    <div className="form-field">
      <div className="field-header">
        <label htmlFor={id} className="field-label">
          <span className="field-emoji">{emoji}</span> {label}
        </label>
        <span className="field-value">{value} <span className="field-unit">{unit}</span></span>
      </div>
      <div className="slider-track">
        <input
          id={id}
          type="range"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="slider"
          style={{ "--pct": `${pct}%` }}
        />
        <div className="slider-fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="slider-labels">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}

function RadioGroup({ id, legend, options, value, onChange, emoji }) {
  return (
    <div className="form-field">
      <p className="field-label">
        <span className="field-emoji">{emoji}</span> {legend}
      </p>
      <div className="radio-group" role="group" aria-label={legend}>
        {options.map((opt) => (
          <label
            key={opt}
            className={`radio-chip ${value === opt.toLowerCase() ? "radio-chip--active" : ""}`}
            htmlFor={`${id}-${opt}`}
          >
            <input
              id={`${id}-${opt}`}
              type="radio"
              name={id}
              value={opt.toLowerCase()}
              checked={value === opt.toLowerCase()}
              onChange={() => onChange(opt.toLowerCase())}
              className="sr-only"
            />
            {opt}
          </label>
        ))}
      </div>
    </div>
  );
}

export default function LifestyleForm({ onSubmit, onBack }) {
  const [sleepHours, setSleepHours] = useState(7);
  const [waterGlasses, setWaterGlasses] = useState(8);
  const [stressLevel, setStressLevel] = useState(5);
  const [dietQuality, setDietQuality] = useState("good");
  const [skincare, setSkincare] = useState("basic cleansing");
  const [skinType, setSkinType] = useState("normal");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      sleep_hours: sleepHours,
      water_glasses: waterGlasses,
      stress_level: stressLevel,
      diet_quality: dietQuality,
      current_skincare: skincare,
      skin_type: skinType,
    });
  };

  return (
    <div className="form-container">
      <div className="capture-hero">
        <h1 className="capture-title">Lifestyle Profile</h1>
        <p className="capture-subtitle">
          These factors significantly influence your skin health. All data stays on your device.
        </p>
      </div>

      <form id="lifestyle-form" className="lifestyle-form" onSubmit={handleSubmit}>
        <div className="form-section">
          <h3 className="section-heading">Daily Habits</h3>
          <SliderField
            id="sleep-slider"
            label="Sleep last night"
            min={3} max={10} value={sleepHours}
            onChange={setSleepHours}
            unit="hrs" emoji="😴"
          />
          <SliderField
            id="water-slider"
            label="Water intake today"
            min={0} max={12} value={waterGlasses}
            onChange={setWaterGlasses}
            unit="glasses" emoji="💧"
          />
          <SliderField
            id="stress-slider"
            label="Stress level"
            min={1} max={10} value={stressLevel}
            onChange={setStressLevel}
            unit="/ 10" emoji="🧠"
          />
        </div>

        <div className="form-section">
          <h3 className="section-heading">Diet & Skincare</h3>
          <RadioGroup
            id="diet"
            legend="Diet quality"
            options={DIET_QUALITIES}
            value={dietQuality}
            onChange={setDietQuality}
            emoji="🥗"
          />
          <RadioGroup
            id="skincare"
            legend="Current skincare routine"
            options={SKINCARE_ROUTINES}
            value={skincare}
            onChange={setSkincare}
            emoji="🧴"
          />
        </div>

        <div className="form-section">
          <h3 className="section-heading">Skin Type</h3>
          <RadioGroup
            id="skin-type"
            legend="How would you describe your skin?"
            options={SKIN_TYPES}
            value={skinType}
            onChange={setSkinType}
            emoji="✨"
          />
        </div>

        <div className="form-actions">
          <button type="button" id="btn-back-form" className="btn btn-ghost" onClick={onBack}>
            ← Back
          </button>
          <button type="submit" id="btn-analyze" className="btn btn-primary btn-large">
            Run Analysis →
          </button>
        </div>
      </form>
    </div>
  );
}

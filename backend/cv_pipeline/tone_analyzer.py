"""
tone_analyzer.py — Skin tone uniformity, redness, and hyperpigmentation.

Pipeline:
  1. Convert full-face ROI to HSV
  2. Create skin mask via cv2.inRange (HSV skin thresholds)
  3. Uniformity = 1 − (std(H-channel within mask) / 180)
  4. Redness index = mean S-value in high-saturation skin areas
  5. Hyperpigmentation = find dark spots via V-channel thresholding

Public API:
    analyze(regions) → dict
"""

import cv2
import numpy as np
from config import (
    SKIN_HSV_LOWER,
    SKIN_HSV_UPPER,
    HYPERPIGMENTATION_V_THRESHOLD,
    HYPERPIGMENTATION_MIN_AREA,
    SEVERITY,
)


def _severity_label(score: float) -> str:
    if score < SEVERITY["mild"]:
        return "none"
    elif score < SEVERITY["moderate"]:
        return "mild"
    elif score < SEVERITY["severe"]:
        return "moderate"
    return "severe"


def _overall_tone_label(uniformity: float) -> str:
    if uniformity > 0.80:
        return "even"
    elif uniformity > 0.65:
        return "slightly_uneven"
    return "uneven"


def analyze(regions: dict) -> dict:
    """
    Analyse skin tone from the full-face ROI.

    Returns
    -------
    {
      "tone_uniformity": float,         # 0–1 (1 = perfectly uniform)
      "redness_index": float,           # 0–100
      "hyperpigmentation_spots": int,
      "overall_tone": str,
      "raw_score": float,               # 0–100
      "severity": str
    }
    """
    roi = regions.get("full_face")
    if roi is None or roi.size == 0:
        return {
            "tone_uniformity": 1.0,
            "redness_index": 0.0,
            "hyperpigmentation_spots": 0,
            "overall_tone": "even",
            "raw_score": 0.0,
            "severity": "none",
        }

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # ── Skin mask ────────────────────────────────────────────────────────────
    lower = np.array(SKIN_HSV_LOWER, dtype=np.uint8)
    upper = np.array(SKIN_HSV_UPPER, dtype=np.uint8)
    skin_mask = cv2.inRange(hsv, lower, upper)

    skin_pixels = int(np.sum(skin_mask > 0))
    if skin_pixels < 50:
        # Fall back: treat the whole ROI as skin if mask is too small
        skin_mask = np.ones(hsv.shape[:2], dtype=np.uint8) * 255

    h_ch = hsv[:, :, 0]
    s_ch = hsv[:, :, 1]
    v_ch = hsv[:, :, 2]

    # ── Tone uniformity ───────────────────────────────────────────────────────
    h_skin = h_ch[skin_mask > 0].astype(np.float32)
    if len(h_skin) > 0:
        h_std = float(h_skin.std())
        tone_uniformity = float(np.clip(1.0 - (h_std / 180.0), 0.0, 1.0))
    else:
        tone_uniformity = 1.0

    # ── Redness index ─────────────────────────────────────────────────────────
    # High-saturation skin pixels with low hue = red/pink tones
    high_sat_mask = (s_ch > 80) & (skin_mask > 0)
    s_red = s_ch[high_sat_mask]
    redness_index = float(np.clip(s_red.mean() / 255 * 100, 0, 100)) if len(s_red) > 0 else 0.0

    # ── Hyperpigmentation ─────────────────────────────────────────────────────
    # Dark spots = low V (dark) within the skin mask
    dark_mask = ((v_ch < HYPERPIGMENTATION_V_THRESHOLD) & (skin_mask > 0)).astype(np.uint8) * 255
    contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hyper_spots = sum(
        1 for c in contours if cv2.contourArea(c) >= HYPERPIGMENTATION_MIN_AREA
    )

    # ── Raw score ─────────────────────────────────────────────────────────────
    uniformity_penalty = (1.0 - tone_uniformity) * 60
    redness_contribution = redness_index * 0.3
    hyper_contribution = min(hyper_spots * 5, 40)
    raw_score = float(np.clip(uniformity_penalty + redness_contribution + hyper_contribution, 0, 100))

    return {
        "tone_uniformity": round(tone_uniformity, 4),
        "redness_index": round(redness_index, 2),
        "hyperpigmentation_spots": hyper_spots,
        "overall_tone": _overall_tone_label(tone_uniformity),
        "raw_score": round(raw_score, 2),
        "severity": _severity_label(raw_score),
    }

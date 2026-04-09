"""
dark_circle_detector.py — Under-eye dark circle analysis.

Pipeline:
  1. Extract L-channel (luminance) from LAB color space
  2. Compare under-eye L mean vs cheek L mean → darkness ratio
  3. Check HSV S-channel for blue/purple pigmentation
  4. Combine into severity

Public API:
    analyze(regions) → dict
"""

import cv2
import numpy as np
from config import (
    DARK_CIRCLE_SEVERITY_MILD,
    DARK_CIRCLE_SEVERITY_MODERATE,
    DARK_CIRCLE_SEVERITY_SEVERE,
    SEVERITY,
)


def _mean_l(roi: np.ndarray) -> float:
    """Mean luminance (LAB L-channel) of a BGR ROI."""
    if roi is None or roi.size == 0:
        return 128.0
    lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
    return float(lab[:, :, 0].mean())


def _mean_saturation(roi: np.ndarray) -> float:
    """Mean HSV saturation of a BGR ROI — high S + low H indicates pigmentation."""
    if roi is None or roi.size == 0:
        return 0.0
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    return float(hsv[:, :, 1].mean())


def _severity_label(darkness_ratio: float) -> str:
    if darkness_ratio < DARK_CIRCLE_SEVERITY_MILD:
        return "none"
    elif darkness_ratio < DARK_CIRCLE_SEVERITY_MODERATE:
        return "mild"
    elif darkness_ratio < DARK_CIRCLE_SEVERITY_SEVERE:
        return "moderate"
    return "severe"


def analyze(regions: dict) -> dict:
    """
    Compute dark circle severity under both eyes.

    Returns
    -------
    {
      "darkness_ratio": float,       # (cheek_L - under_eye_L) / cheek_L
      "pigmentation_score": float,   # 0–100
      "raw_score": float,
      "severity": str
    }
    """
    ue_left = regions.get("under_eye_left")
    ue_right = regions.get("under_eye_right")
    lc = regions.get("left_cheek")
    rc = regions.get("right_cheek")

    # Reference luminance from cheeks (brighter mid-face skin)
    cheek_l_vals = [_mean_l(r) for r in [lc, rc] if r is not None and r.size > 0]
    cheek_l = float(np.mean(cheek_l_vals)) if cheek_l_vals else 160.0

    # Under-eye luminance
    ue_l_vals = [_mean_l(r) for r in [ue_left, ue_right] if r is not None and r.size > 0]
    ue_l = float(np.mean(ue_l_vals)) if ue_l_vals else cheek_l

    darkness_ratio = max(0.0, (cheek_l - ue_l) / (cheek_l + 1e-8))

    # Pigmentation: high saturation in under-eye = blue/purple tone
    ue_s_vals = [_mean_saturation(r) for r in [ue_left, ue_right] if r is not None and r.size > 0]
    ue_s = float(np.mean(ue_s_vals)) if ue_s_vals else 0.0
    pigmentation_score = float(np.clip(ue_s / 255 * 100, 0, 100))

    # Raw 0–100 score
    raw_score = float(np.clip(darkness_ratio * 300 + pigmentation_score * 0.3, 0, 100))

    return {
        "darkness_ratio": round(darkness_ratio, 4),
        "pigmentation_score": round(pigmentation_score, 2),
        "raw_score": round(raw_score, 2),
        "severity": _severity_label(darkness_ratio),
    }

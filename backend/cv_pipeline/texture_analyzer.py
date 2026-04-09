"""
texture_analyzer.py — Skin texture analysis via manual LBP + Laplacian.

LBP implementation uses pure NumPy/OpenCV — no scikit-image.

Pipeline:
  1. Convert ROI to grayscale
  2. Compute 8-neighbour LBP for each pixel → histogram
  3. Roughness = std(histogram) / mean(histogram)
  4. Pore visibility = Laplacian variance (sharpness indicator)
  5. Uniformity = 1 − normalised histogram entropy

Public API:
    analyze(regions) → dict
"""

import cv2
import numpy as np
from config import LBP_NEIGHBORS, LBP_RADIUS, SEVERITY

TEXTURE_REGIONS = ["forehead", "left_cheek", "right_cheek", "nose"]

# Precompute 8-neighbour offsets for radius=1
_LBP_OFFSETS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0,  1),  (1,  1), (1,  0),
    (1,  -1), (0,  -1),
]


def _compute_lbp(gray: np.ndarray) -> np.ndarray:
    """
    Compute uniform LBP texture map for a grayscale image.
    Returns an ndarray of the same H×W shape with LBP codes (0–255).
    """
    h, w = gray.shape
    lbp = np.zeros((h, w), dtype=np.uint8)

    for bit, (dy, dx) in enumerate(_LBP_OFFSETS):
        # Shift the image in the neighbour direction
        shifted = np.roll(np.roll(gray, dy, axis=0), dx, axis=1)
        # Set bit if neighbour >= center
        lbp |= ((shifted >= gray).astype(np.uint8) << bit)

    return lbp


def _analyze_roi(roi: np.ndarray) -> dict:
    """Compute texture metrics for a single BGR ROI."""
    if roi is None or roi.size == 0 or roi.shape[0] < 10 or roi.shape[1] < 10:
        return {"roughness": 0.0, "pore_visibility": 0.0, "uniformity": 1.0}

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # ── LBP ──────────────────────────────────────────────────────────────────
    lbp_map = _compute_lbp(gray)
    hist, _ = np.histogram(lbp_map.ravel(), bins=256, range=(0, 256))
    hist_norm = hist / (hist.sum() + 1e-8)

    lbp_mean = hist_norm.mean()
    lbp_std = hist_norm.std()
    roughness = float(lbp_std / (lbp_mean + 1e-8))   # coefficient of variation

    # ── Laplacian variance (pore sharpness) ───────────────────────────────────
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    pore_visibility = float(lap.var())

    # ── Uniformity (1 − entropy normalised) ───────────────────────────────────
    entropy = -np.sum(hist_norm * np.log2(hist_norm + 1e-8))
    max_entropy = np.log2(256)
    uniformity = float(1.0 - (entropy / max_entropy))

    return {
        "roughness": roughness,
        "pore_visibility": pore_visibility,
        "uniformity": uniformity,
    }


def _severity_label(score: float) -> str:
    if score < SEVERITY["mild"]:
        return "none"
    elif score < SEVERITY["moderate"]:
        return "mild"
    elif score < SEVERITY["severe"]:
        return "moderate"
    return "severe"


def analyze(regions: dict) -> dict:
    """
    Aggregate texture metrics across analysed regions.

    Returns
    -------
    {
      "roughness_score": float,    # 0–100
      "pore_visibility": float,    # 0–100
      "uniformity": float,         # 0–1
      "raw_score": float,
      "severity": str
    }
    """
    roughness_vals, pore_vals, uniformity_vals = [], [], []

    for name in TEXTURE_REGIONS:
        roi = regions.get(name)
        if roi is None:
            continue
        m = _analyze_roi(roi)
        roughness_vals.append(m["roughness"])
        pore_vals.append(m["pore_visibility"])
        uniformity_vals.append(m["uniformity"])

    if not roughness_vals:
        return {"roughness_score": 0, "pore_visibility": 0, "uniformity": 1.0,
                "raw_score": 0, "severity": "none"}

    mean_roughness = float(np.mean(roughness_vals))
    mean_pore = float(np.mean(pore_vals))
    mean_uniformity = float(np.mean(uniformity_vals))

    # Normalise to 0–100
    # roughness: empirically ~0–5 range; pore_visibility ~0–2000 range
    roughness_score = float(np.clip(mean_roughness * 20, 0, 100))
    pore_score = float(np.clip(mean_pore / 20, 0, 100))

    raw_score = roughness_score * 0.6 + pore_score * 0.4

    return {
        "roughness_score": round(roughness_score, 2),
        "pore_visibility": round(pore_score, 2),
        "uniformity": round(mean_uniformity, 4),
        "raw_score": round(raw_score, 2),
        "severity": _severity_label(raw_score),
    }

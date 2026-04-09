"""
wrinkle_detector.py — Fine line and wrinkle detection.

Pipeline:
  1. Gaussian blur to suppress noise
  2. Canny edge detection with tight thresholds (fine-line tuned)
  3. Morphological closing to connect broken line segments
  4. Edge density = non-zero edge pixels / total pixels
  5. HoughLinesP to count long continuous lines

Public API:
    analyze(regions) → dict
"""

import cv2
import numpy as np
from config import (
    WRINKLE_BLUR_KERNEL,
    WRINKLE_CANNY_LOW,
    WRINKLE_CANNY_HIGH,
    WRINKLE_MORPH_KERNEL,
    WRINKLE_HOUGH_MIN_LINE,
    WRINKLE_HOUGH_MAX_GAP,
    SEVERITY,
)

WRINKLE_REGIONS = ["forehead"]   # Primary site; eye-corners derived from landmarks


def _analyze_roi(roi: np.ndarray) -> dict:
    """Detect wrinkles/fine lines in a single BGR ROI."""
    if roi is None or roi.size == 0 or roi.shape[0] < 10 or roi.shape[1] < 10:
        return {"edge_density": 0.0, "line_count": 0}

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # 1. Gaussian blur to reduce noise while preserving structure
    blurred = cv2.GaussianBlur(gray, WRINKLE_BLUR_KERNEL, 0)

    # 2. CLAHE to enhance low-contrast fine lines before Canny
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    enhanced = clahe.apply(blurred)

    # 3. Canny with narrow thresholds to pick up fine lines
    edges = cv2.Canny(enhanced, WRINKLE_CANNY_LOW, WRINKLE_CANNY_HIGH)

    # 4. Morphological closing to connect broken segments
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, WRINKLE_MORPH_KERNEL)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # 5. Edge density
    total_pixels = closed.shape[0] * closed.shape[1]
    edge_pixels = int(np.count_nonzero(closed))
    edge_density = edge_pixels / (total_pixels + 1e-8)

    # 6. HoughLinesP for long continuous lines (actual wrinkles vs noise)
    lines = cv2.HoughLinesP(
        closed,
        rho=1,
        theta=np.pi / 180,
        threshold=15,
        minLineLength=WRINKLE_HOUGH_MIN_LINE,
        maxLineGap=WRINKLE_HOUGH_MAX_GAP,
    )
    line_count = len(lines) if lines is not None else 0

    return {"edge_density": edge_density, "line_count": line_count}


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
    Detect wrinkles across forehead (primary) region.

    Returns
    -------
    {
      "edge_density": float,   # 0–1
      "line_count": int,
      "raw_score": float,      # 0–100
      "severity": str
    }
    """
    total_edge_density = 0.0
    total_line_count = 0
    count = 0

    for name in WRINKLE_REGIONS:
        roi = regions.get(name)
        if roi is None:
            continue
        r = _analyze_roi(roi)
        total_edge_density += r["edge_density"]
        total_line_count += r["line_count"]
        count += 1

    if count == 0:
        return {"edge_density": 0.0, "line_count": 0, "raw_score": 0.0, "severity": "none"}

    mean_density = total_edge_density / count

    # Raw score: edge density contributes most; line count as modifier
    # Empirically: edge density 0.02+ = mild; 0.05+ = moderate; 0.10+ = severe
    density_score = float(np.clip(mean_density * 1000, 0, 80))
    line_score = float(np.clip(total_line_count * 2, 0, 20))
    raw_score = density_score + line_score

    return {
        "edge_density": round(mean_density, 6),
        "line_count": total_line_count,
        "raw_score": round(raw_score, 2),
        "severity": _severity_label(raw_score),
    }

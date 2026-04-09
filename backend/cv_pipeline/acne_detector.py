"""
acne_detector.py — Acne/blemish detection via LAB A-channel analysis.

Pipeline per ROI:
  1. Convert BGR → LAB, extract A-channel (redness indicator)
  2. Gaussian blur → Otsu threshold
  3. Canny edge detection → findContours
  4. Filter contours by area and circularity
  5. Aggregate count, density, redness score across regions

Public API:
    analyze(regions) → dict
"""

import cv2
import numpy as np
from config import (
    ACNE_BLUR_KERNEL,
    ACNE_CANNY_LOW,
    ACNE_CANNY_HIGH,
    ACNE_MIN_CONTOUR_AREA,
    ACNE_MAX_CONTOUR_AREA,
    ACNE_CIRCULARITY_THRESHOLD,
    SEVERITY,
)

# Regions that contribute to acne analysis
ACNE_REGIONS = ["forehead", "left_cheek", "right_cheek", "nose"]


def _circularity(contour) -> float:
    """4π·area / perimeter² — 1.0 = perfect circle, 0 = line."""
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    if perimeter == 0:
        return 0.0
    return (4 * np.pi * area) / (perimeter ** 2)


def _analyze_roi(roi: np.ndarray) -> dict:
    """Detect acne lesions in a single BGR ROI."""
    if roi is None or roi.size == 0 or roi.shape[0] < 5 or roi.shape[1] < 5:
        return {"count": 0, "redness_sum": 0.0, "pixel_count": 0}

    # 1. LAB A-channel (positive = red/magenta, negative = green)
    lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
    a_channel = lab[:, :, 1]

    # 2. Blur & Otsu threshold on A-channel
    blurred = cv2.GaussianBlur(a_channel, ACNE_BLUR_KERNEL, 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 3. Canny edges
    edges = cv2.Canny(thresh, ACNE_CANNY_LOW, ACNE_CANNY_HIGH)

    # 4. Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    qualified = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < ACNE_MIN_CONTOUR_AREA or area > ACNE_MAX_CONTOUR_AREA:
            continue
        if _circularity(c) < ACNE_CIRCULARITY_THRESHOLD:
            continue
        qualified.append(c)

    # 5. Redness in detected lesion areas
    mask = np.zeros(a_channel.shape, dtype=np.uint8)
    cv2.drawContours(mask, qualified, -1, 255, -1)
    redness_sum = float(np.sum(a_channel[mask > 0]))
    pixel_count = int(np.sum(mask > 0))

    return {
        "count": len(qualified),
        "redness_sum": redness_sum,
        "pixel_count": pixel_count,
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
    Analyze all acne-relevant regions and return aggregated stats.

    Returns
    -------
    {
      "count": int,
      "density": float,           # lesions per 1000 px²
      "redness_score": float,     # 0–100
      "severity": str,
      "affected_regions": list[str]
    }
    """
    total_count = 0
    total_redness_sum = 0.0
    total_pixel_count = 0
    total_roi_area = 0
    affected = []

    for name in ACNE_REGIONS:
        roi = regions.get(name)
        if roi is None:
            continue
        result = _analyze_roi(roi)
        if result["count"] > 0:
            affected.append(name)
        total_count += result["count"]
        total_redness_sum += result["redness_sum"]
        total_pixel_count += result["pixel_count"]
        total_roi_area += roi.shape[0] * roi.shape[1]

    density = (total_count / (total_roi_area / 1000)) if total_roi_area > 0 else 0.0

    # Redness score: mean A-channel value in lesion areas, normalised 0–100
    if total_pixel_count > 0:
        mean_a = total_redness_sum / total_pixel_count
        # A-channel in OpenCV LAB ranges 0–255 (128 = neutral)
        redness_score = float(np.clip((mean_a - 128) / 127 * 100, 0, 100))
    else:
        redness_score = 0.0

    # Composite score: weight count + redness
    raw_score = min(100.0, (total_count * 4) + (redness_score * 0.5) + (density * 5))

    return {
        "count": total_count,
        "density": round(density, 3),
        "redness_score": round(redness_score, 2),
        "raw_score": round(raw_score, 2),
        "severity": _severity_label(raw_score),
        "affected_regions": affected,
    }

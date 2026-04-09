"""
region_extractor.py — ROI extraction using dlib 68-point landmarks.

dlib landmark indices used:
  Forehead : synthesised above points 17–26 (eyebrows)
  Left cheek : 1–4
  Right cheek : 12–15
  Under-eye left : 37–41
  Under-eye right : 43–47
  Nose : 27–35
  Full face : entire bounding box

Public API:
    extract_regions(image_bgr, bbox, landmarks) → dict[str, np.ndarray]
"""

import cv2
import numpy as np
from config import FOREHEAD_HEIGHT_RATIO, ROI_BLUR_KERNEL


def _safe_crop(image: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
    """Clamp coordinates to image bounds and return the crop."""
    h, w = image.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    if x2 <= x1 or y2 <= y1:
        return np.zeros((10, 10, 3), dtype=np.uint8)
    return image[y1:y2, x1:x2].copy()


def _blur(roi: np.ndarray) -> np.ndarray:
    """Light Gaussian blur to suppress sensor noise before analysis."""
    if roi.size == 0:
        return roi
    return cv2.GaussianBlur(roi, ROI_BLUR_KERNEL, 0)


def extract_regions(
    image_bgr: np.ndarray,
    bbox: tuple,
    landmarks: np.ndarray,
) -> dict:
    """
    Extract named ROIs from *image_bgr* using dlib landmark positions.

    Parameters
    ----------
    image_bgr : np.ndarray – full input image
    bbox      : (x, y, w, h) – face bounding box
    landmarks : (68, 2) int array – dlib landmark co-ordinates

    Returns
    -------
    dict with keys: forehead, left_cheek, right_cheek,
                    under_eye_left, under_eye_right, nose, full_face
    Values are BGR crops (np.ndarray), lightly blurred.
    """
    x, y, w, h = bbox

    # ── Full face ─────────────────────────────────────────────────────────────
    full_face = _blur(_safe_crop(image_bgr, x, y, x + w, y + h))

    # ── Forehead ──────────────────────────────────────────────────────────────
    # Defined as the band above the eyebrow row (points 17–26)
    brow_y = int(np.mean(landmarks[17:27, 1]))   # mean Y of eyebrow points
    forehead_top = max(0, y)
    forehead_bot = brow_y
    forehead_left = int(landmarks[17, 0])
    forehead_right = int(landmarks[26, 0])
    forehead = _blur(_safe_crop(image_bgr, forehead_left, forehead_top, forehead_right, forehead_bot))

    # ── Left cheek (points 1–4, lower region) ─────────────────────────────────
    # Use the mid-face area left of the nose
    lc_pts = landmarks[1:5]  # jaw-left segment
    nose_left_x = int(landmarks[31, 0])   # left side of nose
    lc_x1 = int(lc_pts[:, 0].min())
    lc_x2 = nose_left_x
    lc_y1 = int(lc_pts[:, 1].min())
    lc_y2 = int(landmarks[33, 1])         # tip of nose Y
    left_cheek = _blur(_safe_crop(image_bgr, lc_x1, lc_y1, lc_x2, lc_y2))

    # ── Right cheek (points 12–15, mirror) ────────────────────────────────────
    rc_pts = landmarks[12:16]
    nose_right_x = int(landmarks[35, 0])   # right side of nose
    rc_x1 = nose_right_x
    rc_x2 = int(rc_pts[:, 0].max())
    rc_y1 = int(rc_pts[:, 1].min())
    rc_y2 = int(landmarks[33, 1])
    right_cheek = _blur(_safe_crop(image_bgr, rc_x1, rc_y1, rc_x2, rc_y2))

    # ── Under-eye left (points 37–41 — left eye lower boundary) ──────────────
    le_pts = landmarks[37:42]
    ue_l_y1 = int(le_pts[:, 1].max())
    ue_l_y2 = ue_l_y1 + int(h * 0.10)
    ue_l_x1 = int(le_pts[:, 0].min())
    ue_l_x2 = int(le_pts[:, 0].max())
    under_eye_left = _blur(_safe_crop(image_bgr, ue_l_x1, ue_l_y1, ue_l_x2, ue_l_y2))

    # ── Under-eye right (points 43–47 — right eye lower boundary) ────────────
    re_pts = landmarks[43:48]
    ue_r_y1 = int(re_pts[:, 1].max())
    ue_r_y2 = ue_r_y1 + int(h * 0.10)
    ue_r_x1 = int(re_pts[:, 0].min())
    ue_r_x2 = int(re_pts[:, 0].max())
    under_eye_right = _blur(_safe_crop(image_bgr, ue_r_x1, ue_r_y1, ue_r_x2, ue_r_y2))

    # ── Nose (bridge to tip, points 27–35) ────────────────────────────────────
    nose_pts = landmarks[27:36]
    n_x1 = int(nose_pts[:, 0].min()) - 5
    n_x2 = int(nose_pts[:, 0].max()) + 5
    n_y1 = int(nose_pts[:, 1].min())
    n_y2 = int(nose_pts[:, 1].max())
    nose = _blur(_safe_crop(image_bgr, n_x1, n_y1, n_x2, n_y2))

    return {
        "forehead":       forehead,
        "left_cheek":     left_cheek,
        "right_cheek":    right_cheek,
        "under_eye_left": under_eye_left,
        "under_eye_right": under_eye_right,
        "nose":           nose,
        "full_face":      full_face,
    }

"""
image_utils.py — Image decoding, resizing, and normalisation helpers.
"""

import base64
import cv2
import numpy as np
from config import IMAGE_MAX_DIM
from exceptions import InvalidImageError


def decode_base64_image(b64_string: str) -> np.ndarray:
    """
    Decode a base64 image string (with or without data:image/* prefix)
    into a BGR numpy array.

    Raises InvalidImageError on failure.
    """
    # Strip data URL header if present (e.g. "data:image/jpeg;base64,...")
    if "," in b64_string:
        b64_string = b64_string.split(",", 1)[1]

    try:
        raw_bytes = base64.b64decode(b64_string)
    except Exception as exc:
        raise InvalidImageError(f"Failed to decode base64 payload: {exc}") from exc

    nparr = np.frombuffer(raw_bytes, dtype=np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise InvalidImageError("cv2.imdecode returned None — the image data is corrupt or unsupported.")

    return image


def resize_for_processing(image: np.ndarray, max_dim: int = IMAGE_MAX_DIM) -> np.ndarray:
    """
    Resize *image* so that neither dimension exceeds *max_dim*, preserving
    aspect ratio. Returns the original array if already small enough.
    """
    h, w = image.shape[:2]
    scale = min(max_dim / max(h, w, 1), 1.0)
    if scale >= 1.0:
        return image
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def generate_annotated_image_base64(image: np.ndarray, bbox: tuple, landmarks: np.ndarray) -> str:
    """
    Draw colored, semi-transparent ROIs on the face and return as a Base64 JPEG data URL.
    """
    overlay = image.copy()
    h, w = image.shape[:2]
    x, y, bw, bh = bbox

    # Setup colors (BGR)
    COLOR_FOREHEAD = (235, 206, 135)   # Light Blue
    COLOR_CHEEK = (112, 142, 240)      # Light Coral/Salmon
    COLOR_UNDEREYE = (180, 130, 210)   # Light Purple
    COLOR_NOSE = (160, 230, 240)       # Light Yellow
    COLOR_FACE = (46, 58, 28)          # Forest Green

    # Full face bounding box (dashed look simplified to solid thin line)
    cv2.rectangle(image, (x, y), (x + bw, y + bh), COLOR_FACE, 2)

    # 1. Forehead
    brow_y = int(np.mean(landmarks[17:27, 1]))
    f_top, f_bot = max(0, y), brow_y
    f_left, f_right = int(landmarks[17, 0]), int(landmarks[26, 0])
    cv2.rectangle(overlay, (f_left, f_top), (f_right, f_bot), COLOR_FOREHEAD, -1)

    # 2. Left Cheek (viewer's right) - points 1-4, 31, 33
    lc_pts = landmarks[1:5]
    lc_x1, lc_y1 = int(lc_pts[:, 0].min()), int(lc_pts[:, 1].min())
    lc_x2, lc_y2 = int(landmarks[31, 0]), int(landmarks[33, 1])
    cv2.rectangle(overlay, (lc_x1, lc_y1), (lc_x2, lc_y2), COLOR_CHEEK, -1)

    # 3. Right Cheek (viewer's left) - points 12-15, 35, 33
    rc_pts = landmarks[12:16]
    rc_x1, rc_y1 = int(landmarks[35, 0]), int(rc_pts[:, 1].min())
    rc_x2, rc_y2 = int(rc_pts[:, 0].max()), int(landmarks[33, 1])
    cv2.rectangle(overlay, (rc_x1, rc_y1), (rc_x2, rc_y2), COLOR_CHEEK, -1)

    # 4. Under-Eye Left
    le_pts = landmarks[37:42]
    ue_l_x1, ue_l_y1 = int(le_pts[:, 0].min()), int(le_pts[:, 1].max())
    ue_l_x2, ue_l_y2 = int(le_pts[:, 0].max()), ue_l_y1 + int(bh * 0.10)
    cv2.rectangle(overlay, (ue_l_x1, ue_l_y1), (ue_l_x2, ue_l_y2), COLOR_UNDEREYE, -1)

    # 5. Under-Eye Right
    re_pts = landmarks[43:48]
    ue_r_x1, ue_r_y1 = int(re_pts[:, 0].min()), int(re_pts[:, 1].max())
    ue_r_x2, ue_r_y2 = int(re_pts[:, 0].max()), ue_r_y1 + int(bh * 0.10)
    cv2.rectangle(overlay, (ue_r_x1, ue_r_y1), (ue_r_x2, ue_r_y2), COLOR_UNDEREYE, -1)

    # 6. Nose
    n_pts = landmarks[27:36]
    n_x1, n_y1 = int(n_pts[:, 0].min()) - 5, int(n_pts[:, 1].min())
    n_x2, n_y2 = int(n_pts[:, 0].max()) + 5, int(n_pts[:, 1].max())
    cv2.rectangle(overlay, (n_x1, n_y1), (n_x2, n_y2), COLOR_NOSE, -1)

    # Blend the overlay with the original image
    alpha = 0.35
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    # Draw landmarks (small white dots)
    for (lx, ly) in landmarks:
        cv2.circle(image, (lx, ly), 1, (255, 255, 255), -1)

    # Encode to base64 JPEG
    _, buffer = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    b64_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{b64_str}"

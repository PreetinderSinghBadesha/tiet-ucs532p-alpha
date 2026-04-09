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

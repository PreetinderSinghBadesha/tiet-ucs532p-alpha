"""
face_detector.py — Face detection using HaarCascade + dlib 68-point landmarks.

Public API:
    detect_face(image_bgr) → (bbox_tuple, landmarks_array) | raises FaceNotDetectedError
"""

import os
import cv2
import dlib
import numpy as np

from config import (
    FACE_DETECTION_SCALE,
    FACE_DETECTION_NEIGHBORS,
    MIN_FACE_SIZE,
)
from exceptions import FaceNotDetectedError

# ── Module-level singletons (loaded once per process) ─────────────────────────
_haar_detector = None
_dlib_detector = dlib.get_frontal_face_detector()
_dlib_predictor = None


def _get_haar():
    global _haar_detector
    if _haar_detector is None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _haar_detector = cv2.CascadeClassifier(cascade_path)
    return _haar_detector


def _get_predictor():
    global _dlib_predictor
    if _dlib_predictor is None:
        # Shape predictor lives in backend/models/
        model_path = os.path.join(
            os.path.dirname(__file__), "..", "models",
            "shape_predictor_68_face_landmarks.dat",
        )
        model_path = os.path.abspath(model_path)
        if os.path.exists(model_path):
            _dlib_predictor = dlib.shape_predictor(model_path)
        else:
            raise FileNotFoundError(
                f"dlib landmark model not found at {model_path}. "
                "Run backend/download_model.py to fetch it."
            )
    return _dlib_predictor


def detect_face(image_bgr: np.ndarray):
    """
    Detect the largest face in *image_bgr* and return its bounding box +
    the 68 dlib landmarks.

    Returns
    -------
    bbox : tuple  (x, y, w, h)
    landmarks : np.ndarray  shape (68, 2)  dtype int

    Raises
    ------
    FaceNotDetectedError  when no face is found.
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Try dlib — more accurate
    dlib_faces = _dlib_detector(gray, 1)

    if len(dlib_faces) == 0:
        # 2. Fallback: HaarCascade
        haar = _get_haar()
        haar_faces = haar.detectMultiScale(
            gray,
            scaleFactor=FACE_DETECTION_SCALE,
            minNeighbors=FACE_DETECTION_NEIGHBORS,
            minSize=MIN_FACE_SIZE,
        )
        if len(haar_faces) == 0:
            raise FaceNotDetectedError(
                "No face detected. Please ensure your face is clearly visible "
                "and well-lit."
            )
        # Pick the largest Haar face, convert to dlib rect
        x, y, w, h = max(haar_faces, key=lambda r: r[2] * r[3])
        dlib_rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
    else:
        # Pick the largest dlib face
        dlib_rect = max(dlib_faces, key=lambda r: r.width() * r.height())

    bbox = (
        dlib_rect.left(),
        dlib_rect.top(),
        dlib_rect.width(),
        dlib_rect.height(),
    )

    # 3. 68-point landmark extraction
    predictor = _get_predictor()
    shape = predictor(gray, dlib_rect)
    landmarks = np.array(
        [[shape.part(i).x, shape.part(i).y] for i in range(68)],
        dtype=np.int32,
    )

    return bbox, landmarks

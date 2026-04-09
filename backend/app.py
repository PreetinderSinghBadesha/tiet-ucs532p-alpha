"""
app.py — DERMA.ai Flask entry point.

Routes:
  GET  /api/health   — liveness check
  POST /api/analyze  — full CV pipeline + recommendations
"""

import time
import sys
import os

# ── Ensure backend directory is on sys.path ───────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.image_utils import decode_base64_image, resize_for_processing, generate_annotated_image_base64
from utils.response_builder import build_success_response, build_error_response
from cv_pipeline.face_detector import detect_face
from cv_pipeline.region_extractor import extract_regions
from cv_pipeline.feature_extractor import extract_features
from recommendation_engine.scorer import compute_scores
from recommendation_engine.recommender import build_recommendations
from exceptions import FaceNotDetectedError, InvalidImageError

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "DERMA.ai CV Pipeline"}), 200


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Expects JSON body:
    {
      "image": "<base64 string>",
      "lifestyle": {
        "sleep_hours":      7,
        "water_glasses":    8,
        "stress_level":     5,
        "diet_quality":     "good",
        "current_skincare": "basic",
        "skin_type":        "normal"
      }
    }
    """
    t_start = time.perf_counter()

    body = request.get_json(silent=True)
    if not body or "image" not in body:
        return jsonify(build_error_response(
            "missing_image",
            "Request body must include an 'image' field with a base64-encoded image."
        )), 400

    lifestyle = body.get("lifestyle", {})

    # ── 1. Decode image ───────────────────────────────────────────────────────
    try:
        image = decode_base64_image(body["image"])
    except InvalidImageError as exc:
        return jsonify(build_error_response("invalid_image", str(exc))), 400

    # ── 2. Resize for performance ─────────────────────────────────────────────
    image = resize_for_processing(image)

    # ── 3. Face detection + landmarks ─────────────────────────────────────────
    try:
        bbox, landmarks = detect_face(image)
    except FaceNotDetectedError as exc:
        resp = build_error_response("no_face_detected", str(exc))
        resp["face_detected"] = False
        return jsonify(resp), 422
    except FileNotFoundError as exc:
        return jsonify(build_error_response("model_missing", str(exc))), 500

    # ── 4. Region extraction ──────────────────────────────────────────────────
    regions = extract_regions(image, bbox, landmarks)

    # ── 5. Feature extraction (all 5 analyzers) ───────────────────────────────
    try:
        features = extract_features(image, regions)
    except Exception as exc:
        app.logger.exception("Feature extraction failed")
        return jsonify(build_error_response("analysis_error", f"CV pipeline error: {exc}")), 500

    # ── 6. Score computation + lifestyle adjustment ───────────────────────────
    scores = compute_scores(features, lifestyle)

    # ── 7. Recommendation generation ─────────────────────────────────────────
    recommendations, see_dermatologist = build_recommendations(features, scores, lifestyle)

    # ── 8. Generate annotated image ───────────────────────────────────────────
    annotated_image_b64 = generate_annotated_image_base64(image, bbox, landmarks)

    processing_ms = (time.perf_counter() - t_start) * 1000

    return jsonify(build_success_response(
        scores=scores,
        features=features,
        recommendations=recommendations,
        see_dermatologist=see_dermatologist,
        processing_ms=processing_ms,
        annotated_image=annotated_image_b64,
    )), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
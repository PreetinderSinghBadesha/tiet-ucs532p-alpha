"""
response_builder.py — Construct the final JSON report sent to the client.
"""


def build_success_response(
    scores: dict,
    features: dict,
    recommendations: list,
    see_dermatologist: bool,
    processing_ms: float,
    annotated_image: str = None,
) -> dict:
    """Assemble the full success response payload."""
    return {
        "success": True,
        "face_detected": True,
        "annotated_image": annotated_image,
        "overall_score": scores["overall_score"],
        "condition_scores": {
            "acne":         scores["acne_score"],
            "texture":      scores["texture_score"],
            "dark_circles": scores["dark_circle_score"],
            "wrinkles":     scores["wrinkle_score"],
            "tone":         scores["tone_score"],
        },
        "condition_details": {
            "acne": {
                "count":           features["acne"]["count"],
                "density":         features["acne"]["density"],
                "redness_score":   features["acne"]["redness_score"],
                "affected_regions": features["acne"]["affected_regions"],
            },
            "texture": {
                "roughness_score": features["texture"]["roughness_score"],
                "pore_visibility": features["texture"]["pore_visibility"],
                "uniformity":      features["texture"]["uniformity"],
            },
            "dark_circles": {
                "darkness_ratio":     features["dark_circles"]["darkness_ratio"],
                "pigmentation_score": features["dark_circles"]["pigmentation_score"],
            },
            "wrinkles": {
                "edge_density": features["wrinkles"]["edge_density"],
                "line_count":   features["wrinkles"]["line_count"],
            },
            "tone": {
                "tone_uniformity":          features["tone"]["tone_uniformity"],
                "redness_index":            features["tone"]["redness_index"],
                "hyperpigmentation_spots":  features["tone"]["hyperpigmentation_spots"],
                "overall_tone":             features["tone"]["overall_tone"],
            },
        },
        "lifestyle_impact":   scores.get("lifestyle_impact", {}),
        "recommendations":    recommendations,
        "see_dermatologist":  see_dermatologist,
        "processing_time_ms": round(processing_ms, 1),
        "disclaimer": (
            "Analysis conducted using classical computer vision. "
            "This is not a medical diagnosis. Consult a qualified dermatologist "
            "for professional skin care advice."
        ),
    }


def build_error_response(error_code: str, message: str) -> dict:
    """Assemble an error payload."""
    return {
        "success":    False,
        "face_detected": False,
        "error":      error_code,
        "message":    message,
    }

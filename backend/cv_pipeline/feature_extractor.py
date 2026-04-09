"""
feature_extractor.py — Master orchestrator that calls all CV sub-analyzers.

Public API:
    extract_features(image_bgr, regions) → dict
"""

from cv_pipeline import (
    acne_detector,
    texture_analyzer,
    dark_circle_detector,
    wrinkle_detector,
    tone_analyzer,
)


def extract_features(image_bgr, regions: dict) -> dict:
    """
    Run all five skin analysis pipelines and return a unified feature dict.

    Parameters
    ----------
    image_bgr : np.ndarray  – full BGR image (unused directly but passed for
                              future extensibility, e.g. whole-image stats)
    regions   : dict        – ROI dict from region_extractor.extract_regions()

    Returns
    -------
    {
      "acne":         {...},
      "texture":      {...},
      "dark_circles": {...},
      "wrinkles":     {...},
      "tone":         {...}
    }
    """
    return {
        "acne":         acne_detector.analyze(regions),
        "texture":      texture_analyzer.analyze(regions),
        "dark_circles": dark_circle_detector.analyze(regions),
        "wrinkles":     wrinkle_detector.analyze(regions),
        "tone":         tone_analyzer.analyze(regions),
    }

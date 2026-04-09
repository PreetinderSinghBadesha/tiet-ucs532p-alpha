"""
scorer.py — Normalise raw CV scores and integrate lifestyle factors.

Weights (must sum to 1.0):
  Acne 35% · Texture 25% · Dark circles 15% · Wrinkles 15% · Tone 10%

Public API:
    compute_scores(features, lifestyle) → dict
"""

import numpy as np
from config import (
    SCORE_WEIGHTS,
    LIFESTYLE_SLEEP_THRESHOLD,
    LIFESTYLE_SLEEP_DARK_CIRCLE_BOOST,
    LIFESTYLE_SLEEP_OVERALL_BOOST,
    LIFESTYLE_STRESS_THRESHOLD,
    LIFESTYLE_STRESS_ACNE_BOOST,
    LIFESTYLE_WATER_THRESHOLD,
    LIFESTYLE_WATER_TEXTURE_BOOST,
    LIFESTYLE_POOR_DIET_ALL_BOOST,
)


def _clamp(v: float, lo=0.0, hi=100.0) -> float:
    return float(np.clip(v, lo, hi))


def compute_scores(features: dict, lifestyle: dict) -> dict:
    """
    Apply lifestyle modifiers to raw CV scores, then compute weighted overall.

    Parameters
    ----------
    features  : output of feature_extractor.extract_features()
    lifestyle : {
        sleep_hours: float,
        water_glasses: float,
        stress_level: float,   # 1–10
        diet_quality: str,     # "poor"|"average"|"good"|"excellent"
        current_skincare: str,
        skin_type: str,
    }

    Returns
    -------
    {
      "acne_score":          float,  # 0–100
      "texture_score":       float,
      "dark_circle_score":   float,
      "wrinkle_score":       float,
      "tone_score":          float,
      "overall_score":       float,  # weighted, lower = healthier
      "lifestyle_impact":    dict
    }
    """
    sleep   = float(lifestyle.get("sleep_hours", 7))
    water   = float(lifestyle.get("water_glasses", 8))
    stress  = float(lifestyle.get("stress_level", 5))
    diet    = str(lifestyle.get("diet_quality", "average")).lower()

    # ── Base raw scores from CV pipeline ────────────────────────────────────
    acne_raw   = features["acne"].get("raw_score", 0.0)
    tex_raw    = features["texture"].get("raw_score", 0.0)
    dc_raw     = features["dark_circles"].get("raw_score", 0.0)
    wk_raw     = features["wrinkles"].get("raw_score", 0.0)
    tone_raw   = features["tone"].get("raw_score", 0.0)

    # ── Lifestyle adjustments ────────────────────────────────────────────────
    lifestyle_impact = {}

    if sleep < LIFESTYLE_SLEEP_THRESHOLD:
        dc_raw += LIFESTYLE_SLEEP_DARK_CIRCLE_BOOST
        acne_raw += LIFESTYLE_SLEEP_OVERALL_BOOST * 0.5
        lifestyle_impact["poor_sleep"] = (
            f"Less than {LIFESTYLE_SLEEP_THRESHOLD}h sleep increases dark circles "
            f"(+{LIFESTYLE_SLEEP_DARK_CIRCLE_BOOST} pts) and skin stress."
        )

    if stress > LIFESTYLE_STRESS_THRESHOLD:
        acne_raw += LIFESTYLE_STRESS_ACNE_BOOST
        lifestyle_impact["high_stress"] = (
            f"Stress level {stress}/10 elevates cortisol, worsening acne "
            f"(+{LIFESTYLE_STRESS_ACNE_BOOST} pts)."
        )

    if water < LIFESTYLE_WATER_THRESHOLD:
        tex_raw += LIFESTYLE_WATER_TEXTURE_BOOST
        lifestyle_impact["low_hydration"] = (
            f"Only {int(water)} glasses/day — dehydration increases skin roughness "
            f"(+{LIFESTYLE_WATER_TEXTURE_BOOST} pts)."
        )

    if diet in ("poor",):
        boost = LIFESTYLE_POOR_DIET_ALL_BOOST
        acne_raw  += boost
        tex_raw   += boost
        dc_raw    += boost
        wk_raw    += boost
        tone_raw  += boost
        lifestyle_impact["poor_diet"] = (
            f"Poor diet quality adds {boost} pts across all skin health dimensions."
        )

    # Clamp all to 0–100
    acne_score  = _clamp(acne_raw)
    tex_score   = _clamp(tex_raw)
    dc_score    = _clamp(dc_raw)
    wk_score    = _clamp(wk_raw)
    tone_score  = _clamp(tone_raw)

    # ── Weighted overall (higher = worse skin health) ────────────────────────
    overall = (
        acne_score  * SCORE_WEIGHTS["acne"]         +
        tex_score   * SCORE_WEIGHTS["texture"]      +
        dc_score    * SCORE_WEIGHTS["dark_circles"] +
        wk_score    * SCORE_WEIGHTS["wrinkles"]     +
        tone_score  * SCORE_WEIGHTS["tone"]
    )

    # Convert to "skin health" score (100 = perfect skin)
    skin_health = _clamp(100.0 - overall)

    return {
        "acne_score":        round(acne_score, 1),
        "texture_score":     round(tex_score, 1),
        "dark_circle_score": round(dc_score, 1),
        "wrinkle_score":     round(wk_score, 1),
        "tone_score":        round(tone_score, 1),
        "overall_score":     round(skin_health, 1),
        "lifestyle_impact":  lifestyle_impact,
    }

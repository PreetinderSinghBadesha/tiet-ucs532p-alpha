"""
config.py — All tunable constants for DERMA.ai CV pipeline.
Never hardcode magic numbers anywhere else in the codebase.
"""

# ── Face Detection ──────────────────────────────────────────────────────────────
FACE_DETECTION_SCALE = 1.1
FACE_DETECTION_NEIGHBORS = 5
MIN_FACE_SIZE = (100, 100)

# ── Region Ratios (relative to face bounding box) ──────────────────────────────
FOREHEAD_HEIGHT_RATIO = 0.25
CHEEK_WIDTH_RATIO = 0.35
UNDER_EYE_HEIGHT_RATIO = 0.10
ROI_BLUR_KERNEL = (3, 3)  # Applied to each ROI before analysis

# ── Acne Detection ─────────────────────────────────────────────────────────────
ACNE_BLUR_KERNEL = (5, 5)
ACNE_CANNY_LOW = 50
ACNE_CANNY_HIGH = 150
ACNE_MIN_CONTOUR_AREA = 20
ACNE_MAX_CONTOUR_AREA = 500
ACNE_CIRCULARITY_THRESHOLD = 0.4
ACNE_LAB_A_THRESHOLD = 135  # A-channel values above this indicate redness

# ── Texture Analysis ───────────────────────────────────────────────────────────
LBP_RADIUS = 1
LBP_NEIGHBORS = 8
TEXTURE_LAPLACIAN_KERNEL = 3

# ── Wrinkle Detection ──────────────────────────────────────────────────────────
WRINKLE_BLUR_KERNEL = (3, 3)
WRINKLE_CANNY_LOW = 30
WRINKLE_CANNY_HIGH = 80
WRINKLE_MORPH_KERNEL = (3, 3)
WRINKLE_HOUGH_MIN_LINE = 20   # pixels — minimum line length
WRINKLE_HOUGH_MAX_GAP = 5     # pixels — maximum gap between segments

# ── Skin Tone (HSV mask thresholds) ───────────────────────────────────────────
SKIN_HSV_LOWER = (0, 20, 70)
SKIN_HSV_UPPER = (20, 255, 255)
HYPERPIGMENTATION_V_THRESHOLD = 80  # V-channel below this = dark spot
HYPERPIGMENTATION_MIN_AREA = 30

# ── Dark Circle Detection ──────────────────────────────────────────────────────
DARK_CIRCLE_SEVERITY_MILD = 0.07
DARK_CIRCLE_SEVERITY_MODERATE = 0.14
DARK_CIRCLE_SEVERITY_SEVERE = 0.22

# ── Severity Thresholds (0–100 scale) ─────────────────────────────────────────
SEVERITY = {
    "none":     0,
    "mild":     30,
    "moderate": 60,
    "severe":   80,
}

# ── Scorer Weights ─────────────────────────────────────────────────────────────
SCORE_WEIGHTS = {
    "acne":         0.35,
    "texture":      0.25,
    "dark_circles": 0.15,
    "wrinkles":     0.15,
    "tone":         0.10,
}

# ── Lifestyle Adjustments (added to raw condition scores, 0-100) ───────────────
LIFESTYLE_SLEEP_THRESHOLD = 6          # hours — below this is poor
LIFESTYLE_SLEEP_DARK_CIRCLE_BOOST = 15
LIFESTYLE_SLEEP_OVERALL_BOOST = 10
LIFESTYLE_STRESS_THRESHOLD = 7         # /10 — above this is high
LIFESTYLE_STRESS_ACNE_BOOST = 10
LIFESTYLE_WATER_THRESHOLD = 6          # glasses — below this is poor
LIFESTYLE_WATER_TEXTURE_BOOST = 10
LIFESTYLE_POOR_DIET_ALL_BOOST = 5

# ── Image Processing ───────────────────────────────────────────────────────────
IMAGE_MAX_DIM = 1024  # Resize to this max dimension before processing

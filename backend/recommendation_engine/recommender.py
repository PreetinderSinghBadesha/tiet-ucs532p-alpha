"""
recommender.py — Rule-based mapping from condition + severity → skin care routine.

Public API:
    build_recommendations(features, scores, lifestyle) → list[dict]
"""

from config import SEVERITY


# ── Rule tables ───────────────────────────────────────────────────────────────

_ACNE_RULES = {
    "none": {
        "causes": ["Balanced oil production"],
        "routine_steps": [
            {"step": "Cleanser", "instruction": "Cleanse twice daily with a gentle foaming formula.", "product_type": "Gentle foaming cleanser (pH-balanced)"},
            {"step": "Moisturiser", "instruction": "Apply a lightweight hydrating moisturiser.", "product_type": "Oil-free gel moisturiser"},
        ],
        "lifestyle_changes": ["Maintain your current cleansing habits."],
        "ingredients_to_use": ["Hyaluronic acid", "Aloe vera"],
        "ingredients_to_avoid": ["Heavy oils", "Comedogenic emollients"],
    },
    "mild": {
        "causes": ["Excess sebum", "Mild inflammation", "Clogged pores"],
        "routine_steps": [
            {"step": "Cleanser", "instruction": "Cleanse morning and night to remove excess oil.", "product_type": "Salicylic acid 0.5–1% cleanser"},
            {"step": "Toner", "instruction": "Apply a pore-minimising toner after cleansing.", "product_type": "Niacinamide 5% toner"},
            {"step": "Treatment", "instruction": "Spot-treat active blemishes at night.", "product_type": "Benzoyl peroxide 2.5% gel"},
            {"step": "Moisturiser", "instruction": "Layer a lightweight moisturiser over treatment.", "product_type": "Oil-free gel moisturiser"},
            {"step": "SPF", "instruction": "Apply SPF 30+ every morning.", "product_type": "Non-comedogenic SPF 30"},
        ],
        "lifestyle_changes": ["Avoid touching your face", "Change pillowcase weekly", "Limit dairy intake"],
        "ingredients_to_use": ["Salicylic acid", "Niacinamide", "Benzoyl peroxide (spot)", "Zinc"],
        "ingredients_to_avoid": ["Coconut oil", "Lanolin", "Heavy silicones"],
    },
    "moderate": {
        "causes": ["Hormonal fluctuations", "Bacterial overgrowth (C. acnes)", "Chronic inflammation", "Pore congestion"],
        "routine_steps": [
            {"step": "Cleanser", "instruction": "Cleanse twice daily with an exfoliating acid wash.", "product_type": "Salicylic acid 2% cleanser"},
            {"step": "Toner", "instruction": "Balance skin pH and reduce oiliness.", "product_type": "AHA/BHA toner (glycolic + salicylic)"},
            {"step": "Treatment", "instruction": "Apply retinoid at night 3×/week — build up slowly.", "product_type": "Adapalene 0.1% gel"},
            {"step": "Spot treatment", "instruction": "Dab on inflamed lesions.", "product_type": "Benzoyl peroxide 5% spot cream"},
            {"step": "Moisturiser", "instruction": "Hydrate to counter retinoid dryness.", "product_type": "Ceramide-rich moisturiser"},
            {"step": "SPF", "instruction": "SPF 50 daily (retinoids increase photosensitivity).", "product_type": "SPF 50 sunscreen"},
        ],
        "lifestyle_changes": ["Reduce refined sugar/glycaemic load", "Manage stress via exercise or meditation", "Stay hydrated (8+ glasses/day)"],
        "ingredients_to_use": ["Adapalene", "Salicylic acid", "Niacinamide", "Azelaic acid"],
        "ingredients_to_avoid": ["Fragrant plant oils", "Alcohol denat", "Harsh scrubs"],
    },
    "severe": {
        "causes": ["Cystic acne — deep nodular lesions", "Severe bacterial infection", "Possible hormonal imbalance"],
        "routine_steps": [
            {"step": "Gentle Cleanser", "instruction": "Use a very gentle non-stripping cleanser — avoid irritants.", "product_type": "Micellar water or mild cream cleanser"},
            {"step": "Prescription treatment", "instruction": "Prescription retinoid or antibiotic — consult dermatologist.", "product_type": "Tretinoin 0.025% or clindamycin (Rx)"},
            {"step": "Moisturiser", "instruction": "Heavy barrier cream to repair compromised skin.", "product_type": "Ceramide + panthenol barrier cream"},
            {"step": "SPF", "instruction": "Mineral SPF daily.", "product_type": "Zinc oxide SPF 30+"},
        ],
        "lifestyle_changes": ["Seek professional medical evaluation", "Avoid all manual extraction", "Document flare-up triggers"],
        "ingredients_to_use": ["Ceramides", "Panthenol", "Zinc oxide"],
        "ingredients_to_avoid": ["All actives until inflammation subsides"],
    },
}

_TEXTURE_RULES = {
    "none": {
        "causes": ["Smooth calibrated skin turnover"],
        "routine_steps": [
            {"step": "Chemical exfoliant", "instruction": "Use 1–2×/week to maintain texture.", "product_type": "AHA lactic acid 5% toner"},
        ],
        "lifestyle_changes": ["Maintain hydration"],
        "ingredients_to_use": ["Lactic acid", "Hyaluronic acid"],
        "ingredients_to_avoid": [],
    },
    "mild": {
        "causes": ["Slow cell turnover", "Dehydration", "Environmental exposure"],
        "routine_steps": [
            {"step": "Exfoliating Cleanser", "instruction": "Exfoliate 2–3×/week.", "product_type": "Glycolic acid 2% cleanser"},
            {"step": "Serum", "instruction": "Daily serum to attract and retain moisture.", "product_type": "Hyaluronic acid serum (3 molecular weights)"},
            {"step": "Moisturiser", "instruction": "Lock in serum with a rich cream.", "product_type": "Ceramide barrier moisturiser"},
        ],
        "lifestyle_changes": ["Drink 8–10 glasses water daily", "Use a humidifier at night"],
        "ingredients_to_use": ["Glycolic acid", "Lactic acid", "Hyaluronic acid"],
        "ingredients_to_avoid": ["Physical scrubs (micro-tears)", "Fragrance"],
    },
    "moderate": {
        "causes": ["Keratin build-up", "Dehydration", "Sun damage (rough texture)"],
        "routine_steps": [
            {"step": "BHA exfoliant", "instruction": "Apply 2% BHA solution 3 evenings/week.", "product_type": "Paula's Choice 2% BHA Liquid Exfoliant"},
            {"step": "Retinol serum", "instruction": "Low-strength retinol nightly for cell turnover.", "product_type": "Retinol 0.025% serum"},
            {"step": "Hyaluronic serum", "instruction": "Apply on damp skin morning and night.", "product_type": "Multi-weight hyaluronic acid serum"},
            {"step": "Occlusive", "instruction": "Apply petrolatum or squalane on top of moisturiser at night.", "product_type": "Squalane oil or petrolatum"},
        ],
        "lifestyle_changes": ["Increase water intake significantly", "Reduce alcohol consumption"],
        "ingredients_to_use": ["BHA", "Retinol", "Squalane", "Polyglutamic acid"],
        "ingredients_to_avoid": ["Drying alcohols", "Harsh cleansers"],
    },
    "severe": {
        "causes": ["Keratosis pilaris-like buildup", "Severe dehydration", "Damaged moisture barrier"],
        "routine_steps": [
            {"step": "Barrier repair cleanser", "instruction": "Use only barrier-safe cleansers, no actives.", "product_type": "Cetaphil or CeraVe Hydrating Cleanser"},
            {"step": "Prescription retinoid", "instruction": "Consult a dermatologist for stronger retinoid.", "product_type": "Tretinoin 0.05% cream (Rx)"},
            {"step": "Intensive moisturiser", "instruction": "Apply immediately after showering, on damp skin.", "product_type": "Urea 10% lotion + ceramide cream"},
        ],
        "lifestyle_changes": ["See a dermatologist", "Avoid long hot showers"],
        "ingredients_to_use": ["Urea", "Ceramides", "Panthenol"],
        "ingredients_to_avoid": ["All exfoliating acids until barrier is repaired"],
    },
}

_DARK_CIRCLE_RULES = {
    "none": {
        "causes": ["Normal periorbital circulation"],
        "routine_steps": [
            {"step": "Eye cream", "instruction": "Light preventive eye cream at night.", "product_type": "Caffeine + peptide eye cream"},
        ],
        "lifestyle_changes": ["Maintain consistent sleep schedule"],
        "ingredients_to_use": ["Caffeine", "Vitamin K"],
        "ingredients_to_avoid": [],
    },
    "mild": {
        "causes": ["Mild fatigue", "Periorbital vascular congestion", "Thin under-eye skin"],
        "routine_steps": [
            {"step": "Eye serum", "instruction": "Apply morning and night with ring finger tapping.", "product_type": "Vitamin C + caffeine eye serum"},
            {"step": "Eye cream", "instruction": "Layer cream on top of serum.", "product_type": "Retinol 0.1% eye cream"},
        ],
        "lifestyle_changes": ["Sleep 7–9 hours", "Elevate head while sleeping", "Reduce salt intake"],
        "ingredients_to_use": ["Caffeine", "Vitamin C", "Retinol (eye-safe)", "Vitamin K"],
        "ingredients_to_avoid": ["Fragrance near eyes"],
    },
    "moderate": {
        "causes": ["Chronic fatigue", "Vascular pooling", "Hyperpigmentation under-eye", "Dehydration"],
        "routine_steps": [
            {"step": "Brightening eye serum", "instruction": "Apply vitamin C serum under eyes each morning.", "product_type": "L-Ascorbic acid 10% eye serum"},
            {"step": "Retinol eye cream", "instruction": "Use 0.25% retinol eye cream nightly.", "product_type": "Retinol 0.25% eye cream"},
            {"step": "Cold compress", "instruction": "Apply cold compresses for 5 min each morning to reduce puffiness.", "product_type": "Chilled rose water pads"},
        ],
        "lifestyle_changes": ["Target 8h sleep", "Reduce screen time before bed", "Increase iron-rich foods"],
        "ingredients_to_use": ["Vitamin C (ascorbic acid)", "Niacinamide", "Peptides", "Retinol"],
        "ingredients_to_avoid": [],
    },
    "severe": {
        "causes": ["Structural melanin deposition", "Chronic sleep debt", "Genetics", "Anaemia"],
        "routine_steps": [
            {"step": "High-potency brightener", "instruction": "Use kojic acid or tranexamic acid serum under eyes.", "product_type": "Tranexamic acid 3% eye serum"},
            {"step": "Retinoid", "instruction": "Dermatologist-prescribed tretinoin for under-eye pigment.", "product_type": "Tretinoin 0.025% eye area (Rx)"},
        ],
        "lifestyle_changes": ["Medical review recommended", "Investigate anaemia", "Strict sleep hygiene"],
        "ingredients_to_use": ["Tranexamic acid", "Kojic acid", "Tretinoin (Rx)"],
        "ingredients_to_avoid": [],
    },
}

_WRINKLE_RULES = {
    "none": {
        "causes": ["Youthful elastin and collagen levels"],
        "routine_steps": [
            {"step": "Antioxidant serum", "instruction": "Morning vitamin C serum for photoprotection.", "product_type": "Vitamin C 10–15% serum"},
            {"step": "SPF", "instruction": "Daily SPF to prevent photoageing.", "product_type": "SPF 50 PA++++"},
        ],
        "lifestyle_changes": ["Maintain regular SPF use"],
        "ingredients_to_use": ["Vitamin C", "Niacinamide"],
        "ingredients_to_avoid": [],
    },
    "mild": {
        "causes": ["Early expression lines", "Mild sun damage", "Beginning collagen reduction"],
        "routine_steps": [
            {"step": "Vitamin C serum", "instruction": "Apply each morning for collagen synthesis.", "product_type": "Vitamin C 15% + ferulic acid serum"},
            {"step": "Retinol", "instruction": "Start retinol 0.1% two nights per week, increase slowly.", "product_type": "Encapsulated retinol 0.1% serum"},
            {"step": "SPF", "instruction": "SPF 50+ every single morning, reapply at noon.", "product_type": "SPF 50 tinted mineral sunscreen"},
        ],
        "lifestyle_changes": ["Wear sunglasses to reduce squinting", "Sleep on back to reduce compression wrinkles"],
        "ingredients_to_use": ["Retinol", "Vitamin C", "Niacinamide", "Peptides"],
        "ingredients_to_avoid": [],
    },
    "moderate": {
        "causes": ["Cumulative UV damage", "Reduced collagen/elastin production", "Repetitive facial movements"],
        "routine_steps": [
            {"step": "Peptide serum", "instruction": "Apply morning and evening to support collagen.", "product_type": "Matrixyl 3000 + Argireline peptide serum"},
            {"step": "Retinol (upgraded)", "instruction": "Progress to retinol 0.3% nightly.", "product_type": "Retinol 0.3% in squalane"},
            {"step": "Rich moisturiser", "instruction": "Apply after retinol to plump and reduce appearance.", "product_type": "Hyaluronic acid + glycerin rich cream"},
            {"step": "SPF 50", "instruction": "Never skip sunscreen — UV is #1 ageing factor.", "product_type": "Chemical/mineral hybrid SPF 50"},
        ],
        "lifestyle_changes": ["Avoid smoking", "Eat antioxidant-rich diet (berries, leafy greens)", "Stay hydrated"],
        "ingredients_to_use": ["Retinol 0.3%", "Peptides", "Bakuchiol", "Vitamin C", "Collagen-boosting ceramides"],
        "ingredients_to_avoid": ["Tanning beds", "Harsh physical scrubs"],
    },
    "severe": {
        "causes": ["Deep dermal remodelling", "Chronic photoageing", "Significant collagen depletion"],
        "routine_steps": [
            {"step": "Prescription retinoid", "instruction": "Tretinoin nightly — dermatologist-supervised.", "product_type": "Tretinoin 0.05–0.1% cream (Rx)"},
            {"step": "Peptide serum", "instruction": "Potent signal peptides to stimulate collagen.", "product_type": "SYN-COLL + Argireline serum"},
            {"step": "Barrier cream", "instruction": "Counter retinoid irritation with ceramide repair.", "product_type": "Ceramide + squalane barrier cream"},
        ],
        "lifestyle_changes": ["Consult a dermatologist for professional treatments (e.g., micro-needling, laser)", "Strict UV avoidance"],
        "ingredients_to_use": ["Tretinoin (Rx)", "Copper peptides", "Vitamin C"],
        "ingredients_to_avoid": ["Over-the-counter gimmick products"],
    },
}

_TONE_RULES = {
    "none": {
        "causes": ["Uniform melanin distribution"],
        "routine_steps": [
            {"step": "SPF", "instruction": "Maintain daily SPF to preserve even tone.", "product_type": "SPF 30+ sunscreen"},
        ],
        "lifestyle_changes": [],
        "ingredients_to_use": ["Vitamin C (preventive)", "SPF"],
        "ingredients_to_avoid": [],
    },
    "mild": {
        "causes": ["Mild sun spots", "Post-inflammatory marks", "Hormonal changes"],
        "routine_steps": [
            {"step": "Brightening serum", "instruction": "Apply after cleansing, morning and evening.", "product_type": "Niacinamide 10% + zinc serum"},
            {"step": "Chemical exfoliant", "instruction": "2×/week to accelerate dark spot fading.", "product_type": "Glycolic acid 7% toner"},
            {"step": "SPF", "instruction": "SPF 50 daily to prevent further pigmentation.", "product_type": "High protection SPF 50"},
        ],
        "lifestyle_changes": ["Wear hats outdoors", "Avoid peak sun hours (10 am–4 pm)"],
        "ingredients_to_use": ["Niacinamide", "Alpha arbutin", "Glycolic acid", "Vitamin C"],
        "ingredients_to_avoid": ["Harsh physical scrubs"],
    },
    "moderate": {
        "causes": ["Melasma", "Sun damage (lentigines)", "PIH from acne", "Uneven melanin regulation"],
        "routine_steps": [
            {"step": "Vitamin C serum", "instruction": "Pure ascorbic acid in the morning for brightening.", "product_type": "Vitamin C 20% serum"},
            {"step": "Kojic acid serum", "instruction": "Evening targeted brightening treatment.", "product_type": "Kojic acid 1% + azelaic acid 10% serum"},
            {"step": "Retinol", "instruction": "Nightly for cell turnover and spot fading.", "product_type": "Retinol 0.2% formula"},
            {"step": "SPF 50", "instruction": "Non-negotiable daily step.", "product_type": "Mineral SPF 50 PA++++"},
        ],
        "lifestyle_changes": ["Strict sun avoidance", "Consider professional treatments (chemical peel, IPL)"],
        "ingredients_to_use": ["Vitamin C", "Kojic acid", "Azelaic acid", "Tranexamic acid", "Alpha arbutin"],
        "ingredients_to_avoid": ["Hydroquinone without medical supervision"],
    },
    "severe": {
        "causes": ["Severe melasma", "Deep PIH", "Perioral hyperpigmentation"],
        "routine_steps": [
            {"step": "Prescription bleaching agent", "instruction": "Dermatologist-prescribed; use as directed.", "product_type": "Hydroquinone 4% cream (Rx)"},
            {"step": "Mineral SPF 70", "instruction": "Imperative — any UV perpetuates hyperpigmentation.", "product_type": "Mineral SPF 70+"},
        ],
        "lifestyle_changes": ["Dermatologist evaluation mandatory", "Consider laser or chemical peel under supervision"],
        "ingredients_to_use": ["Hydroquinone (Rx)", "Tranexamic acid", "Retinoids"],
        "ingredients_to_avoid": ["DIY lemon juice treatments (phototoxic)"],
    },
}

_RULE_MAP = {
    "acne":         _ACNE_RULES,
    "texture":      _TEXTURE_RULES,
    "dark_circles": _DARK_CIRCLE_RULES,
    "wrinkles":     _WRINKLE_RULES,
    "tone":         _TONE_RULES,
}

_CONDITION_LABELS = {
    "acne":         "Acne & Blemishes",
    "texture":      "Skin Texture",
    "dark_circles": "Dark Circles",
    "wrinkles":     "Fine Lines & Wrinkles",
    "tone":         "Skin Tone Evenness",
}


def build_recommendations(features: dict, scores: dict, lifestyle: dict) -> tuple:
    """
    Build condition recommendation list and determine dermatologist flag.

    Returns
    -------
    (recommendations: list[dict], see_dermatologist: bool)
    """
    severity_map = {
        "acne":         features["acne"]["severity"],
        "texture":      features["texture"]["severity"],
        "dark_circles": features["dark_circles"]["severity"],
        "wrinkles":     features["wrinkles"]["severity"],
        "tone":         features["tone"]["severity"],
    }

    recommendations = []
    see_dermatologist = False

    for condition, severity in severity_map.items():
        rules = _RULE_MAP[condition].get(severity, _RULE_MAP[condition]["none"])
        if severity == "severe":
            see_dermatologist = True

        rec = {
            "condition":          _CONDITION_LABELS[condition],
            "condition_key":      condition,
            "severity":           severity,
            "score":              scores.get(f"{condition.replace('dark_circles','dark_circle')}_score", 0),
            "causes":             rules["causes"],
            "routine_steps":      rules["routine_steps"],
            "lifestyle_changes":  rules["lifestyle_changes"],
            "ingredients_to_use": rules["ingredients_to_use"],
            "ingredients_to_avoid": rules["ingredients_to_avoid"],
            "see_dermatologist":  severity == "severe",
        }
        recommendations.append(rec)

    return recommendations, see_dermatologist

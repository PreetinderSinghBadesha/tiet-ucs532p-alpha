/**
 * dermaApi.js — HTTP client for the DERMA.ai backend.
 */

const BASE_URL = "/api";

/**
 * Analyze a face image with lifestyle metadata.
 *
 * @param {string} imageBase64   – base64 data URL from canvas/input
 * @param {object} lifestyleData – { sleep_hours, water_glasses, stress_level,
 *                                   diet_quality, current_skincare, skin_type }
 * @returns {Promise<object>}    – the full analysis JSON
 */
export async function analyzeSkin(imageBase64, lifestyleData) {
  const response = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: imageBase64, lifestyle: lifestyleData }),
  });

  if (!response.ok) {
    let errBody;
    try {
      errBody = await response.json();
    } catch {
      errBody = { message: await response.text() };
    }
    const err = new Error(errBody.message || "Analysis failed");
    err.code = errBody.error || "unknown_error";
    err.status = response.status;
    throw err;
  }

  return response.json();
}

/**
 * Ping the health endpoint.
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

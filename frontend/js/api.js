import { API_BASE } from "./config.js";

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, options);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body.detail) {
        detail =
          typeof body.detail === "string"
            ? body.detail
            : JSON.stringify(body.detail);
      }
    } catch {
      /* not JSON */
    }
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res;
}

/**
 * GET /exercise/random — Return random exercise with option to choose difficulty.
 * @param {string|null} trudnosc — łatwa | średnia | trudna | bardzo trudna
 */
export async function getRandomExercise(trudnosc = null) {
  const params = new URLSearchParams();
  if (trudnosc) params.set("trudnosc", trudnosc);
  const qs = params.toString();
  const res = await request(`/exercise/random${qs ? `?${qs}` : ""}`);
  return res.json();
}

/**
 * POST /upload — Upload audio file along with exercise id.
 * API indexes exercises by list position (0-based), not JSON `id` field.
 * @param {Blob} file
 * @param {number} exerciseIndex — index in cwiczenia_dykcja array
 */
export async function uploadAudio(file, exerciseIndex) {
  const form = new FormData();
  const name = file.type === "audio/wav" ? "recording.wav" : "recording.webm";
  form.append("file", file, name);
  form.append("exercise_id", String(exerciseIndex));
  const res = await request("/upload", { method: "POST", body: form });
  return res.json();
}

/**
 * GET /score/{audio_id} — Get report with all scores.
 */
export async function getScore(audioId) {
  const res = await request(`/score/${encodeURIComponent(audioId)}`);
  return res.json();
}

/**
 * GET /score/cer_vis/{audio_id} — Get HTML with CER visualization.
 */
export async function getCerVisualization(audioId) {
  const res = await request(`/score/cer_vis/${encodeURIComponent(audioId)}`);
  const text = await res.text();
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

/**
 * GET /transcription/{audio_id} — Get transcription and reference text.
 */
export async function getTranscription(audioId) {
  const res = await request(`/transcription/${encodeURIComponent(audioId)}`);
  return res.json();
}

/**
 * GET /audio/{audio_id} — Get Audio data (y, sample_rate, reference).
 */
export async function getAudio(audioId) {
  const res = await request(`/audio/${encodeURIComponent(audioId)}`);
  return res.json();
}

/**
 * GET /scores/history — Get list of all scores (previous attempts).
 */
export async function getScoresHistory() {
  const res = await request("/scores/history");
  return res.json();
}

/** GET /health */
export async function healthCheck() {
  const res = await request("/health");
  return res.json();
}

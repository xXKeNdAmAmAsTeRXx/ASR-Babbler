/** Sample rate for uploads — matches notebook and NeMo Polish ASR model. */
export const TARGET_SAMPLE_RATE = 16000;

/**
 * API base URL. Empty string = same origin (use dev proxy or mount static on API host).
 * Override: window.ASR_BUBBLER_API_BASE = "http://127.0.0.1:8000" before other scripts.
 */
export const API_BASE =
  typeof window !== "undefined" && window.ASR_BUBBLER_API_BASE != null
    ? String(window.ASR_BUBBLER_API_BASE).replace(/\/$/, "")
    : "";

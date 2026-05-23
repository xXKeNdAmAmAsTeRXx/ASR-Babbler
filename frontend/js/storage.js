const AUDIO_ID_KEY = "asr_bubbler_audio_id";
const COOKIE_MAX_AGE_DAYS = 7;

function setCookie(name, value, days) {
  const maxAge = days * 24 * 60 * 60;
  document.cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)};path=/;max-age=${maxAge};SameSite=Lax`;
}

function getCookie(name) {
  const prefix = `${encodeURIComponent(name)}=`;
  const parts = document.cookie.split(";").map((c) => c.trim());
  for (const part of parts) {
    if (part.startsWith(prefix)) {
      return decodeURIComponent(part.slice(prefix.length));
    }
  }
  return null;
}

function deleteCookie(name) {
  document.cookie = `${encodeURIComponent(name)}=;path=/;max-age=0;SameSite=Lax`;
}

/** Persist audio_id for score / CER / transcription endpoints. */
export function saveAudioId(audioId) {
  if (!audioId) return;
  try {
    sessionStorage.setItem(AUDIO_ID_KEY, audioId);
  } catch {
    /* sessionStorage blocked */
  }
  setCookie(AUDIO_ID_KEY, audioId, COOKIE_MAX_AGE_DAYS);
}

export function getAudioId() {
  try {
    const fromSession = sessionStorage.getItem(AUDIO_ID_KEY);
    if (fromSession) return fromSession;
  } catch {
    /* ignore */
  }
  return getCookie(AUDIO_ID_KEY);
}

export function clearAudioId() {
  try {
    sessionStorage.removeItem(AUDIO_ID_KEY);
  } catch {
    /* ignore */
  }
  deleteCookie(AUDIO_ID_KEY);
}

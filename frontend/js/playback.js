import { samplesToWavBlob } from "./wav.js";

/**
 * Parse `y` from GET /audio — mono (n,) or multi-channel (channels, n) as nested JSON lists.
 */
export function parseAudioSamples(y) {
  if (!Array.isArray(y) || y.length === 0) {
    throw new Error("Puste dane audio (y).");
  }
  if (typeof y[0] === "number") {
    return [y];
  }
  if (Array.isArray(y[0]) && typeof y[0][0] === "number") {
    return y;
  }
  throw new Error("Nierozpoznany format tablicy audio.");
}

function channelsToMono(channels) {
  const length = channels[0].length;
  const mono = new Float32Array(length);
  for (const ch of channels) {
    for (let i = 0; i < length; i++) {
      mono[i] += ch[i] / channels.length;
    }
  }
  return mono;
}

/**
 * Build object URL for <audio src> from API Audio payload { y, sample_rate, ... }.
 */
export function apiAudioToObjectUrl(audio) {
  const sampleRate = audio.sample_rate ?? audio.sr;
  if (!sampleRate) {
    throw new Error("Brak sample_rate w odpowiedzi audio.");
  }
  const channels = parseAudioSamples(audio.y);
  const mono = channelsToMono(channels);
  const blob = samplesToWavBlob(mono, sampleRate);
  return URL.createObjectURL(blob);
}

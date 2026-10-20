/**
 * Decode browser recording (WebM/OGG), resample to TARGET_SAMPLE_RATE, encode as WAV for librosa/ASR.
 */

import { TARGET_SAMPLE_RATE } from "./config.js";

function writeString(view, offset, str) {
  for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i));
  }
}

function mixToMono(audioBuffer) {
  const { length, numberOfChannels } = audioBuffer;
  const mono = new Float32Array(length);
  for (let ch = 0; ch < numberOfChannels; ch++) {
    const channel = audioBuffer.getChannelData(ch);
    for (let i = 0; i < length; i++) {
      mono[i] += channel[i] / numberOfChannels;
    }
  }
  return mono;
}

/** Resample decoded audio to the ASR target rate (e.g. 16 kHz). */
async function resampleAudioBuffer(buffer, targetSampleRate) {
  if (buffer.sampleRate === targetSampleRate) {
    return buffer;
  }
  const length = Math.max(1, Math.ceil(buffer.duration * targetSampleRate));
  const offline = new OfflineAudioContext(
    buffer.numberOfChannels,
    length,
    targetSampleRate
  );
  const source = offline.createBufferSource();
  source.buffer = buffer;
  source.connect(offline.destination);
  source.start(0);
  return offline.startRendering();
}

function encodeWav(samples, sampleRate) {
  const numChannels = 1;
  const bitsPerSample = 16;
  const blockAlign = (numChannels * bitsPerSample) / 8;
  const byteRate = sampleRate * blockAlign;
  const dataSize = samples.length * 2;
  const buffer = new ArrayBuffer(44 + dataSize);
  const view = new DataView(buffer);

  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + dataSize, true);
  writeString(view, 8, "WAVE");
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitsPerSample, true);
  writeString(view, 36, "data");
  view.setUint32(40, dataSize, true);

  let offset = 44;
  for (let i = 0; i < samples.length; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    offset += 2;
  }

  return new Blob([buffer], { type: "audio/wav" });
}

/** @param {Float32Array|number[]} samples */
export function samplesToWavBlob(samples, sampleRate) {
  const floats =
    samples instanceof Float32Array ? samples : new Float32Array(samples);
  return encodeWav(floats, sampleRate);
}

/**
 * @param {Blob} blob — WebM/OGG/etc. from MediaRecorder
 * @returns {Promise<Blob>} mono WAV at TARGET_SAMPLE_RATE (16 kHz)
 */
export async function blobToWav(blob) {
  const arrayBuffer = await blob.arrayBuffer();
  const ctx = new AudioContext();
  try {
    const decoded = await ctx.decodeAudioData(arrayBuffer.slice(0));
    const resampled = await resampleAudioBuffer(decoded, TARGET_SAMPLE_RATE);
    const mono = mixToMono(resampled);
    return encodeWav(mono, TARGET_SAMPLE_RATE);
  } finally {
    await ctx.close();
  }
}

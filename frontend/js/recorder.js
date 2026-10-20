import { TARGET_SAMPLE_RATE } from "./config.js";

/**
 * Browser audio capture via MediaRecorder.
 * Upload path resamples to 16 kHz in wav.js; constraints ask the device when possible.
 */
export class AudioRecorder {
  constructor() {
    this.mediaRecorder = null;
    this.chunks = [];
    this.stream = null;
    this.startedAt = null;
  }

  get isRecording() {
    return this.mediaRecorder?.state === "recording";
  }

  async start() {
    if (this.isRecording) return;
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: { ideal: 1 },
        sampleRate: { ideal: TARGET_SAMPLE_RATE },
      },
    });
    const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
      ? "audio/webm;codecs=opus"
      : "audio/webm";
    this.mediaRecorder = new MediaRecorder(this.stream, { mimeType });
    this.chunks = [];
    this.mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) this.chunks.push(e.data);
    };
    this.mediaRecorder.start();
    this.startedAt = Date.now();
  }

  stop() {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder || this.mediaRecorder.state === "inactive") {
        this._releaseStream();
        reject(new Error("Brak nagrania do zatrzymania."));
        return;
      }
      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.chunks, { type: this.mediaRecorder.mimeType });
        const durationMs = this.startedAt ? Date.now() - this.startedAt : 0;
        this._releaseStream();
        resolve({ blob, durationMs });
      };
      this.mediaRecorder.onerror = () => {
        this._releaseStream();
        reject(new Error("Błąd nagrywania."));
      };
      this.mediaRecorder.stop();
    });
  }

  _releaseStream() {
    if (this.stream) {
      this.stream.getTracks().forEach((t) => t.stop());
      this.stream = null;
    }
  }
}

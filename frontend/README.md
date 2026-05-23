# ASR Bubbler — Frontend

Vanilla HTML/CSS/JS UI styled similarly to [Human Benchmark](https://humanbenchmark.com/): dark, minimal, centered layout.

## Flow

1. **Losuj tekst** — `GET /exercise/random` (optional `trudnosc` filter)
2. **Nagraj** — browser microphone (`MediaRecorder`, WebM)
3. **Wyślij i oceń** — converts to **mono WAV at 16 kHz** in the browser (same as notebook; librosa does not read WebM), then `POST /upload` with `exercise_id` (list index: `exercise.id - 1`)
4. **Wyniki** — `GET /score/{audio_id}`, `GET /transcription/{audio_id}`, `GET /score/cer_vis/{audio_id}`, `GET /audio/{audio_id}` (odtwarzanie nagrania w przeglądarce)

`audio_id` is stored in **sessionStorage** and a **cookie** (`asr_bubbler_audio_id`, 7 days) so scores and CER HTML can be reloaded after refresh.

## Run locally

**Terminal 1 — API** (from repo root):

```bash
uv run uvicorn API.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — frontend + proxy** (no CORS changes to API):

```bash
uv run python frontend/serve.py
```

Open **http://127.0.0.1:8080**

The dev proxy forwards `/exercise/*`, `/upload`, `/score/*`, `/transcription/*`, `/audio/*`, and `/health` to the API on port 8000.

## Alternative: direct API URL

If the API is served with CORS enabled elsewhere, set before scripts load:

```html
<script>window.ASR_BUBBLER_API_BASE = "http://127.0.0.1:8000";</script>
```

Then serve only static files (e.g. `python -m http.server 8080 --directory frontend`).

## Files

| File | Role |
|------|------|
| `index.html` | Page structure |
| `css/style.css` | Human Benchmark–like dark theme |
| `js/api.js` | API client (mirrors `API/main.py` docstrings) |
| `js/storage.js` | `audio_id` in session + cookie |
| `js/recorder.js` | Microphone capture |
| `js/app.js` | UI logic |
| `serve.py` | Static + API proxy for development |

"""NeMo CTC word timestamps: offset units depend on model stride; calibrate from audio length."""

from __future__ import annotations

import string

import numpy as np

PUNCTUATION = set(string.punctuation)


def is_punctuation_token(word: str) -> bool:
    stripped = word.strip()
    return not stripped or all(ch in PUNCTUATION for ch in stripped)


def audio_duration_seconds(audio: np.ndarray, sr: int) -> float:
    n_samples = int(audio.shape[-1]) if audio.ndim > 1 else int(audio.size)
    return n_samples / float(sr)


def frame_duration_from_timestamps(
    word_timestamps: list[dict], audio_duration_s: float, *, fallback: float = 0.01
) -> float:
    """Map NeMo frame indices to seconds using full audio length and max end offset."""
    if not word_timestamps or audio_duration_s <= 0:
        return fallback
    max_end = max(int(entry["end_offset"]) for entry in word_timestamps)
    if max_end <= 0:
        return fallback
    return audio_duration_s / max_end

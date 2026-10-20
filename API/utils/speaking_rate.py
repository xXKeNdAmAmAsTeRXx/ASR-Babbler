from __future__ import annotations

import numpy as np

from API.utils.timestamps import frame_duration_from_timestamps, is_punctuation_token

OPTIMUM_WPM = 130.0
WPM_TOLERANCE = 100.0


def speaking_rate_metrics(
    word_timestamps: list[dict],
    *,
    audio_duration_s: float | None = None,
) -> dict[str, float]:
    """
    Words per minute from NeMo word timestamps.

    Offsets are frame indices (FastConformer ~80 ms/frame), not 10 ms.
    When audio_duration_s is given, frame length is calibrated as
    audio_duration_s / max(end_offset) so the span matches real time.
    """
    words = [e for e in word_timestamps if not is_punctuation_token(e["word"])]

    if len(words) < 2:
        return {"speaking_rate_wpm": 0.0, "speaking_rate_score": 0.0}

    if audio_duration_s is not None and audio_duration_s > 0:
        frame_duration = frame_duration_from_timestamps(word_timestamps, audio_duration_s)
    else:
        frame_duration = 0.01

    start_s = int(words[0]["start_offset"]) * frame_duration
    end_s = int(words[-1]["end_offset"]) * frame_duration
    total_speech_time = end_s - start_s

    if total_speech_time <= 0:
        return {"speaking_rate_wpm": 0.0, "speaking_rate_score": 0.0}

    wpm = float(len(words) / total_speech_time * 60)
    rate_score = float(np.clip(1.0 - abs(wpm - OPTIMUM_WPM) / WPM_TOLERANCE, 0, 1))

    return {
        "speaking_rate_wpm": wpm,
        "speaking_rate_score": rate_score,
    }

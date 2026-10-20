from __future__ import annotations

from API.utils.timestamps import frame_duration_from_timestamps


def word_metrics(
    hyp,
    *,
    frame_duration: float | None = None,
    audio_duration_s: float | None = None,
) -> dict:
    word_start, word_end, word_hypothesis, word_confidence = [], [], [], []

    timestamps = hyp.timestep["word"]
    if frame_duration is None:
        if audio_duration_s is not None and audio_duration_s > 0:
            frame_duration = frame_duration_from_timestamps(timestamps, audio_duration_s)
        else:
            frame_duration = 0.01

    for entry, word_conf in zip(timestamps, hyp.word_confidence):
        word = entry["word"]
        start_s = int(entry["start_offset"]) * frame_duration
        end_s = int(entry["end_offset"]) * frame_duration

        word_start.append(start_s)
        word_end.append(end_s)
        word_hypothesis.append(word)
        word_confidence.append(word_conf)

    return {
        "word_start": word_start,
        "word_end": word_end,
        "word_hypothesis": word_hypothesis,
        "word_confidence": word_confidence,
    }

import numpy as np

PUNCTUATION = {'.', ',', '!', '?', ':', ';', '-'}
FRAME_DURATION = 0.01  # seconds per frame


def speaking_rate_metrics(word_timestamps: list[dict]) -> dict:
    words = [e for e in word_timestamps if e['word'] not in PUNCTUATION]

    if len(words) < 2:
        return {'speaking_rate_wpm': 0.0, 'speaking_rate_score': 0.0}

    total_speech_time = (words[-1]['end_offset'] - words[0]['start_offset']) * FRAME_DURATION
    wpm = float((len(words) / total_speech_time) * 60) if total_speech_time > 0 else 0.0

    # normalize: optimum WPM is 130 WPM, <80 and >200 are considered abnormal
    rate_score = float(np.clip(1.0 - abs(wpm - 130) / 100, 0, 1))

    return {
        'speaking_rate_wpm': wpm,
        'speaking_rate_score': rate_score,
    }
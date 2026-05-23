import numpy as np
import librosa


def zcr_metrics(audio: np.ndarray, hop_length: int = 256, silence_threshold: float = 0.02) -> dict:
    rms = librosa.feature.rms(y=audio, hop_length=hop_length)[0]
    zcr = librosa.feature.zero_crossing_rate(audio, hop_length=hop_length)[0]

    speech_frames = rms > silence_threshold
    mean_zcr = float(np.mean(zcr[speech_frames])) if np.any(speech_frames) else 0.0

    # normalize: higher ZCR in speech shows better articulation
    zcr_score = float(np.clip((mean_zcr - 0.03) / 0.12, 0, 1))

    return {
        'zcr_mean': mean_zcr,
        'zcr_score': zcr_score,
    }

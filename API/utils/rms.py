import numpy as np
import librosa


def rms_metrics(audio: np.ndarray, hop_length: int = 256) -> dict:
    rms = librosa.feature.rms(y=audio, hop_length=hop_length)[0]

    mean_rms = float(np.mean(rms))
    std_rms = float(np.std(rms))

    # normalize: stability score is better when std is lower
    rms_stability = float(1.0 - np.clip(std_rms / 0.1, 0, 1))

    return {
        'rms_mean': mean_rms,
        'rms_std': std_rms,
        'rms_stability': rms_stability,
    }
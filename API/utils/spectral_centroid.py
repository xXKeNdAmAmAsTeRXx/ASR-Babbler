import numpy as np
import librosa


def spectral_centroid_metrics(audio: np.ndarray, sr: int, S: np.ndarray = None, hop_length: int = 256) -> dict:
    if S is None:
        S = np.abs(librosa.stft(audio, hop_length=hop_length))

    centroid = librosa.feature.spectral_centroid(S=S, sr=sr)[0]
    mean_centroid = float(np.mean(centroid))

    # normalize: higher centroid shows better articulation, typical speech range 1000–3500 Hz
    centroid_score = float(np.clip((mean_centroid - 1000) / 2500, 0, 1))

    return {
        'spectral_centroid_hz': mean_centroid,
        'spectral_centroid_score': centroid_score,
    }
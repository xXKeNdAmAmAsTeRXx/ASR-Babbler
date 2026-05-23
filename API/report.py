import numpy as np
import librosa
from jiwer import cer
from API.utils.word_metrics import word_metrics
from API.utils.cer import highlight_cer
from API.utils.rms import rms_metrics
from API.utils.zcr import zcr_metrics
from API.utils.spectral_centroid import spectral_centroid_metrics
from API.utils.speaking_rate import speaking_rate_metrics

def report(ref, hyp, audio: np.ndarray, sr: int) -> dict:
    conf_score = 1 - np.exp(hyp.score)
    S = np.abs(librosa.stft(audio, n_fft=1024, hop_length=256))

    return {
        'transcription': hyp.text,
        'reference': ref,
        'confidence': conf_score,
        'cer_score': cer(ref, hyp.text),
        'vis_cer': highlight_cer(ref, hyp.text),
        **word_metrics(hyp),
        **rms_metrics(audio),
        **zcr_metrics(audio),
        **spectral_centroid_metrics(audio, sr, S=S),
        **speaking_rate_metrics(hyp.timestep['word']),
    }
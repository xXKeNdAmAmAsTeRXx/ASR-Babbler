from typing import Any

import numpy as np
import librosa
from jiwer import cer
from numpy import dtype, ndarray

from API.utils.word_metrics import word_metrics
from API.utils.cer import highlight_cer
from API.utils.rms import rms_metrics
from API.utils.zcr import zcr_metrics
from API.utils.spectral_centroid import spectral_centroid_metrics
from API.utils.speaking_rate import speaking_rate_metrics

def report(ref, hyp, audio: np.ndarray, sr: int) -> tuple[
    dict[str, ndarray[tuple[Any, ...], dtype[Any]] | float | None | Any], ndarray[tuple[Any, ...], dtype[
        Any]] | float | None | Any]:
    conf_score = 1 - np.exp(hyp.score)
    S = np.abs(librosa.stft(audio, n_fft=1024, hop_length=256))


    # Bajon insisted we need it for future development
    report = {
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

    return {
        'confidence': conf_score,
        'cer_score': cer(ref, hyp.text),
        'rms_stability': report['rms_stability'],
        'zcr_score': report['zcr_score'],
        'spectral_centroid_score': report['spectral_centroid_score'],
        'speaking_rate_wpm': report['wpm'],
        'speaking_rate_score': report['rate_score']
    }, report['vis_cer']
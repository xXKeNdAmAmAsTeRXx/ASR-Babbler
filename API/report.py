import numpy as np
from jiwer import cer
from API.utils.word_metrics import word_metrics
from API.utils.cer import highlight_cer

def report(ref, hyp):
    conf_score = 1 - np.exp(hyp.score)
    cer_score = cer(ref, hyp.text)
    word_start, word_end, word_hypothesis, word_confidence = word_metrics(hyp)

    report = {
        'transcription': hyp.text,
        'reference': ref,
        'confidence': conf_score,
        'cer_score': cer_score,
        'vis_cer': highlight_cer(ref, hyp.text),
        'word_start': word_start,
        'word_end': word_end,
        'word_hypothesis': word_hypothesis,
        'word_confidence': word_confidence
    }

    return report
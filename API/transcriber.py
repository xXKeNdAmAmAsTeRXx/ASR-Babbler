def transcribe_audio(audio, asr_model):
    return asr_model.transcribe([audio], return_hypotheses=True)[0][0]

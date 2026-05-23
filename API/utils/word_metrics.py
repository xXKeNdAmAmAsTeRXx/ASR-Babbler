def word_metrics(hyp):
    word_start, word_end, word_hypothesis, word_confidence = [], [], [], []
    frame_duration = 0.01

    for entry, word_conf in zip(hyp.timestep['word'], hyp.word_confidence):
        word = entry['word']
        start_s = entry['start_offset'] * frame_duration
        end_s = entry['end_offset'] * frame_duration
        print(f"{word:25s} {start_s:.2f}s - {end_s:.2f}s  conf={word_conf:.3f}")

        word_start.append(start_s)
        word_end.append(end_s)
        word_hypothesis.append(word)
        word_confidence.append(word_conf)

    return word_start, word_end, word_hypothesis, word_confidence
import difflib
from jiwer import cer
from IPython.display import HTML, display

def char_diff_html(a: str, b: str, color: str) -> tuple[str, str]:
    bg = {"red": ("#FCEBEB", "#A32D2D"), "amber": ("#FAEEDA", "#633806")}[color]
    matcher = difflib.SequenceMatcher(None, a, b)
    a_out, b_out = [], []
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        ac, bc = a[i1:i2], b[j1:j2]
        s = f'background:{bg[0]};color:{bg[1]};border-radius:3px;padding:0 1px'
        if op == 'equal':
            a_out.append(ac); b_out.append(bc)
        elif op == 'replace':
            a_out.append(f'<span style="{s}">{ac}</span>')
            b_out.append(f'<span style="{s}">{bc}</span>')
        elif op == 'delete':
            a_out.append(f'<span style="{s}">{ac}</span>')
        elif op == 'insert':
            b_out.append(f'<span style="{s}">{bc}</span>')
    return ''.join(a_out), ''.join(b_out)

def highlight_cer(reference: str, hypothesis: str) -> None:
    cer_score = cer(reference, hypothesis)

    ref_words = reference.split()
    hyp_words = hypothesis.split()

    matcher = difflib.SequenceMatcher(None, ref_words, hyp_words)
    ref_html, hyp_html = [], []

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == 'equal':
            ref_html.append(' '.join(ref_words[i1:i2]))
            hyp_html.append(' '.join(hyp_words[j1:j2]))
        elif op == 'replace':
            ref_str = ' '.join(ref_words[i1:i2])
            hyp_str = ' '.join(hyp_words[j1:j2])
            r, h = char_diff_html(ref_str, hyp_str, "red")
            ref_html.append(r); hyp_html.append(h)
        elif op == 'delete':
            s = f'background:#FCEBEB;color:#A32D2D;border-radius:3px;padding:0 2px'
            ref_html.append(f'<span style="{s}">{" ".join(ref_words[i1:i2])}</span>')
        elif op == 'insert':
            s = f'background:#FAEEDA;color:#633806;border-radius:3px;padding:0 2px'
            hyp_html.append(f'<span style="{s}">{" ".join(hyp_words[j1:j2])}</span>')

    html = f"""
    <div style="font-family:monospace;font-size:14px;line-height:2">
        <div style="margin-bottom:8px">
            <span style="font-size:12px;color:#888">CER: </span>
            <strong>{(1-cer_score)*100:.1f}</strong>
        </div>
        <div style="margin-bottom:12px">
            <span style="font-size:11px;color:#888;display:block;margin-bottom:2px">referencja</span>
            {' '.join(ref_html)}
        </div>
        <div>
            <span style="font-size:11px;color:#888;display:block;margin-bottom:2px">transkrypcja</span>
            {' '.join(hyp_html)}
        </div>
    </div>
    """
    display(HTML(html))
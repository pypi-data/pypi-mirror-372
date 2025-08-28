import re
from meowsum import meow


WORD_RE = re.compile(r"^me+(?:o+)?w$")


def _tokenize_phrase(phrase: str) -> list[str]:
    # Strip optional surrounding quotes
    if len(phrase) >= 2 and phrase[0] == phrase[-1] and phrase[0] in {'"', "'"}:
        phrase = phrase[1:-1]

    tokens = []
    for raw in phrase.split():
        t = raw

        # Remove trailing commas
        if t.endswith(","):
            t = t[:-1]

        # Remove terminal punctuation ., !, ?, ... (strip all trailing . ! ?)
        while t and t[-1] in {".", "!", "?"}:
            t = t[:-1]

        # Remove surrounding parentheses
        t = t.lstrip("(").rstrip(")")

        # Remove any stray quotes (defensive)
        t = t.strip('"\'')

        tokens.append(t.lower())
    return tokens


def test_word_shape_and_length():
    for _ in range(1000):
        w = meow.word()
        assert WORD_RE.match(w), f"Bad shape: {w!r}"
        assert len(w) <= 10, f"Word too long: {w!r} (len={len(w)})"


def test_bias_plain_meow_dominates():
    meow.seed(12345)
    total = 2000
    cnt = sum(1 for _ in range(total) if meow.word() == "meow")
    frac = cnt / total
    assert frac >= 0.5, f"Expected majority 'meow', got fraction={frac:.3f}"


def test_phrase_exact_word_count_and_tokens_shape():
    meow.seed(1)
    p = meow.phrase(words_count=8)
    toks = _tokenize_phrase(p)
    assert len(toks) == 8, f"Expected 8 tokens, got {len(toks)}: {p!r}"
    for t in toks:
        assert WORD_RE.match(t), f"Token not a meow word: {t!r} in phrase {p!r}"


def test_phrases_list_count_and_each_words_count():
    meow.seed(2)
    lines = meow.phrases(n=3, words_count=5, as_list=True)
    assert isinstance(lines, list)
    assert len(lines) == 3
    for line in lines:
        toks = _tokenize_phrase(line)
        assert len(toks) == 5, f"Expected 5 tokens, got {len(toks)}: {line!r}"
        for t in toks:
            assert WORD_RE.match(t), f"Token not a meow word: {t!r} in phrase {line!r}"


def test_seed_determinism():
    meow.seed(42)
    a = meow.phrases(n=2, words_count=4, as_list=True)
    meow.seed(42)
    b = meow.phrases(n=2, words_count=4, as_list=True)
    assert a == b, "Outputs should match under the same seed"


def test_text_html_wrapping():
    meow.seed(7)
    out = meow.text(paragraphs_count=2, html=True)
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 2
    for ln in lines:
        assert ln.startswith("<p>") and ln.endswith("</p>"), f"Paragraph not HTML-wrapped: {ln!r}"

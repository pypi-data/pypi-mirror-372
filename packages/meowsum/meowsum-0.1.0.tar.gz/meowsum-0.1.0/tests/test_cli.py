import re
import subprocess
import sys


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


def _run_cli(*args: str) -> str:
    proc = subprocess.run(
        [sys.executable, "-m", "meowsum", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.stdout.strip()


def test_cli_phrases_and_words_exact_counts():
    out = _run_cli("--seed", "123", "--phrases", "3", "--words", "4")
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 3, f"Expected 3 phrases, got {len(lines)}: {out!r}"
    for line in lines:
        toks = _tokenize_phrase(line)
        assert len(toks) == 4, f"Expected 4 tokens per phrase, got {len(toks)}: {line!r}"
        for t in toks:
            assert WORD_RE.match(t), f"Bad token shape: {t!r}"


def test_cli_words_only():
    out = _run_cli("--seed", "777", "--words", "7")
    toks = [t.lower() for t in out.split()]
    assert len(toks) == 7, f"Expected 7 words, got {len(toks)}: {out!r}"
    for t in toks:
        assert WORD_RE.match(t), f"Bad token shape: {t!r}"


def test_cli_seed_determinism():
    a = _run_cli("--seed", "99", "--phrases", "2", "--words", "5")
    b = _run_cli("--seed", "99", "--phrases", "2", "--words", "5")
    assert a == b, "CLI output should be deterministic under the same seed"


def test_cli_sentences_range_and_paragraphs_html():
    # Sentences with range (no exact words) should run and produce non-empty output
    out = _run_cli("--seed", "5", "--sentences", "2", "--min-words", "4", "--max-words", "6")
    assert out, "Expected non-empty output for sentences mode"

    # Paragraphs with HTML wrapping should wrap each paragraph
    out2 = _run_cli("--seed", "6", "--paragraphs", "2", "--html")
    lines = [ln for ln in out2.splitlines() if ln.strip()]
    assert len(lines) == 2
    for ln in lines:
        assert ln.startswith("<p>") and ln.endswith("</p>"), f"Paragraph not HTML-wrapped: {ln!r}"


def test_cli_default_is_single_paragraph_500_words():
    out = _run_cli()
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 1, f"Expected 1 paragraph line by default, got {len(lines)}: {out!r}"
    toks = _tokenize_phrase(lines[0])
    assert len(toks) == 500, f"Default output should be 500 words, got {len(toks)}"

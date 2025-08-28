from __future__ import annotations

import argparse
import sys
from typing import Tuple

from . import meow


def _range_tuple(min_val: int | None, max_val: int | None, default_min: int, default_max: int) -> Tuple[int, int]:
    lo = default_min if min_val is None else int(min_val)
    hi = default_max if max_val is None else int(max_val)
    if lo > hi:
        lo, hi = hi, lo
    return max(0, lo), max(0, hi)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="meowsum",
        description="Meow ipsum generator: cat-sound placeholder text (meow, meeeow, meeooow, ...).",
    )

    # Selection of what to generate
    p.add_argument("--phrases", type=int, help="Number of phrases to generate. Requires --words.")
    p.add_argument("--sentences", type=int, help="Number of sentences to generate.")
    p.add_argument("--paragraphs", type=int, help="Number of paragraphs to generate.")
    p.add_argument("--words", type=int, help="Word count. With --phrases: words per phrase. With --sentences: words per sentence. Alone: generate exactly this many words.")

    # Ranges for when exact counts are not provided
    p.add_argument("--min-words", type=int, help="Minimum words per sentence (when --words is not given).")
    p.add_argument("--max-words", type=int, help="Maximum words per sentence (when --words is not given).")
    p.add_argument("--min-sentences", type=int, help="Minimum sentences per paragraph (default 3).")
    p.add_argument("--max-sentences", type=int, help="Maximum sentences per paragraph (default 7).")

    # Formatting options
    p.add_argument("--html", action="store_true", help="Wrap paragraphs in <p>...</p> (only used with --paragraphs).")
    p.add_argument("--no-punct", action="store_true", help="Disable punctuation in phrases/sentences.")

    # Reproducibility / tuning
    p.add_argument("--seed", type=int, help="Random seed for reproducible output.")
    p.add_argument("--meow-bias", type=float, help='Probability that a word is exactly "meow" (default 0.7).', dest="meow_bias")

    return p


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.seed is not None:
        meow.seed(args.seed)

    # Allow tweaking meow bias globally by temporarily wrapping meow.word
    if args.meow_bias is not None:
        bias = float(args.meow_bias)
        bias = 0.0 if bias < 0 else 1.0 if bias > 1 else bias

        _orig_word = meow.word

        def _biased_word(*wargs, **wkwargs):
            wkwargs.setdefault("meow_bias", bias)
            return _orig_word(*wargs, **wkwargs)

        meow.word = _biased_word  # type: ignore

    punctuation = not args.no_punct

    # Priority: explicit pair --phrases and --words
    if args.phrases is not None:
        if args.words is None:
            parser.error("--phrases requires --words to specify words per phrase.")
        n = max(0, int(args.phrases))
        w = max(0, int(args.words))
        out = meow.phrases(n=n, words_count=w, punctuation=punctuation)
        print(out)
        return 0

    # Next: sentences or paragraphs or bare words
    if args.sentences is not None:
        n = max(0, int(args.sentences))
        if args.words is not None:
            w = max(0, int(args.words))
            out = meow.sentences(n=n, words=w, punctuation=punctuation)
        else:
            wr = _range_tuple(args.min_words, args.max_words, 4, 12)
            out = meow.sentences(n=n, words=None, word_range=wr, punctuation=punctuation)
        print(out)
        return 0

    if args.paragraphs is not None:
        n = max(0, int(args.paragraphs))
        sr = _range_tuple(args.min_sentences, args.max_sentences, 3, 7)
        if args.html:
            out = meow.text(paragraphs_count=n, sentence_range=sr, html=True)
        else:
            out = meow.paragraphs(n=n, sentence_range=sr, as_list=False)
        print(out)
        return 0

    # Fallback: if user provided only --words, emit exactly that many words
    if args.words is not None:
        w = max(0, int(args.words))
        print(meow.words(w))
        return 0

    # Default behavior: one paragraph of 500 words
    print(meow.phrases(n=1, words_count=500))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

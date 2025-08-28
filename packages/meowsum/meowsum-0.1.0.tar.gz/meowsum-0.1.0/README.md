# Meowsum

Cat-sound lorem ipsum generator. Produces text composed of “meow” variants like: meow, meeeow, meeooow, meeeoooow, etc.

Key properties:
- Word shape: m + e* + o* + w
- Hard cap: each word length ≤ 10 characters
- Distribution: plain “meow” appears more often than any variant (default bias ~70%)
- Punctuation: sometimes includes ., ..., !, ?, , and quotes " or ' in phrases/sentences
- Deterministic mode via seed()

## Install

```bash
pip install meowsum
```

Local dev:

```bash
pip install -e .
```

## Quickstart

Python:

```python
from meowsum import meow

print(meow.words(5))             # e.g., "meow meow meeoow meow meow"
print(meow.sentence(words=8))    # one phrase of exactly 8 words
print("\n\n".join(meow.paragraphs(2)))  # two paragraphs
```

CLI:

```bash
# Exactly N phrases of M words
meowsum --phrases 2 --words 6

# N sentences (word count sampled in [min, max])
meowsum --sentences 3 --min-words 5 --max-words 10

# N paragraphs, optionally HTML-wrapped
meowsum --paragraphs 2 --html

# Make output deterministic
meowsum --phrases 2 --words 5 --seed 42
```

Examples:

```
$ meowsum --phrases 1 --words 6
Meeoow meow meow meow, meow meeeow.
```

```
$ meowsum --paragraphs 1 --html
<p>Meeoow meow meow meow? Meeoow meow meow meow meow meow. Meow meow meow...</p>
```

## API

The public API mirrors common lorem-ipsum ergonomics but strictly outputs cat sounds.

- meow.seed(value: int | None) -> None  
  Seed the internal RNG for reproducible output.

- meow.word(e_range=(1, 5), o_range=(1, 7), max_len=10, capitalize=False, meow_bias=0.7) -> str  
  Generate one word obeying:
  - shape m + e* + o* + w
  - length ≤ max_len (default 10)
  - “meow” appears more often than variants (controlled by meow_bias)

- meow.words(n=1, as_list=False, sep=" ") -> str | list[str]  
  Generate n words (joined by sep unless as_list=True).

- meow.phrase(words_count: int, punctuation=True) -> str  
  Exactly words_count words, capitalize first token, sometimes include commas, always end with [., !, ?, ...], and occasionally wrap in quotes.

- meow.phrases(n: int, words_count: int, as_list=False, punctuation=True) -> str | list[str]  
  Generate n phrases, each with words_count words. Joined by newline unless as_list=True.

- meow.sentence(words: int | None = None, word_range=(4, 12), punctuation=True) -> str  
  Convenience alias for a single phrase. If words is None, samples uniformly from word_range.

- meow.sentences(n=1, words: int | None = None, word_range=(4, 12), as_list=False, punctuation=True) -> str | list[str]  
  Multiple sentences. Joined by space unless as_list=True.

- meow.paragraph(sentence_range=(3, 7)) -> str  
  Paragraph with a sampled number of sentences.

- meow.paragraphs(n=1, sentence_range=(3, 7), as_list=False) -> str | list[str]  
  Multiple paragraphs (double-newline separated unless as_list=True).

- meow.text(paragraphs_count=3, sentence_range=(3, 7), html=False) -> str  
  Produce multiple paragraphs; html=True wraps each as <p>...</p>.

## CLI

Console script: meowsum

- Selection
  - --phrases N --words M       Generate N phrases, each with exactly M words
  - --sentences N               Generate N sentences (pair with --words or use --min-words/--max-words)
  - --paragraphs N              Generate N paragraphs (pair with --html optionally)
  - --words M                   Generate exactly M words (standalone)

- Ranges
  - --min-words X --max-words Y
  - --min-sentences A --max-sentences B

- Formatting
  - --html                      Wrap paragraphs in <p>...</p> (only with --paragraphs)
  - --no-punct                  Disable punctuation for phrases/sentences

- Reproducibility / tuning
  - --seed INT
  - --meow-bias FLOAT           Probability a word is exactly “meow” (default 0.7)

Notes:
- Default: Running meowsum with no options prints a single paragraph of 500 words.
- When both --phrases and --words are given, you get N phrases with exactly M words each (as requested).
- Each word never exceeds 10 characters; samplers honor this cap.
- Punctuation can appear mid-sentence (commas, !, ?, ...), and sentences end with one of ., !, ?, .... Occasionally an entire phrase is wrapped in quotes, and a pair of parentheses may span 1–10 words.

## Rationale and behavior

- Word shape strictly enforced as “m + multiple e + multiple o + w”.
- Bias: “meow” dominates to keep content readable and compact; variants are sprinkled in.
- Length cap ensures consistent visual width and avoids extreme stretched variants.

## Development

Build:

```bash
python -m pip install -U build
python -m build
```

Run tests (if pytest is available):

```bash
pytest -q
```

## License

MIT

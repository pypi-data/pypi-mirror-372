from __future__ import annotations

import random
from typing import Iterable, List, Sequence, Tuple, Union

# Module-level RNG with optional seeding via seed()
_rng = random.Random()

# Default weights and probabilities
_DEFAULT_MEOW_BIAS = 0.7  # Probability to emit exactly "meow"
_DEFAULT_END_PUNCT_WEIGHTS = (
    (".", 0.7),
    ("!", 0.15),
    ("?", 0.1),
    ("...", 0.05),
)
_DEFAULT_QUOTE_PROB = 0.03  # Reduced again: chance to wrap a phrase in quotes
_Default_COMMA_PROB_OLD = 0.12
_DEFAULT_COMMA_PROB = 0.045  # Reduced again: per-gap probability to insert a comma (no space before, space after)

# Inner punctuation probabilities (mid-sentence)
_DEFAULT_INNER_EXCLAM_PROB = 0.005
_DEFAULT_INNER_QUEST_PROB = 0.005
_DEFAULT_INNER_ELLIPSIS_PROB = 0.0075

# Parentheses behavior
_DEFAULT_BRACKET_OPEN_PROB = 0.02
_DEFAULT_BRACKET_CLOSE_MAX_SPAN = 10

# Optional "mew" probability (emit mew without 'o')
_DEFAULT_MEW_PROB = 0.05


def seed(value: Union[int, None]) -> None:
    """
    Seed the internal random generator for reproducible output.
    """
    _rng.seed(value)


def _weighted_choice(choices_with_weights: Sequence[Tuple[str, float]]) -> str:
    total = sum(w for _, w in choices_with_weights)
    r = _rng.random() * total
    upto = 0.0
    for choice, w in choices_with_weights:
        upto += w
        if r <= upto:
            return choice
    return choices_with_weights[-1][0]


def _sample_lengths(
    e_range: Tuple[int, int],
    o_range: Tuple[int, int],
    max_len: int,
) -> Tuple[int, int]:
    """
    Sample (E, O) such that:
      - E in e_range, O in o_range
      - total word length len("m" + "e"*E + "o"*O + "w") <= max_len  -> E + O <= max_len - 2
      - Not both E == 1 and O == 1 (reserved for exact 'meow' path)
    Uses simple rejection sampling biased to lower values by attempting small values first.
    """
    e_min, e_max = e_range
    o_min, o_max = o_range
    cap = max_len - 2
    if cap < 2:  # must allow at least E=1,O=1
        cap = 2

    # Build candidate lists biased toward small values
    e_candidates = list(range(e_min, e_max + 1))
    o_candidates = list(range(o_min, o_max + 1))

    # Shuffle lightly but preserve bias by sorting after shuffling on value
    _rng.shuffle(e_candidates)
    _rng.shuffle(o_candidates)
    e_candidates.sort()
    o_candidates.sort()

    # Try a bounded number of attempts
    for _ in range(64):
        e = _rng.choice(e_candidates)
        o = _rng.choice(o_candidates)
        if e + o <= cap and not (e == 1 and o == 1):
            return e, o

    # Fallback: clamp to fit
    e = max(e_min, min(e_max, cap - 1))
    o = max(o_min, min(o_max, cap - e))
    if e + o > cap:
        o = max(o_min, cap - e)
    if e + o < 2:
        e = 1
        o = 1
    if e == 1 and o == 1 and cap >= 3:
        # Try to bump one dimension to avoid exact "meow"
        if e_max >= 2 and 2 + o <= cap:
            e = 2
        elif o_max >= 2 and e + 2 <= cap:
            o = 2
    return e, o


def word(
    e_range: Tuple[int, int] = (1, 5),
    o_range: Tuple[int, int] = (1, 7),
    max_len: int = 10,
    capitalize: bool = False,
    meow_bias: float = _DEFAULT_MEOW_BIAS,
) -> str:
    """
    Generate a single cat-sound word with shape: 'm' + 'e'*E + 'o'*O + 'w'.

    Constraints:
      - Each word's total length <= max_len (default 10).
      - Exact 'meow' appears more frequently than variants (controlled by meow_bias).

    Parameters:
      e_range: inclusive range for the count of 'e'
      o_range: inclusive range for the count of 'o'
      max_len: maximum allowed characters for the word (including 'm' and 'w')
      capitalize: if True, capitalize the first letter (useful for sentence starts)
      meow_bias: probability to return exactly 'meow'

    Returns:
      A string like 'meow', 'meeeow', 'meeooow', etc.
    """
    # Prefer plain "meow" per bias if it fits the length cap (it does, length=4)
    r = _rng.random()
    if r < meow_bias:
        out = "meow"
    else:
        # Occasionally emit "mew" (no 'o' run), respecting max_len and e_range
        if _rng.random() < _DEFAULT_MEW_PROB:
            cap_e = max(1, min(e_range[1], max_len - 2))
            lo_e = max(1, e_range[0])
            hi_e = max(lo_e, cap_e)
            e = _rng.randint(lo_e, hi_e)
            out = "m" + ("e" * e) + "w"
        else:
            e, o = _sample_lengths(e_range, o_range, max_len)
            out = "m" + ("e" * e) + ("o" * o) + "w"

    if capitalize:
        out = out.capitalize()
    return out


def words(n: int = 1, as_list: bool = False, sep: str = " ") -> Union[str, List[str]]:
    """
    Generate n meow-words. By default returns a single space-joined string.

    Parameters:
      n: number of words to generate
      as_list: return a list if True, else a joined string
      sep: separator used when joining into a string
    """
    ws = [word() for _ in range(max(0, n))]
    return ws if as_list else sep.join(ws)


def _apply_inner_punct_and_brackets(
    tokens: List[str],
    comma_prob: float = _DEFAULT_COMMA_PROB,
    excl_prob: float = _DEFAULT_INNER_EXCLAM_PROB,
    quest_prob: float = _DEFAULT_INNER_QUEST_PROB,
    ellipsis_prob: float = _DEFAULT_INNER_ELLIPSIS_PROB,
    open_bracket_prob: float = _DEFAULT_BRACKET_OPEN_PROB,
    bracket_close_max_span: int = _DEFAULT_BRACKET_CLOSE_MAX_SPAN,
) -> List[str]:
    """
    Insert mid-sentence punctuation and optionally a single pair of parentheses.

    Rules:
      - Mid-sentence punctuation may include ',', '!', '?', '...'.
      - Do not apply mid punctuation to the first or last token.
      - At most one parentheses pair per phrase:
        '(' opens at a mid position with a small probability,
        ')' closes within 1..bracket_close_max_span tokens after opening.
    """
    n = len(tokens)
    if n < 3:
        return tokens

    last_idx = n - 1

    # Decide on a parentheses span (at most one)
    open_idx: int | None = None
    close_idx: int | None = None
    if n >= 4 and _rng.random() < open_bracket_prob:
        # Open cannot be the first or the last-2 (need room to close before end)
        max_open = max(1, last_idx - 2)
        if max_open >= 1:
            oi = _rng.randint(1, max_open)
            max_span = min(bracket_close_max_span, last_idx - oi)  # allow closing up to the last token
            if max_span >= 1:
                ci = oi + _rng.randint(1, max_span)
                open_idx, close_idx = oi, ci

    # Build output with optional punctuation and parentheses
    out: List[str] = []
    p_sum = comma_prob + excl_prob + quest_prob + ellipsis_prob

    for i, raw in enumerate(tokens):
        t = raw

        # Opening parenthesis before token (prefix)
        if open_idx is not None and i == open_idx:
            t = "(" + t

        # Mid-sentence punctuation (exclude first and last token)
        if 0 < i < last_idx and p_sum > 0:
            r = _rng.random()
            if r < p_sum:
                if r < comma_prob:
                    t = t + ","
                elif r < comma_prob + excl_prob:
                    t = t + "!"
                elif r < comma_prob + excl_prob + quest_prob:
                    t = t + "?"
                else:
                    t = t + "..."

        # Closing parenthesis after token (suffix)
        if close_idx is not None and i == close_idx:
            t = t + ")"

        out.append(t)

    return out


def phrase(
    words_count: int,
    punctuation: bool = True,
) -> str:
    """
    Generate exactly 'words_count' meow-words as a single phrase (sentence-like).

    Behavior:
      - First word capitalized.
      - Optionally inserts commas at low probability.
      - Ends with punctuation chosen from [., !, ?, ...] with default weights.
      - Occasionally wraps the whole phrase in quotes (\"...\" or '...').

    Parameters:
      words_count: exact number of words in the phrase
      punctuation: if True, enable commas, terminal punctuation, and quotes
    """
    n = max(0, int(words_count))
    if n == 0:
        return ""

    tokens = [word() for _ in range(n)]
    tokens[0] = tokens[0].capitalize()

    if punctuation:
        tokens = _apply_inner_punct_and_brackets(tokens)

    core = " ".join(tokens)

    end = ""
    if punctuation:
        end = _weighted_choice(_DEFAULT_END_PUNCT_WEIGHTS)

    text = f"{core}{end}"

    if punctuation and _rng.random() < _DEFAULT_QUOTE_PROB:
        quote = '"' if _rng.random() < 0.5 else "'"
        text = f"{quote}{text}{quote}"

    return text


def phrases(
    n: int,
    words_count: int,
    as_list: bool = False,
    punctuation: bool = True,
) -> Union[str, List[str]]:
    """
    Generate 'n' phrases, each containing exactly 'words_count' words.

    Parameters:
      n: number of phrases
      words_count: words per phrase
      as_list: return list if True, else return a single string with phrases separated by newline
      punctuation: enable/disable punctuation features

    Returns:
      Either a list[str] of phrases or a single string with each phrase on its own line.
    """
    items = [phrase(words_count=words_count, punctuation=punctuation) for _ in range(max(0, n))]
    return items if as_list else "\n".join(items)


# Synonyms for users who expect lorem-ipsum-like naming
def sentence(
    words: Union[int, None] = None,
    word_range: Tuple[int, int] = (4, 12),
    punctuation: bool = True,
) -> str:
    """
    Generate one sentence-like phrase.

    If 'words' is provided, uses that exact count. Otherwise samples uniformly in word_range.
    """
    if words is None:
        w = _rng.randint(word_range[0], word_range[1])
    else:
        w = int(words)
    return phrase(words_count=w, punctuation=punctuation)


def sentences(
    n: int = 1,
    words: Union[int, None] = None,
    word_range: Tuple[int, int] = (4, 12),
    as_list: bool = False,
    punctuation: bool = True,
) -> Union[str, List[str]]:
    """
    Generate multiple sentences.

    If 'words' is provided, uses that exact count for each sentence. Otherwise each sentence
    samples its length uniformly in word_range.
    """
    results: List[str] = []
    for _ in range(max(0, n)):
        if words is None:
            w = _rng.randint(word_range[0], word_range[1])
        else:
            w = int(words)
        results.append(phrase(words_count=w, punctuation=punctuation))
    return results if as_list else " ".join(results)


def paragraph(sentence_range: Tuple[int, int] = (3, 7)) -> str:
    """
    Generate a paragraph by sampling a number of sentences in sentence_range.
    """
    n = _rng.randint(sentence_range[0], sentence_range[1])
    # Join sentences with a space to mimic natural paragraphs.
    return sentences(n=n)


def paragraphs(
    n: int = 1,
    sentence_range: Tuple[int, int] = (3, 7),
    as_list: bool = False,
) -> Union[str, List[str]]:
    """
    Generate multiple paragraphs.
    """
    items = [paragraph(sentence_range=sentence_range) for _ in range(max(0, n))]
    return items if as_list else "\n\n".join(items)


def text(
    paragraphs_count: int = 3,
    sentence_range: Tuple[int, int] = (3, 7),
    html: bool = False,
) -> str:
    """
    Generate multi-paragraph meow ipsum text.

    Parameters:
      paragraphs_count: number of paragraphs
      sentence_range: number of sentences per paragraph (inclusive)
      html: if True, wrap each paragraph in <p>...</p>
    """
    paras = paragraphs(n=paragraphs_count, sentence_range=sentence_range, as_list=True)  # type: ignore
    if html:
        return "\n".join(f"<p>{p}</p>" for p in paras)
    return "\n\n".join(paras)

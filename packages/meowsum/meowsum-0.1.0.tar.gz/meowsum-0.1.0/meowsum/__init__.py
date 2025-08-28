"""
Meowsum: cat-sound lorem ipsum generator.

Public API mirrors common lorem ipsum ergonomics, with constraints:
- Word shape: m + e* + o* + w
- Each word length <= 10
- Plain "meow" appears more often than variants
- Phrases/sentences can include punctuation: ., ..., !, ?, , and quotes sometimes
"""

from .meow import (
    seed,
    word,
    words,
    phrase,
    phrases,
    sentence,
    sentences,
    paragraph,
    paragraphs,
    text,
)

# Re-export submodule to support: from meowsum import meow
from . import meow as meow

__all__ = [
    "seed",
    "word",
    "words",
    "phrase",
    "phrases",
    "sentence",
    "sentences",
    "paragraph",
    "paragraphs",
    "text",
    "meow",
]

__version__ = "0.1.0"

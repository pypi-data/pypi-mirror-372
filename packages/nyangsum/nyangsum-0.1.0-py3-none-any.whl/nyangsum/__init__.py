"""
Nyangsum: Korean cat-sound lorem ipsum generator.

Public API mirrors common lorem ipsum ergonomics, adapted to Hangul tokens:
- Core tokens favored: "냥", "냐옹", "나앙" (elongated variants like "냐아앙")
- Phrase/sentence punctuation similar to reference: ., ..., !, ?, commas, optional quotes
"""

from .nyang import (
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

# Re-export submodule to support: from nyangsum import nyang
from . import nyang as nyang

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
    "nyang",
]

__version__ = "0.1.0"

from __future__ import annotations

import random
from typing import Dict, Iterable, List, Sequence, Tuple, Union

# Module-level RNG with optional seeding via seed()
_rng = random.Random()

# Distribution defaults (favor base tokens: 냥, 냐옹, 나앙)
_DEFAULT_BASE_WEIGHTS: Sequence[Tuple[str, float]] = (
    ("냥", 0.45),
    ("냐옹", 0.30),
    ("나앙", 0.15),  # 요청에 '나앙' 명시됨(일반적으로 '냐앙'도 쓰이나, 우선 명시대로)
)
_DEFAULT_ELONGATED_WEIGHT = 0.10  # 늘임형 총 비중

# Elongation (for '냐' + '아'*k + ('앙'|'옹'))
_DEFAULT_ELONG_MIN_A = 1
_DEFAULT_ELONG_MAX_A = 4
_DEFAULT_TAIL_WEIGHTS: Sequence[Tuple[str, float]] = (("앙", 0.6), ("옹", 0.4))

# Punctuation probabilities and weights (borrowed style from reference)
_DEFAULT_END_PUNCT_WEIGHTS: Sequence[Tuple[str, float]] = (
    (".", 0.7),
    ("!", 0.15),
    ("?", 0.1),
    ("...", 0.05),
)
_DEFAULT_QUOTE_PROB = 0.03  # chance to wrap a phrase in quotes
_DEFAULT_COMMA_PROB = 0.045  # per-gap probability to insert a comma (no space before, space after)

# Inner punctuation probabilities (mid-sentence)
_DEFAULT_INNER_EXCLAM_PROB = 0.005
_DEFAULT_INNER_QUEST_PROB = 0.005
_DEFAULT_INNER_ELLIPSIS_PROB = 0.0075

# Parentheses behavior
_DEFAULT_BRACKET_OPEN_PROB = 0.02
_DEFAULT_BRACKET_CLOSE_MAX_SPAN = 10


def seed(value: Union[int, None]) -> None:
    """
    Seed the internal random generator for reproducible output.
    """
    _rng.seed(value)


def _weighted_choice(choices_with_weights: Sequence[Tuple[str, float]]) -> str:
    total = sum(w for _, w in choices_with_weights)
    if total <= 0:
        # Fallback: return first key if weights invalid
        return choices_with_weights[0][0]
    r = _rng.random() * total
    upto = 0.0
    for choice, w in choices_with_weights:
        upto += w
        if r <= upto:
            return choice
    return choices_with_weights[-1][0]


def _pick_token_category(
    weights: Union[Dict[str, float], None]
) -> str:
    """
    Decide which token to emit:
      - One of the base tokens: '냥', '냐옹', '나앙'
      - Or ELONGATED category: '__ELONG__'
    'weights' can override base/elongated weights, e.g.:
      {'냥':0.5, '냐옹':0.3, '나앙':0.15, 'elongated':0.05}
    """
    if weights is None:
        base = list(_DEFAULT_BASE_WEIGHTS)
        elongated = _DEFAULT_ELONGATED_WEIGHT
    else:
        base = []
        for tok, default_w in _DEFAULT_BASE_WEIGHTS:
            base.append((tok, float(weights.get(tok, default_w))))
        elongated = float(weights.get("elongated", _DEFAULT_ELONGATED_WEIGHT))

    choices: List[Tuple[str, float]] = list(base) + [("__ELONG__", elongated)]
    return _weighted_choice(choices)


def _generate_elongated(
    max_len: int,
    min_a: int = _DEFAULT_ELONG_MIN_A,
    max_a: int = _DEFAULT_ELONG_MAX_A,
    tail_weights: Sequence[Tuple[str, float]] = _DEFAULT_TAIL_WEIGHTS,
) -> str:
    """
    Create an elongated token of the shape:
        '냐' + '아' * k + tail
    where tail in {'앙','옹'} by weights, and ensure total syllable length <= max_len.

    Syllable count here equals Python len() for Hangul syllables.
    Length formula: 1(냐) + k(아...) + 1(tail) = k + 2
    """
    if max_len < 2:
        # Not enough room for elongated shape; fallback to a base short form
        return "냥"

    cap_k = max(0, min(max_a, max_len - 2))
    lo_k = max(1, min_a)
    if cap_k < 1:
        # Can't place any '아' within cap -> fallback
        return "냐옹"

    if lo_k > cap_k:
        # Swap to keep consistent bounds
        lo_k, cap_k = cap_k, lo_k

    k = _rng.randint(lo_k, cap_k)
    tail = _weighted_choice(tail_weights)
    return "냐" + ("아" * k) + tail


def word(
    max_len: int = 6,
    capitalize: bool = False,
    weights: Union[Dict[str, float], None] = None,
    elong_min_a: int = _DEFAULT_ELONG_MIN_A,
    elong_max_a: int = _DEFAULT_ELONG_MAX_A,
    tail_weights: Sequence[Tuple[str, float]] = _DEFAULT_TAIL_WEIGHTS,
) -> str:
    """
    Generate a single Korean cat-sound word.

    Categories:
      - Base tokens (favored): '냥', '냐옹', '나앙'
      - Elongated: '냐' + '아'*k + ('앙' | '옹'), with k in [elong_min_a, elong_max_a]

    Parameters:
      max_len: maximum allowed characters (Hangul syllables) for a word (default 6)
      capitalize: kept for API symmetry; no effect for Hangul
      weights: optional override dict for base/elongated weights:
               {'냥':float, '냐옹':float, '나앙':float, 'elongated':float}
      elong_min_a / elong_max_a: range for '아' run-length in elongated tokens
      tail_weights: weights for choosing '앙' vs '옹' in elongated tokens

    Returns:
      One token like '냥', '냐옹', '나앙', '냐아앙', '냐아옹', ...
    """
    category = _pick_token_category(weights)

    if category == "__ELONG__":
        out = _generate_elongated(
            max_len=max_len,
            min_a=elong_min_a,
            max_a=elong_max_a,
            tail_weights=tail_weights,
        )
    else:
        # Base token can be returned as-is if it doesn't exceed max_len
        if len(category) <= max_len:
            out = category
        else:
            # Fallback to a short base if an override made it longer than cap (unlikely)
            out = "냥"

    if capitalize:
        out = out.capitalize()
    return out


def words(n: int = 1, as_list: bool = False, sep: str = " ") -> Union[str, List[str]]:
    """
    Generate n words. By default returns a single space-joined string.
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
        max_open = max(1, last_idx - 2)
        if max_open >= 1:
            oi = _rng.randint(1, max_open)
            max_span = min(bracket_close_max_span, last_idx - oi)
            if max_span >= 1:
                ci = oi + _rng.randint(1, max_span)
                open_idx, close_idx = oi, ci

    # Build output with optional punctuation and parentheses
    out: List[str] = []
    p_sum = max(0.0, comma_prob) + max(0.0, excl_prob) + max(0.0, quest_prob) + max(0.0, ellipsis_prob)

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
    Generate exactly 'words_count' nyang-words as a single phrase.

    Behavior:
      - First token capitalize() for symmetry (no visual effect in Hangul).
      - Optionally inserts commas at low probability.
      - Ends with punctuation chosen from [., !, ?, ...] with default weights.
      - Occasionally wraps the whole phrase in quotes (\"...\" or '...').
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

    text_out = f"{core}{end}"

    if punctuation and _rng.random() < _DEFAULT_QUOTE_PROB:
        quote = '"' if _rng.random() < 0.5 else "'"
        text_out = f"{quote}{text_out}{quote}"

    return text_out


def phrases(
    n: int,
    words_count: int,
    as_list: bool = False,
    punctuation: bool = True,
) -> Union[str, List[str]]:
    """
    Generate 'n' phrases, each containing exactly 'words_count' words.
    """
    items = [phrase(words_count=words_count, punctuation=punctuation) for _ in range(max(0, n))]
    return items if as_list else "\n".join(items)


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
    Generate multi-paragraph nyang ipsum text.

    Parameters:
      paragraphs_count: number of paragraphs
      sentence_range: number of sentences per paragraph (inclusive)
      html: if True, wrap each paragraph in <p>...</p>
    """
    paras = paragraphs(n=paragraphs_count, sentence_range=sentence_range, as_list=True)  # type: ignore
    if html:
        return "\n".join(f"<p>{p}</p>" for p in paras)
    return "\n\n".join(paras)

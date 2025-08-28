# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Callable, Literal
import math
import re
import collections
from array import array


_WORD = re.compile(r"\w+", re.UNICODE)
SimilarityMethod = Literal["cosine", "jaccard", "levenshtein"]


def _ngrams(text: str, n: int) -> list[str]:
    tokens = _WORD.findall(text.lower())
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _tf_vector(text: str) -> Dict[str, int]:
    grams = _ngrams(text, 1) + _ngrams(text, 2)
    return collections.Counter(grams)


def _cosine(a: str, b: str) -> float:
    va, vb = _tf_vector(a), _tf_vector(b)
    small, big = (va, vb) if len(va) < len(vb) else (vb, va)
    dot = sum(freq * big.get(tok, 0) for tok, freq in small.items())
    na = math.sqrt(sum(f * f for f in va.values()))
    nb = math.sqrt(sum(f * f for f in vb.values()))
    return dot / (na * nb) if na and nb else 0.0


def _jaccard(a: str, b: str) -> float:
    sa, sb = set(_WORD.findall(a.lower())), set(_WORD.findall(b.lower()))
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0


def _lev_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    v0 = array("I", range(len(b) + 1))
    v1 = array("I", [0]) * (len(b) + 1)

    for i, ca in enumerate(a, 1):
        v1[0] = i
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            v1[j] = min(
                v1[j - 1] + 1,   # insertion
                v0[j] + 1,       # deletion
                v0[j - 1] + cost # substitution
            )
        v0, v1 = v1, v0
    return v0[-1]


def _levenshtein(a: str, b: str) -> float:
    d = _lev_distance(a, b)
    max_len = max(len(a), len(b))
    return 1.0 - d / max_len if max_len else 1.0



_FUNC_MAP: dict[str, Callable[[str, str], float]] = {
    "cosine": _cosine,
    "jaccard": _jaccard,
    "levenshtein": _levenshtein,
}

@dataclass(slots=True)
class TextSimilarity:
    """
    Callable similarity object.

    Example
    -------
    >>> sim = TextSimilarity("jaccard")
    >>> sim("the cat", "a cat")
    0.5
    """

    method: str = "cosine"   

    def __post_init__(self) -> None:
        if self.method not in _FUNC_MAP:
            raise ValueError(
                f"Unsupported similarity method: {self.method!r}. "
                f"Choose from {', '.join(_FUNC_MAP)}."
            )

    def __call__(self, a: str, b: str) -> float:  # pragma: no cover
        return _FUNC_MAP[self.method](a, b)
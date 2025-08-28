# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from statistics import mean
from typing import Any, Dict, Tuple,Callable


_LOG2: Callable[[float], float] = math.log2
_LOG10: Callable[[float], float] = math.log10


def _shannon_entropy(freqs: Counter[str], total: int) -> float:
    """Shannon entropy in bits per token."""
    return -sum((count / total) * _LOG2(count / total) for count in freqs.values())


def _zipf_slope_r2(freqs: Counter[str]) -> Tuple[float, float]:
    """
    Closed-form linear regression on log₁₀(rank) → log₁₀(freq).

    Returns
    -------
    (slope, R²), both rounded to 3 decimals.
    """
    n_types = len(freqs)
    if n_types < 2:
        return float("nan"), float("nan")

    sorted_freqs = sorted(freqs.values(), reverse=True)
    log_ranks = [_LOG10(i) for i in range(1, n_types + 1)]
    log_freqs = [_LOG10(f) for f in sorted_freqs]

    x_bar = mean(log_ranks)
    y_bar = mean(log_freqs)

    ss_xy = sum((x - x_bar) * (y - y_bar) for x, y in zip(log_ranks, log_freqs))
    ss_xx = sum((x - x_bar) ** 2 for x in log_ranks)
    slope = ss_xy / ss_xx if ss_xx else float("nan")

    ss_tot = sum((y - y_bar) ** 2 for y in log_freqs)
    ss_res = sum(
        (y - (slope * x + y_bar - slope * x_bar)) ** 2
        for x, y in zip(log_ranks, log_freqs)
    )
    r2 = 1 - ss_res / ss_tot if ss_tot else float("nan")

    return round(slope, 3), round(r2, 3)


def _gini(freqs: Counter[str], total: int) -> float:
    """Gini coefficient of the type–frequency distribution (0=uniform, 1=max inequality)."""
    n = len(freqs)
    if n == 0:
        return 0.0

    sorted_vals = sorted(freqs.values())
    cum = sum(i * v for i, v in enumerate(sorted_vals, start=1))
    gini = (2 * cum) / (n * total) - (n + 1) / n
    return round(gini, 3)


def _simpson_index(freqs: Counter[str], total: int) -> float:
    """
    Simpson’s Diversity Index:
    D = 1 - ∑ (f_w / N)²
    where f_w is the frequency of type w, N is total tokens.
    """
    if total == 0:
        return 0.0
    sum_sq = sum((count / total) ** 2 for count in freqs.values())
    return round(1 - sum_sq, 3)


def _yules_k(freqs: Counter[str], total: int) -> float:
    """
    Yule’s K:
    K = 10^4 * (∑_{i=1}^m i² V_i - N) / N²
    where V_i = number of types with frequency i, N = total tokens.
    """
    if total == 0:
        return 0.0
    freq_of_freq: Counter[int] = Counter(freqs.values())
    sum_i2_vi = sum(i * i * vi for i, vi in freq_of_freq.items())
    k = 1e4 * (sum_i2_vi - total) / (total * total)
    return round(k, 3)


def _avg_word_length(freqs: Counter[str], total: int) -> float:
    """Average word length (in characters), weighted by frequency."""
    if total == 0:
        return 0.0
    total_chars = sum(len(word) * count for word, count in freqs.items())
    return round(total_chars / total, 3)


# --------------------------------------------------------------------------- #
# Standalone StatisticalAnalyzer                                              #
# --------------------------------------------------------------------------- #
@dataclass(slots=True)
class StatisticalAnalyzer:
    """
    Computes a suite of statistical metrics on the distribution of lower-cased tokens.

    Implemented metrics
    -------------------
    * entropy           : Shannon entropy (bits per token)
    * zipf              : {'slope': float, 'r2': float} of log₁₀(rank) → log₁₀(freq)
    * vocab_gini        : Gini coefficient of type–frequency distribution
    * type_token_ratio  : |V| / N, where |V| is number of unique types, N is total tokens
    * hapax_ratio       : fraction of types that occur exactly once
    * simpson_index     : Simpson’s diversity index = 1 - ∑ (f_w / N)²
    * yule_k            : Yule’s K for lexical concentration
    * avg_word_length   : average length of tokens (characters), weighted by frequency

    """


    def __call__(self, text: str) -> Dict[str, Any]:
        return self.run(text)

    @staticmethod
    def run(text: str) -> Dict[str, Any]:
        tokens = text.lower().split()
        total = len(tokens)

        if total == 0:
            return {
                "entropy": 0.0,
                "zipf": {"slope": float("nan"), "r2": float("nan")},
                "vocab_gini": 0.0,
                "type_token_ratio": 0.0,
                "hapax_ratio": 0.0,
                "simpson_index": 0.0,
                "yule_k": 0.0,
                "avg_word_length": 0.0,
            }

        freqs = Counter(tokens)

        entropy = round(_shannon_entropy(freqs, total), 3)
        slope, r2 = _zipf_slope_r2(freqs)
        vocab_gini = _gini(freqs, total)

        type_token_ratio = round(len(freqs) / total, 3)
        hapaxes = sum(1 for c in freqs.values() if c == 1)
        hapax_ratio = round(hapaxes / total, 3)

        simpson_index = _simpson_index(freqs, total)
        yule_k = _yules_k(freqs, total)
        avg_word_length = _avg_word_length(freqs, total)

        return {
            "entropy": entropy,
            "zipf": {"slope": slope, "r2": r2},
            "vocab_gini": vocab_gini,
            "type_token_ratio": type_token_ratio,
            "hapax_ratio": hapax_ratio,
            "simpson_index": simpson_index,
            "yule_k": yule_k,
            "avg_word_length": avg_word_length,
        }

    def __repr__(self) -> str:
        return "<StatisticalAnalyzer>"

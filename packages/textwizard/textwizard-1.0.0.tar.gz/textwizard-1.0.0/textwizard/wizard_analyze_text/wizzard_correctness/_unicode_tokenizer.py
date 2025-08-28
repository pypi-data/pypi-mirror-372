# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations

from pathlib import Path
from functools import lru_cache
from typing import Optional, List
import unicodedata as _u
import regex as rx

try:
    import jieba  # type: ignore
    _HAS_JIEBA = True
except Exception:
    _HAS_JIEBA = False

# Numbers (for correctness/display only)
NUM_RE = rx.compile(
    r"^[\p{Nd}]+(?:[,\.\u202F\u2009\u00A0\u066B\u066C'][\p{Nd}]+)*"
    r"(?:\u2013[\p{Nd}]+(?:[,\.\u202F\u2009\u00A0\u066B\u066C'][\p{Nd}]+)*)?$"
)

# Apostrophes; leave middle dot separate (Catalan uses U+00B7)
APOS_CHARS = ("'", "’", "ʼ", "\u02BC", "\u2019")
MIDDLE_DOT = "\u00B7"
_APOS_TBL  = {ord(a): "'" for a in APOS_CHARS}

EDGE_TRIM_RE = rx.compile(r"^[^\p{L}\p{N}\p{M}\p{Cf}]+|[^\p{L}\p{N}\p{M}\p{Cf}]+$")

URL_RE   = rx.compile(r"https?://\S+")
EMAIL_RE = rx.compile(r"[\p{L}\p{N}\p{M}\p{Pc}\p{Pd}\.'\+\p{Cf}]+@[\p{L}\p{N}\p{M}\p{Pc}\p{Pd}\.-]+\.[\p{L}]{2,}")
HASH_RE  = rx.compile(r"[#@][\p{L}\p{N}\p{M}_\p{Pd}]+")
ASCII_LET_RE = rx.compile(r"[A-Za-z]+")
EMOJI_RE = rx.compile(r"\p{Extended_Pictographic}")
EMOJI_ZWJ_SEQ_RE = rx.compile(r"(?:\p{Extended_Pictographic}\uFE0F?(?:\u200D\p{Extended_Pictographic}\uFE0F?)*)")

# Japanese
JA_RUN_RE = rx.compile(r"[\p{Han}\p{Hiragana}\p{Katakana}ー々ゝゞ]+")  # run massima CJK-ja
HALF_KATA_RUN_RE  = rx.compile(r"[\uFF66-\uFF9D\uFF9E\uFF9F\uFF70]+")
FW_LATIN_RUN_RE   = rx.compile(r"[\uFF10-\uFF19\uFF21-\uFF3A\uFF41-\uFF5A]+")

# Strong path pattern reused by correctness.py
PATH_RE = rx.compile(r"(?:[A-Za-z]:)?(?:/|\\)[^\s]+")

# Joiners inside tokens (ISO-like) + middle dot
_JOINERS = set('._:-_‐-‒–—―−' + "\u05BE\u05F3\u05F4" + MIDDLE_DOT)


def _longest_prefix(trie, s: str) -> Optional[str]:
    best = None
    for w in trie.iter_prefixes(s):
        if best is None or len(w) > len(best):
            best = w
    return best

def _is_apostrophe(ch: str) -> bool:
    return ch in APOS_CHARS


UNICODE_QUOTES = {'"', '\u201C', '\u201D', '\u201E', '\u00AB', '\u00BB'}
def _is_quote(ch: str) -> bool:
    return ch in UNICODE_QUOTES


def _lang_base(lang: str) -> str:
    b = (lang or "").split("_", 1)[0]
    b = b.split("-", 1)[0]
    b = b.split(".", 1)[0]
    return b.casefold()


def normalize_text(text: str) -> str:
    """Remove soft hyphen; canonicalize typographic apostrophes to ASCII '."""
    return text.replace("\u00AD", "").translate(_APOS_TBL)


def _is_skip_space(ch: str) -> bool:
    if ch in ("\u00A0", "\u202F", "\u2009"):
        return False
    return ch.isspace()


@lru_cache(maxsize=1)
def _get_ja_trie(dict_dir_str: Optional[str]):
    from textwizard.wizard_analyze_text.wizzard_correctness.loader_dict import load_trie
    return load_trie(
        "ja",
        path_dict=Path(dict_dir_str) if dict_dir_str else None,
        auto_download=(dict_dir_str is None),
        ask_download=False,
        use_mmap=False,
    )


def _is_core(ch: str) -> bool:
    cat = _u.category(ch)
    return (cat[0] in ("L", "M", "N")) or (cat == "Cf")


def _is_joiner(ch: str) -> bool:
    return ch in _JOINERS


def tokenize_words(
    text: str,
    lang: str,
    dict_dir: Optional[Path] = None,
) -> List[str]:
    """
    Unicode tokenizer.
    Non-CJK: aggregate core with single joiners; split runs of apostrophes/quotes ≥ 2.
    CJK: jieba for zh, trie-driven segmentation for ja.
    """
    t = normalize_text(text)
    base = _lang_base(lang)

    # Chinese
    if base == "zh":
        if not _HAS_JIEBA:
            raise RuntimeError("jieba not installed – `pip install jieba`")
        return [tok for tok in jieba.cut(t, HMM=True) if tok]  # type: ignore

    # Japanese
    if base == "ja":
        trie = _get_ja_trie(str(dict_dir.resolve()) if dict_dir else None)
        out: List[str] = []
        i, n = 0, len(t)
        while i < n:
            # blocchi speciali
            m = EMOJI_ZWJ_SEQ_RE.match(t, i)
            if m: out.append(m.group()); i = m.end(); continue
            for R in (URL_RE, EMAIL_RE, HASH_RE, PATH_RE):
                m = R.match(t, i)
                if m: out.append(m.group()); i = m.end(); break
            else:
                ch = t[i]
                if _is_skip_space(ch): i += 1; continue
                if ch in ("\uFE0F", "\u200D"): i += 1; continue
                if EMOJI_RE.search(ch): out.append(ch); i += 1; continue

                # half-width katakana
                m = HALF_KATA_RUN_RE.match(t, i)
                if m: out.append(m.group()); i = m.end(); continue

                # fullwidth latin
                m = FW_LATIN_RUN_RE.match(t, i)
                if m: out.append(m.group()); i = m.end(); continue

                # giapponese: prova longest-prefix dal dizionario
                if JA_RUN_RE.match(ch):
                    s = t[i:]
                    w = _longest_prefix(trie, s)
                    if w:
                        out.append(w);
                        i += len(w);
                        continue
                    # nessun prefisso: prendi la run massima CJK-ja
                    m = JA_RUN_RE.match(s)
                    out.append(m.group());
                    i += m.end();
                    continue

                # ASCII letters contigue
                m = ASCII_LET_RE.match(t, i)
                if m: out.append(m.group()); i = m.end(); continue

                # fallback: singolo char visibile
                if _u.category(ch)[0] != "C":
                    out.append(ch)
                i += 1

        return [tok for tok in out if tok]

    # -------- Non-CJK --------
    out: List[str] = []
    i, n = 0, len(t)

    while i < n:
        ch = t[i]
        if _is_skip_space(ch):
            i += 1
            continue

        # ZWJ emoji sequence
        m_zwj = EMOJI_ZWJ_SEQ_RE.match(t, i)
        if m_zwj:
            out.append(m_zwj.group()); i = m_zwj.end(); continue

        # Special blocks
        for R in (URL_RE, EMAIL_RE, HASH_RE, PATH_RE):
            m = R.match(t, i)
            if m:
                out.append(m.group()); i = m.end(); break
        else:
            if ch in ("\uFE0F", "\u200D"):
                i += 1; continue

            if _is_core(ch):
                j = i + 1
                while j < n:
                    cj = t[j]
                    if _is_core(cj):
                        j += 1; continue

                    # Apostrophe: a single ' joins if followed by core; runs of 2+ split
                    if cj in APOS_CHARS:
                        k2 = j
                        while k2 < n and t[k2] in APOS_CHARS:
                            k2 += 1
                        if (k2 - j) >= 2:
                            break
                        if k2 < n and _is_core(t[k2]):
                            j = k2 + 1; continue
                        break

                    # Quote: a single " can join between cores; runs of 2+ split
                    if _is_quote(cj):
                        k2 = j
                        while k2 < n and _is_quote(t[k2]):
                            k2 += 1
                        if (k2 - j) >= 2:
                            break
                        if (i < j) and _is_core(t[j - 1]) and (k2 < n and _is_core(t[k2])):
                            j = k2 + 1;
                            continue
                        break

                    # Other joiners (includes U+00B7)
                    if _is_joiner(cj):
                        k2 = j
                        while k2 < n and _is_joiner(t[k2]):
                            k2 += 1
                        if k2 < n and _is_core(t[k2]):
                            j = k2 + 1; continue
                        break

                    break

                out.append(t[i:j]); i = j; continue

            m_ascii = ASCII_LET_RE.match(t, i)
            if m_ascii:
                out.append(m_ascii.group()); i = m_ascii.end(); continue

            if EMOJI_RE.match(ch):
                out.append(ch); i += 1; continue

            if _u.category(ch)[0] != "C":
                out.append(ch)
            i += 1

    return out
# abano
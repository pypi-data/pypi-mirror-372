# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations

import unicodedata as _u
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, List, Optional, Union, Dict

import marisa_trie
import regex as _re
import zstandard as zstd

from textwizard.wizard_analyze_text.wizzard_correctness.loader_dict import load_trie
from textwizard.wizard_analyze_text.wizzard_correctness._unicode_tokenizer import (
    tokenize_words,
    normalize_text,
    NUM_RE as _NUM_RE,
    EDGE_TRIM_RE as _EDGE_TRIM_RE,
    PATH_RE as _PATH_RE,
    URL_RE as _URL_RE,
    EMAIL_RE as _EMAIL_RE,
    EMOJI_RE as _EMOJI_RE,
    EMOJI_ZWJ_SEQ_RE as _EMOJI_ZWJ_SEQ_RE,
    APOS_CHARS as _APOS,
)

# Time (HH:MM[:SS])
_TIME_RE      = _re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$")

# Explicit negative flags (must error)
_B64_FULL_RE  = _re.compile(r"^(?=.{12,}$)(?:[A-Za-z0-9+/]{4})+(?:==|=)?$")
_HEX_RE       = _re.compile(r"^0x[0-9A-Fa-f]{6,}$")
_UUID_RE      = _re.compile(r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$")
_FILE_EXT_RE  = _re.compile(r"^[A-Za-z0-9_+\-]+\.[A-Za-z0-9]{2,6}$")
_DOT_IDENT_RE = _re.compile(r"^[A-Za-z0-9]+(?:\.[A-Za-z0-9]+){2,}$")

# Surface canon (do not touch U+00B7)
_DASH_MAP = {
    ord("\u2010"): "-",
    ord("\u2011"): "-",
    ord("\u2012"): "-",
    ord("\u2013"): "-",
    ord("\u2014"): "-",
    ord("\u2212"): "-",
}
_APOS_SET = set(_APOS)
_APOS_MAP = {ord(a): "'" for a in _APOS}

__all__ = ["correctness_text", "CorrectnessAnalyzer"]

# ZW drop for lookup-tolerant comparisons
_ZW_DROP = {0x200C: None, 0x200D: None}


def _lookup_norm(s: str) -> str:
    return _dict_norm(s).translate(_ZW_DROP)


def _has_zw(s: str) -> bool:
    return ("\u200c" in s) or ("\u200d" in s)


def _is_punct_only(s: str) -> bool:
    return bool(s) and all(_u.category(ch).startswith("P") for ch in s)


def _is_marks_only(s: str) -> bool:
    return bool(s) and all(_u.category(ch) in ("Mn", "Me", "Cf") for ch in s)


def _dict_norm(s: str) -> str:
    """Dictionary-aligned normalization. Do not touch U+00B7. Do not strip U+2060 here."""
    s = _u.normalize("NFKC", s)
    s = _re.sub(r'(?:^/[^|]+\||/[^|]+\|)$', "", s)
    s = s.replace("\u200d", "\u200c")
    s = _re.sub(r"\u200c+", "\u200c", s)
    s = s.translate(_APOS_MAP)
    s = _re.sub(r"\u200b", "", s)  # drop ZWSP
    return s.casefold()


def _canon_surface(s: str) -> str:
    """Light surface canon before lookup (hyphens/apostrophes)."""
    return _u.normalize("NFC", s).translate(_DASH_MAP).translate(_APOS_MAP)


@dataclass(slots=True)
class CorrectnessAnalyzer:
    language: str
    _dict_dir: Optional[Union[str, Path]] = None
    _dict_path: Optional[Union[str, Path]] = None
    use_mmap: bool = False

    _tries: List[marisa_trie.Trie] = field(init=False, repr=False)
    _base: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._base = (self.language or "").split("_", 1)[0].split("-", 1)[0].split(".", 1)[0].casefold()
        src_dir = Path(self._dict_dir).expanduser().resolve() if self._dict_dir else None
        if self._dict_path is not None:
            self._tries = [self._load_trie_from_file(Path(self._dict_path))]
            return
        self._tries = [
            load_trie(
                self._base,
                path_dict=src_dir,
                auto_download=(src_dir is None),
                ask_download=False,
                use_mmap=self.use_mmap,
            )
        ]

    @staticmethod
    def _load_trie_from_file(path: Path) -> marisa_trie.Trie:
        trie = marisa_trie.Trie()
        if path.suffix == ".marisa":
            trie.mmap(str(path)); return trie
        if path.suffix == ".zst":
            raw = zstd.ZstdDecompressor().decompress(path.read_bytes())
            trie.frombytes(raw); return trie
        raise ValueError(f"Unsupported format: {path.suffix}")

    # ---------------- Block-by-block pipeline ----------------

    def run(self, text: str) -> Dict[str, Any]:
        """
        For each whitespace-separated block:
          1) specials (URL, email, path, numbers, time, emoji, #, @, etc.)
          2) whole-block dictionary check
          3) fallback: tokenize and validate token-by-token
        """
        errors: List[str] = []
        for blk in normalize_text(text).split():
            if self._block_is_special_ok(blk):
                continue
            if self._whole_block_in_dict(blk):
                continue
            toks = list(self._tokenize(blk))
            if not toks:
                base = _EDGE_TRIM_RE.sub("", blk) or blk
                if base:
                    errors.append(base)
                continue
            errors.extend(self._scan_tokens(toks))
        return {"errors_count": len(errors), "errors": errors}

    # ---------------- Helpers ----------------

    def _in_dict_candidates(self, candidates: Iterable[str]) -> bool:
        norm = {_dict_norm(v) for v in candidates if v}
        for trie in self._tries:
            for v in norm:
                if v in trie:
                    return True
        return False

    def _whole_block_in_dict(self, blk: str) -> bool:
        if not blk or "\u2060" in blk:
            return False
        base = _EDGE_TRIM_RE.sub("", blk) or blk
        vset = {blk, base, _canon_surface(blk), _canon_surface(base)}
        if self._in_dict_candidates(vset):
            return True
        if any(_has_zw(v) for v in vset):
            drop = {_lookup_norm(v) for v in vset if v}
            return self._in_dict_candidates(drop)
        return False

    def _block_is_special_ok(self, s: str) -> bool:
        # reject if WORD JOINER is present
        if "\u2060" in s:
            return False
        # mentions / hashtags
        if s.startswith("#") or s.startswith("@"):
            return True
        # URL / path / email
        if _PATH_RE.fullmatch(s) or _URL_RE.fullmatch(s) or _EMAIL_RE.fullmatch(s):
            return True
        # numbers / time
        if _NUM_RE.fullmatch(s) or _TIME_RE.fullmatch(s):
            return True
        # emoji or ZWJ emoji sequence
        if _EMOJI_ZWJ_SEQ_RE.fullmatch(s) or _EMOJI_RE.fullmatch(s):
            return True
        # pure FE0F/200D
        if s and all(ch in ("\uFE0F", "\u200D") for ch in s):
            return True
        # pure marks (Mn/Me/Cf)
        if s and all(_u.category(ch) in ("Mn", "Me", "Cf") for ch in s):
            return True
        return False

    def _scan_tokens(self, toks: List[str]) -> List[str]:
        errors: List[str] = []
        i, n = 0, len(toks)

        while i < n:
            tok = toks[i]
            if _is_punct_only(tok) or _is_marks_only(tok):
                i += 1
                continue

            # single trailer: accept only if exact form exists in dictionary
            if i + 1 < n and len(toks[i + 1]) == 1:
                tr = toks[i + 1]
                if tr in _APOS_SET or tr == ".":
                    if self._is_token_ok(tok, trailer=tr):
                        i += 2
                        continue

            if not self._is_token_ok(tok):
                base = _EDGE_TRIM_RE.sub("", tok) or tok
                if not _is_marks_only(base):
                    errors.append(base)
            i += 1

        return errors

    def _tokenize(self, text: str) -> Iterable[str]:
        src_dir = Path(self._dict_dir).expanduser().resolve() if self._dict_dir else None
        t = normalize_text(text)
        for tok in tokenize_words(t, self.language, src_dir):
            if not tok or tok.isspace():
                continue
            if all(ch in ("\uFE0F", "\u200D") for ch in tok):
                continue
            if _is_marks_only(tok):
                continue
            yield tok

    def _is_token_ok(self, tok: str, trailer: Optional[str] = None) -> bool:
        base = _EDGE_TRIM_RE.sub("", tok)
        if not base:
            return True

        # hard error if WORD JOINER inside word
        if "\u2060" in base:
            return False

        # mentions/hashtags
        if tok.startswith(("#", "@")):
            return True

        # URL / path / email
        if _PATH_RE.fullmatch(tok) or _PATH_RE.fullmatch(base):
            return True
        if _URL_RE.fullmatch(base) or _EMAIL_RE.fullmatch(base):
            return True

        # numbers / time
        if _NUM_RE.fullmatch(base) or _TIME_RE.fullmatch(base):
            return True

        # emoji
        if _EMOJI_RE.search(base) or _EMOJI_ZWJ_SEQ_RE.fullmatch(base):
            return True

        # dictionary with light canon
        vset = {tok, base, _canon_surface(tok), _canon_surface(base)}
        if self._in_dict_candidates(vset):
            return True

        # trailer-aware exact forms
        if trailer:
            if trailer in _APOS_SET:
                if self._in_dict_candidates({base + trailer}):
                    return True
            elif trailer == ".":
                if self._in_dict_candidates({base + "."}):
                    return True

        # ZW tolerant lookup
        if _has_zw(tok) or _has_zw(base):
            if self._in_dict_candidates({_lookup_norm(tok), _lookup_norm(base)}):
                return True

        # explicit negative flags
        if _B64_FULL_RE.fullmatch(base) or _HEX_RE.fullmatch(base) or _UUID_RE.fullmatch(base):
            return False
        if _FILE_EXT_RE.fullmatch(base) or _DOT_IDENT_RE.fullmatch(base):
            return False

        return False


def correctness_text(
    text: str,
    language: str = "en",
    *,
    dict_dir: Union[str, Path, None] = None,
    use_mmap: bool = False,
) -> Dict[str, Any]:
    analyzer = CorrectnessAnalyzer(language, _dict_dir=dict_dir, use_mmap=use_mmap)
    return analyzer.run(text)

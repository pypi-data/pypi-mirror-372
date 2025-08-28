# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations
"""
WildcardSearch
===============
A blazing‑fast wildcard matcher that supports **SQL–style** patterns plus a
few convenient extensions.

Supported wildcard symbols
--------------------------
Symbol | Meaning                                    | Regex translation
------ | ------------------------------------------ | -----------------
``*``  | 0 or more *of any* characters (greedy)     | ``.*?``
``%``  | 0 or more *of any* characters (greedy)
``_``  | exactly **1** character                    | ``.``
``?``  | **1 or more** characters *(lazy)*          | ``.+?``
``[abc]`` | character‑class / range (SQL/regex style) | kept as is (with   safe escaping of ``-`` & ``^``)


Anchoring rules
---------------
* **Start anchor** (``^``) is added automatically **unless** the pattern
  starts with ``*`` or ``%``.
* **End anchor** (``$``) is added automatically **unless** the pattern
  ends   with ``*`` or ``%``.

This mimics SQL behaviour where, e.g., ``'foo%'`` matches any string that
*starts* with ``foo``, while bare ``'foo'`` must match the *entire* value.

Features
--------
* Prefix / suffix / contains optimisations via **marisa‑trie** and
  **Aho‑Corasick** for thousands of patterns.
* Case‑insensitive search handled lazily (original casing preserved in
  results).
* Unified behaviour across all wildcard tokens — no hidden surprises.

Example
~~~~~~~
>>> ws = WildcardSearch()
>>> ws.search("apple application applet", ["appl?", "app*"])
['apple', 'application', 'applet']

"""
import re
from functools import lru_cache
from typing import Iterable, List, Set, Tuple

import ahocorasick as _ahoc          # type: ignore
import marisa_trie                   # type: ignore

try:
    import regex as _re              # se disponibile è più veloce
except ModuleNotFoundError:          # pragma: no cover
    _re = re


TOKEN_RE: re.Pattern[str] = re.compile(r"[^\s]+")
TAG_RX   : re.Pattern[str] = re.compile(r"</?\s*([A-Za-z][\w\-:]*)[^>]*>")
OR_THRESHOLD = 32                     # soglia OR-regex vs A-C

_WILDCARD_SYMS = set("*%?_[]")
_WC_CHARS = {"*", "?", "[", "%", "_"}
ATTR_RX = re.compile(r'\s+([A-Za-z_:][\w:.-]*)\s*=\s*')   # nome attr prima di =


def _is_literal(text: str) -> bool:
    return not any(ch in _WILDCARD_SYMS for ch in text)


def _extract_tokens(text: str) -> List[str]:
    tokens: list[str] = []

    for m in TAG_RX.finditer(text):
        full_tag  = m.group(0)         
        tag_name  = m.group(1)         
        tokens.append(full_tag)
        tokens.append(tag_name)

        for attr in ATTR_RX.findall(full_tag):
            tokens.append(attr)         

    clean = TAG_RX.sub(" ", text)
    tokens.extend(TOKEN_RE.findall(clean))

    return tokens


class _LazyAC:                              
    @staticmethod
    @lru_cache(maxsize=128)
    def build(patterns: Tuple[str, ...]) -> _ahoc.Automaton:  # type: ignore
        ac = _ahoc.Automaton(_ahoc.TRIE)
        for p in patterns:
            ac.add_word(p, p)
        ac.make_automaton()
        return ac


# ---------------------------------------------------------------------------
#  Wildcard → regex
# ---------------------------------------------------------------------------

def _wildcard_to_regex(pat: str) -> str:

    if len(pat) >= 2 and pat[0] == pat[-1] and pat[0] in {"'", '"'}:
        pat = pat[1:-1]

    start_anchor = not pat.startswith(("*", "%"))
    end_anchor   = not pat.endswith(("*", "%"))

    out: list[str] = []
    in_group = False
    first_in_group = False

    i = 0
    while i < len(pat):
        ch = pat[i]

        if not in_group:                     
            if ch in "*%":
                out.append(".*?")           
            elif ch == "?":
                out.append(".+?")             
            elif ch == "_":
                out.append(".")                
            elif ch == "[":
                in_group = True
                first_in_group = True
                out.append("[")
            else:
                out.append(re.escape(ch))
        else:                                
            if ch == "]":
                in_group = False
                out.append("]")
            elif ch == "-":
                if first_in_group or i + 1 == len(pat) or pat[i + 1] == "]":
                    out.append(r"\-")
                else:
                    out.append("-")
            elif ch == "^":
                out.append("^" if first_in_group else r"\^")
            else:
                out.append(ch)
            first_in_group = False
        i += 1

    body = "".join(out)
    if start_anchor:
        body = "^" + body
    if end_anchor:
        body += "$"
    return body


@lru_cache(maxsize=256)
def _compile_rx(pattern: str, flags: int):
    return _re.compile(pattern, flags | _re.DOTALL)


# ---------------------------------------------------------------------------
#  WildcardSearch
# ---------------------------------------------------------------------------

class WildcardSearch:
    __slots__ = (
        "_text",
        "_tokens",
        "_tokens_lc",
        "_idx_lc",
        "_rev_idx_lc",
        "_trie_cs",
        "_trie_lc",
        "_rev_trie_lc",
    )

    def __init__(self, text: str | None = None):
        self.text = text or ""

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text        = value or ""
        self._tokens      = _extract_tokens(self._text)
        self._tokens_lc   = [t.lower() for t in self._tokens]

        self._idx_lc: dict[str, Set[str]] = {}
        self._rev_idx_lc: dict[str, Set[str]] = {}
        for tok in self._tokens:
            lc = tok.lower()
            self._idx_lc    .setdefault(lc, set()).add(tok)
            self._rev_idx_lc.setdefault(lc[::-1], set()).add(tok)

        self._trie_cs     = marisa_trie.Trie(self._tokens)
        self._trie_lc     = marisa_trie.Trie(list(self._idx_lc))
        self._rev_trie_lc = marisa_trie.Trie(list(self._rev_idx_lc))


    def search(
        self,
        text: str | None,
        patterns: Iterable[str],
        *,
        ignore_case: bool = True,
    ) -> List[str]:
        """
        Return sorted list of tokens matching any wildcard in `patterns`.
        """
        if text is not None:
            self.text = text

        pats = list(patterns)
        if not pats:
            return []

        pre, suf, cont, other = self._bucket(pats)
        found: set[str] = set()
        if pre:
            found |= self._match_prefix(pre, ignore_case)
        if suf:
            found |= self._match_suffix(suf, ignore_case)
        if cont:
            found |= self._match_contains(cont, ignore_case)
        if other:
            found |= self._match_regex(other, ignore_case)


        wants_full_tag = any(p.startswith("<") and p.endswith(">") for p in pats)
        if wants_full_tag:
            found = {t for t in found if "<" in t and ">" in t}
        else:
            found = {t for t in found if "<" not in t and ">" not in t}

        return sorted(found)


    @staticmethod
    def _bucket(pats: List[str]):
        pre: List[str] = []
        suf: List[str] = []
        cont: List[str] = []
        other: List[str] = []
        for p in pats:
            ls, rs = p.startswith(("*", "%")), p.endswith(("*", "%"))
            core   = p.lstrip("*%").rstrip("*%")

            if rs and not ls and _is_literal(core):
                pre.append(core)          
            elif ls and not rs and _is_literal(core):
                suf.append(core)          
            elif ls and rs and _is_literal(core):
                cont.append(core)        
            else:
                other.append(p)         
        return pre, suf, cont, other


    def _match_prefix(self, prefs: List[str], ic: bool) -> Set[str]:
        trie = self._trie_lc if ic else self._trie_cs
        idx  = self._idx_lc  if ic else {t: {t} for t in self._tokens}
        out: Set[str] = set()
        for p in prefs:
            key = p.lower() if ic else p
            for k in trie.keys(key):
                out |= idx[k]
        return out

    def _match_suffix(self, sufs: List[str], ic: bool) -> Set[str]:
        out: Set[str] = set()
        for s in sufs:
            rs = s.lower()[::-1] if ic else s[::-1]
            for rev_key in self._rev_trie_lc.keys(rs):
                out |= self._rev_idx_lc[rev_key]
        if not ic:                       
            out = {t for t in out if any(t.endswith(s) for s in sufs)}
        return out

    def _match_contains(self, subs: List[str], ic: bool) -> Set[str]:
        if not subs:
            return set()
        if len(subs) <= OR_THRESHOLD:     
            flags = re.IGNORECASE if ic else 0
            rx = _re.compile("|".join(re.escape(s) for s in subs), flags)
            return {tok for tok in self._tokens if rx.search(tok)}

        pats = tuple(s.lower() if ic else s for s in subs)
        ac   = _LazyAC.build(pats)
        tgt  = self._text.lower() if ic else self._text
        return {pat for _, pat in ac.iter(tgt)}


    def _match_regex(self, pats: List[str], ic: bool) -> Set[str]:
        if not pats:
            return set()
        flags = _re.IGNORECASE if ic else 0
        compiled = [
            _compile_rx("|".join(_wildcard_to_regex(p) for p in pats[i:i + 32]), flags)
            for i in range(0, len(pats), 32)
        ]
        out: Set[str] = set()
        for tok in self._tokens:
            tgt = tok.lower() if ic else tok
            if any(rx.search(tgt) for rx in compiled):
                out.add(tok)
        return out

    def __repr__(self) -> str:            # pragma: no cover
        return f"WildcardSearch(len={len(self._text)})"


def _dedup_preserve(seq):
    from collections import OrderedDict
    return list(OrderedDict.fromkeys(seq))


def _csv_cells(text: str, delim: str):
    import csv, io
    rdr = csv.reader(io.StringIO(text), delimiter=delim)
    return [cell for row in rdr for cell in row]


def process_wildcard_words(
    text,
    patterns,
    *,
    ignore_case: bool = True,
    csv_delimiter: str | None = None,
):
    """Return the set of values that must be blanked according to *patterns*.

    This is the same behaviour that was previously in
    `wizard_cleaners.utils.process_wildcard_words`, kept here so that both
    import paths keep working.
    """
    if isinstance(patterns, (str, int)):
        patterns = [patterns]
    patterns = [str(p) for p in patterns]

    def has_wc(p): return any(ch in p for ch in _WC_CHARS)

    wc_patterns = [p for p in patterns if has_wc(p)]
    plain       = [p for p in patterns if not has_wc(p)]

    if csv_delimiter is not None:
        tokens = _csv_cells(text, csv_delimiter)
        search_text = " ".join(tokens)
    else:
        search_text = text

    result = []
    if wc_patterns:
        ws = WildcardSearch(search_text)
        result.extend(ws.search(None, wc_patterns, ignore_case=ignore_case))

    result.extend(plain)
    return _dedup_preserve(result)
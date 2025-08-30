# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations
from typing import Any, Dict, Iterator, List, Optional, Tuple

from textwizard.utils.tw_html_parser.dom import NodeType  # type: ignore
from textwizard.utils.tw_html_parser.parser import TWHTMLParser as _Parser  # type: ignore



# ──────────────────────────────────────────────────────────────────────────────
# Parser wrapper
# ──────────────────────────────────────────────────────────────────────────────

def _parse_html(html: str):
    if _Parser is None:
        raise RuntimeError("TWHTMLParser not available.")
    try:
        inst = _Parser(html)
        parse = getattr(inst, "parse", None)
        if callable(parse):
            try:
                return parse()
            except TypeError:
                return parse(html)
        for attr in ("document", "doc", "node", "dom", "tree", "root"):
            n = getattr(inst, attr, None)
            if n is not None:
                return n
    except TypeError:
        inst = _Parser()
        for name in ("parse_document", "parse"):
            fn = getattr(inst, name, None)
            if callable(fn):
                try:
                    return fn(html)
                except TypeError:
                    return fn()
    raise RuntimeError("TWHTMLParser API not recognized.")


# ──────────────────────────────────────────────────────────────────────────────
# Duck-typing layer per il DOM TextWizard
# ──────────────────────────────────────────────────────────────────────────────

def _is_text_node(node: Any) -> bool:
    if node is None:
        return False
    nt = getattr(node, "node_type", None)
    if nt == NodeType.TEXT_NODE:  # type: ignore[attr-defined]
        return True
    return isinstance(node, str)


def _get_text(node: Any) -> str:
    if isinstance(node, str):
        return node
    nt = getattr(node, "node_type", None)
    if nt == NodeType.TEXT_NODE:
        d = getattr(node, "data", "")
        return d if isinstance(d, str) else ""
    t = getattr(node, "text", None)
    if isinstance(t, str):
        return t
    d = getattr(node, "data", None)
    if isinstance(d, str):
        return d
    return ""


def _get_tag(node: Any) -> Optional[str]:
    if node is None:
        return None
    tn = getattr(node, "tag_name", None)
    if isinstance(tn, str):
        return tn.lower()
    t = getattr(node, "tag", None)
    if isinstance(t, str):
        return t.lower()
    n = getattr(node, "name", None)
    if isinstance(n, str):
        return n.lower()
    return None


def _get_attrs(node: Any) -> Dict[str, str]:
    # TextWizard Element: .get_attributes() -> dict
    ga = getattr(node, "get_attributes", None)
    if callable(ga):
        try:
            d = ga()
            if isinstance(d, dict):
                return {str(k).lower(): str(v) for k, v in d.items()}
        except Exception:
            pass
    # fallback comuni
    for attr_name in ("attrs", "attributes", "attrib"):
        val = getattr(node, attr_name, None)
        if isinstance(val, dict):
            return {str(k).lower(): str(v) for k, v in val.items()}
    return {}


def _iter_children_generic(node: Any) -> Iterator[Any]:
    # TextWizard: .child_nodes
    for name in ("child_nodes", "children", "childNodes", "contents"):
        ch = getattr(node, name, None)
        if isinstance(ch, (list, tuple)):
            yield from ch
            return
    # document.body-like
    for name in ("body", "elements"):
        ch = getattr(node, name, None)
        if isinstance(ch, (list, tuple)):
            yield from ch
            return
    return


def _get_children(node: Any) -> List[Any]:
    return list(_iter_children_generic(node))


def _text_content(node: Any) -> str:
    if _is_text_node(node):
        return _get_text(node)
    return "".join(_text_content(ch) for ch in _get_children(node))


# ──────────────────────────────────────────────────────────────────────────────
# Utils
# ──────────────────────────────────────────────────────────────────────────────

_MD_SPECIALS = "\\`*_{}[]()#+-.!|>~"

def _escape_md(text: str) -> str:
    if not text:
        return ""
    out = []
    for ch in text:
        out.append("\\" + ch if ch in _MD_SPECIALS else ch)
    return "".join(out)

def _collapse_ws(s: str) -> str:
    return " ".join(s.split())

def _trim_blank_lines(s: str) -> str:
    lines = s.splitlines()
    out: List[str] = []
    blank = False
    for ln in lines:
        if ln.strip():
            out.append(ln.rstrip())
            blank = False
        else:
            if not blank:
                out.append("")
                blank = True
    while out and out[0] == "":
        out.pop(0)
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)

def _fence(lang_hint: Optional[str] = None) -> str:
    return "```" + (lang_hint or "")

def _attr(node: Any, name: str, default: str = "") -> str:
    return _get_attrs(node).get(name, default)

def _has_class(node: Any, cls: str) -> bool:
    classes = _get_attrs(node).get("class", "")
    return any(c.strip() == cls for c in classes.split()) if classes else False


# ──────────────────────────────────────────────────────────────────────────────
# Inline rendering
# ──────────────────────────────────────────────────────────────────────────────

def _render_inline(node: Any) -> str:
    if _is_text_node(node):
        return _escape_md(_get_text(node))
    tag = _get_tag(node) or ""

    if tag in ("strong", "b"):
        inner = "".join(_render_inline(ch) for ch in _get_children(node))
        return f"**{inner}**"
    if tag in ("em", "i"):
        inner = "".join(_render_inline(ch) for ch in _get_children(node))
        return f"*{inner}*"
    if tag in ("u",):
        inner = "".join(_render_inline(ch) for ch in _get_children(node))
        return f"_{inner}_"
    if tag in ("del", "s", "strike"):
        inner = "".join(_render_inline(ch) for ch in _get_children(node))
        return f"~~{inner}~~"
    if tag in ("code", "kbd"):
        txt = _text_content(node).replace("`", "\\`")
        return f"`{txt}`"
    if tag == "mark":
        inner = "".join(_render_inline(ch) for ch in _get_children(node))
        return f"__{inner}__"
    if tag in ("sup", "sub"):
        inner_txt = _collapse_ws(_text_content(node))
        return f"^{_escape_md(inner_txt)}^" if tag == "sup" else f"~{_escape_md(inner_txt)}~"
    if tag == "br":
        return "  \n"

    if tag == "a":
        href = _attr(node, "href", "")
        title = _attr(node, "title", "")
        label = "".join(_render_inline(ch) for ch in _get_children(node)) or href
        if href:
            return f"[{label}]({href} \"{title}\")" if title else f"[{label}]({href})"
        return label

    if tag == "img":
        src = _attr(node, "src", "")
        alt = _attr(node, "alt", "")
        title = _attr(node, "title", "")
        return f"![{_escape_md(alt)}]({src} \"{title}\")" if title else f"![{_escape_md(alt)}]({src})"

    inner = "".join(_render_inline(ch) for ch in _get_children(node))
    return inner


# ──────────────────────────────────────────────────────────────────────────────
# Block rendering
# ──────────────────────────────────────────────────────────────────────────────

def _render_paragraph(node: Any) -> str:
    inner = "".join(_render_inline(ch) for ch in _get_children(node)).strip()
    return inner if inner else ""

def _render_heading(node: Any) -> str:
    tag = _get_tag(node) or "h1"
    level = 1
    if tag.startswith("h") and tag[1:2].isdigit():
        try:
            level = max(1, min(6, int(tag[1])))
        except Exception:
            level = 1
    content = "".join(_render_inline(ch) for ch in _get_children(node)).strip()
    return f"{'#' * level} {content}".rstrip()

def _render_blockquote(node: Any) -> str:
    body = _render_children_blocks(node)
    return "\n".join(["> " + (ln if ln.strip() else "") for ln in body.splitlines()])

def _render_hr(_: Any) -> str:
    return "---"

def _render_pre(node: Any) -> str:
    kids = _get_children(node)
    if len(kids) == 1 and (_get_tag(kids[0]) == "code"):
        code = _text_content(kids[0])
        lang = _attr(kids[0], "class", "").split()[0] if _attr(kids[0], "class", "") else ""
        return f"{_fence(lang)}\n{code.rstrip()}\n```"
    code = _text_content(node)
    return f"```\n{code.rstrip()}\n```"

def _render_list(node: Any, ordered: bool, depth: int = 0) -> str:
    out: List[str] = []
    index = 1
    for li in (ch for ch in _get_children(node) if _get_tag(ch) == "li"):
        chunks: List[str] = []
        sublists: List[Any] = []
        for sub in _get_children(li):
            t = _get_tag(sub)
            if t in ("ul", "ol"):
                sublists.append(sub)
            else:
                chunks.append(_render_inline(sub) if not _is_block(sub) else _render_block(sub))

        first_line = _collapse_ws("".join(chunks).strip())
        indent = "  " * depth
        bullet = f"{index}." if ordered else "-"
        out.append(f"{indent}{bullet} {first_line}" if first_line else f"{indent}{bullet} ")

        for sub in sublists:
            ordered_sub = (_get_tag(sub) == "ol")
            rendered = _render_list(sub, ordered=ordered_sub, depth=depth + 1)
            out.append(rendered)

        index += 1
    return "\n".join(out)

def _is_block(node: Any) -> bool:
    tag = (_get_tag(node) or "")
    return tag in {
        "p", "div", "section", "article", "aside",
        "header", "footer", "nav", "main",
        "ul", "ol", "li",
        "pre", "code",
        "blockquote",
        "hr",
        "table", "thead", "tbody", "tfoot", "tr", "th", "td",
        "figure", "figcaption",
        "h1", "h2", "h3", "h4", "h5", "h6",
        "html", "head", "body",
    }

def _render_table(node: Any) -> str:
    rows: List[List[str]] = []
    header: Optional[List[str]] = None

    def _cells(tr: Any) -> Tuple[List[str], bool]:
        cells = []
        is_header = False
        for td in _get_children(tr):
            tag = _get_tag(td)
            if tag in ("th", "td"):
                txt = _collapse_ws("".join(_render_inline(ch) for ch in _get_children(td)).strip())
                cells.append(txt)
                if tag == "th":
                    is_header = True
        return cells, is_header

    queue = _get_children(node)
    flat_tr: List[Any] = []
    for x in queue:
        t = _get_tag(x)
        if t in ("thead", "tbody", "tfoot"):
            for tr in _get_children(x):
                if _get_tag(tr) == "tr":
                    flat_tr.append(tr)
        elif t == "tr":
            flat_tr.append(x)

    for tr in flat_tr:
        cells, is_header = _cells(tr)
        if not cells:
            continue
        if is_header and header is None:
            header = cells
        else:
            rows.append(cells)

    if header is None and rows:
        header = rows.pop(0)
    if not header:
        return ""

    width = max(len(header), *(len(r) for r in rows)) if rows else len(header)

    def _pad(row: List[str]) -> List[str]:
        return row + [""] * (width - len(row))

    header = _pad(header)
    rows = [_pad(r) for r in rows]

    md = []
    md.append("| " + " | ".join(header) + " |")
    md.append("| " + " | ".join("---" for _ in header) + " |")
    for r in rows:
        md.append("| " + " | ".join(r) + " |")
    return "\n".join(md)

def _render_figure(node: Any) -> str:
    children = _get_children(node)
    img = next((ch for ch in children if _get_tag(ch) == "img"), None)
    cap = next((ch for ch in children if _get_tag(ch) == "figcaption"), None)
    parts = []
    if img is not None:
        parts.append(_render_inline(img))
    if cap is not None:
        cap_txt = "".join(_render_inline(ch) for ch in _get_children(cap)).strip()
        if cap_txt:
            parts.append(f"*{cap_txt}*")
    return "\n\n".join(parts)

def _render_block(node: Any) -> str:
    tag = _get_tag(node) or ""

    if tag in ("p", "div", "section", "article", "aside", "main", "header", "footer", "nav"):
        return _render_paragraph(node)
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        return _render_heading(node)
    if tag == "blockquote":
        return _render_blockquote(node)
    if tag == "hr":
        return _render_hr(node)
    if tag == "pre":
        return _render_pre(node)
    if tag == "ul":
        return _render_list(node, ordered=False)
    if tag == "ol":
        return _render_list(node, ordered=True)
    if tag == "table":
        return _render_table(node)
    if tag == "figure":
        return _render_figure(node)
    if tag == "br":
        return ""  

    if not _get_children(node):
        return _render_inline(node)
    return _render_children_blocks(node)

def _render_children_blocks(node: Any) -> str:
    out: List[str] = []
    for ch in _get_children(node):
        if _is_text_node(ch):
            txt = _collapse_ws(_get_text(ch))
            if txt:
                out.append(_escape_md(txt))
            continue
        if _is_block(ch):
            b = _render_block(ch)
            if b:
                out.append(b)
        else:
            inline = _render_inline(ch)
            if inline:
                if out and not out[-1].endswith("\n\n"):
                    out[-1] = (out[-1].rstrip() + " " + inline).strip()
                else:
                    out.append(inline)
    return "\n\n".join([s for s in out if s is not None])


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def html_dom_to_markdown(dom: Any) -> str:
    """Convert a TWHTMLParser DOM to Markdown."""
    if dom is None:
        return ""
    children = _get_children(dom)
    md = _render_children_blocks(dom) if children else _render_block(dom)
    return _trim_blank_lines(md)

def html_to_markdown_from_html(html: str) -> str:
    """
    Convert HTML string to Markdown. If parsing fails, return the original HTML.
    """
    try:
        dom = _parse_html(html)
    except Exception:
        return html
    return html_dom_to_markdown(dom)

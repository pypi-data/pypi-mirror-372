# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations
from typing import Any, List, Dict

from textwizard.utils.tw_html_parser.dom import DocumentType, Element, Node, NodeType, Text
from textwizard.utils.tw_html_parser.serializer import HTMLSerializer
from textwizard.utils.tw_html_parser._utils import VOID_ELEMENTS, rcdata_elements

__all__ = ["PrettyHTMLSerializer"]


class PrettyHTMLSerializer(HTMLSerializer):
    """
    Pretty-printer on top of HTMLSerializer with a single output buffer.
    """

    __slots__ = ("_indent", "expand_mixed_content", "expand_empty_elements", "_icache", "encoding")

    def __init__(
        self,
        *,
        indent: int = 2,
        expand_mixed_content: bool = False,
        expand_empty_elements: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._indent = max(int(indent or 0), 0)
        self.expand_mixed_content = bool(expand_mixed_content)
        self.expand_empty_elements = bool(expand_empty_elements)
        self._icache: Dict[int, str] = {0: ""}

    # ---------- public ----------
    def render(self, node: Node, encoding: Any = None) -> str:  # type: ignore[override]
        self.encoding = encoding
        out_parts: List[str] = []
        self._write_node(node, 0, out_parts)
        out = "".join(out_parts)
        if encoding:
            return out.encode(encoding, errors="htmlentityreplace")
        return out

    # ---------- internals ----------
    def _indent_str(self, depth: int) -> str:
        if self._indent <= 0:
            return ""
        s = self._icache.get(depth)
        if s is None:
            s = " " * (self._indent * depth)
            self._icache[depth] = s
        return s

    def _write_node(self, node: Node, depth: int, out: List[str]) -> None:
        nt = node.node_type

        if nt == NodeType.DOCUMENT_NODE:
            for ch in node.child_nodes:
                self._write_node(ch, depth, out)
            return

        if nt == NodeType.DOCUMENT_TYPE_NODE:
            dt: DocumentType = node
            pub = dt.public_id.strip() if dt.public_id else ""
            sys = dt.system_id.strip() if dt.system_id else ""
            out.append(f'<!DOCTYPE {dt.name} PUBLIC "{pub}" "{sys}">' if (pub or sys) else f"<!DOCTYPE {dt.name}>")
            return

        if nt == NodeType.COMMENT_NODE:
            out.append(f"<!--{node.data}-->")
            return

        if nt == NodeType.TEXT_NODE:
            out.append(self._serialize_text(node))
            return

        # Element
        elem: Element = node  # type: ignore[assignment]
        tag = self._get_tag(elem)

        out.append("<"); out.append(tag)

        # preserve customized built-ins
        is_val = getattr(elem, "is_value", None)
        if is_val is not None and "is" not in elem.get_attributes():
            out.append(' is="'); out.append(self._escape_attr(is_val)); out.append('"')

        attrs = elem.get_attributes()
        items = list(attrs.items())
        if self.alphabetical_attributes:
            items.sort(key=lambda kv: kv[0])
        for name, value in items:
            out.append(" "); out.append(self._serialize_attribute(name, value, tag))

        if tag in VOID_ELEMENTS:
            if self.use_trailing_solidus:
                out.append(" /" if self.space_before_trailing_solidus else "/")
            out.append(">")
            return

        out.append(">")

        # flat if no indenting
        if self._indent <= 0:
            self._write_children_flat(elem, depth, out)
            out.append("</"); out.append(tag); out.append(">")
            return

        # RCData stays flat
        if tag in rcdata_elements:
            self._write_children_flat(elem, depth, out)
            out.append("</"); out.append(tag); out.append(">")
            return

        children = elem.child_nodes
        if not children:
            if self.expand_empty_elements:
                out.append("\n"); out.append(self._indent_str(depth))
            out.append("</"); out.append(tag); out.append(">")
            return

        # mixed content flat unless expansion requested
        if (not self.expand_mixed_content) and self._has_mixed_content(elem):
            self._write_children_flat(elem, depth, out)
            out.append("</"); out.append(tag); out.append(">")
            return

        # pretty block
        nl = "\n"
        indent_child = self._indent_str(depth + 1)
        indent_cur = self._indent_str(depth)

        out.append(nl)
        for ch in children:
            out.append(indent_child)
            self._write_node(ch, depth + 1, out)
            out.append(nl)
        out.append(indent_cur); out.append("</"); out.append(tag); out.append(">")

    def _write_children_flat(self, elem: Element, depth: int, out: List[str]) -> None:
        # shadow root first
        if self._is_shadow_host(elem):
            shadow = getattr(elem, "shadowRoot", None)
            if shadow is not None:
                out.append(self._serialize_shadow_root(shadow))

        tag = self._get_tag(elem)
        if tag in rcdata_elements:
            for ch in elem.child_nodes:
                if ch.node_type == NodeType.TEXT_NODE:
                    out.append(ch.data)
                else:
                    self._write_node(ch, depth, out)
            return

        for ch in elem.child_nodes:
            self._write_node(ch, depth, out)

    @staticmethod
    def _has_mixed_content(elem: Element) -> bool:
        has_text = False
        has_non_text = False
        for c in elem.child_nodes:
            if c.node_type == NodeType.TEXT_NODE:
                if isinstance(c, Text) and c.data.strip():
                    has_text = True
            else:
                has_non_text = True
            if has_text and has_non_text:
                return True
        return False

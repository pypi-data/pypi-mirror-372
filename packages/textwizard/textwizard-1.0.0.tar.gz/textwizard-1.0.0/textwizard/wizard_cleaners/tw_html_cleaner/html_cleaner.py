# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations
from collections import deque
from typing import Callable, Deque, FrozenSet, Iterable, List, Set, Tuple, Dict, Protocol

from textwizard.utils.tw_html_parser.dom import Element, Node, NodeType
from textwizard.utils.tw_html_parser.parser import TWHTMLParser
from textwizard.utils.tw_html_parser.serializer import HTMLSerializer
from textwizard.utils.wildcard import process_wildcard_words
from textwizard.wizard_cleaners.tw_html_cleaner.constants import (
    EMBEDDED_CONTENT,
    FLOW_CONTENT,
    HEADING_CONTENT,
    INTERACTIVE_CONTENT,
    METADATA_CONTENT,
    PALPABLE_CONTENT,
    PHRASING_CONTENT,
    SCRIPT_SUPPORTING,
    SECTIONING_CONTENT,
)


if not hasattr(Element, "tag_lower"):
    Element.tag_lower = Element.tag_name_lower


_TAG_GROUPS: Dict[str, FrozenSet[str]] = {
    "html.remove_script": SCRIPT_SUPPORTING,
    "html.remove_metadata_tags": METADATA_CONTENT,
    "html.remove_flow_tags": FLOW_CONTENT,
    "html.remove_sectioning_tags": SECTIONING_CONTENT,
    "html.remove_heading_tags": HEADING_CONTENT,
    "html.remove_phrasing_tags": PHRASING_CONTENT,
    "html.remove_embedded_tags": EMBEDDED_CONTENT,
    "html.remove_interactive_tags": INTERACTIVE_CONTENT,
    "html.remove_palpable": PALPABLE_CONTENT,
}

# ===================== traversal =========================== #
def iter_nodes(
    root: Node, predicate: Callable[[Node], bool] | None = None, *, include_root: bool = False
) -> Iterable[Tuple[Node, Node | None]]:
    dq: Deque[Tuple[Node, Node | None]] = deque([(root, None)])
    append, pop = dq.append, dq.pop
    while dq:
        node, parent = pop()
        if include_root or parent is not None:
            if predicate is None or predicate(node):
                yield node, parent
        for child in reversed(node.child_nodes):
            append((child, node))


def _siblings(container: Node, target: Node) -> Tuple[Node | None, Node | None]:
    sibs = container.child_nodes
    idx = sibs.index(target)
    return sibs[idx - 1] if idx else None, sibs[idx + 1] if idx < len(sibs) - 1 else None


class Action(Protocol):
    def __call__(self, node: Node, parent: Node | None) -> bool: ...


class HTMLCleaner:
    __slots__ = ("doc", "_preserve_set", "html_text")

    def __init__(self) -> None:
        self.doc: Node | None = None
        self._preserve_set: Set[str] = set()
        self.html_text: str = ""

    def clean(self, html_text: str, **kwargs) -> str:
        self.html_text = html_text
        self.doc = TWHTMLParser(html_text).parse()

        params = {k: v for k, v in kwargs.items() if v is not None}
        if not params:
            return self._extract_text(self.doc)

        if any(params.values()):
            actions = self._build_actions(params)
            self._apply_actions_once(actions)
            self._apply_extra_true_params(params)
        else:
            self._apply_false_params({k: v for k, v in params.items() if v is False})
            return self._extract_text_preserving(
                self.doc,
                self._preserve_set,
                preserve_comments=params.get("html.remove_comments") is False,
                preserve_doctype=params.get("html.remove_doctype") is False,
            )

        if not self.doc.child_nodes:
            return ""
        return HTMLSerializer(quote_attr_values="always").render(self.doc)

    def _build_actions(self, params: dict) -> List[Action]:
        actions: List[Action] = []
        doc = self.doc
        sibs = _siblings

        for key, tag_set in _TAG_GROUPS.items():
            if params.get(key):
                ts = tag_set

                def remove_group(n: Node, p: Node | None, ts=ts, d=doc) -> bool:
                    if p and n.node_type == NodeType.ELEMENT_NODE and n.tag_lower in ts:
                        prev, nxt = sibs(p, n)
                        if (
                                prev and nxt
                                and prev.node_type == nxt.node_type == NodeType.TEXT_NODE
                                and not prev.data.endswith(" ")
                                and not nxt.data.startswith(" ")
                        ):
                            p.insert_before(d.create_text_node(" "), n)
                        p.remove_child(n)
                        return True
                    return False

                actions.append(remove_group)

        if params.get("html.remove_doctype"):
            actions.append(
                lambda n, p: (
                    p is not None
                    and n.node_type == NodeType.DOCUMENT_TYPE_NODE
                    and p.remove_child(n) is None
                )
            )

        if params.get("html.remove_comments"):
            actions.append(
                lambda n, p: (
                    p is not None
                    and n.node_type == NodeType.COMMENT_NODE
                    and p.remove_child(n) is None
                )
            )

        return actions

    def _apply_actions_once(self, actions: List[Action]) -> None:
        doc = self.doc
        it = iter_nodes
        for node, parent in it(doc, include_root=False):
            for act in actions:
                if act(node, parent):
                    break

    def _apply_extra_true_params(self, params: dict) -> None:
        if "html.remove_specific_tags" in params:
            self._unwrap_elements_by_tag_names(
                set(process_wildcard_words(self.html_text, params["html.remove_specific_tags"]))
            )
        if "html.remove_tags_and_contents" in params:
            self._remove_tags_and_contents(
                set(process_wildcard_words(self.html_text, params["html.remove_tags_and_contents"]))
            )
        if "html.remove_content_tags" in params:
            self._remove_content_from_elements_by_tag_names(
                set(process_wildcard_words(self.html_text, params["html.remove_content_tags"]))
            )
        if "html.remove_specific_attributes" in params:
            self._remove_specific_attributes(
                process_wildcard_words(self.html_text, params["html.remove_specific_attributes"])
            )
        if params.get("html.remove_empty_tags"):
            self._remove_empty_tags(self.doc)

    def _apply_false_params(self, params: dict) -> None:
        keep: Set[str] = set()
        for key, tag_set in _TAG_GROUPS.items():
            if params.get(key) is False:
                keep |= tag_set
        self._preserve_set = keep

    @staticmethod
    def _extract_text(root: Node) -> str:
        pieces: List[str] = []
        stack = deque([(root, False)])
        pop = stack.pop
        push = stack.append
        skip_tags = SCRIPT_SUPPORTING

        while stack:
            node, in_skip = pop()
            nt = node.node_type
            if nt is NodeType.TEXT_NODE:
                if not in_skip:
                    pieces.append(node.data)
            elif nt is NodeType.ELEMENT_NODE:
                new_skip = in_skip or node.tag_name_lower in skip_tags
                if not new_skip:
                    for c in reversed(node.child_nodes):
                        push((c, new_skip))
            else:
                for c in reversed(node.child_nodes):
                    push((c, in_skip))

        out: List[str] = []
        append_out = out.append
        for blk in pieces:
            if not blk:
                continue
            if out and not out[-1][-1].isspace() and not blk[0].isspace():
                append_out(" ")
            append_out(blk)
        return "".join(out)


    def _extract_preserved_sectioning(self, node: Node, preserve_set: Set[str]) -> str:
        return "".join(
            child.data
            if child.node_type == NodeType.TEXT_NODE
            else (
                f"<{child.tag_name}>{self._extract_preserved_sectioning(child, preserve_set)}</{child.tag_name}>"
                if child.node_type == NodeType.ELEMENT_NODE and child.tag_name.lower() in preserve_set
                else ""
            )
            for child in node.child_nodes
        )

    def _extract_text_preserving(
        self,
        node: Node,
        preserve_set: Set[str],
        preserve_comments: bool = False,
        preserve_doctype: bool = False,
    ) -> str:
        from textwizard.utils.tw_html_parser.serializer import HTMLSerializer

        def merge(parts: List[str]) -> str:
            out: List[str] = []
            for part in parts:
                if not part or not part.strip():
                    continue
                if out:
                    last, first = out[-1][-1], part[0]
                    if last != ">" and first != "<" and not last.isspace() and not first.isspace():
                        out.append(" ")
                out.append(part)
            return "".join(out)

        if node.node_type == NodeType.TEXT_NODE:
            return node.data
        if node.node_type == NodeType.COMMENT_NODE:
            return f"<!--{node.data}-->" if preserve_comments else ""
        if node.node_type == NodeType.DOCUMENT_TYPE_NODE:
            return f"<!DOCTYPE {getattr(node, 'name', 'html')}>" if preserve_doctype else ""

        if node.node_type == NodeType.ELEMENT_NODE:
            tag = node.tag_lower
            if tag in SCRIPT_SUPPORTING and tag not in preserve_set:
                return ""
            if tag in preserve_set:
                if tag in SECTIONING_CONTENT:
                    inner = merge(
                        [
                            self._extract_text_preserving(c, preserve_set, preserve_comments, preserve_doctype)
                            for c in node.child_nodes
                        ]
                    )
                    return f"<{node.tag_name}>{inner}</{node.tag_name}>"
                return HTMLSerializer(quote_attr_values="always").render(node)

            return merge(
                [
                    self._extract_text_preserving(c, preserve_set, preserve_comments, preserve_doctype)
                    for c in node.child_nodes
                ]
            )

        return merge(
            [
                self._extract_text_preserving(c, preserve_set, preserve_comments, preserve_doctype)
                for c in node.child_nodes
            ]
        )


    def _remove_elements_by_tag_names(self, tag_names: FrozenSet[str]) -> None:
        pred = lambda n: n.node_type == NodeType.ELEMENT_NODE and n.tag_lower in tag_names  # noqa: E731
        for node, parent in iter_nodes(self.doc, pred):
            if parent is None:
                continue
            prev_sib, next_sib = _siblings(parent, node)
            if (
                prev_sib
                and next_sib
                and prev_sib.node_type == next_sib.node_type == NodeType.TEXT_NODE
                and not prev_sib.data.endswith(" ")
                and not next_sib.data.startswith(" ")
            ):
                parent.insert_before(self.doc.create_text_node(" "), node)
            parent.remove_child(node)

    def _unwrap_elements_by_tag_names(self, tag_names: Set[str]) -> None:
        changed = True
        while changed:
            changed = self._unwrap_pass(tag_names)

    def _unwrap_pass(self, tag_names: Set[str]) -> bool:
        changed = False
        tag_lower = {t.lower() for t in tag_names}
        stack = [self.doc]

        while stack:
            cur = stack.pop()
            for child in list(cur.child_nodes):
                if child.node_type == NodeType.ELEMENT_NODE:
                    elem = child
                    if elem.tag_lower in tag_lower:
                        changed = True
                        idx = cur.child_nodes.index(elem)
                        cur.remove_child(elem)

                        grand = list(elem.child_nodes)
                        for g in grand:
                            cur.insert_before(
                                g, cur.child_nodes[idx] if idx < len(cur.child_nodes) else None
                            )
                            if (
                                idx > 0
                                and cur.child_nodes[idx - 1].node_type == g.node_type == NodeType.TEXT_NODE
                                and not cur.child_nodes[idx - 1].data.endswith(" ")
                                and not g.data.startswith(" ")
                            ):
                                cur.child_nodes[idx - 1].data += " "
                            idx += 1

                        if grand:
                            last_g = grand[-1]
                            next_sib = cur.child_nodes[idx] if idx < len(cur.child_nodes) else None
                            if (
                                last_g.node_type == NodeType.TEXT_NODE
                                and next_sib
                                and next_sib.node_type == NodeType.TEXT_NODE
                                and not last_g.data.endswith(" ")
                                and not next_sib.data.startswith(" ")
                            ):
                                last_g.data += " "
                        continue
                    stack.append(child)
                else:
                    stack.append(child)
        return changed

    @staticmethod
    def _remove_comments(root: Node) -> None:
        for node, parent in iter_nodes(
            root, lambda n: n.node_type == NodeType.COMMENT_NODE, include_root=False
        ):
            parent.remove_child(node)  # type: ignore[arg-type]

    def _remove_doctype(self) -> None:
        if self.doc is not None and hasattr(self.doc, "child_nodes"):
            for child in list(self.doc.child_nodes):
                if child.node_type == NodeType.DOCUMENT_TYPE_NODE:
                    self.doc.remove_child(child)

    def _remove_content_from_elements_by_tag_names(self, tag_names: Set[str]) -> None:
        tag_names_lower = {t.lower() for t in tag_names}
        pred = lambda n: n.node_type == NodeType.ELEMENT_NODE and n.tag_lower in tag_names_lower  # noqa: E731
        for node, _ in iter_nodes(self.doc, pred):
            node._children = []  # type: ignore[attr-defined]

    def _remove_tags_and_contents(self, tag_names: Set[str]) -> None:
        names = {t.lower() for t in tag_names}
        pred = lambda n: n.node_type == NodeType.ELEMENT_NODE and n.tag_lower in names  # noqa: E731
        for node, parent in iter_nodes(self.doc, pred):
            if parent is None:
                continue
            prev_sib, next_sib = _siblings(parent, node)
            if (
                prev_sib
                and next_sib
                and prev_sib.node_type == next_sib.node_type == NodeType.TEXT_NODE
                and not prev_sib.data.endswith(" ")
                and not next_sib.data.startswith(" ")
            ):
                parent.insert_before(self.doc.create_text_node(" "), node)
            parent.remove_child(node)

    def _remove_specific_attributes(self, attributes: List[str]) -> None:
        attr_set = {a.lower() for a in attributes}
        pred = lambda n: n.node_type == NodeType.ELEMENT_NODE  # noqa: E731
        for node, _ in iter_nodes(self.doc, pred, include_root=True):
            if node.node_type == NodeType.ELEMENT_NODE:
                for attr in list(node.get_attributes().keys()):
                    if attr.lower() in attr_set:
                        node.remove_attribute(attr)

    @staticmethod
    def _remove_empty_tags(root: Node) -> None:
        changed = True
        while changed:
            changed = False
            for node, parent in iter_nodes(root, include_root=False):
                if parent is None:
                    continue
                if node.node_type == NodeType.ELEMENT_NODE:
                    if (
                        not node.child_nodes
                        or all(
                            c.node_type == NodeType.TEXT_NODE and not c.data.strip()
                            for c in node.child_nodes
                        )
                    ):
                        parent.remove_child(node)  # type: ignore[arg-type]
                        changed = True

        if root and not root.child_nodes:
            root._children.clear()  # type: ignore[attr-defined]


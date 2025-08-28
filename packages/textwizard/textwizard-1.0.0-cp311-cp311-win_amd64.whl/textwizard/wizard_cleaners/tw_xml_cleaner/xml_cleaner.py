# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations

import fnmatch
import html
import re
from functools import wraps
from typing import Mapping, Sequence, Set, Tuple

from lxml import etree
from xml.dom.minidom import Node, parseString

from textwizard.utils.wildcard import process_wildcard_words


def _strip_nodes_dom(src: str, *, remove_comments: bool = False, remove_processing: bool = False) -> str:
    if not (remove_comments or remove_processing):
        return src
    doc = parseString(src)

    def recurse(node: Node) -> None:
        for child in list(node.childNodes):
            remove = (
                remove_comments and child.nodeType == Node.COMMENT_NODE
            ) or (
                remove_processing and child.nodeType == Node.PROCESSING_INSTRUCTION_NODE
            )
            if remove:
                prev, nxt = child.previousSibling, child.nextSibling
                if (
                    prev
                    and nxt
                    and prev.nodeType == nxt.nodeType == Node.TEXT_NODE
                    and not prev.data.endswith((" ", "\n"))
                    and not nxt.data.startswith((" ", "\n"))
                ):
                    prev.data += " "
                node.removeChild(child)
            elif child.nodeType in (Node.DOCUMENT_NODE, Node.ELEMENT_NODE):
                recurse(child)

    recurse(doc)
    return doc.toxml()


def _normalize_ws(text: str | None) -> str | None:
    if text is None:
        return None
    parts = text.split()
    return " ".join(parts) if parts else text


def _all_text(xml_text: str) -> str:
    parser = etree.XMLParser(remove_blank_text=False, recover=True, strip_cdata=False)
    try:
        root = etree.fromstring(xml_text.encode("utf-8"), parser)
    except etree.XMLSyntaxError:
        return xml_text
    return " ".join(t for t in root.xpath("//text()") if t and t.strip())


def _needs_root(method):  # type: ignore[override]
    @wraps(method)
    def wrapper(self: "XMLCleaner", *args, **kwargs):
        if self.root is None:
            raise RuntimeError("Call clean() first")
        return method(self, *args, **kwargs)

    return wrapper


class XMLCleaner:  # noqa: D101
    __slots__ = ("root", "_parser", "_xml_text")

    _PIPE: Mapping[str, str] = {
        "xml.remove_comments": "_remove_comments",
        "xml.remove_processing_instructions": "_remove_processing",
        "xml.remove_namespaces": "_strip_namespaces",
        "xml.remove_content_tags": "_remove_content_tags",
        "xml.remove_specific_tags": "_remove_specific_tags",
        "xml.remove_attributes": "_remove_attributes",
        "xml.remove_cdata_sections": "_remove_cdata",
        "xml.collapse_whitespace": "_collapse_whitespace",
        "xml.remove_duplicate_siblings": "_remove_duplicate_siblings",
        "xml.remove_empty_tags": "_remove_empty_tags",
    }

    def __init__(self) -> None:
        self._parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False, recover=True)
        self.root: etree._Element | None = None
        self._xml_text: str | None = None

    # ------------------------------------------------------------------ #
    def clean(self, xml: str | bytes, /, **flags) -> str:
        xml_text = xml.decode("utf-8", "replace") if isinstance(xml, bytes) else str(xml)
        xml_bytes = xml if isinstance(xml, bytes) else xml_text.encode()
        self._xml_text = xml_text
        active = {k: v for k, v in flags.items() if v is not None}

        if not active:
            return _all_text(xml_text)

        self.root = etree.fromstring(xml_bytes, self._parser)

        if active.get("xml.remove_comments") or active.get("xml.remove_processing_instructions"):
            cleaned = _strip_nodes_dom(
                etree.tostring(self.root, encoding="unicode", with_tail=False),
                remove_comments=bool(active.get("xml.remove_comments")),
                remove_processing=bool(active.get("xml.remove_processing_instructions")),
            )
            self.root = etree.fromstring(cleaned.encode(), self._parser)

        for flag, helper in self._PIPE.items():
            if flag in active and flag not in (
                "xml.remove_comments",
                "xml.remove_processing_instructions",
            ):
                getattr(self, helper)(active[flag])

        if (
            "xml.remove_empty_tags" in active
            and len(self.root) == 0
            and not (self.root.text or "").strip()
        ):
            return ""

        return etree.tostring(self.root, encoding="unicode", pretty_print=False, xml_declaration=False)

    @_needs_root
    def _remove_comments(self, _):
        pass

    @_needs_root
    def _remove_processing(self, _):
        pass

    @_needs_root
    def _strip_namespaces(self, _):
        for el in self.root.iter():
            if isinstance(el.tag, str) and "}" in el.tag:
                el.tag = el.tag.split("}", 1)[1]
            for attr in list(el.attrib):
                if "}" in attr:
                    el.attrib[attr.split("}", 1)[1]] = el.attrib.pop(attr)
        etree.cleanup_namespaces(self.root)


    @_needs_root
    def _remove_content_tags(self, patterns):
        patterns = self._prepare_patterns(patterns)
        for tag in patterns:
            local = tag.split(":", 1)[1] if ":" in tag else tag
            xpath = f".//*[local-name()='{local}' or name()='{tag}']"
            for el in list(self.root.xpath(xpath)):
                for child in list(el):
                    child.tail = None
                    el.remove(child)
                el.text = None

    @_needs_root
    def _remove_specific_tags(self, patterns):
        patterns = self._prepare_patterns(patterns)
        for tag in patterns:
            local = tag.split(":", 1)[1] if ":" in tag else tag
            xpath = f".//*[local-name()='{local}' or name()='{tag}']"
            for el in list(self.root.xpath(xpath)):
                parent = el.getparent()
                if parent is None:
                    continue
                tail = el.tail
                prev = el.getprevious()
                parent.remove(el)
                if tail:
                    if prev is not None:
                        prev.tail = (prev.tail or "") + tail
                    else:
                        parent.text = (parent.text or "") + tail

    @_needs_root
    def _remove_attributes(self, patterns):
        patterns = self._prepare_patterns(patterns)
        plain: Set[str] = {p for p in patterns if "*" not in p and "?" not in p}
        wild = [p for p in patterns if p not in plain]
        wild_compiled: Sequence[Tuple[bool, re.Pattern[str]]] = [(":" in p, re.compile(fnmatch.translate(p)).fullmatch) for p in wild]
        nsmap = {k: v for k, v in self.root.nsmap.items() if k}
        nsmap.setdefault("xml", "http://www.w3.org/XML/1998/namespace")

        for el in self.root.iter():
            for attr_key in list(el.attrib):
                local, prefix = self._split_qname(attr_key, nsmap)
                qname = f"{prefix}:{local}" if prefix else local
                if qname in plain or local in plain:
                    del el.attrib[attr_key]
                    continue
                for is_qname, rx in wild_compiled:
                    if (is_qname and rx(qname)) or (not is_qname and rx(local)):
                        del el.attrib[attr_key]
                        break

    @_needs_root
    def _remove_cdata(self, _):
        for el in self.root.iter():
            if el.text is not None:
                el.text = html.unescape(str(el.text))
            if el.tail is not None:
                el.tail = html.unescape(str(el.tail))

    @_needs_root
    def _collapse_whitespace(self, _):
        for txt in self.root.xpath("//text()"):
            new = _normalize_ws(str(txt))
            if new != str(txt):
                parent = txt.getparent()
                if getattr(txt, "is_tail", False):
                    parent.tail = new
                else:
                    parent.text = new

    @_needs_root
    def _remove_duplicate_siblings(self, _):
        for parent in self.root.iter():
            seen: Set[str] = set()
            for child in list(parent):
                rep = etree.tostring(child, encoding="unicode")
                if rep in seen:
                    parent.remove(child)
                else:
                    seen.add(rep)

    @_needs_root
    def _remove_empty_tags(self, _):
        self._strip_blank_text_nodes(self.root)
        while True:
            empty = [
                el
                for el in self.root.iter()
                if len(el) == 0 and not (el.text or "").strip() and el is not self.root
            ]
            if not empty:
                break
            for el in empty:
                parent = el.getparent()
                if parent is None:
                    continue
                tail = el.tail
                prev = el.getprevious()
                parent.remove(el)
                if tail:
                    if prev is not None:
                        prev.tail = (prev.tail or "") + tail
                    else:
                        parent.text = (parent.text or "") + tail
            self._strip_blank_text_nodes(self.root)


    @staticmethod
    def _strip_blank_text_nodes(elem: etree._Element) -> None:
        for node in elem.iter():
            if node.text is not None and not node.text.strip():
                node.text = None
            if node.tail is not None and not node.tail.strip():
                node.tail = None

    @staticmethod
    def _split_qname(attr_key: str, nsmap: Mapping[str, str]):
        if attr_key.startswith("{") and "}" in attr_key:
            uri, local = attr_key[1:].split("}", 1)
            prefix = next((p for p, u in nsmap.items() if u == uri), None)
            return local, prefix
        return attr_key, None


    def _prepare_patterns(self, raw) -> Tuple[str, ...]:
        return tuple(process_wildcard_words(self._xml_text or "", raw))

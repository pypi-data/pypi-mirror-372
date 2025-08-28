# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

import re
from typing import Any, List
from textwizard.utils.tw_html_parser.dom import (
    DocumentType,
    Element,
    Text,
    Node,
    NodeType,
    ShadowRoot,
)
from textwizard.utils.tw_html_parser.entities_wrapper import lookup_entity_value_py  # type: ignore
from textwizard.utils.tw_html_parser._utils import VOID_ELEMENTS, space_characters, boolean_attributes, rcdata_elements

_quote_attr_spec_chars = "".join(space_characters) + "\"'=<>`/"
_quote_attr_spec = re.compile("[" + re.escape(_quote_attr_spec_chars) + "]")
_quote_attr_legacy = re.compile("[" + re.escape(_quote_attr_spec_chars) + "\x00-\x1F]")

class HTMLSerializer:
    options = (
        "quote_attr_values", "quote_char", "use_best_quote_char",
        "omit_optional_tags", "minimize_boolean_attributes",
        "use_trailing_solidus", "space_before_trailing_solidus",
        "escape_lt_in_attrs", "escape_rcdata", "resolve_entities",
        "alphabetical_attributes", "inject_meta_charset",
        "strip_whitespace", "sanitize", "include_doctype"
    )

    def __init__(self, **kwargs: Any) -> None:
        """
           Initialize the HTMLSerializer with various options for serializing HTML nodes.

           Keyword Args:
               quote_attr_values (str): Determines how attribute values are quoted in the
                   serialized HTML output. Acceptable values are:
                       - "always": Always enclose attribute values in quotes, regardless of content.
                       - "spec": Only enclose attribute values in quotes if they contain special characters
                                 (e.g., whitespace, quotes, '=', '<', '>', or '`') as defined by the specification.
                       - "legacy": Quote attribute values only if they contain characters that require quoting
                                   based on legacy behavior.
                   Default is "legacy".
               quote_char (str): The character used for quoting attribute values. Default is '"'.
               use_best_quote_char (bool): If True, dynamically chooses the best quote character for each attribute,
                   based on its content, to minimize escaping. Default is True.
               omit_optional_tags (bool): If True, omits optional tags in the output. Default is True.
               minimize_boolean_attributes (bool): If True, minimizes boolean attributes (e.g., renders `disabled`
                   instead of `disabled="disabled"`). Default is True.
               use_trailing_solidus (bool): If True, uses a trailing solidus in void elements. Default is False.
               space_before_trailing_solidus (bool): If True, adds a space before the trailing solidus.
                   Default is True.
               escape_lt_in_attrs (bool): If True, escapes the '<' character in attribute values. Default is False.
               escape_rcdata (bool): If True, escapes RCData in the output. Default is False.
               resolve_entities (bool): If True, resolves entities in the output. Default is True.
               alphabetical_attributes (bool): If True, sorts attributes alphabetically. Default is False.
               inject_meta_charset (bool): If True, injects a meta charset tag into the output. Default is True.
               strip_whitespace (bool): If True, strips extra whitespace in text nodes. Default is False.
               sanitize (bool): If True, sanitizes the output. Default is False.
               include_doctype (bool): If True, includes the doctype in the output. Default is True.
           """
        defaults = {
            "quote_attr_values": "legacy",  # "legacy", "spec", "always"
            "quote_char": '"',
            "use_best_quote_char": True,
            "omit_optional_tags": True,
            "minimize_boolean_attributes": True,
            "use_trailing_solidus": False,
            "space_before_trailing_solidus": True,
            "escape_lt_in_attrs": False,
            "escape_rcdata": False,
            "resolve_entities": True,
            "alphabetical_attributes": False,
            "inject_meta_charset": True,
            "strip_whitespace": False,
            "sanitize": False,
            "include_doctype": True,
        }
        for opt in self.options:
            setattr(self, opt, kwargs.get(opt, defaults[opt]))
        self.errors: List[str] = []
        self.strict = False
        self.encoding: Any = None

    def encode(self, s: str) -> str:
        if self.encoding:
            return s.encode(self.encoding, errors="htmlentityreplace")
        return s

    def encode_strict(self, s: str) -> bytes | str:
        if self.encoding:
            return s.encode(self.encoding, errors="strict")
        return s

    def render(self, node: Node, encoding: Any = None) -> str:
        self.encoding = encoding
        result = self.serialize_node(node)
        if encoding:
            return result.encode(encoding, errors="htmlentityreplace")
        return result

    def serialize_node(self, node: Node) -> str:
        parts: List[str] = []
        if node.node_type == NodeType.DOCUMENT_NODE:
            for child in node.child_nodes:
                parts.append(self.serialize_node(child))
        elif node.node_type == NodeType.DOCUMENT_TYPE_NODE:
            dt: DocumentType = node
            public_id = dt.public_id.strip() if dt.public_id else ""
            system_id = dt.system_id.strip() if dt.system_id else ""
            if public_id or system_id:
                parts.append(f'<!DOCTYPE {dt.name} PUBLIC "{public_id}" "{system_id}">')
            else:
                parts.append(f'<!DOCTYPE {dt.name}>')
        elif node.node_type == NodeType.ELEMENT_NODE:
            parts.append(self._serialize_element(node))
        elif node.node_type == NodeType.TEXT_NODE:
            parts.append(self._serialize_text(node))
        elif node.node_type == NodeType.COMMENT_NODE:
            parts.append(f"<!--{node.data}-->")
        return "".join(parts)

    def _serialize_element(self, elem: Element) -> str:
        parts: List[str] = []
        tag = self._get_tag(elem)
        parts.append(f"<{tag}")
        if getattr(elem, "is_value", None) is not None and "is" not in elem.get_attributes():
            parts.append(f' is="{self._escape_attr(elem.is_value)}"')
        attrs = elem.get_attributes()
        attr_items = list(attrs.items())
        if self.alphabetical_attributes:
            attr_items.sort(key=lambda x: x[0])
        for name, value in attr_items:
            parts.append(" " + self._serialize_attribute(name, value, tag))
        if tag in VOID_ELEMENTS and self.use_trailing_solidus:
            parts.append(" /" if self.space_before_trailing_solidus else "/")
        parts.append(">")
        if tag in VOID_ELEMENTS:
            return "".join(parts)
        if self._is_shadow_host(elem):
            shadow = getattr(elem, "shadowRoot", None)
            if shadow is not None:
                parts.append(self._serialize_shadow_root(shadow))
        for child in elem.child_nodes:
            if tag in rcdata_elements and child.node_type == NodeType.TEXT_NODE:
                parts.append(child.data)
            else:
                parts.append(self.serialize_node(child))
        parts.append(f"</{tag}>")
        return "".join(parts)

    def _serialize_attribute(self, name: str, value: str, element_tag: str) -> str:
        if self.minimize_boolean_attributes and (
            value.lower() == name.lower() or
            name in boolean_attributes.get(element_tag.lower(), frozenset()) or
            name in boolean_attributes.get("", frozenset())
        ):
            return name
        escaped = self._escape_attr(value)
        if self.quote_attr_values == "always":
            quote = True
        elif self.quote_attr_values == "spec":
            quote = bool(_quote_attr_spec.search(value))
        elif self.quote_attr_values == "legacy":
            quote = bool(_quote_attr_legacy.search(value))
        else:
            raise ValueError("quote_attr_values must be 'always', 'spec', or 'legacy'")
        if quote:
            qc = self.quote_char
            if self.use_best_quote_char:
                if "'" in value and '"' not in value:
                    qc = '"'
                elif '"' in value and "'" not in value:
                    qc = "'"
            return f'{name}={qc}{escaped}{qc}'
        return f'{name}={escaped}'

    def _escape_attr(self, value: str) -> str:
        v = value.replace("&", "&amp;").replace("\u00A0", "&nbsp;")
        if self.escape_lt_in_attrs:
            v = v.replace("<", "&lt;").replace(">", "&gt;")
        qc = self.quote_char
        if qc == '"':
            v = v.replace('"', "&quot;")
        else:
            v = v.replace("'", "&#39;")
        return v

    def _serialize_text(self, text_node: Text) -> str:
        data = text_node.data
        if self.strip_whitespace:
            data = " ".join(data.split())
        data = data.replace("&", "&amp;").replace("\u00A0", "&nbsp;")
        data = data.replace("<", "&lt;").replace(">", "&gt;")
        if self.resolve_entities:
            res: List[str] = []
            for ch in data:
                if ch in {"&", "<", ">", '"'}:
                    res.append(ch)
                else:
                    ent = lookup_entity_value_py(ch)
                    if ent is not None:
                        if not ent.endswith(";"):
                            ent += ";"
                        res.append("&" + ent)
                    else:
                        res.append(ch)
            data = "".join(res)
        return data

    def _get_tag(self, elem: Element) -> str:
        ns = getattr(elem, "namespace", "http://www.w3.org/1999/xhtml")
        return elem.tag_name.lower() if ns == "http://www.w3.org/1999/xhtml" else elem.tag_name

    def _is_shadow_host(self, elem: Element) -> bool:
        return hasattr(elem, "shadowRoot") and getattr(elem, "shadowRoot") is not None

    def _serialize_shadow_root(self, shadow: ShadowRoot) -> str:
        parts: List[str] = []
        parts.append('<template shadowrootmode="')
        mode = getattr(shadow, "mode", "open")
        parts.append("open" if mode == "open" else "closed")
        parts.append('"')
        if getattr(shadow, "delegatesFocus", False):
            parts.append(' shadowrootdelegatesfocus=""')
        if getattr(shadow, "serializable", False):
            parts.append(' shadowrootserializable=""')
        if getattr(shadow, "clonable", False):
            parts.append(' shadowrootclonable=""')
        parts.append(">")
        for child in shadow.child_nodes:
            parts.append(self.serialize_node(child))
        parts.append("</template>")
        return "".join(parts)

class SerializeError(Exception):
    pass

def serialize(dom_node: Node, encoding: Any = None, **opts: Any) -> str:
    serializer = HTMLSerializer(**opts)
    return serializer.render(dom_node, encoding=encoding)


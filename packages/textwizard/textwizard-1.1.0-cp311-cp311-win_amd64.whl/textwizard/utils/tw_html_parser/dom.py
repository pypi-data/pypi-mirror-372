# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from enum import IntEnum
from typing import Optional, Dict, List, Union
from textwizard.utils.tw_html_parser.tokens import Attribute

class NodeType(IntEnum):
    ELEMENT_NODE = 1
    ATTRIBUTE_NODE = 2
    TEXT_NODE = 3
    COMMENT_NODE = 8
    DOCUMENT_NODE = 9
    DOCUMENT_TYPE_NODE = 10
    SHADOW_ROOT_NODE = 11

class Node:
    __slots__ = (
        "_node_type",
        "_owner_document",
        "_parent",
        "_children",
    )

    def __init__(self, node_type: NodeType, owner_document: 'Document'):
        self._node_type = node_type
        self._owner_document = owner_document
        self._parent: Optional['Node'] = None
        self._children: List['Node'] = []

    @property
    def node_type(self) -> NodeType:
        return self._node_type

    @property
    def owner_document(self) -> 'Document':
        return self._owner_document

    @property
    def parent_node(self) -> Optional['Node']:
        return self._parent

    @property
    def child_nodes(self) -> List['Node']:
        return self._children

    def append_child(self, new_child: 'Node') -> 'Node':
        if new_child._parent is not None:
            new_child._parent.remove_child(new_child)
        new_child._parent = self
        self._children.append(new_child)
        return new_child

    def remove_child(self, old_child: 'Node') -> 'Node':
        if old_child._parent != self:
            raise ValueError("removeChild: old_child is not a child of this node")

        idx = self._children.index(old_child)
        self._children.pop(idx)
        old_child._parent = None
        return old_child

    def insert_before(self, new_child: 'Node', ref_child: Optional['Node']) -> 'Node':
        if ref_child is None:
            return self.append_child(new_child)

        if ref_child._parent != self:
            raise ValueError("insert_before: refChild is not a child of this node")

        if new_child._parent is not None:
            new_child._parent.remove_child(new_child)

        idx = self._children.index(ref_child)
        self._children.insert(idx, new_child)
        new_child._parent = self
        return new_child

    def replace_child(self, new_child: 'Node', old_child: 'Node') -> 'Node':
        self.insert_before(new_child, old_child)
        self.remove_child(old_child)
        return old_child

    def has_child_nodes(self) -> bool:
        return bool(self._children)

    def _descendant_elements_by_id(self, lookup_id: str) -> Optional['Element']:
        for c in self._children:
            if c.node_type == NodeType.ELEMENT_NODE:
                elem = c  # type: Element
                if elem.get_attribute("id") == lookup_id:
                    return elem
                found = c._descendant_elements_by_id(lookup_id)
                if found:
                    return found
        return None


# =============================================================================
# DocumentType
# =============================================================================

class DocumentType(Node):
    __slots__ = ("name", "public_id", "system_id")

    def __init__(self, name: str, public_id: str, system_id: str, owner_document: 'Document'):
        super().__init__(NodeType.DOCUMENT_TYPE_NODE, owner_document)
        self.name = name
        self.public_id = public_id
        self.system_id = system_id

    def __repr__(self):
        return f"<!DOCTYPE {self.name} PUBLIC '{self.public_id}' '{self.system_id}'>"

# =============================================================================
# DocumentFragment
# =============================================================================

class DocumentFragment(Node):
    __slots__ = ()

    def __init__(self, owner_document: 'Document'):
        super().__init__(NodeType.DOCUMENT_NODE, owner_document)

    def __repr__(self):
        return f"<DocumentFragment with {len(self._children)} childNodes>"

# =============================================================================
# Document
# =============================================================================

class Document(Node):
    __slots__ = (
        "_doctype",
        "_document_element",
        "custom_element_definitions",
        "custom_element_reactions_stack",
        "throw_on_dynamic_markup_insertion_counter",
        "microtask_queue",
        "form_element",
        "_quirks_mode",
        "frameset_ok",
    )

    def __init__(self):
        super().__init__(NodeType.DOCUMENT_NODE, owner_document=None)

        self._owner_document = self
        self._doctype: Optional[DocumentType] = None
        self._document_element: Optional['Element'] = None

        self.custom_element_definitions = {}
        self.custom_element_reactions_stack = []
        self.throw_on_dynamic_markup_insertion_counter = 0
        self.microtask_queue = []
        self.form_element = None
        self._quirks_mode: Union[bool, str] = False
        self.frameset_ok = True

    @property
    def doctype(self) -> Optional[DocumentType]:
        return self._doctype

    @doctype.setter
    def doctype(self, val: DocumentType):
        self._doctype = val

    @property
    def document_element(self) -> Optional['Element']:
        return self._document_element

    def set_document_element(self, elem: 'Element'):
        self._document_element = elem

    def create_document_type(self, name: str, public_id: str, system_id: str) -> DocumentType:
        return DocumentType(name, public_id, system_id, self)

    def create_element(self, tag_name: str, namespace: Optional[str] = None) -> 'Element':
        return Element(tag_name, self, namespace)

    def create_text_node(self, data: str) -> 'Text':
        return Text(data, self)

    def create_comment(self, data: str) -> 'Comment':
        return Comment(data, self)

    def create_document_fragment(self) -> DocumentFragment:
        return DocumentFragment(self)

    def get_element_by_id(self, element_id: str) -> Optional['Element']:
        if self._document_element and self._document_element.get_attribute("id") == element_id:
            return self._document_element
        if self._document_element:
            return self._document_element._descendant_elements_by_id(element_id)
        return None

    def perform_microtask_checkpoint(self) -> None:
        while self.microtask_queue:
            task = self.microtask_queue.pop(0)
            try:
                task()
            except Exception as e:
                raise e

    @property
    def quirks_mode(self) -> Union[bool, str]:
        return self._quirks_mode

    @quirks_mode.setter
    def quirks_mode(self, value: Union[bool, str]):
        self._quirks_mode = value

    def __str__(self) -> str:
        return self._to_string_tree()

    def __repr__(self) -> str:
        return self.__str__()

    def _to_string_tree(self, indent: int = 0) -> str:
        spc = "  " * indent
        result = f"{spc}Document:\n"
        for child in self._children:
            result += self._node_to_string(child, indent + 1)
        return result

    def _node_to_string(self, node: Node, indent: int = 0) -> str:
        spc = "  " * indent
        if node.node_type == NodeType.ELEMENT_NODE:
            elem: Element = node  # type: ignore
            s = f"{spc}Element <{elem.tag_name}> (namespace={elem.namespace})\n"
            for child in elem.child_nodes:
                s += self._node_to_string(child, indent + 1)
            return s
        elif node.node_type == NodeType.TEXT_NODE:
            txt = node  # type: Text
            snippet = txt.data.replace("\n", "\\n")
            return f"{spc}Text '{snippet}'\n"
        elif node.node_type == NodeType.COMMENT_NODE:
            cmt = node  # type: Comment
            snippet = cmt.data.replace("\n", "\\n")
            return f"{spc}Comment '{snippet}'\n"
        elif node.node_type == NodeType.DOCUMENT_TYPE_NODE:
            return f"{spc}{node}\n"
        elif node.node_type == NodeType.SHADOW_ROOT_NODE:
            shadow = node  # type: ShadowRoot
            s = f"{spc}ShadowRoot (mode={shadow.mode})\n"
            for child in shadow.child_nodes:
                s += self._node_to_string(child, indent + 1)
            return s
        else:
            return f"{spc}Node type={node.node_type}\n"

# =============================================================================
# Element
# =============================================================================

class Element(Node):
    __slots__ = (
        "_tag_name",
        "_tag_name_lower",
        "_attr_map",
        "namespace",
        "form",
        "parser_inserted",
        "template_contents",
        "is_value",
    )

    def __init__(self, tag_name: str, owner_document: Document, namespace: Optional[str] = None):
        super().__init__(NodeType.ELEMENT_NODE, owner_document)
        self._tag_name = tag_name
        self._tag_name_lower = tag_name.lower()
        self.namespace = namespace or "http://www.w3.org/1999/xhtml"
        self.form = None
        self.parser_inserted = False
        self.template_contents = None
        self.is_value = None

        self._attr_map: Dict[str, Attribute] = {}

    @property
    def tag_name(self) -> str:
        return self._tag_name

    @property
    def tag_name_lower(self) -> str:
        return self._tag_name_lower

    def get_attribute(self, name: str) -> Optional[str]:
        attr = self._attr_map.get(name)
        return attr.value if attr else None

    def set_attribute(self, name: str, value: str, namespace: Optional[str] = None, prefix: Optional[str] = None):
        if name in self._attr_map:
            existing_attr = self._attr_map[name]
            existing_attr.value = value
            existing_attr.namespace = namespace
            existing_attr.prefix = prefix
        else:
            new_attr = Attribute(name=name, value=value, namespace=namespace, prefix=prefix)
            self._attr_map[name] = new_attr

    def remove_attribute(self, name: str):
        self._attr_map.pop(name, None)

    def has_attribute(self, name: str) -> bool:
        return name in self._attr_map

    def get_attributes(self) -> Dict[str, str]:
        return {attr.name: attr.value for attr in self._attr_map.values()}

    def __repr__(self):
        return f"<Element {self._tag_name} at {hex(id(self))} ns={self.namespace}>"

# =============================================================================
# Text
# =============================================================================

class Text(Node):
    __slots__ = ("_data",)

    def __init__(self, data: str, owner_document: Document):
        super().__init__(NodeType.TEXT_NODE, owner_document)
        self._data = data

    @property
    def data(self) -> str:
        return self._data

    @data.setter
    def data(self, val: str):
        self._data = val

    def append_data(self, text: str):
        self._data += text

    def __repr__(self):
        snippet = (self._data[:20] + "...") if len(self._data) > 20 else self._data
        return f"<Text '{snippet}'>"

# =============================================================================
# Comment
# =============================================================================

class Comment(Node):
    __slots__ = ("_data",)

    def __init__(self, data: str, owner_document: Document):
        super().__init__(NodeType.COMMENT_NODE, owner_document)
        self._data = data

    @property
    def data(self) -> str:
        return self._data

    @data.setter
    def data(self, val: str):
        self._data = val

    def __repr__(self):
        snippet = (self._data[:20] + "...") if len(self._data) > 20 else self._data
        return f"<!-- {snippet} -->"

# =============================================================================
# ShadowRoot
# =============================================================================

class ShadowRoot(Node):
    __slots__ = (
        "host",
        "mode",
        "clonable",
        "serializable",
        "delegates_focus",
        "slot_type",
        "declarative",
        "available_to_element_internals",
    )

    def __init__(
        self,
        host: Element,
        mode: str,
        clonable: bool,
        serializable: bool,
        delegates_focus: bool,
        slot_type: str = "named"
    ):
        super().__init__(NodeType.SHADOW_ROOT_NODE, host.owner_document)
        self.host = host
        self.mode = mode
        self.clonable = clonable
        self.serializable = serializable
        self.delegates_focus = delegates_focus
        self.slot_type = slot_type
        self.declarative = False
        self.available_to_element_internals = False

    def append_child(self, new_child: Node) -> Node:
        if new_child._parent is not None:
            new_child._parent.remove_child(new_child)
        new_child._parent = self
        self._children.append(new_child)
        return new_child

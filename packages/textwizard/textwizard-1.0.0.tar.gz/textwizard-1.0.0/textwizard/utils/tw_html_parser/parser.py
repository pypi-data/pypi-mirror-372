# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from textwizard.utils.tw_html_parser.tokenizer import TWHTMLTokenizer,TokenizerState
from textwizard.utils.tw_html_parser.tokens import Token, CHARACTER, START_TAG, END_TAG, COMMENT, DOCTYPE, EOF ,Attribute
from textwizard.utils.tw_html_parser.dom import Document, Element, Text, Comment, Node, NodeType
from textwizard.utils.tw_html_parser._utils import (SVG_ATTRIBUTE_FIXES, MATHML_ATTRIBUTE_FIXES, NAMESPACED_ATTRIBUTE_FIXES, SPECIAL_ELEMENTS, IMPLIED_END_TAGS,
                    NO_OPEN_ELEMENTS, SVG_TAGNAME_FIXES, space_characters, SCOPE_SETS, namespaces, ascii_upper2lower,
                    BREAKOUT_ELEMENTS, html_integration_point_elements, mathml_integration_point_elements, table_insert_text, HEADING_TAGS)
from textwizard.utils.tw_html_parser.error import ParseError
from collections import deque
from typing import Callable, Optional, Union, Any, Dict, List


class InsertionMode:
    INITIAL = "initial"
    BEFORE_HTML = "before_html"
    BEFORE_HEAD = "before_head"
    IN_HEAD = "in_head"
    IN_HEAD_NOSCRIPT = "in_head_noscript"
    AFTER_HEAD = "after_head"
    IN_BODY = "in_body"
    TEXT = "text"
    IN_TABLE = "in_table"
    IN_TABLE_TEXT = "in_table_text"
    IN_CAPTION = "in_caption"
    IN_COLUMN_GROUP = "in_column_group"
    IN_TABLE_BODY = "in_table_body"
    IN_ROW = "in_row"
    IN_CELL = "in_cell"
    IN_SELECT = "in_select"
    IN_SELECT_IN_TABLE = "in_select_in_table"
    AFTER_BODY = "after_body"
    IN_FRAMESET = "in_frameset"
    AFTER_FRAMESET = "after_frameset"
    AFTER_AFTER_BODY = "after_after_body"
    AFTER_AFTER_FRAMESET = "after_after_frameset"
    FOREIGN_CONTENT = "foreign_content"


MARKER = object()

def parse_fragment(doc, container="div", **kwargs):
    parser = TWHTMLParser(doc)
    return parser.parse_fragment(container=container, **kwargs)


class TWHTMLParser:
    __slots__ = (
        "text","parser", "document","process_token", "tokenizer", "open_elements", "insertion_mode",
        "is_fragment_parsing","original_mode", "errors", "head_element", "active_formatting_elements",
        "scripting_enabled", "frameset_ok","fragment_case","context_element",
        "pending_table_character_tokens", "insert_element_token", "_insert_from_table", "first_tag_html",
        "default_name_spaces","_dispatch_cache")


    def __init__(self, text: str):
        self.text: str = text
        self.document: Document = Document()
        self.process_token=self._process_token
        self.document.custom_element_definitions = {}
        self.document.custom_element_reactions_stack = []
        self.document.throw_on_dynamic_markup_insertion_counter = 0
        self.tokenizer = TWHTMLTokenizer(text, parser=self)
        self.open_elements: List[Element] = []
        self.insertion_mode = InsertionMode.INITIAL
        self.is_fragment_parsing = False
        self.original_mode = []
        self.head_element = None
        self.frameset_ok: bool = True
        self.scripting_enabled: bool = False
        self.active_formatting_elements: List[Any] = []
        self.fragment_case = False
        self.context_element = None
        self.first_tag_html=False
        self.insert_element_token = self.insert_element_normal

        self._insert_from_table = False
        self.default_name_spaces=namespaces["html"]

        self.pending_table_character_tokens = []
        self._dispatch_cache = {}
        self.errors = deque()

    def log_error(self, error: Union[ParseError, tuple, str]) -> None:
        if isinstance(error, tuple):
            base_error, custom_message = error
            formatted_message = f"[Error: {base_error.code()}: {base_error.description().format(custom_message)}]"
        elif isinstance(error, ParseError):
            formatted_message = f"[Error: {error.code()}: {error.description()}]"
        elif isinstance(error, str):
            formatted_message = f"[Error: {error}]"
        else:
            raise ValueError("Invalid error type passed to log_error.")
        self.errors.append(formatted_message)

    @property
    def current_node(self) -> Union[Element, Document]:
        return self.open_elements[-1] if self.open_elements else self.document

    def __repr__(self) -> str:
        mode_val = self.insertion_mode.value if self.insertion_mode else "None"
        return f"<HTMLParser mode={mode_val} open_elements={[el.tag_name for el in self.open_elements]}>"

    def parse_fragment(self, container="div", scripting=False, name_spaces=None):
        self.is_fragment_parsing = True
        self.fragment_case = True
        self.context_element = self.document.create_element(container, name_spaces)
        self.document.append_child(self.context_element)
        self.open_elements.append(self.context_element)

        container_lower = container.lower()
        if container_lower in ["title", "textarea"]:
            self.tokenizer.appropriate_end_tag_name = container_lower
            self.tokenizer.state = TokenizerState.RCDATA_STATE
        elif container_lower in ["style", "xmp", "iframe", "noembed", "noframes"]:
            self.tokenizer.appropriate_end_tag_name = container_lower
            self.tokenizer.state = TokenizerState.RAWTEXT_STATE
        elif container_lower == "script":
            self.tokenizer.appropriate_end_tag_name = container_lower
            self.tokenizer.state = TokenizerState.SCRIPT_DATA_STATE
        else:
            self.tokenizer.state = TokenizerState.DATA_STATE

        self.scripting_enabled = scripting
        self.reset_insertion_mode_appropriately()

        token_iter = iter(self.tokenizer)

        while True:
            token = next(token_iter, None)
            if token is None:
                break
            if token.type == CHARACTER and token.data != "\uFFFD":
                parts = [token.data]
                while True:
                    nxt = next(token_iter, None)
                    if nxt is None or nxt.type != CHARACTER:
                        break
                    parts.append(nxt.data)
                token.data = "".join(parts)
            self.process_token(token)

        self.finalize_parsing()

        fragment = self.document.create_document_fragment()
        for child in self.context_element.child_nodes:
            fragment.append_child(child)
        return fragment

    def parse(self) -> Document:
        work_token=self.process_token
        for token in self.tokenizer:
            work_token(token)
        self.finalize_parsing()
        return self.document

    def finalize_parsing(self):
        self.open_elements.clear()
        self.pending_table_character_tokens.clear()

    def _process_token(self, token: Token, override_mode = None):
        effective_mode = override_mode or self.insertion_mode
        open_elements = self.open_elements
        token_type = token.type
        token_name = token.name
        _dispatch_cache = self._dispatch_cache
        if not open_elements:
            mode = effective_mode
        else:
            current = open_elements[-1]
            current_ns = getattr(current, "namespace", "")
            current_tag_lower = current.tag_name_lower if current.tag_name else ""


            is_html_elem = (not hasattr(current, "namespace") or current_ns == namespaces["html"])
            is_mathml_text = ((current_ns, current.tag_name) in mathml_integration_point_elements)

            if (
                    is_html_elem
                    or current_ns == namespaces["html"]
                    or (
                    is_mathml_text
                    and (
                            (token_type == START_TAG and token_name not in ("mglyph", "malignmark"))
                            or token_type == CHARACTER
                    )
            )
                    or (
                    current_ns == namespaces["mathml"]
                    and current_tag_lower == "annotation-xml"
                    and token_type == START_TAG
                    and token_name == "svg"
            )
                    or (
                    self.is_html_integration_point(current)
                    and token_type in (START_TAG, CHARACTER)
            )
            ):
                mode = effective_mode
            else:
                mode = InsertionMode.FOREIGN_CONTENT

        if token_type == CHARACTER:
            cache_key = (mode, token_type, 'space_characters') if token.space_character else (mode, token_type, 'GENERIC')
        elif token_type in (START_TAG, END_TAG):
            cache_key = (mode, token_type, token_name)
        else:
            cache_key = (mode, token_type)

        if cache_key in _dispatch_cache:
            handler = _dispatch_cache[cache_key]
        else:
            dt = PRECOMPUTED_DISPATCH.get(mode)
            handler = dt.lookup(token) if dt else None
            _dispatch_cache[cache_key] = handler

        if handler:
            handler(self, token)
        else:
            self.log_error(f"No handler for token: {token}")

    def get_dispatch_handler(self, token, mode):
        if token.type == CHARACTER:
            if token.space_character:
                cache_key = (mode, token.type, 'space_characters')
            else:
                cache_key = (mode, token.type, 'GENERIC')
        elif token.type in (START_TAG, END_TAG):
            cache_key = (mode, token.type, token.name)
        else:
            cache_key = (mode, token.type)

        if cache_key in self._dispatch_cache:
            return self._dispatch_cache[cache_key]

        dt = PRECOMPUTED_DISPATCH.get(mode)
        if dt:
            handler = dt.lookup(token)
        else:
            handler = None

        self._dispatch_cache[cache_key] = handler
        return handler

    @staticmethod
    def attr_name_is(attr_obj, candidates):
        if not hasattr(attr_obj, "name"):
            return False
        return attr_obj.name.lower() in candidates

    @staticmethod
    def adjust_svg_tag_names(token: Token) -> None:
        name_lower = (token.name or "").lower()
        if name_lower in SVG_TAGNAME_FIXES:
            token.name = SVG_TAGNAME_FIXES[name_lower]

    def reset_insertion_mode_appropriately(self) -> None:
        st = self
        mapping_array = (
            ("select", lambda idx, last: InsertionMode.IN_SELECT_IN_TABLE
            if (not last and any(a.tag_name == "table" for a in st.open_elements[idx - 1::-1] if a.tag_name != "template"))
            else InsertionMode.IN_SELECT),
            ("td", lambda idx, last: InsertionMode.IN_CELL if not last else None),
            ("th", lambda idx, last: InsertionMode.IN_CELL if not last else None),
            ("tr", lambda idx, last: InsertionMode.IN_ROW),
            (("tbody", "thead", "tfoot"), lambda idx, last: InsertionMode.IN_TABLE_BODY),
            ("caption", lambda idx, last: InsertionMode.IN_CAPTION),
            ("colgroup", lambda idx, last: InsertionMode.IN_COLUMN_GROUP),
            ("table", lambda idx, last: InsertionMode.IN_TABLE),
            ("head", lambda idx, last: InsertionMode.IN_HEAD if not last else None),
            ("body", lambda idx, last: InsertionMode.IN_BODY),
            ("frameset", lambda idx, last: InsertionMode.IN_FRAMESET),
            ("html", lambda idx, last: InsertionMode.BEFORE_HEAD if st.head_element is None else InsertionMode.AFTER_HEAD),
        )

        n = len(st.open_elements)
        for idx in range(n - 1, -1, -1):
            last = (idx == 0)
            node = st.open_elements[idx]
            if last and getattr(st, "fragment_case", False) and getattr(st, "context_element", None) is not None:
                node = st.context_element
            for tag, func in mapping_array:
                if isinstance(tag, tuple):
                    if node.tag_name in tag:
                        mode = func(idx, last)
                        if mode is not None:
                            st.insertion_mode = mode
                            return
                else:
                    if node.tag_name == tag:
                        mode = func(idx, last)
                        if mode is not None:
                            st.insertion_mode = mode
                            return
        st.insertion_mode = InsertionMode.IN_BODY

    @staticmethod
    def is_html_integration_point(node: Element) -> bool:
        if (node.tag_name == "annotation-xml" and
                node.namespace == namespaces["mathml"]):
            return (node.has_attribute("encoding") and
                    node.get_attribute("encoding").translate(ascii_upper2lower) in
                    ("text/html", "application/xhtml+xml"))
        else:
            return (node.namespace, node.tag_name) in html_integration_point_elements


    def get_adjusted_insertion_location(self,override_target: Optional[Element] = None,) -> tuple[Union[Element, Document], Optional[Element]]:
        target: Union[Element, Document] = override_target if override_target is not None else self.current_node
        insertion_parent: Union[Element, Document] = target
        reference_node: Optional[Element] = None
        return insertion_parent, reference_node

    def create_element_for_token_in_namespace(self, token: Token, namespace: str, intended_parent: Optional[Element]) -> Element:
        document = self.document
        if intended_parent is not None:
            node_document = intended_parent.owner_document
            if not node_document:
                node_document = document
        else:
            node_document = document

        local_name = (token.name or "")
        is_value = None
        for attr in token.attributes:
            if hasattr(attr, "name") and hasattr(attr, "value"):
                attr_name,attr_value = attr.name, attr.value
            elif isinstance(attr, dict):
                attr_name,attr_value = attr.get("name"), attr.get("value")
            else:
                raise ValueError("Unknown attribute type")

            if attr_name.lower() == "is":
                is_value = attr_value
                break
        definition = node_document.custom_element_definitions.get((namespace, local_name, is_value))

        will_execute_script = (definition is not None) and (not self.is_fragment_parsing)

        if will_execute_script:
            node_document.throw_on_dynamic_markup_insertion_counter += 1
            node_document.perform_microtask_checkpoint()
            node_document.custom_element_reactions_stack.append([])

        element = node_document.create_element(local_name)
        element.namespace = namespace
        element.is_value = is_value

        for attr in token.attributes:
            if hasattr(attr, "name") and hasattr(attr, "value"):
                attr_name,attr_value = attr.name, attr.value
            elif isinstance(attr, dict):
                attr_name,attr_value = attr.get("name"), attr.get("value")
            else:
                raise ValueError("Unknown attribute type")

            if namespace == namespaces["svg"]:
                fixed_name = SVG_ATTRIBUTE_FIXES.get(attr_name.lower(), attr_name)
                element.set_attribute(fixed_name, attr_value)
            else:
                element.set_attribute(attr_name, attr_value)

            if attr_name in NAMESPACED_ATTRIBUTE_FIXES:
                prefix, local, ns_for_attr = NAMESPACED_ATTRIBUTE_FIXES[attr_name]
                element.set_attribute(f"{prefix}:{local}", attr_value)

        if will_execute_script:
            reaction_queue = node_document.custom_element_reactions_stack.pop()
            for reaction in reaction_queue:
                reaction()
            node_document.throw_on_dynamic_markup_insertion_counter -= 1

        if element.has_attribute("xmlns"):
            xmlns_val = element.get_attribute("xmlns")
            if xmlns_val and xmlns_val != namespace:
                self.log_error(ParseError.custom_error(f"xmlns attribute mismatch: expected {namespace}, got {xmlns_val}"))
        if element.has_attribute("xmlns:xlink"):
            xlink_val = element.get_attribute("xmlns:xlink")
            if xlink_val and xlink_val != namespaces["xlink"]:
                self.log_error(ParseError.custom_error("xmlns:xlink attribute value incorrect"))

        if hasattr(element, "reset"):
            element.reset()

        form_associated_tags = {"input", "button", "select", "textarea", "keygen", "output", "progress", "meter"}

        if ((element.tag_name not in form_associated_tags) or element.has_attribute("form") or
                not hasattr(document, "form_element") or document.form_element is None):
            pass
        elif any(el.tag_name == "template" for el in self.open_elements):
            pass
        else:
            element.form = document.form_element
            element.parser_inserted = True

        return element

    def insert_and_change_state_tokenizer(self, token: Token, new_state, appropriate_end_tag_name, insertion_mode=InsertionMode.TEXT) -> None:
        self.insert_element_token(token)
        self.tokenizer.state = new_state
        self.tokenizer.appropriate_end_tag_name=appropriate_end_tag_name

        self.tokenizer._reconsume_current_input = True
        if not self.original_mode:
            self.original_mode.append(self.insertion_mode)

        self.insertion_mode = insertion_mode

    def restore_original_insertion_mode(self):
        restore = self.original_mode[0]
        self.original_mode.clear()
        return restore

    def generate_implied_end_tags(self, exclude: Optional[str] = None) -> None:
        open_elements= self.open_elements
        while open_elements:
            top_name = open_elements[-1].tag_name
            if top_name in IMPLIED_END_TAGS and top_name != exclude:
                self.open_elements.pop()
            else:
                break

    @property
    def insert_from_table(self) -> bool:
        return self._insert_from_table

    @insert_from_table.setter
    def insert_from_table(self, value: bool):
        self._insert_from_table = value
        if value:
            self.insert_element_token = self.insert_element_table
        else:
            self.insert_element_token = self.insert_element_normal

    def insert_element_table(self, token: Token,name_spaces=None) -> Element:
        open_elements = self.open_elements
        if name_spaces is None:
            name_spaces = self.default_name_spaces

        element = self.create_element_for_token_in_namespace(token, name_spaces, intended_parent=None)

        if open_elements[-1].tag_name_lower not in (
                "table", "tbody", "tfoot", "thead", "tr"
        ):
            return self.insert_element_normal(token)
        else:
            parent, insert_before = self.get_table_misnested_node_position()
            if insert_before is None:
                parent.append_child(element)
            else:
                parent.insert_before(element, insert_before)
            self.open_elements.append(element)
        return element

    def get_table_misnested_node_position(self) -> tuple[Union[Element, Document], Optional[Element]]:
        open_elements = self.open_elements
        last_table: Optional[Element] = None
        insert_before: Optional[Element] = None
        for el in open_elements[::-1]:
            if el.tag_name_lower == "table":
                last_table = el
                break
        if last_table:
            if getattr(last_table, "parent_node", None):
                foster_parent = last_table.parent_node
                insert_before = last_table
            else:
                idx = open_elements.index(last_table)
                foster_parent = open_elements[idx - 1] if idx > 0 else open_elements[0]
        else:
            foster_parent = open_elements[0] if open_elements else None

        return foster_parent, insert_before

    def insert_element_normal(self, token: Token,name_spaces=None) -> Element:
        open_elements = self.open_elements
        document = self.document
        if name_spaces is None:
            name_spaces = self.default_name_spaces
        element = self.create_element_for_token_in_namespace(token, name_spaces, intended_parent=None)

        parent = open_elements[-1] if open_elements else document
        parent.append_child(element)
        self.open_elements.append(element)
        return element

    def insert_text(self, data: str, override_target: Optional[Element] = None) -> None:
        text_node = self.document.create_text_node(data)
        parent_node = override_target if override_target is not None else (self.open_elements[-1] if self.open_elements else self.document)

        if (not self.insert_from_table or
                (self.insert_from_table and parent_node.tag_name_lower not in table_insert_text)):
            parent_node.append_child(text_node)
        else:
            foster_parent, insert_before = self.get_table_misnested_node_position()
            if insert_before is not None:
                foster_parent.insert_before(text_node, insert_before)
            else:
                foster_parent.append_child(text_node)

    def insert_character(self, data: str, override_target: Optional[Element] = None) -> None:
        parent_node, ref_node = self.get_adjusted_insertion_location(override_target)
        if parent_node.node_type == NodeType.DOCUMENT_NODE:
            return

        if parent_node.child_nodes:
            last_child = parent_node.child_nodes[-1]
            if last_child.node_type == NodeType.TEXT_NODE and hasattr(last_child, "data"):
                last_child.data += data
                return

        text_node: Text = self.document.create_text_node(data)

        if ref_node is not None:
            parent_node.insert_before(text_node, ref_node)
        else:
            parent_node.append_child(text_node)


    @staticmethod
    def adjust_attributes(token: Token, replacements: dict) -> None:
        new_attributes = []
        for attr in token.attributes:
            key = attr.name.lower()
            if key in replacements:
                replacement = replacements[key]
                if isinstance(replacement, tuple):
                    new_prefix, new_local_name, new_namespace = replacement
                    new_attributes.append(
                        Attribute(
                            name=new_local_name,
                            value=attr.value,
                            prefix=new_prefix,
                            namespace=new_namespace
                        )
                    )
                else:
                    new_attributes.append(
                        Attribute(
                            name=replacements[key],
                            value=attr.value,
                            prefix=attr.prefix,
                            namespace=attr.namespace
                        )
                    )
            else:
                new_attributes.append(attr)
        token.attributes = new_attributes


    def reconstruct_active_formatting_elements(self) -> None:
        open_elements = self.open_elements

        active_formatting_elements = self.active_formatting_elements
        if not active_formatting_elements:
            return

        i = len(active_formatting_elements) - 1
        entry = active_formatting_elements[i]
        if entry == MARKER or entry in open_elements:
            return

        while entry != MARKER and entry not in open_elements:
            if i == 0:
                i = -1
                break
            i -= 1
            entry = active_formatting_elements[i]

        while True:
            i += 1
            entry = active_formatting_elements[i]
            clone = self.clone_formatting_element(entry)
            token = Token(START_TAG, clone.tag_name)
            token.attributes = [{"name": k, "value": v} for k, v in clone.get_attributes().items()]
            inserted_element = self.insert_element_token(token)
            active_formatting_elements[i] = inserted_element
            if inserted_element == active_formatting_elements[-1]:
                break


    def add_formatting_element(self, token: Token) -> None:
        self.insert_element_token(token)
        element = self.open_elements[-1]
        matching = []
        for node in self.active_formatting_elements[::-1]:
            if node is MARKER:
                break
            elif (node.tag_name_lower == element.tag_name_lower and
                  node.namespace == element.namespace and
                  node.get_attributes() == element.get_attributes()):
                matching.append(node)

        if len(matching) == 3:
            self.active_formatting_elements.remove(matching[-1])
        self.active_formatting_elements.append(element)

    def clone_formatting_element(self, element: Element) -> Element:
        new_element = self.document.create_element(element.tag_name)
        new_element.namespace = element.namespace
        for attr_name, attr_value in element.get_attributes().items():
            new_element.set_attribute(attr_name, attr_value)
        return new_element

    def close_p_element(self) -> None:
        open_elements = self.open_elements
        self.generate_implied_end_tags(exclude="p")
        if self.current_node.tag_name_lower != "p":
            self.log_error("Parse error: expected current node to be <p> when closing a <p> element.")
        while open_elements:
            popped = self.open_elements.pop()
            if popped.tag_name_lower == "p":
                break

    def has_element_in_scope(self, target: str, scope_type: str = "default") -> bool:
        scope_set, invert = SCOPE_SETS[scope_type]
        for node in reversed(self.open_elements):
            if node.tag_name_lower == target:
                return True
            in_set = (node.tag_name in scope_set)
            if invert ^ in_set:
                return False
        return False

    def find_last_active_formatting_element(self, subject: str) -> Optional[Element]:
        for item in self.active_formatting_elements[::-1]:
            if item == MARKER:
                break
            if item.tag_name_lower == subject:
                return item
        return None

    def clear_active_formatting_elements_up_to_marker(self) -> None:
        while self.active_formatting_elements:
            entry = self.active_formatting_elements.pop()
            if entry is MARKER:
                break

    def clear_stack_back_to_table_body_context(self) -> None:
        while self.open_elements[-1].tag_name not in ("tbody", "tfoot", "thead", "html"):
            self.open_elements.pop()

    def clear_stack_back_to_table_row_context(self) -> None:
        open_elements=self.open_elements
        while open_elements[-1].tag_name_lower not in ("tr", "html"):
            self.log_error(f"Parse error: unexpected implied end tag in table row.{open_elements[-1].tag_name}")
            self.open_elements.pop()

    def close_the_cell(self) -> None:
        open_elements = self.open_elements
        self.generate_implied_end_tags()
        if self.current_node.tag_name_lower not in ("td", "th"):
            self.log_error("Parse error: current node not <td> or <th> at close_the_cell.")
        while open_elements:
            popped = self.open_elements.pop()
            if popped.tag_name_lower in ("td", "th"):
                break
        self.clear_active_formatting_elements_up_to_marker()
        self.insertion_mode = InsertionMode.IN_ROW


##############################################################################
# DISPATCH HANDLERS
##############################################################################

# -----------------------------------------------------------------------------
# Generic Handlers
# -----------------------------------------------------------------------------

def ignore_handler(parser: "TWHTMLParser", token: Token) -> None:
    pass

def parse_error_ignore_token(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error(f"Error - ignore token: {token}")

def insert_comment(parser: "TWHTMLParser", token: Token) -> None:
    data: str = token.data
    insertion_parent, insertion_reference = parser.get_adjusted_insertion_location()
    comment_node: Comment = parser.document.create_comment(data)
    insertion_parent.append_child(comment_node)

def handle_insert_character(parser: "TWHTMLParser", token: Token) -> None:
    token.data = token.data.replace("\u0000", "").replace("\uFFFD", "")
    parser.insert_character(token.data)

def handle_reproces_token(parser: "TWHTMLParser", token: Token, override_mode) -> None:
    parser.process_token(token, override_mode=override_mode)

def handle_start_tag_htlm(parser: "TWHTMLParser", token: Token) -> None:
    if not parser.first_tag_html and token.name=="html":
        parser.log_error("Unexpected <html> start tag in in-body ")
    for attr in token.attributes:
        if not parser.open_elements[0].get_attribute(attr.name):
            parser.open_elements[0].set_attribute(attr.name, attr.value)
    parser.first_tag_html=False


# ---------------------------
# --- INITIAL
# ---------------------------

def determine_quirks_mode(token: Token) -> str:
    if getattr(token, "force_quirks", False):
        return "quirks"

    name = token.lower_name
    public_id = (token.public_id or "").strip()
    system_id = (token.system_id or "").strip()

    if name != "html" or public_id != "" or (system_id != "" and system_id.lower() != "about:legacy-compat"):
        quirks_exact = {
            "-//W3O//DTD W3 HTML Strict 3.0//EN//",
            "-/W3C/DTD HTML 4.0 Transitional/EN",
            "html"
        }
        if public_id in quirks_exact:
            return "quirks"
        quirks_prefixes = [
            "+//Silmaril//dtd html Pro v0r11 19970101//",
            "-//AS//DTD HTML 3.0 asWedit + extensions//",
            "-//AdvaSoft Ltd//DTD HTML 3.0 asWedit + extensions//",
            "-//IETF//DTD HTML 2.0 Level 1//",
            "-//IETF//DTD HTML 2.0 Level 2//",
            "-//IETF//DTD HTML 2.0 Strict Level 1//",
            "-//IETF//DTD HTML 2.0 Strict Level 2//",
            "-//IETF//DTD HTML 2.0 Strict//",
            "-//IETF//DTD HTML 2.0//",
            "-//IETF//DTD HTML 2.1E//",
            "-//IETF//DTD HTML 3.0//",
            "-//IETF//DTD HTML 3.2 Final//",
            "-//IETF//DTD HTML 3.2//",
            "-//IETF//DTD HTML 3//",
            "-//IETF//DTD HTML Level 0//",
            "-//IETF//DTD HTML Level 1//",
            "-//IETF//DTD HTML Level 2//",
            "-//IETF//DTD HTML Level 3//",
            "-//IETF//DTD HTML Strict Level 0//",
            "-//IETF//DTD HTML Strict Level 1//",
            "-//IETF//DTD HTML Strict Level 2//",
            "-//IETF//DTD HTML Strict Level 3//",
            "-//IETF//DTD HTML Strict//",
            "-//IETF//DTD HTML//",
            "-//Metrius//DTD Metrius Presentational//",
            "-//Microsoft//DTD Internet Explorer 2.0 HTML Strict//",
            "-//Microsoft//DTD Internet Explorer 2.0 HTML//",
            "-//Microsoft//DTD Internet Explorer 2.0 Tables//",
            "-//Microsoft//DTD Internet Explorer 3.0 HTML Strict//",
            "-//Microsoft//DTD Internet Explorer 3.0 HTML//",
            "-//Microsoft//DTD Internet Explorer 3.0 Tables//",
            "-//Netscape Comm. Corp.//DTD HTML//",
            "-//Netscape Comm. Corp.//DTD Strict HTML//",
            "-//O'Reilly and Associates//DTD HTML 2.0//",
            "-//O'Reilly and Associates//DTD HTML Extended 1.0//",
            "-//O'Reilly and Associates//DTD HTML Extended Relaxed 1.0//",
            "-//SQ//DTD HTML 2.0 HoTMetaL + extensions//",
            "-//SoftQuad Software//DTD HoTMetaL PRO 6.0::19990601::extensions to HTML 4.0//",
            "-//SoftQuad//DTD HoTMetaL PRO 4.0::19971010::extensions to HTML 4.0//",
            "-//Spyglass//DTD HTML 2.0 Extended//",
            "-//Sun Microsystems Corp.//DTD HotJava HTML//",
            "-//Sun Microsystems Corp.//DTD HotJava Strict HTML//",
            "-//W3C//DTD HTML 3 1995-03-24//",
            "-//W3C//DTD HTML 3.2 Draft//",
            "-//W3C//DTD HTML 3.2 Final//",
            "-//W3C//DTD HTML 3.2//",
            "-//W3C//DTD HTML 3.2S Draft//",
            "-//W3C//DTD HTML 4.0 Frameset//",
            "-//W3C//DTD HTML 4.0 Transitional//",
            "-//W3C//DTD HTML Experimental 19960712//",
            "-//W3C//DTD HTML Experimental 970421//",
            "-//W3C//DTD W3 HTML//",
            "-//W3O//DTD W3 HTML 3.0//",
            "-//WebTechs//DTD Mozilla HTML 2.0//",
            "-//WebTechs//DTD Mozilla HTML//"
        ]
        for prefix in quirks_prefixes:
            if public_id.lower().startswith(prefix.lower()):
                return "quirks"

        limited_quirks_prefixes = [
            "-//W3C//DTD XHTML 1.0 Frameset//",
            "-//W3C//DTD XHTML 1.0 Transitional//"
        ]
        if public_id != "":
            for prefix in limited_quirks_prefixes:
                if public_id.lower().startswith(prefix.lower()):
                    return "limited"
        if system_id != "" and (public_id.lower().startswith("-//W3C//DTD HTML 4.01 Frameset//") or
                                 public_id.lower().startswith("-//W3C//DTD HTML 4.01 Transitional//")):
            return "limited"

        return "quirks"
    return "no"

def handle_initial_doctype(parser: "TWHTMLParser", token: Token) -> None:
    public_id = (token.public_id or "").strip()
    system_id = (token.system_id or "").strip()

    doctype_node = parser.document.create_document_type(token.name if token.name else "", public_id, system_id)
    parser.document.append_child(doctype_node)
    parser.document.doctype = doctype_node

    mode = determine_quirks_mode(token)
    if not getattr(parser, "iframe_srcdoc", False) and not getattr(parser, "cannot_change_mode_flag", False):
        if mode == "quirks":
            parser.document.quirks_mode = True
        elif mode == "limited":
            parser.document.quirks_mode = "limited"
        else:
            parser.document.quirks_mode = False

    parser.insertion_mode = InsertionMode.BEFORE_HTML

def handle_initial_fallback(parser: "TWHTMLParser", token: Token) -> None:
    if not getattr(parser, "iframe_srcdoc", False) and not getattr(parser, "cannot_change_mode_flag", False):
        parser.document.quirks_mode = True
    parser.insertion_mode = InsertionMode.BEFORE_HTML
    parser.process_token(token)

# ---------------------------
# BEFORE_HTML
# ---------------------------

def handle_before_html_html(parser: "TWHTMLParser", token: Token) -> None:
    synthetic_head_token = Token(START_TAG, "html", attributes=[])
    parser.insert_element_token(synthetic_head_token)
    parser.insertion_mode = InsertionMode.BEFORE_HEAD
    parser.first_tag_html=True
    parser.process_token(token)

def handle_before_html_fallback(parser: "TWHTMLParser", token: Token) -> None:
    synthetic_head_token = Token(START_TAG, "html", attributes=[])
    parser.insert_element_token(synthetic_head_token)
    parser.insertion_mode = InsertionMode.BEFORE_HEAD
    parser.process_token(token)

# ---------------------------
# --- BEFORE_HEAD
# ---------------------------

def handle_before_head_head(parser: "TWHTMLParser", token: Token) -> None:
    head_elem = parser.insert_element_token(token)
    parser.head_element = head_elem
    parser.insertion_mode = InsertionMode.IN_HEAD

def handle_before_head_anything_else(parser: "TWHTMLParser", token: Token) -> None:
    synthetic_head_token = Token(START_TAG, "head", attributes=[])
    head_elem = parser.insert_element_token(synthetic_head_token)
    parser.head_element = head_elem
    parser.insertion_mode = InsertionMode.IN_HEAD
    parser.process_token(token)

# ---------------------------
# --- IN_HEAD
# ---------------------------

def handle_in_head_base(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_element_token(token)
    if parser.open_elements:
        parser.open_elements.pop()
    if not getattr(token, "self_closing", False):
        token.acknowledge_self_closing()

def handle_in_head_meta(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_element_token(token)
    if parser.open_elements:
        parser.open_elements.pop()
    token.acknowledge_self_closing()

def handle_in_head_title(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.RCDATA_STATE, appropriate_end_tag_name="title")

def handle_in_head_noframes_style(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.RAWTEXT_STATE, appropriate_end_tag_name=("noframes", "style"))

def handle_in_head_noscript_enabled(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.RCDATA_STATE, appropriate_end_tag_name="noscript")

def handle_in_head_noscript_disabled(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_element_token(token)
    parser.insertion_mode = InsertionMode.IN_HEAD_NOSCRIPT

def handle_in_head_script(parser: "TWHTMLParser", token: Token) -> None:
    parser.get_adjusted_insertion_location()
    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.SCRIPT_DATA_STATE, appropriate_end_tag_name="script")

def handle_in_head_end_tag_head(parser: "TWHTMLParser", token: Token) -> None:
    if parser.open_elements and parser.current_node.tag_name_lower == "head":
        parser.open_elements.pop()
    else:
        parser.log_error(ParseError.custom_error("End tag </head> encountered but current node is not <head>"))
    parser.insertion_mode = InsertionMode.AFTER_HEAD

def handle_in_head_end_tag_body_html_br(parser: "TWHTMLParser", token: Token) -> None:
    if parser.open_elements and parser.current_node.tag_name_lower == "head":
        parser.open_elements.pop()
    parser.insertion_mode = InsertionMode.AFTER_HEAD
    parser.process_token(token)

def handle_in_head_anything_else(parser: "TWHTMLParser", token: Token) -> None:
    if parser.open_elements and parser.current_node.tag_name_lower == "head":
        parser.open_elements.pop()
    parser.insertion_mode = InsertionMode.AFTER_HEAD
    parser.process_token(token)

# ---------------------------
# --- IN_HEAD_NOSCRIPT
# ---------------------------

def handle_in_head_noscript_endtag_noscript(parser: "TWHTMLParser", token: Token) -> None:
    parser.open_elements.pop()
    parser.insertion_mode = InsertionMode.IN_HEAD

def handle_in_head_noscript_anything_else(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error(ParseError.custom_error("Unexpected token in IN_HEAD_NOSCRIPT mode."))
    if parser.open_elements and parser.current_node.tag_name_lower == "noscript":
        parser.open_elements.pop()
    parser.insertion_mode = InsertionMode.IN_HEAD
    parser.process_token(token)

# ---------------------------
# --- AFTER_HEAD
# ---------------------------

def handle_after_head_body(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_element_token(token)
    parser.frameset_ok = False
    parser.insertion_mode = InsertionMode.IN_BODY

def handle_after_head_frameset(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_element_token(token)
    parser.insertion_mode = InsertionMode.IN_FRAMESET

def handle_after_head_in_head_tags(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error(ParseError.custom_error(f"Unexpected start tag <{token.name}> in after head mode; token ignored."))
    if parser.head_element is None:
        parser.log_error("No head element present in after head mode; cannot push head element.")
        return
    parser.open_elements.append(parser.head_element)
    parser.process_token(token, override_mode=InsertionMode.IN_HEAD)
    if parser.head_element in parser.open_elements:
        parser.open_elements.remove(parser.head_element)

def handle_after_head_anything_else(parser: "TWHTMLParser", token: Token) -> None:
    synthetic_token = Token(START_TAG, name="body", attributes=[])
    parser.insert_element_token(synthetic_token)
    parser.frameset_ok = True
    parser.insertion_mode = InsertionMode.IN_BODY
    parser.process_token(token)

# ---------------------------
# --- IN_BODY
# ---------------------------

def adoption_agency_algorithm(parser: "TWHTMLParser", token: Token) -> None:
    token_name_lower = token.lower_name
    counter = 0

    # STEP 1-3:
    while counter < 8:
        counter += 1

        # STEP 4:
        formatting_element = parser.find_last_active_formatting_element(token_name_lower)
        if (formatting_element is None or
                (formatting_element in parser.open_elements and
                 not parser.has_element_in_scope(token_name_lower, "default"))):
            handle_in_body_any_other_end_tag(parser, token)
            return

        # STEP 4.2:
        if formatting_element not in parser.open_elements:
            parser.log_error("Adoption Agency: formatting element not in open elements.")
            parser.active_formatting_elements.remove(formatting_element)
            return

        # STEP 4.3:
        if formatting_element != parser.current_node:
            parser.log_error(f"Adoption Agency parse error: formatting element is not current node: </{token_name_lower}>")

        # STEP 5:
        afe_index = parser.open_elements.index(formatting_element)

        furthest_block = None
        for element in parser.open_elements[afe_index:]:
            if element.tag_name_lower in SPECIAL_ELEMENTS and (element.namespace == namespaces["html"] or (element.tag_name_lower == "foreignobject")) :
                furthest_block = element
                break

        # STEP 6:
        if furthest_block is None:
            popped = parser.open_elements.pop()
            while popped != formatting_element:
                popped = parser.open_elements.pop()
            parser.active_formatting_elements.remove(popped)
            return

        # STEP 7:
        common_ancestor = parser.open_elements[afe_index - 1] if afe_index > 0 else None

        # STEP 8:
        try:
            bookmark = parser.active_formatting_elements.index(formatting_element)
        except ValueError:
            parser.log_error("Adoption Agency: formatting element not found in active formatting_elements.")
            return

        # STEP 9:
        last_node = node = furthest_block
        inner_loop_counter = 0
        index = parser.open_elements.index(furthest_block)
        while inner_loop_counter < 3:
            inner_loop_counter += 1
            index -= 1
            if index < 0:
                break
            node = parser.open_elements[index]
            if node not in parser.active_formatting_elements:
                parser.open_elements.remove(node)
                continue
            if node == formatting_element:
                break
            if last_node == furthest_block:
                try:
                    bookmark = parser.active_formatting_elements.index(node) + 1
                except ValueError:
                    pass

            # STEP 9.8:
            clone = parser.clone_formatting_element(node)
            try:
                idx_afe = parser.active_formatting_elements.index(node)
                parser.active_formatting_elements[idx_afe] = clone
            except ValueError:
                pass
            try:
                idx_open = parser.open_elements.index(node)
                parser.open_elements[idx_open] = clone
            except ValueError:
                pass
            node = clone
            # STEP 9.9:
            if last_node.parent_node:
                last_node.parent_node.remove_child(last_node)
            node.append_child(last_node)
            last_node = node

        # STEP 10:
        if last_node.parent_node:
            last_node.parent_node.remove_child(last_node)

        if common_ancestor and common_ancestor.tag_name_lower in ("table", "tbody", "tfoot", "thead", "tr"):
            parent, insert_before = parser.get_table_misnested_node_position()
            if insert_before is None:
                parent.append_child(last_node)
            else:
                parent.insert_before(last_node, insert_before)
        elif common_ancestor:
            common_ancestor.append_child(last_node)
        else:
            insertion_parent, ref_node = parser.get_adjusted_insertion_location()
            insertion_parent.append_child(last_node)

        # STEP 11-13:
        new_clone = parser.clone_formatting_element(formatting_element)
        while furthest_block.child_nodes:
            child = furthest_block.child_nodes[0]
            furthest_block.remove_child(child)
            new_clone.append_child(child)
        furthest_block.append_child(new_clone)

        # STEP 14:
        try:
            parser.active_formatting_elements.remove(formatting_element)
        except ValueError:
            pass
        parser.active_formatting_elements.insert(bookmark, new_clone)

        # STEP 15:
        try:
            parser.open_elements.remove(formatting_element)
        except ValueError:
            pass
        try:
            idx_fb = parser.open_elements.index(furthest_block)
            parser.open_elements.insert(idx_fb + 1, new_clone)
        except ValueError:
            pass

def handle_in_body_whitespace(parser: "TWHTMLParser", token: Token) -> None:
    parser.reconstruct_active_formatting_elements()
    parser.insert_character(token.data)

def handle_in_body_other_character(parser: "TWHTMLParser", token: Token) -> None:
    if token.null_character:
        parser.log_error(f"Error: {token}")
    else:
        token.data = token.data.replace("\u0000", "")
        parser.reconstruct_active_formatting_elements()

        parser.insert_text(token.data)
        if (parser.frameset_ok and
            any([char not in space_characters
                 for char in token.data])):
            parser.frameset_ok = False


def handle_in_body_body(parser: "TWHTMLParser", token: Token) -> None:
    if (len(parser.open_elements) <= 1 or
            parser.open_elements[1].tag_name_lower != "body" or
            any(el.tag_name_lower == "template" for el in parser.open_elements)):

        synthetic_body = Token(START_TAG, name="body", attributes=[])
        parser.insert_element_token(synthetic_body)
        parser.insertion_mode = InsertionMode.IN_BODY
    else:
        parser.frameset_ok = False
        body_elem = parser.open_elements[1]
        for attr in token.attributes:
            if not body_elem.has_attribute(attr.name):
                body_elem.set_attribute(attr.name, attr.value)

def handle_in_body_frameset(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error("Unexpected <frameset> start tag in IN_BODY insertion mode.")
    if len(parser.open_elements) == 1 or parser.open_elements[1].tag_name_lower != "body":
        return
    if not parser.frameset_ok:
        return
    body_elem = parser.open_elements[1]
    if hasattr(body_elem, "parent_node") and body_elem.parent_node is not None:
        body_elem.parent_node.remove_child(body_elem)
    while len(parser.open_elements) > 1:
        parser.open_elements.pop()
    parser.insert_element_token(token)
    parser.insertion_mode = InsertionMode.IN_FRAMESET

def handle_in_body_eof(parser: "TWHTMLParser", token: Token) -> None:
    for el in parser.open_elements:
        if el.tag_name_lower not in NO_OPEN_ELEMENTS:
            parser.log_error("Parse error at EOF: unexpected node in open elements.")
            break

def handle_in_body_endtag_body(parser: "TWHTMLParser", token: Token) -> None:
    if not any(el.tag_name_lower == "body" for el in parser.open_elements):
        parser.log_error("Unexpected </body> end tag in IN_BODY insertion mode; no body element in scope.")
        return
    for el in parser.open_elements:
        if el.tag_name_lower not in NO_OPEN_ELEMENTS:
            parser.log_error("Parse error: unexpected node in open elements when processing </body>.")
            break
    parser.insertion_mode = InsertionMode.AFTER_BODY

def handle_in_body_endtag_html(parser: "TWHTMLParser", token: Token) -> None:
    if not any(el.tag_name_lower == "body" for el in parser.open_elements):
        parser.log_error("Unexpected </html> end tag in IN_BODY insertion mode; no body element in scope.")
        return
    for el in parser.open_elements:
        if el.tag_name_lower not in NO_OPEN_ELEMENTS:
            parser.log_error("Parse error: unexpected node in open elements when processing </html>.")
            break
    parser.insertion_mode = InsertionMode.AFTER_BODY
    parser.process_token(token)

def handle_in_body_generic_container(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope("p", "button"):
        parser.close_p_element()
    parser.insert_element_token(token)

def handle_in_body_heading(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope("p", "button"):
        parser.close_p_element()

    if parser.open_elements[-1].tag_name_lower in HEADING_TAGS:
        parser.log_error("Parse error: nested heading; popping current heading element.")
        parser.open_elements.pop()
    parser.insert_element_token(token)

def handle_in_body_pre_listing(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope("p", "button"):
        parser.close_p_element()
    parser.insert_element_token(token)
    parser.frameset_ok = False
    data = token.data

    parser.reconstruct_active_formatting_elements()

    if data.startswith("\n") and parser.open_elements[-1].tag_name_lower in ("pre", "listing", "textarea"):
        data = data[1:]
    if data:
        parser.reconstruct_active_formatting_elements()
        parser.insert_text(data)

def handle_in_body_form(parser: "TWHTMLParser", token: Token) -> None:
    if parser.document.form_element is not None and not any(el.tag_name_lower == "template" for el in parser.open_elements):
        parser.log_error("Parse error: form element already exists and no template element present; ignoring <form> token.")
        return
    if parser.has_element_in_scope("p", "button"):
        parser.close_p_element()

    new_form = parser.insert_element_token(token)
    if not any(el.tag_name_lower == "template" for el in parser.open_elements):
        parser.document.form_element = new_form

def handle_in_body_dd_dt_li(parser: "TWHTMLParser", token: Token) -> None:
    parser.frameset_ok = False
    incoming_tag = token.lower_name
    closing_candidates = {"li": ["li"],
                            "dt": ["dt", "dd"],
                            "dd": ["dt", "dd"]}

    to_close = closing_candidates.get(incoming_tag)
    for node in reversed(parser.open_elements):
        tag = node.tag_name_lower
        if tag in to_close:
            synthetic_token = Token(END_TAG, name=node.tag_name)
            parser.process_token(synthetic_token, override_mode=InsertionMode.IN_BODY)
            break

        if tag in SPECIAL_ELEMENTS and tag not in {"address", "div", "p"}:
            break

    if parser.has_element_in_scope("p", "button"):
        synthetic_token = Token(END_TAG, "p")
        parser.process_token(synthetic_token, override_mode=InsertionMode.IN_BODY)

    parser.insert_element_token(token)

def handle_in_body_plaintext(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope("p", "button"):
        synthetic_token = Token(END_TAG, name="p")
        handle_in_body_endtag_p(parser,synthetic_token)

    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.PLAINTEXT_STATE, appropriate_end_tag_name="plaintext", insertion_mode=parser.insertion_mode)

def handle_in_body_button(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope("button", "button"):
        parser.log_error("Parse error: <button> element already in scope.")
        parser.generate_implied_end_tags()
        while parser.open_elements:
            popped = parser.open_elements.pop()
            if popped.tag_name_lower == "button":
                break
    parser.reconstruct_active_formatting_elements()
    parser.insert_element_token(token)
    parser.frameset_ok = False

def handle_in_body_generic_end(parser: "TWHTMLParser", token: Token) -> None:
    tag = token.lower_name
    in_scope= parser.has_element_in_scope(tag, "default")
    if in_scope:
        parser.generate_implied_end_tags(exclude=tag)
    if parser.current_node.tag_name_lower != tag:
        parser.log_error(f"Parse error: current node is not <{tag}> when processing end tag.")
    if in_scope:
        popped = parser.open_elements.pop()
        while popped.tag_name_lower != tag:
            popped = parser.open_elements.pop()

def handle_in_body_endtag_form(parser: "TWHTMLParser", token: Token) -> None:
    has_template = any(el.tag_name_lower == "template" for el in parser.open_elements)
    if not has_template:
        node = parser.document.form_element
        parser.document.form_element = None
        if node is None or not parser.has_element_in_scope(node.tag_name, "default"):
            parser.log_error("Parse error: form element pointer is null or not in scope; ignoring </form> token.")
            return
        parser.generate_implied_end_tags()
        if parser.current_node != node:
            parser.log_error("Parse error: current node is not the form element when processing </form>.")
        if node in parser.open_elements:
            parser.open_elements.remove(node)
    else:
        if not parser.has_element_in_scope("form", "default"):
            parser.log_error("Parse error: no <form> element in scope (template case); ignoring </form> token.")
            return
        parser.generate_implied_end_tags()
        if parser.current_node.tag_name_lower != "form":
            parser.log_error("Parse error: current node is not <form> when processing </form> (template case).")
        while parser.open_elements:
            popped = parser.open_elements.pop()
            if popped.tag_name_lower == "form":
                break

def handle_in_body_endtag_p(parser: "TWHTMLParser", token: Token) -> None:
    if not parser.has_element_in_scope("p", "button"):
        parser.log_error("Parse error: no <p> element in button scope when processing </p>; inserting a synthetic <p>.")
        synthetic_token = Token(START_TAG, name="p", attributes=[])
        parser.insert_element_token(synthetic_token)
    parser.close_p_element()

def handle_in_body_endtag_li(parser: "TWHTMLParser", token: Token) -> None:
    if not parser.has_element_in_scope("li", "list_item"):
        parser.log_error("Parse error: no <li> element in list item scope; ignoring </li> token.")
        return
    parser.generate_implied_end_tags(exclude="li")
    if parser.current_node.tag_name_lower != "li":
        parser.log_error("Parse error: current node is not <li> when processing </li> token.")
    while parser.open_elements:
        popped = parser.open_elements.pop()
        if popped.tag_name_lower == "li":
            break

def handle_in_body_endtag_dd_dt(parser: "TWHTMLParser", token: Token) -> None:
    tag = token.lower_name
    if not parser.has_element_in_scope(tag, "default"):
        parser.log_error(f"Parse error: no <{tag}> element in scope; ignoring </{tag}> token.")
        return
    parser.generate_implied_end_tags(exclude=tag)
    if parser.current_node.tag_name_lower != tag:
        parser.log_error(f"Parse error: current node is not <{tag}> when processing </{tag}> token.")
    while parser.open_elements:
        popped = parser.open_elements.pop()
        if popped.tag_name_lower == tag:
            break

def handle_in_body_endtag_heading(parser: "TWHTMLParser", token: Token) -> None:
    tag = token.lower_name
    for heading in HEADING_TAGS:
        if parser.has_element_in_scope(heading):
            parser.generate_implied_end_tags()
            break

    if parser.open_elements[-1].tag_name_lower != tag:
        parser.log_error(f"Parse error: no heading element in scope for </{tag}>; ignoring token.")

    for heading in HEADING_TAGS:
        if parser.has_element_in_scope(heading):
            popped = parser.open_elements.pop()
            while popped.tag_name not in HEADING_TAGS:
                popped = parser.open_elements.pop()
            break

def handle_in_body_a(self, token: Token) -> None:
    afe_element = self.find_last_active_formatting_element("a")
    if afe_element is not None:
        self.log_error("Parse error: unexpected start_tag implies end_tag for <a>")
        implied_end_token = Token(END_TAG, "a")
        adoption_agency_algorithm(self, implied_end_token)
        if afe_element in self.open_elements:
            self.open_elements.remove(afe_element)
        if afe_element in self.active_formatting_elements:
            self.active_formatting_elements.remove(afe_element)

    self.reconstruct_active_formatting_elements()
    self.add_formatting_element(token)

def handle_in_body_formatting(parser: "TWHTMLParser", token: Token) -> None:
    parser.reconstruct_active_formatting_elements()
    parser.add_formatting_element(token)

def handle_in_body_nobr(parser: "TWHTMLParser", token: Token) -> None:
    parser.reconstruct_active_formatting_elements()
    if parser.has_element_in_scope("nobr", "default"):
        parser.log_error("Parse error: <nobr> element already in scope.")
        adoption_agency_algorithm(parser, token)
        parser.reconstruct_active_formatting_elements()
    parser.add_formatting_element(token)

def handle_in_body_applet_marquee_object(parser: "TWHTMLParser", token: Token) -> None:
    parser.reconstruct_active_formatting_elements()
    parser.insert_element_token(token)
    parser.active_formatting_elements.append(MARKER)
    parser.frameset_ok = False

def handle_in_body_endtag_applet_marquee_object(parser: "TWHTMLParser", token: Token) -> None:
    tag = token.lower_name
    if not parser.has_element_in_scope(tag, "default"):
        parser.log_error(f"Parse error: no <{tag}> element in scope; ignoring end tag.")
        return
    parser.generate_implied_end_tags()
    if parser.current_node.tag_name_lower != tag:
        parser.log_error(f"Parse error: current node is not <{tag}> when processing end tag.")
    while parser.open_elements:
        popped = parser.open_elements.pop()
        if popped.tag_name_lower == tag:
            break
    while parser.active_formatting_elements:
        entry = parser.active_formatting_elements.pop()
        if entry == MARKER:
            break

def handle_in_body_table(parser: "TWHTMLParser", token: Token) -> None:
    if not parser.document.quirks_mode and parser.has_element_in_scope("p", "button"):
        parser.close_p_element()
    parser.insert_element_token(token)
    parser.frameset_ok = False
    parser.insertion_mode = InsertionMode.IN_TABLE

def handle_in_body_endtag_br(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error("Parse error: unexpected </br> end tag; treating as a <br> start tag with no attributes.")
    synthetic_token = Token(START_TAG, name="br", attributes=[])
    parser.process_token(synthetic_token)

def handle_in_body_void_elements(parser: "TWHTMLParser", token: Token) -> None:
    parser.reconstruct_active_formatting_elements()
    parser.insert_element_token(token)
    parser.open_elements.pop()
    token.acknowledge_self_closing()
    parser.frameset_ok = False

def handle_in_body_input(parser: "TWHTMLParser", token: Token) -> None:
    old_frameset_ok = parser.frameset_ok
    parser.reconstruct_active_formatting_elements()
    element = parser.insert_element_token(token)
    if element in parser.open_elements:
        parser.open_elements.remove(element)

    if token.self_closing:
        token.acknowledge_self_closing()

    type_attr = token.get_attribute_value("type")
    if not (type_attr and type_attr.lower() == "hidden"):
        parser.frameset_ok = False
    else:
        parser.frameset_ok = old_frameset_ok

def handle_in_body_param_source_track(parser: "TWHTMLParser", token: Token) -> None:
    element = parser.insert_element_token(token)
    if element in parser.open_elements:
        parser.open_elements.remove(element)
    if getattr(token, "self_closing", False):
        token.acknowledge_self_closing()

def handle_in_body_hr(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope("p", "button"):
        parser.close_p_element()
    element = parser.insert_element_token(token)
    if element in parser.open_elements:
        parser.open_elements.remove(element)
    if getattr(token, "self_closing", False):
        token.acknowledge_self_closing()
    parser.frameset_ok = False

def handle_in_body_image(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error("Parse error: <image> start tag encountered; changing tag name to <img> and reprocessing.")
    token.name = "img"
    parser.process_token(token)

def handle_in_body_textarea(parser: "TWHTMLParser", token: Token) -> None:
    parser.get_adjusted_insertion_location()
    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.RCDATA_STATE, appropriate_end_tag_name="textarea")
    parser.frameset_ok = False

def handle_in_body_xmp(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope("p", "button"):
        parser.close_p_element()
    parser.reconstruct_active_formatting_elements()
    parser.frameset_ok = False
    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.RAWTEXT_STATE, appropriate_end_tag_name="xmp")

def handle_in_body_iframe(parser: "TWHTMLParser", token: Token) -> None:
    parser.frameset_ok = False
    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.RAWTEXT_STATE, appropriate_end_tag_name="iframe")

def handle_in_body_noembed_noframes(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.RAWTEXT_STATE, appropriate_end_tag_name=("noembed", "noframes"))

def handle_in_body_noscript(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.RAWTEXT_STATE, appropriate_end_tag_name="noscript")

def handle_in_body_select(parser: "TWHTMLParser", token: Token) -> None:
    parser.reconstruct_active_formatting_elements()
    parser.insert_element_token(token)
    parser.frameset_ok = False
    if parser.insertion_mode in {
        InsertionMode.IN_TABLE,
        InsertionMode.IN_CAPTION,
        InsertionMode.IN_TABLE_BODY,
        InsertionMode.IN_ROW,
        InsertionMode.IN_CELL,
    }:
        parser.insertion_mode = InsertionMode.IN_SELECT_IN_TABLE
    else:
        parser.insertion_mode = InsertionMode.IN_SELECT

def handle_in_body_optgroup_option(parser: "TWHTMLParser", token: Token) -> None:
    if parser.current_node.tag_name_lower == "option":
        parser.open_elements.pop()
    parser.reconstruct_active_formatting_elements()
    parser.insert_element_token(token)

def handle_in_body_rb_rtc(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope("ruby", "default"):
        parser.generate_implied_end_tags()
        if parser.current_node.tag_name_lower != "ruby":
            parser.log_error("Parse error: current node is not <ruby> when processing <rb>/<rtc> start tag.")
    parser.insert_element_token(token)

def handle_in_body_rp_rt(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope("ruby", "default"):
        parser.generate_implied_end_tags(exclude="rtc")
        current = parser.current_node.tag_name_lower
        if current not in {"ruby", "rtc"}:
            parser.log_error("Parse error: current node is not <ruby> or <rtc> when processing <rp>/<rt> start tag.")
    parser.insert_element_token(token)

def handle_in_body_math(parser: "TWHTMLParser", token: Token) -> None:
    parser.reconstruct_active_formatting_elements()
    parser.adjust_attributes(token, MATHML_ATTRIBUTE_FIXES)
    parser.adjust_attributes(token, NAMESPACED_ATTRIBUTE_FIXES)

    parser.insert_element_token(token, name_spaces=namespaces["mathml"])
    if getattr(token, "self_closing", False):
        parser.open_elements.pop()
        token.acknowledge_self_closing()

def handle_in_body_svg(parser: "TWHTMLParser", token: Token) -> None:
    parser.reconstruct_active_formatting_elements()
    parser.adjust_attributes(token, SVG_ATTRIBUTE_FIXES)
    parser.adjust_attributes(token, NAMESPACED_ATTRIBUTE_FIXES)

    element = parser.insert_element_token(token, name_spaces=namespaces["svg"])
    if getattr(token, "self_closing", False):
        if element in parser.open_elements:
            parser.open_elements.remove(element)
        token.acknowledge_self_closing()

def handle_in_body_any_other_start_tag(parser: "TWHTMLParser", token: Token) -> None:
    parser.reconstruct_active_formatting_elements()
    if token.lower_name == "noscript" and not parser.scripting_enabled:
        pass
    parser.insert_element_token(token)

def handle_in_body_any_other_end_tag(parser: "TWHTMLParser", token: Token) -> None:
    tag = token.lower_name
    for node in reversed(parser.open_elements):
        if node.tag_name_lower == tag:
            parser.generate_implied_end_tags(exclude=tag)
            if parser.open_elements and parser.open_elements[-1].tag_name_lower != tag:
                parser.log_error(f"Parse error: current node is not <{tag}> when processing end tag.")
            while parser.open_elements:
                popped = parser.open_elements.pop()
                if popped.tag_name_lower == tag:
                    break
            break
        else:
            if node.tag_name_lower in SPECIAL_ELEMENTS:
                parser.log_error(f"Parse error: encountered special element <{node.tag_name}> while processing end tag </{tag}>; token ignored.")
                break

# ---------------------------
# --- TEXT
# ---------------------------

def handle_text_character(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_character(token.data)

def handle_text_eof(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error("Parse error: EOF in 'text' insertion mode.")

    if parser.open_elements:
        parser.open_elements.pop()

    parser.insertion_mode = parser.restore_original_insertion_mode()
    parser.process_token(token)

def handle_text_end_script(parser: "TWHTMLParser", token: Token) -> None:
    node = parser.open_elements.pop()
    parser.insertion_mode = parser.restore_original_insertion_mode()

def handle_text_end_other(parser: "TWHTMLParser", token: Token) -> None:
    if parser.open_elements:
        parser.open_elements.pop()
    parser.insertion_mode = parser.restore_original_insertion_mode()

# ---------------------------
# --- IN_TABLE
# ---------------------------

def clear_stack_back_to_table_context(parser: "TWHTMLParser") -> None:
    while parser.open_elements:
        current = parser.current_node
        if current.tag_name_lower in ("table", "template", "html"):
            break
        parser.open_elements.pop()

def handle_in_table_character_with_table_node(parser: "TWHTMLParser", token: Token) -> None:
    parser.pending_table_character_tokens = []
    parser.original_mode.append(parser.insertion_mode)
    parser.process_token(token, override_mode=InsertionMode.IN_TABLE_TEXT)

def handle_in_table_start_caption(parser: "TWHTMLParser", token: Token) -> None:
    clear_stack_back_to_table_context(parser)
    parser.active_formatting_elements.append(MARKER)
    parser.insert_element_token(token)
    parser.insertion_mode = InsertionMode.IN_CAPTION

def handle_in_table_start_colgroup(parser: "TWHTMLParser", token: Token) -> None:
    clear_stack_back_to_table_context(parser)
    parser.insert_element_token(token)
    parser.insertion_mode = InsertionMode.IN_COLUMN_GROUP

def handle_in_table_start_col(parser: "TWHTMLParser", token: Token) -> None:
    clear_stack_back_to_table_context(parser)
    synthetic_colgroup = Token(START_TAG, "colgroup", attributes=[])
    parser.insert_element_token(synthetic_colgroup)
    parser.insertion_mode = InsertionMode.IN_COLUMN_GROUP
    parser.process_token(token)

def handle_in_table_start_tbody_tfoot_thead(parser: "TWHTMLParser", token: Token) -> None:
    clear_stack_back_to_table_context(parser)
    parser.insert_element_token(token)
    parser.insertion_mode = InsertionMode.IN_TABLE_BODY

def handle_in_table_start_td_th_tr(parser: "TWHTMLParser", token: Token) -> None:
    clear_stack_back_to_table_context(parser)
    synthetic_tbody = Token(START_TAG, "tbody", attributes=[])
    parser.insert_element_token(synthetic_tbody)
    parser.insertion_mode = InsertionMode.IN_TABLE_BODY
    parser.process_token(token)

def handle_in_table_start_table(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error("Parse error: unexpected <table> start tag in 'in table' mode.")
    if not parser.has_element_in_scope("table", "table"):
        return

    while parser.open_elements:
        popped = parser.open_elements.pop()
        if popped.tag_name_lower == "table":
            break

    parser.reset_insertion_mode_appropriately()
    parser.process_token(token)

def handle_in_table_end_table(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope("table", "table"):
        parser.generate_implied_end_tags()
        if parser.open_elements[-1].tag_name_lower != "table":
            parser.log_error(f"Parse error: end tag too early named got 'table', expected '{parser.current_node.tag_name}'")

        while parser.open_elements[-1].tag_name_lower != "table":
            parser.open_elements.pop()
        parser.open_elements.pop()
        parser.reset_insertion_mode_appropriately()

    else:
         parser.log_error(f"Parse error: '{token.name}'")

def handle_in_table_start_input(parser: "TWHTMLParser", token: Token) -> None:
    type_val = token.get_attribute_value("type")
    if type_val is None or type_val.lower() != "hidden":
        handle_in_table_anything_else(parser, token)
        return

    parser.log_error("Parse error: <input type='hidden'> in 'in table' insertion mode.")
    parser.insert_element_token(token)
    if parser.open_elements:
        parser.open_elements.pop()
    if getattr(token, "self_closing", False):
        token.acknowledge_self_closing()

def handle_in_table_start_form(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error("Parse error: <form> start tag in 'in table' insertion mode.")
    has_template = any(el.tag_name_lower == "template" for el in parser.open_elements)
    if has_template or (parser.document.form_element is not None):
        return

    form_elem = parser.insert_element_token(token)
    parser.document.form_element = form_elem
    if parser.open_elements and parser.open_elements[-1] == form_elem:
        parser.open_elements.pop()

def handle_in_table_start_select(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_from_table  = True
    handle_in_body_select(parser,token)
    parser.insert_from_table  = False

def handle_in_table_anything_else(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error(f"Parse error: unexpected token {token} in 'in table' mode. Using foster parenting.")
    parser.insert_from_table   = True
    parser.process_token(token, override_mode=InsertionMode.IN_BODY)
    parser.insert_from_table   = False

# ---------------------------
# --- IN_TABLE_TEXT mode handlers
# ---------------------------

def handle_in_table_text_char_other(parser: "TWHTMLParser", token: Token) -> None:
    if token.null_character:
        parser.log_error(f"Error: {token}")
    else:
        token.data = token.data.replace("\u0000", "").replace("\uFFFD", "")
        parser.pending_table_character_tokens.append(token)
        parser.insertion_mode = InsertionMode.IN_TABLE_TEXT

def handle_in_table_text_anything_else(parser: "TWHTMLParser", token: Token) -> None:
    data = "".join([item.data for item in parser.pending_table_character_tokens])
    if any(ch not in space_characters for ch in data):
        synthetic_token = Token(CHARACTER, data=data)
        parser.insert_from_table  = True
        parser.process_token(synthetic_token, override_mode=InsertionMode.IN_BODY)
        parser.insert_from_table  = False
    elif data:
        parser.insert_text(data)

    parser.pending_table_character_tokens.clear()
    if parser.original_mode:
        parser.insertion_mode = parser.restore_original_insertion_mode()
        parser.process_token(token, parser.insertion_mode)

# ---------------------------
# --- IN_CAPTION
# ---------------------------

def handle_in_caption_end_tag_caption(parser: "TWHTMLParser", token: Token) -> None:
    if not parser.has_element_in_scope("caption", "table"):
        parser.log_error("Parse error: </caption> without <caption> in table scope.")
        return

    parser.generate_implied_end_tags()
    if parser.current_node.tag_name_lower != "caption":
        parser.log_error("Parse error: current node is not <caption> after implied end tags.")
    while parser.open_elements:
        popped = parser.open_elements.pop()
        if popped.tag_name_lower == "caption":
            break

    parser.clear_active_formatting_elements_up_to_marker()
    parser.insertion_mode = InsertionMode.IN_TABLE

def handle_in_caption_start_caption_col_colgroup_tbody_td_tfoot_th_thead_tr_end_tag_table(parser: "TWHTMLParser", token: Token) -> None:
    if not parser.has_element_in_scope("caption", "table"):
        parser.log_error(f"Parse error: {token} but no <caption> in table scope.")
        return

    parser.generate_implied_end_tags()
    if parser.current_node.tag_name_lower != "caption":
        parser.log_error("Parse error: current node is not <caption> after implied end tags.")
    while parser.open_elements:
        popped = parser.open_elements.pop()
        if popped.tag_name_lower == "caption":
            break
    parser.clear_active_formatting_elements_up_to_marker()
    parser.insertion_mode = InsertionMode.IN_TABLE
    parser.process_token(token)

# ---------------------------
# --- IN_COLUMN_GROUP
# ---------------------------

def handle_in_column_group_character(parser: "TWHTMLParser", token: Token) -> None:
    synthetic_token = Token(END_TAG, name="colgroup", attributes=[])
    handle_in_column_group_end_colgroup(parser,synthetic_token)
    if not (parser.current_node.tag_name_lower == "html"):
        parser.process_token(token)

def handle_in_column_group_start_col(parser: "TWHTMLParser", token: Token) -> None:
    element = parser.insert_element_token(token)
    if parser.open_elements and parser.open_elements[-1] == element:
        parser.open_elements.pop()
    if getattr(token, "self_closing", False):
        token.acknowledge_self_closing()

def handle_in_column_group_end_colgroup(parser: "TWHTMLParser", token: Token) -> None:
    if not parser.open_elements:
        parser.log_error("Parse error: </colgroup> but open_elements is empty.")
        return
    if parser.current_node.tag_name_lower != "colgroup":
        parser.log_error("Parse error: </colgroup> when current node is not <colgroup>.")
        return
    parser.open_elements.pop()
    parser.insertion_mode = InsertionMode.IN_TABLE

def handle_in_column_group_anything_else(parser: "TWHTMLParser", token: Token) -> None:
    if not parser.open_elements:
        parser.log_error(f"Parse error: {token}, but open_elements empty in 'in column group'. Ignoring.")
        return
    if parser.current_node.tag_name_lower != "colgroup":
        parser.log_error(f"Parse error: {token}, current node is not <colgroup>. Ignoring.")
        return

    parser.open_elements.pop()
    parser.insertion_mode = InsertionMode.IN_TABLE
    parser.process_token(token)

# ---------------------------
# --- IN_TABLE_BODY
# ---------------------------

def handle_in_table_body_start_tr(parser: "TWHTMLParser", token: Token) -> None:
    parser.clear_stack_back_to_table_body_context()
    parser.insert_element_token(token)
    parser.insertion_mode = InsertionMode.IN_ROW

def handle_in_table_body_start_th_td(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error(f"Parse error: <{token.name}> start tag in 'in table body' mode.")
    parser.clear_stack_back_to_table_body_context()
    synthetic_tr = Token(START_TAG, "tr", attributes=[])
    parser.insert_element_token(synthetic_tr)
    parser.insertion_mode = InsertionMode.IN_ROW
    parser.process_token(token)

def handle_in_table_body_end_tbody_tfoot_thead(parser: "TWHTMLParser", token: Token) -> None:
    if not parser.has_element_in_scope(token.name, "table"):
        parser.log_error(f"Parse error: </{token.name}> with no <{token.name}> in table scope.")
        return

    parser.clear_stack_back_to_table_body_context()
    parser.open_elements.pop()
    parser.insertion_mode = InsertionMode.IN_TABLE

def handle_end_tag_table_row_group(parser: "TWHTMLParser", token: Token) -> None:
    if (parser.has_element_in_scope("tbody", "table") or
       parser.has_element_in_scope("thead", "table") or
       parser.has_element_in_scope("tfoot", "table")):
        parser.clear_stack_back_to_table_body_context()
        synthetic_tr = Token(END_TAG, parser.open_elements[-1].tag_name)
        handle_in_table_body_end_tbody_tfoot_thead(parser, synthetic_tr)
        parser.process_token(token)
    else:
        parser.log_error(f"Parse error: unexpected end tag </{token.name}> in table body.")

def handle_end_tag_table(parser: "TWHTMLParser", token: Token) -> None:
    if (parser.has_element_in_scope("tbody", "table") or
        parser.has_element_in_scope("thead", "table") or
        parser.has_element_in_scope("tfoot", "table")):
        parser.clear_stack_back_to_table_body_context()
        implied_token = Token(END_TAG, parser.current_node.tag_name)
        handle_end_tag_table_row_group(parser, implied_token)
        parser.process_token(token)
    else:
        parser.log_error("Parse error: unexpected </table> without table row group.")

def handle_in_table_body_anything_else(parser: "TWHTMLParser", token: Token) -> None:
    parser.original_mode.append(parser.insertion_mode)
    parser.process_token(token, override_mode=InsertionMode.IN_TABLE)

# ---------------------------
# --- IN_ROW
# ---------------------------
def ignore_end_tag_tr(parser: "TWHTMLParser", token: Token):
    parser.log_error("Parse error: </tr> without <tr> in table scope.")
    return not parser.has_element_in_scope("tr", "table")

def handle_in_row_start_th_td(parser: "TWHTMLParser", token: Token) -> None:
    parser.clear_stack_back_to_table_row_context()
    parser.insert_element_token(token)
    parser.insertion_mode = InsertionMode.IN_CELL
    parser.active_formatting_elements.append(MARKER)

def handle_in_row_end_tr(parser: "TWHTMLParser", token: Token) -> None:
    if not ignore_end_tag_tr(parser, token):
        parser.clear_stack_back_to_table_row_context()
        parser.open_elements.pop()
        parser.insertion_mode = InsertionMode.IN_TABLE_BODY
    else:
        parser.log_error(f"Parse error: {token}.")

def handle_end_tag_tr(parser: "TWHTMLParser", token: Token):
    if parser.has_element_in_scope("tr", "table"):
        parser.clear_stack_back_to_table_row_context()
        parser.open_elements.pop()
        parser.insertion_mode = InsertionMode.IN_TABLE_BODY
    else:
        parser.log_error(f"Parse error: {token} but no <tr> in table scope.")

def handle_in_row_start_the_table_stuff(parser: "TWHTMLParser", token: Token):
    ignore_tag=ignore_end_tag_tr(parser, token)
    synthetic_tr = Token(END_TAG, "tr")
    handle_in_row_end_tr(parser, synthetic_tr)
    if not ignore_tag:
        parser.process_token(token, override_mode=InsertionMode.IN_TABLE_BODY)

def handle_in_row_end_table(parser: "TWHTMLParser", token: Token):
    ignore_tag = ignore_end_tag_tr(parser, token)
    synthetic_tr = Token(END_TAG, "tr")
    handle_in_row_end_tr(parser, synthetic_tr)
    if not ignore_tag:
        parser.process_token(token, override_mode=InsertionMode.IN_TABLE_BODY)

def handle_in_row_end_tbody_tfoot_thead(parser: "TWHTMLParser", token: Token) -> None:
    tag_lower_name = token.lower_name
    if not parser.has_element_in_scope(tag_lower_name, "table"):
        parser.log_error(f"Parse error: </{tag_lower_name}> with no <{tag_lower_name}> in table scope.")
        return
    if not parser.has_element_in_scope("tr", "table"):
        parser.log_error(f"Parse error: </{tag_lower_name}> but no <tr> in table scope => ignoring.")
        return

    synthetic_tr = Token(END_TAG, "tr")
    handle_end_tag_tr(parser, synthetic_tr)
    parser.process_token(token, override_mode=InsertionMode.IN_TABLE_BODY)

def handle_in_row_anything_else(parser: "TWHTMLParser", token: Token) -> None:
    parser.original_mode.append(parser.insertion_mode)
    parser.process_token(token, override_mode=InsertionMode.IN_TABLE)

# ---------------------------
# --- IN_CELL
# ---------------------------
def handle_in_cell_end_td_th(parser: "TWHTMLParser", token: Token) -> None:
    cell_name = token.name
    if parser.has_element_in_scope(cell_name, "table"):
        parser.generate_implied_end_tags(cell_name)

        if parser.current_node.tag_name_lower != cell_name:
            parser.log_error(f"Parse error: unexpected-cell-end-tag: current node is not <{cell_name}>.")
            while True:
                node = parser.open_elements.pop()
                if node.tag_name == cell_name:
                    break
        else:
            parser.open_elements.pop()

        parser.clear_active_formatting_elements_up_to_marker()
        parser.insertion_mode = InsertionMode.IN_ROW
    else:
        parser.log_error(f"Parse error: </{cell_name}> without <{cell_name}> in table scope.")
        return

def handle_in_cell_start_caption_col_colgroup_tbody_td_tfoot_th_thead_tr(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope("td", "table") or parser.has_element_in_scope("th", "table"):
        if parser.has_element_in_scope("td", "table"):
            synthetic_head_token = Token(START_TAG, "td", attributes=[])
            handle_in_cell_end_td_th(parser, synthetic_head_token)
        elif parser.has_element_in_scope("th", "table"):
            synthetic_head_token = Token(START_TAG, "th", attributes=[])
            handle_in_cell_end_td_th(parser, synthetic_head_token)

        parser.process_token(token)
    else:
        parser.log_error(f"Parse error: </{token.name}>")

def handle_in_cell_end_tag_ignored(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error(f"Parse error: unexpected end tag </{token.name}> in 'in cell' mode. Ignoring.")

def handle_in_cell_end_table_tbody_tfoot_thead_tr(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope(token.lower_name, "table"):
        parser.close_the_cell()
        parser.process_token(token)
    else:
        parser.log_error(f"Parse error: </{token.name}> with no <{token.name}> in table scope.")

# ---------------------------
# --- IN_SELECT
# ---------------------------

def handle_insert_character_inselect(parser: "TWHTMLParser", token: Token) -> None:
    if token.null_character:
        parser.log_error(f"Error: {token}")
    else:
        token.data = token.data.replace("\u0000", "").replace("\uFFFD", "")
        parser.insert_character(token.data)

def handle_in_select_start_option(parser: "TWHTMLParser", token: Token) -> None:
    if parser.current_node.tag_name_lower == "option":
        parser.open_elements.pop()
    parser.insert_element_token(token)

def handle_in_select_start_optgroup(parser: "TWHTMLParser", token: Token) -> None:
    if parser.current_node.tag_name_lower == "option":
        parser.open_elements.pop()
    if parser.current_node.tag_name_lower == "optgroup":
        parser.open_elements.pop()
    parser.insert_element_token(token)

def handle_in_select_start_hr(parser: "TWHTMLParser", token: Token) -> None:
    if parser.current_node.tag_name_lower == "option":
        parser.open_elements.pop()
    if parser.current_node.tag_name_lower == "optgroup":
        parser.open_elements.pop()
    element = parser.insert_element_token(token)
    if parser.open_elements and parser.open_elements[-1] == element:
        parser.open_elements.pop()
    if getattr(token, "self_closing", False):
        token.acknowledge_self_closing()

def handle_in_select_end_optgroup(parser: "TWHTMLParser", token: Token) -> None:
    if (parser.current_node.tag_name_lower == "option" and
        len(parser.open_elements) >= 2 and
        parser.open_elements[-2].tag_name_lower == "optgroup"):
        parser.open_elements.pop()

    if parser.current_node.tag_name_lower == "optgroup":
        parser.open_elements.pop()
    else:
        parser.log_error("Parse error: </optgroup> but current node not <optgroup>. Ignored.")

def handle_in_select_end_option(parser: "TWHTMLParser", token: Token) -> None:
    if parser.current_node.tag_name_lower == "option":
        parser.open_elements.pop()
    else:
        parser.log_error("Parse error: </option> but current node not <option>. Ignored.")

def handle_in_select_end_select(parser: "TWHTMLParser", token: Token) -> None:
    if parser.has_element_in_scope("select", "select"):
        pop = parser.open_elements.pop()
        while pop.tag_name_lower != "select":
            pop = parser.open_elements.pop()
        parser.reset_insertion_mode_appropriately()
    else:
        parser.log_error("Parse error: </select> but no <select> in select scope. Ignored.")

def handle_in_select_start_select(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error("Parse error: <select> start tag in 'in select' mode.")
    synthetic_token = Token(END_TAG, "select")
    handle_in_select_end_select(parser,synthetic_token)

def handle_in_select_start_input_keygen_textarea(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error(f"Parse error: <{token.name}> in 'in select' mode.")
    if parser.has_element_in_scope("select", "select"):
        synthetic_token = Token(END_TAG, "select")
        handle_in_select_end_select(parser, synthetic_token)
        parser.process_token(token)


# ---------------------------
# --- IN_SELECT_IN_TABLE mode handlers
# ---------------------------

def handle_in_select_in_table_start_ctable(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error(f"Parse error: {token} in 'in select in table' mode.")
    while parser.open_elements:
        popped = parser.open_elements.pop()
        if popped.tag_name_lower == "select":
            break
    parser.reset_insertion_mode_appropriately()
    parser.process_token(token)

def handle_in_select_in_table_end_ctable(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error(f"Parse error: {token} in 'in select in table' mode.")
    if not parser.has_element_in_scope(token.lower_name, "table"):
        return
    while parser.open_elements:
        popped = parser.open_elements.pop()
        if popped.tag_name_lower == "select":
            break
    parser.reset_insertion_mode_appropriately()
    parser.process_token(token)


# ---------------------------
# --- AFTER_BODY
# ---------------------------

def handle_after_body_comment(parser: "TWHTMLParser", token: Token) -> None:
    if parser.open_elements:
        html_elem = parser.open_elements[0]
        data: str = token.data
        insertion_parent, insertion_reference = parser.get_adjusted_insertion_location(html_elem)
        comment_node: Comment = parser.document.create_comment(data)
        insertion_parent.append_child(comment_node)
    else:
        parser.log_error("Parse error: no element in open_elements when inserting comment in 'after body' mode.")

def handle_after_body_endtag_html(parser: "TWHTMLParser", token: Token) -> None:
    if parser.is_fragment_parsing:
        parser.log_error("Parse error: unexpected </html> in fragment parsing mode. Ignoring token.")
        return
    parser.insertion_mode = InsertionMode.AFTER_AFTER_BODY

def handle_after_body_eof(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error("Parse error: Reached EOF in 'after body' insertion mode.")

def handle_after_body_anything_else(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error(f"Parse error: unexpected token {token} in 'after body' insertion mode.")
    parser.insertion_mode = InsertionMode.IN_BODY
    parser.process_token(token)

# ---------------------------
# --- IN_FRAMESET
# ---------------------------

def handle_character_frameset(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error("Parse error: unexpected char in frameset.")

def handle_in_frameset_start_frameset(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_element_token(token)

def handle_in_frameset_end_frameset(parser: "TWHTMLParser", token: Token) -> None:
    if parser.current_node.tag_name_lower == "html":
        parser.log_error("Parse error: </frameset> but current node is <html>. Ignored.")
        return
    if parser.open_elements:
        parser.open_elements.pop()

    if not parser.is_fragment_parsing:
        if parser.current_node.tag_name_lower != "frameset":
            parser.insertion_mode = InsertionMode.AFTER_FRAMESET

def handle_in_frameset_start_frame(parser: "TWHTMLParser", token: Token) -> None:
    element = parser.insert_element_token(token)
    if parser.open_elements and parser.open_elements[-1] == element:
        parser.open_elements.pop()
    if getattr(token, "self_closing", False):
        token.acknowledge_self_closing()

def handle_in_frameset_start_noframes(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.RAWTEXT_STATE, appropriate_end_tag_name="noframes")
    parser.process_token(token)

def handle_in_frameset_eof(parser: "TWHTMLParser", token: Token) -> None:
    if parser.current_node.tag_name_lower != "html":
        parser.log_error("Parse error: EOF in frameset but current node is not <html>.")

def handle_in_frameset_anything_else(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error(f"Parse error: unexpected {token} in 'in frameset' mode. Ignored.")

# ---------------------------
# --- AFTER_FRAMESET
# ---------------------------

def handle_after_frameset_end_html(parser: "TWHTMLParser", token: Token) -> None:
    parser.insertion_mode = InsertionMode.AFTER_AFTER_FRAMESET

def handle_after_frameset_start_noframes(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.RAWTEXT_STATE, appropriate_end_tag_name="noframes")
    parser.process_token(token)


# ---------------------------
# --- AFTER_AFTER_BODY
# ---------------------------

def handle_after_after_body_comment(parser: "TWHTMLParser", token: Token) -> None:
    comment_node = parser.document.create_comment(token.data)
    parser.document.append_child(comment_node)

def create_node_from_token(parser: "TWHTMLParser", token: Token) -> Node:
    if token.type == START_TAG:
        return parser.document.create_element(token.name)
    elif token.type == CHARACTER:
        return parser.document.create_text_node(token.data)
    elif token.type == COMMENT:
        return parser.document.create_comment(token.data)
    else:
        raise ValueError(f"Token type {token.type} non supportato in create_node_from_token")

def handle_after_after_body_anything_else(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error(f"Parse error: unexpected {token} in 'after after body'. Switching to 'in body'.")
    parser.insertion_mode = InsertionMode.IN_BODY
    parser.process_token(token)

# ---------------------------
# --- AFTER_AFTER_FRAMESET
# ---------------------------

def handle_after_after_frameset_comment(parser: "TWHTMLParser", token: Token) -> None:
    comment_node = parser.document.create_comment(token.data)
    parser.document.append_child(comment_node)

def handle_after_after_frameset_start_noframes(parser: "TWHTMLParser", token: Token) -> None:
    parser.insert_and_change_state_tokenizer(token, new_state=TokenizerState.RAWTEXT_STATE, appropriate_end_tag_name="noframes")
    parser.process_token(token)

# ---------------------------
# --- FOREIGN_CONTENT
# ---------------------------

def handle_character_foreign_content(parser: "TWHTMLParser", token: Token) -> None:
    if parser.frameset_ok and any(ch not in space_characters for ch in token.data) and token.data != "\uFFFD":
        parser.frameset_ok = False
    parser.insert_text(token.data)
    return

def handle_doctype_foreign_content(parser: "TWHTMLParser", token: Token) -> None:
    parser.log_error("Parse error: DOCTYPE in foreign content. Ignoring.")

def handle_start_tag_foreign_content(parser: "TWHTMLParser", token: Token) -> None:
    token_name_lower = token.lower_name
    if (
        token_name_lower in BREAKOUT_ELEMENTS
        or (
            token_name_lower == "font"
            and any(
                parser.attr_name_is(attr_obj, ("color", "face", "size"))
                for attr_obj in token.attributes
            )
        )
    ):
        parser.log_error(f"Parse error: unexpected HTML element <{token_name_lower}> in foreign content.")
        while (
            parser.open_elements[-1].namespace != namespaces["html"]
            and not ((parser.open_elements[-1], parser.open_elements[-1].tag_name) in mathml_integration_point_elements)
            and not parser.is_html_integration_point(parser.open_elements[-1])
        ):
            parser.open_elements.pop()

        handler = parser.get_dispatch_handler(token, parser.insertion_mode)
        if handler:
            handler(parser, token)
        else:
            parser.log_error(f"No handler for token: {token}")
        return


    current_ns = parser.current_node.namespace
    if current_ns == namespaces["mathml"]:
        parser.adjust_attributes(token, MATHML_ATTRIBUTE_FIXES)
    elif current_ns == namespaces["svg"]:
        parser.adjust_svg_tag_names(token)
        parser.adjust_attributes(token, SVG_ATTRIBUTE_FIXES)

    parser.adjust_attributes(token, NAMESPACED_ATTRIBUTE_FIXES)

    elem = parser.insert_element_token(token, name_spaces=current_ns)

    if getattr(token, "self_closing", False):
        if parser.open_elements and parser.open_elements[-1] == elem:
            parser.open_elements.pop()
        token.acknowledge_self_closing()


def handle_end_tag_foreign_content(parser: "TWHTMLParser", token: Token) -> None:
    tn =  token.lower_name

    node_i = len(parser.open_elements) - 1
    node = parser.open_elements[node_i]

    if node.tag_name.translate(ascii_upper2lower) != tn:
        parser.log_error(f"Unexpected end tag: {token.name}")

    while True:
        if node.tag_name.translate(ascii_upper2lower) == tn:
            if parser.insertion_mode == InsertionMode.IN_TABLE_TEXT:
                data = "".join(item.data for item in parser.pending_table_character_tokens)
                if any(ch not in space_characters for ch in data):
                    synthetic_token = Token(CHARACTER, data=data)
                    parser.insert_from_table = True
                    handler = parser.get_dispatch_handler(synthetic_token, InsertionMode.IN_BODY)
                    if handler:
                        handler(parser, synthetic_token)

                    parser.insert_from_table = False
                elif data:
                    parser.insert_text(data)

                parser.pending_table_character_tokens.clear()
                if parser.original_mode:
                    parser.insertion_mode = parser.restore_original_insertion_mode()

            while parser.open_elements.pop() != node:
                assert parser.open_elements, "Stack shouldn't become empty here"
            break

        node_i -= 1
        if node_i < 0:
            parser.log_error(f"Parse error: no matching element for </{tn}> in foreign content.")
            break

        node = parser.open_elements[node_i]
        if node.namespace != namespaces["html"]:
            continue
        else:
            handler = parser.get_dispatch_handler(token, parser.insertion_mode)
            if handler:
                handler(parser, token)
            else:
                parser.log_error(f"No handler for token: {token}")
            break


#####################################################################
####   DISPATCH
#####################################################################

GENERIC = None
MODE_DISPATCH = {
    InsertionMode.INITIAL: {
        CHARACTER: {
            space_characters: ignore_handler,
        },
        COMMENT: {
            GENERIC: insert_comment,
        },
        DOCTYPE: {
            GENERIC: handle_initial_doctype,
        },
        "FALLBACK": handle_initial_fallback,
    },
    InsertionMode.BEFORE_HTML: {
        CHARACTER: {
            space_characters: ignore_handler,
        },
        COMMENT: {
            GENERIC: insert_comment,
        },
        DOCTYPE: {
            GENERIC: parse_error_ignore_token
        },
        START_TAG: {
            "html": handle_before_html_html,
        },
        END_TAG: {
            ("head", "body", "html", "br"): handle_before_html_fallback,
            GENERIC: parse_error_ignore_token,
        },
        "FALLBACK": handle_before_html_fallback,
    },
    InsertionMode.BEFORE_HEAD: {
        CHARACTER: {
            space_characters: ignore_handler,
        },
        COMMENT: {
            GENERIC: insert_comment,
        },
        DOCTYPE: {
            GENERIC: parse_error_ignore_token,
        },
        START_TAG: {
            "html": lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_BODY)
,
            "head": handle_before_head_head,
        },
        END_TAG: {
            ("head", "body", "html", "br"): handle_before_head_anything_else,
            GENERIC: parse_error_ignore_token,
        },
        "FALLBACK": handle_before_head_anything_else,
    },
    InsertionMode.IN_HEAD: {
        CHARACTER: {
            space_characters: handle_insert_character,
        },
        COMMENT: {
            GENERIC: insert_comment,
        },
        DOCTYPE: {
            GENERIC: parse_error_ignore_token,
        },
        START_TAG: {
            "html": lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_BODY),
            ("base", "basefont", "bgsound", "link"): handle_in_head_base,
            "meta": handle_in_head_meta,
            "title": handle_in_head_title,
            "noscript": handle_in_head_noscript_disabled,
            ("noframes", "style"): handle_in_head_noframes_style,
            "script": handle_in_head_script,
            "head": parse_error_ignore_token,
        },
        END_TAG: {
            "head": handle_in_head_end_tag_head,
            ("body", "html", "br"): handle_in_head_end_tag_body_html_br,
            GENERIC: parse_error_ignore_token,
        },
        "FALLBACK": handle_in_head_anything_else,
    },
    InsertionMode.IN_HEAD_NOSCRIPT: {
        CHARACTER: {
            space_characters: lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_HEAD),
        },
        COMMENT: {
            GENERIC: lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_HEAD),
        },
        DOCTYPE: {
            GENERIC: parse_error_ignore_token,
        },
        START_TAG: {
            "html": lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_BODY),
            ("basefont", "bgsound", "link", "meta", "noframes", "style"): lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_HEAD),
            ("head", "noscript"): parse_error_ignore_token,
        },
        END_TAG: {
            "noscript": handle_in_head_noscript_endtag_noscript,
            "br": handle_in_head_noscript_anything_else,
            GENERIC: parse_error_ignore_token,
        },
        "FALLBACK": handle_in_head_noscript_anything_else,
    },
    InsertionMode.AFTER_HEAD: {
        CHARACTER: {
            space_characters: handle_insert_character,
        },
        COMMENT: {
            GENERIC: insert_comment,
        },
        DOCTYPE: {
            GENERIC: parse_error_ignore_token,
        },
        START_TAG: {
            "html": lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_BODY),
            "body": handle_after_head_body,
            "frameset": handle_after_head_frameset,
            ("base", "basefont", "bgsound", "link", "meta", "noframes", "script", "style", "title"): handle_after_head_in_head_tags,
            "head": parse_error_ignore_token,
        },
        END_TAG: {
            ("body", "html", "br"): handle_after_head_anything_else,
            GENERIC: parse_error_ignore_token,
        },
        "FALLBACK": handle_after_head_anything_else,
    },
    InsertionMode.IN_BODY: {
        CHARACTER: {
            space_characters: handle_in_body_whitespace,
            GENERIC: handle_in_body_other_character,
        },
        COMMENT: {
            GENERIC: insert_comment,
        },
        DOCTYPE: {
            GENERIC: parse_error_ignore_token,
        },
        START_TAG: {
            "html": handle_start_tag_htlm,
            ("base", "basefont", "bgsound", "link", "meta", "script", "style", "title"): lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_HEAD),
            ("noframes", "noembed"): handle_in_body_noembed_noframes,
            "body": handle_in_body_body,
            "frameset": handle_in_body_frameset,
            ("address", "article", "aside", "blockquote", "center", "details",
            "dialog", "dir", "div", "dl", "fieldset", "figcaption", "figure",
            "footer", "header", "hgroup", "main", "menu", "nav", "ol", "p",
            "search", "section", "summary", "ul"): handle_in_body_generic_container,
            ("h1", "h2", "h3", "h4", "h5", "h6"): handle_in_body_heading,
            ("pre", "listing"): handle_in_body_pre_listing,
            "form": handle_in_body_form,
            ("dd", "dt", "li"): handle_in_body_dd_dt_li,
            "plaintext": handle_in_body_plaintext,
            "button": handle_in_body_button,
            "a": handle_in_body_a,
            ("b", "big", "code", "em", "font", "i", "s", "small", "strike", "strong", "tt", "u"): handle_in_body_formatting,
            "nobr": handle_in_body_nobr,
            ("applet", "marquee", "object"): handle_in_body_applet_marquee_object,
            "table": handle_in_body_table,
            ("area", "br", "embed", "img", "keygen", "wbr"): handle_in_body_void_elements,
            "input": handle_in_body_input,
            ("param", "source", "track"): handle_in_body_param_source_track,
            "hr": handle_in_body_hr,
            "image": handle_in_body_image,
            "textarea": handle_in_body_textarea,
            "xmp": handle_in_body_xmp,
            "iframe": handle_in_body_iframe,
            "noscript": lambda parser, token: handle_in_body_noscript(parser, token) if getattr(parser, "scripting_enabled", True) else parser.insert_element_token(token),
            "select": handle_in_body_select,
            ("optgroup", "option"): handle_in_body_optgroup_option,
            ("rb", "rtc"): handle_in_body_rb_rtc,
            ("rp", "rt"): handle_in_body_rp_rt,
            "svg": handle_in_body_svg,
            "math": handle_in_body_math,
            ("caption", "col", "colgroup", "frame", "head",
                               "tbody", "td", "tfoot", "th", "thead",
                               "tr"): parse_error_ignore_token,
            GENERIC: handle_in_body_any_other_start_tag,
        },
        END_TAG: {
            "body": handle_in_body_endtag_body,
            "html": handle_in_body_endtag_html,
            ("address", "article", "aside", "blockquote", "button", "center", "details",
            "dialog", "dir", "div", "dl", "fieldset", "figcaption", "figure", "footer",
            "header", "hgroup", "listing", "main", "menu", "nav", "ol", "pre", "search",
            "section", "summary", "ul"): handle_in_body_generic_end,
            "form": handle_in_body_endtag_form,
            "p": handle_in_body_endtag_p,
            "li": handle_in_body_endtag_li,
            ("dd", "dt"): handle_in_body_endtag_dd_dt,
            ("h1", "h2", "h3", "h4", "h5", "h6"): handle_in_body_endtag_heading,
            ("a", "b", "big", "code", "em", "font", "i", "nobr", "s", "small", "strike", "strong", "tt", "u"): adoption_agency_algorithm,
            ("applet", "marquee", "object"): handle_in_body_endtag_applet_marquee_object,
            "br": handle_in_body_endtag_br,
            GENERIC: handle_in_body_any_other_end_tag,
        },
        EOF: {
            GENERIC: handle_in_body_eof,
        },
    },
    InsertionMode.TEXT: {
        CHARACTER: {
            GENERIC: handle_text_character,
        },
        END_TAG: {
            "script": handle_text_end_script,
            GENERIC: handle_text_end_other,
        },
        EOF: {
            GENERIC: handle_text_eof,
        },
    },
    InsertionMode.IN_TABLE: {
        CHARACTER: {
                    GENERIC: handle_in_table_character_with_table_node,
                },
        COMMENT: {
                    GENERIC: insert_comment,
                },
        DOCTYPE: {
                    GENERIC: parse_error_ignore_token,
                },
        START_TAG: {
            "html": handle_start_tag_htlm,
            "caption": handle_in_table_start_caption,
            "colgroup": handle_in_table_start_colgroup,
            "col": handle_in_table_start_col,
            ("tbody","tfoot","thead"): handle_in_table_start_tbody_tfoot_thead,
            ("td","th","tr"): handle_in_table_start_td_th_tr,
            "table": handle_in_table_start_table,
            ("style", "script"): lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_HEAD),
            "input": handle_in_table_start_input,
            "form": handle_in_table_start_form,
            "select": handle_in_table_start_select,
                },
        END_TAG: {
            "table": handle_in_table_end_table,
            ("body","caption","col","colgroup","html","tbody","td","tfoot","th","thead","tr"): parse_error_ignore_token,
                },
        EOF: {
                    GENERIC: lambda parser, token,: handle_reproces_token(parser, token,InsertionMode.IN_BODY),
                },
        "FALLBACK": handle_in_table_anything_else
    },
    InsertionMode.IN_TABLE_TEXT: {
        CHARACTER: {
            GENERIC: handle_in_table_text_char_other,
        },
        "FALLBACK": handle_in_table_text_anything_else,
    },
    InsertionMode.IN_CAPTION: {
        START_TAG: {
            "html": handle_start_tag_htlm,
            ("caption", "col", "colgroup", "tbody", "td", "tfoot", "th", "thead", "tr"): handle_in_caption_start_caption_col_colgroup_tbody_td_tfoot_th_thead_tr_end_tag_table,
        },
        END_TAG: {
            "caption": handle_in_caption_end_tag_caption,
            "table": handle_in_caption_start_caption_col_colgroup_tbody_td_tfoot_th_thead_tr_end_tag_table,
            ("body", "col", "colgroup", "html", "tbody", "td", "tfoot", "th", "thead", "tr"): parse_error_ignore_token,
        },
        "FALLBACK": lambda parser, token,: handle_reproces_token(parser, token,InsertionMode.IN_BODY)
    },
    InsertionMode.IN_COLUMN_GROUP: {
        CHARACTER: {
            space_characters: handle_insert_character,
            GENERIC: handle_in_column_group_character,
        },
        COMMENT: {
            GENERIC: insert_comment,
        },
        DOCTYPE: {
            GENERIC: parse_error_ignore_token,
        },
        START_TAG: {
            "html": handle_start_tag_htlm,
            "col": handle_in_column_group_start_col,
        },
        END_TAG: {
            "colgroup": handle_in_column_group_end_colgroup,
            "col": parse_error_ignore_token,
        },
        EOF: {
            GENERIC: lambda parser, token,: handle_reproces_token(parser, token,InsertionMode.IN_BODY),
        },
        "FALLBACK": handle_in_column_group_anything_else,
    },
    InsertionMode.IN_TABLE_BODY: {
        START_TAG: {
            "html": handle_start_tag_htlm,
            "tr": handle_in_table_body_start_tr,
            ("th", "td"): handle_in_table_body_start_th_td,
            ("caption", "col", "colgroup", "tbody", "tfoot", "thead"): handle_end_tag_table_row_group,
        },
        END_TAG: {
            ("tbody", "tfoot", "thead"): handle_in_table_body_end_tbody_tfoot_thead,
            "table": handle_end_tag_table,
            ("body", "caption", "col", "colgroup", "html", "td", "th", "tr"): parse_error_ignore_token,
        },
        "FALLBACK": handle_in_table_body_anything_else
    },
    InsertionMode.IN_ROW: {
        START_TAG: {
            "html": handle_start_tag_htlm,
            ("th", "td"): handle_in_row_start_th_td,
            ("caption", "col", "colgroup", "tbody", "tfoot", "thead", "tr"): handle_in_row_start_the_table_stuff,
        },
        END_TAG: {
            "tr": handle_in_row_end_tr,
            "table": handle_in_row_end_table,
            ("tbody", "tfoot", "thead"): handle_in_row_end_tbody_tfoot_thead,
            ("body", "caption", "col", "colgroup", "html", "td", "th"): parse_error_ignore_token,
        },
        "FALLBACK": handle_in_row_anything_else
    },
    InsertionMode.IN_CELL: {
        START_TAG: {
            "html": handle_start_tag_htlm,
            ("caption", "col", "colgroup", "tbody", "td", "tfoot", "th", "thead", "tr"): handle_in_cell_start_caption_col_colgroup_tbody_td_tfoot_th_thead_tr,
        },
        END_TAG: {
            ("td", "th"): handle_in_cell_end_td_th,
            ("body", "caption", "col", "colgroup", "html"): handle_in_cell_end_tag_ignored,
            ("table", "tbody", "tfoot", "thead", "tr"): handle_in_cell_end_table_tbody_tfoot_thead_tr,
        },
        "FALLBACK": lambda parser, token,: handle_reproces_token(parser, token,InsertionMode.IN_BODY)
    },
    InsertionMode.IN_SELECT: {
        CHARACTER: {
            GENERIC: handle_insert_character_inselect,
        },
        COMMENT: {
            GENERIC: insert_comment,
        },
        DOCTYPE: {
            GENERIC: parse_error_ignore_token,
        },
        START_TAG: {
            "html": handle_start_tag_htlm,
            "option": handle_in_select_start_option,
            "optgroup": handle_in_select_start_optgroup,
            "hr": handle_in_select_start_hr,
            "select": handle_in_select_start_select,
            "script": lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_HEAD),
            ("input", "keygen", "textarea"): handle_in_select_start_input_keygen_textarea,
        },
        END_TAG: {
            "optgroup": handle_in_select_end_optgroup,
            "option": handle_in_select_end_option,
            "select": handle_in_select_end_select,
        },
        EOF: {
            GENERIC: lambda parser, token,: handle_reproces_token(parser, token,InsertionMode.IN_BODY),
        },
        "FALLBACK": parse_error_ignore_token
    },
    InsertionMode.IN_SELECT_IN_TABLE: {
        START_TAG: {
            ("caption", "table", "tbody", "tfoot", "thead", "tr", "td", "th"): handle_in_select_in_table_start_ctable,
        },
        END_TAG: {
            ("caption", "table", "tbody", "tfoot", "thead", "tr", "td", "th"): handle_in_select_in_table_end_ctable,
        },
        "FALLBACK": lambda parser, token,: handle_reproces_token(parser, token,InsertionMode.IN_SELECT)

    },
    InsertionMode.AFTER_BODY: {
        CHARACTER: {
            space_characters: lambda parser, token,: handle_reproces_token(parser, token,InsertionMode.IN_BODY),
        },
        COMMENT: {
            GENERIC: handle_after_body_comment,
        },
        DOCTYPE: {
            GENERIC: parse_error_ignore_token,
        },
        START_TAG: {
            "html": lambda parser, token,: handle_reproces_token(parser, token,InsertionMode.IN_BODY),
        },
        END_TAG: {
            "html": handle_after_body_endtag_html,
        },
        EOF: {
            GENERIC: handle_after_body_eof,
        },
        "FALLBACK": handle_after_body_anything_else,
    },
    InsertionMode.IN_FRAMESET: {
        CHARACTER: {
            space_characters: handle_insert_character,
        },
        COMMENT: {
            GENERIC: insert_comment,
        },
        DOCTYPE: {
            GENERIC: parse_error_ignore_token,
        },
        START_TAG: {
            "html": handle_start_tag_htlm,
            "frameset": handle_in_frameset_start_frameset,
            "frame": handle_in_frameset_start_frame,
            "noframes": handle_in_frameset_start_noframes,
        },
        END_TAG: {
            "frameset": handle_in_frameset_end_frameset,
        },
        EOF: {
            GENERIC: handle_in_frameset_eof,
        },
        "FALLBACK": handle_in_frameset_anything_else
    },
    InsertionMode.AFTER_FRAMESET: {
        CHARACTER: {
            space_characters: handle_insert_character,
        },
        COMMENT: {
            GENERIC: insert_comment,
        },
        DOCTYPE: {
            GENERIC: parse_error_ignore_token,
        },
        START_TAG: {
            "html": handle_start_tag_htlm,
            "noframes": handle_after_frameset_start_noframes,
        },
        END_TAG: {
            "html": handle_after_frameset_end_html,
        },
        EOF: {
            GENERIC: ignore_handler,
        },
        "FALLBACK": parse_error_ignore_token
    },
    InsertionMode.AFTER_AFTER_BODY: {
        CHARACTER: {
            space_characters: lambda parser, token,: handle_reproces_token(parser, token,InsertionMode.IN_BODY),
        },
        COMMENT: {
            GENERIC: handle_after_after_body_comment,
        },
        DOCTYPE: {
            GENERIC: lambda parser, token,: handle_reproces_token(parser, token,InsertionMode.IN_BODY),
        },
        START_TAG: {
            "html": lambda parser, token,: handle_reproces_token(parser, token,InsertionMode.IN_BODY),
        },
        EOF: {
            GENERIC: ignore_handler,
        },
        "FALLBACK": handle_after_after_body_anything_else
    },
    InsertionMode.AFTER_AFTER_FRAMESET: {
        CHARACTER: {
            space_characters: lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_BODY),
        },
        COMMENT: {
            GENERIC: handle_after_after_frameset_comment,
        },
        DOCTYPE: {
            GENERIC: lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_BODY)
        },
        START_TAG: {
            "html": lambda parser, token,: handle_reproces_token(parser, token, InsertionMode.IN_BODY),
            "noframes": handle_after_after_frameset_start_noframes,
        },
        EOF: {
            GENERIC: ignore_handler,
        },
        "FALLBACK": parse_error_ignore_token
    },
    InsertionMode.FOREIGN_CONTENT: {
        CHARACTER: {
            GENERIC: handle_character_foreign_content,
        },
        COMMENT: {
            GENERIC: insert_comment,
        },
        DOCTYPE: {
            GENERIC: handle_doctype_foreign_content
        },
        START_TAG: {
            GENERIC:handle_start_tag_foreign_content
        },
        END_TAG: {
            GENERIC:handle_end_tag_foreign_content
        },
        "FALLBACK": parse_error_ignore_token
    }
}

def get_token_pattern(token: Token):
    if token.type == CHARACTER:
        if token.space_character:
            return space_characters
        return GENERIC

    if token.type in (START_TAG, END_TAG):
        return token.lower_name

    return GENERIC


class NestedDispatchTable:
    def __init__(self, mode_mapping: dict):
        self.handlers_by_type = {}
        self.fallback = None

        for key, value in mode_mapping.items():
            if key == "FALLBACK":
                self.fallback = value
            else:
                self.handlers_by_type[key] = value

    def lookup(self, token: Token) -> Optional[Callable]:
        type_map = self.handlers_by_type.get(token.type)
        if not type_map:
            return self.fallback

        pattern = get_token_pattern(token)

        if pattern in type_map:
            return type_map[pattern]

        for k, handler in type_map.items():
            if isinstance(k, tuple) and pattern in k:
                return handler

        if GENERIC in type_map:
            return type_map[GENERIC]

        return self.fallback

PRECOMPUTED_DISPATCH: Dict[InsertionMode, NestedDispatchTable] = {}

for mode, mode_mapping in MODE_DISPATCH.items():
    dt = NestedDispatchTable(mode_mapping)
    PRECOMPUTED_DISPATCH[mode] = dt

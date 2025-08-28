# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from collections import deque
from textwizard.utils.tw_html_parser.entities_wrapper import lookup_entity_value_py  # type: ignore
from textwizard.utils.tw_html_parser._utils import ascii_letters, ascii_uppercase, space_characters, null_character ,entitiesWindows1252, namespaces,hex_digit
from textwizard.utils.tw_html_parser.error import  ParseError
from textwizard.utils.tw_html_parser.tokens import Token, Attribute ,CHARACTER, START_TAG, END_TAG, COMMENT, DOCTYPE, EOF
from typing import Optional
import re


class TokenizerState:
    DATA_STATE = 0
    RCDATA_STATE = 1
    RAWTEXT_STATE = 2
    SCRIPT_DATA_STATE = 3
    PLAINTEXT_STATE = 4
    TAG_OPEN_STATE = 5
    END_TAG_OPEN_STATE = 6
    TAG_NAME_STATE = 7
    RCDATA_LESS_THAN_SIGN_STATE = 8
    RCDATA_END_TAG_OPEN_STATE = 9
    RCDATA_END_TAG_NAME_STATE = 10
    RAWTEXT_LESS_THAN_SIGN_STATE = 11
    RAWTEXT_END_TAG_OPEN_STATE = 12
    RAWTEXT_END_TAG_NAME_STATE = 13
    SCRIPT_DATA_LESS_THAN_SIGN_STATE = 14
    SCRIPT_DATA_END_TAG_OPEN_STATE = 15
    SCRIPT_DATA_END_TAG_NAME_STATE = 16
    SCRIPT_DATA_ESCAPE_START_STATE = 17
    SCRIPT_DATA_ESCAPE_START_DASH_STATE = 18
    SCRIPT_DATA_ESCAPED_STATE = 19
    SCRIPT_DATA_ESCAPED_DASH_STATE = 20
    SCRIPT_DATA_ESCAPED_DASH_DASH_STATE = 21
    SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN_STATE = 22
    SCRIPT_DATA_ESCAPED_END_TAG_OPEN_STATE = 23
    SCRIPT_DATA_ESCAPED_END_TAG_NAME_STATE = 24
    SCRIPT_DATA_DOUBLE_ESCAPE_START_STATE = 25
    SCRIPT_DATA_DOUBLE_ESCAPED_STATE = 26
    SCRIPT_DATA_DOUBLE_ESCAPED_DASH_STATE = 27
    SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH_STATE = 28
    SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN_STATE = 29
    SCRIPT_DATA_DOUBLE_ESCAPE_END_STATE = 30
    BEFORE_ATTRIBUTE_NAME_STATE = 31
    ATTRIBUTE_NAME_STATE = 32
    AFTER_ATTRIBUTE_NAME_STATE = 33
    BEFORE_ATTRIBUTE_VALUE_STATE = 34
    ATTRIBUTE_VALUE_DOUBLE_QUOTED_STATE = 35
    ATTRIBUTE_VALUE_SINGLE_QUOTED_STATE = 36
    ATTRIBUTE_VALUE_UNQUOTED_STATE = 37
    AFTER_ATTRIBUTE_VALUE_STATE = 38
    SELF_CLOSING_START_TAG_STATE = 39
    BOGUS_COMMENT_STATE = 40
    MARKUP_DECLARATION_OPEN_STATE = 41
    COMMENT_START_STATE = 42
    COMMENT_START_DASH_STATE = 43
    COMMENT_STATE = 44
    COMMENT_LESS_THAN_SIGN_BANG_STATE=45
    COMMENT_LESS_THAN_SIGN_BANG_DASH_STATE=46
    COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH_STATE=47
    COMMENT_END_DASH_STATE=48
    COMMENT_END_STATE=49
    COMMENT_END_BANG_STATE=50
    DOCTYPE_STATE = 51
    BEFORE_DOCTYPE_NAME_STATE = 52
    DOCTYPE_NAME_STATE = 53
    AFTER_DOCTYPE_NAME_STATE = 54
    AFTER_DOCTYPE_PUBLIC_KEYWORD_STATE = 55
    BEFORE_DOCTYPE_PUBLIC_IDENTIFIER_STATE = 56
    DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED_STATE = 57
    DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED_STATE = 58
    AFTER_DOCTYPE_PUBLIC_IDENTIFIER_STATE = 59
    BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS_STATE = 60
    AFTER_DOCTYPE_SYSTEM_KEYWORD_STATE = 61
    BEFORE_DOCTYPE_SYSTEM_IDENTIFIER_STATE = 62
    DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED_STATE = 63
    DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED_STATE = 64
    AFTER_DOCTYPE_SYSTEM_IDENTIFIER_STATE = 65
    BOGUS_DOCTYPE_STATE = 66
    CDATA_SECTION_STATE = 67



ALPHABET_SIZE = 128
EXTENDED_INDEX = ALPHABET_SIZE
EOF_INDEX = ALPHABET_SIZE + 1
NUM_INDICES = ALPHABET_SIZE + 2

NUM_STATES = 68
MIN_LEN_ENTITY = 2
MAX_LEN_ENTITY = 32



_raw_chars_regex = re.compile(r'[^<&\x00]+')
_read_tag_name_regex = re.compile(r'[^' + re.escape(''.join(sorted(space_characters | {'/', '>'})) + '\x00') + r']+')
_chars_until_lt = re.compile(r'[^<&\x00]+')
_chars_no_stop = re.compile(r'[^\x00]+')

SETUP_REGISTRY = []
_CHAR_TO_INDEX_CACHE = {chr(i): i for i in range(ALPHABET_SIZE)}
EOF_STATE=None


def register_setup(priority=NUM_STATES):
    def decorator(func):
        SETUP_REGISTRY.append((priority, func))
        return func

    return decorator

class TWHTMLTokenizer:
    __slots__ = (
        "text", "parser", "length", "position", "state", "tokens",
        "temp_buffer", "current_token", "errors",
        "appropriate_end_tag_name", "check_action_transition",
        "_reconsume_current_input", "drop_duplicate_attributes",
        "next_state", "actions", "eof_action","emit_character","emit_token",
        "emit_token_oef", "reconsume_in_state","log_error"
    )


    _dfa_built = False
    _next_state_table = None
    _actions_table = None

    @classmethod
    def build_static_dfa(cls):
        if not cls._dfa_built:
            next_state = [[None] * NUM_INDICES for _ in range(NUM_STATES)]
            actions = [[None] * NUM_INDICES for _ in range(NUM_STATES)]

            dummy = cls.__new__(cls)
            dummy.next_state = next_state
            dummy.actions = actions
            dummy.eof_action = [None] * NUM_STATES
            for priority, func in sorted(SETUP_REGISTRY, key=lambda x: x[0]):
                func(dummy)
            cls._next_state_table = next_state
            cls._actions_table = actions
            cls._dfa_built = True

    def __init__(self, text, parser=None, initial_state=TokenizerState.DATA_STATE, position=0, drop_duplicate_attributes=False):
        self.text = self.sanitize_input(text)
        self.parser = parser
        self.length = len(self.text)
        self.position = position
        self.state = initial_state
        self.tokens = deque()
        self.temp_buffer = []
        self.current_token = None
        self.errors = deque()
        self.appropriate_end_tag_name = None
        self.check_action_transition = False
        self._reconsume_current_input = False
        self.drop_duplicate_attributes = drop_duplicate_attributes


        self.__class__.build_static_dfa()
        self.next_state = self.__class__._next_state_table
        self.actions = self.__class__._actions_table

        self.emit_character = self._emit_character
        self.emit_token = self._emit_token
        self.emit_token_oef = self._emit_token_oef

        self.reconsume_in_state = self._reconsume_in_state
        self.log_error = self._log_error

    def tokenize(self):
        text = self.text
        length = self.length
        char_cache = _CHAR_TO_INDEX_CACHE
        next_state = self.next_state
        actions = self.actions
        state = self.state
        pos = self.position

        while True:
            if pos < length:
                current_char = text[pos]
                code = char_cache.get(current_char, EXTENDED_INDEX)
            else:
                current_char = None
                code = EOF_INDEX

            old_state = state
            ns = next_state[state][code]
            act = actions[state][code]

            if act:
                act(self, current_char)
                state = self.state
                pos = self.position

            if state == old_state:
                state = ns

            while self.tokens:
                yield self.tokens.popleft()

            if code == EOF_INDEX:
                break

            if self._reconsume_current_input:
                self._reconsume_current_input = False
                state = self.state

            pos += 1
            self.state = state
            self.position = pos

        self.emit_token_oef(Token(type=EOF))
        while self.tokens:
            yield self.tokens.popleft()

    def __iter__(self):
        return self.tokenize()

    @staticmethod
    def sanitize_input(data: str) -> str:
        data = data.replace('\r\n', '\n')
        data = data.replace('\r', '\n')
        return data

    def tokenize_all(self):
        tokens = list(self.tokenize())
        return tokens

    def current_namespace(self) -> Optional[str]:
        if self.parser.open_elements:
            if self.parser and hasattr(self.parser, "current_node"):
                return self.parser.open_elements[-1].namespace
        return None


    def _log_error(self, error_code, position=None):
        if not isinstance(error_code, ParseError):
            raise ValueError("Invalid error code passed. Must be an instance of ParseError.")
        if position is None:
            position = self.position
        self.errors.append(f"[Error at position {position}] {error_code.code()}: {error_code.description()}")

    @staticmethod
    def emit_current_token(tokenizer, ch):
        tokenizer.emit_token(tokenizer.current_token)

    def _emit_token(self, token: Token):
        self.tokens.append(token)

    def _emit_character(self, char,is_space=False):
        token = Token(
            type=CHARACTER,
            data=char,
            space_character=is_space,
            null_character=char in null_character
        )
        self.tokens.append(token)

    def _emit_token_oef(self, token: Token):
        self.tokens.append(token)

    @staticmethod
    def emit_and_reset_buffer(tokenizer, ch):
        if tokenizer.temp_buffer:
            if tokenizer.temp_buffer:
                text = ''.join(tokenizer.temp_buffer)
                if text:
                    if (tokenizer.current_token and
                            tokenizer.current_token.type == CHARACTER):
                        tokenizer.current_token.data += text
                        tokenizer.temp_buffer = []
                    elif (tokenizer.tokens and
                          tokenizer.tokens[-1].type == CHARACTER):
                        tokenizer.tokens[-1].data += text
                        tokenizer.temp_buffer = []
                    else:
                        tokenizer.emit_character(text)

                tokenizer.temp_buffer = []
        tokenizer.temp_buffer = []

    @staticmethod
    def emit_current_char(tokenizer, ch):
        tokenizer.emit_character(ch)

    @staticmethod
    def reset_buffer(tokenizer, ch):
        tokenizer.temp_buffer = []

    def get_buffer(self):
        return ''.join(self.temp_buffer)

    def append_to_buffer(self, value):
        if isinstance(value, str):
            self.temp_buffer.extend(value)
        elif isinstance(value, (list, tuple)):
            self.temp_buffer.extend(value)
        else:
            self.temp_buffer.append(value)

    def _reconsume_in_state(self, new_state):
        self.position -= 1
        self.state = new_state

    @staticmethod
    def read_raw_characters_in_blocks(tokenizer, ch):
        pos = tokenizer.position
        length = tokenizer.length
        text = tokenizer.text
        buf = tokenizer.temp_buffer
        pattern = _raw_chars_regex

        while pos < length:
            m = pattern.match(text, pos)
            if m is not None:
                block = m.group()
                buf.append(block)
                pos = m.end()
            if pos >= length:
                break
            c = text[pos]
            if c == '<':
                pos -= 1
                break
            elif c == '&':
                tokenizer.position = pos
                tokenizer.handle_character_reference(tokenizer, c)
                pos = tokenizer.position + 1
                continue
            elif c == '\x00':
                tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
                buf.append("\uFFFD")
                pos += 1
            else:
                buf.append(c)
                pos += 1

        tokenizer.position = pos
        if buf:
            token_text = ''.join(buf)
            is_space = all(ch in space_characters for ch in token_text)
            tokenizer.emit_character(token_text, is_space)
            buf.clear()


    @staticmethod
    def read_characters_in_blocks(tokenizer, ch, stop):
        pos = tokenizer.position
        length = tokenizer.length
        text = tokenizer.text
        buf = tokenizer.temp_buffer
        regex = stop

        while pos < length:
            m = regex.match(text, pos)
            if m is not None:
                block = m.group()
                buf.append(block)
                pos = m.end()
            if pos >= length:
                break
            c = text[pos]
            if c == '<':
                pos -= 1
                break
            elif c == '\x00':
                tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
                buf.append("\uFFFD")
                pos += 1
            else:
                buf.append(c)
                pos += 1

        tokenizer.position = pos
        if buf:
            token_text = ''.join(buf)
            is_space = all(ch in space_characters for ch in token_text)
            tokenizer.emit_character(token_text, is_space)
            buf.clear()


    @staticmethod
    def read_chars_until_lt(tokenizer, ch):
        return tokenizer.read_characters_in_blocks(tokenizer, ch, _chars_until_lt)

    @staticmethod
    def read_chars_no_stop(tokenizer, ch):
        return tokenizer.read_characters_in_blocks(tokenizer, ch, _chars_no_stop)

    # -------------------------------------------------------------------------
    # Set Transition
    # -------------------------------------------------------------------------
    def set_transition(self, state_from: int, input_char: str | None, state_to: int | None = None, action=None):
        if input_char is None:
            idx = EOF_INDEX
        else:
            code = ord(input_char)
            if code < ALPHABET_SIZE:
                idx = code
            else:
                idx = EXTENDED_INDEX
        self.next_state[state_from][idx] = state_to
        self.actions[state_from][idx] = action

    def set_action_transition(self, state_from: int, input_char: str|None, action):
        if input_char is None:
            idx = EOF_INDEX
        else:
            code = ord(input_char)
            if code < ALPHABET_SIZE:
                idx = code
            else:
                idx = EXTENDED_INDEX

        self.next_state[state_from][idx] = None
        self.actions[state_from][idx] = action

    def set_default_transition(self, state: int, default_state: int | None = None, default_action=None):
        for char_code in range(ALPHABET_SIZE):
            if self.next_state[state][char_code] is None:
                self.next_state[state][char_code] = default_state if default_state is not None else state
                if self.actions[state][char_code] is None and default_action is not None:
                    self.actions[state][char_code] = default_action

        if self.next_state[state][EXTENDED_INDEX] is None:
            self.next_state[state][EXTENDED_INDEX] = default_state if default_state is not None else state
            if self.actions[state][EXTENDED_INDEX] is None and default_action is not None:
                self.actions[state][EXTENDED_INDEX] = default_action

    # -------------------------------------------------------------------------
    # Action Handlers
    # -------------------------------------------------------------------------

    @staticmethod
    def append_buffer_current_character(tokenizer, ch):
        tokenizer.append_to_buffer(ch)

    @staticmethod
    def append_buffer_current_lower_character(tokenizer, ch):
        lower = ch.lower()
        tokenizer.append_to_buffer(lower)

    @staticmethod
    def handle_null_in_state(tokenizer, ch):
        tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
        tokenizer.emit_character(f"{tokenizer.get_buffer()}\uFFFD")

    @staticmethod
    def handle_commit_attribute_name(tokenizer, ch):
        if not tokenizer.current_token or not tokenizer.current_token.attributes:
            return

        last_attr = tokenizer.current_token.attributes[-1]
        last_name_lower = last_attr.name.lower()

        for attr in tokenizer.current_token.attributes[:-1]:
            if attr.name.lower() == last_name_lower:
                tokenizer.log_error(ParseError.DUPLICATE_ATTRIBUTE)
                if tokenizer.drop_duplicate_attributes:
                    tokenizer.current_token.attributes.pop()
                break

    @staticmethod
    def handle_appropriate_end_tag_name(tokenizer, ch, next_state, else_state, emit=False):
        buffer_value = tokenizer.get_buffer().lower()

        if isinstance(tokenizer.appropriate_end_tag_name, str):
            is_valid = buffer_value == tokenizer.appropriate_end_tag_name
        elif isinstance(tokenizer.appropriate_end_tag_name, tuple):
            is_valid = buffer_value in tokenizer.appropriate_end_tag_name
        else:
            is_valid = False

        if is_valid:
            tokenizer.current_token = Token(type=END_TAG, name=tokenizer.get_buffer())
            if emit:
                tokenizer.emit_current_token(tokenizer, ch)
            tokenizer.reset_buffer(tokenizer, ch)
            tokenizer.state = next_state
        else:
            appended_text = "</" + tokenizer.get_buffer()
            tokenizer.emit_character(appended_text)
            tokenizer.reset_buffer(tokenizer, ch)
            tokenizer.reconsume_in_state(else_state)
            tokenizer.state = else_state

        tokenizer.check_action_transition = True

    @staticmethod
    def handle_default_rcdata_end_tag(tokenizer, ch, next_state):
        appended_text = "</" + tokenizer.get_buffer()
        tokenizer.emit_character(appended_text)
        tokenizer.reset_buffer(tokenizer, ch)
        tokenizer.reconsume_in_state(next_state)

    # -------------------------------------------------------------------------
    # OEF
    # -------------------------------------------------------------------------

    @staticmethod
    def handle_eof_in_tag_open(tokenizer, ch):
        tokenizer.log_error(ParseError.EOF_BEFORE_TAG_NAME)
        tokenizer.append_to_buffer("<")
        tokenizer.emit_and_reset_buffer(tokenizer, ch)

    @staticmethod
    def handle_eof_in_end_tag_open_state(tokenizer, ch):
        tokenizer.log_error(ParseError.EOF_BEFORE_TAG_NAME)
        tokenizer.emit_character("</")

    @staticmethod
    def handle_eof_in_tag_name(tokenizer, ch):
        tokenizer.log_error(ParseError.EOF_BEFORE_TAG_NAME)

    @staticmethod
    def handle_eof_in_scrip(tokenizer, ch):
        tokenizer.log_error(ParseError.EOF_IN_SCRIPT_HTML_COMMENT_LIKE_TEXT)

    @staticmethod
    def handle_eof_in_after_attr_name(tokenizer, ch):
        tokenizer.handle_commit_attribute_name(tokenizer, ch)
        tokenizer.log_error(ParseError.EOF_IN_TAG)

    @staticmethod
    def handle_eof_in_tag(tokenizer, ch):
        tokenizer.log_error(ParseError.EOF_IN_TAG)

    @staticmethod
    def handle_eof_in_bogus_comment_state(tokenizer, ch):
        tokenizer.log_error(ParseError.EOF_IN_TAG)
        tokenizer.emit_current_token(tokenizer, ch)

    @staticmethod
    def handle_eof_in_comment(tokenizer, ch):
        tokenizer.emit_current_token(tokenizer, ch)
        tokenizer.log_error(ParseError.EOF_IN_COMMENT)

    @staticmethod
    def handle_eof_in_doctype_state(tokenizer, ch):
        tokenizer.log_error(ParseError.EOF_IN_DOCTYPE)
        doctype_token = Token(type=DOCTYPE, quirks_mode=True)
        tokenizer.emit_token(doctype_token)

    @staticmethod
    def handle_eof_in_doctype(tokenizer, ch):
        tokenizer.log_error(ParseError.EOF_IN_DOCTYPE)
        if tokenizer.current_token:
            tokenizer.current_token.quirks_mode = True
        tokenizer.emit_current_token(tokenizer, ch)

    @staticmethod
    def handle_eof_in_bogus(tokenizer, ch):
        if not tokenizer.current_token:
            doctype_token = Token(type=DOCTYPE, quirks_mode=True)
            tokenizer.emit_token(doctype_token)
        else:
            tokenizer.emit_current_token(tokenizer, ch)

    @staticmethod
    def handle_eof_in_cdata(tokenizer, ch):
        tokenizer.log_error(ParseError.EOF_IN_CDATA)


# -------------------------------------------------------------------------
# STATES
# -------------------------------------------------------------------------

    @register_setup(priority=0)
    def setup_data_state(self):
        self.set_transition(TokenizerState.DATA_STATE, '<', TokenizerState.TAG_OPEN_STATE)
        self.set_transition(TokenizerState.DATA_STATE, '\x00', TokenizerState.DATA_STATE, action=TWHTMLTokenizer.handle_null_in_state)
        self.set_default_transition(TokenizerState.DATA_STATE, default_state=TokenizerState.DATA_STATE, default_action=TWHTMLTokenizer.read_raw_characters_in_blocks)
        self.set_transition(TokenizerState.TAG_OPEN_STATE, EOF_STATE, None,TWHTMLTokenizer.emit_and_reset_buffer)

    @register_setup(priority=1)
    def setup_rcdata_state(self):
        self.set_transition(TokenizerState.RCDATA_STATE, '<', TokenizerState.RCDATA_LESS_THAN_SIGN_STATE)
        self.set_transition(TokenizerState.RCDATA_STATE, '\x00', TokenizerState.RCDATA_STATE, action=TWHTMLTokenizer.handle_null_in_state)
        self.set_default_transition(TokenizerState.RCDATA_STATE, default_state=TokenizerState.RCDATA_STATE, default_action=TWHTMLTokenizer.read_raw_characters_in_blocks)

    @register_setup(priority=2)
    def setup_rawtext_state(self):
        self.set_transition(TokenizerState.RAWTEXT_STATE, '<', TokenizerState.RAWTEXT_LESS_THAN_SIGN_STATE)
        self.set_transition(TokenizerState.RAWTEXT_STATE, '\x00', TokenizerState.RAWTEXT_STATE, action=TWHTMLTokenizer.handle_null_in_state)
        self.set_default_transition(TokenizerState.RAWTEXT_STATE, default_state=TokenizerState.RAWTEXT_STATE, default_action=TWHTMLTokenizer.read_chars_until_lt)

    @register_setup(priority=3)
    def setup_script_data_state(self):
        self.set_transition(TokenizerState.SCRIPT_DATA_STATE, '<', TokenizerState.SCRIPT_DATA_LESS_THAN_SIGN_STATE)
        self.set_transition(TokenizerState.SCRIPT_DATA_STATE, '\x00', TokenizerState.SCRIPT_DATA_STATE, action=TWHTMLTokenizer.handle_null_in_state)
        self.set_default_transition(TokenizerState.SCRIPT_DATA_STATE, default_state=TokenizerState.SCRIPT_DATA_STATE, default_action=TWHTMLTokenizer.read_chars_until_lt)

    @register_setup(priority=4)
    def setup_plaintext_state(self):
        self.set_transition(TokenizerState.PLAINTEXT_STATE, '\x00', TokenizerState.PLAINTEXT_STATE, action=TWHTMLTokenizer.handle_null_in_state)
        self.set_default_transition(TokenizerState.PLAINTEXT_STATE, default_state=TokenizerState.PLAINTEXT_STATE, default_action=TWHTMLTokenizer.read_chars_no_stop)

    @register_setup(priority=5)
    def setup_tag_open_state(self):

        def handle_start_tag(tokenizer, ch):
            tokenizer.current_token = Token(type=START_TAG, name='', attributes=[])
            tokenizer.reconsume_in_state(TokenizerState.TAG_NAME_STATE)

        def handle_unexpected_question_mark(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_QUESTION_MARK_INSTEAD_OF_TAG_NAME)
            tokenizer.current_token = Token(type=COMMENT, data="")
            tokenizer.reconsume_in_state(TokenizerState.BOGUS_COMMENT_STATE)

        def handle_invalid_tag_open(tokenizer, ch):
            tokenizer.log_error(ParseError.INVALID_FIRST_CHARACTER_OF_TAG_NAME)
            tokenizer.append_to_buffer("<")
            tokenizer.reconsume_in_state(TokenizerState.DATA_STATE)

        self.set_transition(TokenizerState.TAG_OPEN_STATE, '!', TokenizerState.MARKUP_DECLARATION_OPEN_STATE)
        self.set_transition(TokenizerState.TAG_OPEN_STATE, '/', TokenizerState.END_TAG_OPEN_STATE)

        for char in ascii_letters:
            self.set_transition(TokenizerState.TAG_OPEN_STATE, char, TokenizerState.TAG_NAME_STATE, action=handle_start_tag)

        self.set_transition(TokenizerState.TAG_OPEN_STATE, '?', TokenizerState.BOGUS_COMMENT_STATE, action=handle_unexpected_question_mark)
        self.set_default_transition(TokenizerState.TAG_OPEN_STATE,TokenizerState.DATA_STATE,handle_invalid_tag_open)
        self.set_transition(TokenizerState.TAG_OPEN_STATE, EOF_STATE, None,TWHTMLTokenizer.handle_eof_in_tag_open)

    @register_setup(priority=6)
    def setup_end_tag_open_state(self):

        def handle_end_tag_name_start(tokenizer, ch):
            tokenizer.current_token = Token(type=END_TAG, name='', attributes=[])
            tokenizer.reconsume_in_state(TokenizerState.TAG_NAME_STATE)

        def handle_unexpected_greater_than(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_END_TAG_NAME)

        def handle_invalid_end_tag(tokenizer, ch):
            tokenizer.log_error(ParseError.INVALID_FIRST_CHARACTER_OF_TAG_NAME)
            tokenizer.current_token = Token(type=COMMENT, name='', attributes=[])
            tokenizer.reconsume_in_state(TokenizerState.BOGUS_COMMENT_STATE)

        for char in ascii_letters:
            self.set_transition(TokenizerState.END_TAG_OPEN_STATE, char, TokenizerState.TAG_NAME_STATE, action=handle_end_tag_name_start)

        self.set_transition(TokenizerState.END_TAG_OPEN_STATE, '>', TokenizerState.DATA_STATE, action=handle_unexpected_greater_than)
        self.set_default_transition(TokenizerState.END_TAG_OPEN_STATE, TokenizerState.BOGUS_COMMENT_STATE, handle_invalid_end_tag)
        self.set_transition(TokenizerState.END_TAG_OPEN_STATE, EOF_STATE, None,TWHTMLTokenizer.handle_eof_in_end_tag_open_state)

    @register_setup(priority=7)
    def setup_tag_name_state(self):

        def read_tag_name(tokenizer, ch):
            pos = tokenizer.position
            length = tokenizer.length
            text = tokenizer.text
            buf = []
            stops = space_characters | {'/', '>'}

            while pos < length:
                m = _read_tag_name_regex.match(text, pos)
                if m:
                    part = m.group()
                    buf.append(part)
                    pos = m.end()
                    if pos < length:
                        c = text[pos]
                        if c in stops:
                            pos -= 1
                            break
                        elif c == '\x00':
                            buf.append("\uFFFD")
                            pos += 1
                    else:
                        break
                else:
                    c = text[pos]
                    if c in stops:
                        pos -= 1
                        break
                    elif c == '\x00':
                        buf.append("\uFFFD")
                    else:
                        buf.append(c)
                    pos += 1

            tokenizer.position = pos
            tokenizer.current_token.name += "".join(buf)


        def handle_null(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            tokenizer.current_token.name+="\uFFFD"

        for char in space_characters:
            self.set_transition(TokenizerState.TAG_NAME_STATE, char, TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE)

        self.set_transition(TokenizerState.TAG_NAME_STATE, '/', TokenizerState.SELF_CLOSING_START_TAG_STATE)
        self.set_transition(TokenizerState.TAG_NAME_STATE, '>',TokenizerState.DATA_STATE, action=TWHTMLTokenizer.emit_current_token)

        self.set_transition(TokenizerState.TAG_NAME_STATE, '\x00', TokenizerState.TAG_NAME_STATE, action=handle_null)
        self.set_default_transition( TokenizerState.TAG_NAME_STATE,TokenizerState.TAG_NAME_STATE,read_tag_name)
        self.set_transition(TokenizerState.TAG_NAME_STATE, EOF_STATE, None,TWHTMLTokenizer.handle_eof_in_tag_name)


    @register_setup(priority=8)
    def setup_rcdata_less_than_sign_state(self):

        def emit_less_than(tokenizer, ch):
            tokenizer.emit_character('<')
            tokenizer.reconsume_in_state(TokenizerState.RCDATA_STATE)

        self.set_transition(TokenizerState.RCDATA_LESS_THAN_SIGN_STATE, '/', TokenizerState.RCDATA_END_TAG_OPEN_STATE)
        self.set_default_transition(TokenizerState.RCDATA_LESS_THAN_SIGN_STATE, TokenizerState.RCDATA_STATE, emit_less_than)
        self.set_transition(TokenizerState.RCDATA_LESS_THAN_SIGN_STATE, EOF_STATE, None,emit_less_than)

    @register_setup(priority=9)
    def setup_rcdata_end_tag_open_state(self):

        def emit_slash_and_reconsume(tokenizer, ch):
            tokenizer.emit_character('</')
            tokenizer.reconsume_in_state(TokenizerState.RCDATA_STATE)

        for char in ascii_letters:
            self.set_transition(TokenizerState.RCDATA_END_TAG_OPEN_STATE, char, TokenizerState.RCDATA_END_TAG_NAME_STATE, action=TWHTMLTokenizer.append_buffer_current_character)

        self.set_default_transition(TokenizerState.RCDATA_END_TAG_OPEN_STATE, TokenizerState.RCDATA_STATE, emit_slash_and_reconsume)
        self.set_transition(TokenizerState.RCDATA_END_TAG_OPEN_STATE, EOF_STATE, None,emit_slash_and_reconsume)

    @register_setup(priority=10)
    def setup_rcdata_end_tag_name_state(self):

        for sp in space_characters:
            self.set_action_transition(TokenizerState.RCDATA_END_TAG_NAME_STATE, sp, action=lambda tokenizer, ch: tokenizer.handle_appropriate_end_tag_name(tokenizer, ch, TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE,TokenizerState.RCDATA_STATE))

        self.set_action_transition(TokenizerState.RCDATA_END_TAG_NAME_STATE, '/', action=lambda tokenizer, ch: tokenizer.handle_appropriate_end_tag_name(tokenizer, ch, TokenizerState.SELF_CLOSING_START_TAG_STATE,TokenizerState.RCDATA_STATE))
        self.set_action_transition(TokenizerState.RCDATA_END_TAG_NAME_STATE, '>', action=lambda tokenizer, ch: tokenizer.handle_appropriate_end_tag_name(tokenizer, ch, TokenizerState.DATA_STATE,TokenizerState.RCDATA_STATE,True))

        for ch in ascii_letters:
            self.set_transition(TokenizerState.RCDATA_END_TAG_NAME_STATE, ch, TokenizerState.RCDATA_END_TAG_NAME_STATE, action=TWHTMLTokenizer.append_buffer_current_character)

        self.set_default_transition(TokenizerState.RCDATA_END_TAG_NAME_STATE, TokenizerState.RCDATA_STATE, lambda tokenizer, ch: tokenizer.handle_default_rcdata_end_tag(tokenizer, ch, TokenizerState.RCDATA_STATE))
        self.set_transition(TokenizerState.RCDATA_END_TAG_NAME_STATE, EOF_STATE, None,action=lambda tokenizer, ch: tokenizer.handle_default_rcdata_end_tag(tokenizer, ch, TokenizerState.RCDATA_STATE))


    @register_setup(priority=11)
    def setup_rawtext_less_than_sign_state(self):

        def handle_default(tokenizer, ch):
            tokenizer.emit_character("<")
            tokenizer.reconsume_in_state(TokenizerState.RAWTEXT_STATE)

        self.set_transition(TokenizerState.RAWTEXT_LESS_THAN_SIGN_STATE, '/', TokenizerState.RAWTEXT_END_TAG_OPEN_STATE, action=TWHTMLTokenizer.emit_and_reset_buffer)
        self.set_default_transition(TokenizerState.RAWTEXT_LESS_THAN_SIGN_STATE, TokenizerState.RAWTEXT_STATE, handle_default)
        self.set_transition(TokenizerState.RAWTEXT_LESS_THAN_SIGN_STATE, EOF_STATE, None,handle_default)

    @register_setup(priority=12)
    def setup_rawtext_end_tag_open_state(self):
        def handle_alpha(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.RAWTEXT_END_TAG_NAME_STATE)

        def handle_default(tokenizer, ch):
            tokenizer.append_to_buffer("</")
            tokenizer.reconsume_in_state(TokenizerState.RAWTEXT_STATE)

        for char in ascii_letters:
            self.set_transition(TokenizerState.RAWTEXT_END_TAG_OPEN_STATE, char, TokenizerState.RAWTEXT_END_TAG_NAME_STATE, action=handle_alpha)

        self.set_default_transition(TokenizerState.RAWTEXT_END_TAG_OPEN_STATE, TokenizerState.RAWTEXT_STATE, handle_default)
        self.set_transition(TokenizerState.RAWTEXT_END_TAG_OPEN_STATE, EOF_STATE, None,handle_default)

    @register_setup(priority=13)
    def setup_rawtext_end_tag_name_state(self):

        for char in space_characters:
            self.set_action_transition(TokenizerState.RAWTEXT_END_TAG_NAME_STATE, char, action=lambda tokenizer, ch: tokenizer.handle_appropriate_end_tag_name(tokenizer, ch, TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE,TokenizerState.RAWTEXT_STATE))

        self.set_action_transition(TokenizerState.RAWTEXT_END_TAG_NAME_STATE, "/", action=lambda tokenizer, ch: tokenizer.handle_appropriate_end_tag_name(tokenizer, ch, TokenizerState.SELF_CLOSING_START_TAG_STATE,TokenizerState.RAWTEXT_STATE))
        self.set_action_transition(TokenizerState.RAWTEXT_END_TAG_NAME_STATE, ">", action=lambda tokenizer, ch: tokenizer.handle_appropriate_end_tag_name(tokenizer, ch, TokenizerState.DATA_STATE,TokenizerState.RAWTEXT_STATE,True))

        for char in ascii_letters:
            self.set_transition(TokenizerState.RAWTEXT_END_TAG_NAME_STATE, char, TokenizerState.RAWTEXT_END_TAG_NAME_STATE, action=TWHTMLTokenizer.append_buffer_current_lower_character)

        self.set_default_transition(TokenizerState.RAWTEXT_END_TAG_NAME_STATE, TokenizerState.RCDATA_STATE, lambda tokenizer, ch: tokenizer.handle_default_rcdata_end_tag(tokenizer, ch, TokenizerState.RAWTEXT_STATE))
        self.set_transition(TokenizerState.RAWTEXT_END_TAG_NAME_STATE, EOF_STATE, None,action=lambda tokenizer, ch: tokenizer.handle_default_rcdata_end_tag(tokenizer, ch, TokenizerState.RAWTEXT_STATE))

    @register_setup(priority=14)
    def setup_script_data_less_than_sign_state(self):

        def handle_default(tokenizer, ch):
            tokenizer.emit_character("<")
            tokenizer.reconsume_in_state(TokenizerState.SCRIPT_DATA_STATE)

        def handle_append_buffer(tokenizer, ch):
            tokenizer.append_to_buffer("<!")
            tokenizer.emit_and_reset_buffer(tokenizer, ch)

        self.set_transition(TokenizerState.SCRIPT_DATA_LESS_THAN_SIGN_STATE, "/", TokenizerState.SCRIPT_DATA_END_TAG_OPEN_STATE,TWHTMLTokenizer.reset_buffer)
        self.set_transition(TokenizerState.SCRIPT_DATA_LESS_THAN_SIGN_STATE, "!", TokenizerState.SCRIPT_DATA_ESCAPE_START_STATE, handle_append_buffer)
        self.set_default_transition(TokenizerState.SCRIPT_DATA_LESS_THAN_SIGN_STATE, TokenizerState.SCRIPT_DATA_STATE, handle_default)
        self.set_transition(TokenizerState.SCRIPT_DATA_LESS_THAN_SIGN_STATE, EOF_STATE, None,handle_default)

    @register_setup(priority=15)
    def setup_script_data_end_tag_open_state(self):
        def handle_alpha(tokenizer, ch):
            tokenizer.current_token = Token(type=END_TAG, name='', attributes=[])
            tokenizer.reconsume_in_state(TokenizerState.SCRIPT_DATA_END_TAG_NAME_STATE)

        def handle_default(tokenizer, ch):
            tokenizer.emit_character("</")
            tokenizer.reconsume_in_state(TokenizerState.SCRIPT_DATA_STATE)

        for char in ascii_letters:
            self.set_transition(TokenizerState.SCRIPT_DATA_END_TAG_OPEN_STATE, char, TokenizerState.SCRIPT_DATA_END_TAG_NAME_STATE, action=handle_alpha)

        self.set_default_transition(TokenizerState.SCRIPT_DATA_END_TAG_OPEN_STATE, TokenizerState.SCRIPT_DATA_STATE, handle_default)
        self.set_transition(TokenizerState.SCRIPT_DATA_END_TAG_OPEN_STATE, EOF_STATE, None,handle_default)

    @register_setup(priority=16)
    def setup_script_data_end_tag_name_state(self):
        for char in space_characters:
            self.set_action_transition(TokenizerState.SCRIPT_DATA_END_TAG_NAME_STATE, char, action=lambda tokenizer, ch: tokenizer.handle_appropriate_end_tag_name(tokenizer, ch, TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE,TokenizerState.SCRIPT_DATA_STATE))

        self.set_action_transition(TokenizerState.SCRIPT_DATA_END_TAG_NAME_STATE, "/", action=lambda tokenizer, ch: tokenizer.handle_appropriate_end_tag_name(tokenizer, ch, TokenizerState.SELF_CLOSING_START_TAG_STATE,TokenizerState.SCRIPT_DATA_STATE))
        self.set_action_transition(TokenizerState.SCRIPT_DATA_END_TAG_NAME_STATE, ">", action=lambda tokenizer, ch: tokenizer.handle_appropriate_end_tag_name(tokenizer, ch, TokenizerState.DATA_STATE,TokenizerState.SCRIPT_DATA_STATE,True))

        for char in ascii_letters:
            self.set_transition(TokenizerState.SCRIPT_DATA_END_TAG_NAME_STATE, char, TokenizerState.SCRIPT_DATA_END_TAG_NAME_STATE, action=TWHTMLTokenizer.append_buffer_current_character)

        self.set_default_transition(TokenizerState.SCRIPT_DATA_END_TAG_NAME_STATE, TokenizerState.RCDATA_STATE, lambda tokenizer, ch: tokenizer.handle_default_rcdata_end_tag(tokenizer, ch, TokenizerState.SCRIPT_DATA_STATE))
        self.set_transition(TokenizerState.SCRIPT_DATA_END_TAG_NAME_STATE, EOF_STATE, None,action=lambda tokenizer, ch: tokenizer.handle_default_rcdata_end_tag(tokenizer, ch, TokenizerState.SCRIPT_DATA_STATE))

    @register_setup(priority=17)
    def setup_script_data_escape_start_state(self):

        def handle_default(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.SCRIPT_DATA_STATE)

        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPE_START_STATE, '-', TokenizerState.SCRIPT_DATA_ESCAPE_START_DASH_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_default_transition(TokenizerState.SCRIPT_DATA_ESCAPE_START_STATE, TokenizerState.SCRIPT_DATA_STATE, handle_default)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPE_START_STATE, EOF_STATE, None,handle_default)

    @register_setup(priority=18)
    def setup_script_data_escape_start_dash_state(self):

        def handle_default(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.SCRIPT_DATA_STATE)

        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPE_START_DASH_STATE, '-', TokenizerState.SCRIPT_DATA_ESCAPED_DASH_DASH_STATE, action=TWHTMLTokenizer.emit_current_char)
        self.set_default_transition(TokenizerState.SCRIPT_DATA_ESCAPE_START_DASH_STATE, TokenizerState.SCRIPT_DATA_STATE, handle_default)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPE_START_DASH_STATE, EOF_STATE, None,handle_default)

    @register_setup(priority=19)
    def setup_script_data_escaped_state(self):
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_STATE, "-", TokenizerState.SCRIPT_DATA_ESCAPED_DASH_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_STATE, "<", TokenizerState.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN_STATE)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_STATE, "\x00", TokenizerState.SCRIPT_DATA_ESCAPED_STATE, TWHTMLTokenizer.handle_null_in_state)
        self.set_default_transition(TokenizerState.SCRIPT_DATA_ESCAPED_STATE, TokenizerState.SCRIPT_DATA_ESCAPED_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_scrip)

    @register_setup(priority=20)
    def setup_script_data_escaped_dash_state(self):
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_DASH_STATE, "-", TokenizerState.SCRIPT_DATA_ESCAPED_DASH_DASH_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_DASH_STATE, "<", TokenizerState.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN_STATE)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_DASH_STATE, "\x00", TokenizerState.SCRIPT_DATA_ESCAPED_STATE, TWHTMLTokenizer.handle_null_in_state)
        self.set_default_transition(TokenizerState.SCRIPT_DATA_ESCAPED_DASH_STATE, TokenizerState.SCRIPT_DATA_ESCAPED_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_DASH_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_scrip)

    @register_setup(priority=21)
    def setup_script_data_escaped_dash_dash_state(self):
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_DASH_DASH_STATE, "-", TokenizerState.SCRIPT_DATA_ESCAPED_DASH_DASH_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_DASH_DASH_STATE, "<", TokenizerState.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN_STATE)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_DASH_DASH_STATE, ">", TokenizerState.SCRIPT_DATA_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_DASH_DASH_STATE, "\x00", TokenizerState.SCRIPT_DATA_ESCAPED_STATE, TWHTMLTokenizer.handle_null_in_state)
        self.set_default_transition(TokenizerState.SCRIPT_DATA_ESCAPED_DASH_DASH_STATE, TokenizerState.SCRIPT_DATA_ESCAPED_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_DASH_DASH_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_scrip)

    @register_setup(priority=22)
    def setup_script_data_escaped_less_than_sign_state(self):

        def handle_alfa(tokenizer, ch):
            tokenizer.emit_character("<")
            tokenizer.reset_buffer(tokenizer, ch)
            tokenizer.reconsume_in_state(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_START_STATE)

        def handle_default(tokenizer, ch):
            tokenizer.emit_character("<")
            tokenizer.reconsume_in_state(TokenizerState.SCRIPT_DATA_ESCAPED_STATE)

        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN_STATE, "/", TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_OPEN_STATE,TWHTMLTokenizer.reset_buffer)
        for char in ascii_letters:
            self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN_STATE, char, TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_START_STATE, handle_alfa)

        self.set_default_transition(TokenizerState.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN_STATE, TokenizerState.SCRIPT_DATA_ESCAPED_STATE, handle_default)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN_STATE, EOF_STATE, None,handle_default)

    @register_setup(priority=23)
    def setup_script_data_escaped_end_tag_open_state(self):

        def handle_alfa(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_NAME_STATE)

        def handle_default(tokenizer, ch):
            tokenizer.emit_character("</")
            tokenizer.reconsume_in_state(TokenizerState.SCRIPT_DATA_ESCAPED_STATE)

        for char in ascii_letters:
            self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_OPEN_STATE, char, TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_NAME_STATE, handle_alfa)

        self.set_default_transition(TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_OPEN_STATE, TokenizerState.SCRIPT_DATA_ESCAPED_STATE, handle_default)
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_OPEN_STATE, EOF_STATE, None,handle_default)

    @register_setup(priority=24)
    def setup_script_data_escaped_end_tag_name_state(self):

        for char in space_characters:
            self.set_action_transition(TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_NAME_STATE, char, action=lambda tokenizer, ch:  tokenizer.handle_appropriate_end_tag_name(tokenizer, ch, TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE, TokenizerState.SCRIPT_DATA_ESCAPED_STATE))

        self.set_action_transition(TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_NAME_STATE, "/", action=lambda tokenizer, ch:  tokenizer.handle_appropriate_end_tag_name(tokenizer, ch, TokenizerState.SELF_CLOSING_START_TAG_STATE, TokenizerState.SCRIPT_DATA_ESCAPED_STATE))
        self.set_action_transition(TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_NAME_STATE, ">", action=lambda tokenizer, ch:  tokenizer.handle_appropriate_end_tag_name(tokenizer, ch, TokenizerState.DATA_STATE, TokenizerState.SCRIPT_DATA_ESCAPED_STATE,True))

        for char in ascii_letters:
            self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_NAME_STATE, char, TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_NAME_STATE, TWHTMLTokenizer.append_buffer_current_lower_character)

        self.set_default_transition(TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_NAME_STATE, TokenizerState.RCDATA_STATE, lambda tokenizer, ch:  tokenizer.handle_default_rcdata_end_tag(tokenizer, ch, TokenizerState.SCRIPT_DATA_ESCAPED_STATE))
        self.set_transition(TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_NAME_STATE, EOF_STATE, None,action=lambda tokenizer, ch:  tokenizer.handle_default_rcdata_end_tag(tokenizer, ch, TokenizerState.SCRIPT_DATA_ESCAPED_STATE))

    @register_setup(priority=25)
    def setup_script_data_double_escape_start_state(self):

        def handle_alfa(tokenizer, ch):
            tokenizer.append_buffer_current_character(tokenizer, ch)
            tokenizer.emit_current_char(tokenizer, ch)

        def handle_check_double_escape(tokenizer, ch):
            temporary_buffer = tokenizer.get_buffer()
            if temporary_buffer.lower() == "script":
                tokenizer.state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE
            else:
                tokenizer.state = TokenizerState.SCRIPT_DATA_ESCAPED_STATE

            tokenizer.emit_character(ch)
            tokenizer.reset_buffer(tokenizer, ch)
            tokenizer.check_action_transition = True

        def fallback(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.SCRIPT_DATA_ESCAPED_STATE)

        for char in space_characters:
            self.set_action_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_START_STATE, char, handle_check_double_escape)

        self.set_action_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_START_STATE, "/", handle_check_double_escape)
        self.set_action_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_START_STATE, ">", handle_check_double_escape)


        for char in ascii_letters:
            self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_START_STATE, char, TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_START_STATE, handle_alfa)

        self.set_default_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_START_STATE, TokenizerState.SCRIPT_DATA_ESCAPED_STATE, fallback)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_START_STATE, EOF_STATE, None,fallback)

    @register_setup(priority=26)
    def setup_script_data_double_escaped_state(self):
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, "-", TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, "<", TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, "\x00", TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, TWHTMLTokenizer.handle_null_in_state)
        self.set_default_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_scrip)

    @register_setup(priority=27)
    def setup_script_data_double_escaped_dash_state(self):
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_STATE, "-", TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_STATE, "<", TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_STATE, "\x00", TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, TWHTMLTokenizer.handle_null_in_state)
        self.set_default_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_STATE, TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_scrip)

    @register_setup(priority=28)
    def setup_script_data_double_escaped_dash_dash_state(self):
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH_STATE, "-", TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH_STATE,TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH_STATE, "<", TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH_STATE, ">", TokenizerState.SCRIPT_DATA_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH_STATE, "\x00", TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, TWHTMLTokenizer.handle_null_in_state)
        self.set_default_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH_STATE, TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, TWHTMLTokenizer.emit_current_char)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_scrip)

    @register_setup(priority=29)
    def setup_script_data_double_escaped_less_than_sign_state(self):
        def handle_alfa(tokenizer, ch):
            tokenizer.reset_buffer(tokenizer, ch)
            tokenizer.emit_character("/")

        def fallback(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE)

        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN_STATE, "/", TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_END_STATE, handle_alfa)
        self.set_default_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN_STATE, TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, fallback)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN_STATE, EOF_STATE, None,fallback)

    @register_setup(priority=30)
    def setup_script_data_double_escape_end_state(self):
        def handle_alfa(tokenizer, ch):
            tokenizer.append_buffer_current_character(tokenizer, ch)
            tokenizer.emit_current_char(tokenizer, ch)

        def handle_check_script(tokenizer, ch):
            temporary_buffer = tokenizer.get_buffer()
            if temporary_buffer.lower() == "script":
                tokenizer.state = TokenizerState.SCRIPT_DATA_ESCAPED_STATE
            else:
                tokenizer.state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE

            tokenizer.emit_character(ch)
            tokenizer.reset_buffer(tokenizer, ch)
            tokenizer.check_action_transition = True

        def fallback(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE)

        for char in space_characters:
            self.set_action_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_END_STATE, char, handle_check_script)

        self.set_action_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_END_STATE, "/", handle_check_script)
        self.set_action_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_END_STATE, ">", handle_check_script)

        for char in ascii_letters:
            self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_END_STATE, char, TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_END_STATE, handle_alfa)

        self.set_default_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_END_STATE, TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_STATE, fallback)
        self.set_transition(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_END_STATE, EOF_STATE, None,fallback)

    @register_setup(priority=31)
    def setup_before_attribute_name_state(self):

        def handle_slash_gt_in_before_attr(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.AFTER_ATTRIBUTE_NAME_STATE)

        def handle_equals_in_before_attr_name(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_EQUALS_SIGN_BEFORE_ATTRIBUTE_NAME)
            if tokenizer.current_token and isinstance(tokenizer.current_token, Token):
                tokenizer.current_token.attributes.append(Attribute(name="=", value=""))

        def handle_default_in_before_attr_name(tokenizer, ch):
            if tokenizer.current_token and isinstance(tokenizer.current_token, Token):
                tokenizer.current_token.attributes.append(Attribute(name="", value=""))
            tokenizer.reconsume_in_state(TokenizerState.ATTRIBUTE_NAME_STATE)

        for char in space_characters:
            self.set_transition( TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE, char, TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE)

        self.set_transition(TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE,'/',TokenizerState.AFTER_ATTRIBUTE_NAME_STATE, action=handle_slash_gt_in_before_attr)
        self.set_transition(TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE,'>',TokenizerState.DATA_STATE,action=TWHTMLTokenizer.emit_current_token)
        self.set_transition(TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE,'=', TokenizerState.ATTRIBUTE_NAME_STATE, action=handle_equals_in_before_attr_name)
        self.set_default_transition(TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE,TokenizerState.ATTRIBUTE_NAME_STATE,handle_default_in_before_attr_name)
        self.set_transition(TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_after_attr_name)

    @register_setup(priority=32)
    def setup_attribute_name_state(self):

        def reconsume_in_after_attr_name(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.AFTER_ATTRIBUTE_NAME_STATE)

        def handle_upper_alpha_in_attr_name(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.attributes:
                tokenizer.current_token.attributes[-1].name += ch.lower()

        def handle_null_in_attr_name(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            if tokenizer.current_token and tokenizer.current_token.attributes:
                tokenizer.current_token.attributes[-1].name += '\uFFFD'

        def handle_unexpected_char_in_attr_name(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_CHARACTER_IN_ATTRIBUTE_NAME)
            handle_append_char_in_attr_name(tokenizer, ch)

        def handle_append_char_in_attr_name(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.attributes:
                tokenizer.current_token.attributes[-1].name += ch

        for char in space_characters:
            self.set_transition(TokenizerState.ATTRIBUTE_NAME_STATE, char, TokenizerState.AFTER_ATTRIBUTE_NAME_STATE,action=reconsume_in_after_attr_name)

        self.set_transition(TokenizerState.ATTRIBUTE_NAME_STATE, '/',TokenizerState.AFTER_ATTRIBUTE_NAME_STATE,action=reconsume_in_after_attr_name)
        self.set_transition(TokenizerState.ATTRIBUTE_NAME_STATE, '>',TokenizerState.DATA_STATE,action=TWHTMLTokenizer.emit_current_token)
        self.set_transition(TokenizerState.ATTRIBUTE_NAME_STATE, '=',TokenizerState.BEFORE_ATTRIBUTE_VALUE_STATE,action=TWHTMLTokenizer.handle_commit_attribute_name)

        for ch in ascii_uppercase:
            self.set_transition(TokenizerState.ATTRIBUTE_NAME_STATE, ch, TokenizerState.ATTRIBUTE_NAME_STATE, action=handle_upper_alpha_in_attr_name)

        self.set_transition(TokenizerState.ATTRIBUTE_NAME_STATE, '\x00', TokenizerState.ATTRIBUTE_NAME_STATE,action=handle_null_in_attr_name)

        for invalid_char in ['"', "'", '<']:
            self.set_transition(TokenizerState.ATTRIBUTE_NAME_STATE, invalid_char,TokenizerState.ATTRIBUTE_NAME_STATE,action=handle_unexpected_char_in_attr_name)

        self.set_default_transition(TokenizerState.ATTRIBUTE_NAME_STATE, TokenizerState.ATTRIBUTE_NAME_STATE, handle_append_char_in_attr_name)
        self.set_transition(TokenizerState.ATTRIBUTE_NAME_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_after_attr_name)

    @register_setup(priority=33)
    def setup_after_attribute_name_state(self):

        def handle_new_attr_and_reconsume(tokenizer, ch):
            if tokenizer.current_token and isinstance(tokenizer.current_token, Token):
                tokenizer.current_token.attributes.append(Attribute(name="", value=""))
            tokenizer.reconsume_in_state(TokenizerState.ATTRIBUTE_NAME_STATE)


        for char in space_characters:
            self.set_transition(TokenizerState.AFTER_ATTRIBUTE_NAME_STATE, char,TokenizerState.AFTER_ATTRIBUTE_NAME_STATE)

        self.set_transition(TokenizerState.AFTER_ATTRIBUTE_NAME_STATE, '/',TokenizerState.SELF_CLOSING_START_TAG_STATE)
        self.set_transition(TokenizerState.AFTER_ATTRIBUTE_NAME_STATE, '=',TokenizerState.BEFORE_ATTRIBUTE_VALUE_STATE)
        self.set_transition(TokenizerState.AFTER_ATTRIBUTE_NAME_STATE, '>', TokenizerState.DATA_STATE, TWHTMLTokenizer.emit_current_token)

        self.set_default_transition(TokenizerState.AFTER_ATTRIBUTE_NAME_STATE,TokenizerState.AFTER_ATTRIBUTE_NAME_STATE,handle_new_attr_and_reconsume)
        self.set_transition(TokenizerState.AFTER_ATTRIBUTE_NAME_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_after_attr_name)

    @register_setup(priority=34)
    def setup_before_attribute_value_state(self):
        def handle_missing_attr_value(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_ATTRIBUTE_VALUE)
            tokenizer.emit_current_token(tokenizer, ch)

        def handle_unquoted_value_reconsume(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE)

        for char in space_characters:
            self.set_transition(TokenizerState.BEFORE_ATTRIBUTE_VALUE_STATE, char, TokenizerState.BEFORE_ATTRIBUTE_VALUE_STATE)

        self.set_transition(TokenizerState.BEFORE_ATTRIBUTE_VALUE_STATE, '"', TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED_STATE)
        self.set_transition(TokenizerState.BEFORE_ATTRIBUTE_VALUE_STATE, "'", TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED_STATE)
        self.set_transition(TokenizerState.BEFORE_ATTRIBUTE_VALUE_STATE, '>',TokenizerState.DATA_STATE, handle_missing_attr_value)

        self.set_default_transition(TokenizerState.BEFORE_ATTRIBUTE_VALUE_STATE,TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE,handle_unquoted_value_reconsume)
        self.set_transition(TokenizerState.BEFORE_ATTRIBUTE_VALUE_STATE, EOF_STATE, None,handle_unquoted_value_reconsume)

    @register_setup(priority=35)
    def setup_attribute_value_double_quoted_state(self):

        def handle_ampersand_in_double_quote(tokenizer, ch):
            tokenizer.handle_character_reference(tokenizer, ch, from_attribute=True)

        def handle_null_in_double_quote(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            if tokenizer.current_token and tokenizer.current_token.attributes:
                tokenizer.current_token.attributes[-1].value += '\uFFFD'

        def handle_append_char_to_value(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.attributes:
                tokenizer.current_token.attributes[-1].value += ch

        self.set_transition(TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED_STATE, '"',TokenizerState.AFTER_ATTRIBUTE_VALUE_STATE)
        self.set_transition(TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED_STATE, '&',TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED_STATE,handle_ampersand_in_double_quote)
        self.set_transition(TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED_STATE, '\x00',TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED_STATE,handle_null_in_double_quote)
        self.set_default_transition(TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED_STATE,TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED_STATE,handle_append_char_to_value)
        self.set_transition(TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_tag)

    @register_setup(priority=36)
    def setup_attribute_value_single_quoted_state(self):

        def handle_ampersand_in_single_quote(tokenizer, ch):
            tokenizer.handle_character_reference(tokenizer, ch, from_attribute=True)

        def handle_null_in_single_quote(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            if tokenizer.current_token and tokenizer.current_token.attributes:
                tokenizer.current_token.attributes[-1].value += '\uFFFD'

        def handle_append_char(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.attributes:
                tokenizer.current_token.attributes[-1].value += ch

        self.set_transition(TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED_STATE, "'", TokenizerState.AFTER_ATTRIBUTE_VALUE_STATE)
        self.set_transition(TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED_STATE, '&',TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED_STATE,handle_ampersand_in_single_quote)
        self.set_transition(TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED_STATE, '\x00',TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED_STATE, handle_null_in_single_quote)

        self.set_default_transition(TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED_STATE,TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED_STATE, handle_append_char)
        self.set_transition(TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_tag)

    @register_setup(priority=37)
    def setup_attribute_value_unquoted_state(self):
        def handle_ampersand_in_unquoted(tokenizer, ch):
            tokenizer.handle_character_reference(tokenizer, ch, from_attribute=True)

        def handle_emit_tag_and_data_state(tokenizer, ch):
            tokenizer.emit_current_token(tokenizer, ch)

        def handle_null_in_unquoted(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            if tokenizer.current_token and tokenizer.current_token.attributes:
                tokenizer.current_token.attributes[-1].value += '\uFFFD'

        def handle_unexpected_char_in_unquoted(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_CHARACTER_IN_UNQUOTED_ATTRIBUTE_VALUE)
            if tokenizer.current_token and tokenizer.current_token.attributes:
                tokenizer.current_token.attributes[-1].value += ch

        def handle_default_unquoted(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.attributes:
                tokenizer.current_token.attributes[-1].value += ch

        for sp in space_characters:
            self.set_transition(TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE, sp,TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE)

        self.set_transition(TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE, '&', TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE, handle_ampersand_in_unquoted)
        self.set_transition(TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE, '>',TokenizerState.DATA_STATE,handle_emit_tag_and_data_state)
        self.set_transition(TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE, '\x00',TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE,handle_null_in_unquoted)

        for invalid_char in ['"', "'", '<', '=', '`']:
            self.set_transition(TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE, invalid_char,TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE,handle_unexpected_char_in_unquoted)

        self.set_default_transition(TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE,TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE,handle_default_unquoted)
        self.set_transition(TokenizerState.ATTRIBUTE_VALUE_UNQUOTED_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_tag)

    @register_setup(priority=38)
    def setup_after_attribute_value_quoted_state(self):

        def handle_missing_whitespace_between_attrs(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_WHITESPACE_BETWEEN_ATTRIBUTES)
            tokenizer.reconsume_in_state(TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE)

        for sp in space_characters:
            self.set_transition(TokenizerState.AFTER_ATTRIBUTE_VALUE_STATE, sp, TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE)

        self.set_transition(TokenizerState.AFTER_ATTRIBUTE_VALUE_STATE, '/', TokenizerState.SELF_CLOSING_START_TAG_STATE)

        self.set_transition(TokenizerState.AFTER_ATTRIBUTE_VALUE_STATE, '>', TokenizerState.DATA_STATE, TWHTMLTokenizer.emit_current_token)

        self.set_default_transition(TokenizerState.AFTER_ATTRIBUTE_VALUE_STATE, TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE, handle_missing_whitespace_between_attrs)
        self.set_transition(TokenizerState.AFTER_ATTRIBUTE_VALUE_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_tag)

    @register_setup(priority=39)
    def setup_self_closing_start_tag_state(self):

        def handle_self_closing_tag(tokenizer, ch):
            if tokenizer.current_token and isinstance(tokenizer.current_token, Token):
                tokenizer.current_token.self_closing = True
            tokenizer.emit_current_token(tokenizer, ch)

        def handle_unexpected_solidus_in_tag(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_SOLIDUS_IN_TAG)
            tokenizer.reconsume_in_state(TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE)

        self.set_transition(TokenizerState.SELF_CLOSING_START_TAG_STATE,'>',TokenizerState.DATA_STATE, action=handle_self_closing_tag)
        self.set_default_transition(TokenizerState.SELF_CLOSING_START_TAG_STATE,TokenizerState.BEFORE_ATTRIBUTE_NAME_STATE, handle_unexpected_solidus_in_tag)
        self.set_transition(TokenizerState.SELF_CLOSING_START_TAG_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_tag)

    @register_setup(priority=40)
    def setup_bogus_comment_state(self):

        def handle_append_bogus_comment(tokenizer, ch):
            tokenizer.current_token.data += ch

        def handle_null_in_bogus_state(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            tokenizer.current_token.data += ("\uFFFD")

        self.set_transition(TokenizerState.BOGUS_COMMENT_STATE, '>', TokenizerState.DATA_STATE, TWHTMLTokenizer.emit_current_token)
        self.set_transition(TokenizerState.BOGUS_COMMENT_STATE, '\x00', TokenizerState.BOGUS_COMMENT_STATE, action=handle_null_in_bogus_state)
        self.set_default_transition(TokenizerState.BOGUS_COMMENT_STATE, TokenizerState.BOGUS_COMMENT_STATE, handle_append_bogus_comment)
        self.set_transition(TokenizerState.BOGUS_COMMENT_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_bogus_comment_state)


    @register_setup(priority=41)
    def setup_markup_declaration_open_state(self):

        def handle_anything_else_markup_declaration_open_state(tokenizer, ch):
            tokenizer.log_error(ParseError.INCORRECTLY_OPENED_COMMENT)
            tokenizer.current_token = Token(type=COMMENT, data='')
            tokenizer.reconsume_in_state(TokenizerState.BOGUS_COMMENT_STATE)

        def handle_markup_declaration_dash(tokenizer, ch):
            if tokenizer.position + 1 < tokenizer.length and tokenizer.text[tokenizer.position + 1] == '-':
                tokenizer.position += 1  # Consuma il secondo '-'
                tokenizer.current_token = Token(type=COMMENT, data="")
                tokenizer.state = TokenizerState.COMMENT_START_STATE
            else:
                handle_anything_else_markup_declaration_open_state(tokenizer, ch)
            tokenizer.check_action_transition = True

        def handle_start_doctype(tokenizer, ch):
            expected = "DOCTYPE"
            end_pos = tokenizer.position + len(expected)
            if end_pos <= tokenizer.length and tokenizer.text[tokenizer.position:end_pos].upper() == expected:
                tokenizer.position += len(expected) - 1
                tokenizer.current_token = Token(type=DOCTYPE,
                                                name='',
                                                public_id=None,
                                                system_id=None,
                                                quirks_mode=False)

                tokenizer.state = TokenizerState.DOCTYPE_STATE
            else:
                handle_anything_else_markup_declaration_open_state(tokenizer, ch)
            tokenizer.check_action_transition = True

        def handle_start_cdata(tokenizer, ch):
            expected = "[CDATA["

            current_ns = tokenizer.current_namespace()
            if tokenizer.parser.open_elements and tokenizer.text.startswith(expected, tokenizer.position) and current_ns != namespaces["html"] and tokenizer.parser:
                tokenizer.state = TokenizerState.CDATA_SECTION_STATE
            else:
                tokenizer.log_error(ParseError.CDATA_IN_HTML_CONTENT)
                tokenizer.current_token = Token(COMMENT, data=expected)
                tokenizer.state = TokenizerState.BOGUS_COMMENT_STATE

            tokenizer.position += len(expected) - 1
            tokenizer.check_action_transition = True

        self.set_action_transition(TokenizerState.MARKUP_DECLARATION_OPEN_STATE,'-', handle_markup_declaration_dash)
        self.set_action_transition(TokenizerState.MARKUP_DECLARATION_OPEN_STATE,'D',action=handle_start_doctype)
        self.set_action_transition(TokenizerState.MARKUP_DECLARATION_OPEN_STATE,'d',action=handle_start_doctype)
        self.set_action_transition(TokenizerState.MARKUP_DECLARATION_OPEN_STATE,'[',handle_start_cdata)
        self.set_default_transition(TokenizerState.MARKUP_DECLARATION_OPEN_STATE, TokenizerState.BOGUS_COMMENT_STATE, handle_anything_else_markup_declaration_open_state)
        self.set_transition(TokenizerState.MARKUP_DECLARATION_OPEN_STATE, EOF_STATE, None,handle_anything_else_markup_declaration_open_state)

    @register_setup(priority=42)
    def setup_comment_start_state(self):

        def handle_gt(tokenizer, ch):
            tokenizer.log_error(ParseError.ABRUPT_CLOSING_OF_EMPTY_COMMENT)
            tokenizer.emit_current_token(tokenizer, ch)

        def handle_default(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.COMMENT_STATE)

        self.set_transition(TokenizerState.COMMENT_START_STATE, '-', TokenizerState.COMMENT_START_DASH_STATE)
        self.set_transition(TokenizerState.COMMENT_START_STATE, '>', TokenizerState.DATA_STATE, action=handle_gt)
        self.set_default_transition(TokenizerState.COMMENT_START_STATE, TokenizerState.COMMENT_STATE, handle_default)
        self.set_transition(TokenizerState.COMMENT_START_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_comment)

    @register_setup(priority=43)
    def setup_comment_start_dash_state(self):

        def handle_gt(tokenizer, ch):
            tokenizer.log_error(ParseError.ABRUPT_CLOSING_OF_EMPTY_COMMENT)
            tokenizer.emit_current_token(tokenizer, ch)

        def handle_default(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.type == COMMENT:
                tokenizer.current_token.data += '-'
            tokenizer.reconsume_in_state(TokenizerState.COMMENT_STATE)

        self.set_transition(TokenizerState.COMMENT_START_DASH_STATE, '-', TokenizerState.COMMENT_END_STATE)
        self.set_transition(TokenizerState.COMMENT_START_DASH_STATE, '>', TokenizerState.DATA_STATE, action=handle_gt)
        self.set_default_transition(TokenizerState.COMMENT_START_DASH_STATE, TokenizerState.COMMENT_STATE, handle_default)
        self.set_transition(TokenizerState.COMMENT_START_DASH_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_comment)

    @register_setup(priority=44)
    def setup_comment_state(self):
        def handle_null(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            if tokenizer.current_token and tokenizer.current_token.type == COMMENT:
                tokenizer.current_token.data += '\uFFFD'

        def handle_default(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.type == COMMENT:
                tokenizer.current_token.data += ch

        self.set_transition(TokenizerState.COMMENT_STATE, '-', TokenizerState.COMMENT_END_DASH_STATE)
        self.set_transition(TokenizerState.COMMENT_STATE, '\x00', TokenizerState.COMMENT_STATE, action=handle_null)
        self.set_default_transition(TokenizerState.COMMENT_STATE, TokenizerState.COMMENT_STATE, handle_default)
        self.set_transition(TokenizerState.COMMENT_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_comment)


    @register_setup(priority=45)
    def setup_comment_less_than_sign_bang_state(self):

        def default_reconsume(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.COMMENT_STATE)

        self.set_transition(TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_STATE, '-', TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_DASH_STATE)
        self.set_default_transition(TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_STATE, TokenizerState.COMMENT_STATE, default_reconsume)
        self.set_transition(TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_STATE, EOF_STATE, None,default_reconsume)

    @register_setup(priority=46)
    def setup_comment_less_than_sign_bang_dash_state(self):

        def default_reconsume(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.COMMENT_END_DASH_STATE)

        self.set_transition(TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_DASH_STATE, '-', TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH_STATE)
        self.set_default_transition(TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_DASH_STATE, TokenizerState.COMMENT_END_DASH_STATE, default_reconsume)
        self.set_transition(TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_DASH_STATE, EOF_STATE, None,default_reconsume)

    @register_setup(priority=47)
    def setup_comment_less_than_sign_bang_dash_dash_state(self):
        def handle_gt(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.COMMENT_END_STATE)

        def default_reconsume(tokenizer, ch):
            tokenizer.log_error(ParseError.NESTED_COMMENT)
            tokenizer.reconsume_in_state(TokenizerState.COMMENT_END_STATE)

        self.set_transition(TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH_STATE, '>', TokenizerState.COMMENT_END_STATE, action=handle_gt)
        self.set_default_transition(TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH_STATE, TokenizerState.COMMENT_END_STATE, default_reconsume)
        self.set_transition(TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH_STATE, EOF_STATE, None,default_reconsume)

    @register_setup(priority=48)
    def setup_comment_end_dash_state(self):

        def default_reconsume(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.type == COMMENT:
                tokenizer.current_token.data += '-'
            tokenizer.reconsume_in_state(TokenizerState.COMMENT_STATE)

        self.set_transition(TokenizerState.COMMENT_END_DASH_STATE, '-', TokenizerState.COMMENT_END_STATE)
        self.set_default_transition(TokenizerState.COMMENT_END_DASH_STATE, TokenizerState.COMMENT_STATE, default_reconsume)
        self.set_transition(TokenizerState.COMMENT_END_DASH_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_comment)

    @register_setup(priority=49)
    def setup_comment_end_state(self):

        def handle_dash(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.type == COMMENT:
                tokenizer.current_token.data += '-'

        def handle_default(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.type == COMMENT:
                tokenizer.current_token.data += '--'
            tokenizer.reconsume_in_state(TokenizerState.COMMENT_STATE)

        self.set_transition(TokenizerState.COMMENT_END_STATE, '>', TokenizerState.DATA_STATE, action=TWHTMLTokenizer.emit_current_token)
        self.set_transition(TokenizerState.COMMENT_END_STATE, '!', TokenizerState.COMMENT_END_BANG_STATE)
        self.set_transition(TokenizerState.COMMENT_END_STATE, '-', TokenizerState.COMMENT_END_STATE, action=handle_dash)
        self.set_default_transition(TokenizerState.COMMENT_END_STATE, TokenizerState.COMMENT_STATE, handle_default)
        self.set_transition(TokenizerState.COMMENT_END_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_comment)

    @register_setup(priority=50)
    def setup_comment_end_bang_state(self):
        def handle_dash(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.type == COMMENT:
                tokenizer.current_token.data += '--!'

        def handle_gt(tokenizer, ch):
            tokenizer.log_error(ParseError.INCORRECTLY_CLOSED_COMMENT)
            tokenizer.emit_current_token(tokenizer, ch)

        def handle_default(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.type == COMMENT:
                tokenizer.current_token.data += '--!'
            tokenizer.reconsume_in_state(TokenizerState.COMMENT_STATE)

        self.set_transition(TokenizerState.COMMENT_END_BANG_STATE, '-', TokenizerState.COMMENT_END_DASH_STATE, action=handle_dash)
        self.set_transition(TokenizerState.COMMENT_END_BANG_STATE, '>', TokenizerState.DATA_STATE, action=handle_gt)
        self.set_default_transition(TokenizerState.COMMENT_END_BANG_STATE, TokenizerState.COMMENT_STATE, handle_default)
        self.set_transition(TokenizerState.COMMENT_END_BANG_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_comment)

    @register_setup(priority=51)
    def setup_doctype_state(self):

        def reconsume_in_before_name(tokenizer, ch):
            tokenizer.reconsume_in_state(TokenizerState.BEFORE_DOCTYPE_NAME_STATE)

        def handle_missing_whitespace(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_WHITESPACE_BEFORE_DOCTYPE_NAME)
            tokenizer.reconsume_in_state(TokenizerState.BEFORE_DOCTYPE_NAME_STATE)

        for sp in space_characters:
            self.set_transition(TokenizerState.DOCTYPE_STATE, sp, TokenizerState.BEFORE_DOCTYPE_NAME_STATE)

        self.set_transition(TokenizerState.DOCTYPE_STATE, '>',TokenizerState.BEFORE_DOCTYPE_NAME_STATE, action=reconsume_in_before_name)
        self.set_default_transition(TokenizerState.DOCTYPE_STATE, TokenizerState.BEFORE_DOCTYPE_NAME_STATE, handle_missing_whitespace)
        self.set_transition(TokenizerState.DOCTYPE_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype_state)

    @register_setup(priority=52)
    def setup_before_doctype_name_state(self):

        def handle_upper_alpha_doctype_name(tokenizer, ch):
            tokenizer.current_token = Token(type=DOCTYPE,
                                            name=ch.lower(),
                                            public_id=None,
                                            system_id=None,
                                            quirks_mode=False)

        def handle_null_in_before_name(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            tokenizer.current_token = Token(type=DOCTYPE,
                                            name='\uFFFD',
                                            public_id=None,
                                            system_id=None,
                                            quirks_mode=False)

        def handle_gt_missing_name(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_DOCTYPE_NAME)
            doctype = Token(type=DOCTYPE, quirks_mode=True,
                            name=None, public_id=None, system_id=None)
            tokenizer.emit_token(doctype)

        def handle_default_in_before_name(tokenizer, ch):
            tokenizer.current_token = Token(type=DOCTYPE,
                                            name=ch,
                                            public_id=None,
                                            system_id=None,
                                            quirks_mode=False)
        for sp in space_characters:
            self.set_transition(TokenizerState.BEFORE_DOCTYPE_NAME_STATE, sp, TokenizerState.BEFORE_DOCTYPE_NAME_STATE)

        for up in ascii_uppercase:
            self.set_transition(TokenizerState.BEFORE_DOCTYPE_NAME_STATE, up, TokenizerState.DOCTYPE_NAME_STATE, action=handle_upper_alpha_doctype_name)

        self.set_transition(TokenizerState.BEFORE_DOCTYPE_NAME_STATE, '\x00', TokenizerState.DOCTYPE_NAME_STATE, action=handle_null_in_before_name)
        self.set_transition(TokenizerState.BEFORE_DOCTYPE_NAME_STATE, '>', TokenizerState.DATA_STATE, action=handle_gt_missing_name)
        self.set_default_transition(TokenizerState.BEFORE_DOCTYPE_NAME_STATE, TokenizerState.DOCTYPE_NAME_STATE, handle_default_in_before_name)
        self.set_transition(TokenizerState.BEFORE_DOCTYPE_NAME_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=53)
    def setup_doctype_name_state(self):

        def handle_upper_alpha_in_name(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.type == DOCTYPE:
                tokenizer.current_token.name = (tokenizer.current_token.name or "")+ ch.lower()

        def handle_null_in_name(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            if tokenizer.current_token and tokenizer.current_token.type == DOCTYPE:
                tokenizer.current_token.name = (tokenizer.current_token.name or "") + '\uFFFD'

        def handle_append_char_to_name(tokenizer, ch):
            if tokenizer.current_token and tokenizer.current_token.type == DOCTYPE:
                tokenizer.current_token.name = (tokenizer.current_token.name or "") + ch

        for sp in space_characters:
            self.set_transition(TokenizerState.DOCTYPE_NAME_STATE, sp, TokenizerState.AFTER_DOCTYPE_NAME_STATE)

        self.set_transition(TokenizerState.DOCTYPE_NAME_STATE, '>',  TokenizerState.DATA_STATE,  action=TWHTMLTokenizer.emit_current_token)

        for up in ascii_uppercase:
            self.set_transition(TokenizerState.DOCTYPE_NAME_STATE, up, TokenizerState.DOCTYPE_NAME_STATE, action=handle_upper_alpha_in_name)

        self.set_transition(TokenizerState.DOCTYPE_NAME_STATE, '\x00',  TokenizerState.DOCTYPE_NAME_STATE, action=handle_null_in_name)
        self.set_default_transition(TokenizerState.DOCTYPE_NAME_STATE, TokenizerState.DOCTYPE_NAME_STATE, handle_append_char_to_name)
        self.set_transition(TokenizerState.DOCTYPE_NAME_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=54)
    def setup_after_doctype_name_state(self):

        def handle_start_keyword(tokenizer, ch, expected, next_state):
            end_pos = tokenizer.position + len(expected)
            if end_pos <= tokenizer.length and tokenizer.text[tokenizer.position:end_pos].upper() == expected:
                tokenizer.position += len(expected) - 1
                tokenizer.state = next_state
            else:
                tokenizer.log_error(ParseError.INVALID_CHARACTER_SEQUENCE_AFTER_DOCTYPE_NAME)
                if tokenizer.current_token and tokenizer.current_token.type == DOCTYPE:
                    tokenizer.current_token.quirks_mode = True
                tokenizer.reconsume_in_state(TokenizerState.BOGUS_DOCTYPE_STATE)
            tokenizer.check_action_transition = True

        def handle_public_system_check(tokenizer, ch):
            tokenizer.log_error(ParseError.INVALID_CHARACTER_SEQUENCE_AFTER_DOCTYPE_NAME)
            if tokenizer.current_token and tokenizer.current_token.type == DOCTYPE:
                tokenizer.current_token.quirks_mode = True
            tokenizer.reconsume_in_state(TokenizerState.BOGUS_DOCTYPE_STATE)

        self.set_action_transition(TokenizerState.AFTER_DOCTYPE_NAME_STATE, 'P',  action=lambda tokenizer, ch: handle_start_keyword(tokenizer, ch, "PUBLIC", TokenizerState.AFTER_DOCTYPE_PUBLIC_KEYWORD_STATE))
        self.set_action_transition(TokenizerState.AFTER_DOCTYPE_NAME_STATE, 'p', action=lambda tokenizer, ch: handle_start_keyword(tokenizer, ch, "PUBLIC", TokenizerState.AFTER_DOCTYPE_PUBLIC_KEYWORD_STATE))
        self.set_action_transition(TokenizerState.AFTER_DOCTYPE_NAME_STATE, 'S', action=lambda tokenizer, ch: handle_start_keyword(tokenizer, ch, "SYSTEM", TokenizerState.AFTER_DOCTYPE_SYSTEM_KEYWORD_STATE))
        self.set_action_transition(TokenizerState.AFTER_DOCTYPE_NAME_STATE, 's', action=lambda tokenizer, ch: handle_start_keyword(tokenizer, ch, "SYSTEM", TokenizerState.AFTER_DOCTYPE_SYSTEM_KEYWORD_STATE))

        for sp in space_characters:
            self.set_transition(TokenizerState.AFTER_DOCTYPE_NAME_STATE, sp, TokenizerState.AFTER_DOCTYPE_NAME_STATE)

        self.set_transition(TokenizerState.AFTER_DOCTYPE_NAME_STATE, '>',  TokenizerState.DATA_STATE, action=TWHTMLTokenizer.emit_current_token)
        self.set_default_transition(TokenizerState.AFTER_DOCTYPE_NAME_STATE, TokenizerState.AFTER_DOCTYPE_NAME_STATE,  handle_public_system_check)
        self.set_transition(TokenizerState.AFTER_DOCTYPE_NAME_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=55)
    def setup_after_doctype_public_keyword_state(self):

        def handle_double_quote_pubid(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_WHITESPACE_AFTER_DOCTYPE_PUBLIC_KEYWORD)
            if tokenizer.current_token.type == DOCTYPE:
                tokenizer.current_token.public_id = ""

        def handle_single_quote_pubid(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_WHITESPACE_AFTER_DOCTYPE_PUBLIC_KEYWORD)
            if tokenizer.current_token.type == DOCTYPE:
                tokenizer.current_token.public_id = ""

        def handle_gt_missing_pubid(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_DOCTYPE_PUBLIC_IDENTIFIER)
            if tokenizer.current_token.type == DOCTYPE:
                tokenizer.current_token.quirks_mode = True
            tokenizer.emit_current_token(tokenizer, ch)

        def handle_missing_quote_pubid(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_QUOTE_BEFORE_DOCTYPE_PUBLIC_IDENTIFIER)
            if tokenizer.current_token.type == DOCTYPE:
                tokenizer.current_token.quirks_mode = True
            tokenizer.reconsume_in_state(TokenizerState.BOGUS_DOCTYPE_STATE)

        for sp in space_characters:
            self.set_transition(TokenizerState.AFTER_DOCTYPE_PUBLIC_KEYWORD_STATE, sp,  TokenizerState.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER_STATE)

        self.set_transition(TokenizerState.AFTER_DOCTYPE_PUBLIC_KEYWORD_STATE, '"', TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED_STATE, action=handle_double_quote_pubid)
        self.set_transition(TokenizerState.AFTER_DOCTYPE_PUBLIC_KEYWORD_STATE, "'", TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED_STATE, action=handle_single_quote_pubid)

        self.set_transition(TokenizerState.AFTER_DOCTYPE_PUBLIC_KEYWORD_STATE, '>', TokenizerState.DATA_STATE, action=handle_gt_missing_pubid)
        self.set_default_transition(TokenizerState.AFTER_DOCTYPE_PUBLIC_KEYWORD_STATE, TokenizerState.BOGUS_DOCTYPE_STATE, handle_missing_quote_pubid)
        self.set_transition(TokenizerState.AFTER_DOCTYPE_PUBLIC_KEYWORD_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=56)
    def setup_before_doctype_public_identifier_state(self):

        def handle_quote_start(tokenizer, ch):
            tokenizer.current_token.public_id = ""

        def handle_missing_quote_pubid(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_QUOTE_BEFORE_DOCTYPE_PUBLIC_IDENTIFIER)
            tokenizer.current_token.quirks_mode = True
            tokenizer.reconsume_in_state(TokenizerState.BOGUS_DOCTYPE_STATE)

        def handle_gt_missing_pubid(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_DOCTYPE_PUBLIC_IDENTIFIER)
            tokenizer.current_token.quirks_mode = True
            tokenizer.emit_current_token(tokenizer, ch)

        for sp in space_characters:
            self.set_transition(TokenizerState.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER_STATE, sp, TokenizerState.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER_STATE)

        self.set_transition(TokenizerState.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER_STATE, '"', TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED_STATE, action=handle_quote_start)
        self.set_transition(TokenizerState.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER_STATE, "'", TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED_STATE, action=handle_quote_start)
        self.set_transition(TokenizerState.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER_STATE, '>', TokenizerState.DATA_STATE, action=handle_gt_missing_pubid)
        self.set_default_transition(TokenizerState.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER_STATE, TokenizerState.BOGUS_DOCTYPE_STATE, handle_missing_quote_pubid)
        self.set_transition(TokenizerState.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=57)
    def setup_doctype_public_identifier_double_quoted_state(self):

        def handle_null_in_double_quoted_pubid(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            tokenizer.current_token.public_id += '\uFFFD'

        def handle_gt_abrupt_pubid(tokenizer, ch):
            tokenizer.log_error(ParseError.ABRUPT_DOCTYPE_PUBLIC_IDENTIFIER)
            tokenizer.current_token.quirks_mode = True
            tokenizer.emit_current_token(tokenizer, ch)

        def append_pubid_char(tokenizer, ch):
            tokenizer.current_token.public_id += ch

        self.set_transition(TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED_STATE, '"', TokenizerState.AFTER_DOCTYPE_PUBLIC_IDENTIFIER_STATE)
        self.set_transition(TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED_STATE, '\x00', TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED_STATE, action=handle_null_in_double_quoted_pubid)
        self.set_transition(TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED_STATE, '>', TokenizerState.DATA_STATE, action=handle_gt_abrupt_pubid)
        self.set_default_transition(TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED_STATE, TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED_STATE, append_pubid_char)
        self.set_transition(TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=58)
    def setup_doctype_public_identifier_single_quoted_state(self):

        def handle_null_in_single_pubid(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            tokenizer.current_token.public_id += '\uFFFD'

        def handle_gt_abrupt_single_pubid(tokenizer, ch):
            tokenizer.log_error(ParseError.ABRUPT_DOCTYPE_PUBLIC_IDENTIFIER)
            tokenizer.current_token.quirks_mode = True
            tokenizer.emit_current_token(tokenizer, ch)

        def append_single_pubid(tokenizer, ch):
            tokenizer.current_token.public_id += ch

        self.set_transition(TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED_STATE, "'",TokenizerState.AFTER_DOCTYPE_PUBLIC_IDENTIFIER_STATE)
        self.set_transition(TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED_STATE, '\x00', TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED_STATE, action=handle_null_in_single_pubid)
        self.set_transition(TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED_STATE, '>', TokenizerState.DATA_STATE, action=handle_gt_abrupt_single_pubid)
        self.set_default_transition(TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED_STATE, TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED_STATE, append_single_pubid)
        self.set_transition(TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED_STATE, EOF_STATE, None,action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=59)
    def setup_after_doctype_public_identifier_state(self):

        def handle_double_quote_system(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_WHITESPACE_BETWEEN_ATTRIBUTES)
            tokenizer.current_token.system_id = ""

        def handle_single_quote_system(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_WHITESPACE_BETWEEN_ATTRIBUTES)
            tokenizer.current_token.system_id = ""

        def handle_missing_quote_before_system(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_QUOTE_BEFORE_DOCTYPE_SYSTEM_IDENTIFIER)
            tokenizer.current_token.quirks_mode = True
            tokenizer.reconsume_in_state(TokenizerState.BOGUS_DOCTYPE_STATE)

        for sp in space_characters:
            self.set_transition(TokenizerState.AFTER_DOCTYPE_PUBLIC_IDENTIFIER_STATE, sp, TokenizerState.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS_STATE)

        self.set_transition(TokenizerState.AFTER_DOCTYPE_PUBLIC_IDENTIFIER_STATE, '>', TokenizerState.DATA_STATE, action=TWHTMLTokenizer.emit_current_token)
        self.set_transition(TokenizerState.AFTER_DOCTYPE_PUBLIC_IDENTIFIER_STATE, '"', TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED_STATE, action=handle_double_quote_system)
        self.set_transition(TokenizerState.AFTER_DOCTYPE_PUBLIC_IDENTIFIER_STATE, "'", TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED_STATE, action=handle_single_quote_system)
        self.set_default_transition(TokenizerState.AFTER_DOCTYPE_PUBLIC_IDENTIFIER_STATE, TokenizerState.BOGUS_DOCTYPE_STATE, handle_missing_quote_before_system)
        self.set_transition(TokenizerState.AFTER_DOCTYPE_PUBLIC_IDENTIFIER_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=60)
    def setup_between_doctype_public_and_system_identifiers_state(self):

        def handle_quote_sysid(tokenizer, ch):
            tokenizer.current_token.system_id = ""

        def handle_missing_quote_sysid(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_QUOTE_BEFORE_DOCTYPE_SYSTEM_IDENTIFIER)
            tokenizer.current_token.quirks_mode = True
            tokenizer.reconsume_in_state(TokenizerState.BOGUS_DOCTYPE_STATE)

        for sp in space_characters:
            self.set_transition(TokenizerState.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS_STATE, sp, TokenizerState.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS_STATE)

        self.set_transition(TokenizerState.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS_STATE, '>', TokenizerState.DATA_STATE, action=TWHTMLTokenizer.emit_current_token)
        self.set_transition(TokenizerState.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS_STATE, '"', TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED_STATE, action=handle_quote_sysid)
        self.set_transition(TokenizerState.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS_STATE, "'", TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED_STATE, action=handle_quote_sysid)
        self.set_default_transition(TokenizerState.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS_STATE, TokenizerState.BOGUS_DOCTYPE_STATE,handle_missing_quote_sysid)
        self.set_transition(TokenizerState.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=61)
    def setup_after_doctype_system_keyword_state(self):

        def handle_quote_system(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_WHITESPACE_AFTER_DOCTYPE_SYSTEM_KEYWORD)
            tokenizer.current_token.system_id = ""

        def handle_gt_missing_sysid(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_DOCTYPE_SYSTEM_IDENTIFIER)
            tokenizer.current_token.quirks_mode = True
            tokenizer.emit_current_token(tokenizer, ch)

        def handle_missing_quote_sysid(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_QUOTE_BEFORE_DOCTYPE_SYSTEM_IDENTIFIER)
            tokenizer.current_token.quirks_mode = True
            tokenizer.reconsume_in_state(TokenizerState.BOGUS_DOCTYPE_STATE)

        for sp in space_characters:
            self.set_transition(TokenizerState.AFTER_DOCTYPE_SYSTEM_KEYWORD_STATE, sp,TokenizerState.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER_STATE)

        self.set_transition(TokenizerState.AFTER_DOCTYPE_SYSTEM_KEYWORD_STATE, '"',  TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED_STATE, action=handle_quote_system)
        self.set_transition(TokenizerState.AFTER_DOCTYPE_SYSTEM_KEYWORD_STATE, "'",TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED_STATE, action=handle_quote_system)
        self.set_transition(TokenizerState.AFTER_DOCTYPE_SYSTEM_KEYWORD_STATE, '>',  TokenizerState.DATA_STATE,  action=handle_gt_missing_sysid)
        self.set_default_transition(TokenizerState.AFTER_DOCTYPE_SYSTEM_KEYWORD_STATE, TokenizerState.BOGUS_DOCTYPE_STATE, handle_missing_quote_sysid)
        self.set_transition(TokenizerState.AFTER_DOCTYPE_SYSTEM_KEYWORD_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=62)
    def setup_before_doctype_system_identifier_state(self):

        def handle_quote_sysid(tokenizer, ch):
            tokenizer.current_token.system_id = ""

        def handle_gt_missing_sysid(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_DOCTYPE_SYSTEM_IDENTIFIER)
            tokenizer.current_token.quirks_mode = True
            tokenizer.emit_current_token(tokenizer, ch)

        def handle_missing_quote_sysid(tokenizer, ch):
            tokenizer.log_error(ParseError.MISSING_QUOTE_BEFORE_DOCTYPE_SYSTEM_IDENTIFIER)
            tokenizer.current_token.quirks_mode = True
            tokenizer.reconsume_in_state(TokenizerState.BOGUS_DOCTYPE_STATE)

        for sp in space_characters:
            self.set_transition(TokenizerState.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER_STATE, sp, TokenizerState.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER_STATE)

        self.set_transition(TokenizerState.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER_STATE, '"', TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED_STATE, action=handle_quote_sysid)
        self.set_transition(TokenizerState.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER_STATE, "'", TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED_STATE, action=handle_quote_sysid)
        self.set_transition(TokenizerState.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER_STATE, '>', TokenizerState.DATA_STATE, action=handle_gt_missing_sysid)
        self.set_default_transition(TokenizerState.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER_STATE, TokenizerState.BOGUS_DOCTYPE_STATE, handle_missing_quote_sysid)
        self.set_transition(TokenizerState.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=63)
    def setup_doctype_system_identifier_double_quoted_state(self):

        def handle_null_in_double_quoted_sysid(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            tokenizer.current_token.system_id += '\uFFFD'

        def handle_gt_abrupt_sysid(tokenizer, ch):
            tokenizer.log_error(ParseError.ABRUPT_DOCTYPE_SYSTEM_IDENTIFIER)
            tokenizer.current_token.quirks_mode = True
            tokenizer.emit_current_token(tokenizer, ch)

        def append_system_id_char(tokenizer, ch):
            tokenizer.current_token.system_id += ch

        self.set_transition(TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED_STATE, '"', TokenizerState.AFTER_DOCTYPE_SYSTEM_IDENTIFIER_STATE)
        self.set_transition(TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED_STATE, '\x00', TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED_STATE, action=handle_null_in_double_quoted_sysid)
        self.set_transition(TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED_STATE, '>', TokenizerState.DATA_STATE, action=handle_gt_abrupt_sysid)
        self.set_default_transition(TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED_STATE, TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED_STATE, append_system_id_char)
        self.set_transition(TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=64)
    def setup_doctype_system_identifier_single_quoted_state(self):

        def handle_null_in_single_quoted_sysid(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
            tokenizer.current_token.system_id += '\uFFFD'

        def handle_gt_abrupt_sysid(tokenizer, ch):
            tokenizer.log_error(ParseError.ABRUPT_DOCTYPE_SYSTEM_IDENTIFIER)
            tokenizer.current_token.quirks_mode = True
            tokenizer.emit_current_token(tokenizer, ch)

        def append_sysid_char(tokenizer, ch):
            tokenizer.current_token.system_id += ch

        self.set_transition(TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED_STATE, "'", TokenizerState.AFTER_DOCTYPE_SYSTEM_IDENTIFIER_STATE)
        self.set_transition(TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED_STATE, '\x00', TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED_STATE, action=handle_null_in_single_quoted_sysid)
        self.set_transition(TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED_STATE, '>', TokenizerState.DATA_STATE, action=handle_gt_abrupt_sysid)
        self.set_default_transition(TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED_STATE,TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED_STATE, append_sysid_char)
        self.set_transition(TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=65)
    def setup_after_doctype_system_identifier_state(self):

        def handle_unexpected_char_after_sysid(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_CHARACTER_AFTER_DOCTYPE_SYSTEM_IDENTIFIER)
            tokenizer.reconsume_in_state(TokenizerState.BOGUS_DOCTYPE_STATE)

        for sp in space_characters:
            self.set_transition(TokenizerState.AFTER_DOCTYPE_SYSTEM_IDENTIFIER_STATE, sp, TokenizerState.AFTER_DOCTYPE_SYSTEM_IDENTIFIER_STATE)

        self.set_transition(TokenizerState.AFTER_DOCTYPE_SYSTEM_IDENTIFIER_STATE, '>', TokenizerState.DATA_STATE, action=TWHTMLTokenizer.emit_current_token)
        self.set_default_transition(TokenizerState.AFTER_DOCTYPE_SYSTEM_IDENTIFIER_STATE, TokenizerState.BOGUS_DOCTYPE_STATE, handle_unexpected_char_after_sysid)
        self.set_transition(TokenizerState.AFTER_DOCTYPE_SYSTEM_IDENTIFIER_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_doctype)

    @register_setup(priority=66)
    def setup_bogus_doctype_state(self):
        def handle_null_in_bogus(tokenizer, ch):
            tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)

        self.set_transition(TokenizerState.BOGUS_DOCTYPE_STATE, '>', TokenizerState.DATA_STATE, action=TWHTMLTokenizer.emit_current_token)
        self.set_transition(TokenizerState.BOGUS_DOCTYPE_STATE, '\x00',  TokenizerState.BOGUS_DOCTYPE_STATE, action=handle_null_in_bogus)
        self.set_default_transition(TokenizerState.BOGUS_DOCTYPE_STATE,  TokenizerState.BOGUS_DOCTYPE_STATE)
        self.set_transition(TokenizerState.BOGUS_DOCTYPE_STATE, EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_bogus)

    @register_setup(priority=67)
    def setup_cdata_section_state(self):
        def read_cdata(tokenizer, ch):
            data_parts = []
            pos = tokenizer.position
            length = tokenizer.length
            text = tokenizer.text

            while pos < length:
                if text[pos] == ']':
                    if pos + 2 < length and text[pos:pos + 3] == "]]>":
                        pos += 3
                        break
                    else:
                        data_parts.append(']')
                        pos += 1
                        continue
                elif text[pos] == '\x00':
                    tokenizer.log_error(ParseError.UNEXPECTED_NULL_CHARACTER)
                    data_parts.append("\uFFFD")
                else:
                    data_parts.append(text[pos])
                pos += 1

            tokenizer.position = pos
            if data_parts:
                token_text = "".join(data_parts)
                tokenizer.append_to_buffer(token_text)
            tokenizer.read_raw_characters_in_blocks(tokenizer, ch)

        self.set_default_transition(TokenizerState.CDATA_SECTION_STATE,TokenizerState.DATA_STATE, default_action=read_cdata)
        self.set_transition(TokenizerState.CDATA_SECTION_STATE,EOF_STATE, action=TWHTMLTokenizer.handle_eof_in_cdata)

    @staticmethod
    def handle_character_reference(tokenizer, ch, from_attribute=False):
        pos = tokenizer.position+1
        length = tokenizer.length
        temp_buf = []
        char_ref_code = 0

        class SubState:
            CHAR_REF = "CHAR_REF"
            NAMED_CHAR_REF = "NAMED_CHAR_REF"
            NUMERIC_CHAR_REF = "NUMERIC_CHAR_REF"
            HEX_CHAR_REF_START = "HEX_CHAR_REF_START"
            DEC_CHAR_REF_START = "DEC_CHAR_REF_START"
            HEX_CHAR_REF = "HEX_CHAR_REF"
            DEC_CHAR_REF = "DEC_CHAR_REF"
            NUMERIC_CHAR_REF_END = "NUMERIC_CHAR_REF_END"
            DONE = "DONE"

        sub_state = SubState.CHAR_REF
        ch=''
        name_buf = []

        def is_ascii_alnum(ch):
            return ch.isalnum() and ch.isascii()

        def flush_temp_buf():
            nonlocal temp_buf
            flush_str = ''.join(temp_buf)
            if from_attribute:
                if tokenizer.current_token and tokenizer.current_token.attributes:
                    tokenizer.current_token.attributes[-1].value += flush_str

            else:
                tokenizer.append_to_buffer(flush_str)
            temp_buf = []

        def next_char():
            nonlocal pos
            if pos < length:
                ch = tokenizer.text[pos]
                pos += 1
                return ch
            return None  # EOF_STATE sentinel

        def next_char_check(pos):
            if pos < length:
                ch = tokenizer.text[pos+1]
                return ch
            return None

        def reconsume(x=1):
            nonlocal pos
            pos = max(0, pos - x)

        def set_position(new_pos):
            nonlocal pos
            pos = new_pos

        while sub_state != SubState.DONE:
            if sub_state == SubState.CHAR_REF:

                ch = next_char()
                if ch is None:
                    temp_buf.append("&")
                    flush_temp_buf()
                    sub_state = SubState.DONE
                    break

                if not temp_buf:
                    temp_buf.append("&")

                if ch.isalnum():
                    reconsume()
                    sub_state = SubState.NAMED_CHAR_REF

                elif ch == '#':
                    temp_buf.append("#")
                    sub_state = SubState.NUMERIC_CHAR_REF

                else:
                    flush_temp_buf()
                    reconsume(2)
                    sub_state = SubState.DONE


            elif sub_state == SubState.NAMED_CHAR_REF:
                """
                Named character reference state.
                """
                name_buf.clear()
                semicolon_found = False
                start_pos=pos
                best_cand=''


                for i in range(MAX_LEN_ENTITY):
                    c = next_char()
                    if c is None:
                        break
                    if is_ascii_alnum(c):
                        name_buf.append(c)
                    elif c == ';':
                        name_buf.append(c)
                        break
                    else:
                        reconsume()
                        break

                n = len(name_buf)
                if n < MIN_LEN_ENTITY:
                    if name_buf:
                        temp_buf.append("".join(name_buf))

                    set_position(start_pos + len(name_buf) - 1)
                    flush_temp_buf()
                    sub_state = SubState.DONE
                    continue

                if 26 <= n <= 31:
                    n = 25

                best_value = None

                for cand_len in range(n, MIN_LEN_ENTITY - 1, -1):
                    lookup_key = "".join(name_buf[:cand_len])
                    val = lookup_entity_value_py(lookup_key)
                    if val is not None:
                        best_value = val
                        best_cand=lookup_key
                        break

                if best_value is None:
                    temp_buf.append("".join(name_buf))
                    set_position(start_pos + len(name_buf) - 1)
                    flush_temp_buf()
                    sub_state = SubState.DONE
                    continue


                if best_value.endswith('\\'):
                    best_value += '\\'
                entity_value = best_value.encode("utf-8").decode("unicode-escape")

                if best_cand[-1]==";":
                    semicolon_found=True

                if from_attribute and not semicolon_found:
                    next_ch_check = next_char_check((start_pos + len(best_cand) -1))
                    if entity_value and not (next_ch_check == "=" or is_ascii_alnum(next_ch_check)):
                        temp_buf.clear()
                        temp_buf.append(entity_value)
                    else:
                        temp_buf.append("".join(name_buf))

                    set_position(start_pos + len(name_buf) - 1)

                    flush_temp_buf()
                    sub_state = SubState.DONE
                    if not semicolon_found:
                        tokenizer.log_error(ParseError.MISSING_SEMICOLON_AFTER_CHARACTER_REFERENCE, position=pos)
                    continue

                temp_buf.clear()
                temp_buf.append(entity_value)
                flush_temp_buf()

                if not semicolon_found:
                    tokenizer.log_error(ParseError.MISSING_SEMICOLON_AFTER_CHARACTER_REFERENCE, position=pos)

                set_position(start_pos+len(best_cand)-1)
                sub_state = SubState.DONE

            elif sub_state == SubState.NUMERIC_CHAR_REF:
                """
                Numeric character reference state
                """
                char_ref_code = 0
                ch = next_char()
                if ch in ('x', 'X'):
                    temp_buf.append(ch)
                    sub_state = SubState.HEX_CHAR_REF_START
                else:
                    reconsume()
                    sub_state = SubState.DEC_CHAR_REF_START

            elif sub_state == SubState.HEX_CHAR_REF_START:
                """
                Hexadecimal character reference start state
                """

                ch = next_char()
                if ch is None:
                    flush_temp_buf()
                    sub_state = SubState.DONE
                elif ch and ch in hex_digit:
                    reconsume()
                    sub_state = SubState.HEX_CHAR_REF
                else:
                    tokenizer.log_error(ParseError.ABSENCE_OF_DIGITS_IN_NUMERIC_CHARACTER_REFERENCE, position=pos)
                    flush_temp_buf()
                    reconsume(2)
                    sub_state = SubState.DONE

            elif sub_state == SubState.DEC_CHAR_REF_START:
                """
                Decimal character reference start state
                """
                ch = next_char()
                if ch is None:
                    flush_temp_buf()
                    sub_state = SubState.DONE
                elif ch.isdigit():
                    reconsume()
                    sub_state = SubState.DEC_CHAR_REF
                else:
                    tokenizer.log_error(ParseError.ABSENCE_OF_DIGITS_IN_NUMERIC_CHARACTER_REFERENCE, position=pos)
                    if ch != "#":
                        temp_buf.append(ch)
                    flush_temp_buf()
                    reconsume()
                    sub_state = SubState.DONE

            elif sub_state == SubState.HEX_CHAR_REF:
                """
                Hexadecimal character reference state
                """
                ch = next_char()
                if ch is None:
                    sub_state = SubState.NUMERIC_CHAR_REF_END
                elif ch in hex_digit:
                    if ch.isdigit():
                        val = ord(ch) - ord('0')
                    elif 'a' <= ch <= 'f':
                        val = ord(ch) - ord('a') + 10
                    else:
                        val = ord(ch) - ord('A') + 10
                    char_ref_code = (char_ref_code * 16) + val
                elif ch == ';':
                    sub_state = SubState.NUMERIC_CHAR_REF_END
                else:
                    sub_state = SubState.NUMERIC_CHAR_REF_END

            elif sub_state == SubState.DEC_CHAR_REF:
                """
                Decimal character reference state
                """
                ch = next_char()

                if ch is None:
                    sub_state = SubState.NUMERIC_CHAR_REF_END

                elif ch.isdigit():
                    temp_buf.append(ch)
                    val = ord(ch) - ord('0')
                    char_ref_code = (char_ref_code * 10) + val
                elif ch == ';':
                    sub_state = SubState.NUMERIC_CHAR_REF_END
                else:
                    sub_state = SubState.NUMERIC_CHAR_REF_END


            elif sub_state == SubState.NUMERIC_CHAR_REF_END:
                """
                Numeric character reference end state
                """
                code = char_ref_code

                if code == 0x00:
                    tokenizer.log_error(ParseError.NULL_CHARACTER_REFERENCE, position=pos)
                    code = 0xFFFD

                elif code > 0x10FFFF:
                    tokenizer.log_error(ParseError.CHARACTER_REFERENCE_OUTSIDE_UNICODE_RANGE, position=pos)
                    code = 0xFFFD

                elif 0xD800 <= code <= 0xDFFF:
                    tokenizer.log_error(ParseError.SURROGATE_CHARACTER_REFERENCE, position=pos)
                    code = 0xFFFD

                # 4) Windows-1252 check (0x80..0x9F)
                elif 0x80 <= code <= 0x9F:
                    mapped = entitiesWindows1252.get(code)
                    if mapped is not None:
                        tokenizer.log_error(ParseError.CONTROL_CHARACTER_REFERENCE, position=pos)
                        temp_buf.clear()
                        temp_buf.append(mapped)
                        flush_temp_buf()
                        sub_state = SubState.DONE
                        if ch != ";":
                            tokenizer.log_error(ParseError.MISSING_SEMICOLON_AFTER_CHARACTER_REFERENCE, position=pos)
                            reconsume(2)
                        else:
                            reconsume()
                        continue
                    else:
                        tokenizer.log_error(ParseError.CONTROL_CHARACTER_REFERENCE, position=pos)

                if (0xFDD0 <= code <= 0xFDEF) or ((code & 0xFFFF) in (0xFFFE, 0xFFFF)):
                    tokenizer.log_error(ParseError.NONCHARACTER_CHARACTER_REFERENCE, position=pos)

                if ((code < 0x20 and code not in (0x09, 0x0A, 0x0C, 0x0D, 0x20))
                        or (code == 0x7F)):
                    tokenizer.log_error(ParseError.CONTROL_CHARACTER_REFERENCE, position=pos)

                try:
                    decoded = chr(code)
                except ValueError:
                    tokenizer.log_error(ParseError.SURROGATE_CHARACTER_REFERENCE, position=pos)
                    decoded = '\uFFFD'
                temp_buf.clear()
                temp_buf.append(decoded)
                flush_temp_buf()
                if ch != ";" and ch is not None:
                    tokenizer.log_error(ParseError.MISSING_SEMICOLON_AFTER_CHARACTER_REFERENCE, position=pos)
                    reconsume(2)
                else:
                    reconsume()
                sub_state = SubState.DONE

        tokenizer.position = pos
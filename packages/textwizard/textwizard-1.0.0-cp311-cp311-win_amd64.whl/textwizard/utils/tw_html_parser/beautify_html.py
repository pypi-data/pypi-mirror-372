# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations
from textwizard.utils.tw_html_parser.parser import TWHTMLParser
from textwizard.utils.tw_html_parser.serializer_pretty import PrettyHTMLSerializer

__all__ = ["beautify_html"]


def beautify_html(
    *,
    html: str,
    indent: int = 2,
    quote_attr_values: str = "spec",
    quote_char: str = '"',
    use_best_quote_char: bool = True,
    minimize_boolean_attributes: bool = False,
    use_trailing_solidus: bool = False,
    space_before_trailing_solidus: bool = True,
    escape_lt_in_attrs: bool = False,
    escape_rcdata: bool = False,
    resolve_entities: bool = True,
    alphabetical_attributes: bool = True,
    strip_whitespace: bool = False,
    include_doctype: bool = True,
    expand_mixed_content: bool = False,
    expand_empty_elements: bool = False,
) -> str:
    """
    Pretty-print raw HTML without changing semantics.
    """
    # Parser contract: TWHTMLParser(html).parse() -> Document
    dom = TWHTMLParser(html).parse()

    serializer = PrettyHTMLSerializer(
        indent=indent,
        expand_mixed_content=expand_mixed_content,
        expand_empty_elements=expand_empty_elements,
        quote_attr_values=quote_attr_values,
        quote_char=quote_char,
        use_best_quote_char=use_best_quote_char,
        minimize_boolean_attributes=minimize_boolean_attributes,
        use_trailing_solidus=use_trailing_solidus,
        space_before_trailing_solidus=space_before_trailing_solidus,
        escape_lt_in_attrs=escape_lt_in_attrs,
        escape_rcdata=escape_rcdata,
        resolve_entities=resolve_entities,
        alphabetical_attributes=alphabetical_attributes,
        strip_whitespace=strip_whitespace,
        include_doctype=include_doctype,
    )

    out = serializer.render(dom)

    # Minimal doctype injection if requested and missing at the start
    if include_doctype and "<!DOCTYPE" not in out[:256].upper():
        out = "<!DOCTYPE html>\n" + out

    # Trim trailing spaces and ensure single terminal newline
    out = "\n".join(line.rstrip() for line in out.splitlines())
    if not out.endswith("\n"):
        out += "\n"
    return out

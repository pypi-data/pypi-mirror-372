# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: BSD-3-Clause

# Metadata content:
METADATA_CONTENT = frozenset({
    "base",
    "link",
    "meta",
    "noscript",
    "script",
    "style",
    "title"
})

# Flow content:
FLOW_CONTENT = frozenset({
    "address",
    "article",
    "aside",
    "blockquote",
    "div",
    "dl",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hgroup",
    "hr",
    "main",
    "nav",
    "ol",
    "p",
    "pre",
    "section",
    "ul",
    "a",
    "abbr",
    "b",
    "bdi",
    "bdo",
    "br",
    "button",
    "cite",
    "code",
    "data",
    "dfn",
    "em",
    "i",
    "img",
    "input",
    "kbd",
    "label",
    "mark",
    "q",
    "ruby",
    "s",
    "samp",
    "small",
    "span",
    "strong",
    "sub",
    "sup",
    "time",
    "u",
    "var",
    "wbr",
})

# Sectioning content:
SECTIONING_CONTENT = frozenset({
    "article",
    "aside",
    "nav",
    "section"
})

# Heading content:
HEADING_CONTENT = frozenset({
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6"
})

# Phrasing content:
PHRASING_CONTENT = frozenset({
    "abbr",
    "audio",
    "b",
    "bdi",
    "bdo",
    "br",
    "button",
    "cite",
    "code",
    "data",
    "dfn",
    "em",
    "i",
    "img",
    "input",
    "kbd",
    "label",
    "mark",
    "math",
    "meter",
    "noscript",
    "object",
    "output",
    "progress",
    "q",
    "ruby",
    "s",
    "samp",
    "script",
    "select",
    "small",
    "span",
    "strong",
    "sub",
    "sup",
    "svg",
    "template",
    "textarea",
    "time",
    "u",
    "var",
    "wbr"
})

# Embedded content:
EMBEDDED_CONTENT = frozenset({
    "audio",
    "canvas",
    "embed",
    "iframe",
    "img",
    "map",
    "object",
    "picture",
    "svg",
    "video",
    "math"
})

# Interactive content: e
INTERACTIVE_CONTENT = frozenset({
    "a",
    "audio",
    "button",
    "details",
    "embed",
    "iframe",
    "img",
    "input",
    "keygen",
    "label",
    "select",
    "textarea",
    "video"
})

PALPABLE_CONTENT = frozenset({
    "a", "abbr", "address", "article", "aside",
    "audio",
    "b", "bdi", "bdo", "blockquote", "button",
    "canvas", "cite", "code", "data", "del",
    "details", "dfn", "div", "dl",
    "em", "embed", "fieldset", "figure", "footer", "form",
    "h1", "h2", "h3", "h4", "h5", "h6", "header", "hgroup",
    "i", "iframe", "img",
    "input",
    "kbd", "label", "main", "map", "mark",
    "math",
    "menu",
    "meter", "nav", "object", "ol",
    "output", "p", "picture", "pre", "progress",
    "q", "ruby", "s", "samp", "search", "section",
    "select", "small", "span", "strong", "sub", "sup",
    "svg", "table", "textarea", "time", "u", "ul",
    "var", "video",
})

# Script-supporting elements
SCRIPT_SUPPORTING = frozenset({
    "script",
    "template"
})
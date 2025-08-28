<img src="https://raw.githubusercontent.com/textwizard-dev/textwizard/main/asset/TextWizard%20Banner.png"
     alt="TextWizard Banner" width="800" height="300">

---

# TextWizard
[![PyPI - Version](https://img.shields.io/pypi/v/textwizard)](https://pypi.org/project/textwizard/)
[![PyPI - Downloads/month](https://img.shields.io/pypi/dm/textwizard?label=PyPI%20downloads)](https://pypistats.org/packages/textwizard)
[![License](https://img.shields.io/pypi/l/textwizard)](https://github.com/textwizard-dev/textwizard/blob/main/LICENSE)


**TextWizard** is a Python library to **extract**, **clean**, and **analyze** text from PDFs, DOCX, images, CSV, HTML/XML, and more. It includes local OCR (Tesseract), cloud OCR with Azure Document Intelligence, multi-backend NER, language detection, lexical statistics, and HTML utilities.


---

## Contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [API overview](#api-overview)
- [Text extraction](#text-extraction)
- [Azure OCR](#azure-ocr)
- [HTML cleaning](#html-cleaning)
- [XML cleaning](#xml-cleaning)
- [CSV cleaning](#csv-cleaning)
- [Named-Entity Recognition (NER)](#named-entity-recognition-ner)
- [Spell checking](#spell-checking)
- [Language detection](#language-detection)
- [Text statistics](#text-statistics)
- [Text similarity](#text-similarity)
- [HTML tools](#html-tools)
- [Migration notes](#migration-notes)
- [License](#license)
- [Resources](#resources)

---
## What is TextWizard?

TextWizard is a Python toolkit for end-to-end text ingestion: it extracts, cleans, and analyzes content from PDFs, Office documents, images, HTML/XML, CSV, and plain text. It unifies local OCR (Tesseract) and Azure Document Intelligence, normalizes noisy markup, and exposes text, tables, and key-value pairs through one consistent API.

It targets production pipelines: deterministic I/O, page selection and hybrid PDF handling, multi-backend NER (spaCy, Stanza), language detection at 160+ languages, compact spell-checking tries, lexical statistics, and HTML utilities (sanitization, pretty-print, HTML→Markdown). The goal is to be a dependable, high-level building block for practical text extraction and cleanup in Python.

---
## Installation

Requires Python 3.9+.

~~~bash
pip install textwizard
~~~

Optional extras:

- **Azure OCR**: `pip install "textwizard[azure]"`
- **NER**: `pip install "textwizard[ner]"`
- **Everything**: `pip install "textwizard[all]"`

> For OCR capabilities, ensure you have [Tesseract](https://github.com/tesseract-ocr/tesseract) installed on your system.  
> For spaCy models, e.g.: `python -m spacy download en_core_web_sm`.

---

## Quick start

~~~python
import textwizard as tw

text = tw.extract_text("example.pdf")
print(text)
~~~

---

## API overview

Method | Purpose
---|---
`extract_text` | Local text extraction with optional Tesseract OCR
`extract_text_azure` | Cloud extraction via Azure (text, tables, key-value)
`clean_html` | High-level HTML cleaning with semantic flags
`clean_xml` | XML cleanup and normalization
`clean_csv` | CSV cleanup with configurable dialect
`extract_entities` | NER via spaCy / Stanza / spaCy-Stanza
`correctness_text` | Spell checking
`lang_detect` | Language detection 
`analyze_text_statistics` | Lexical metrics (entropy, Zipf, Gini, …)
`text_similarity` | Similarity: `cosine`, `jaccard`, `levenshtein`
`beutifull_html` | Pretty-print HTML 
`html_to_markdown` | Convert HTML → Markdown

---

## Text extraction

### Parameters

- `input_data`: `[str, bytes, Path]`  
- `extension`: The file extension, required only if `input_data` is `bytes`.  
- `pages`: Page/sheet selection.  
  • Paged (PDF, DOCX, TIFF): `1`, `"1-3"`, `[1, 3, "5-8"]`  
  • Excel (XLSX/XLS): sheet index (`int`), name (`str`), or mixed list  
- `ocr`: Enables OCR using Tesseract. Applies to PDF/DOCX and image-based files.  
- `language_ocr`: Language code for OCR. Defaults to `'eng'`.

### Examples

Basic:

~~~python
import textwizard as tw

txt = tw.extract_text("docs/report.pdf")
~~~

From bytes:

~~~python
from pathlib import Path
import textwizard as tw

raw = Path("img.png").read_bytes()
txt_img = tw.extract_text(raw, extension="png")
~~~

Paged selection and OCR:

~~~python
import textwizard as tw

sel = tw.extract_text("docs/big.pdf", pages=[1, 3, "5-7"])
ocr_txt = tw.extract_text("scan.tiff", ocr=True, language_ocr="ita")
~~~

#### **Supported Formats**

| Format | OCR Option |
|---|---|
| PDF | Optional |
| DOC | No |
| DOCX | Optional |
| XLSX | No |
| XLS | No |
| TXT | No |
| CSV | No |
| JSON | No |
| HTML | No |
| HTM | No |
| TIF | Default |
| TIFF | Default |
| JPG | Default |
| JPEG | Default |
| PNG | Default |
| GIF | Default |

---

## Azure OCR

### Parameters

- `input_data`: `[str, bytes, Path]`  
- `extension`: File extension when `bytes` are passed.  
- `language_ocr`: OCR language code (ISO-639).  
- `pages`: Page selection (`int`, `"1,3,5-7"`, or list).  
- `azure_endpoint`: Azure Document Intelligence endpoint URL.  
- `azure_key`: Azure API key.  
- `azure_model_id`: `"prebuilt-read"` (text only) or `"prebuilt-layout"` (text + tables + key-value).  
- `hybrid`: If `True`, for PDFs: native text via PyMuPDF and images via OCR.

### Example

~~~python
import textwizard as tw

res = tw.extract_text_azure(
    "invoice.pdf",
    language_ocr="ita",
    azure_endpoint="https://<resource>.cognitiveservices.azure.com/",
    azure_key="<KEY>",
    azure_model_id="prebuilt-layout",
    hybrid=True,
)

print(res.text)
print(res.pretty_tables[:1])
print(res.key_value)
~~~

---

## HTML cleaning

### Parameters

- `text`: `str` HTML input.  
- `remove_script`: Remove executable tags (`<script>`, `<template>`).  
- `remove_metadata_tags`: Remove metadata (`<link>`, `<meta>`, `<base>`, `<noscript>`, `<style>`, `<title>`).  
- `remove_flow_tags`: Remove flow content (`<address>`, `<div>`, `<input>`, …).  
- `remove_sectioning_tags`: Remove sectioning content (`<article>`, `<aside>`, `<nav>`, …).  
- `remove_heading_tags`: Remove heading tags (`<h1>`–`<h6>`).  
- `remove_phrasing_tags`: Remove phrasing content (`<audio>`, `<code>`, `<textarea>`, …).  
- `remove_embedded_tags`: Remove embedded content (`<iframe>`, `<embed>`, `<img>`).  
- `remove_interactive_tags`: Remove interactive content (`<button>`, `<input>`, `<select>`).  
- `remove_palpable`: Remove palpable elements (`<address>`, `<math>`, `<table>`, …).  
- `remove_doctype`: Remove `<!DOCTYPE html>`.  
- `remove_comments`: Remove HTML comments.  
- `remove_specific_attributes`: Remove specific attributes (supports wildcards).  
- `remove_specific_tags`: Remove specific tags (supports wildcards).  
- `remove_empty_tags`: Drop empty tags.  
- `remove_content_tags`: Remove content of given tags.  
- `remove_tags_and_contents`: Remove tags and their contents.


### Behavior

There are three modes with different return types:

| Mode | How to trigger | Output | Description |
|---|---|---|---|
| **A – text-only** | No parameters provided (all `None`) | `str` (plain text) | Extracts text, skips script-supporting tags, inserts safe spaces. |
| **B – structural clean** | At least one flag is `True` | `str` (serialized HTML) | Removes/unwraps per flags. Supports wildcard tag/attribute removal, content stripping, empty-tag pruning. |
| **C – text with preservation** | Parameters present and all `False` | `str` (text + preserved markup) | Extracts text but **preserves** groups explicitly set to `False` (and comments/doctype if set `False`). |


### Examples

**A) Text-only (no params)**

~~~python
import textwizard as tw
txt = tw.clean_html("<div><p>Hello</p><script>x()</script></div>")
print(txt)  # -> "Hello"
~~~

**B) Structural clean (HTML out)**

~~~python
import textwizard as tw

html = """
<html><head><title>x</title><script>evil()</script></head>
<body>
  <article><h1>Title</h1><img src="a.png"><p id="k" onclick="x()">hello</p></article><!-- comment -->
</body></html>
"""
out = tw.clean_html(
    html,
    remove_script=True,
    remove_metadata_tags=True,
    remove_embedded_tags=True,
    remove_specific_attributes=["id", "on*"],
    remove_empty_tags=True,
    remove_comments=True,
    remove_doctype=True,
)
print(out)
~~~
**Output**  
~~~html
<html>
<body>
  <article><h1>Title</h1><p>hello</p></article>

</body></html>
~~~


**C) Text with preservation (False flags)**

~~~python
import textwizard as tw

html = "<html><body><article><h1>T</h1><p>Body</p><!-- c --></article></body></html>"
txt = tw.clean_html(
    html,
    remove_sectioning_tags=False,   # keep <article> in output
    remove_heading_tags=False,      # keep <h1> in output
    remove_comments=False,          # keep comments
)
print(txt)
~~~
**Output**  
~~~html
<article><h1>T</h1>Body<!-- c --></article>
~~~

**Wildcard selectors**

~~~python
import textwizard as tw
html = '<div id="hero" data-track="x" onclick="h()"><img src="a.png"></div>'
out = tw.clean_html(
    html,
    remove_specific_attributes=["id", "data-*", "on*"],
    remove_specific_tags=["im_"],
)
print(out) 
~~~
**Output**  
~~~html
<html><head></head><body><div></div></body></html>
~~~


---

## XML cleaning

### Parameters

- `text`: `str | bytes` XML input.  
- `remove_comments`: Remove `<!-- ... -->`.  
- `remove_processing_instructions`: Remove `<? ... ?>`.  
- `remove_cdata_sections`: Unwrap `<![CDATA[...]]>`.  
- `remove_empty_tags`: Drop empty elements.  
- `remove_namespaces`: Drop prefixes and `xmlns`.  
- `remove_duplicate_siblings`: Keep only the first identical sibling.  
- `collapse_whitespace`: Collapse runs of whitespace.  
- `remove_specific_tags`: Delete tags (supports wildcards).  
- `remove_content_tags`: Keep tag but delete inner content.  
- `remove_attributes`: Delete attributes (supports wildcards).  
- `remove_declaration`: Drop `<?xml ...?>`.  
- `normalize_entities`: Convert entities like `&amp;` → `&`.

### Examples

~~~python
import textwizard as tw

xml = "<root xmlns='ns'><a/><b>ok</b><!-- x --></root>"
fixed = tw.clean_xml(
    xml,
    remove_namespaces=True,
    remove_empty_tags=True,
    remove_comments=True,
    normalize_entities=True,
)
print(fixed)
~~~
**Output**  
~~~xml
<root><b>ok</b></root>
~~~
---

## CSV cleaning

**Behavior**

- Columns can be removed by **name** (with header) or **0-based index**.
- `remove_row_index` uses **0-based** indices over the parsed rows. If a header exists, it is row `0`.
- `remove_values` blanks matching cells. Supports wildcards `*` and `?`.
- `remove_empty_columns` / `remove_empty_rows` run after other edits.
- Output is serialized with the provided dialect (`delimiter`, `quotechar`, `quoting`, etc.).

**Parameters**

- `text`: Raw CSV string.
- `delimiter`, `quotechar`, `escapechar`, `doublequote`, `skipinitialspace`, `lineterminator`, `quoting`.
- `remove_columns`: Name or 0-based index (or list).
- `remove_row_index`: 0-based index (or list).
- `remove_values`: Literal values or wildcard patterns to blank out.
- `remove_duplicates_rows`: Remove duplicate rows.
- `trim_whitespace`: Strip whitespace inside fields.
- `remove_empty_columns`: Drop empty columns.
- `remove_empty_rows`: Drop empty rows.

**Example**

~~~python
import textwizard as tw

csv_data = """id,name,age,city,salary
1,John,30,New York,50000
2,Jane,25,,40000
3,,35,Los Angeles,60000
4,Mark,45,,70000
5,Sarah,40,New York,
1,John,30,New York,50000
"""
out = tw.clean_csv(
    csv_data,
    delimiter=",",
    remove_columns=["id", "salary"],
    remove_values=["John", "50000"],
    trim_whitespace=True,
    remove_empty_columns=True,
    remove_empty_rows=True,
    remove_duplicates_rows=True,
)
print(out)
~~~

**Output**
~~~csv
name,age,city
,30,New York
Jane,25,
,35,Los Angeles
Mark,45,
Sarah,40,New York
~~~

## Named-Entity Recognition (NER)

### Parameters

- `text`: `str` input.  
- `engine`: `'spacy' | 'stanza' | 'spacy_stanza'` (default `'spacy'`).  
- `model`: spaCy model name or path (spaCy engine only).  
- `language`: ISO code for Stanza engines.  
- `device`: `'auto' | 'cpu' | 'gpu'` (default `'auto'`).

### Examples

~~~python
import textwizard as tw

sample = (
    "Alex Rivera traveled to Springfield to meet the research team at Northstar Analytics on 14 March 2025. "
    "The next day, he signed a pilot agreement with Horizon Bank and gave a talk at the University of Westland at 10:30 AM."
)
res = tw.extract_entities(sample)
print([e.text for e in res.entities["PERSON"]])
print([e.text for e in res.entities["GPE"]])
print([e.text for e in res.entities["ORG"]])
~~~

**Output**   
~~~text
['Alex Rivera']
['Springfield']
['Northstar Analytics', 'Horizon Bank', 'the University of Westland']
~~~


---

## Spell checking

### Parameters

- `text`: String to analyze.  
- `language`: ISO code.  
- `dict_dir`: Folder with `*.marisa.zst` dictionaries. If `None`, user data dir and on-demand downloads.  
- `use_mmap`: `True` to memory-map the uncompressed trie.

### Example

~~~python
import textwizard as tw

check = tw.correctness_text("Thiss sentense has a typo.", language="en")
print(check)
~~~

**Output**  
~~~json
{'errors_count': 2, 'errors': ['thiss', 'sentense']}
~~~

---

## Language detection

Character n-gram detector with smart gating, priors, and linguistic hints.  
**Supports 161 ISO-639-1 languages.** Returns either a single top-1 code or a ranked list with probabilities.

### Parameters

- `text`: Input string (Unicode).  
- `top_k`: Number of candidates to return (default `3`).  
- `profiles_dir`: Override the bundled profiles directory.  
- `use_mmap`: If `True`, memory-map the profile tries (lower RAM; first access may be slightly slower).  
- `return_top1`: If `True`, return only the best language code; otherwise a list of `(lang, prob)`.


### Examples

**Top-1 (single code)**

```python
import textwizard as tw

text = "Ciao, come stai oggi?"
lang = tw.lang_detect(text, return_top1=True)
print(lang) 
```
**Output**  
~~~
it
~~~
**Top-k distribution**

```python
import textwizard as tw

text = "The quick brown fox jumps over the lazy dog."
langs = tw.lang_detect(text, top_k=5, return_top1=False)
print(langs) 
```
**Output**  
~~~list
[('en', 0.9999376335362183), ('mg', 4.719212057614953e-05), ('fy', 1.4727973350205069e-05), ('rm', 2.8718519851832537e-07), ('la', 1.5918465665694727e-07)]
~~~
**Batch example**

```python
import textwizard as tw

tests = [
    "これは日本語のテスト文です。",
    "Alex parle un peu français, aber nicht so viel.",
    "¿Dónde está la estación de tren?",
]
for s in tests:
    print("TOP1:", tw.lang_detect(s, return_top1=True))
```
**Output**  
~~~
TOP1: ja
TOP1: fr
TOP1: es
~~~

**Custom profiles & mmap**

```python
from pathlib import Path
import textwizard as tw

langs = tw.lang_detect(
    "Buongiorno a tutti!",
    profiles_dir=Path("/opt/textwizard/profiles"),  # custom profiles
    use_mmap=True,                                   # lower RAM
    top_k=3,
)
print(langs)
```
---

## Text statistics

### Parameters

Computes: `entropy`, `zipf.slope`, `zipf.r2`, `vocab_gini`, `type_token_ratio`, `hapax_ratio`, `simpson_index`, `yule_k`, `avg_word_length`.  
Tokens are lower-cased and split on whitespace.

### Example

~~~python
import textwizard as tw

stats = tw.analyze_text_statistics("a a a b b c d e f g")
print(stats)
~~~
**Output**  
~~~json
{'entropy': 2.646, 'zipf': {'slope': -0.605, 'r2': 0.838}, 'vocab_gini': 0.229, 'type_token_ratio': 0.7, 'hapax_ratio': 0.5, 'simpson_index': 0.82, 'yule_k': 800.0, 'avg_word_length': 1.0}
~~~
---

## Text similarity

Compute a similarity score between two strings using one of three measures.  
Returns a **float in [0.0, 1.0]** (`1.0` ≡ identical).

**Parameters**
- `a`, `b`: Strings to compare.  
- `method`: `"cosine" | "jaccard" | "levenshtein"` (default `"cosine"`).

**Notes**
- Tokenization for cosine/jaccard uses lowercase word tokens matched by `\w+` (Unicode letters, digits, underscore).
- Quick guide:

| Method | Best for | Trade-offs |
|---|---|---|
| cosine | “bag of words” overlap incl. short phrases | needs some tokens; bigram TF helps with order |
| jaccard | set overlap (unique words) | ignores frequency; robust to duplicates |
| levenshtein | character-level edits | `O(len(a)·len(b))`; great for short strings |

- **Example**
```python
import textwizard as tw

s1 = tw.text_similarity("kitten", "sitting", method="levenshtein")
s2 = tw.text_similarity("hello world", "hello brave world", method="jaccard")
s3 = tw.text_similarity("abc def", "abc xyz", method="cosine")
print(s1, s2, s3)
```

**Output**  
~~~text
0.5714285714285714
0.6666666666666666
0.33333333333333337
~~~
---

## Beutifull HTML

Pretty-print raw HTML without changing its semantics. Controls indentation, attribute quoting/sorting, whitespace normalization, and optional DOCTYPE insertion.

### Parameters

- `html`: Raw HTML string.  
- `indent`: Spaces per indentation level (default `2`).  
- `quote_attr_values`: `"always" | "spec" | "legacy"` (default `"spec"`).  
- `quote_char`: `"` or `'` (default `"`).  
- `use_best_quote_char`: If `true`, auto-pick the quote char that needs fewer escapes.  
- `minimize_boolean_attributes`: If `true`, render compact booleans (e.g., `disabled`).  
- `use_trailing_solidus`: If `true`, add a trailing slash on void elements (`<br />`).  
- `space_before_trailing_solidus`: Add a space before that slash when used.  
- `escape_lt_in_attrs`: Escape `<` and `>` inside attribute values.  
- `escape_rcdata`: Escape within RCData (`<script>`, `<style>`, `<textarea>`).  
- `resolve_entities`: Prefer named entities when serializing.  
- `alphabetical_attributes`: Sort attributes alphabetically.  
- `strip_whitespace`: Trim/collapse whitespace in text nodes.  
- `include_doctype`: Prepend `<!DOCTYPE html>` if missing.  
- `expand_mixed_content`: Put each child of mixed-content nodes on its own line.  
- `expand_empty_elements`: Render empty non-void elements on two lines.  

### Example

```python
import textwizard as tw

html = """
<body>
  <button id='btn1' class="primary" disabled="disabled">
    Click   <b>me</b>
  </button>
  <img alt="Logo" src="/static/logo.png">
</body>
"""

pretty = tw.beutifull_html(
    html=html,
    indent=4,
    alphabetical_attributes=True,
    minimize_boolean_attributes=True,
    quote_attr_values="always",
    strip_whitespace=True,
    include_doctype=True,
    expand_mixed_content=True,
    expand_empty_elements=True,
)

print(pretty)
```

**Output**  
~~~html
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body>

        <button class="primary" disabled id="btn1">
            Click
            <b>
                me
            </b>

        </button>

        <img alt="Logo" src="/static/logo.png">

    </body>
</html>
~~~

## HTML → Markdown

### Parameters

- `html`: Raw HTML input.

### Example

~~~python
import textwizard as tw

md = tw.html_to_markdown("<h1>Hello</h1><p>World</p>")
print(md)
~~~
**Output**  
~~~markdown
# Hello

World
~~~
---


## License

[AGPL-3.0-or-later](LICENSE).

## RESOURCES

- [GitHub Repository](https://github.com/textwizard-dev/TextWizard)
- [Documentation](https://textwizard.readthedocs.io/en/latest/)
- [PyPI Package](https://pypi.org/project/textwizard/)
---

## Contact & Author

**Author:** Mattia Rubino  
**Email:** <textwizard.dev@gmail.com>

<img src="https://raw.githubusercontent.com/textwizard-dev/wizardhtml/main/asset/WizardHTML%20Banner.png"
     alt="WizardHTML Banner" width="800" height="300">

---

# WizardHTML
[![PyPI - Version](https://img.shields.io/pypi/v/wizardhtml)](https://pypi.org/project/wizardhtml/)
[![PyPI - Downloads/month](https://img.shields.io/pypi/dm/wizardhtml?label=PyPI%20downloads)](https://pypistats.org/packages/wizardhtml)
[![License](https://img.shields.io/pypi/l/wizardhtml)](https://github.com/texwhizard-dev/wizardhtml/blob/main/LICENSE)


**WizardHTML** is a Python library for WHATWG-compliant HTML5 toolkit: DFA tokenizer, spec-guided tree builder, DOM, configurable serializer, and helpers for cleaning, pretty-printing, and HTML→Markdown.

---

## Contents
- [Installation](#installation)
- [Quick start](#quick-start)
- [Public API](#public-api)
- [Parsing](#Parse)
- [HTML cleaning](#html-cleaning)
- [Text helper](#to_text)
- [Beautiful HTML](#beautiful-html)
- [Serialization](#serialization)
- [HTML → Markdown](#html--markdown)
- [License](#license)
- [Resources](#resources)
- [Contact & Author](#contact--author)

---
## Installation

Requires Python 3.9+.

~~~bash
pip install wizardhtml
~~~

---

## Quick start

```python
import wizardhtml as wh

# Mode A: text-only extraction
print(wh.clean_html("<div><p>Hello</p><script>x()</script></div>"))  # -> "Hello"

# Pretty print
html = "<body><p>Hi <b>there</b></p><img src=x></body>"
print(wh.beautiful_html(html, indent=2))

# HTML → Markdown
print(wh.html_to_markdown("<h1>T</h1><p>Body</p>"))

# Parser and DOM
doc = wh.parse("<!doctype html><html><body><p>Hi</p></body></html>")
```

---

## Public API

Function | Purpose
---|---
`parse(html, fragment_context=None, return_errors=False)` | Parse into `Document` or `DocumentFragment`; optional parse error list
`clean_html(text, **flags)` | HTML cleaning with modes A/B/C
`beautiful_html(html, **opts)` | Non-destructive pretty-printer
`html_to_markdown(html)` | HTML → Markdown (best-effort)
`serialize(node, **opts)` | Serialize DOM → HTML
`to_text(html, separator="\n", strip=True, collapse_ws=True)` | Extract readable text (Mode A + whitespace normalization)

---

## `Parse`

Parse HTML as full document or fragment. Collect spec-like parse errors when requested.

**Parameters**

| Name | Type | Default | Meaning |
|---|---|---|---|
| `html` | `str` | required | Input HTML. |
| `fragment_context` | `str \| None` | `None` | Context element name for fragment parsing (e.g., `"div"`, `"template"`, `"tbody"`, `"svg"`, `"math"`). |
| `return_errors` | `bool` | `False` | If `True`, return `(node, errors:list[str])`. |


- Full document when `fragment_context is None` → returns `Document`.
- Fragment parsing with context name (e.g. `"div"`, `"template"`, `"tbody"`, `"svg"`, `"math"`) → returns `DocumentFragment`.
- `return_errors=True` returns `(node, list[str])`.

```python
import wizardhtml as wh

doc = wh.parse("<!doctype html><html><body><p>Hi</p></body></html>")
frag = wh.parse("<li>item</li>", fragment_context="ul")
node, errors = wh.parse("<p><b>x</p>", return_errors=True)
```

---

## HTML cleaning

Clean HTML with granular flags. Three modes: A) all `None` → text-only, B) any `True` → HTML sanitized, C) all provided and `False` → text with selected markup preserved.


### Behavior

There are three modes with different return types:

| Mode | How to trigger | Output | Description |
|---|---|---|---|
| **A – text-only** | No parameters provided (all `None`) | `str` (plain text) | Extracts text, skips script-supporting tags, inserts safe spaces. |
| **B – structural clean** | At least one flag is `True` | `str` (serialized HTML) | Removes/unwraps per flags. Supports wildcard tag/attribute removal, content stripping, empty-tag pruning. |
| **C – text with preservation** | Parameters present and all `False` | `str` (text + preserved markup) | Extracts text but **preserves** groups explicitly set to `False` (and comments/doctype if set `False`). |


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

### Examples


**A) Text-only (no params)**

~~~python
import wizardhtml as wh
txt = wh.clean_html("<div><p>Hello</p><script>x()</script></div>")
print(txt)  # -> "Hello"
~~~

**B) Structural clean (HTML out)**

~~~python
import wizardhtml as wh

html = """
<html><head><title>x</title><script>evil()</script></head>
<body>
  <article><h1>Title</h1><img src="a.png"><p id="k" onclick="x()">hello</p></article><!-- comment -->
</body></html>
"""
out = wh.clean_html(
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
import wizardhtml as wh

html = "<html><body><article><h1>T</h1><p>Body</p><!-- c --></article></body></html>"
txt = wh.clean_html(
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
import wizardhtml as wh
html = '<div id="hero" data-track="x" onclick="h()"><img src="a.png"></div>'
out = wh.clean_html(
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

## to_text

Extract readable text using Mode A internally, then normalize whitespace and separators.
**Parameters**

| Name | Type | Default | Meaning |
|---|---|---|---|
| `html` | `str` | required | Source HTML. |
| `separator` | `str` | `"\n"` | Line separator used in final string. |
| `strip` | `bool` | `True` | Trim leading/trailing whitespace. |
| `collapse_ws` | `bool` | `True` | Collapse runs of spaces and blank lines. |

```python
import wizardhtml as wh
txt = wh.to_text("<div> A <b> B </b>\n\n <i>C</i></div>", separator=" ")
print(txt)  # "A B C"
```

---

## Beautiful HTML

Pretty-print HTML without changing semantics. Controls indentation, quoting, attribute ordering, whitespace, DOCTYPE.

**Parameters**

| Name | Type | Default | Meaning |
|---|---|---|---|
| `html` | `str` | required | Raw HTML input. |
| `indent` | `int` | `2` | Spaces per level. |
| `quote_attr_values` | `"always" \| "spec" \| "legacy"` | `"spec"` | Attribute quoting policy. |
| `quote_char` | `"\""` or `"'"` | `"` | Preferred quote char. |
| `use_best_quote_char` | `bool` | `True` | Auto-pick quote char to minimize escapes. |
| `minimize_boolean_attributes` | `bool` | `False` | Render compact booleans (`disabled`). |
| `use_trailing_solidus` | `bool` | `False` | Add `/` on void elements. |
| `space_before_trailing_solidus` | `bool` | `True` | Space before `/` if used. |
| `escape_lt_in_attrs` | `bool` | `False` | Escape `<` `>` in attributes. |
| `escape_rcdata` | `bool` | `False` | Escape inside RCData. |
| `resolve_entities` | `bool` | `True` | Prefer named entities. |
| `alphabetical_attributes` | `bool` | `True` | Sort attributes alphabetically. |
| `strip_whitespace` | `bool` | `False` | Trim/collapse text-node whitespace. |
| `include_doctype` | `bool` | `True` | Insert `<!DOCTYPE html>` if missing. |
| `expand_mixed_content` | `bool` | `True` | Put mixed-content children on own lines. |
| `expand_empty_elements` | `bool` | `True` | Render empty non-void on two lines. |


```python
import wizardhtml as wh

html = """
<body>
  <button id='btn1' class="primary" disabled="disabled">
    Click   <b>me</b>
  </button>
  <img alt="Logo" src="/static/logo.png">
</body>
"""
pretty = wh.beautiful_html(
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

---

## Serialization

**Parameters**

| Name | Type | Default | Meaning |
|---|---|---|---|
| `node` | `Node` | required | `Document`, `DocumentFragment`, `Element`, `Text`, `Comment`. |
| `quote_attr_values` | `"spec" \| "legacy" \| "always"` | `"spec"` | Quoting policy. |
| `quote_char` | `"\""` or `"'"` | `"` | Preferred quote char. |
| `use_best_quote_char` | `bool` | `True` | Minimize escapes. |
| `minimize_boolean_attributes` | `bool` | `False` | Compact booleans. |
| `resolve_entities` | `bool` | `True` | Prefer named entities. |
| `alphabetical_attributes` | `bool` | `False` | Sort attributes. |
| `strip_whitespace` | `bool` | `False` | Trim/collapse text-node whitespace. |
| `include_doctype` | `bool` | `True` | Applies only when `node` is `Document`. |


**Example**

```python
import wizardhtml as wh

doc = wh.parse("<!doctype html><html><body><p id='x'>Hi</p></body></html>")
print(wh.serialize(doc, alphabetical_attributes=True))        # with DOCTYPE
p = wh.parse("<p id='x'>Hi</p>", fragment_context="div")
print(wh.serialize(p, include_doctype=False))                 # no DOCTYPE for fragments
```

---

## HTML → Markdown

Best-effort conversion of common HTML structures to Markdown; falls back to original HTML if conversion is unsafe.

**Parameters**

| Name | Type | Default | Meaning |
|---|---|---|---|
| `html` | `str` | required | Raw HTML input. |


### Example

~~~python
import wizardhtml as wh

md = wh.html_to_markdown("<h1>Hello</h1><p>World</p>")
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

- [GitHub Repository](https://github.com/texwhizard-dev/WizardHTML)
- [Documentation](https://WizardHTML.readthedocs.io/en/latest/)
- [PyPI Package](https://pypi.org/project/wizardhtml/)
---

## Contact & Author

**Author:** Mattia Rubino  
**Email:** <texwhizard.dev@gmail.com>

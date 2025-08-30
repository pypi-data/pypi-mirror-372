# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations
from wizardhtml.wizard_cleaners.tw_html_cleaner.html_cleaner import HTMLCleaner
from typing import Union
from wizardhtml.utils.tw_html_parser.dom import (
    Node, Document, DocumentFragment, Element, Text, Comment
)



class WizardHTML:
    def __init__(self):
        self._html_cleaner = HTMLCleaner()


    def parse(
            self,
            html: str,
            fragment_context: str | None = None,
            return_errors: bool = False,
    ):
        """
        Parse HTML into a DOM tree using a WHATWG-compliant tree builder.

        This is a thin wrapper over the internal parser. It supports both full
        document parsing and fragment parsing with a context element, mirroring
        browser behavior (insertion modes, foster parenting, foreign content).

        Args:
            html: The HTML source string.
            fragment_context: Optional context element name for fragment parsing
                (e.g., "div", "template", "tbody", "svg", "math"). If None, the
                input is parsed as a full document.
            return_errors: If True, also return a list of parse errors collected
                during tree construction. Errors are informative and do not stop
                parsing.

        Returns:
            - Document (full parse) or DocumentFragment (fragment parse).
            - If ``return_errors=True``: a tuple ``(node, errors)`` where
              ``errors`` is ``list[str]``.

        Notes:
            - Conforms to the HTML Standard (WHATWG): insertion modes, implied
              end tags, active formatting elements, foster parenting for table
              text, and correct integration with SVG/MathML (foreign content).
            - Fragment parsing sets the tokenizer state according to the context
              element (e.g., RCDATA for <textarea>, RAWTEXT for <style>, etc.).
            - The returned node is owned by an internal Document; adopt/import
              nodes as needed before moving them to another tree.

        Examples:
            >>> import wizardhtml as wh
            >>> node = wh.parse("<!doctype html><html><body><p>Hi</p></body></html>")
            >>> frag = wh.parse("<li>item</li>", fragment_context="ul")
            >>> node, errors = wh.parse("<p><b>x</p>", return_errors=True)
        """
        if not isinstance(html, str):
            raise TypeError("html must be a str")

        from wizardhtml.utils.tw_html_parser.parser import TWHTMLParser

        parser = TWHTMLParser(html)
        if fragment_context is None:
            node = parser.parse()
        else:
            node = parser.parse_fragment(container=fragment_context)

        if return_errors:
            return node, list(parser.errors)
        return node

    
    
    # -----------------------
    # Serialize helpers
    # -----------------------
    def serialize(
            self,
            node: Node | Document | DocumentFragment | Element | Text | Comment,
            *,
            quote_attr_values: str = "spec",
            quote_char: str = '"',
            use_best_quote_char: bool = True,
            minimize_boolean_attributes: bool = False,
            resolve_entities: bool = True,
            alphabetical_attributes: bool = False,
            strip_whitespace: bool = False,
            include_doctype: bool = True,
    ) -> str:
        from wizardhtml.utils.tw_html_parser.serializer import serialize as _serialize
        return _serialize(
            node,
            quote_attr_values=quote_attr_values,
            quote_char=quote_char,
            use_best_quote_char=use_best_quote_char,
            minimize_boolean_attributes=minimize_boolean_attributes,
            resolve_entities=resolve_entities,
            alphabetical_attributes=alphabetical_attributes,
            strip_whitespace=strip_whitespace,
            include_doctype=include_doctype,
        )
    
    
    # ----------------------------------------------------------------------
    # HTML cleaning
    # ----------------------------------------------------------------------
    def to_text(
            self,
            html: str,
            separator: str = "\n",
            strip: bool = True,
            collapse_ws: bool = True,
    ) -> str:
        """
        Extract readable text from HTML using the cleaner's Mode A, then optionally
        normalize whitespace.

        - Delegates extraction to `clean_html(html)` with all flags None.
        - If `collapse_ws=True`, collapses intra-line spaces and multiple blank lines.
        - Replaces internal newlines with `separator` at the end.

        Args:
            html: Source HTML string.
            separator: Line separator to use in the final string. Default: "\\n".
            strip: Trim leading/trailing whitespace on the final string.
            collapse_ws: Collapse runs of whitespace and multiple blank lines.

        Returns:
            Plain-text string.
        """
        if not isinstance(html, str):
            raise TypeError("html must be a str")

        # Mode A: all flags None → text-only extraction from the cleaner
        text = self.clean_html(html)

        if collapse_ws:
            import re
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            text = re.sub(r"[ \t\f\v]+", " ", text)
            text = re.sub(r" *\n *", "\n", text)
            text = re.sub(r"\n{2,}", "\n", text)

        if strip:
            text = text.strip()

        # Apply the requested separator
        if separator != "\n":
            text = text.replace("\n", separator)

        return text

    def clean_html(
            self,
            text: str,
            remove_script: bool = None,
            remove_metadata_tags: bool = None,
            remove_flow_tags: bool = None,
            remove_sectioning_tags: bool = None,
            remove_heading_tags: bool = None,
            remove_phrasing_tags: bool = None,
            remove_embedded_tags: bool = None,
            remove_interactive_tags: bool = None,
            remove_palpable: bool = None,
            remove_doctype: bool = None,
            remove_comments: bool = None,
            remove_specific_attributes: Union[str, list, None] = None,
            remove_specific_tags: Union[str, list, None] = None,
            remove_empty_tags: bool = None,
            remove_content_tags: Union[str, list, None] = None,
            remove_tags_and_contents: Union[str, list, None] = None,
    ) -> str:
        """
         Modes
        -----
        A) No parameters provided (all None) → **Text-only extraction**
           - Returns: str (plain text)
           - Behavior: traverses DOM, skips SCRIPT_SUPPORTING tags, concatenates text with safe spacing.
    
        B) At least one parameter is True → **Structural clean (destructive)**
           - Returns: str (serialized HTML)
           - Behavior:
             * Group removals (scripts/metadata/flow/sectioning/headings/phrasing/embedded/interactive/palpable)
             * Optional removals: doctype, comments
             * Extra selectors (only in Mode B):
                 - remove_specific_tags: unwrap tags matched by names/wildcards
                 - remove_tags_and_contents: delete tags and their contents
                 - remove_content_tags: keep tag, drop inner content
                 - remove_specific_attributes: delete matching attributes
                 - remove_empty_tags: prune empty nodes after edits
             * Preserves readable spacing when deleting nodes.
    
        C) Parameters provided and all are False → **Text extraction with preservation**
           - Returns: str (mostly text, with selected tags/comments/doctype preserved inline)
           - Behavior:
             * Any group flagged False is **preserved** as markup in the output
               (e.g., remove_heading_tags=False keeps <h1>…</h6>).
             * remove_comments=False and/or remove_doctype=False preserve those nodes.



        Args:
            text (str): The HTML text to be cleaned.
            remove_script (bool, optional): Removes script tags containing executable code (e.g., <script>, <template>).
            remove_metadata_tags (bool, optional): Removes metadata tags (e.g., <link>, <meta>, <base>, <noscript>, <script>, <style>, <title>).
            remove_flow_tags (bool, optional): Removes flow content tags (e.g., <address>, <div>,<input>.).
            remove_sectioning_tags (bool, optional): Removes sectioning content tags (e.g., <article>, <aside>,<nav>.)..
            remove_heading_tags (bool, optional): Removes heading tags (e.g., <h1> to <h6>).
            remove_phrasing_tags (bool, optional): Removes phrasing content tags (e.g., <audio>, <code>,<textarea>.)..
            remove_embedded_tags (bool, optional): Removes embedded content tags (e.g., <iframe>, <embed>, <img>).
            remove_interactive_tags (bool, optional): Removes interactive content tags (e.g., <button>, <input>, <select>).
            remove_palpable (bool, optional): Removes palpable content elements (e.g., <address>, <math>, <table>).
            remove_doctype (bool, optional): Removes the document type declaration (e.g., <!DOCTYPE html>).
            remove_comments (bool, optional): Removes HTML comments.
            remove_specific_attributes (str | list, optional): Specific attributes to remove from tags. Supports wildcards.
            remove_specific_tags (str | list, optional): Specific tags to remove. Supports wildcards.
            remove_empty_tags (bool, optional): Removes empty HTML tags.
            remove_content_tags (str | list, optional): Removes the content of specified tags. Supports wildcards.
            remove_tags_and_contents (str | list, optional): Removes specified tags along with their contents. Supports wildcards.

        Returns:
            str: The cleaned HTML text.

        Raises:
            ValueError: If the input text is not a valid string.
            
        Notes
        -----
        - Wildcards for tag/attribute selectors:
            * "on*"  matches event handlers (onclick, onload, …)
            * "data-*", "aria-*"
            * Exact names or lists are accepted.
        - When DOM becomes empty after removals, returns "".
    
        """
        clean_params = {
            "html.remove_script": remove_script,
            "html.remove_metadata_tags": remove_metadata_tags,
            "html.remove_flow_tags": remove_flow_tags,
            "html.remove_sectioning_tags": remove_sectioning_tags,
            "html.remove_heading_tags": remove_heading_tags,
            "html.remove_phrasing_tags": remove_phrasing_tags,
            "html.remove_embedded_tags": remove_embedded_tags,
            "html.remove_interactive_tags": remove_interactive_tags,
            "html.remove_palpable": remove_palpable,
            "html.remove_doctype": remove_doctype,
            "html.remove_comments": remove_comments,
            "html.remove_specific_attributes": remove_specific_attributes,
            "html.remove_specific_tags": remove_specific_tags,
            "html.remove_empty_tags": remove_empty_tags,
            "html.remove_content_tags": remove_content_tags,
            "html.remove_tags_and_contents": remove_tags_and_contents,
        }

        return self._html_cleaner.clean(text, **clean_params)

   
    
    def beautiful_html(
            self,
            html: str,
            indent: int = 2,
            quote_attr_values: str = "spec",  # "legacy" | "spec" | "always"
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
            expand_mixed_content: bool = True,
            expand_empty_elements: bool = True,
    ) -> str:
        """
            Pretty-print raw HTML without changing its semantics.
            
            This function parses *html* with ``TWHTMLParser``, serializes the DOM with
            ``PrettyHTMLSerializer``, and indents each node by *indent* spaces per depth
            level. It never reflows RCData content (e.g., ``<script>``, ``<style>``,
            ``<textarea>``) and avoids introducing visible whitespace unless explicitly
            requested.
            
            Parameters
            ----------
            html : str
                The HTML string to format.
            indent : int, default 2
                Number of spaces per indentation level.
            quote_attr_values : {"always", "spec", "legacy"}, default "spec"
                Policy for quoting attribute values:
                  - "always": always wrap the value in quotes.
                  - "spec"  : quote only when required by the HTML5 spec
                              (whitespace, quotes, equals, angle brackets, backtick).
                  - "legacy": mimic legacy behavior; quote only for whitespace or quotes.
            quote_char : {"\"", "'"}, default '"'
                Preferred quote character when quoting is applied.
            use_best_quote_char : bool, default True
                If True, choose the quote character that minimizes escaping per attribute.
            minimize_boolean_attributes : bool, default False
                Render boolean attributes in compact form (e.g., ``disabled`` instead of
                ``disabled="disabled"``).
            use_trailing_solidus : bool, default False
                If True, write a trailing solidus on void elements (``<br />``). Purely
                cosmetic in HTML5.
            space_before_trailing_solidus : bool, default True
                If True, insert a space before the trailing solidus if it is used.
            escape_lt_in_attrs : bool, default False
                If True, escape ``<`` and ``>`` inside attribute values.
            escape_rcdata : bool, default False
                If True, escape characters inside RCData elements. Usually leave False.
            resolve_entities : bool, default True
                Replace characters with named entities when available.
            alphabetical_attributes : bool, default True
                Sort attributes alphabetically within each start tag. Useful for diffs.
            strip_whitespace : bool, default False
                Trim leading/trailing whitespace in text nodes and collapse runs of spaces
                to a single space.
            include_doctype : bool, default True
                Prepend ``<!DOCTYPE html>`` if not already present.
            expand_mixed_content : bool, default False
                If True, expand elements that contain both text and child elements so that
                each child appears on its own indented line. May introduce visible
                whitespace in inline contexts.
            expand_empty_elements : bool, default False
                If True, render empty non-void elements on two lines (open and close tag on
                separate lines).
            
            Returns
            -------
            str
                The formatted HTML.
            
            Notes
            -----
            - RCData elements are not pretty-printed internally by default to preserve
              semantics.
            - Void elements remain on a single line and are never given closing tags.
            - This formatter does not alter the DOM structure: it only affects whitespace,
              attribute ordering, quoting, and serialization cosmetics.
            
            """

        from wizardhtml.utils.tw_html_parser.beautify_html import beautify_html

        return beautify_html(
            html=html,
            indent=indent,
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
            expand_mixed_content=expand_mixed_content,
            expand_empty_elements=expand_empty_elements,
        )

    def inner_html(
            self,
            node: Element | DocumentFragment,
    ) -> str:
        """
        Serialize only the children of an Element or DocumentFragment.
        Never includes a <!DOCTYPE>.
        """
        if not isinstance(node, (Element, DocumentFragment)):
            raise TypeError("inner_html: node must be Element or DocumentFragment")
        # child_nodes è la lista del tuo DOM
        return "".join(self.serialize(ch, include_doctype=False) for ch in node.child_nodes)

    def outer_html(
            self,
            node: Node | Document | DocumentFragment | Element | Text | Comment,
    ) -> str:
        """
        Serialize the node itself.
        Includes <!DOCTYPE> only when node is a Document.
        """
        return self.serialize(node, include_doctype=isinstance(node, Document))
    
    
    
    
    def html_to_markdown(self, html: str) -> str:
        """
        Convert HTML to Markdown using TextWizard's internal HTML parser/renderer.

        Parameters
        ----------
        html : str
            Raw HTML string to convert.

        Returns
        -------
        str
            Markdown representation of the input HTML. If the underlying parser
            cannot handle the input, the converter falls back gracefully and
            returns the original HTML string.

        """
        from wizardhtml.utils.tw_html_parser.html_to_md_dom import html_to_markdown_from_html
        return html_to_markdown_from_html(html)

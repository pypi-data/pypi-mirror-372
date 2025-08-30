# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from .wizard_html import WizardHTML
from .utils.tw_html_parser.dom import (
    Node, Document, DocumentFragment, Element, Text, Comment
)
_wizard = WizardHTML()

parse              = _wizard.parse
clean_html         = _wizard.clean_html
beautiful_html     = _wizard.beautiful_html
html_to_markdown   = _wizard.html_to_markdown
serialize          = _wizard.serialize
to_text            = _wizard.to_text



__all__ = [
    "WizardHTML",
    "to_text",
    "clean_html",
    "beautiful_html",    
    "html_to_markdown",
    "parse",
    "serialize",
    "Node", "Document", "DocumentFragment", "Element", "Text", "Comment",
]

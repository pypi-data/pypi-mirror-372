# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


import string

ascii_letters =frozenset(string.ascii_letters)
ascii_uppercase = frozenset(string.ascii_uppercase)
hex_digit = frozenset(string.hexdigits)
ascii_upper2lower = {ord(c): ord(c.lower()) for c in string.ascii_uppercase}

space_characters  = frozenset([
    "\t",   # U+0009
    "\n",   # U+000A
    "\u000C",  # U+000C
    "\r",   # U+000D
    " "     # U+0020
])

null_character= frozenset(["\uFFFD","\u0000"])

RCDATA_ELEMENTS = frozenset([
    "title",
    "textarea"
])
RAWTEXT_ELEMENTS = frozenset([
    "style",
    "xmp",
    "iframe",
    "noembed",
    "noframes"
])

SCRIPT_DATA_ELEMENTS = frozenset(["script"])
PLAINTEXT_ELEMENT = "plaintext"
NOSCRIPT_ELEMENT = "noscript"
HEADING_TAGS = frozenset(("h1", "h2", "h3", "h4", "h5", "h6"))

namespaces = {
    "html": "http://www.w3.org/1999/xhtml",
    "mathml": "http://www.w3.org/1998/Math/MathML",
    "svg": "http://www.w3.org/2000/svg",
    "xlink": "http://www.w3.org/1999/xlink",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "xmlns": "http://www.w3.org/2000/xmlns/"
}
html_integration_point_elements = frozenset([
    (namespaces["mathml"], "annotation-xml"),
    (namespaces["svg"], "foreignObject"),
    (namespaces["svg"], "desc"),
    (namespaces["svg"], "title")
])

mathml_integration_point_elements = frozenset([
    (namespaces["mathml"], "mi"),
    (namespaces["mathml"], "mo"),
    (namespaces["mathml"], "mn"),
    (namespaces["mathml"], "ms"),
    (namespaces["mathml"], "mtext")
])

table_insert_text = frozenset([
    "table",
    "tbody",
    "tfoot",
    "thead",
    "tr"
])
IMPLIED_END_TAGS = {"dd", "dt", "li", "optgroup", "option", "p", "rb", "rp", "rt", "rtc"}

NO_OPEN_ELEMENTS = frozenset(("dd", "dt", "li", "optgroup", "option", "p", "rb", "rp", "rt", "rtc",
               "tbody", "td", "tfoot", "th", "thead", "tr", "body", "html"))

SPECIAL_ELEMENTS = frozenset((
    "address", "applet", "area", "article", "aside", "base", "basefont", "bgsound", "blockquote",
    "body", "br", "button", "caption", "center", "col", "colgroup", "dd", "details", "dir", "div",
    "dl", "dt", "embed", "fieldset", "figcaption", "figure", "footer", "form", "frame", "frameset",
    "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "hr", "html", "iframe", "img",
    "input", "keygen", "li", "link", "listing", "main", "marquee", "menu", "meta", "nav", "noembed",
    "noframes", "noscript", "object", "ol", "p", "param", "plaintext", "pre", "script", "search",
    "section", "select", "source", "style", "summary", "table", "tbody", "td", "template", "textarea",
    "tfoot", "th", "thead", "title", "tr", "track", "ul", "wbr", "xmp"
))


MATHML_ELEMENTS = frozenset(("mi", "mo", "mn", "ms", "mtext", "annotation-xml"))
SVG_ELEMENTS = frozenset(("foreignObject", "desc", "title"))

SCOPE_BOUNDARY_ELEMENTS = frozenset((
    "applet", "caption", "html", "table", "td", "th", "marquee", "object",
)) | MATHML_ELEMENTS | SVG_ELEMENTS

LIST_ITEM_SCOPE_ELEMENTS = SCOPE_BOUNDARY_ELEMENTS | frozenset(("ol", "ul"))

BUTTON_SCOPE_ELEMENTS = SCOPE_BOUNDARY_ELEMENTS | frozenset(("button",))
TABLE_SCOPE_ELEMENTS = frozenset(("html", "table"))
SELECT_SCOPE_EXCLUDED = frozenset(("optgroup", "option"))

SCOPE_SETS = {
    "default":   (SCOPE_BOUNDARY_ELEMENTS,  False),
    "list_item": (LIST_ITEM_SCOPE_ELEMENTS, False),
    "button":    (BUTTON_SCOPE_ELEMENTS,    False),
    "table":     (TABLE_SCOPE_ELEMENTS,    False),
    "select":    (SELECT_SCOPE_EXCLUDED,   True),
}

BREAKOUT_ELEMENTS = frozenset([
    "b", "big", "blockquote", "body", "br",
    "center", "code", "dd", "div", "dl", "dt",
    "em", "embed", "h1", "h2", "h3",
    "h4", "h5", "h6", "head", "hr", "i", "img",
    "li", "listing", "menu", "meta", "nobr",
    "ol", "p", "pre", "ruby", "s", "small",
    "span", "strong", "strike", "sub", "sup",
    "table", "tt", "u", "ul", "var"
])

MATHML_ATTRIBUTE_FIXES = {"definitionurl": "definitionURL"}

SVG_ATTRIBUTE_FIXES = {
    "attributename": "attributeName",
    "attributetype": "attributeType",
    "basefrequency": "baseFrequency",
    "baseprofile": "baseProfile",
    "calcmode": "calcMode",
    "clippathunits": "clipPathUnits",
    "diffuseconstant": "diffuseConstant",
    "edgemode": "edgeMode",
    "filterunits": "filterUnits",
    "glyphref": "glyphRef",
    "gradienttransform": "gradientTransform",
    "gradientunits": "gradientUnits",
    "kernelmatrix": "kernelMatrix",
    "kernelunitlength": "kernelUnitLength",
    "keypoints": "keyPoints",
    "keysplines": "keySplines",
    "keytimes": "keyTimes",
    "lengthadjust": "lengthAdjust",
    "limitingconeangle": "limitingConeAngle",
    "markerheight": "markerHeight",
    "markerunits": "markerUnits",
    "markerwidth": "markerWidth",
    "maskcontentunits": "maskContentUnits",
    "maskunits": "maskUnits",
    "numoctaves": "numOctaves",
    "pathlength": "pathLength",
    "patterncontentunits": "patternContentUnits",
    "patterntransform": "patternTransform",
    "patternunits": "patternUnits",
    "pointsatx": "pointsAtX",
    "pointsaty": "pointsAtY",
    "pointsatz": "pointsAtZ",
    "preservealpha": "preserveAlpha",
    "preserveaspectratio": "preserveAspectRatio",
    "primitiveunits": "primitiveUnits",
    "refx": "refX",
    "refy": "refY",
    "repeatcount": "repeatCount",
    "repeatdur": "repeatDur",
    "requiredextensions": "requiredExtensions",
    "requiredfeatures": "requiredFeatures",
    "specularconstant": "specularConstant",
    "specularexponent": "specularExponent",
    "spreadmethod": "spreadMethod",
    "startoffset": "startOffset",
    "stddeviation": "stdDeviation",
    "stitchtiles": "stitchTiles",
    "surfacescale": "surfaceScale",
    "systemlanguage": "systemLanguage",
    "tablevalues": "tableValues",
    "targetx": "targetX",
    "targety": "targetY",
    "textlength": "textLength",
    "viewbox": "viewBox",
    "viewtarget": "viewTarget",
    "xchannelselector": "xChannelSelector",
    "ychannelselector": "yChannelSelector",
    "zoomandpan": "zoomAndPan",
}

NAMESPACED_ATTRIBUTE_FIXES = {
    "xlink:actuate": ("xlink", "actuate", namespaces['xlink']),
    "xlink:arcrole": ("xlink", "arcrole", namespaces['xlink']),
    "xlink:href": ("xlink", "href", namespaces['xlink']),
    "xlink:role": ("xlink", "role", namespaces['xlink']),
    "xlink:show": ("xlink", "show", namespaces['xlink']),
    "xlink:title": ("xlink", "title", namespaces['xlink']),
    "xlink:type": ("xlink", "type", namespaces['xlink']),
    "xml:lang": ("xml", "lang", namespaces['xml']),
    "xml:space": ("xml", "space", namespaces['xml']),
    "xmlns": (None, "xmlns", namespaces['xmlns']),
    "xmlns:xlink": ("xmlns", "xlink", namespaces['xmlns']),
}


SVG_TAGNAME_FIXES = {
    "altglyph": "altGlyph",
    "altglyphdef": "altGlyphDef",
    "altglyphitem": "altGlyphItem",
    "animatecolor": "animateColor",
    "animatemotion": "animateMotion",
    "animatetransform": "animateTransform",
    "clippath": "clipPath",
    "feblend": "feBlend",
    "fecolormatrix": "feColorMatrix",
    "fecomponenttransfer": "feComponentTransfer",
    "fecomposite": "feComposite",
    "feconvolvematrix": "feConvolveMatrix",
    "fediffuselighting": "feDiffuseLighting",
    "fedisplacementmap": "feDisplacementMap",
    "fedistantlight": "feDistantLight",
    "fedropshadow": "feDropShadow",
    "feflood": "feFlood",
    "fefunca": "feFuncA",
    "fefuncb": "feFuncB",
    "fefuncg": "feFuncG",
    "fefuncr": "feFuncR",
    "fegaussianblur": "feGaussianBlur",
    "feimage": "feImage",
    "femerge": "feMerge",
    "femergenode": "feMergeNode",
    "femorphology": "feMorphology",
    "feoffset": "feOffset",
    "fepointlight": "fePointLight",
    "fespecularlighting": "feSpecularLighting",
    "fespotlight": "feSpotLight",
    "fetile": "feTile",
    "feturbulence": "feTurbulence",
    "foreignobject": "foreignObject",
    "glyphref": "glyphRef",
    "lineargradient": "linearGradient",
    "radialgradient": "radialGradient",
    "textpath": "textPath",
}


VOID_ELEMENTS = frozenset([
    "base",
    "command",
    "event-source",
    "link",
    "meta",
    "hr",
    "br",
    "img",
    "embed",
    "param",
    "area",
    "col",
    "input",
    "source",
    "track",
    "image"
])


rcdata_elements = frozenset([
    'style',
    'script',
    'xmp',
    'iframe',
    'noembed',
    'noframes',
    'noscript'
])

boolean_attributes = {
    "": frozenset(["irrelevant", "itemscope"]),
    "style": frozenset(["scoped"]),
    "img": frozenset(["ismap"]),
    "audio": frozenset(["autoplay", "controls"]),
    "video": frozenset(["autoplay", "controls"]),
    "script": frozenset(["defer", "async"]),
    "details": frozenset(["open"]),
    "datagrid": frozenset(["multiple", "disabled"]),
    "command": frozenset(["hidden", "disabled", "checked", "default"]),
    "hr": frozenset(["noshade"]),
    "menu": frozenset(["autosubmit"]),
    "fieldset": frozenset(["disabled", "readonly"]),
    "option": frozenset(["disabled", "readonly", "selected"]),
    "optgroup": frozenset(["disabled", "readonly"]),
    "button": frozenset(["disabled", "autofocus"]),
    "input": frozenset(["disabled", "readonly", "required", "autofocus", "checked", "ismap"]),
    "select": frozenset(["disabled", "readonly", "autofocus", "multiple"]),
    "output": frozenset(["disabled", "readonly"]),
    "iframe": frozenset(["seamless"]),
}


#dictionary for Windows-1252 specific mappings (0x80-0x9F)
entitiesWindows1252 = {
    0x80: "\u20AC",  # EURO SIGN (€)
    0x82: "\u201A",  # SINGLE LOW-9 QUOTATION MARK (‚)
    0x83: "\u0192",  # LATIN SMALL LETTER F WITH HOOK (ƒ)
    0x84: "\u201E",  # DOUBLE LOW-9 QUOTATION MARK („)
    0x85: "\u2026",  # HORIZONTAL ELLIPSIS (…)
    0x86: "\u2020",  # DAGGER (†)
    0x87: "\u2021",  # DOUBLE DAGGER (‡)
    0x88: "\u02C6",  # MODIFIER LETTER CIRCUMFLEX ACCENT (ˆ)
    0x89: "\u2030",  # PER MILLE SIGN (‰)
    0x8A: "\u0160",  # LATIN CAPITAL LETTER S WITH CARON (Š)
    0x8B: "\u2039",  # SINGLE LEFT-POINTING ANGLE QUOTATION MARK (‹)
    0x8C: "\u0152",  # LATIN CAPITAL LIGATURE OE (Œ)
    0x8E: "\u017D",  # LATIN CAPITAL LETTER Z WITH CARON (Ž)
    0x91: "\u2018",  # LEFT SINGLE QUOTATION MARK (‘)
    0x92: "\u2019",  # RIGHT SINGLE QUOTATION MARK (’)
    0x93: "\u201C",  # LEFT DOUBLE QUOTATION MARK (“)
    0x94: "\u201D",  # RIGHT DOUBLE QUOTATION MARK (”)
    0x95: "\u2022",  # BULLET (•)
    0x96: "\u2013",  # EN DASH (–)
    0x97: "\u2014",  # EM DASH (—)
    0x98: "\u02DC",  # SMALL TILDE (˜)
    0x99: "\u2122",  # TRADE MARK SIGN (™)
    0x9A: "\u0161",  # LATIN SMALL LETTER S WITH CARON (š)
    0x9B: "\u203A",  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK (›)
    0x9C: "\u0153",  # LATIN SMALL LIGATURE OE (œ)
    0x9E: "\u017E",  # LATIN SMALL LETTER Z WITH CARON (ž)
    0x9F: "\u0178",  # LATIN CAPITAL LETTER Y WITH DIAERESIS (Ÿ)
}

# -*- coding: utf-8 -*-
"""
This module contains the core mappings and constants for the CodeBangla transpiler.

It defines the translation from Bangla (in English transliteration) to native Python
keywords, as well as the mapping for converting Bangla numerals to ASCII.
"""

import unicodedata

KEYWORD_MAP = {
    # Keywords
    "chhap": "print",
    "neoa": "input",
    "jodi": "if",
    "noile_jodi": "elif",
    "noile": "else",
    "jotokkhon": "while",
    "shuru": "def",
    "classh": "class",
    "phiredao": "return",
    "sotti": "True",
    "miththa": "False",
    "na": "not",
    "ebong": "and",
    "othoba": "or",
    "chesta_koro": "try",
    "dhoro": "except",
    "seshe": "finally",
    "tulona": "assert",
    "theke": "from",
    "ano": "import",
    "hishabe": "as",
    "bad_dao": "pass",
    "porikkha": "lambda",
    "sathe": "with",
    "tolotupi": "yield",
    "uththapon": "raise",
    "muchhe_dao": "del",
    "shorbogrohon": "global",
    "osthaniyo": "nonlocal",
    "er_jonno": "for",
    "moddhe": "in",
    "thamo": "break",
    "chaliye_jao": "continue",

    # Built-in Functions
    "shongkhya": "int",
    "shobdo": "str",
    "tothyo": "float",
    "talika": "list",
    "shongroho": "set",
    "obhidhan": "dict",
    "jora": "tuple",
    "dhoron": "type",
    "dhoirgho": "len",

    # Operators (less common to replace, but possible)
    "jog": "+",
    "biyog": "-",
    "gun": "*",
    "vag": "/",
    "vagshesh": "%",
}

_BANGLA_NUMERALS = {
    '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
    '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9',
}

# Unicode characters can have multiple representations. Normalizing the keys
# to NFC (Normalization Form C) ensures that matching is consistent, regardless
# of how the source text was encoded.
BANGLA_TO_ENGLISH_NUMERALS = {
    unicodedata.normalize('NFC', k): v for k, v in _BANGLA_NUMERALS.items()
}

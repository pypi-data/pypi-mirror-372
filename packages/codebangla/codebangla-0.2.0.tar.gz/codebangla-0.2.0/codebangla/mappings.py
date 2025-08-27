# -*- coding: utf-8 -*-
"""
This module contains the core mappings and constants for the CodeBangla transpiler.

It defines the translation from Bangla (in English transliteration) to native Python
keywords, as well as the mapping for converting Bangla numerals to ASCII.

This module supports advanced Python features including:
- Async/await patterns
- Type hints and annotations
- Context managers
- Decorators
- Exception handling
- Data structures
- Modern Python features (match/case, walrus operator, etc.)
"""

import unicodedata
from typing import Dict, Optional, Set, List, Tuple, Any

# Core language keywords
CORE_KEYWORDS = {
    # Basic statements
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
    "shunno": "None",
    
    # Logical operators
    "na": "not",
    "ebong": "and",
    "othoba": "or",
    
    # Exception handling
    "chesta_koro": "try",
    "dhoro": "except",
    "seshe": "finally",
    "tulona": "assert",
    "uththapon": "raise",
    
    # Import and module system
    "theke": "from",
    "ano": "import",
    "hishabe": "as",
    
    # Control flow
    "bad_dao": "pass",
    "er_jonno": "for",
    "moddhe": "in",
    "thamo": "break",
    "chaliye_jao": "continue",
    
    # Scope and memory
    "muchhe_dao": "del",
    "shorbogrohon": "global",
    "osthaniyo": "nonlocal",
    
    # Advanced features
    "porikkha": "lambda",
    "sathe": "with",
    "tolotupi": "yield",
    "tolotupi_theke": "yield from",
    
    # Self reference
    "nijei": "self",
}

# Async/await keywords for modern Python
ASYNC_KEYWORDS = {
    "ashinchronous": "async",
    "opeksha": "await",
    "ashinchronous_shuru": "async def",
    "ashinchronous_sathe": "async with",
    "ashinchronous_er_jonno": "async for",
}

# Type annotations and hints
TYPE_KEYWORDS = {
    "dhoron": "type",
    "bishesh_dhoron": "TypeVar",
    "milbe": "Union",
    "hote_pare": "Optional",
    "talika_dhoron": "List",
    "obhidhan_dhoron": "Dict",
    "jora_dhoron": "Tuple",
    "shongroho_dhoron": "Set",
    "kormo_dhoron": "Callable",
    "jenerik": "Generic",
    "literal": "Literal",
    "chabi": "TypedDict",
}

# Built-in functions and data structures
BUILTIN_FUNCTIONS = {
    # Basic data types
    "shongkhya": "int",
    "shobdo": "str",
    "tothyo": "float",
    "jotil": "complex",
    "bool_dhoron": "bool",
    "byte_dhara": "bytes",
    "byte_array": "bytearray",
    
    # Collections
    "talika": "list",
    "shongroho": "set",
    "shunno_shongroho": "frozenset",
    "obhidhan": "dict",
    "jora": "tuple",
    "range_banao": "range",
    
    # Functions
    "dhoirgho": "len",
    "shorbochho": "min",
    "shorbochchho": "max",
    "jog_koro": "sum",
    "shajano": "sorted",
    "ulto": "reversed",
    "gonona": "enumerate",
    "jip": "zip",
    "filter_koro": "filter",
    "map_koro": "map",
    "shob": "all",
    "kono": "any",
    
    # I/O and system
    "kholo": "open",
    "format": "format",
    "repr": "repr",
    "exec": "exec",
    "eval": "eval",
    "compile": "compile",
    
    # Object manipulation
    "bisheshotto": "getattr",
    "bisheshotto_set": "setattr",
    "ache_ki": "hasattr",
    "id_dekho": "id",
    "hash_koro": "hash",
    "instance_ki": "isinstance",
    "subclass_ki": "issubclass",
    "dir_dekho": "dir",
    "vars_dekho": "vars",
    "help_nao": "help",
}

# Modern Python features (3.8+)
MODERN_FEATURES = {
    # Match-case (Python 3.10+)
    "mil": "match",
    "khetre": "case",
    
    # Walrus operator
    "walrus": ":=",
    
    # Positional-only and keyword-only parameters
    "shudhu_position": "/",
    "shudhu_keyword": "*",
    
    # F-strings and formatting
    "f_string": "f",
    "r_string": "r",
    "b_string": "b",
}

# Decorators and meta-programming
DECORATOR_KEYWORDS = {
    "shojja": "property",
    "setter": "setter",
    "deleter": "deleter",
    "static_method": "staticmethod",
    "class_method": "classmethod",
    "cache": "cache",
    "lru_cache": "lru_cache",
    "singledispatch": "singledispatch",
    "overload": "overload",
    "final": "final",
    "abstractmethod": "abstractmethod",
}

# Operators with more comprehensive coverage
OPERATORS = {
    # Arithmetic
    "jog": "+",
    "biyog": "-",
    "gun": "*",
    "vag": "/",
    "vagshesh": "%",
    "ghat": "**",
    "floor_vag": "//",
    
    # Comparison
    "soman": "==",
    "na_soman": "!=",
    "choto": "<",
    "boro": ">",
    "choto_soman": "<=",
    "boro_soman": ">=",
    "identity": "is",
    "na_identity": "is not",
    
    # Assignment
    "jog_assignment": "+=",
    "biyog_assignment": "-=",
    "gun_assignment": "*=",
    "vag_assignment": "/=",
    "vagshesh_assignment": "%=",
    "ghat_assignment": "**=",
    "floor_vag_assignment": "//=",
    
    # Bitwise
    "bitwise_and": "&",
    "bitwise_or": "|",
    "bitwise_xor": "^",
    "bitwise_not": "~",
    "left_shift": "<<",
    "right_shift": ">>",
}

# Combine all mappings
KEYWORD_MAP: Dict[str, str] = {
    **CORE_KEYWORDS,
    **ASYNC_KEYWORDS,
    **TYPE_KEYWORDS,
    **BUILTIN_FUNCTIONS,
    **MODERN_FEATURES,
    **DECORATOR_KEYWORDS,
    **OPERATORS,
}

# Bangla numerals mapping
_BANGLA_NUMERALS = {
    '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
    '৫': '5', '৆': '6', '৭': '7', '৮': '8', '৯': '9',
}

# Unicode characters can have multiple representations. Normalizing the keys
# to NFC (Normalization Form C) ensures that matching is consistent, regardless
# of how the source text was encoded.
BANGLA_TO_ENGLISH_NUMERALS = {
    unicodedata.normalize('NFC', k): v for k, v in _BANGLA_NUMERALS.items()
}

# Keywords that should not be translated (reserved Python keywords)
PROTECTED_KEYWORDS: Set[str] = {
    'def', 'class', 'if', 'else', 'elif', 'while', 'for', 'in', 'try', 'except',
    'finally', 'with', 'as', 'import', 'from', 'return', 'yield', 'lambda',
    'and', 'or', 'not', 'is', 'True', 'False', 'None', 'async', 'await',
    'break', 'continue', 'pass', 'del', 'global', 'nonlocal', 'assert', 'raise'
}

# Special syntax patterns for advanced features
SYNTAX_PATTERNS = {
    # Type annotations
    "dhoron_annotation": ":",
    "return_type": "->",
    
    # Comprehensions
    "list_comp_start": "[",
    "list_comp_end": "]",
    "dict_comp_start": "{",
    "dict_comp_end": "}",
    "set_comp_start": "{",
    "set_comp_end": "}",
    "gen_comp_start": "(",
    "gen_comp_end": ")",
    
    # Context managers
    "context_as": "as",
    "context_comma": ",",
}

def get_keyword_categories() -> Dict[str, List[str]]:
    """Return categorized keywords for documentation and IDE support."""
    return {
        "core": list(CORE_KEYWORDS.keys()),
        "async": list(ASYNC_KEYWORDS.keys()),
        "types": list(TYPE_KEYWORDS.keys()),
        "builtins": list(BUILTIN_FUNCTIONS.keys()),
        "modern": list(MODERN_FEATURES.keys()),
        "decorators": list(DECORATOR_KEYWORDS.keys()),
        "operators": list(OPERATORS.keys()),
    }

def is_valid_keyword(keyword: str) -> bool:
    """Check if a keyword is valid in CodeBangla."""
    return keyword in KEYWORD_MAP

def get_python_equivalent(bangla_keyword: str) -> Optional[str]:
    """Get the Python equivalent for a Bangla keyword."""
    return KEYWORD_MAP.get(bangla_keyword)

def get_all_keywords() -> List[str]:
    """Get all available Bangla keywords."""
    return list(KEYWORD_MAP.keys())

def get_keyword_by_category(category: str) -> List[str]:
    """Get keywords by category."""
    categories = get_keyword_categories()
    return categories.get(category, [])

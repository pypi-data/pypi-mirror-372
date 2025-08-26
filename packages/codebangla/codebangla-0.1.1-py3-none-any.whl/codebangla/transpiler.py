# -*- coding: utf-8 -*-
"""
Core transpiler logic for converting Bangla-Python to standard Python.

This module uses Python's built-in `tokenize` module to safely parse
the source code into tokens. It then reconstructs the code string from these
tokens, replacing specific `NAME` and `NUMBER` tokens with their Python
equivalents while preserving all other code structures like strings, comments,
and indentation.
"""

import io
import tokenize
from typing import List

from .mappings import KEYWORD_MAP
from .utils import convert_bangla_numerals

def transpile(code: str) -> str:
    """
    Transpiles a string of Bangla-Python code to standard Python.

    This function implements a coordinate-based reconstruction approach. It iterates
    through the tokens and uses their exact line and column information to rebuild
    the source code with translated keywords. This is a robust method that
    preserves the original formatting of the user's code.

    Args:
        code: A string containing the source code written with Bangla keywords.

    Returns:
        A string containing the equivalent, standard Python code.
    """
    tokens = tokenize.generate_tokens(io.StringIO(code).readline)
    
    result_parts: List[str] = []
    last_line = 0
    last_col = 0

    for token in tokens:
        start_line, start_col = token.start
        end_line, end_col = token.end

        # Add whitespace and newlines based on token position to preserve formatting
        if start_line > last_line:
            result_parts.append('\n' * (start_line - last_line))
            last_col = 0
        if start_col > last_col:
            result_parts.append(' ' * (start_col - last_col))

        token_string = token.string
        string_to_append = ""

        if token.type == tokenize.NAME:
            string_to_append = KEYWORD_MAP.get(token_string, token_string)
        elif token.type == tokenize.NUMBER:
            # Note: This conversion has a known, unresolved issue in some environments.
            string_to_append = convert_bangla_numerals(token_string)
        elif token.type in (tokenize.ENCODING, tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER):
            # These tokens are ignored; their effect is handled by the coordinate-based reconstruction.
            pass
        else:
            string_to_append = token_string
        
        result_parts.append(string_to_append)
        
        last_line = end_line
        last_col = end_col
        
    return "".join(result_parts)
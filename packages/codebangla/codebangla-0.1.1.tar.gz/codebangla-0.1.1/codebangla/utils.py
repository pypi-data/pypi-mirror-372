# -*- coding: utf-8 -*-
"""General utility functions for the CodeBangla package."""

import unicodedata
from typing import Dict

from .mappings import BANGLA_TO_ENGLISH_NUMERALS

def convert_bangla_numerals(token_string: str) -> str:
    """
    Converts a string containing Bangla numerals to one with ASCII numerals.

    This function handles potential Unicode normalization issues by converting
    the input string to NFC form before character-by-character replacement.

    Args:
        token_string: The input string, likely from the tokenizer.

    Returns:
        A new string with all Bangla numerals replaced by ASCII (0-9) equivalents.
    """
    # Normalize the input string to ensure consistent matching.
    normalized_string = unicodedata.normalize('NFC', token_string)
    return "".join(BANGLA_TO_ENGLISH_NUMERALS.get(char, char) for char in normalized_string)

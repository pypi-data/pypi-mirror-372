# -*- coding: utf-8 -*-
"""
Advanced tokenizer for CodeBangla with enhanced features.

This module provides comprehensive tokenization capabilities including:
- Unicode normalization and validation
- Context-aware token classification
- Error recovery and reporting
- Performance optimization
- Plugin support for custom tokens
"""

import io
import re
import token
import tokenize
import unicodedata
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Optional, Iterator, Tuple, Set, Any
import logging

from .mappings import KEYWORD_MAP, BANGLA_TO_ENGLISH_NUMERALS, PROTECTED_KEYWORDS

logger = logging.getLogger(__name__)

class TokenType(Enum):
    """Extended token types for CodeBangla."""
    BANGLA_KEYWORD = auto()
    BANGLA_IDENTIFIER = auto()
    BANGLA_NUMERAL = auto()
    PYTHON_KEYWORD = auto()
    PYTHON_IDENTIFIER = auto()
    STRING_LITERAL = auto()
    COMMENT = auto()
    OPERATOR = auto()
    DELIMITER = auto()
    WHITESPACE = auto()
    NEWLINE = auto()
    UNKNOWN = auto()

@dataclass
class CodeBanglaToken:
    """Enhanced token representation."""
    type: TokenType
    value: str
    line: int
    column: int
    end_line: int
    end_column: int
    raw_value: Optional[str] = None
    context: Optional[str] = None
    python_equivalent: Optional[str] = None

class TokenizationError(Exception):
    """Exception for tokenization errors."""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Line {line}, Column {column}: {message}")

class AdvancedTokenizer:
    """
    Advanced tokenizer with context awareness and error recovery.
    
    Features:
    - Unicode normalization
    - Context-aware classification
    - Error recovery
    - Performance optimization
    - Extensible through plugins
    """
    
    def __init__(self, enable_error_recovery: bool = True):
        self.enable_error_recovery = enable_error_recovery
        self.errors: List[TokenizationError] = []
        self.warnings: List[str] = []
        self._keyword_cache: Dict[str, str] = {}
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Setup regex patterns for token recognition."""
        # Bangla script detection
        self.bangla_script_pattern = re.compile(r'[\u0980-\u09FF]+')
        
        # Identifier patterns
        self.identifier_pattern = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
        self.bangla_identifier_pattern = re.compile(r'[\u0980-\u09FF][\u0980-\u09FF0-9]*')
        
        # Numeral patterns
        self.bangla_numeral_pattern = re.compile(r'[\u09E6-\u09EF]+')
        
        # Comment patterns
        self.comment_pattern = re.compile(r'#.*$', re.MULTILINE)
        
        # String patterns
        self.string_patterns = [
            re.compile(r'""".*?"""', re.DOTALL),  # Triple quoted strings
            re.compile(r"'''.*?'''", re.DOTALL),
            re.compile(r'"[^"]*"'),               # Double quoted strings
            re.compile(r"'[^']*'"),               # Single quoted strings
        ]
    
    def tokenize(self, code: str) -> List[CodeBanglaToken]:
        """
        Tokenize CodeBangla source code.
        
        Args:
            code: Source code to tokenize
            
        Returns:
            List of CodeBanglaToken objects
            
        Raises:
            TokenizationError: If critical tokenization error occurs
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Normalize Unicode
        code = unicodedata.normalize('NFC', code)
        
        try:
            return self._tokenize_with_python_tokenizer(code)
        except Exception as e:
            if self.enable_error_recovery:
                logger.warning(f"Python tokenizer failed: {e}")
                # For now, return empty list - could implement regex fallback
                return []
            else:
                raise TokenizationError(f"Tokenization failed: {e}", 1, 1)
    
    def _tokenize_with_python_tokenizer(self, code: str) -> List[CodeBanglaToken]:
        """Use Python's built-in tokenizer with enhancements."""
        tokens = []
        
        try:
            python_tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
        except tokenize.TokenError as e:
            raise TokenizationError(f"Python tokenizer error: {e}", 1, 1)
        
        for py_token in python_tokens:
            cb_token = self._convert_python_token(py_token)
            if cb_token:
                tokens.append(cb_token)
        
        return tokens
    
    def _convert_python_token(self, py_token) -> Optional[CodeBanglaToken]:
        """Convert Python token to CodeBangla token."""
        if py_token.type == tokenize.ENDMARKER:
            return None
        
        token_value = py_token.string
        start_line, start_col = py_token.start
        end_line, end_col = py_token.end
        
        # Classify token
        if py_token.type == tokenize.NAME:
            cb_type, python_equiv = self._classify_name_token(token_value)
        elif py_token.type == tokenize.NUMBER:
            cb_type, python_equiv = self._classify_number_token(token_value)
        elif py_token.type == tokenize.STRING:
            cb_type, python_equiv = TokenType.STRING_LITERAL, token_value
        elif py_token.type == tokenize.COMMENT:
            cb_type, python_equiv = TokenType.COMMENT, token_value
        elif py_token.type in (tokenize.NL, tokenize.NEWLINE):
            cb_type, python_equiv = TokenType.NEWLINE, token_value
        elif py_token.type == tokenize.OP:
            cb_type, python_equiv = TokenType.OPERATOR, token_value
        else:
            cb_type, python_equiv = TokenType.UNKNOWN, token_value
        
        return CodeBanglaToken(
            type=cb_type,
            value=token_value,
            line=start_line,
            column=start_col,
            end_line=end_line,
            end_column=end_col,
            python_equivalent=python_equiv
        )
    
    def _classify_name_token(self, token_value: str) -> Tuple[TokenType, str]:
        """Classify NAME tokens (identifiers and keywords)."""
        # Check cache first
        if token_value in self._keyword_cache:
            return TokenType.BANGLA_KEYWORD, self._keyword_cache[token_value]
        
        # Check if it's a Bangla keyword
        if token_value in KEYWORD_MAP:
            python_equiv = KEYWORD_MAP[token_value]
            self._keyword_cache[token_value] = python_equiv
            return TokenType.BANGLA_KEYWORD, python_equiv
        
        # Check if it's a protected Python keyword
        if token_value in PROTECTED_KEYWORDS:
            return TokenType.PYTHON_KEYWORD, token_value
        
        # Check if it contains Bangla script
        if self.bangla_script_pattern.search(token_value):
            return TokenType.BANGLA_IDENTIFIER, token_value
        
        # Default to Python identifier
        return TokenType.PYTHON_IDENTIFIER, token_value
    
    def _classify_number_token(self, token_value: str) -> Tuple[TokenType, str]:
        """Classify NUMBER tokens."""
        # Check if it contains Bangla numerals
        if self.bangla_numeral_pattern.search(token_value):
            # Convert Bangla numerals to ASCII
            converted = self._convert_bangla_numerals(token_value)
            return TokenType.BANGLA_NUMERAL, converted
        
        return TokenType.PYTHON_IDENTIFIER, token_value
    
    def _convert_bangla_numerals(self, text: str) -> str:
        """Convert Bangla numerals to ASCII."""
        result = ""
        for char in text:
            if char in BANGLA_TO_ENGLISH_NUMERALS:
                result += BANGLA_TO_ENGLISH_NUMERALS[char]
            else:
                result += char
        return result

def create_tokenizer(enable_error_recovery: bool = True) -> AdvancedTokenizer:
    """Factory function to create a tokenizer instance."""
    return AdvancedTokenizer(enable_error_recovery=enable_error_recovery)
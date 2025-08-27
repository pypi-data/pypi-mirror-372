# -*- coding: utf-8 -*-
"""
CodeBangla: Advanced Python transpiler for Bangla keywords.

CodeBangla allows you to write Python code using Bangla keywords (in English transliteration),
making programming more accessible for Bengali speakers. This package provides a comprehensive
transpilation engine with support for modern Python features.

Key Features:
- Complete Python language support including async/await, type hints, and decorators
- Advanced error handling and debugging capabilities
- Performance optimization and caching
- Plugin architecture for extensibility
- Professional-grade tooling and documentation
- Unicode normalization and proper Bangla text handling

Example:
    >>> from codebangla import transpile
    >>> code = 'chhap("Hello, World!")'
    >>> python_code = transpile(code)
    >>> print(python_code)
    print("Hello, World!")

For advanced usage:
    >>> from codebangla.transpiler import AdvancedTranspiler, TranspilerConfig
    >>> config = TranspilerConfig(strict_mode=True, enable_type_checking=True)
    >>> transpiler = AdvancedTranspiler(config)
    >>> result = transpiler.transpile(code)
    >>> print(result.code if result.success else result.errors)

CLI Usage:
    $ codebangla run myprogram.bp
    $ codebangla compile myprogram.bp -o myprogram.py
    $ codebangla repl
"""

__version__ = "0.2.0"
__author__ = "CodeBangla Team"
__email__ = "team@codebangla.org"
__license__ = "MIT"
__copyright__ = "Copyright 2024 CodeBangla Team"

# Import main functionality for convenience
from .transpiler import transpile, AdvancedTranspiler, TranspilerConfig, TranspilationResult
from .mappings import KEYWORD_MAP, get_all_keywords, get_keyword_categories
from .utils import convert_bangla_numerals, validate_bangla_code
from .tokenizer import AdvancedTokenizer, TokenType, CodeBanglaToken

# Version info tuple for programmatic access
VERSION_INFO = tuple(int(x) for x in __version__.split('.'))

# Package metadata
__all__ = [
    # Version and metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
    "VERSION_INFO",
    
    # Core transpilation
    "transpile",
    "AdvancedTranspiler",
    "TranspilerConfig", 
    "TranspilationResult",
    
    # Mappings and keywords
    "KEYWORD_MAP",
    "get_all_keywords",
    "get_keyword_categories",
    
    # Utilities
    "convert_bangla_numerals",
    "validate_bangla_code",
    
    # Tokenization
    "AdvancedTokenizer",
    "TokenType",
    "CodeBanglaToken",
]

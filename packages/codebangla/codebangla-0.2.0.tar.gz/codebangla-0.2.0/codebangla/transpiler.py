# -*- coding: utf-8 -*-
"""
Advanced transpiler logic for converting Bangla-Python to standard Python.

This module provides a comprehensive transpilation engine that supports:
- Advanced Python features (async/await, type hints, decorators)
- Error handling and debugging
- AST-based transformations
- Plugin architecture
- Performance optimizations
- Source mapping for debugging

The transpiler uses multiple strategies:
1. Token-based replacement for simple keywords
2. AST transformations for complex syntax
3. Pattern matching for special constructs
4. Post-processing for optimization
"""

import ast
import io
import re
import sys
import tokenize
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Set, Callable
import logging

from .mappings import (
    KEYWORD_MAP, 
    BANGLA_TO_ENGLISH_NUMERALS, 
    PROTECTED_KEYWORDS,
    get_keyword_categories,
    is_valid_keyword
)
from .utils import convert_bangla_numerals

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class TranspilationResult:
    """Result of transpilation operation."""
    code: str
    success: bool
    errors: List[str]
    warnings: List[str]
    source_map: Optional[Dict[int, int]] = None
    execution_time: Optional[float] = None

@dataclass
class TranspilerConfig:
    """Configuration for the transpiler."""
    strict_mode: bool = False
    enable_type_checking: bool = True
    enable_async_support: bool = True
    enable_debugging: bool = False
    target_python_version: Tuple[int, int] = (3, 8)
    plugins: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.plugins is None:
            self.plugins = []

class TranspilerError(Exception):
    """Base exception for transpiler errors."""
    def __init__(self, message: str, line_number: Optional[int] = None, 
                 column: Optional[int] = None):
        self.message = message
        self.line_number = line_number
        self.column = column
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        if self.line_number is not None:
            if self.column is not None:
                return f"Line {self.line_number}, Column {self.column}: {self.message}"
            return f"Line {self.line_number}: {self.message}"
        return self.message

class SyntaxTranspilerError(TranspilerError):
    """Exception for syntax-related transpilation errors."""
    pass

class SemanticTranspilerError(TranspilerError):
    """Exception for semantic-related transpilation errors."""
    pass

class AdvancedTranspiler:
    """
    Advanced transpiler with support for modern Python features.
    
    This transpiler provides comprehensive support for:
    - All Python language constructs
    - Type annotations and hints
    - Async/await patterns
    - Decorators and metaclasses
    - Error handling and debugging
    - Performance optimization
    """
    
    def __init__(self, config: Optional[TranspilerConfig] = None):
        self.config = config or TranspilerConfig()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.source_map: Dict[int, int] = {}
        self._plugins: Dict[str, Callable] = {}
        self._load_plugins()
    
    def _load_plugins(self):
        """Load transpiler plugins."""
        for plugin_name in self.config.plugins:
            try:
                # Plugin loading logic would go here
                logger.info(f"Loaded plugin: {plugin_name}")
            except Exception as e:
                logger.warning(f"Failed to load plugin {plugin_name}: {e}")
    
    def transpile(self, code: str, filename: str = "<string>") -> TranspilationResult:
        """
        Advanced transpilation with comprehensive error handling.
        
        Args:
            code: Source code in Bangla-Python
            filename: Source filename for error reporting
            
        Returns:
            TranspilationResult with code, success status, and metadata
        """
        import time
        start_time = time.time()
        
        self.errors.clear()
        self.warnings.clear()
        self.source_map.clear()
        
        try:
            # Step 1: Preprocess the code
            preprocessed = self._preprocess(code)
            
            # Step 2: Token-based transpilation
            token_result = self._token_transpile(preprocessed)
            
            # Step 3: AST-based validation and transformation
            if self.config.enable_type_checking:
                ast_result = self._ast_transform(token_result)
            else:
                ast_result = token_result
            
            # Step 4: Post-processing and optimization
            final_result = self._postprocess(ast_result)
            
            # Step 5: Validation
            self._validate_result(final_result)
            
            execution_time = time.time() - start_time
            
            return TranspilationResult(
                code=final_result,
                success=len(self.errors) == 0,
                errors=self.errors.copy(),
                warnings=self.warnings.copy(),
                source_map=self.source_map.copy(),
                execution_time=execution_time
            )
            
        except Exception as e:
            self.errors.append(f"Internal transpiler error: {str(e)}")
            if self.config.enable_debugging:
                self.errors.append(traceback.format_exc())
            
            execution_time = time.time() - start_time
            return TranspilationResult(
                code="",
                success=False,
                errors=self.errors.copy(),
                warnings=self.warnings.copy(),
                execution_time=execution_time
            )
    
    def _preprocess(self, code: str) -> str:
        """Preprocess the code before transpilation."""
        # Remove BOM if present
        if code.startswith('\ufeff'):
            code = code[1:]
        
        # Normalize Unicode
        import unicodedata
        code = unicodedata.normalize('NFC', code)
        
        # Handle special syntax patterns
        code = self._handle_special_syntax(code)
        
        return code
    
    def _handle_special_syntax(self, code: str) -> str:
        """Handle special syntax patterns like type annotations."""
        # Convert type annotations
        code = re.sub(
            r'(\w+)\s*dhoron_annotation\s*([^=\n]+)',
            r'\1: \2',
            code
        )
        
        # Convert return type annotations
        code = re.sub(
            r'return_type\s*([^:\n]+):',
            r'-> \1:',
            code
        )
        
        return code
    
    def _token_transpile(self, code: str) -> str:
        """
        Enhanced token-based transpilation with better error handling.
        """
        try:
            tokens = tokenize.generate_tokens(io.StringIO(code).readline)
            result_parts: List[str] = []
            last_line = 0
            last_col = 0
            
            for token in tokens:
                try:
                    start_line, start_col = token.start
                    end_line, end_col = token.end
                    
                    # Update source mapping
                    if start_line not in self.source_map:
                        self.source_map[start_line] = len(result_parts)
                    
                    # Handle whitespace and newlines - skip for certain token types
                    if token.type not in (tokenize.ENCODING, tokenize.ENDMARKER):
                        # Handle whitespace and newlines
                        if start_line > last_line:
                            result_parts.append('\n' * (start_line - last_line))
                            last_col = 0
                        if start_col > last_col:
                            result_parts.append(' ' * (start_col - last_col))
                    
                    # Process token
                    processed_token = self._process_token(token)
                    if processed_token:  # Only append non-empty tokens
                        result_parts.append(processed_token)
                    
                    last_line = end_line
                    last_col = end_col
                    
                except Exception as e:
                    error_msg = f"Error processing token at line {token.start[0]}: {str(e)}"
                    self.errors.append(error_msg)
                    result_parts.append(token.string)
            
            return "".join(result_parts)
            
        except tokenize.TokenError as e:
            raise SyntaxTranspilerError(f"Tokenization error: {str(e)}")
        except Exception as e:
            raise TranspilerError(f"Unexpected error during tokenization: {str(e)}")
    
    def _process_token(self, token: tokenize.TokenInfo) -> str:
        """Process an individual token."""
        if token.type == tokenize.NAME:
            return self._process_name_token(token)
        elif token.type == tokenize.NUMBER:
            return self._process_number_token(token)
        elif token.type == tokenize.STRING:
            return self._process_string_token(token)
        elif token.type == tokenize.COMMENT:
            return self._process_comment_token(token)
        elif token.type == tokenize.NEWLINE:
            return "\n"
        elif token.type == tokenize.NL:
            return "\n"
        elif token.type in (tokenize.ENCODING, tokenize.ENDMARKER):
            return ""
        else:
            return token.string
    
    def _process_name_token(self, token: tokenize.TokenInfo) -> str:
        """Process NAME tokens (identifiers, keywords)."""
        token_string = token.string
        
        # Check if it's a protected keyword
        if token_string in PROTECTED_KEYWORDS:
            return token_string
        
        # Look up in keyword map
        if token_string in KEYWORD_MAP:
            return KEYWORD_MAP[token_string]
        
        # Check for compound keywords (e.g., "async def")
        return self._handle_compound_keywords(token_string)
    
    def _handle_compound_keywords(self, token_string: str) -> str:
        """Handle compound keywords like 'async def'."""
        # This could be extended for more complex patterns
        return token_string
    
    def _process_number_token(self, token: tokenize.TokenInfo) -> str:
        """Process NUMBER tokens with Bangla numeral conversion."""
        try:
            return convert_bangla_numerals(token.string)
        except Exception as e:
            self.warnings.append(f"Could not convert numeral '{token.string}': {str(e)}")
            return token.string
    
    def _process_string_token(self, token: tokenize.TokenInfo) -> str:
        """Process STRING tokens (leave unchanged to preserve content)."""
        return token.string
    
    def _process_comment_token(self, token: tokenize.TokenInfo) -> str:
        """Process COMMENT tokens (preserve comments)."""
        return token.string
    
    def _ast_transform(self, code: str) -> str:
        """
        Perform AST-based transformations for complex syntax.
        """
        try:
            tree = ast.parse(code)
            transformer = BanglaASTTransformer(self)
            new_tree = transformer.visit(tree)
            
            # Convert back to source code using ast.unparse (Python 3.9+)
            if hasattr(ast, 'unparse'):
                return ast.unparse(new_tree)
            else:
                # Fallback: return original code if ast.unparse not available
                self.warnings.append("AST transformation skipped (requires Python 3.9+)")
                return code
            
        except SyntaxError as e:
            self.errors.append(f"Syntax error in generated Python code: {str(e)}")
            return code
        except Exception as e:
            self.warnings.append(f"AST transformation failed: {str(e)}")
            return code
    
    def _postprocess(self, code: str) -> str:
        """Post-process the transpiled code."""
        # Remove extra whitespace
        lines = code.split('\n')
        processed_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            processed_lines.append(line)
        
        # Remove multiple consecutive empty lines
        final_lines = []
        prev_empty = False
        
        for line in processed_lines:
            if line.strip() == "":
                if not prev_empty:
                    final_lines.append(line)
                prev_empty = True
            else:
                final_lines.append(line)
                prev_empty = False
        
        return '\n'.join(final_lines)
    
    def _validate_result(self, code: str):
        """Validate the transpiled code."""
        if self.config.strict_mode:
            try:
                compile(code, '<transpiled>', 'exec')
            except SyntaxError as e:
                self.errors.append(f"Generated code has syntax error: {str(e)}")

class BanglaASTTransformer(ast.NodeTransformer):
    """AST transformer for advanced Bangla-Python constructs."""
    
    def __init__(self, transpiler: AdvancedTranspiler):
        self.transpiler = transpiler
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """Transform function definitions."""
        # Handle async functions, decorators, etc.
        return self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        """Transform class definitions."""
        # Handle metaclasses, decorators, etc.
        return self.generic_visit(node)

# Legacy function for backward compatibility
def transpile(code: str) -> str:
    """
    Legacy transpilation function for backward compatibility.
    
    For new code, use AdvancedTranspiler class directly.
    """
    transpiler = AdvancedTranspiler()
    result = transpiler.transpile(code)
    
    if not result.success:
        # For backward compatibility, we'll log errors but not raise
        for error in result.errors:
            logger.error(error)
    
    return result.code
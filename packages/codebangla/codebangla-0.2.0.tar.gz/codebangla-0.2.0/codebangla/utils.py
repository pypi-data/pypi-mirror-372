# -*- coding: utf-8 -*-
"""
Advanced utility functions for the CodeBangla package.

This module provides comprehensive utilities for:
- Numeral conversion and validation
- Text processing and normalization
- Error handling and debugging
- Performance profiling
- File operations
- Plugin management
"""

import os
import re
import sys
import time
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple, Iterator
import logging
from contextlib import contextmanager
from functools import wraps, lru_cache
import hashlib

from .mappings import BANGLA_TO_ENGLISH_NUMERALS, KEYWORD_MAP

# Configure logging
logger = logging.getLogger(__name__)

class CodeBanglaError(Exception):
    """Base exception for CodeBangla utilities."""
    pass

class NumeralConversionError(CodeBanglaError):
    """Exception for numeral conversion errors."""
    pass

class ValidationError(CodeBanglaError):
    """Exception for validation errors."""
    pass

def convert_bangla_numerals(token_string: str) -> str:
    """
    Enhanced conversion of Bangla numerals to ASCII numerals.

    This function handles potential Unicode normalization issues by converting
    the input string to NFC form before character-by-character replacement.
    It also provides better error handling and logging.

    Args:
        token_string: The input string, likely from the tokenizer.

    Returns:
        A new string with all Bangla numerals replaced by ASCII (0-9) equivalents.
        
    Raises:
        NumeralConversionError: If conversion fails for unexpected reasons.
    """
    try:
        # Normalize the input string to ensure consistent matching
        normalized_string = unicodedata.normalize('NFC', token_string)
        
        # Convert character by character
        result = "".join(
            BANGLA_TO_ENGLISH_NUMERALS.get(char, char) 
            for char in normalized_string
        )
        
        logger.debug(f"Converted numerals: '{token_string}' -> '{result}'")
        return result
        
    except Exception as e:
        raise NumeralConversionError(f"Failed to convert numerals in '{token_string}': {str(e)}")

@lru_cache(maxsize=1000)
def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode text for consistent processing.
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text in NFC form
    """
    return unicodedata.normalize('NFC', text)

def validate_bangla_code(code: str) -> List[str]:
    """
    Validate Bangla-Python code for common issues.
    
    Args:
        code: Source code to validate
        
    Returns:
        List of validation warnings/errors
    """
    issues = []
    lines = code.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Check for mixed scripts
        if has_mixed_scripts(line):
            issues.append(f"Line {line_num}: Mixed scripts detected")
        
        # Check for incomplete keywords
        incomplete = find_incomplete_keywords(line)
        if incomplete:
            issues.append(f"Line {line_num}: Possible incomplete keywords: {incomplete}")
    
    return issues

def has_mixed_scripts(text: str) -> bool:
    """
    Check if text contains mixed scripts (e.g., Bangla and Latin).
    
    Args:
        text: Text to check
        
    Returns:
        True if mixed scripts are detected
    """
    scripts = set()
    for char in text:
        if char.isalpha():
            script = unicodedata.name(char, '').split()[0] if unicodedata.name(char, '') else 'UNKNOWN'
            scripts.add(script)
    
    return len(scripts) > 1

def find_incomplete_keywords(line: str) -> List[str]:
    """
    Find potentially incomplete or misspelled keywords.
    
    Args:
        line: Line of code to check
        
    Returns:
        List of potentially incomplete keywords
    """
    incomplete = []
    words = re.findall(r'\b\w+\b', line)
    
    for word in words:
        if not word in KEYWORD_MAP and is_similar_to_keyword(word):
            incomplete.append(word)
    
    return incomplete

def is_similar_to_keyword(word: str, threshold: float = 0.8) -> bool:
    """
    Check if a word is similar to a known keyword.
    
    Args:
        word: Word to check
        threshold: Similarity threshold (0-1)
        
    Returns:
        True if word is similar to a known keyword
    """
    from difflib import SequenceMatcher
    
    for keyword in KEYWORD_MAP.keys():
        similarity = SequenceMatcher(None, word.lower(), keyword.lower()).ratio()
        if similarity >= threshold:
            return True
    
    return False

class PerformanceProfiler:
    """Simple performance profiler for transpilation operations."""
    
    def __init__(self):
        self.timings: Dict[str, List[float]] = {}
    
    @contextmanager
    def profile(self, operation: str):
        """Context manager for profiling operations."""
        start_time = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            if operation not in self.timings:
                self.timings[operation] = []
            self.timings[operation].append(elapsed)
    
    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics."""
        stats = {}
        for operation, times in self.timings.items():
            stats[operation] = {
                'total': sum(times),
                'average': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'count': len(times)
            }
        return stats
    
    def reset(self):
        """Reset all timings."""
        self.timings.clear()

def profile_performance(func):
    """Decorator for profiling function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.time() - start_time
            logger.debug(f"Function {func.__name__} took {elapsed:.4f} seconds")
    return wrapper

class FileManager:
    """Utility class for file operations."""
    
    @staticmethod
    def read_bangla_file(filepath: Union[str, Path], encoding: str = 'utf-8') -> str:
        """
        Read a Bangla-Python file with proper encoding handling.
        
        Args:
            filepath: Path to the file
            encoding: File encoding (default: utf-8)
            
        Returns:
            File contents as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If encoding is incorrect
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Normalize Unicode
            return normalize_unicode(content)
            
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding, e.object, e.start, e.end,
                f"Failed to decode file {filepath}: {e.reason}"
            )
    
    @staticmethod
    def write_python_file(filepath: Union[str, Path], content: str, 
                         encoding: str = 'utf-8') -> None:
        """
        Write transpiled Python code to a file.
        
        Args:
            filepath: Output file path
            content: Python code content
            encoding: File encoding (default: utf-8)
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
    
    @staticmethod
    def backup_file(filepath: Union[str, Path]) -> Path:
        """
        Create a backup of a file.
        
        Args:
            filepath: Path to the file to backup
            
        Returns:
            Path to the backup file
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {filepath}")
        
        # Create backup with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = path.with_suffix(f'.{timestamp}{path.suffix}.bak')
        
        import shutil
        shutil.copy2(path, backup_path)
        return backup_path

def calculate_file_hash(filepath: Union[str, Path], algorithm: str = 'sha256') -> str:
    """
    Calculate hash of a file for integrity checking.
    
    Args:
        filepath: Path to the file
        algorithm: Hash algorithm to use
        
    Returns:
        Hexadecimal hash string
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    hash_obj = hashlib.new(algorithm)
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()

def get_file_info(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Get comprehensive information about a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Dictionary with file information
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    stat = path.stat()
    return {
        'path': str(path.absolute()),
        'name': path.name,
        'size': stat.st_size,
        'modified': stat.st_mtime,
        'created': stat.st_ctime,
        'extension': path.suffix,
        'is_bangla_file': path.suffix == '.bp',
        'hash': calculate_file_hash(path),
        'encoding': detect_file_encoding(path)
    }

def detect_file_encoding(filepath: Union[str, Path]) -> str:
    """
    Detect the encoding of a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Detected encoding name
    """
    try:
        import chardet
        
        with open(filepath, 'rb') as f:
            raw_data = f.read()
        
        result = chardet.detect(raw_data)
        return result['encoding'] or 'utf-8'
        
    except ImportError:
        # chardet not available, assume utf-8
        return 'utf-8'

class MemoryCache:
    """Simple in-memory cache for transpilation results."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def _evict_oldest(self) -> None:
        """Evict the oldest accessed item."""
        if self.access_times:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self.access_times.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)

# Global cache instance
_global_cache = MemoryCache()

def get_cache() -> MemoryCache:
    """Get the global cache instance."""
    return _global_cache

@contextmanager
def temporary_directory():
    """Context manager for creating temporary directories."""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    try:
        yield Path(temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def format_code(code: str, style: str = 'pep8') -> str:
    """
    Format Python code according to style guidelines.
    
    Args:
        code: Python code to format
        style: Code style ('pep8', 'black', etc.)
        
    Returns:
        Formatted code
    """
    try:
        if style == 'black':
            import black
            return black.format_str(code, mode=black.FileMode())
        else:
            # Basic formatting for PEP 8
            return _basic_format(code)
    except ImportError:
        logger.warning(f"Formatter '{style}' not available, using basic formatting")
        return _basic_format(code)

def _basic_format(code: str) -> str:
    """Basic code formatting."""
    lines = code.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Remove trailing whitespace
        line = line.rstrip()
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def create_source_map(original_lines: List[str], 
                     transpiled_lines: List[str]) -> Dict[int, int]:
    """
    Create a source map between original and transpiled code.
    
    Args:
        original_lines: Lines from original Bangla code
        transpiled_lines: Lines from transpiled Python code
        
    Returns:
        Dictionary mapping original line numbers to transpiled line numbers
    """
    source_map = {}
    
    # Simple 1:1 mapping for now
    for i, _ in enumerate(original_lines):
        if i < len(transpiled_lines):
            source_map[i + 1] = i + 1
    
    return source_map

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeBangla command-line interface entry point.

This module allows CodeBangla to be executed as a module:
    python -m codebangla

It provides access to all CLI functionality including transpilation,
REPL, project management, and validation tools.
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())

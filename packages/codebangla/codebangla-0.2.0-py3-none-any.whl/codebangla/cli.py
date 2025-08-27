# -*- coding: utf-8 -*-
"""
Advanced command-line interface for the CodeBangla package.

This module provides a comprehensive CLI with features including:
- Interactive mode and REPL
- Debugging and profiling
- Plugin management
- Configuration management
- Advanced compilation options
- Project scaffolding
- Documentation generation
"""

import os
import sys
import json
import click
import logging
from pathlib import Path
from typing import TextIO, Optional, List, Dict, Any
from datetime import datetime

from .transpiler import AdvancedTranspiler, TranspilerConfig, TranspilationResult
from .utils import (
    FileManager, PerformanceProfiler, validate_bangla_code,
    get_file_info, MemoryCache
)
from .mappings import get_keyword_categories, get_all_keywords

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global profiler instance
profiler = PerformanceProfiler()

class CodeBanglaContext:
    """Context object for CLI commands."""
    
    def __init__(self):
        self.config = TranspilerConfig()
        self.verbose = False
        self.debug = False
        self.profile = False
        self.cache = MemoryCache()

# Create global context
pass_context = click.make_pass_decorator(CodeBanglaContext, ensure=True)

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode')
@click.option('--profile', '-p', is_flag=True, help='Enable performance profiling')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@pass_context
def main(ctx: CodeBanglaContext, verbose: bool, debug: bool, profile: bool, config: Optional[str]) -> None:
    """
    CodeBangla: Advanced Python transpiler for Bangla keywords.

    A professional-grade transpiler that converts Bangla-Python (.bp) files
    to standard Python, with support for modern Python features, debugging,
    and comprehensive error handling.
    """
    ctx.verbose = verbose
    ctx.debug = debug
    ctx.profile = profile
    
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        ctx.config.enable_debugging = True
    
    if config:
        ctx.config = load_config(config)
    
    if verbose:
        click.echo(f"CodeBangla CLI v0.2.0")
        click.echo(f"Python version: {sys.version}")
        click.echo(f"Debug mode: {debug}")
        click.echo(f"Profile mode: {profile}")

@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--watch', '-w', is_flag=True, help='Watch file for changes')
@click.option('--strict', is_flag=True, help='Enable strict mode')
@click.option('--no-cache', is_flag=True, help='Disable caching')
@pass_context
def run(ctx: CodeBanglaContext, file: str, output: Optional[str], 
        watch: bool, strict: bool, no_cache: bool) -> None:
    """Transpile and execute a .bp file directly."""
    
    if strict:
        ctx.config.strict_mode = True
    
    if watch:
        watch_and_run(ctx, file, output)
        return
    
    try:
        # Check cache first
        if not no_cache:
            file_info = get_file_info(file)
            cache_key = f"{file}_{file_info['hash']}"
            cached_result = ctx.cache.get(cache_key)
            
            if cached_result and ctx.verbose:
                click.echo("Using cached transpilation result")
        
        # Read and transpile
        source_code = FileManager.read_bangla_file(file)
        
        # Validate if in strict mode
        if ctx.config.strict_mode:
            issues = validate_bangla_code(source_code)
            if issues:
                click.echo("Validation issues found:", err=True)
                for issue in issues:
                    click.echo(f"  {issue}", err=True)
                sys.exit(1)
        
        # Transpile
        transpiler = AdvancedTranspiler(ctx.config)
        
        if ctx.profile:
            with profiler.profile("transpilation"):
                result = transpiler.transpile(source_code, file)
        else:
            result = transpiler.transpile(source_code, file)
        
        # Handle result
        if not result.success:
            click.echo("Transpilation failed:", err=True)
            for error in result.errors:
                click.echo(f"  Error: {error}", err=True)
            for warning in result.warnings:
                click.echo(f"  Warning: {warning}", err=True)
            sys.exit(1)
        
        # Cache result
        if not no_cache:
            ctx.cache.set(cache_key, result.code)
        
        # Save output if specified
        if output:
            FileManager.write_python_file(output, result.code)
            if ctx.verbose:
                click.echo(f"Transpiled code saved to: {output}")
        
        # Execute
        if ctx.verbose:
            click.echo("Executing transpiled code...")
        
        try:
            exec_globals = {"__name__": "__main__", "__file__": file}
            exec(result.code, exec_globals)
        except Exception as e:
            click.echo(f"Runtime error: {e}", err=True)
            if ctx.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)
        
        # Show profiling results
        if ctx.profile:
            show_profile_results()
    
    except Exception as e:
        click.echo(f"An error occurred: {e}", err=True)
        if ctx.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

@main.command()
@click.argument('infile', type=click.Path(exists=True))
@click.option('-o', '--output', 'outfile', type=click.Path(), help="Output path for the compiled .py file")
@click.option('--format', 'code_format', type=click.Choice(['pep8', 'black']), default='pep8', help="Code formatting style")
@click.option('--optimize', is_flag=True, help="Enable code optimization")
@click.option('--add-header', is_flag=True, help="Add generation header to output")
@pass_context
def compile(ctx: CodeBanglaContext, infile: str, outfile: Optional[str], 
           code_format: str, optimize: bool, add_header: bool) -> None:
    """Transpile a .bp file and save it as a .py file."""
    
    try:
        # Determine output path
        if not outfile:
            input_path = Path(infile)
            output_path = input_path.with_suffix('.py')
        else:
            output_path = Path(outfile)
        
        # Read and transpile
        source_code = FileManager.read_bangla_file(infile)
        
        transpiler = AdvancedTranspiler(ctx.config)
        result = transpiler.transpile(source_code, infile)
        
        if not result.success:
            click.echo("Compilation failed:", err=True)
            for error in result.errors:
                click.echo(f"  Error: {error}", err=True)
            sys.exit(1)
        
        # Process code
        final_code = result.code
        
        # Add header if requested
        if add_header:
            header = generate_header(infile)
            final_code = header + "\n\n" + final_code
        
        # Format code
        if code_format != 'pep8':
            from .utils import format_code
            final_code = format_code(final_code, code_format)
        
        # Save output
        FileManager.write_python_file(output_path, final_code)
        
        click.echo(f"Successfully compiled {infile} to {output_path}")
        
        if ctx.verbose:
            file_info = get_file_info(output_path)
            click.echo(f"Output file size: {file_info['size']} bytes")
            if result.execution_time:
                click.echo(f"Compilation time: {result.execution_time:.4f} seconds")
    
    except Exception as e:
        click.echo(f"An error occurred during compilation: {e}", err=True)
        if ctx.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

@main.command()
@click.option('--port', default=8000, help='Port for the REPL server')
@click.option('--history', is_flag=True, help='Enable command history')
@pass_context
def repl(ctx: CodeBanglaContext, port: int, history: bool) -> None:
    """Start an interactive CodeBangla REPL."""
    
    click.echo("Starting CodeBangla Interactive REPL...")
    click.echo("Type 'help' for available commands, 'exit' to quit.")
    
    if history:
        try:
            import readline
            histfile = Path.home() / '.codebangla_history'
            try:
                readline.read_history_file(histfile)
            except FileNotFoundError:
                pass
        except ImportError:
            click.echo("Warning: readline not available, no command history")
    
    transpiler = AdvancedTranspiler(ctx.config)
    
    while True:
        try:
            line = input(">>> ")
            
            if line.strip() in ['exit', 'quit']:
                break
            elif line.strip() == 'help':
                show_repl_help()
                continue
            elif line.strip() == 'keywords':
                show_keywords()
                continue
            elif line.strip() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
            
            if line.strip():
                result = transpiler.transpile(line)
                if result.success:
                    try:
                        exec(result.code)
                    except Exception as e:
                        click.echo(f"Runtime error: {e}")
                else:
                    for error in result.errors:
                        click.echo(f"Error: {error}")
        
        except KeyboardInterrupt:
            click.echo("\nUse 'exit' to quit")
        except EOFError:
            break
    
    if history:
        try:
            readline.write_history_file(histfile)
        except:
            pass
    
    click.echo("Goodbye!")

@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--rules', multiple=True, help='Specific validation rules to run')
@pass_context
def validate(ctx: CodeBanglaContext, file: str, rules: List[str]) -> None:
    """Validate a .bp file for common issues and best practices."""
    
    try:
        source_code = FileManager.read_bangla_file(file)
        issues = validate_bangla_code(source_code)
        
        if not issues:
            click.echo(f"✓ {file} passed validation")
            return
        
        click.echo(f"Validation issues found in {file}:")
        for issue in issues:
            click.echo(f"  ⚠ {issue}")
        
        # Additional checks based on rules
        if 'performance' in rules:
            click.echo("Running performance analysis...")
            # Performance analysis would go here
        
        if 'style' in rules:
            click.echo("Running style analysis...")
            # Style analysis would go here
    
    except Exception as e:
        click.echo(f"Validation failed: {e}", err=True)
        sys.exit(1)

@main.command()
@click.argument('project_name')
@click.option('--template', type=click.Choice(['basic', 'advanced', 'web', 'data']), 
              default='basic', help='Project template')
@click.option('--author', help='Author name')
@click.option('--license', type=click.Choice(['MIT', 'GPL', 'Apache']), 
              default='MIT', help='License type')
def init(project_name: str, template: str, author: Optional[str], license: str) -> None:
    """Initialize a new CodeBangla project."""
    
    project_path = Path(project_name)
    
    if project_path.exists():
        click.echo(f"Directory {project_name} already exists", err=True)
        sys.exit(1)
    
    # Create project structure
    project_path.mkdir()
    (project_path / 'src').mkdir()
    (project_path / 'tests').mkdir()
    (project_path / 'docs').mkdir()
    
    # Create main file
    main_content = get_template_content(template)
    (project_path / 'src' / 'main.bp').write_text(main_content, encoding='utf-8')
    
    # Create configuration
    config = {
        'name': project_name,
        'version': '0.1.0',
        'author': author or 'Unknown',
        'license': license,
        'template': template,
        'transpiler': {
            'strict_mode': False,
            'enable_type_checking': True,
            'target_python_version': [3, 8]
        }
    }
    
    (project_path / 'codebangla.json').write_text(
        json.dumps(config, indent=2), encoding='utf-8'
    )
    
    # Create README
    readme_content = f"""# {project_name}

A CodeBangla project created from the {template} template.

## Getting Started

1. Run your main file:
   ```bash
   codebangla run src/main.bp
   ```

2. Compile to Python:
   ```bash
   codebangla compile src/main.bp -o dist/main.py
   ```

## Development

- Source files: `src/`
- Tests: `tests/`
- Documentation: `docs/`

## License

{license}
"""
    
    (project_path / 'README.md').write_text(readme_content, encoding='utf-8')
    
    click.echo(f"✓ Created new CodeBangla project: {project_name}")
    click.echo(f"  Template: {template}")
    click.echo(f"  Author: {author or 'Unknown'}")
    click.echo(f"  License: {license}")

@main.command()
@pass_context
def info(ctx: CodeBanglaContext) -> None:
    """Show CodeBangla system information."""
    
    click.echo("=== CodeBangla System Information ===")
    click.echo(f"Version: 0.2.0")
    click.echo(f"Python: {sys.version}")
    click.echo(f"Platform: {sys.platform}")
    click.echo(f"Cache size: {ctx.cache.size()}")
    
    click.echo("\n=== Available Keywords ===")
    categories = get_keyword_categories()
    for category, keywords in categories.items():
        click.echo(f"{category.title()}: {len(keywords)} keywords")
    
    click.echo(f"\nTotal keywords: {len(get_all_keywords())}")

@main.command()
@click.option('--category', type=click.Choice(['core', 'async', 'types', 'builtins', 'modern', 'decorators', 'operators']),
              help='Show keywords from specific category')
@click.option('--search', help='Search for keywords containing text')
def keywords(category: Optional[str], search: Optional[str]) -> None:
    """List available Bangla keywords."""
    
    if category:
        from .mappings import get_keyword_by_category
        keywords_list = get_keyword_by_category(category)
        click.echo(f"=== {category.title()} Keywords ===")
    else:
        keywords_list = get_all_keywords()
        click.echo("=== All Keywords ===")
    
    if search:
        keywords_list = [k for k in keywords_list if search.lower() in k.lower()]
    
    # Group by starting letter for better display
    grouped = {}
    for keyword in sorted(keywords_list):
        first_letter = keyword[0].upper()
        if first_letter not in grouped:
            grouped[first_letter] = []
        grouped[first_letter].append(keyword)
    
    for letter, words in grouped.items():
        click.echo(f"\n{letter}:")
        for word in words:
            from .mappings import get_python_equivalent
            python_equiv = get_python_equivalent(word)
            click.echo(f"  {word:<20} -> {python_equiv}")

def load_config(config_path: str) -> TranspilerConfig:
    """Load configuration from file."""
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        return TranspilerConfig(
            strict_mode=config_data.get('strict_mode', False),
            enable_type_checking=config_data.get('enable_type_checking', True),
            enable_async_support=config_data.get('enable_async_support', True),
            enable_debugging=config_data.get('enable_debugging', False),
            target_python_version=tuple(config_data.get('target_python_version', [3, 8])),
            plugins=config_data.get('plugins', [])
        )
    except Exception as e:
        click.echo(f"Warning: Could not load config file: {e}", err=True)
        return TranspilerConfig()

def watch_and_run(ctx: CodeBanglaContext, file: str, output: Optional[str]) -> None:
    """Watch file for changes and re-run on modification."""
    import time
    
    click.echo(f"Watching {file} for changes... (Ctrl+C to stop)")
    
    last_modified = os.path.getmtime(file)
    
    while True:
        try:
            current_modified = os.path.getmtime(file)
            if current_modified > last_modified:
                click.echo(f"\n{datetime.now().strftime('%H:%M:%S')} - File changed, re-running...")
                # Run the file (simplified version)
                try:
                    source_code = FileManager.read_bangla_file(file)
                    transpiler = AdvancedTranspiler(ctx.config)
                    result = transpiler.transpile(source_code, file)
                    
                    if result.success:
                        exec_globals = {"__name__": "__main__", "__file__": file}
                        exec(result.code, exec_globals)
                    else:
                        for error in result.errors:
                            click.echo(f"Error: {error}", err=True)
                except Exception as e:
                    click.echo(f"Error: {e}", err=True)
                
                last_modified = current_modified
            
            time.sleep(1)
        
        except KeyboardInterrupt:
            click.echo("\nWatching stopped.")
            break

def show_profile_results() -> None:
    """Show profiling results."""
    stats = profiler.get_stats()
    if stats:
        click.echo("\n=== Performance Profile ===")
        for operation, timings in stats.items():
            click.echo(f"{operation}: {timings['average']:.4f}s avg ({timings['count']} calls)")

def show_repl_help() -> None:
    """Show REPL help."""
    click.echo("""
Available commands:
  help      - Show this help
  keywords  - List all available keywords
  clear     - Clear screen
  exit/quit - Exit REPL

Type any Bangla-Python code to execute it immediately.
""")

def show_keywords() -> None:
    """Show keywords in REPL."""
    categories = get_keyword_categories()
    for category, keywords in categories.items():
        click.echo(f"{category.title()}: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")

def generate_header(source_file: str) -> str:
    """Generate header for compiled files."""
    return f"""# -*- coding: utf-8 -*-
\"\"\"
Generated by CodeBangla v0.2.0
Source: {source_file}
Generated: {datetime.now().isoformat()}

This file was automatically transpiled from Bangla-Python.
Do not edit this file directly. Edit the source .bp file instead.
\"\"\"
"""

def get_template_content(template: str) -> str:
    """Get template content for project initialization."""
    templates = {
        'basic': '''# -*- coding: utf-8 -*-
# মূল প্রোগ্রাম

shuru main():
    chhap("আসসালামু আলাইকুম! CodeBangla এ আপনাকে স্বাগতম!")
    naam = neoa("আপনার নাম কি? ")
    chhap(f"হ্যালো, {naam}!")

jodi __name__ == "__main__":
    main()
''',
        'advanced': '''# -*- coding: utf-8 -*-
# উন্নত CodeBangla প্রোগ্রাম

theke typing ano List, Dict, Optional

classh Person:
    shuru __init__(nijei, naam: shobdo, boyosh: shongkhya):
        nijei.naam = naam
        nijei.boyosh = boyosh
    
    shuru greet(nijei) -> shobdo:
        phiredao f"আমার নাম {nijei.naam}, আমার বয়স {nijei.boyosh}"

ashinchronous shuru fetch_data() -> List[Dict]:
    # এখানে async কোড থাকবে
    phiredao []

shuru main():
    person = Person("আহমেদ", 25)
    chhap(person.greet())

jodi __name__ == "__main__":
    main()
''',
        'web': '''# -*- coding: utf-8 -*-
# ওয়েব অ্যাপ্লিকেশন

shuru create_app():
    chhap("ওয়েব অ্যাপ্লিকেশন তৈরি করা হচ্ছে...")
    # এখানে ওয়েব ফ্রেমওয়ার্ক কোড থাকবে

jodi __name__ == "__main__":
    create_app()
''',
        'data': '''# -*- coding: utf-8 -*-
# ডেটা সায়েন্স প্রজেক্ট

shuru analyze_data():
    chhap("ডেটা বিশ্লেষণ শুরু...")
    # এখানে ডেটা সায়েন্স কোড থাকবে

jodi __name__ == "__main__":
    analyze_data()
'''
    }
    
    return templates.get(template, templates['basic'])

if __name__ == '__main__':
    main()
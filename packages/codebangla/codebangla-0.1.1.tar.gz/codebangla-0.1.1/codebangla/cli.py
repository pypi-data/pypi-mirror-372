# -*- coding: utf-8 -*-
"""Command-line interface for the CodeBangla package."""

import sys
import click
from typing import TextIO

from .transpiler import transpile

@click.group()
def main() -> None:
    """CodeBangla: A Python transpiler for Bangla keywords.

    This CLI allows you to run or compile .bp files.
    """
    pass

@main.command()
@click.argument('file', type=click.File('r', encoding='utf-8'))
def run(file: TextIO) -> None:
    """Transpile and execute a .bp file directly."""
    source_code = file.read()
    try:
        python_code = transpile(source_code)
        # Using a dedicated globals dict for exec is safer
        exec_globals = {"__name__": "__main__"}
        exec(python_code, exec_globals)
    except Exception as e:
        click.echo(f"An error occurred during transpilation or execution: {e}", err=True)
        sys.exit(1)

@main.command()
@click.argument('infile', type=click.File('r', encoding='utf-8'))
@click.option(
    '-o', '--output', 'outfile',
    type=click.File('w', encoding='utf-8'),
    help="Output path for the compiled .py file."
)
def compile(infile: TextIO, outfile: TextIO) -> None:
    """Transpile a .bp file and save it as a .py file."""
    if not outfile:
        # If no output file is specified, create one based on the input filename
        output_path = infile.name.replace('.bp', '.py')
        if output_path == infile.name:
            output_path += ".py"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                _compile_file(infile, f)
            click.echo(f"Successfully compiled {infile.name} to {output_path}")
        except IOError as e:
            click.echo(f"Error writing to file: {e}", err=True)
            sys.exit(1)
    else:
        _compile_file(infile, outfile)
        click.echo(f"Successfully compiled {infile.name} to {outfile.name}")

def _compile_file(infile: TextIO, outfile: TextIO) -> None:
    """Helper function to handle the core compilation logic."""
    source_code = infile.read()
    try:
        python_code = transpile(source_code)
        outfile.write(python_code)
    except Exception as e:
        click.echo(f"An error occurred during transpilation: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
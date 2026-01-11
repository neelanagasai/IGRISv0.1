"""
IGRIS Output Formatting

Handles syntax highlighting for code blocks and rich terminal output.
"""

import re
import sys
from typing import Optional

try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

# Regex to detect code blocks
CODE_BLOCK_PATTERN = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)
INLINE_CODE_PATTERN = re.compile(r'`([^`]+)`')


def detect_language(code: str, hint: Optional[str] = None) -> str:
    """Detect programming language from code content."""
    if hint:
        return hint.lower()
    
    # Simple heuristics
    if 'def ' in code or 'import ' in code or 'print(' in code:
        return 'python'
    elif 'function ' in code or 'const ' in code or 'let ' in code:
        return 'javascript'
    elif '#include' in code or 'int main' in code:
        return 'cpp'
    elif 'fn ' in code or 'let mut' in code:
        return 'rust'
    elif '#!/bin/bash' in code or 'echo ' in code:
        return 'bash'
    elif 'SELECT ' in code.upper() or 'FROM ' in code.upper():
        return 'sql'
    else:
        return 'text'


def format_code_block(code: str, language: str = 'python') -> None:
    """Print a syntax-highlighted code block."""
    if RICH_AVAILABLE and console:
        syntax = Syntax(code.strip(), language, theme="monokai", line_numbers=False)
        console.print(syntax)
    else:
        print(code)


def format_output(text: str) -> None:
    """
    Format and print output with syntax highlighting for code blocks.
    """
    if not RICH_AVAILABLE or not console:
        print(text)
        return
    
    # Find all code blocks
    last_end = 0
    for match in CODE_BLOCK_PATTERN.finditer(text):
        # Print text before code block
        before = text[last_end:match.start()]
        if before.strip():
            console.print(before.strip())
        
        # Print highlighted code block
        lang = match.group(1) or 'python'
        code = match.group(2)
        format_code_block(code, lang)
        
        last_end = match.end()
    
    # Print remaining text
    remaining = text[last_end:]
    if remaining.strip():
        console.print(remaining.strip())


def print_streaming(token: str) -> None:
    """Print a token for streaming output (no newline)."""
    sys.stdout.write(token)
    sys.stdout.flush()


def print_status(message: str, style: str = "bold blue") -> None:
    """Print a status message."""
    if RICH_AVAILABLE and console:
        console.print(f"[{style}]{message}[/{style}]")
    else:
        print(message)


def print_error(message: str) -> None:
    """Print an error message."""
    if RICH_AVAILABLE and console:
        console.print(f"[bold red]{message}[/bold red]")
    else:
        print(f"ERROR: {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    if RICH_AVAILABLE and console:
        console.print(f"[bold green]{message}[/bold green]")
    else:
        print(message)


def print_latency(model: str, latency_ms: float) -> None:
    """Print latency info."""
    if RICH_AVAILABLE and console:
        console.print(f"[dim][{model.upper()}] {latency_ms}ms[/dim]")
    else:
        print(f"[{model.upper()}] {latency_ms}ms")

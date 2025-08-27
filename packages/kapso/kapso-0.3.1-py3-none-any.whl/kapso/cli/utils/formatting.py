"""
Formatting utilities for the Kapso CLI.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]{message}[/green]")

def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]Error: {message}[/red]")

def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]Warning: {message}[/yellow]")

def print_info(message: str) -> None:
    """Print an info message."""
    console.print(message)

def print_header(title: str) -> None:
    """Print a header."""
    console.print(f"\n[bold]{title}[/bold]")
    console.print("─" * 50)

def print_panel(title: str, content: str) -> None:
    """Print a panel with a title and content."""
    console.print(Panel(content, title=title))

def print_table(title: str, headers: list, rows: list) -> None:
    """Print a table with a title, headers, and rows."""
    table = Table(title=title)
    
    for header in headers:
        table.add_column(header)
    
    for row in rows:
        table.add_row(*row)
    
    console.print(table)

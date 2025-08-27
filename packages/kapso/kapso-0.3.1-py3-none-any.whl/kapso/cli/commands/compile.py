"""
Implementation of the compile command for the Kapso CLI.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress

from kapso.cli.utils.agent import compile_agent

app = typer.Typer(name="compile", help="Compile an agent from Python code to YAML.")
console = Console()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    agent_file: Optional[str] = typer.Argument(
        None,
        help="Path to the Python file defining the agent (defaults to agent.py)"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (defaults to agent.yaml in the current directory)"
    ),
    silent: bool = typer.Option(
        False,
        "--silent",
        help="Suppress output messages (used when called from other commands)",
        hidden=True
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output with detailed error messages"
    ),
):
    """
    Compile an agent from Python code to YAML.
    
    This command imports the agent definition from a Python file, validates it,
    and serializes it to YAML for deployment.
    
    ⚠️  DEPRECATED: Use 'kapso agent push <name>' instead.
    
    Examples:
    
        kapso compile
        
        kapso compile ./agents/booking-agent.py
        
        kapso compile ./agents/booking-agent.py --output custom-name.yaml
    """
    # If subcommand was invoked, we skip this
    if ctx.invoked_subcommand is not None:
        return
    
    # Show deprecation warning
    if not silent:
        console.print("[yellow]⚠️  DEPRECATED: 'kapso compile' is deprecated.[/yellow]")
        console.print("[yellow]   Use 'kapso agent push <name>' instead for the new workflow.[/yellow]")
        console.print()
    
    # Use local verbose flag directly (can be overridden by common options if needed)
    if ctx.obj and hasattr(ctx.obj, 'verbose') and ctx.obj.verbose:
        verbose = True
    
    if verbose and not silent:
        console.print("Verbose mode enabled")
    
    # Default to agent.py if no file is specified
    input_file = agent_file or "agent.py"
    
    # Check if file exists
    if not Path(input_file).exists():
        if not silent:
            console.print(f"[red]Error: File not found: {input_file}[/red]")
        sys.exit(1)
    
    # Start compilation process
    if not silent:
        console.print(f"Loading agent from {input_file}...")
        
        with Progress() as progress:
            task = progress.add_task("Compiling agent...", total=1)
            
            # Use the compile_agent utility function
            output_path = compile_agent(
                agent_file=input_file,
                output_file=output,
                verbose=verbose
            )
            
            if not output_path:
                progress.stop()
                console.print("[red]Error: Failed to compile agent.[/red]")
                if not verbose:
                    console.print("[yellow]Run with --verbose flag for detailed error information.[/yellow]")
                sys.exit(1)
                
            progress.update(task, advance=1)
        
        # Get agent name from output file
        try:
            import yaml
            with open(output_path, "r") as f:
                agent_data = yaml.safe_load(f)
                agent_name = agent_data.get("name", "Unnamed Agent")
        except Exception:
            agent_name = "Agent"
            
        console.print(f"[green]Agent '{agent_name}' compiled successfully to {output_path}[/green]")
        
        # Suggest next steps
        console.print("\nTo deploy this agent:")
        console.print("  kapso deploy")
    else:
        # Silent mode - just compile without output
        output_path = compile_agent(
            agent_file=input_file,
            output_file=output,
            verbose=verbose
        )
        
        if not output_path:
            sys.exit(1)
    
    return output_path 
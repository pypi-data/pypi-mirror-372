"""
Implementation of the test command for the Kapso CLI.
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
# Runner imports removed - cloud-only execution
import typer
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.panel import Panel
from rich.markdown import Markdown

from kapso.cli.utils.agent import compile_agent, load_agent_graph
from kapso.cli.utils.formatting import print_error, print_warning, print_info, print_header, print_table, console


# Configure logger
logger = logging.getLogger('kapso.cli.commands.test')

class UIHelper:
    """Helper class for UI-related functions"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.active_progress = None
        self.active_task_id = None

    def start_spinner(self, text: str) -> Tuple[Progress, Any]:
        """
        Start a spinner with text.

        Args:
            text: Text to display with spinner

        Returns:
            Tuple of (Progress object, task_id) that can be used to update the spinner
        """
        # Make sure any existing spinner is stopped first
        self.stop_spinner()

        # Create a new progress display
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold]{task.description}"),
            console=self.console,
            transient=True
        )
        task_id = progress.add_task(description=text, total=None)
        progress.start()

        # Store references to the active progress display
        self.active_progress = progress
        self.active_task_id = task_id

        return progress, task_id

    def stop_spinner(self) -> None:
        """Stop any active spinner"""
        if self.active_progress:
            try:
                self.active_progress.stop()
            except Exception:
                # Ignore errors when stopping (might already be stopped)
                pass
            self.active_progress = None
            self.active_task_id = None

ui = UIHelper(console)

def compile_agent_if_needed(verbose: bool) -> None:
    """
    Compile agent.py to update agent.yaml if needed.

    Args:
        verbose: Whether to show verbose output
    """
    spinner, spinner_task = ui.start_spinner("Compiling agent to update agent.yaml...")

    try:
        # Use the compile_agent utility function directly
        agent_path = compile_agent(
            agent_file="agent.py",
            output_file=None,
            verbose=verbose
        )

        if agent_path:
            spinner.update(spinner_task, description="Compile successful, proceeding with tests...")
        else:
            spinner.update(spinner_task, description="Compile failed, continuing with existing agent.yaml...")
    except Exception as e:
        # Just log a warning and continue if compile fails
        print_warning(f"Failed to compile agent: {str(e)}")
        spinner.update(spinner_task, description="Continuing with existing agent.yaml...")
    finally:
        ui.stop_spinner()

def load_test_case_from_yaml(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load a test case from a YAML file.

    Args:
        file_path: Path to the YAML file containing the test case

    Returns:
        The loaded test case as a dictionary, or None if not found
    """
    try:
        with open(file_path, 'r') as f:
            test_case = yaml.safe_load(f)
        
        # Validate required fields
        if not test_case:
            print_warning(f"Empty test file: {file_path}")
            return None
            
        if not test_case.get('name'):
            print_warning(f"Test case missing 'name' field: {file_path}")
            return None
            
        if not test_case.get('script'):
            print_warning(f"Test case missing 'script' field: {file_path}")
            return None
            
        return test_case
    except Exception as e:
        print_error(f"Error loading test case from {file_path}: {str(e)}")
        return None


def discover_test_files() -> List[Path]:
    """
    Discover all test files in the tests directory.

    Returns:
        List of paths to discovered test files (YAML files)
    """
    tests_dir = Path.cwd() / "tests"
    if not tests_dir.exists() or not tests_dir.is_dir():
        print_warning("tests directory not found.")
        return []

    # Find all YAML test files (both in root and subdirectories)
    test_files = []
    
    # Look for YAML files in the tests directory and subdirectories
    for pattern in ["*.yaml", "*.yml"]:
        test_files.extend(tests_dir.glob(pattern))  # Root level
        test_files.extend(tests_dir.glob(f"**/{pattern}"))  # Subdirectories
    
    # Filter out test-suite metadata files
    test_files = [f for f in test_files if not f.name.startswith("test-suite.")]

    if not test_files:
        print_warning("No test files found in tests directory.")

    return test_files

async def run_test_case(
    test_case: Dict[str, Any],
    graph_definition: Dict[str, Any],
    thread_id: Optional[str] = None,
    llm_config: Optional[Dict[str, Any]] = None,
    judge_llm_config: Optional[Dict[str, Any]] = None,
    debug: bool = False
) -> Dict[str, Any]:
    """
    Run a single test case against the agent.

    Args:
        test_case: The test case to run
        graph_definition: The agent graph definition
        thread_id: Optional thread ID
        llm_config: Optional LLM configuration
        judge_llm_config: Optional LLM configuration for the judge
        debug: Whether to enable debug mode

    Returns:
        The test result
    """
    # Local test execution is no longer supported
    print_error("Local test execution is no longer supported.")
    print_info("Please use Kapso Cloud for running tests:")
    print_info("1. Deploy your agent: kapso deploy")
    print_info("2. Run tests through the web interface at https://app.kapso.ai")
    sys.exit(1)


def load_agent_configuration() -> Dict[str, Any]:
    """
    Load agent configuration and graph.

    Returns:
        The agent graph definition
    """
    # Try to read local graph definition
    local_graph, _ = load_agent_graph()

    if not local_graph:
        print_error("Could not load agent graph. Make sure agent.yaml exists in the current directory.")
        sys.exit(1)

    return local_graph

def display_conversation(conversation: List[Dict[str, Any]]) -> None:
    """
    Display the conversation between the agent and the simulated user.

    Args:
        conversation: List of message objects from the test result
    """
    if not conversation:
        print_info("No conversation to display.")
        return

    print_header("Conversation:")

    # Create a more concise conversation view
    for msg in conversation:
        role = msg.get("role", "")
        content = msg.get("content", "")

        # Format the content with indentation for better readability
        formatted_content = "\n".join(f"    {line}" for line in content.split("\n"))

        # Simplify the display based on role
        if role == "user":
            console.print(f"[bold green]User:[/bold green]")
            console.print(formatted_content)
        elif role == "assistant":
            console.print(f"[bold blue]Assistant:[/bold blue]")
            console.print(formatted_content)
        else:
            console.print(f"[bold yellow]{role.title()}:[/bold yellow]")
            console.print(formatted_content)

        # Add a small separator between messages
        console.print("")

def display_test_result(test_result: Dict[str, Any], verbose: bool = False) -> None:
    """
    Display a test result in the console.

    Args:
        test_result: The test result to display
        verbose: Whether to show verbose output
    """
    score = test_result.get("score", 0.0)
    color = "green" if score >= 0.8 else "yellow" if score >= 0.5 else "red"
    status = "PASS" if score >= 0.8 else "FAIL"

    # Display the test result summary
    headers = ["Test Case", "Score", "Status"]
    rows = [[test_result.get("test_case_name", "Unknown"), f"{score:.2f}", status]]
    print_table("Test Result", headers, rows)

    # Always display the feedback (evaluation)
    feedback = test_result.get("feedback", "No feedback available")

    # Try to render feedback as markdown if it looks like markdown
    if "###" in feedback or "##" in feedback or "*" in feedback or "- " in feedback:
        try:
            console.print(Panel(Markdown(feedback), title="[bold cyan]Evaluation[/bold cyan]", border_style="cyan"))
        except Exception:
            console.print(Panel(feedback, title="[bold cyan]Evaluation[/bold cyan]", border_style="cyan"))
    else:
        console.print(Panel(feedback, title="[bold cyan]Evaluation[/bold cyan]", border_style="cyan"))

    # Always display the conversation
    conversation = test_result.get("conversation", [])
    display_conversation(conversation)

    # Display any errors if present
    error = test_result.get("error")
    if error and isinstance(error, dict):
        print_header("Error:")
        print_error(error.get("message", "Unknown error"))

def display_test_suite_results(results: List[Dict[str, Any]], verbose: bool = False) -> None:
    """
    Display test suite results in the console.

    Args:
        results: List of test results to display
        verbose: Whether to show verbose output
    """
    if not results:
        console.print("[yellow]No test results to display.[/yellow]")
        return

    # Create a summary table
    table = Table(show_header=True, header_style="bold", box=box.SIMPLE)
    table.add_column("Test Case", style="cyan")
    table.add_column("Score", style="white")
    table.add_column("Status", style="white")

    # Aggregate stats
    passed = 0
    total_score = 0.0

    for result in results:
        score = result.get("score", 0.0)
        total_score += score

        status = "PASS" if score >= 0.8 else "FAIL"
        if status == "PASS":
            passed += 1
            status_color = "green"
        else:
            status_color = "red"

        # Determine color based on score
        if score >= 0.8:
            score_color = "green"
        elif score >= 0.5:
            score_color = "yellow"
        else:
            score_color = "red"

        table.add_row(
            result.get("test_case_name", "Unknown"),
            f"[{score_color}]{score:.2f}[/{score_color}]",
            f"[{status_color}]{status}[/{status_color}]"
        )

    # Add summary row
    avg_score = total_score / len(results) if results else 0
    table.add_section()
    table.add_row(
        "[bold]Summary[/bold]",
        f"[bold]{avg_score:.2f}[/bold]",
        f"[bold]{passed}/{len(results)} passed[/bold]"
    )

    console.print(table)

    # Display individual test details if verbose
    if verbose:
        console.print("\n[bold cyan]Test Details:[/bold cyan]")
        for i, result in enumerate(results):
            console.print(f"\n[bold]{i+1}. {result.get('test_case_name', 'Unknown')}[/bold]")
            console.print(f"Score: {result.get('score', 0.0):.2f}")
            console.print(f"Feedback: {result.get('feedback', 'No feedback available')}")

            # Show error if any
            error = result.get("error")
            if error and isinstance(error, dict):
                console.print(f"[red]Error: {error.get('message', 'Unknown error')}[/red]")

async def async_main(
    test_file: Optional[Path] = None,
    test_case_name: Optional[str] = None,
    debug: bool = False,
    verbose: bool = False
) -> None:
    """
    Async implementation of the main function.
    """
    # Local test execution is no longer supported
    console.print("\n[yellow]Local test execution is no longer supported.[/yellow]\n")
    console.print("[cyan]Please use Kapso Cloud for running tests:[/cyan]")
    console.print("1. Deploy your agent: [green]kapso deploy[/green]")
    console.print("2. Run tests through the web interface at [blue]https://app.kapso.ai[/blue]\n")
    sys.exit(0)
    
    # The code below is kept for reference but won't be executed
    current_cwd = Path.cwd().resolve(strict=True)
    llm_api_key = os.getenv("LLM_API_KEY", "")
    judge_llm_api_key = os.getenv("JUDGE_LLM_API_KEY", "")
    
    if False and not llm_api_key:
        console.print("\n[red]Error: No JUDGE_LLM_API_KEY found for test evaluation[/red]\n")
        console.print("The judge LLM is used to evaluate test results.\n")
        console.print("[yellow]Options:[/yellow]")
        console.print("1. Set up your environment variables:")
        console.print("   • Edit .env and add:")
        console.print("     [cyan]JUDGE_LLM_API_KEY=your-judge-api-key[/cyan]\n")
        console.print("2. Export the environment variable directly:")
        console.print("   [cyan]export JUDGE_LLM_API_KEY=your-api-key[/cyan]\n")
        console.print("3. Use the same key as your main LLM:")
        console.print("   [cyan]export JUDGE_LLM_API_KEY=$LLM_API_KEY[/cyan]")
        sys.exit(1)

    compile_agent_if_needed(verbose)
    graph_definition = load_agent_configuration()

    # Discover test files
    test_files_to_run = []
    if test_file:
        if not test_file.exists():
            console.print(f"[red]Error: Test file not found: {test_file.relative_to(current_cwd)}[/red]")
            sys.exit(1)
        test_files_to_run = [test_file]
    else:
        test_files_to_run = discover_test_files()

    if not test_files_to_run:
        console.print("[yellow]No test files found.[/yellow]")
        sys.exit(0)

    all_results = []
    
    # Group test files by directory for suite organization
    from collections import defaultdict
    test_suites = defaultdict(list)
    
    for file_path in test_files_to_run:
        # Group by parent directory
        suite_dir = file_path.parent
        test_suites[suite_dir].append(file_path)
    
    # Run tests by suite
    for suite_dir, test_files in test_suites.items():
        suite_name = suite_dir.name if suite_dir.name != "tests" else "Default"
        relative_suite_path = suite_dir.relative_to(current_cwd)
        
        # If running a specific test by name, filter
        if test_case_name and test_file:
            # Load the test file to check if it matches
            test_case = load_test_case_from_yaml(test_file)
            if not test_case or test_case.get('name') != test_case_name:
                console.print(f"[red]Error: Test case '{test_case_name}' not found in {test_file.relative_to(current_cwd)}[/red]")
                continue
            console.print(f"\n[bold cyan]Running test case '{test_case_name}'[/bold cyan]")
        else:
            console.print(f"\n[bold cyan]Running tests from: {relative_suite_path}[/bold cyan]")
        
        suite_results = []
        
        for test_file_path in sorted(test_files):
            # Load test case from YAML
            test_case = load_test_case_from_yaml(test_file_path)
            if not test_case:
                continue
                
            # Skip if looking for specific test name and this isn't it
            if test_case_name and not test_file and test_case.get('name') != test_case_name:
                continue
            
            test_name = test_case.get('name', 'Unknown')
            spinner, spinner_task = ui.start_spinner(f"Running test case: {test_name}...")

            try:
                # Run the test case
                result = await run_test_case(
                    test_case=test_case,
                    graph_definition=graph_definition,
                    debug=debug
                )

                ui.stop_spinner()

                # Display the result
                display_test_result(result, verbose)

                # Add to results
                suite_results.append(result)
                all_results.append(result)

            except Exception as e:
                ui.stop_spinner()
                console.print(f"[red]Error running test case '{test_name}': {str(e)}[/red]")
                if debug:
                    import traceback
                    traceback.print_exc()

        # If we ran multiple test cases in this suite, show a summary
        if len(suite_results) > 1:
            console.print(f"\n[bold cyan]{suite_name} Suite Summary:[/bold cyan]")
            display_test_suite_results(suite_results, False)

    # If we ran multiple test suites, show an overall summary
    if len(test_suites) > 1 and all_results:
        console.print("\n[bold cyan]Overall Test Summary:[/bold cyan]")
        display_test_suite_results(all_results, False)

def test_command(
    test_path: Optional[str] = typer.Argument(
        None,
        help="Path to test file or directory (relative to tests/ or absolute)"
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Name of a specific test case to run"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug logging"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output"
    ),
):
    """
    Run tests for your agent. By default, runs all discovered test files.
    Specify a test file, directory, or a specific test case to run.
    
    Examples:
        kapso test                              # Run all tests
        kapso test greeting_test                # Run test by name (searches all files)
        kapso test greeting_test.yaml           # Run specific test file
        kapso test basic_functionality/         # Run all tests in a directory
    """
    # Configure logging
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            force=True
        )

    # Handle test path resolution
    test_file = None
    if test_path:
        # First check if the path exists as is
        direct_path = Path(test_path)
        if direct_path.exists():
            if direct_path.is_file():
                test_file = direct_path.resolve(strict=True)
            elif direct_path.is_dir():
                # If it's a directory, we'll discover all tests in it
                test_file = None  # Will be handled by discover_test_files
            else:
                print_error(f"Path '{test_path}' is neither a file nor directory.")
                sys.exit(1)
        else:
            # Check if it's in the tests directory
            tests_dir = Path.cwd() / "tests"
            test_in_tests = tests_dir / test_path
            
            if test_in_tests.exists():
                if test_in_tests.is_file():
                    test_file = test_in_tests.resolve(strict=True)
                elif test_in_tests.is_dir():
                    test_file = None  # Will be handled by discover_test_files
            else:
                # Try adding .yaml extension if not already present
                if not test_path.endswith(('.yaml', '.yml')):
                    for ext in ['.yaml', '.yml']:
                        test_with_ext = tests_dir / f"{test_path}{ext}"
                        if test_with_ext.exists() and test_with_ext.is_file():
                            test_file = test_with_ext.resolve(strict=True)
                            break
                        # Also check in subdirectories
                        matches = list(tests_dir.glob(f"**/{test_path}{ext}"))
                        if matches:
                            test_file = matches[0].resolve(strict=True)
                            break
                
                if not test_file:
                    # If still not found, try to match by test name
                    all_test_files = discover_test_files()
                    for f in all_test_files:
                        if f.stem == test_path:
                            test_file = f
                            break
                    
                    if not test_file:
                        print_error(f"Test '{test_path}' not found.")
                        sys.exit(1)

    # Run the async main coroutine
    try:
        asyncio.run(async_main(
            test_file=test_file,
            test_case_name=name,
            debug=debug,
            verbose=verbose
        ))
    except KeyboardInterrupt:
        print_warning("Testing interrupted.")
        sys.exit(0)
    except Exception as e:
        print_error(str(e))
        sys.exit(1)
"""
Definition for file operation tools.
"""

# Import later when needed
# import glob
import logging
import os
import re

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
# For future use
# from pathlib import Path


logger = logging.getLogger(__name__)


@tool
def file_read(file: str, state, config: RunnableConfig, start_line: int = None, end_line: int = None, ) -> str:
    """
    Read file content. Use for checking file contents, analyzing logs, or reading configuration files.

    Key usage guidelines:
    - Use for reading text files, logs, or configuration files
    - Specify line ranges for large files to avoid memory issues
    - Files are read from the thread-specific directory

    Args:
        file: Absolute path of the file to read
        start_line: (Optional) Starting line to read from, 0-based
        end_line: (Optional) Ending line number (exclusive)
        sudo: (Optional) Whether to use sudo privileges
    """
    try:
        # Get thread_id from config
        thread_id = _get_thread_id(config)
        if not thread_id:
            return "Error: Could not determine thread ID"

        # Ensure the file is within the thread directory
        file_path = _ensure_thread_path(file, thread_id)

        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"

        # Read file content
        with open(file_path, "r") as f:
            lines = f.readlines()

        # Apply line range if specified
        if start_line is not None and end_line is not None:
            lines = lines[start_line:end_line]
        elif start_line is not None:
            lines = lines[start_line:]
        elif end_line is not None:
            lines = lines[:end_line]

        return "".join(lines)

    except Exception as e:
        logger.error(f"Error reading file {file}: {str(e)}")
        return f"Error reading file: {str(e)}"


@tool
def file_write(
    file: str,
    content: str,
    state,
    config: RunnableConfig,
    append: bool = False,
    leading_newline: bool = False,
    trailing_newline: bool = True,
) -> str:
    """
    Overwrite or append content to a file. Use for creating new files, appending content, or modifying existing files.

    Key usage guidelines:
    - Use for creating new files or modifying existing ones
    - Set append=True to add to existing content instead of overwriting
    - Files are written to the thread-specific directory
    - "file" and "content" are required arguments.

    Args:
        file: Absolute path of the file to write to
        content: Text content to write
        append: (Optional) Whether to use append mode
        leading_newline: (Optional) Whether to add a leading newline
        trailing_newline: (Optional) Whether to add a trailing newline
    """
    try:
        # Get thread_id from config
        thread_id = _get_thread_id(config)
        if not thread_id:
            return "Error: Could not determine thread ID"

        # Ensure the file is within the thread directory
        file_path = _ensure_thread_path(file, thread_id)

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Prepare content with optional newlines
        final_content = content
        if leading_newline:
            final_content = "\n" + final_content
        if trailing_newline and not final_content.endswith("\n"):
            final_content = final_content + "\n"

        # Write to file
        mode = "a" if append else "w"
        with open(file_path, mode) as f:
            f.write(final_content)

        return f"Successfully wrote to file: {file_path}"

    except Exception as e:
        logger.error(f"Error writing to file {file}: {str(e)}")
        return f"Error writing to file: {str(e)}"


@tool
def file_str_replace(file: str, old_str: str, new_str: str, state, config: RunnableConfig) -> str:
    """
    Replace specified string in a file. Use for updating specific content in files or fixing errors in code.

    Key usage guidelines:
    - Use for making targeted replacements in files
    - Useful for updating configuration values or fixing errors
    - Files are modified in the thread-specific directory

    Args:
        file: Absolute path of the file to perform replacement on
        old_str: Original string to be replaced
        new_str: New string to replace with
    """
    try:
        # Get thread_id from config
        thread_id = _get_thread_id(config)
        if not thread_id:
            return "Error: Could not determine thread ID"

        # Ensure the file is within the thread directory
        file_path = _ensure_thread_path(file, thread_id)

        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"

        # Read file content
        with open(file_path, "r") as f:
            content = f.read()

        # Replace string
        new_content = content.replace(old_str, new_str)

        # Write back to file
        with open(file_path, "w") as f:
            f.write(new_content)

        # Count replacements
        count = content.count(old_str)
        return f"Successfully replaced {count} occurrences in file: {file_path}"

    except Exception as e:
        logger.error(f"Error replacing string in file {file}: {str(e)}")
        return f"Error replacing string in file: {str(e)}"


@tool
def file_find_in_content(file: str, regex: str, state, config: RunnableConfig) -> str:
    """
    Search for matching text within file content. Use for finding specific content or patterns in files.

    Key usage guidelines:
    - Use for searching for patterns in files
    - Returns all matching lines with line numbers
    - Files are searched in the thread-specific directory

    Args:
        file: Absolute path of the file to search within
        regex: Regular expression pattern to match
        sudo: (Optional) Whether to use sudo privileges
    """
    try:
        # Get thread_id from config
        thread_id = _get_thread_id(config)
        if not thread_id:
            return "Error: Could not determine thread ID"

        # Ensure the file is within the thread directory
        file_path = _ensure_thread_path(file, thread_id)

        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"

        # Compile regex
        pattern = re.compile(regex)

        # Search in file
        matches = []
        with open(file_path, "r") as f:
            for i, line in enumerate(f):
                if pattern.search(line):
                    matches.append(f"Line {i + 1}: {line.rstrip()}")

        if matches:
            return f"Found {len(matches)} matches in {file_path}:\n" + "\n".join(matches)
        else:
            return f"No matches found in {file_path} for pattern: {regex}"

    except Exception as e:
        logger.error(f"Error searching in file {file}: {str(e)}")
        return f"Error searching in file: {str(e)}"


@tool
def file_find_by_name(path: str, glob_pattern: str, state, config: RunnableConfig) -> str:
    """
    Find files by name pattern in specified directory. Use for locating files with specific naming patterns.

    Key usage guidelines:
    - Use for finding files matching a pattern
    - Searches are restricted to the thread-specific directory
    - Returns a list of matching files with their sizes

    Args:
        path: Absolute path of directory to search
        glob_pattern: Filename pattern using glob syntax wildcards
    """
    # Import glob here to avoid circular import issues
    import glob as glob_module

    try:
        # Get thread_id from config
        thread_id = _get_thread_id(config)
        if not thread_id:
            return "Error: Could not determine thread ID"

        # Ensure the path is within the thread directory
        dir_path = _ensure_thread_path(path, thread_id)

        # Check if directory exists
        if not os.path.exists(dir_path):
            return f"Error: Directory does not exist: {dir_path}"

        # Find files matching pattern
        search_pattern = os.path.join(dir_path, glob_pattern)
        matching_files = glob_module.glob(search_pattern)

        if matching_files:
            # Format results with file sizes
            results = []
            for file_path in matching_files:
                size = os.path.getsize(file_path)
                results.append(f"{file_path} ({_format_size(size)})")

            return (
                f"Found {len(matching_files)} files matching '{glob_pattern}' in {dir_path}:\n"
                + "\n".join(results)
            )
        else:
            return f"No files found matching '{glob_pattern}' in {dir_path}"

    except Exception as e:
        logger.error(f"Error finding files in {path}: {str(e)}")
        return f"Error finding files: {str(e)}"


# Helper functions


def _get_thread_id(config: RunnableConfig) -> str:
    """Get thread ID from the config."""
    try:
        configurable = config.get("configurable") or {}
        if configurable:
            return configurable.get("thread_id")
        return None
    except Exception as e:
        logger.error(f"Error getting thread ID: {str(e)}")
        return None


def _ensure_thread_path(path: str, thread_id: str) -> str:
    """Ensure the path is within the thread directory."""
    # Create a path that's guaranteed to be within the thread directory
    thread_base_dir = os.path.join(os.environ.get("THREAD_BASE_DIR", "./tmp/threads"), thread_id)

    # If the path already contains the thread_id, use it as is
    if thread_id in path:
        # Ensure it's still within the thread base directory
        if not os.path.abspath(path).startswith(os.path.abspath(thread_base_dir)):
            # If not, rebase it to the thread directory
            rel_path = os.path.basename(path)
            return os.path.join(thread_base_dir, rel_path)
        return path

    # Otherwise, treat the path as relative to the thread directory
    return os.path.join(thread_base_dir, os.path.basename(path))


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

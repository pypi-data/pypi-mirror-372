import os
import site
import subprocess
# import sys
from typing import List, Dict, Union, Tuple
from rich import print as rprint
from rich.markup import escape
# from pathlib import Path

# Initialize global variables
BBTOOLS_PATH = None

def find_bbtools_path():
    """
    Find the BBTools directory by checking multiple possible locations.
    Returns the path to the BBTools directory or None if not found.
    """
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of possible paths to check
    possible_paths = [
        # Check vendor directory relative to this file
        os.path.join(current_dir, "vendor", "bbmap"),
        # Check site-packages directory
        os.path.join(site.getsitepackages()[0], "bbmapy", "vendor", "bbmap"),
        # Check parent directories
        os.path.join(os.path.dirname(current_dir), "vendor", "bbmap"),
        # Check current working directory
        os.path.join(os.getcwd(), "vendor", "bbmap"),
    ]
    
    # Add conda environment paths if available
    if 'CONDA_PREFIX' in os.environ:
        conda_prefix = os.environ['CONDA_PREFIX']
        possible_paths.extend([
            os.path.join(conda_prefix, "lib", "python3.*", "site-packages", "bbmapy", "vendor", "bbmap"),
            os.path.join(conda_prefix, "vendor", "bbmap"),
        ])
    
    # Check each path
    for path in possible_paths:
        # Handle glob patterns in path
        if '*' in path:
            import glob
            matches = glob.glob(path)
            for match in matches:
                if os.path.exists(match) and os.path.isdir(match):
                    return match
        else:
            if os.path.exists(path) and os.path.isdir(path):
                return path
    
    # If no path is found, return None
    return None

try:
    BBTOOLS_PATH = find_bbtools_path()  
    os.environ["PATH"] = f"{BBTOOLS_PATH}/:{os.environ['PATH']}"
except FileNotFoundError as e:
    rprint(f"[red]Error: {e}[/red]")
    # Don't exit here, as this might be imported before bbtools is installed
    # We'll check again when functions are actually called

def _pack_args(kwargs: Dict[str, Union[str, bool, int]]) -> List[str]:
    """Convert Python keyword arguments to BBTools command line arguments."""
    args = []
    
    for key, value in kwargs.items():
        if key in ['Xmx', 'Xms', 'da', 'ea', 'eoom']:
            if isinstance(value, bool) and value:
                args.append(f"-{key}")
            elif value is not None:
                args.append(f"-{key}{str(value)}")
        elif key == "in_file":
            args.append(f"in={str(value)}")
        elif isinstance(value, bool) and value:
            args.append(key)
        elif value is not None:
            args.append(f"{key}={str(value)}")
    
    return args


def _run_command(tool: str, args: List[str], capture_output: bool = False) -> Union[None, Tuple[str, str]]:
    """Run a BBTools command using subprocess (fallback method)."""

    # Find the BBTools path if not already set
    global BBTOOLS_PATH
    if BBTOOLS_PATH is None:
        BBTOOLS_PATH = find_bbtools_path()
        if BBTOOLS_PATH is None:
            raise RuntimeError("BBTools directory not found.")
        os.environ["PATH"] = f"{BBTOOLS_PATH}/current/:{os.environ['PATH']}"
    
    # Build the command
    command = [os.path.join(BBTOOLS_PATH, tool)] + args
    escaped_command = ' '.join(escape(str(arg)) for arg in command)
    
    if capture_output:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {escaped_command}\nError: {escape(result.stderr)}")
        return result.stdout, result.stderr
    else:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        while True:
            stdout_line = process.stdout.readline()
            stderr_line = process.stderr.readline()
            
            if not stdout_line and not stderr_line and process.poll() is not None:
                break
            
            if stdout_line:
                rprint(escape(stdout_line.strip()))
            if stderr_line:
                rprint("[bold red]" + escape(stderr_line.strip()) + "[/bold red]")
        
        if process.returncode != 0:
            raise RuntimeError(f"Command failed: {escaped_command}")
        
        return None


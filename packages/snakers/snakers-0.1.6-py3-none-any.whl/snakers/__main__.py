"""
Main entry point for snakers package.

This allows the package to be executed with:
    python -m snakers
"""

from pathlib import Path
from .cli import main
from rich.console import Console

# Add the package's exercises directory to the path
PACKAGE_DIR = Path(__file__).parent
EXERCISES_DIR = PACKAGE_DIR / "exercises"

console = Console()

def run():
    """Entry point for the snakers command."""
    # First look for exercises in current directory (user's initialized exercises)
    cwd_exercises = Path.cwd() / "exercises"
    if cwd_exercises.exists():
        main(exercises_dir=cwd_exercises)
    else:
        main()

if __name__ == "__main__":
    run()

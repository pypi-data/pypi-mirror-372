"""
Snakers - Interactive Python exercises with Ruff linting

A tool to help learn Python by fixing and completing code exercises.
"""

__version__ = "0.1.4"
__author__ = "Arman Rostami"
__email__ = "armanrostami@outlook.com"

from .runner import ExerciseRunner
from .exercise import Exercise

__all__ = ["ExerciseRunner", "Exercise", "__version__"]

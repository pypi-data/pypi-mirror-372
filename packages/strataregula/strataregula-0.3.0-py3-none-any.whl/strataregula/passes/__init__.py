"""
StrataRegula Compile Passes

This package contains compilation passes that transform configuration data
through various optimization and processing steps.
"""

from .intern import InternPass

__all__ = ["InternPass"]

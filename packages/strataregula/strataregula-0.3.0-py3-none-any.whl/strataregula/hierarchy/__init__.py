"""
Hierarchy Processing Module - Handle configuration merging and hierarchy management.

Provides functionality for:
- Merging configurations with deep copy for same hierarchies
- Environment-specific configuration management
- Automatic conflict resolution
"""

from .commands import EnvironmentMergeCommand, MergeCommand
from .merger import HierarchyMerger, MergeStrategy
from .processor import HierarchyProcessor

__all__ = [
    "EnvironmentMergeCommand",
    "HierarchyMerger",
    "HierarchyProcessor",
    "MergeCommand",
    "MergeStrategy",
]

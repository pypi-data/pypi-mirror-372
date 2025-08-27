"""
Hierarchy Processing Module - Handle configuration merging and hierarchy management.

Provides functionality for:
- Merging configurations with deep copy for same hierarchies
- Environment-specific configuration management
- Automatic conflict resolution
"""

from .merger import HierarchyMerger, MergeStrategy
from .processor import HierarchyProcessor
from .commands import MergeCommand, EnvironmentMergeCommand

__all__ = [
    'HierarchyMerger',
    'MergeStrategy',
    'HierarchyProcessor',
    'MergeCommand',
    'EnvironmentMergeCommand',
]

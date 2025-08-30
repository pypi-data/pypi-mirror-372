from contextlib import suppress

"""
Strataregula - Layered Configuration Management with Strata Rules Architecture.

A hierarchical configuration management tool with pattern expansion
for large-scale configuration generation.

Features:
- Wildcard pattern expansion (* and **)
- Hierarchical mapping (47 prefectures → 8 regions)
- Multiple output formats (Python, JSON, YAML)
- Memory-efficient streaming processing
- Simple CLI interface
- Pass/View kernel architecture (v0.3.0)
- Config interning and hash-consing (v0.3.0)
- Content-addressed caching (v0.3.0)
"""

__version__ = "0.3.0"
__author__ = "Strataregula Team"
__email__ = "team@strataregula.com"

# Only import what actually works and is tested
with suppress(ImportError):
    from .core.pattern_expander import EnhancedPatternExpander, PatternExpander

with suppress(ImportError):
    from .core.config_compiler import CompilationConfig, ConfigCompiler

# v0.3.0 New Architecture
with suppress(ImportError):
    from .kernel import CacheStats, Kernel, LRUCacheBackend

with suppress(ImportError):
    from .passes import InternPass

__all__ = [
    # Version info
    "__version__",
    # v0.3.0 New Architecture
    "Kernel",
    "InternPass",
]

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
"""

__version__ = "0.2.0"
__author__ = "Strataregula Team"
__email__ = "team@strataregula.com"

# Only import what actually works and is tested
try:
    from .core.pattern_expander import (
        PatternExpander,
        EnhancedPatternExpander
    )
except ImportError:
    pass

try:
    from .core.config_compiler import (
        ConfigCompiler,
        CompilationConfig
    )
except ImportError:
    pass

__all__ = [
    # Version info
    '__version__',
]
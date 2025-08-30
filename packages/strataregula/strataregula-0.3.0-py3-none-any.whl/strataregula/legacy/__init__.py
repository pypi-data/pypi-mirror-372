"""
Legacy API compatibility layer for StrataRegula v0.2.x

This module provides backward compatibility for code written against
StrataRegula v0.2.x API. All legacy APIs will emit DeprecationWarnings
and will be removed in v1.0.0.

Migration Timeline:
- v0.3.0: Full compatibility with warnings
- v0.4.0: Compatibility maintained, stronger warnings
- v0.5.0: Legacy imports require explicit opt-in
- v1.0.0: Complete removal

Example:
    # Old v0.2.x code
    from strataregula import Engine
    engine = Engine(config_path="config.yaml")
    result = engine.compile()
    
    # New v0.3.0+ code
    from strataregula.kernel import Kernel
    kernel = Kernel()
    result = kernel.compile("config.yaml")
"""

import warnings
from typing import Any, Dict, Optional, Union, List
from pathlib import Path
import functools

# Import new v0.3.0 components
from ..kernel import Kernel
from ..core.config_compiler import ConfigCompiler
from ..core.pattern_expander import PatternExpander


def deprecated(since: str, removed_in: str, alternative: str = None):
    """Decorator to mark functions/classes as deprecated."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            message = (
                f"{func.__name__} is deprecated since v{since} "
                f"and will be removed in v{removed_in}."
            )
            if alternative:
                message += f" Use {alternative} instead."
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class Engine:
    """
    Legacy Engine class for v0.2.x compatibility.
    
    DEPRECATED: Use strataregula.kernel.Kernel instead.
    This class will be removed in v1.0.0.
    """
    
    def __init__(self, 
                 config_path: Optional[Union[str, Path]] = None,
                 template_dir: Optional[str] = None,
                 output_format: str = "yaml",
                 **kwargs):
        """
        Initialize legacy Engine with v0.2.x parameters.
        
        Args:
            config_path: Path to configuration file (v0.2.x style)
            template_dir: Directory containing templates (deprecated)
            output_format: Output format (yaml/json)
            **kwargs: Additional v0.2.x parameters (ignored with warning)
        """
        warnings.warn(
            "Engine class is deprecated since v0.3.0 and will be removed in v1.0.0. "
            "Use strataregula.kernel.Kernel instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Map to new Kernel
        self._kernel = Kernel()
        self._config_path = config_path
        self._output_format = output_format
        
        # Warn about ignored parameters
        if template_dir:
            warnings.warn(
                "template_dir parameter is deprecated and ignored. "
                "Templates are now resolved automatically.",
                DeprecationWarning,
                stacklevel=2
            )
        
        if kwargs:
            warnings.warn(
                f"Parameters {list(kwargs.keys())} are deprecated and ignored.",
                DeprecationWarning,
                stacklevel=2
            )
    
    @deprecated(since="0.3.0", removed_in="1.0.0", alternative="Kernel.compile()")
    def compile(self, config_override: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Compile configuration using v0.2.x API.
        
        Args:
            config_override: Optional configuration override
            
        Returns:
            Compiled configuration dictionary
        """
        if self._config_path:
            return self._kernel.compile(str(self._config_path))
        elif config_override:
            # Handle inline config (v0.2.x feature)
            import tempfile
            import yaml
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(config_override, f)
                temp_path = f.name
            try:
                return self._kernel.compile(temp_path)
            finally:
                import os
                os.unlink(temp_path)
        else:
            raise ValueError("No configuration provided")
    
    @deprecated(since="0.3.0", removed_in="1.0.0", alternative="Kernel.expand()")
    def expand_pattern(self, pattern: str, context: Optional[Dict] = None) -> List[str]:
        """
        Expand pattern using v0.2.x API.
        
        Args:
            pattern: Pattern to expand
            context: Optional context dictionary
            
        Returns:
            List of expanded values
        """
        # Use internal pattern expander
        expander = PatternExpander()
        return expander.expand(pattern, context or {})
    
    @deprecated(since="0.3.0", removed_in="1.0.0", alternative="Kernel.validate()")
    def validate(self, strict: bool = False) -> bool:
        """
        Validate configuration using v0.2.x API.
        
        Args:
            strict: Whether to use strict validation
            
        Returns:
            True if valid, False otherwise
        """
        if not self._config_path:
            return False
        
        try:
            # New validation through kernel
            self._kernel.validate(str(self._config_path))
            return True
        except Exception:
            return False
    
    @deprecated(since="0.3.0", removed_in="1.0.0")
    def service_time(self, service_id: str) -> float:
        """
        Legacy service_time method for benchmarking.
        
        Args:
            service_id: Service identifier (v0.2.x format)
            
        Returns:
            Simulated service time in milliseconds
        """
        # Simulate legacy behavior
        import random
        warnings.warn(
            "service_time() is deprecated. Use performance benchmarks instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return random.uniform(0.1, 2.0)
    
    @deprecated(since="0.3.0", removed_in="1.0.0", alternative="Kernel.get_stats()")
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get engine metrics using v0.2.x API.
        
        Returns:
            Dictionary of metrics
        """
        # Map to new kernel stats
        stats = self._kernel.get_stats()
        
        # Transform to v0.2.x format
        return {
            "compile_count": stats.get("compilations", 0),
            "cache_hits": stats.get("cache_hits", 0),
            "cache_misses": stats.get("cache_misses", 0),
            "total_time": stats.get("total_time_ms", 0.0),
            "memory_usage": stats.get("memory_bytes", 0),
        }


class ConfigLoader:
    """
    Legacy ConfigLoader class for v0.2.x compatibility.
    
    DEPRECATED: Use strataregula.core.config_compiler.ConfigCompiler instead.
    """
    
    def __init__(self, search_paths: Optional[List[str]] = None):
        """Initialize legacy ConfigLoader."""
        warnings.warn(
            "ConfigLoader is deprecated since v0.3.0. "
            "Use ConfigCompiler or Kernel directly.",
            DeprecationWarning,
            stacklevel=2
        )
        self._compiler = ConfigCompiler()
    
    @deprecated(since="0.3.0", removed_in="1.0.0", alternative="ConfigCompiler.load()")
    def load(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration file."""
        import yaml
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    @deprecated(since="0.3.0", removed_in="1.0.0")
    def merge(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple configurations."""
        result = {}
        for config in configs:
            result.update(config)
        return result


class TemplateEngine:
    """
    Legacy TemplateEngine class for v0.2.x compatibility.
    
    DEPRECATED: Template functionality is now integrated into Kernel.
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """Initialize legacy TemplateEngine."""
        warnings.warn(
            "TemplateEngine is deprecated since v0.3.0. "
            "Template functionality is now integrated into Kernel.",
            DeprecationWarning,
            stacklevel=2
        )
    
    @deprecated(since="0.3.0", removed_in="1.0.0", alternative="Kernel.render()")
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render template with context."""
        # Simulate legacy template rendering
        return f"Rendered: {template_name} with {len(context)} variables"


# Legacy function aliases
@deprecated(since="0.3.0", removed_in="1.0.0", alternative="strataregula.cli.main()")
def cli_run(*args, **kwargs):
    """Legacy CLI entry point."""
    from ..cli.main import main
    return main()


@deprecated(since="0.3.0", removed_in="1.0.0", alternative="Kernel.compile()")
def compile_config(path: str, **kwargs) -> Dict[str, Any]:
    """Legacy standalone compile function."""
    kernel = Kernel()
    return kernel.compile(path)


@deprecated(since="0.3.0", removed_in="1.0.0")
def load_yaml(path: str) -> Dict[str, Any]:
    """Legacy YAML loader."""
    import yaml
    with open(path, 'r') as f:
        return yaml.safe_load(f)


# Export legacy API
__all__ = [
    'Engine',
    'ConfigLoader', 
    'TemplateEngine',
    'cli_run',
    'compile_config',
    'load_yaml',
]

# Version info for compatibility checking
LEGACY_API_VERSION = "0.2.x"
DEPRECATION_VERSION = "0.3.0"
REMOVAL_VERSION = "1.0.0"
"""
Advanced Plugin System for Strataregula - Layered Configuration Management.

This plugin system provides:
- Automatic plugin discovery via entry points and filesystem scanning
- Lifecycle management with states (discovered, loaded, active, failed)
- Configuration management with YAML/JSON support
- Error handling with circuit breakers and fallback mechanisms
- Hook integration for extensibility
"""

# Core plugin interfaces
from .base import PatternPlugin, PluginInfo, PluginManager

# Built-in plugins
from .builtin import SimulationPlugins
from .config import (
    ConfigValidator,
    GlobalPluginConfig,
    JSONSchemaValidator,
    PluginConfigEntry,
    PluginConfigManager,
)
from .error_handling import (
    CircuitBreaker,
    ErrorCategory,
    ErrorRecoveryStrategy,
    ErrorSeverity,
    FallbackHandler,
    PluginError,
    PluginErrorHandler,
)

# Advanced plugin system components
from .loader import PluginEntryPoint, PluginLoader, PluginLoadResult
from .manager import EnhancedPluginManager, PluginConfig, PluginContext, PluginState

__all__ = [
    # Core interfaces
    "PatternPlugin",
    "PluginInfo",
    "PluginManager",
    # Advanced system
    "PluginLoader",
    "PluginEntryPoint",
    "PluginLoadResult",
    "EnhancedPluginManager",
    "PluginState",
    "PluginContext",
    "PluginConfig",
    # Configuration
    "PluginConfigManager",
    "PluginConfigEntry",
    "GlobalPluginConfig",
    "ConfigValidator",
    "JSONSchemaValidator",
    # Error handling
    "PluginErrorHandler",
    "PluginError",
    "ErrorSeverity",
    "ErrorCategory",
    "ErrorRecoveryStrategy",
    "CircuitBreaker",
    "FallbackHandler",
    # Built-in
    "SimulationPlugins",
]

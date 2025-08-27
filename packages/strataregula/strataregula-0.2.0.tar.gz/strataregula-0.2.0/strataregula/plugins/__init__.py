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

# Advanced plugin system components  
from .loader import PluginLoader, PluginEntryPoint, PluginLoadResult
from .manager import (
    EnhancedPluginManager, 
    PluginState, 
    PluginContext, 
    PluginConfig
)
from .config import (
    PluginConfigManager, 
    PluginConfigEntry, 
    GlobalPluginConfig,
    ConfigValidator,
    JSONSchemaValidator
)
from .error_handling import (
    PluginErrorHandler,
    PluginError, 
    ErrorSeverity,
    ErrorCategory,
    ErrorRecoveryStrategy,
    CircuitBreaker,
    FallbackHandler
)

# Built-in plugins
from .builtin import SimulationPlugins

__all__ = [
    # Core interfaces
    'PatternPlugin', 
    'PluginInfo',
    'PluginManager',
    
    # Advanced system
    'PluginLoader',
    'PluginEntryPoint', 
    'PluginLoadResult',
    'EnhancedPluginManager',
    'PluginState',
    'PluginContext',
    'PluginConfig',
    
    # Configuration
    'PluginConfigManager',
    'PluginConfigEntry',
    'GlobalPluginConfig', 
    'ConfigValidator',
    'JSONSchemaValidator',
    
    # Error handling
    'PluginErrorHandler',
    'PluginError',
    'ErrorSeverity', 
    'ErrorCategory',
    'ErrorRecoveryStrategy',
    'CircuitBreaker',
    'FallbackHandler',
    
    # Built-in
    'SimulationPlugins'
]
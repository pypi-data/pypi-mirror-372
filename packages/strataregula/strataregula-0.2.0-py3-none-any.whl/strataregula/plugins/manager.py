"""
Enhanced Plugin Manager - Advanced plugin lifecycle management.
"""

import logging
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from contextlib import asynccontextmanager
import threading
import time

from .base import PatternPlugin, PluginInfo
from .loader import PluginLoader, PluginLoadResult
from ..hooks.base import HookManager, HookType

logger = logging.getLogger(__name__)


class PluginState(Enum):
    """Plugin lifecycle states."""
    DISCOVERED = "discovered"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    UNLOADING = "unloading"
    UNLOADED = "unloaded"


@dataclass
class PluginContext:
    """Runtime context for a plugin."""
    plugin: PatternPlugin
    state: PluginState
    load_time: float
    last_used: float
    use_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_usage(self) -> None:
        """Update usage statistics."""
        self.use_count += 1
        self.last_used = time.time()
    
    def record_error(self, error: str) -> None:
        """Record an error for this plugin."""
        self.error_count += 1
        self.last_error = error


@dataclass
class PluginConfig:
    """Configuration for plugin management."""
    max_errors: int = 5
    error_cooldown: float = 300.0  # 5 minutes
    auto_reload: bool = False
    lazy_loading: bool = True
    timeout: float = 30.0
    priority_patterns: List[str] = field(default_factory=list)


class EnhancedPluginManager:
    """Enhanced plugin manager with lifecycle management."""
    
    def __init__(self, config: Optional[PluginConfig] = None, plugin_group: str = "strataregula.plugins"):
        self.config = config or PluginConfig()
        self.loader = PluginLoader(plugin_group)
        self.hooks = HookManager()
        
        # Plugin management
        self._plugins: Dict[str, PluginContext] = {}
        self._plugin_order: List[str] = []
        self._state_listeners: Dict[PluginState, List[Callable]] = {
            state: [] for state in PluginState
        }
        
        # Thread safety
        self._lock = threading.RLock()
        self._shutdown_event = threading.Event()
        
        # Performance tracking
        self._performance_stats: Dict[str, Dict[str, Any]] = {}
        
        # Auto-discovery
        if not self.config.lazy_loading:
            self._discover_and_load_all()
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins."""
        with self._lock:
            discovered = self.loader.discover_plugins()
            
            for entry_point in discovered:
                if entry_point.name not in self._plugins:
                    # Create placeholder context for discovered plugins
                    self._plugins[entry_point.name] = PluginContext(
                        plugin=None,  # Will be loaded later
                        state=PluginState.DISCOVERED,
                        load_time=0,
                        last_used=0
                    )
            
            plugin_names = [ep.name for ep in discovered]
            logger.info(f"Discovered {len(plugin_names)} plugins: {', '.join(plugin_names)}")
            return plugin_names
    
    def load_plugin(self, name: str, force: bool = False) -> bool:
        """Load a specific plugin."""
        with self._lock:
            if name not in self._plugins:
                logger.error(f"Plugin '{name}' not discovered")
                return False
            
            context = self._plugins[name]
            
            if context.state == PluginState.LOADED and not force:
                return True
            
            if context.state == PluginState.FAILED and not force:
                if context.last_error and time.time() - context.load_time < self.config.error_cooldown:
                    logger.debug(f"Plugin '{name}' in cooldown period")
                    return False
            
            # Update state to loading
            self._update_plugin_state(name, PluginState.LOADING)
            
            try:
                # Load plugin using loader
                start_time = time.time()
                result = self.loader.load_plugin(name)
                
                if result.success and result.plugin:
                    # Update context with loaded plugin
                    context.plugin = result.plugin
                    context.load_time = time.time()
                    context.last_error = None
                    
                    # Initialize plugin hooks
                    self._setup_plugin_hooks(name, result.plugin)
                    
                    # Trigger lifecycle hooks
                    asyncio.create_task(self.hooks.trigger(
                        'plugin_loaded', 
                        plugin_name=name, 
                        plugin=result.plugin
                    ))
                    
                    self._update_plugin_state(name, PluginState.LOADED)
                    
                    # Performance tracking
                    load_duration = time.time() - start_time
                    self._record_performance(name, 'load_time', load_duration)
                    
                    logger.info(f"Successfully loaded plugin '{name}' in {load_duration:.3f}s")
                    return True
                else:
                    context.record_error(result.error or "Unknown error")
                    self._update_plugin_state(name, PluginState.FAILED)
                    logger.error(f"Failed to load plugin '{name}': {result.error}")
                    return False
                    
            except Exception as e:
                context.record_error(str(e))
                self._update_plugin_state(name, PluginState.FAILED)
                logger.exception(f"Exception loading plugin '{name}': {e}")
                return False
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a specific plugin."""
        with self._lock:
            if name not in self._plugins:
                return False
            
            context = self._plugins[name]
            if context.state not in [PluginState.LOADED, PluginState.ACTIVE, PluginState.INACTIVE]:
                return False
            
            self._update_plugin_state(name, PluginState.UNLOADING)
            
            try:
                # Cleanup plugin hooks
                self._cleanup_plugin_hooks(name)
                
                # Trigger lifecycle hooks
                asyncio.create_task(self.hooks.trigger(
                    'plugin_unloaded', 
                    plugin_name=name, 
                    plugin=context.plugin
                ))
                
                # Remove from loader
                self.loader.unload_plugin(name)
                
                # Reset context
                context.plugin = None
                self._update_plugin_state(name, PluginState.UNLOADED)
                
                logger.info(f"Successfully unloaded plugin '{name}'")
                return True
                
            except Exception as e:
                logger.exception(f"Exception unloading plugin '{name}': {e}")
                self._update_plugin_state(name, PluginState.FAILED)
                return False
    
    def activate_plugin(self, name: str) -> bool:
        """Activate a loaded plugin."""
        with self._lock:
            if name not in self._plugins:
                return False
            
            context = self._plugins[name]
            
            # Ensure plugin is loaded
            if context.state == PluginState.DISCOVERED:
                if not self.load_plugin(name):
                    return False
            
            if context.state != PluginState.LOADED:
                return False
            
            self._update_plugin_state(name, PluginState.ACTIVE)
            
            # Add to plugin order if not already present
            if name not in self._plugin_order:
                self._plugin_order.append(name)
                self._sort_plugins_by_priority()
            
            logger.info(f"Activated plugin '{name}'")
            return True
    
    def deactivate_plugin(self, name: str) -> bool:
        """Deactivate an active plugin."""
        with self._lock:
            if name not in self._plugins:
                return False
            
            context = self._plugins[name]
            if context.state != PluginState.ACTIVE:
                return False
            
            self._update_plugin_state(name, PluginState.INACTIVE)
            
            # Remove from plugin order
            if name in self._plugin_order:
                self._plugin_order.remove(name)
            
            logger.info(f"Deactivated plugin '{name}'")
            return True
    
    def get_plugin_for_pattern(self, pattern: str) -> Optional[PatternPlugin]:
        """Find the first active plugin that can handle the pattern."""
        with self._lock:
            for plugin_name in self._plugin_order:
                context = self._plugins.get(plugin_name)
                
                if (context and 
                    context.state == PluginState.ACTIVE and 
                    context.plugin and 
                    context.plugin.can_handle(pattern)):
                    
                    context.update_usage()
                    return context.plugin
            
            return None
    
    def expand_pattern(self, pattern: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Expand pattern using appropriate plugin with error handling."""
        start_time = time.time()
        
        try:
            plugin = self.get_plugin_for_pattern(pattern)
            if plugin:
                result = plugin.expand(pattern, context)
                
                # Record performance
                duration = time.time() - start_time
                plugin_name = plugin.info.name
                self._record_performance(plugin_name, 'expand_time', duration)
                
                return result
            else:
                # Fallback to default behavior
                return {pattern: context.get('value', None)}
                
        except Exception as e:
            # Record error and fall back
            logger.exception(f"Error expanding pattern '{pattern}': {e}")
            return {pattern: context.get('value', None)}
    
    def get_plugin_contexts(self) -> Dict[str, PluginContext]:
        """Get all plugin contexts."""
        with self._lock:
            return self._plugins.copy()
    
    def get_active_plugins(self) -> List[PatternPlugin]:
        """Get all active plugins in priority order."""
        with self._lock:
            active_plugins = []
            for plugin_name in self._plugin_order:
                context = self._plugins.get(plugin_name)
                if context and context.state == PluginState.ACTIVE and context.plugin:
                    active_plugins.append(context.plugin)
            return active_plugins
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """Get comprehensive plugin statistics."""
        with self._lock:
            stats_by_state = {}
            for state in PluginState:
                stats_by_state[state.value] = sum(
                    1 for ctx in self._plugins.values() 
                    if ctx.state == state
                )
            
            return {
                "total_plugins": len(self._plugins),
                "by_state": stats_by_state,
                "active_order": self._plugin_order.copy(),
                "performance": self._performance_stats.copy(),
                "loader_stats": self.loader.get_plugin_stats()
            }
    
    def add_state_listener(self, state: PluginState, callback: Callable[[str, PluginState], None]) -> None:
        """Add listener for plugin state changes."""
        self._state_listeners[state].append(callback)
    
    def remove_state_listener(self, state: PluginState, callback: Callable[[str, PluginState], None]) -> None:
        """Remove state change listener."""
        if callback in self._state_listeners[state]:
            self._state_listeners[state].remove(callback)
    
    async def shutdown(self) -> None:
        """Shutdown the plugin manager."""
        self._shutdown_event.set()
        
        # Unload all plugins
        plugin_names = list(self._plugins.keys())
        for name in plugin_names:
            self.unload_plugin(name)
        
        logger.info("Plugin manager shutdown complete")
    
    def _discover_and_load_all(self) -> None:
        """Discover and load all plugins."""
        plugin_names = self.discover_plugins()
        
        for name in plugin_names:
            if self.load_plugin(name):
                self.activate_plugin(name)
    
    def _update_plugin_state(self, name: str, new_state: PluginState) -> None:
        """Update plugin state and notify listeners."""
        old_state = self._plugins[name].state
        self._plugins[name].state = new_state
        
        # Notify listeners
        for callback in self._state_listeners[new_state]:
            try:
                callback(name, new_state)
            except Exception as e:
                logger.exception(f"Error in state listener: {e}")
        
        logger.debug(f"Plugin '{name}' state: {old_state.value} -> {new_state.value}")
    
    def _setup_plugin_hooks(self, name: str, plugin: PatternPlugin) -> None:
        """Setup hooks for a plugin."""
        # Register plugin-specific hooks if the plugin supports them
        if hasattr(plugin, 'register_hooks'):
            plugin.register_hooks(self.hooks)
    
    def _cleanup_plugin_hooks(self, name: str) -> None:
        """Cleanup hooks for a plugin."""
        # Remove plugin-specific hooks
        # This is a simplified implementation
        pass
    
    def _sort_plugins_by_priority(self) -> None:
        """Sort plugins by priority patterns."""
        def get_priority(plugin_name: str) -> int:
            for i, pattern in enumerate(self.config.priority_patterns):
                if pattern in plugin_name:
                    return i
            return len(self.config.priority_patterns)
        
        self._plugin_order.sort(key=get_priority)
    
    def _record_performance(self, plugin_name: str, metric: str, value: float) -> None:
        """Record performance metrics for a plugin."""
        if plugin_name not in self._performance_stats:
            self._performance_stats[plugin_name] = {}
        
        if metric not in self._performance_stats[plugin_name]:
            self._performance_stats[plugin_name][metric] = []
        
        # Keep only last 100 measurements
        measurements = self._performance_stats[plugin_name][metric]
        measurements.append(value)
        if len(measurements) > 100:
            measurements.pop(0)
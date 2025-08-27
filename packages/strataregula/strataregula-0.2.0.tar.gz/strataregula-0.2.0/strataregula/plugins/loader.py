"""
Plugin Loader - Advanced plugin discovery and loading system.
"""

import importlib
import importlib.metadata
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type, Any, Iterator
from dataclasses import dataclass
import inspect

from .base import PatternPlugin, PluginInfo

logger = logging.getLogger(__name__)


@dataclass
class PluginEntryPoint:
    """Represents a plugin entry point."""
    name: str
    group: str
    module_name: str
    attr_name: str
    dist_name: Optional[str] = None
    
    def load(self) -> Type[PatternPlugin]:
        """Load the plugin class from the entry point."""
        try:
            module = importlib.import_module(self.module_name)
            plugin_class = getattr(module, self.attr_name)
            
            if not issubclass(plugin_class, PatternPlugin):
                raise ValueError(f"Plugin class {self.attr_name} does not inherit from PatternPlugin")
                
            return plugin_class
        except ImportError as e:
            logger.error(f"Failed to import module {self.module_name}: {e}")
            raise
        except AttributeError as e:
            logger.error(f"Plugin class {self.attr_name} not found in {self.module_name}: {e}")
            raise


@dataclass
class PluginLoadResult:
    """Result of plugin loading operation."""
    success: bool
    plugin: Optional[PatternPlugin] = None
    error: Optional[str] = None
    entry_point: Optional[PluginEntryPoint] = None


class PluginLoader:
    """Advanced plugin loader with entry point discovery."""
    
    def __init__(self, plugin_group: str = "strataregula.plugins"):
        self.plugin_group = plugin_group
        self._discovered_plugins: Dict[str, PluginEntryPoint] = {}
        self._loaded_plugins: Dict[str, PatternPlugin] = {}
        self._failed_loads: Dict[str, str] = {}
        
    def discover_plugins(self) -> List[PluginEntryPoint]:
        """Discover plugins using entry points and file system scan."""
        self._discovered_plugins.clear()
        
        # Method 1: Entry points from installed packages
        self._discover_from_entry_points()
        
        # Method 2: File system scan for local plugins
        self._discover_from_filesystem()
        
        logger.info(f"Discovered {len(self._discovered_plugins)} plugins")
        return list(self._discovered_plugins.values())
    
    def _discover_from_entry_points(self) -> None:
        """Discover plugins from package entry points."""
        try:
            # Use importlib.metadata for Python 3.8+
            entry_points = importlib.metadata.entry_points()
            
            # Handle both old and new entry_points API
            if hasattr(entry_points, 'select'):
                # New API (Python 3.10+)
                plugin_entries = entry_points.select(group=self.plugin_group)
            else:
                # Old API (Python 3.8-3.9)
                plugin_entries = entry_points.get(self.plugin_group, [])
            
            for entry_point in plugin_entries:
                ep = PluginEntryPoint(
                    name=entry_point.name,
                    group=self.plugin_group,
                    module_name=entry_point.module,
                    attr_name=entry_point.attr,
                    dist_name=getattr(entry_point, 'dist', {}).get('name', 'unknown')
                )
                self._discovered_plugins[entry_point.name] = ep
                logger.debug(f"Found entry point plugin: {entry_point.name}")
                
        except Exception as e:
            logger.warning(f"Failed to discover entry point plugins: {e}")
    
    def _discover_from_filesystem(self) -> None:
        """Discover plugins from local filesystem."""
        # Look for plugins in common locations
        search_paths = [
            Path(__file__).parent / "builtin",  # Built-in plugins
            Path.cwd() / "plugins",             # Project local plugins
            Path.home() / ".strataregula" / "plugins",  # User plugins
        ]
        
        for search_path in search_paths:
            if search_path.exists() and search_path.is_dir():
                self._scan_directory(search_path)
    
    def _scan_directory(self, directory: Path) -> None:
        """Scan directory for Python plugin files."""
        for py_file in directory.glob("*.py"):
            if py_file.name.startswith("_"):
                continue  # Skip private files
                
            try:
                self._analyze_plugin_file(py_file)
            except Exception as e:
                logger.debug(f"Failed to analyze {py_file}: {e}")
    
    def _analyze_plugin_file(self, file_path: Path) -> None:
        """Analyze a Python file for plugin classes."""
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        
        if spec is None or spec.loader is None:
            return
            
        try:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find PatternPlugin subclasses
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PatternPlugin) and 
                    obj != PatternPlugin):
                    
                    plugin_name = getattr(obj, 'plugin_name', name.lower())
                    ep = PluginEntryPoint(
                        name=plugin_name,
                        group="filesystem",
                        module_name=f"file:{file_path}",
                        attr_name=name
                    )
                    self._discovered_plugins[plugin_name] = ep
                    logger.debug(f"Found filesystem plugin: {plugin_name}")
                    
        except Exception as e:
            logger.debug(f"Failed to load module from {file_path}: {e}")
    
    def load_plugin(self, name: str) -> PluginLoadResult:
        """Load a specific plugin by name."""
        if name in self._loaded_plugins:
            return PluginLoadResult(
                success=True, 
                plugin=self._loaded_plugins[name]
            )
        
        if name not in self._discovered_plugins:
            return PluginLoadResult(
                success=False,
                error=f"Plugin '{name}' not found in discovered plugins"
            )
        
        entry_point = self._discovered_plugins[name]
        
        try:
            # Handle filesystem plugins differently
            if entry_point.module_name.startswith("file:"):
                plugin_class = self._load_filesystem_plugin(entry_point)
            else:
                plugin_class = entry_point.load()
            
            # Instantiate the plugin
            plugin_instance = plugin_class()
            
            # Validate plugin
            if not hasattr(plugin_instance, 'info'):
                raise ValueError("Plugin must have 'info' property")
                
            self._loaded_plugins[name] = plugin_instance
            logger.info(f"Successfully loaded plugin: {name}")
            
            return PluginLoadResult(
                success=True,
                plugin=plugin_instance,
                entry_point=entry_point
            )
            
        except Exception as e:
            error_msg = f"Failed to load plugin '{name}': {e}"
            logger.error(error_msg)
            self._failed_loads[name] = error_msg
            
            return PluginLoadResult(
                success=False,
                error=error_msg,
                entry_point=entry_point
            )
    
    def _load_filesystem_plugin(self, entry_point: PluginEntryPoint) -> Type[PatternPlugin]:
        """Load plugin from filesystem."""
        file_path = Path(entry_point.module_name[5:])  # Remove 'file:' prefix
        module_name = f"strataregula_plugin_{file_path.stem}"
        
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load spec from {file_path}")
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        plugin_class = getattr(module, entry_point.attr_name)
        if not issubclass(plugin_class, PatternPlugin):
            raise ValueError(f"Class {entry_point.attr_name} is not a PatternPlugin")
            
        return plugin_class
    
    def load_all_plugins(self) -> List[PluginLoadResult]:
        """Load all discovered plugins."""
        results = []
        
        for plugin_name in self._discovered_plugins.keys():
            result = self.load_plugin(plugin_name)
            results.append(result)
            
        return results
    
    def get_loaded_plugins(self) -> Dict[str, PatternPlugin]:
        """Get all successfully loaded plugins."""
        return self._loaded_plugins.copy()
    
    def get_failed_loads(self) -> Dict[str, str]:
        """Get plugins that failed to load."""
        return self._failed_loads.copy()
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin."""
        if name in self._loaded_plugins:
            del self._loaded_plugins[name]
            logger.info(f"Unloaded plugin: {name}")
            return True
        return False
    
    def reload_plugin(self, name: str) -> PluginLoadResult:
        """Reload a plugin."""
        if name in self._loaded_plugins:
            self.unload_plugin(name)
        
        # Clear any previous failure records
        if name in self._failed_loads:
            del self._failed_loads[name]
            
        return self.load_plugin(name)
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """Get statistics about plugin loading."""
        return {
            "discovered": len(self._discovered_plugins),
            "loaded": len(self._loaded_plugins),
            "failed": len(self._failed_loads),
            "success_rate": len(self._loaded_plugins) / len(self._discovered_plugins) if self._discovered_plugins else 0
        }
"""
Plugin Configuration System - Manage plugin configurations and settings.
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
import jsonschema

logger = logging.getLogger(__name__)


@dataclass
class PluginConfigEntry:
    """Configuration entry for a single plugin."""
    enabled: bool = True
    priority: int = 50
    settings: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GlobalPluginConfig:
    """Global plugin system configuration."""
    auto_discover: bool = True
    lazy_loading: bool = True
    max_errors: int = 5
    error_cooldown: float = 300.0
    timeout: float = 30.0
    plugin_paths: List[str] = field(default_factory=lambda: [])
    entry_point_groups: List[str] = field(default_factory=lambda: ["strataregula.plugins"])
    
    # Performance settings
    enable_metrics: bool = True
    metrics_retention: int = 100
    
    # Security settings
    allow_filesystem_plugins: bool = True
    trusted_sources: List[str] = field(default_factory=list)


class ConfigValidator(ABC):
    """Abstract base for configuration validators."""
    
    @abstractmethod
    def validate(self, config_data: Dict[str, Any]) -> bool:
        """Validate configuration data."""
        pass
    
    @abstractmethod
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        pass


class JSONSchemaValidator(ConfigValidator):
    """JSON Schema-based configuration validator."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.errors: List[str] = []
    
    def validate(self, config_data: Dict[str, Any]) -> bool:
        """Validate using JSON Schema."""
        self.errors.clear()
        
        try:
            jsonschema.validate(config_data, self.schema)
            return True
        except jsonschema.ValidationError as e:
            self.errors.append(f"Schema validation error: {e.message}")
            return False
        except jsonschema.SchemaError as e:
            self.errors.append(f"Schema definition error: {e.message}")
            return False
    
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return self.errors.copy()


class PluginConfigManager:
    """Manages plugin configurations from various sources."""
    
    # Default JSON schema for plugin configurations
    DEFAULT_SCHEMA = {
        "type": "object",
        "properties": {
            "global": {
                "type": "object",
                "properties": {
                    "auto_discover": {"type": "boolean"},
                    "lazy_loading": {"type": "boolean"},
                    "max_errors": {"type": "integer", "minimum": 0},
                    "error_cooldown": {"type": "number", "minimum": 0},
                    "timeout": {"type": "number", "minimum": 0},
                    "plugin_paths": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "entry_point_groups": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "enable_metrics": {"type": "boolean"},
                    "metrics_retention": {"type": "integer", "minimum": 1},
                    "allow_filesystem_plugins": {"type": "boolean"},
                    "trusted_sources": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "plugins": {
                "type": "object",
                "patternProperties": {
                    ".*": {
                        "type": "object",
                        "properties": {
                            "enabled": {"type": "boolean"},
                            "priority": {"type": "integer", "minimum": 0},
                            "settings": {"type": "object"},
                            "dependencies": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "metadata": {"type": "object"}
                        }
                    }
                }
            }
        }
    }
    
    def __init__(self, config_paths: Optional[List[Union[str, Path]]] = None):
        self.config_paths = config_paths or self._get_default_config_paths()
        self.validator = JSONSchemaValidator(self.DEFAULT_SCHEMA)
        self.global_config = GlobalPluginConfig()
        self.plugin_configs: Dict[str, PluginConfigEntry] = {}
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        
        # Load configurations
        self.load_configurations()
    
    def _get_default_config_paths(self) -> List[Path]:
        """Get default configuration file paths."""
        paths = []
        
        # System-wide config
        if os.name == 'posix':
            paths.append(Path('/etc/strataregula/plugins.yaml'))
            paths.append(Path('/etc/strataregula/plugins.json'))
        
        # User config
        home = Path.home()
        paths.extend([
            home / '.strataregula' / 'plugins.yaml',
            home / '.strataregula' / 'plugins.json',
            home / '.config' / 'strataregula' / 'plugins.yaml',
            home / '.config' / 'strataregula' / 'plugins.json'
        ])
        
        # Project local config
        cwd = Path.cwd()
        paths.extend([
            cwd / 'strataregula.plugins.yaml',
            cwd / 'strataregula.plugins.json',
            cwd / '.strataregula' / 'plugins.yaml',
            cwd / '.strataregula' / 'plugins.json'
        ])
        
        # Environment variable override
        env_config = os.getenv('STRATAREGULA_PLUGIN_CONFIG')
        if env_config:
            paths.append(Path(env_config))
        
        return paths
    
    def load_configurations(self) -> None:
        """Load configurations from all available sources."""
        merged_config = {}
        
        for config_path in self.config_paths:
            if isinstance(config_path, str):
                config_path = Path(config_path)
            
            if config_path.exists() and config_path.is_file():
                try:
                    config_data = self._load_config_file(config_path)
                    if config_data:
                        # Validate configuration
                        if self.validator.validate(config_data):
                            merged_config = self._merge_configs(merged_config, config_data)
                            logger.info(f"Loaded plugin config from: {config_path}")
                        else:
                            logger.error(f"Invalid config in {config_path}: {self.validator.get_errors()}")
                except Exception as e:
                    logger.error(f"Failed to load config from {config_path}: {e}")
        
        # Apply merged configuration
        if merged_config:
            self._apply_configuration(merged_config)
        
        # Load environment variable overrides
        self._load_env_overrides()
    
    def _load_config_file(self, config_path: Path) -> Optional[Dict[str, Any]]:
        """Load configuration from a file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    logger.warning(f"Unsupported config file format: {config_path}")
                    return None
        except Exception as e:
            logger.error(f"Error reading config file {config_path}: {e}")
            return None
    
    def _merge_configs(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _validate_plugin_paths(self, paths: List[str]) -> List[str]:
        """Validate plugin paths for security issues."""
        safe_paths = []
        
        for path in paths:
            # Normalize path
            normalized_path = os.path.normpath(path)
            
            # Check for path traversal attempts
            if '..' in normalized_path:
                logger.warning(f"Rejecting plugin path with traversal attempt: {path}")
                continue
                
            # Check for absolute paths to sensitive directories
            sensitive_dirs = ['/etc', '/root', '/home', '/usr/bin', '/bin', '/sbin',
                            'C:\\Windows', 'C:\\Users', 'C:\\Program Files']
            
            if any(normalized_path.startswith(sensitive_dir) for sensitive_dir in sensitive_dirs):
                logger.warning(f"Rejecting plugin path to sensitive directory: {path}")
                continue
                
            # Only allow relative paths or paths within common safe directories
            if os.path.isabs(normalized_path):
                safe_base_dirs = ['plugins', 'extensions', '.strataregula']
                if not any(safe_base in normalized_path for safe_base in safe_base_dirs):
                    logger.warning(f"Rejecting absolute path to potentially unsafe directory: {path}")
                    continue
            
            safe_paths.append(normalized_path)
            
        return safe_paths
    
    def _apply_configuration(self, config_data: Dict[str, Any]) -> None:
        """Apply configuration data to internal structures."""
        # Apply global configuration
        if 'global' in config_data:
            global_data = config_data['global']
            for field_name, field_value in global_data.items():
                if hasattr(self.global_config, field_name):
                    # Apply security validation for sensitive fields
                    if field_name == 'plugin_paths':
                        field_value = self._validate_plugin_paths(field_value)
                    setattr(self.global_config, field_name, field_value)
        
        # Apply plugin-specific configurations
        if 'plugins' in config_data:
            plugins_data = config_data['plugins']
            for plugin_name, plugin_data in plugins_data.items():
                config_entry = PluginConfigEntry(
                    enabled=plugin_data.get('enabled', True),
                    priority=plugin_data.get('priority', 50),
                    settings=plugin_data.get('settings', {}),
                    dependencies=plugin_data.get('dependencies', []),
                    metadata=plugin_data.get('metadata', {})
                )
                self.plugin_configs[plugin_name] = config_entry
    
    def _load_env_overrides(self) -> None:
        """Load configuration overrides from environment variables."""
        env_prefix = "STRATAREGULA_PLUGIN_"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                
                # Global config overrides
                if config_key.startswith('global_'):
                    field_name = config_key[7:]  # Remove 'global_' prefix
                    if hasattr(self.global_config, field_name):
                        # Type conversion
                        field_type = type(getattr(self.global_config, field_name))
                        try:
                            if field_type == bool:
                                converted_value = value.lower() in ('true', '1', 'yes', 'on')
                            elif field_type in (int, float):
                                converted_value = field_type(value)
                            elif field_type == list:
                                converted_value = [item.strip() for item in value.split(',')]
                            else:
                                converted_value = value
                            
                            setattr(self.global_config, field_name, converted_value)
                            logger.debug(f"Applied env override: {field_name} = {converted_value}")
                        except (ValueError, TypeError) as e:
                            logger.error(f"Invalid env value for {key}: {e}")
    
    def get_global_config(self) -> GlobalPluginConfig:
        """Get global plugin configuration."""
        return self.global_config
    
    def get_plugin_config(self, plugin_name: str) -> PluginConfigEntry:
        """Get configuration for a specific plugin."""
        return self.plugin_configs.get(plugin_name, PluginConfigEntry())
    
    def set_plugin_config(self, plugin_name: str, config: PluginConfigEntry) -> None:
        """Set configuration for a specific plugin."""
        self.plugin_configs[plugin_name] = config
    
    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """Check if a plugin is enabled."""
        return self.get_plugin_config(plugin_name).enabled
    
    def get_plugin_priority(self, plugin_name: str) -> int:
        """Get plugin priority."""
        return self.get_plugin_config(plugin_name).priority
    
    def get_plugin_settings(self, plugin_name: str) -> Dict[str, Any]:
        """Get plugin settings."""
        return self.get_plugin_config(plugin_name).settings
    
    def get_plugin_dependencies(self, plugin_name: str) -> List[str]:
        """Get plugin dependencies."""
        return self.get_plugin_config(plugin_name).dependencies
    
    def get_enabled_plugins(self) -> List[str]:
        """Get list of enabled plugin names."""
        return [
            name for name, config in self.plugin_configs.items() 
            if config.enabled
        ]
    
    def get_plugins_by_priority(self) -> List[str]:
        """Get plugin names sorted by priority (highest first)."""
        return sorted(
            self.plugin_configs.keys(),
            key=lambda name: self.get_plugin_priority(name),
            reverse=True
        )
    
    def save_configuration(self, config_path: Optional[Path] = None) -> bool:
        """Save current configuration to file."""
        if config_path is None:
            # Use first writable path from config_paths
            config_path = self._find_writable_config_path()
        
        if config_path is None:
            logger.error("No writable configuration path found")
            return False
        
        try:
            # Prepare configuration data
            config_data = {
                "global": asdict(self.global_config),
                "plugins": {
                    name: asdict(config) 
                    for name, config in self.plugin_configs.items()
                }
            }
            
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write configuration
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config_data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_data, f, indent=2)
            
            logger.info(f"Saved plugin configuration to: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            return False
    
    def _find_writable_config_path(self) -> Optional[Path]:
        """Find the first writable configuration path."""
        # Try user config directory first
        candidates = [
            Path.home() / '.strataregula' / 'plugins.yaml',
            Path.cwd() / '.strataregula' / 'plugins.yaml'
        ]
        
        for path in candidates:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                # Test if writable
                test_file = path.parent / '.test_write'
                test_file.write_text('')
                test_file.unlink()
                return path
            except (PermissionError, OSError):
                continue
        
        return None
    
    def reload_configuration(self) -> None:
        """Reload configuration from all sources."""
        self.global_config = GlobalPluginConfig()
        self.plugin_configs.clear()
        self._config_cache.clear()
        self.load_configurations()
        logger.info("Plugin configuration reloaded")
    
    def validate_plugin_dependencies(self) -> Dict[str, List[str]]:
        """Validate plugin dependencies and return any issues."""
        issues = {}
        
        for plugin_name, config in self.plugin_configs.items():
            plugin_issues = []
            
            for dependency in config.dependencies:
                if dependency not in self.plugin_configs:
                    plugin_issues.append(f"Unknown dependency: {dependency}")
                elif not self.plugin_configs[dependency].enabled:
                    plugin_issues.append(f"Dependency disabled: {dependency}")
            
            if plugin_issues:
                issues[plugin_name] = plugin_issues
        
        return issues
# StrataRegula API Reference v0.2.0

Complete API documentation for StrataRegula Python library.

## Table of Contents
- [Core Classes](#core-classes)
- [Plugin System](#plugin-system)
- [Configuration](#configuration)
- [Utilities](#utilities)
- [Examples](#examples)

## Core Classes

### ConfigCompiler

Main configuration compiler class with plugin system integration.

```python
from strataregula.core.config_compiler import ConfigCompiler
```

#### Constructor

```python
ConfigCompiler(config: CompilationConfig = None, use_plugins: bool = True)
```

**Parameters:**
- `config` (CompilationConfig, optional): Compilation configuration settings
- `use_plugins` (bool): Enable/disable plugin system (default: True)

**Example:**
```python
# Default configuration with plugins
compiler = ConfigCompiler()

# Custom configuration
config = CompilationConfig(output_format='json', max_memory_mb=500)
compiler = ConfigCompiler(config=config)

# Disable plugins for performance
compiler = ConfigCompiler(use_plugins=False)
```

#### Methods

##### `compile_traffic_config(traffic_file, prefectures_file=None, output_file=None)`

Compile traffic configuration with pattern expansion.

**Parameters:**
- `traffic_file` (Path): Input YAML file with service patterns
- `prefectures_file` (Path, optional): YAML file defining region hierarchy  
- `output_file` (Path, optional): Output file path

**Returns:**
- `str`: Compiled configuration content

**Example:**
```python
from pathlib import Path

compiler = ConfigCompiler()
result = compiler.compile_traffic_config(
    traffic_file=Path('services.yaml'),
    prefectures_file=Path('regions.yaml'),
    output_file=Path('compiled_config.py')
)
```

##### `compile_large_config(input_file, output_file, progress_callback=None)`

Compile large configuration files with streaming and progress tracking.

**Parameters:**
- `input_file` (Path): Input configuration file
- `output_file` (Path): Output file path
- `progress_callback` (callable, optional): Progress callback function

**Example:**
```python
def progress_callback(current, total):
    print(f"Progress: {current}/{total} ({100*current/total:.1f}%)")

compiler.compile_large_config(
    input_file=Path('large_config.yaml'),
    output_file=Path('result.py'),
    progress_callback=progress_callback
)
```

### CompilationConfig

Configuration settings for the compilation process.

```python
from strataregula.core.config_compiler import CompilationConfig
```

#### Constructor

```python
CompilationConfig(
    input_format: str = "yaml",
    output_format: str = "python", 
    template_path: Optional[Path] = None,
    include_metadata: bool = True,
    include_provenance: bool = True,
    optimize_lookups: bool = True,
    chunk_size: int = 1024,
    max_memory_mb: int = 200
)
```

**Parameters:**
- `input_format`: Input format (`"yaml"`, `"json"`)
- `output_format`: Output format (`"python"`, `"json"`, `"yaml"`)
- `template_path`: Custom template file path
- `include_metadata`: Include metadata in output
- `include_provenance`: Include compilation provenance
- `optimize_lookups`: Enable lookup optimization
- `chunk_size`: Processing chunk size for large files
- `max_memory_mb`: Maximum memory usage in MB

**Example:**
```python
config = CompilationConfig(
    output_format='json',
    max_memory_mb=500,
    chunk_size=2048,
    include_metadata=True
)

compiler = ConfigCompiler(config=config)
```

### EnhancedPatternExpander

Advanced pattern expansion engine with caching and optimization.

```python
from strataregula.core.pattern_expander import EnhancedPatternExpander
```

#### Constructor

```python
EnhancedPatternExpander(
    hierarchy: RegionHierarchy = None,
    cache_size: int = 10000,
    plugins: EnhancedPluginManager = None
)
```

**Example:**
```python
expander = EnhancedPatternExpander(cache_size=20000)
result = expander.expand_pattern('web.*.response', {'value': 200})
```

#### Methods

##### `expand_pattern(pattern, context)`

Expand a single pattern with context.

**Parameters:**
- `pattern` (str): Pattern to expand (e.g., 'web.*.response')
- `context` (dict): Context data for expansion

**Returns:**
- `dict`: Expanded pattern mappings

##### `compile_to_static_mapping(patterns)`

Compile patterns to static mapping for O(1) lookups.

**Parameters:**
- `patterns` (dict): Dictionary of patterns to expand

**Returns:**
- `dict`: Compiled static mapping

**Example:**
```python
patterns = {
    'web.*.response': 200,
    'api.*.timeout': 30
}

mapping = expander.compile_to_static_mapping(patterns)
# Returns: {'web.frontend.response': 200, 'web.backend.response': 200, ...}
```

## Plugin System

### EnhancedPluginManager

Central plugin management system with lifecycle management.

```python
from strataregula.plugins.manager import EnhancedPluginManager
```

#### Constructor

```python
EnhancedPluginManager(config: PluginConfig = None)
```

**Example:**
```python
from strataregula.plugins.config import PluginConfigManager

config_manager = PluginConfigManager()
plugin_manager = EnhancedPluginManager(
    config=config_manager.get_global_config()
)
```

#### Methods

##### `discover_plugins()`

Discover and load plugins from entry points and file system.

```python
plugin_manager.discover_plugins()
```

##### `register_plugin(plugin)`

Register a plugin instance manually.

**Parameters:**
- `plugin`: Plugin instance implementing required interface

```python
from my_plugin import CustomPlugin

plugin_manager.register_plugin(CustomPlugin())
```

##### `get_plugin_by_name(name)`

Retrieve plugin by name.

**Parameters:**
- `name` (str): Plugin name

**Returns:**
- Plugin instance or None

```python
plugin = plugin_manager.get_plugin_by_name('timestamp')
```

### Base Plugin Classes

#### PatternPlugin

Base class for pattern expansion plugins.

```python
from strataregula.plugins.base import PatternPlugin

class MyPlugin(PatternPlugin):
    name = "my_plugin"
    version = "1.0.0"
    description = "Custom pattern expansion"
    
    def can_handle(self, pattern: str) -> bool:
        return "@custom" in pattern
    
    def expand(self, pattern: str, context) -> dict:
        # Implementation
        expanded = pattern.replace("@custom", "value")
        return {expanded: context.get('value', 1.0)}
```

**Required Methods:**
- `can_handle(pattern: str) -> bool`: Check if plugin can handle pattern
- `expand(pattern: str, context) -> dict`: Expand the pattern

**Optional Attributes:**
- `name` (str): Plugin name
- `version` (str): Plugin version  
- `description` (str): Plugin description
- `priority` (int): Plugin priority (higher = earlier execution)

#### HookPlugin

Base class for compilation pipeline hooks.

```python
from strataregula.plugins.base import HookPlugin

class MyHookPlugin(HookPlugin):
    name = "compilation_logger"
    
    async def pre_compilation(self, **kwargs):
        print(f"Starting compilation: {kwargs['traffic_file']}")
    
    async def pattern_discovered(self, patterns, **kwargs):
        print(f"Found {len(patterns)} patterns")
    
    async def pre_expand(self, patterns, **kwargs):
        print("Starting pattern expansion")
    
    async def post_expand(self, compiled_mapping, **kwargs):
        print(f"Expanded to {len(compiled_mapping)} mappings")
    
    async def compilation_complete(self, output_content, duration, **kwargs):
        print(f"Compilation completed in {duration:.2f}s")
```

**Available Hooks:**
- `pre_compilation(**kwargs)`: Before compilation starts
- `pattern_discovered(patterns, **kwargs)`: When patterns are discovered
- `pre_expand(patterns, **kwargs)`: Before pattern expansion
- `post_expand(compiled_mapping, **kwargs)`: After pattern expansion
- `compilation_complete(output_content, duration, **kwargs)`: After completion

## Configuration

### PluginConfigManager

Manages plugin configuration with cascading settings.

```python
from strataregula.plugins.config import PluginConfigManager

config_manager = PluginConfigManager()
global_config = config_manager.get_global_config()
plugin_config = config_manager.get_plugin_config('my_plugin')
```

#### Methods

##### `get_global_config()`

Get global plugin configuration.

**Returns:**
- `PluginConfig`: Global configuration object

##### `get_plugin_config(plugin_name)`

Get configuration for specific plugin.

**Parameters:**
- `plugin_name` (str): Name of plugin

**Returns:**
- `dict`: Plugin-specific configuration

##### `set_plugin_config(plugin_name, config)`

Set configuration for specific plugin.

**Parameters:**
- `plugin_name` (str): Name of plugin
- `config` (dict): Configuration dictionary

**Example:**
```python
config_manager.set_plugin_config('timestamp', {
    'format': '%Y%m%d_%H%M%S',
    'timezone': 'UTC'
})
```

## Utilities

### Compatibility Functions

Environment compatibility checking utilities.

```python
from strataregula.core.compatibility import (
    check_environment_compatibility,
    safe_import_psutil,
    get_python_info
)
```

#### `check_environment_compatibility()`

Check environment compatibility and return detailed report.

**Returns:**
- `dict`: Compatibility report with issues and warnings

**Example:**
```python
report = check_environment_compatibility()
if report['compatible']:
    print("Environment is compatible!")
else:
    for issue in report['issues']:
        print(f"Issue: {issue}")
```

#### `safe_import_psutil()`

Safely import psutil with fallback handling.

**Returns:**
- psutil module or None if not available

**Example:**
```python
psutil = safe_import_psutil()
if psutil:
    process = psutil.Process()
    memory_info = process.memory_info()
```

### Template Engine

Template rendering for output generation.

```python
from strataregula.core.config_compiler import TemplateEngine

engine = TemplateEngine()
output = engine.render('python', context_data)
```

## Examples

### Basic Usage

```python
from strataregula.core.config_compiler import ConfigCompiler
from pathlib import Path

# Simple compilation
compiler = ConfigCompiler()
result = compiler.compile_traffic_config(Path('config.yaml'))
print(result)
```

### Custom Configuration

```python
from strataregula.core.config_compiler import ConfigCompiler, CompilationConfig

# Custom configuration
config = CompilationConfig(
    output_format='json',
    include_metadata=True,
    max_memory_mb=300
)

compiler = ConfigCompiler(config=config)
result = compiler.compile_traffic_config(Path('config.yaml'))
```

### Plugin Development

```python
from strataregula.plugins.base import PatternPlugin
from strataregula.core.config_compiler import ConfigCompiler

# Custom plugin
class EnvironmentPlugin(PatternPlugin):
    name = "environment"
    
    def can_handle(self, pattern: str) -> bool:
        return "$" in pattern
    
    def expand(self, pattern: str, context) -> dict:
        import os
        # Replace $VAR with environment variable
        expanded = pattern.replace("$ENV", os.getenv("ENV", "dev"))
        return {expanded: context.get('value', 1.0)}

# Use plugin
compiler = ConfigCompiler()
compiler.plugin_manager.register_plugin(EnvironmentPlugin())

# Test with pattern containing $ENV
config = {"service.$ENV.timeout": 30}
result = compiler.compile_traffic_config(config)
```

### Hook Integration

```python
from strataregula.plugins.base import HookPlugin
from strataregula.core.config_compiler import ConfigCompiler

class MetricsPlugin(HookPlugin):
    def __init__(self):
        self.start_time = None
        self.pattern_count = 0
    
    async def pre_compilation(self, **kwargs):
        import time
        self.start_time = time.time()
        print("Starting metrics collection...")
    
    async def pattern_discovered(self, patterns, **kwargs):
        self.pattern_count = len(patterns)
        print(f"Discovered {self.pattern_count} patterns")
    
    async def compilation_complete(self, **kwargs):
        import time
        duration = time.time() - self.start_time
        print(f"Metrics: {self.pattern_count} patterns in {duration:.2f}s")

# Use hook plugin
compiler = ConfigCompiler()
compiler.plugin_manager.register_plugin(MetricsPlugin())
result = compiler.compile_traffic_config(Path('config.yaml'))
```

### Performance Optimization

```python
from strataregula.core.config_compiler import ConfigCompiler, CompilationConfig

# High-performance configuration
config = CompilationConfig(
    optimize_lookups=True,
    include_metadata=False,    # Reduce output size
    chunk_size=4096,          # Larger chunks for big files
    max_memory_mb=1000        # More memory for processing
)

# Disable plugins for maximum speed
compiler = ConfigCompiler(config=config, use_plugins=False)

# Compile large configuration
result = compiler.compile_large_config(
    input_file=Path('massive_config.yaml'),
    output_file=Path('optimized_output.py')
)
```

### Error Handling

```python
from strataregula.core.config_compiler import ConfigCompiler
from strataregula.core.compatibility import check_environment_compatibility
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    # Check environment first
    compatibility = check_environment_compatibility()
    if not compatibility['compatible']:
        print("Environment issues detected:")
        for issue in compatibility['issues']:
            print(f"  - {issue}")
    
    # Proceed with compilation
    compiler = ConfigCompiler()
    result = compiler.compile_traffic_config(Path('config.yaml'))
    
except FileNotFoundError:
    print("Configuration file not found")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

For more examples and detailed guides, see:
- [Documentation Index](../index.md) - Main documentation hub
- [Plugin Quick Start](../developer-guide/PLUGIN_QUICKSTART.md) - Plugin development tutorial  
- [CLI Reference](../user-guide/CLI_REFERENCE.md) - Command-line interface documentation
- [Migration Guide](../migration/MIGRATION_GUIDE.md) - Upgrading from v0.1.x
- [Examples](../examples/examples.md) - Real-world usage patterns
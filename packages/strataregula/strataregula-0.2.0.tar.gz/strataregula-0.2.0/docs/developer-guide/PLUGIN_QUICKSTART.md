# StrataRegula Plugin Development Quick Start

This guide helps you create your first StrataRegula plugin in minutes.

## 🚀 Quick Start (5 minutes)

### 1. Basic Plugin Template

Create a simple plugin that adds timestamps to patterns:

```python
# my_timestamp_plugin.py
from strataregula.plugins.base import PatternPlugin

class MyTimestampPlugin(PatternPlugin):
    name = "my_timestamp"
    version = "1.0.0"
    description = "Adds timestamps to patterns"
    
    def can_handle(self, pattern: str) -> bool:
        return "@now" in pattern
    
    def expand(self, pattern: str, context) -> dict:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        expanded = pattern.replace("@now", timestamp)
        return {expanded: context.get('value', 1.0)}
```

### 2. Test Your Plugin

```python
# test_my_plugin.py
from my_timestamp_plugin import MyTimestampPlugin

plugin = MyTimestampPlugin()
result = plugin.expand("service.@now.response", {"value": 200})
print(result)
# Output: {'service.20250826_143022.response': 200}
```

### 3. Use with StrataRegula

```python
from strataregula.core.config_compiler import ConfigCompiler
from strataregula.plugins.manager import EnhancedPluginManager

# Register your plugin
compiler = ConfigCompiler()
compiler.plugin_manager.register_plugin(MyTimestampPlugin())

# Create config with your pattern
config = {"services": {"api.@now.latency": 50}}
result = compiler.compile_traffic_config(config)
```

## 🎯 Hook-Based Plugins

For advanced pipeline integration:

```python
from strataregula.plugins.base import HookPlugin

class LoggingPlugin(HookPlugin):
    name = "compilation_logger"
    
    async def pre_compilation(self, **kwargs):
        print(f"🚀 Starting compilation: {kwargs['traffic_file']}")
    
    async def compilation_complete(self, **kwargs):
        duration = kwargs['duration']
        print(f"✅ Completed in {duration:.2f}s")
```

## 📦 Plugin Package Structure

For distributable plugins:

```
my_strataregula_plugin/
├── setup.py
├── my_plugin/
│   ├── __init__.py
│   └── plugin.py
└── tests/
    └── test_plugin.py
```

**setup.py** with entry points:
```python
from setuptools import setup

setup(
    name="my-strataregula-plugin",
    version="1.0.0",
    packages=["my_plugin"],
    entry_points={
        "strataregula.plugins": [
            "my_plugin = my_plugin.plugin:MyPlugin"
        ]
    }
)
```

## 🔧 Common Plugin Patterns

### Environment Variable Expansion
```python
class EnvPlugin(PatternPlugin):
    def can_handle(self, pattern: str) -> bool:
        return "$" in pattern
    
    def expand(self, pattern: str, context) -> dict:
        import os, re
        def replace_env(match):
            return os.getenv(match.group(1), match.group(0))
        
        expanded = re.sub(r'\$(\w+)', replace_env, pattern)
        return {expanded: context.get('value', 1.0)}
```

### Conditional Expansion
```python
class ConditionalPlugin(PatternPlugin):
    def can_handle(self, pattern: str) -> bool:
        return "?if:" in pattern
    
    def expand(self, pattern: str, context) -> dict:
        # Pattern: "service.?if:prod.logging"
        if "?if:prod" in pattern and context.get('env') == 'prod':
            expanded = pattern.replace("?if:prod", "prod")
            return {expanded: context.get('value', 1.0)}
        return {}
```

### Data Transformation
```python
class TransformPlugin(HookPlugin):
    async def post_expand(self, compiled_mapping, **kwargs):
        # Transform all service times by multiplying by factor
        factor = 1.5
        for key, value in compiled_mapping.items():
            if "service_time" in key:
                compiled_mapping[key] = value * factor
```

## 🧪 Testing Your Plugins

```python
import pytest
from your_plugin import YourPlugin

def test_plugin_basic():
    plugin = YourPlugin()
    assert plugin.can_handle("test.@special.pattern")
    
    result = plugin.expand("test.@special.pattern", {"value": 100})
    assert "test.expanded.pattern" in result
    assert result["test.expanded.pattern"] == 100

def test_plugin_integration():
    from strataregula.core.config_compiler import ConfigCompiler
    
    compiler = ConfigCompiler()
    compiler.plugin_manager.register_plugin(YourPlugin())
    
    # Test with real configuration
    config = {"test": {"service.@special.latency": 50}}
    result = compiler.compile_traffic_config(config)
    assert len(result) > 0
```

## 📖 Next Steps

1. **Read Full Documentation**: [API Reference](../api-reference/API_REFERENCE.md)
2. **Study Sample Plugins**: Check `strataregula/plugins/samples/`
3. **Plugin Configuration**: Learn about plugin configuration files
4. **Performance Optimization**: Best practices for high-performance plugins
5. **Error Handling**: Robust error handling patterns
6. **Async Patterns**: Advanced async plugin development

## 💡 Plugin Ideas

- **Database Integration**: Load patterns from databases
- **Template Engine**: Jinja2/Mustache template expansion  
- **Validation**: Pattern validation and linting
- **Metrics**: Custom metrics collection during compilation
- **Caching**: Intelligent caching for expensive expansions
- **API Integration**: Fetch patterns from REST APIs
- **Notification**: Send compilation results to Slack/email

## 🆘 Common Issues

**Plugin not discovered:**
```bash
# Check plugin registration
python -c "from strataregula.plugins.loader import PluginLoader; print(PluginLoader().discover_entry_point_plugins())"
```

**Import errors:**
- Ensure your plugin's dependencies are installed
- Check Python path and package structure
- Verify entry point configuration in setup.py

**Hook not called:**
- Confirm hook method name matches exactly (`pre_compilation`, `post_expand`, etc.)
- Check if plugin inherits from correct base class (`HookPlugin`)
- Verify plugin is registered with plugin manager

Ready to build awesome plugins? Start with the basic template above and expand from there! 🚀
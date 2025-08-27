# API Reference

Complete Python API documentation for StrataRegula v0.2.0.

## Contents

- **[API Reference](API_REFERENCE.md)** - Complete Python API documentation with examples

## Quick Reference

### Core Classes

- `ConfigCompiler` - Main compilation engine with plugin support
- `PatternExpander` - Core pattern expansion with hook integration  
- `PluginManager` - Plugin lifecycle management
- `PatternPlugin` - Base class for custom plugins

### Usage Examples

```python
from strataregula.core.config_compiler import ConfigCompiler

# Basic usage
compiler = ConfigCompiler()
result = compiler.compile_yaml_file("config.yaml")

# With plugins
compiler = ConfigCompiler(use_plugins=True)
result = compiler.compile_yaml_file("config.yaml")
```

## Quick Navigation

- [← Back to Documentation Index](../index.md)
- [Developer Guide](../developer-guide/)
- [Examples →](../examples/examples.md)
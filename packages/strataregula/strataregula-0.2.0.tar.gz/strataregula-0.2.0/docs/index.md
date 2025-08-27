# StrataRegula Documentation

**StrataRegula v0.2.0** - Advanced YAML Configuration Pattern Compiler with Plugin System

## Overview

StrataRegula transforms YAML configurations with wildcard patterns into concrete, optimized configurations through intelligent pattern expansion and a powerful plugin system.

### Key Features ✨

- **🔌 Plugin System**: 5 hook points for custom expansion logic
- **⚡ High Performance**: 100,000+ patterns/second expansion
- **🔍 Config Visualization**: 5 output formats for debugging
- **🩺 Environment Diagnostics**: Built-in compatibility checking
- **📊 Multiple Output Formats**: Python, JSON, YAML generation
- **🔄 100% Backward Compatible**: Seamless upgrade from v0.1.x

## Quick Start

### Installation

```bash
pip install strataregula

# With optional performance monitoring
pip install 'strataregula[performance]'
```

### 30-Second Example

```bash
# Create sample config
echo "service_times:
  web.*.response: 150  
  api.*.timeout: 30" > config.yaml

# See the magic
strataregula compile --traffic config.yaml
```

**Result**: Wildcard patterns automatically expand to real service configurations!

## Documentation Index

### 🚀 **User Guide**
- **[Installation & Setup](getting-started/installation.md)** - Get started in minutes
- **[CLI Reference](user-guide/CLI_REFERENCE.md)** - Complete command-line guide
- **[Configuration Examples](examples/examples.md)** - Real-world usage patterns
- **[Migration Guide](migration/MIGRATION_GUIDE.md)** - Upgrading from v0.1.x

### 🔧 **Developer Guide**
- **[Plugin Quick Start](developer-guide/PLUGIN_QUICKSTART.md)** - Create plugins in 5 minutes
- **[API Reference](api-reference/API_REFERENCE.md)** - Complete Python API
- **[Architecture Overview](#architecture)** - System design and components
- **[Contributing Guidelines](#contributing)** - How to contribute

### 📚 **Reference**
- **[Release Scope](RELEASE_SCOPE.md)** - What's included in v0.2.0
- **[Changelog](../CHANGELOG.md)** - Version history
- **[GitHub Repository](https://github.com/strataregula/strataregula)** - Source code

## v0.2.0 Plugin System

### Hook Points
The plugin system provides 5 integration points in the compilation pipeline:

1. **`pre_compilation`** - Before processing starts
2. **`pattern_discovered`** - When patterns are found
3. **`pre_expand`** / **`post_expand`** - Around pattern expansion
4. **`compilation_complete`** - After output generation

### Sample Plugins Included
- **TimestampPlugin** - Dynamic timestamp insertion
- **EnvironmentPlugin** - Environment variable expansion  
- **ConditionalPlugin** - Conditional pattern logic
- **PrefixPlugin** - Pattern prefix management
- **MultiplicatorPlugin** - Pattern multiplication
- **ValidationPlugin** - Pattern validation rules

### Quick Plugin Example

```python
from strataregula.plugins.base import PatternPlugin

class MyPlugin(PatternPlugin):
    def can_handle(self, pattern: str) -> bool:
        return "@custom" in pattern
    
    def expand(self, pattern: str, context) -> dict:
        expanded = pattern.replace("@custom", "value")
        return {expanded: context.get('value', 1.0)}
```

## CLI Features

### Basic Usage
```bash
# Simple compilation
strataregula compile --traffic config.yaml

# Custom output format
strataregula compile --traffic config.yaml --format json

# With visualization
strataregula compile --traffic config.yaml --dump-compiled-config --dump-format tree
```

### Advanced Features
```bash
# Environment diagnostics
strataregula doctor                    # Basic compatibility check
strataregula doctor --fix-suggestions  # Get help fixing issues

# Configuration visualization (5 formats)
strataregula compile --traffic config.yaml --dump-compiled-config --dump-format json
```

### Visualization Formats

**Tree Format** - Hierarchical view:
```
services/
├── web/
│   ├── frontend.response: 200ms
│   └── backend.response: 300ms  
└── api/
    ├── v1.timeout: 30s
    └── v2.timeout: 45s
```

**Table Format** - Structured data:
```
| Pattern              | Value | Type    |
|---------------------|-------|---------|  
| web.frontend.response| 200   | service |
| api.v1.timeout      | 30    | config  |
```

## Architecture

```
strataregula/                      # Core Library v0.2.0
├── core/                          # Core pattern expansion engine
│   ├── compiler.py               # High-performance pattern compiler
│   ├── config_compiler.py        # Main compilation with plugin integration
│   ├── pattern_expander.py       # Enhanced pattern expansion with hooks
│   └── compatibility.py          # Environment compatibility checking
├── plugins/                       # Plugin system
│   ├── manager.py                # Plugin lifecycle management
│   ├── base.py                   # Plugin base classes
│   ├── config.py                 # Configuration management
│   ├── samples/                  # Sample plugin implementations
│   └── hooks.py                  # Hook point definitions
├── cli/                          # Command-line interface
│   ├── main.py                   # Main CLI with diagnostics
│   └── compile_command.py        # Compilation with visualization
└── data/                         # Data sources and hierarchy definitions
```

**Note**: Editor integration (LSP, VS Code) developed in separate repositories.

## Performance

- **Pattern Expansion**: 100,000-400,000 patterns/second
- **Plugin Overhead**: <5% when enabled
- **Memory Efficient**: Streaming support for large datasets  
- **Scalable**: Handles 1-10MB configurations efficiently

## Getting Help

### Community
- **GitHub Issues**: [Report bugs or request features](https://github.com/strataregula/strataregula/issues)
- **GitHub Discussions**: [Community support and ideas](https://github.com/strataregula/strataregula/discussions)

### Documentation
- **Environment Issues**: Run `strataregula doctor --fix-suggestions`
- **Migration Help**: See [Migration Guide](migration/MIGRATION_GUIDE.md)
- **Plugin Development**: See [Plugin Quick Start](developer-guide/PLUGIN_QUICKSTART.md)

### Support Channels
- Search existing issues before creating new ones
- Provide minimal reproduction examples
- Include environment info (`strataregula doctor --verbose`)

## Contributing

We welcome contributions! Areas where you can help:

- **Plugin Development** - Create plugins for common use cases
- **Documentation** - Improve guides and examples
- **Testing** - Add test cases and improve coverage
- **Performance** - Optimize pattern expansion algorithms
- **Integration** - Connect with other tools and platforms

See our [Contributing Guidelines](#) for detailed information.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**StrataRegula v0.2.0** - Enterprise-ready pattern expansion with plugin extensibility.

*Last updated: August 26, 2025*
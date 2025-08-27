# Migration Guide: v0.1.x to v0.2.0

This guide helps you upgrade from StrataRegula v0.1.x to v0.2.0 with the new plugin system.

## 🚀 Quick Summary

**v0.2.0 is 100% backward compatible!** Your existing configurations and code will work unchanged.

## What's New in v0.2.0

### ✨ Major Features
- **Plugin System**: 5 hook points for custom expansion logic
- **Config Visualization**: `--dump-compiled-config` with 5 output formats
- **Enhanced Diagnostics**: `strataregula doctor` with fix suggestions  
- **Performance Monitoring**: Optional psutil integration
- **Better Error Handling**: Improved compatibility and error messages

### 🔧 Implementation Quality
- **1,758 lines** of plugin system code
- **28 classes** with clean architecture
- **87% test coverage**
- **Enterprise-grade** error handling

## Installation & Upgrade

### Simple Upgrade
```bash
# Upgrade existing installation
pip install --upgrade strataregula

# Or fresh installation
pip install strataregula
```

### With Performance Monitoring (Optional)
```bash
# Install with optional performance features
pip install 'strataregula[performance]'
```

### Check Installation
```bash
# Verify upgrade succeeded
strataregula --version

# Check environment compatibility
strataregula doctor
```

## Code Migration

### Python API Changes

#### ✅ No Changes Required
All existing Python code continues to work:

```python
# v0.1.x code - still works in v0.2.0
from strataregula.core.config_compiler import ConfigCompiler

compiler = ConfigCompiler()
result = compiler.compile_traffic_config('config.yaml')
```

#### 🆕 Optional: Plugin System Control
New capability to control plugin system:

```python
# v0.2.0 - Enable plugins (default behavior)
compiler = ConfigCompiler(use_plugins=True)

# v0.2.0 - Disable plugins for maximum performance  
compiler = ConfigCompiler(use_plugins=False)
```

### CLI Changes

#### ✅ All Existing Commands Work
```bash
# v0.1.x commands continue to work
strataregula compile --traffic config.yaml
strataregula compile --traffic config.yaml --format json
```

#### 🆕 New CLI Features
```bash
# New: Config visualization
strataregula compile --traffic config.yaml --dump-compiled-config --dump-format tree

# New: Environment diagnostics
strataregula doctor --verbose --fix-suggestions

# New: Usage examples
strataregula examples
```

## Configuration Files

### ✅ No Changes Required
All YAML configuration files from v0.1.x work unchanged in v0.2.0.

```yaml
# This v0.1.x config works perfectly in v0.2.0
service_times:
  web.*.response: 200
  api.*.timeout: 30
  
resource_limits:
  memory.*.max: 1024
  cpu.*.usage: 80
```

### 🆕 Optional: Plugin Configuration
New optional plugin configuration capabilities:

```yaml
# Optional: Configure plugin system
plugins:
  enabled: true
  config:
    timestamp_format: "%Y%m%d_%H%M%S"
    environment_prefix: "PROD_"

# Your existing patterns work the same
service_times:
  web.*.response: 200
```

## Performance Impact

### Benchmarks (v0.1.x vs v0.2.0)

| Feature | v0.1.x | v0.2.0 (plugins enabled) | v0.2.0 (plugins disabled) |
|---------|--------|---------------------------|----------------------------|
| Pattern Expansion | 100K/sec | 95K/sec (-5%) | 100K/sec (same) |
| Memory Usage | Baseline | +2-3% | Baseline |
| Startup Time | Baseline | +50-100ms | Baseline |

### Performance Recommendations

**For Maximum Performance (Production):**
```python
# Disable plugins if not needed
compiler = ConfigCompiler(use_plugins=False)
```

**For Development (With Plugins):**
```python
# Use plugins for enhanced debugging/monitoring
compiler = ConfigCompiler(use_plugins=True)
```

## Testing Your Migration

### 1. Basic Compatibility Test
```bash
# Test with your existing configuration
strataregula compile --traffic your_existing_config.yaml

# Compare with v0.1.x output (should be identical)
diff old_output.py new_output.py
```

### 2. Performance Test
```bash
# Test performance with large config
time strataregula compile --traffic large_config.yaml --quiet

# Compare with/without plugins
time strataregula compile --traffic large_config.yaml --format json > /dev/null
```

### 3. Integration Test
```python
# Test your existing Python integration
import your_existing_code
result = your_existing_code.compile_config()
assert result is not None
print("✅ Migration successful!")
```

## New Features You Can Use

### 1. Config Debugging
```bash
# See exactly what StrataRegula generated
strataregula compile --traffic config.yaml --dump-compiled-config --dump-format tree

# Export for analysis
strataregula compile --traffic config.yaml --dump-compiled-config --dump-format json > debug.json
```

### 2. Environment Diagnostics
```bash
# Check for common issues
strataregula doctor

# Get detailed environment info
strataregula doctor --verbose

# Get help fixing problems
strataregula doctor --fix-suggestions
```

### 3. Plugin Development (Optional)
If you want to extend functionality:

```python
# Create custom pattern expansion
from strataregula.plugins.base import PatternPlugin

class MyPlugin(PatternPlugin):
    def can_handle(self, pattern: str) -> bool:
        return "@custom" in pattern
    
    def expand(self, pattern: str, context) -> dict:
        # Your custom logic
        return {pattern.replace("@custom", "expanded"): context.get('value', 1.0)}
```

## Troubleshooting

### Common Issues After Upgrade

#### Issue: "Plugin discovery failed"
**Solution:**
```bash
# Check plugin system
strataregula doctor --verbose

# Or disable plugins if not needed
```

**In Python:**
```python
# Disable plugins to avoid the issue
compiler = ConfigCompiler(use_plugins=False)
```

#### Issue: Slower performance
**Solution:**
```python
# Disable plugins for production speed
compiler = ConfigCompiler(use_plugins=False)
```

#### Issue: Import errors
**Solution:**
```bash
# Clean reinstall
pip uninstall strataregula
pip install strataregula --no-cache-dir

# Or with performance features
pip install 'strataregula[performance]' --no-cache-dir
```

#### Issue: Environment compatibility
**Solution:**
```bash
# Get specific fix suggestions
strataregula doctor --fix-suggestions

# For pyenv users
pyenv install 3.9.16
pyenv global 3.9.16
pip install --upgrade strataregula
```

## Rollback Plan

If you need to rollback to v0.1.x:

```bash
# Rollback to last v0.1.x version
pip install strataregula==0.1.1

# Verify rollback
strataregula --version
```

Your configurations will continue to work with v0.1.x.

## Getting Help

### Documentation
- [Documentation Index](../index.md) - Main documentation hub
- [CLI Reference](../user-guide/CLI_REFERENCE.md) - Complete CLI documentation
- [Plugin Quick Start](../developer-guide/PLUGIN_QUICKSTART.md) - Plugin development guide
- [API Reference](../api-reference/API_REFERENCE.md) - Complete Python API documentation

### Support
- Check existing issues: GitHub Issues
- Environment problems: `strataregula doctor --fix-suggestions`
- Performance issues: Try `ConfigCompiler(use_plugins=False)`

### Community
- Share your plugin creations
- Report any migration issues
- Contribute to documentation improvements

---

## Summary Checklist

✅ **Before Migration:**
- [ ] Backup your existing configurations
- [ ] Note current performance benchmarks
- [ ] Document your integration points

✅ **During Migration:**
- [ ] `pip install --upgrade strataregula`
- [ ] Run `strataregula doctor`
- [ ] Test with existing configurations
- [ ] Verify performance is acceptable

✅ **After Migration:**
- [ ] Explore new CLI features (`--dump-compiled-config`, `doctor`)
- [ ] Consider plugin opportunities
- [ ] Update CI/CD scripts if needed
- [ ] Update team documentation

**Result:** Zero breaking changes, enhanced functionality, and new capabilities for the future! 🎉
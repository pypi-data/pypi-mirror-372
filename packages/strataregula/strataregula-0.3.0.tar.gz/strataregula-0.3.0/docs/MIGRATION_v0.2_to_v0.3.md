# Migration Guide: StrataRegula v0.2.x → v0.3.0

This guide helps you migrate from StrataRegula v0.2.x to v0.3.0, which introduces the new Kernel Architecture and Config Interning system.

## 📋 Migration Timeline

| Version | Status | Action Required |
|---------|--------|-----------------|
| **v0.3.0** | ✅ Full Compatibility | Optional migration with warnings |
| **v0.4.0** | ⚠️ Maintained | Strong deprecation warnings |
| **v0.5.0** | 🚨 Explicit Opt-in | Legacy imports require flag |
| **v1.0.0** | ❌ Removed | Must migrate to new API |

## 🚀 Quick Migration

### Before (v0.2.x)
```python
from strataregula import Engine
from strataregula import ConfigLoader, TemplateEngine

# Old API
engine = Engine(config_path="app.yaml", template_dir="templates")
result = engine.compile()
valid = engine.validate(strict=True)
metrics = engine.get_metrics()
```

### After (v0.3.0+)
```python
from strataregula.kernel import Kernel
from strataregula.core.config_compiler import ConfigCompiler

# New API
kernel = Kernel()
result = kernel.compile("app.yaml")
kernel.validate("app.yaml")
stats = kernel.get_stats()
```

## 📚 API Migration Reference

### Engine → Kernel

| v0.2.x Method | v0.3.0+ Equivalent | Notes |
|---------------|-------------------|-------|
| `Engine(config_path=...)` | `Kernel()` + `compile(path)` | Kernel is stateless |
| `engine.compile()` | `kernel.compile(path)` | Path passed to method |
| `engine.validate(strict=True)` | `kernel.validate(path)` | Always strict |
| `engine.expand_pattern(...)` | `kernel.expand(...)` | Improved pattern syntax |
| `engine.get_metrics()` | `kernel.get_stats()` | Enhanced stats format |
| `engine.service_time(...)` | Use benchmarks instead | Dedicated performance tools |

### ConfigLoader → ConfigCompiler

| v0.2.x Method | v0.3.0+ Equivalent | Notes |
|---------------|-------------------|-------|
| `ConfigLoader(search_paths)` | `ConfigCompiler()` | Auto-discovery |
| `loader.load(path)` | Built into Kernel | Automatic loading |
| `loader.merge(configs...)` | Config composition | YAML anchors/references |

### TemplateEngine → Integrated

| v0.2.x Feature | v0.3.0+ Equivalent | Notes |
|----------------|-------------------|-------|
| `TemplateEngine(template_dir)` | Automatic template discovery | No separate engine |
| `engine.render(template, ctx)` | Pattern expansion | Integrated into compilation |

## 🔄 Step-by-Step Migration

### Step 1: Install v0.3.0 with Legacy Support
```bash
pip install strataregula>=0.3.0
```

### Step 2: Test Existing Code
Your v0.2.x code should work immediately with deprecation warnings:

```python
import warnings
# Capture warnings during testing
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    
    # Your existing v0.2.x code
    from strataregula import Engine
    engine = Engine(config_path="config.yaml")
    result = engine.compile()
    
    # Check for deprecation warnings
    deprecation_warnings = [
        warning for warning in w 
        if issubclass(warning.category, DeprecationWarning)
    ]
    print(f"Found {len(deprecation_warnings)} deprecation warnings")
```

### Step 3: Gradual Migration

#### 3a. Replace Core Classes
```python
# Before
from strataregula import Engine
engine = Engine(config_path="app.yaml")

# After  
from strataregula.kernel import Kernel
kernel = Kernel()
```

#### 3b. Update Method Calls
```python
# Before
result = engine.compile()
valid = engine.validate(strict=True)

# After
result = kernel.compile("app.yaml")
kernel.validate("app.yaml")  # Always strict
```

#### 3c. Update Metrics Access
```python
# Before
metrics = engine.get_metrics()
compile_count = metrics["compile_count"]
cache_hits = metrics["cache_hits"]

# After
stats = kernel.get_stats()
compilations = stats["compilations"] 
cache_hits = stats["cache_hits"]
```

### Step 4: Remove Template Engine Usage
```python
# Before
from strataregula import TemplateEngine
template_engine = TemplateEngine(template_dir="templates")
rendered = template_engine.render("service.j2", context)

# After - Templates are automatic
kernel = Kernel()
result = kernel.compile("config.yaml")  # Templates resolved automatically
```

### Step 5: Update Configuration Files

#### Enhanced YAML Features (Optional)
```yaml
# v0.3.0 supports enhanced YAML with anchors
defaults: &defaults
  timeout: 30
  retries: 3

services:
  api:
    <<: *defaults
    port: 8080
  
  worker:
    <<: *defaults  
    queue: tasks
```

### Step 6: Performance Optimization (Optional)

Take advantage of new performance features:

```python
# Config Interning - automatic memory optimization
kernel = Kernel()

# Multiple compilations reuse cached configs
result1 = kernel.compile("config.yaml")  # Cache miss
result2 = kernel.compile("config.yaml")  # Cache hit!

# Check interning stats
stats = kernel.get_stats()
print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")
print(f"Memory saved: {stats['memory_saved_bytes'] / 1024:.1f} KB")
```

## 🧪 Testing Your Migration

### Automated Compatibility Tests

Create tests to ensure migration works:

```python
import pytest
import warnings
from strataregula.kernel import Kernel

def test_migration_equivalence():
    """Test that v0.2.x and v0.3.0 produce same results."""
    
    # v0.2.x approach (with warnings suppressed for test)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from strataregula.legacy import Engine
        old_engine = Engine(config_path="test.yaml")
        old_result = old_engine.compile()
    
    # v0.3.0 approach
    new_kernel = Kernel()
    new_result = new_kernel.compile("test.yaml")
    
    # Results should be equivalent
    assert old_result == new_result

def test_deprecation_warnings():
    """Ensure v0.2.x APIs produce warnings."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        from strataregula.legacy import Engine
        engine = Engine()
        
        assert len(w) >= 1
        assert issubclass(w[0].category, DeprecationWarning)
```

### Performance Comparison
```python
import time
from strataregula.kernel import Kernel
from strataregula.legacy import Engine

def benchmark_migration():
    """Compare performance between v0.2.x and v0.3.0."""
    config_path = "large_config.yaml"
    
    # v0.2.x timing
    start = time.time()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        old_engine = Engine(config_path=config_path)
        for _ in range(10):
            old_engine.compile()
    old_time = time.time() - start
    
    # v0.3.0 timing
    start = time.time() 
    kernel = Kernel()
    for _ in range(10):
        kernel.compile(config_path)
    new_time = time.time() - start
    
    print(f"v0.2.x: {old_time:.2f}s")
    print(f"v0.3.0: {new_time:.2f}s") 
    print(f"Speedup: {old_time/new_time:.1f}x")
```

## ⚠️ Breaking Changes

### Removed Features
- `template_dir` parameter - templates auto-discovered
- `search_paths` configuration - automatic path resolution  
- `output_format` parameter - format inferred from extension
- `service_time()` method - use dedicated benchmarks

### Behavioral Changes
- **Validation**: Always strict (no `strict=False` option)
- **Caching**: Enabled by default for performance
- **Memory**: Config interning reduces memory usage
- **Error Handling**: More detailed error messages

### Configuration Changes
- **YAML anchors**: Now fully supported
- **Include paths**: Automatic discovery
- **Schema validation**: Enhanced type checking

## 🚨 Common Migration Issues

### Issue 1: Import Errors
```python
# This will fail in v1.0.0
from strataregula import Engine  

# Solution: Update imports
from strataregula.kernel import Kernel
```

### Issue 2: Method Signatures
```python
# v0.2.x
engine = Engine(config_path="app.yaml")
result = engine.compile()

# v0.3.0 - path moved to compile()
kernel = Kernel()
result = kernel.compile("app.yaml")
```

### Issue 3: Metrics Format
```python
# v0.2.x format
metrics = engine.get_metrics()
count = metrics["compile_count"]

# v0.3.0 format  
stats = kernel.get_stats()
count = stats["compilations"]
```

### Issue 4: Template Directory
```python
# v0.2.x
engine = Engine(template_dir="/templates")

# v0.3.0 - templates auto-discovered
kernel = Kernel()  # Templates found automatically
```

## 🎯 Migration Checklist

- [ ] **Test with v0.3.0**: Existing code works with warnings
- [ ] **Update imports**: Replace `strataregula.*` with specific modules  
- [ ] **Migrate Engine**: Replace `Engine` with `Kernel`
- [ ] **Update method calls**: Move config path to compile method
- [ ] **Fix metrics access**: Update to new stats format
- [ ] **Remove template engine**: Use automatic template discovery
- [ ] **Test equivalence**: Verify same results as v0.2.x
- [ ] **Check performance**: Measure improvement from new features
- [ ] **Update documentation**: Reflect new API usage
- [ ] **Plan timeline**: Schedule complete migration before v1.0.0

## 📞 Getting Help

- **Deprecation warnings**: Read the specific guidance in each warning
- **API reference**: Check updated documentation 
- **Examples**: See `examples/` directory for v0.3.0 patterns
- **Issues**: Report migration problems on GitHub
- **Discussions**: Ask questions in GitHub Discussions

## 📈 Benefits of Migrating

### Performance Improvements
- **50x memory reduction** with config interning
- **3-5x faster compilation** with kernel architecture  
- **Better caching** reduces redundant work

### Enhanced Features
- **Full YAML anchors** and references support
- **Improved error messages** with context
- **Better validation** with detailed feedback
- **Automatic template discovery**

### Future-Proofing  
- **v1.0.0 compatibility** - no more breaking changes
- **Performance optimizations** continue in each release
- **New features** only available in v0.3.0+ API

## 🗓️ Version Support Policy

| Version Range | Support Level | End of Life |
|---------------|---------------|-------------|
| v0.2.x | Legacy only | v1.0.0 release |
| v0.3.x | Full support | 18 months |
| v0.4.x | Latest features | 24 months |

**Recommendation**: Migrate to v0.3.0+ API as soon as possible to benefit from ongoing improvements and ensure future compatibility.
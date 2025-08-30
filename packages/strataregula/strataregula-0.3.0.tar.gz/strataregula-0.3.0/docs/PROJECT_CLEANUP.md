# Project Cleanup - 散らかしたおもちゃを整理

## 📁 File Organization

### Created Files (要整理)
```
Current Location → Target Location
```

#### 🎯 Core Pattern Libraries
```
micro_patterns.py           → examples/patterns/micro_patterns.py
advanced_patterns.py        → examples/patterns/advanced_patterns.py  
micro_tests.py             → tests/patterns/micro_tests.py
pattern_benchmark.py        → benchmarks/pattern_benchmark.py
pattern_summary.md          → docs/PATTERN_LIBRARY.md
```

#### ⚡ Performance Optimization
```
optimized_benchmark.py      → benchmarks/optimized_benchmark.py
cpu_locality_optimization.py → benchmarks/cpu_locality.py
functional_speedup_demo.py  → benchmarks/functional_speedup.py
precompiled_philosophy.py   → docs/examples/philosophy_demo.py
```

#### 🏆 Golden Metrics
```
golden_fix.py              → strataregula/golden/optimized.py
golden_metrics_diagnosis.py → tools/diagnose_golden_metrics.py
```

#### 📊 Documentation
```
VISION.md                  → ✅ Already in correct location
docs/GOLDEN_METRICS_GUARD.md → ✅ Already in correct location
```

## 🧹 Cleanup Actions

### 1. Create Directory Structure
```bash
mkdir -p examples/patterns
mkdir -p benchmarks
mkdir -p tools
mkdir -p docs/examples
```

### 2. Move Pattern Files
```bash
mv micro_patterns.py examples/patterns/
mv advanced_patterns.py examples/patterns/
mv micro_tests.py tests/patterns/
mv pattern_benchmark.py benchmarks/
```

### 3. Move Performance Files  
```bash
mv optimized_benchmark.py benchmarks/
mv cpu_locality_optimization.py benchmarks/cpu_locality.py
mv functional_speedup_demo.py benchmarks/functional_speedup.py
mv precompiled_philosophy.py docs/examples/philosophy_demo.py
```

### 4. Move Golden Metrics Tools
```bash
mv golden_fix.py strataregula/golden/optimized.py
mv golden_metrics_diagnosis.py tools/diagnose_golden_metrics.py
```

### 5. Update Imports
Update all import statements in moved files to reflect new locations.

## 📋 Final Directory Structure

```
strataregula/
├── docs/
│   ├── VISION.md                      ✅ Project philosophy
│   ├── GOLDEN_METRICS_GUARD.md        ✅ Golden Metrics docs
│   ├── PATTERN_LIBRARY.md             📝 Pattern documentation
│   └── examples/
│       └── philosophy_demo.py         📝 Philosophy demonstration
├── examples/
│   └── patterns/
│       ├── micro_patterns.py          📝 25 core patterns  
│       └── advanced_patterns.py       📝 25 advanced patterns
├── benchmarks/
│   ├── pattern_benchmark.py           📝 Pattern performance tests
│   ├── optimized_benchmark.py         📝 Optimization comparisons
│   ├── cpu_locality.py                📝 CPU locality demos
│   └── functional_speedup.py          📝 Functional programming speedup
├── tests/
│   └── patterns/
│       └── micro_tests.py              📝 Comprehensive pattern tests
├── tools/
│   └── diagnose_golden_metrics.py     📝 Golden Metrics diagnosis
└── strataregula/golden/
    └── optimized.py                    📝 Ultra-optimized implementation
```

## 🎯 Benefits of Organization

### 1. Clear Purpose
- `examples/` - Demonstration code
- `benchmarks/` - Performance analysis  
- `tools/` - Utility scripts
- `tests/` - Test suites
- `docs/` - Documentation

### 2. Easy Discovery
- Developers know where to find pattern examples
- Performance engineers can locate benchmarks
- Documentation is centralized

### 3. Maintainability
- Related files are grouped together
- Import paths are logical
- CI can target specific directories

## 🚀 Post-Cleanup Tasks

### 1. Update README.md
Add sections pointing to new directory structure:
```markdown
## 📚 Examples
- Pattern Library: `examples/patterns/`  
- Performance Demos: `benchmarks/`

## 🔧 Tools
- Golden Metrics Diagnosis: `tools/`

## 📖 Documentation  
- Project Vision: `docs/VISION.md`
- Golden Metrics: `docs/GOLDEN_METRICS_GUARD.md`
```

### 2. Update CI Configuration
```yaml
# Test different components separately
- name: Test Patterns
  run: python -m pytest tests/patterns/

- name: Run Benchmarks  
  run: python benchmarks/pattern_benchmark.py
```

### 3. Create Index Files
Create `__init__.py` files with proper exports in each directory.

## ✅ Completion Checklist

- [ ] Create directory structure
- [ ] Move files to appropriate locations  
- [ ] Update import statements
- [ ] Update README.md
- [ ] Update CI configuration
- [ ] Create index files
- [ ] Test all moved files work correctly
- [ ] Remove original scattered files

---

**Result**: Clean, organized project structure that reflects the evolution from config compilation to comprehensive performance optimization system.
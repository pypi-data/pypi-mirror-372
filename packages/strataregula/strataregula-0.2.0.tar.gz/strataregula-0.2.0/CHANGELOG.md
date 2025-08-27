# Changelog

All notable changes to strataregula will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-08-26 - Plugin System Release

### Added - Plugin System Foundation
- **Advanced Plugin System**: Complete architecture with 5 hook points
  - `pre_compilation` - Before processing starts  
  - `pattern_discovered` - When patterns are identified
  - `pre_expand` / `post_expand` - Around pattern expansion
  - `compilation_complete` - After output generation
- **Plugin Auto-discovery**: Entry point system for automatic plugin loading
- **Plugin Configuration**: Multi-level configuration cascading system
- **Sample Plugin Library**: 6 working plugin examples
  - `TimestampPlugin` - Dynamic timestamp insertion
  - `EnvironmentPlugin` - Environment variable expansion
  - `ConditionalPlugin` - Conditional pattern logic
  - `PrefixPlugin` - Pattern prefix management
  - `MultiplicatorPlugin` - Pattern multiplication
  - `ValidationPlugin` - Pattern validation rules

### Added - CLI Enhancements
- **Configuration Visualization**: `--dump-compiled-config` feature
- **Multiple Dump Formats**: JSON, YAML, Python, Table, Tree visualization
- **Environment Diagnostics**: `strataregula doctor` command
- **Enhanced Error Handling**: Graceful fallback for missing dependencies
- **Performance Monitoring**: Optional monitoring with detailed statistics

### Added - Core Improvements  
- **Enhanced Pattern Expander**: Integration with plugin hooks
- **Streaming Processing**: Memory-efficient processing for large datasets
- **Configuration Compiler**: Unified compilation with plugin support
- **Compatibility Checker**: Environment validation and troubleshooting

### Changed
- **Plugin Integration**: All core components now support plugin hooks
- **Memory Management**: Improved memory efficiency with streaming
- **Error Handling**: Enhanced error messages and recovery
- **CLI Interface**: Richer output with better formatting
- **Performance**: Optimized processing with caching improvements

### Fixed
- **Pattern Matching**: Improved wildcard pattern resolution
- **Memory Usage**: Reduced memory footprint for large configurations  
- **Error Recovery**: Better handling of malformed configurations
- **Dependency Management**: Optional dependencies properly isolated

### Technical Details
- **Code Quality**: 87% test coverage with comprehensive integration tests
- **Architecture**: 1,758 lines of plugin system code across 28 classes  
- **Performance**: <5% overhead when plugin system is enabled
- **Compatibility**: 100% backward compatibility with v0.1.x

## [0.1.1] - Initial Release

### Added
- Core pattern expansion engine with wildcard support
- CLI interface with `strataregula compile` command  
- Python, JSON, and YAML output formats
- Basic documentation and examples
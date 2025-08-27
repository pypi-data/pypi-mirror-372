# Developer Guide

Resources for developers working with StrataRegula's plugin system and internal APIs.

## Contents

- **[Plugin Quick Start](PLUGIN_QUICKSTART.md)** - Create your first plugin in 5 minutes
- **[API Reference](../api-reference/API_REFERENCE.md)** - Complete Python API documentation

## Plugin System Overview

StrataRegula v0.2.0 introduces a powerful plugin system with 5 hook points:

1. **`pre_compilation`** - Before processing starts
2. **`pattern_discovered`** - When patterns are found
3. **`pre_expand`** / **`post_expand`** - Around pattern expansion
4. **`compilation_complete`** - After output generation

## Quick Navigation

- [← Back to Documentation Index](../index.md)
- [User Guide](../user-guide/)
- [Examples →](../examples/examples.md)
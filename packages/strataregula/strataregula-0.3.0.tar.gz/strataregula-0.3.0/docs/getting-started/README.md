# Getting Started

Everything you need to get up and running with StrataRegula.

## Contents

- **[Installation](installation.md)** - Installation instructions and setup guide

## Quick Start

1. **Install StrataRegula**
   ```bash
   pip install strataregula
   ```

2. **Create a sample configuration**
   ```bash
   echo "service_times:
     web.*.response: 150  
     api.*.timeout: 30" > config.yaml
   ```

3. **See the magic**
   ```bash
   strataregula compile --traffic config.yaml
   ```

## Next Steps

- [CLI Reference](../user-guide/CLI_REFERENCE.md) - Learn all CLI commands
- [Examples](../examples/examples.md) - See real-world usage patterns
- [Plugin Development](../developer-guide/PLUGIN_QUICKSTART.md) - Create custom plugins

## Quick Navigation

- [← Back to Documentation Index](../index.md)
- [User Guide](../user-guide/)
- [Examples →](../examples/examples.md)
# Installation Guide

Complete installation guide for Strataregula and its ecosystem components.

## System Requirements

### Minimum Requirements
- **Python**: 3.11 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 512MB RAM
- **Disk Space**: 100MB for installation

### Recommended Requirements
- **Python**: 3.11 or 3.12 (latest stable)
- **Memory**: 2GB RAM for large pattern expansions
- **Disk Space**: 500MB for cache and logs

### Supported Platforms
- **Linux**: Ubuntu 20.04+, RHEL 8+, CentOS 8+, Amazon Linux 2+
- **macOS**: 11.0+ (Big Sur and later)
- **Windows**: 10, 11, Server 2019+

## Core Installation

### Option 1: PyPI Installation (Recommended)

```bash
# Install latest stable version
pip install strataregula

# Verify installation
sr --version
# Output: strataregula 0.1.1
```

### Option 2: Development Installation

```bash
# Clone repository
git clone https://github.com/strataregula/strataregula.git
cd strataregula

# Install in development mode
pip install -e ".[dev]"

# Run tests to verify
pytest
```

### Option 3: Docker Installation

```bash
# Pull official image
docker pull strataregula/strataregula:latest

# Run with volume mount
docker run --rm -v $(pwd):/workspace strataregula/strataregula:latest sr --help
```

## Optional Dependencies

## Optional Dependencies

### Development Tools

```bash
# Install development dependencies
pip install strataregula[dev]

# Individual tools
pip install pytest pytest-cov mypy ruff bandit pre-commit
```

### Performance Dependencies

```bash
# For large-scale processing
pip install strataregula[performance]

# Individual performance packages
pip install pandas numpy psutil
```

### Documentation Dependencies

```bash
# For local documentation building
pip install strataregula[docs]

# Individual documentation packages
pip install mkdocs mkdocs-material mkdocstrings
```

## Environment Setup

### Python Virtual Environment

#### Using venv (Python 3.11+)
```bash
# Create virtual environment
python -m venv strataregula-env

# Activate (Linux/macOS)
source strataregula-env/bin/activate

# Activate (Windows)
strataregula-env\Scripts\activate

# Install Strataregula
pip install strataregula

# Deactivate when done
deactivate
```

#### Using conda
```bash
# Create conda environment
conda create -n strataregula python=3.11

# Activate environment
conda activate strataregula

# Install Strataregula
pip install strataregula

# Deactivate when done
conda deactivate
```

#### Using Poetry
```bash
# Initialize Poetry project
poetry init
poetry add strataregula

# Install with dev dependencies
poetry add strataregula --group dev

# Run in Poetry environment
poetry run sr --help
```

### System Environment Variables

```bash
# Add to ~/.bashrc or ~/.zshrc
export STRATAREGULA_CONFIG_DIR="~/.strataregula"
export STRATAREGULA_CACHE_DIR="~/.strataregula/cache"
export STRATAREGULA_LOG_LEVEL="INFO"

# Optional configuration
export STRATAREGULA_DEBUG="false"
```

## Verification

### Basic Functionality Test

```bash
# Test core functionality
echo "services: [\"api.*.service\"]" > test-config.yaml
sr compile test-config.yaml --output test-output.py --format python

# Check output
python -c "
import sys
sys.path.append('.')
from test_output import SERVICES
print(f'Generated {len(SERVICES)} services')
"
```

### Advanced Pattern Test

```bash
# Test complex patterns
echo "services:
  api-*-*:
    port: 8080
  db-**:
    port: 5432" > complex-test.yaml

sr compile complex-test.yaml --verbose
echo "✅ Complex patterns working"
```

### Performance Test

```bash
# Test with larger dataset
python -c "
import yaml
config = {
    'services': [f'api.{i:03d}.service' for i in range(100)],
    'regions': {'test': list(range(10))}
}
with open('perf-test.yaml', 'w') as f:
    yaml.dump(config, f)
"

# Measure performance
time sr compile perf-test.yaml --stats
```

## IDE Integration

### VS Code Setup

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./strataregula-env/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "files.associations": {
        "*.sr": "yaml"
    }
}
```

### PyCharm Setup

1. Configure Python interpreter to use virtual environment
2. Enable pytest as test runner
3. Configure code style to use Black formatter
4. Add Strataregula file types (.sr) as YAML

## Docker Environment

### Official Images

```bash
# Core Strataregula
docker pull strataregula/strataregula:latest
docker pull strataregula/strataregula:0.1.1
```

### Custom Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Strataregula
RUN pip install --no-cache-dir strataregula

# Set working directory
WORKDIR /workspace

# Default command
CMD ["sr", "--help"]
```

### Docker Compose Setup

```yaml
version: '3.8'

services:
  strataregula:
    image: strataregula/strataregula:latest
    volumes:
      - ./config:/workspace/config
      - ./output:/workspace/output
    environment:
      - STRATAREGULA_LOG_LEVEL=INFO
    working_dir: /workspace
```

## Platform-Specific Instructions

### Ubuntu/Debian

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Strataregula
python3.11 -m pip install --user strataregula

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### CentOS/RHEL

```bash
# Install Python 3.11
sudo dnf install python3.11 python3.11-pip -y

# Install Strataregula
python3.11 -m pip install --user strataregula

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
```

### macOS

```bash
# Using Homebrew
brew install python@3.11

# Install Strataregula
python3.11 -m pip install strataregula

# Alternative: Using MacPorts
sudo port install python311
python3.11 -m pip install strataregula
```

### Windows

#### Command Prompt
```cmd
# Download Python 3.11 from python.org
# Install with "Add to PATH" option checked

# Install Strataregula
python -m pip install strataregula

# Verify installation
sr --version
```

#### PowerShell
```powershell
# Using Chocolatey
choco install python311

# Install Strataregula
python -m pip install strataregula

# Using Scoop
scoop install python
python -m pip install strataregula
```

## Troubleshooting

### Common Issues

#### Python Version Compatibility
```bash
# Check Python version
python --version
python3 --version

# If using old Python
pyenv install 3.11.0
pyenv global 3.11.0
```

#### Permission Errors
```bash
# Use user installation
pip install --user strataregula

# Or fix permissions
sudo chown -R $(whoami) ~/.local/lib/python*
```

#### Path Issues
```bash
# Add Python user bin to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Windows
setx PATH "%PATH%;%APPDATA%\Python\Python311\Scripts"
```

#### Module Import Issues
```python
# Debug module imports
try:
    from strataregula.core import config_compiler
    print('✅ Core compiler available')
except ImportError as e:
    print(f'❌ Import error: {e}')
```

### Performance Issues

#### Large Memory Usage
```bash
# Reduce memory usage
export STRATAREGULA_CACHE_SIZE=64
export STRATAREGULA_MEMORY_LIMIT=512

# Use streaming mode
sr compile large-config.yaml --stream --memory-limit 200
```

#### Slow Pattern Expansion
```bash
# Enable performance mode
export STRATAREGULA_PERFORMANCE_MODE=1

# Use compiled patterns
sr compile config.yaml --enable-cache --cache-size 256
```

### Getting Help

#### Check Installation
```bash
# Verify installation
python -c "
import strataregula
print(f'Strataregula: {strataregula.__version__}')
from strataregula.cli.main import main
print('✅ CLI module working')
from strataregula.core import pattern_expander
print('✅ Core modules working')
"
```

#### System Information
```bash
# Generate system report
python -c "
import sys
import platform
import strataregula
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Strataregula: {strataregula.__version__}')
"
```

#### Log Analysis
```bash
# Enable debug logging
export STRATAREGULA_LOG_LEVEL=DEBUG
sr compile config.yaml --verbose > debug.log 2>&1

# Check logs
tail -f debug.log
```

## Next Steps

After successful installation:

1. **[Examples](../examples/examples.md)** - Real-world usage patterns
2. **[CLI Reference](../user-guide/CLI_REFERENCE.md)** - Complete command reference
3. **[Plugin Development](../developer-guide/PLUGIN_QUICKSTART.md)** - Create custom plugins
4. **[API Reference](../api-reference/API_REFERENCE.md)** - Complete Python API documentation

## Support

If you encounter installation issues:

- **Documentation**: Continue reading this guide
- **GitHub Issues**: [Report Installation Problems](https://github.com/strataregula/strataregula/issues)
- **Discussions**: [Community Support](https://github.com/strataregula/strataregula/discussions)
- **Email**: team@strataregula.com
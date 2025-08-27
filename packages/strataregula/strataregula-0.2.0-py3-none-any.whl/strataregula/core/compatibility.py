"""
Compatibility layer for different Python environments and package versions.
Handles pyenv, conda, and various dependency versions gracefully.
"""
import sys
import warnings
from typing import Dict, Any, Optional, Tuple
from importlib import import_module
from importlib.metadata import version, PackageNotFoundError


def get_python_info() -> Dict[str, Any]:
    """Get detailed Python environment information."""
    return {
        "version": sys.version_info,
        "executable": sys.executable,
        "platform": sys.platform,
        "implementation": sys.implementation.name,
        "prefix": sys.prefix,
    }


def check_package_version(package: str, min_version: str) -> Tuple[bool, Optional[str]]:
    """
    Check if package meets minimum version requirement.
    
    Returns:
        (is_compatible, installed_version)
    """
    try:
        installed = version(package)
        # Simple version comparison (works for most cases)
        installed_parts = [int(x) for x in installed.split('.') if x.isdigit()]
        min_parts = [int(x) for x in min_version.split('.') if x.isdigit()]
        
        # Pad shorter version with zeros
        max_len = max(len(installed_parts), len(min_parts))
        installed_parts.extend([0] * (max_len - len(installed_parts)))
        min_parts.extend([0] * (max_len - len(min_parts)))
        
        is_compatible = installed_parts >= min_parts
        return is_compatible, installed
        
    except (PackageNotFoundError, ValueError):
        return False, None


def check_environment_compatibility() -> Dict[str, Any]:
    """
    Comprehensive environment compatibility check.
    
    Returns detailed compatibility report.
    """
    python_info = get_python_info()
    
    # Check minimum requirements
    requirements = {
        "python": "3.8.0",
        "click": "7.0.0",
        "rich": "10.0.0", 
        "pyyaml": "5.4.0",
        "typing-extensions": "3.10.0"
    }
    
    compatibility_report = {
        "python_info": python_info,
        "compatible": True,
        "issues": [],
        "warnings": [],
        "package_versions": {}
    }
    
    # Check Python version
    if python_info["version"] < (3, 8):
        compatibility_report["compatible"] = False
        compatibility_report["issues"].append(
            f"Python {python_info['version']} is not supported. Minimum required: 3.8.0"
        )
    
    # Check package versions
    for package, min_ver in requirements.items():
        if package == "python":
            continue
            
        is_compat, installed_ver = check_package_version(package, min_ver)
        compatibility_report["package_versions"][package] = {
            "required": min_ver,
            "installed": installed_ver,
            "compatible": is_compat
        }
        
        if not is_compat:
            if installed_ver:
                compatibility_report["issues"].append(
                    f"{package} {installed_ver} < {min_ver} (required)"
                )
            else:
                compatibility_report["issues"].append(
                    f"{package} is not installed (required >= {min_ver})"
                )
    
    # Environment-specific warnings
    if "pyenv" in python_info["executable"]:
        compatibility_report["warnings"].append(
            "Using pyenv Python. If you encounter issues, try 'pyenv install 3.9.16' "
            "or newer for better package compatibility."
        )
    
    if python_info["implementation"] != "cpython":
        compatibility_report["warnings"].append(
            f"Using {python_info['implementation']} instead of CPython. "
            "Some features may not work as expected."
        )
    
    return compatibility_report


def safe_import_with_fallback(package: str, fallback_package: Optional[str] = None):
    """
    Safely import a package with optional fallback.
    
    Args:
        package: Primary package to import
        fallback_package: Alternative package to try if primary fails
        
    Returns:
        Imported module or None if both fail
    """
    try:
        return import_module(package)
    except ImportError as e:
        if fallback_package:
            try:
                return import_module(fallback_package)
            except ImportError:
                pass
        
        warnings.warn(
            f"Could not import {package}. Some features may be unavailable.",
            RuntimeWarning
        )
        return None


def safe_import_psutil():
    """
    Safely import psutil with helpful error messages.
    
    Returns:
        psutil module or None if not available
    """
    try:
        import psutil
        return psutil
    except ImportError:
        warnings.warn(
            "psutil not available. Memory/CPU monitoring features disabled. "
            "Install with: pip install 'strataregula[performance]'",
            RuntimeWarning
        )
        return None


class MockPsutilProcess:
    """Mock psutil.Process for when psutil is not available."""
    
    def memory_info(self):
        return type('obj', (object,), {'rss': 0, 'vms': 0})()
    
    def cpu_percent(self):
        return 0.0
    
    def memory_percent(self):
        return 0.0


def get_compatible_rich_console():
    """Get Rich console with compatibility fallbacks."""
    try:
        from rich.console import Console
        from rich.theme import Theme
        
        # Test if advanced features work
        console = Console(theme=Theme({
            "info": "cyan",
            "warning": "yellow", 
            "error": "bold red"
        }))
        
        # Test if console works properly
        with console.capture() as capture:
            console.print("test", style="info")
        
        if capture.get():  # If capture worked, Rich is functional
            return console
        else:
            raise ImportError("Rich console not working properly")
            
    except (ImportError, Exception):
        # Fallback to basic console
        warnings.warn(
            "Rich console not available. Using basic output.",
            RuntimeWarning
        )
        return None


def check_yaml_compatibility():
    """Check PyYAML compatibility and suggest fixes."""
    try:
        import yaml
        
        # Test basic functionality
        test_data = {"test": "value", "number": 123}
        yaml_str = yaml.dump(test_data)
        parsed = yaml.safe_load(yaml_str)
        
        if parsed != test_data:
            raise RuntimeError("YAML serialization/deserialization failed")
            
        return True, None
        
    except ImportError:
        return False, "PyYAML not installed. Run: pip install 'PyYAML>=5.4.0'"
    except Exception as e:
        return False, f"PyYAML compatibility issue: {e}"


def print_compatibility_report():
    """Print detailed compatibility report."""
    report = check_environment_compatibility()
    
    print("=" * 60)
    print("🔍 STRATAREGULA ENVIRONMENT COMPATIBILITY CHECK")
    print("=" * 60)
    
    # Python info
    py_info = report["python_info"]
    print(f"🐍 Python: {py_info['version'][0]}.{py_info['version'][1]}.{py_info['version'][2]}")
    print(f"📍 Executable: {py_info['executable']}")
    print(f"🏗️  Implementation: {py_info['implementation']}")
    
    print("\n📦 PACKAGE VERSIONS:")
    print("-" * 40)
    for pkg, info in report["package_versions"].items():
        status = "✅" if info["compatible"] else "❌"
        installed = info["installed"] or "Not installed"
        print(f"{status} {pkg:<18} {installed:<12} (>= {info['required']})")
    
    # Warnings
    if report["warnings"]:
        print(f"\n⚠️  WARNINGS:")
        print("-" * 40)
        for warning in report["warnings"]:
            print(f"⚠️  {warning}")
    
    # Issues
    if report["issues"]:
        print(f"\n❌ ISSUES:")
        print("-" * 40)
        for issue in report["issues"]:
            print(f"❌ {issue}")
    
    # Overall status
    print(f"\n🎯 OVERALL STATUS: {'✅ COMPATIBLE' if report['compatible'] else '❌ INCOMPATIBLE'}")
    
    # Suggestions for pyenv users
    if "pyenv" in py_info["executable"] and not report["compatible"]:
        print("\n💡 PYENV TROUBLESHOOTING:")
        print("-" * 40)
        print("1. Install a newer Python version:")
        print("   pyenv install 3.9.16")
        print("   pyenv global 3.9.16")
        print("")
        print("2. Upgrade pip and reinstall packages:")
        print("   pip install --upgrade pip")
        print("   pip install --upgrade strataregula")
        print("")
        print("3. If issues persist, create a fresh environment:")
        print("   pyenv virtualenv 3.9.16 strataregula-env")
        print("   pyenv activate strataregula-env")
        print("   pip install strataregula")
    
    return report["compatible"]


if __name__ == "__main__":
    print_compatibility_report()
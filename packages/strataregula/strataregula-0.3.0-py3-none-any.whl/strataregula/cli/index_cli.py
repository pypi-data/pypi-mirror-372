#!/usr/bin/env python3
"""
Index provider CLI for statistics and diagnostics.

Provides self-diagnosis capabilities to inspect the current index provider,
base commit, file counts, and capabilities.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from strataregula.index import loader


def get_config_priority() -> dict[str, Any]:
    """
    Get configuration with priority: CLI > env > config > default

    Returns:
        Dictionary with resolved configuration values
    """
    config = {
        "provider": None,
        "base": None,
        "roots": ["src", "tests"],
        "config_file": None,
    }

    # 3. Config file (if exists)
    config_path = Path.cwd() / ".strataregula.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                file_config = json.load(f)
                config.update(file_config.get("index", {}))
                config["config_file"] = str(config_path)
        except Exception:
            pass

    # 2. Environment variables (override config)
    if env_provider := os.environ.get("SR_INDEX_PROVIDER"):
        config["provider"] = env_provider
    if env_base := os.environ.get("SR_INDEX_BASE"):
        config["base"] = env_base
    if env_roots := os.environ.get("SR_INDEX_ROOTS"):
        config["roots"] = env_roots.split(",")

    return config


def stats_command(args: argparse.Namespace) -> int:
    """
    Execute stats command to show index provider statistics.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success)
    """
    # Get configuration with priority
    config = get_config_priority()

    # 1. CLI arguments (highest priority)
    provider_name = args.provider or config["provider"]
    base = args.base or config["base"]
    roots = args.roots or config["roots"]

    # Resolve provider
    try:
        provider = loader.resolve_provider(provider_name, cfg=None)
    except Exception as e:
        print(f"Error resolving provider: {e}", file=sys.stderr)
        return 1

    # Get repository root
    repo_root = Path.cwd()
    while repo_root != repo_root.parent:
        if (repo_root / ".git").exists():
            break
        repo_root = repo_root.parent
    else:
        repo_root = Path.cwd()

    # Run changed_py to populate stats
    try:
        files = provider.changed_py(base, roots, repo_root, verbose=args.verbose)
    except Exception as e:
        if args.verbose:
            print(f"Error getting changed files: {e}", file=sys.stderr)
        files = []

    # Get stats
    stats = provider.stats()

    # Add configuration source information
    stats["config"] = {
        "provider_source": "cli"
        if args.provider
        else (
            "env"
            if os.environ.get("SR_INDEX_PROVIDER")
            else (
                "config" if config["config_file"] and config["provider"] else "default"
            )
        ),
        "base_source": "cli"
        if args.base
        else (
            "env"
            if os.environ.get("SR_INDEX_BASE")
            else ("config" if config["config_file"] and config["base"] else "auto")
        ),
        "roots_source": "cli"
        if args.roots
        else (
            "env"
            if os.environ.get("SR_INDEX_ROOTS")
            else (
                "config" if config["config_file"] and "roots" in config else "default"
            )
        ),
        "config_file": config.get("config_file"),
    }

    # Add capability information
    if hasattr(provider, "capabilities"):
        stats["capabilities"] = list(provider.capabilities)

    # Output format
    if args.format == "json":
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    elif args.format == "text":
        print("Index Provider Statistics")
        print("=" * 40)
        print(
            f"Provider: {stats.get('provider', 'unknown')} v{stats.get('version', 'unknown')}"
        )
        print(f"Base: {stats.get('base', 'none')}")
        print(f"Files: {stats.get('files', 0)}")
        print(f"Roots: {', '.join(stats.get('roots', []))}")
        if "capabilities" in stats:
            print(f"Capabilities: {', '.join(stats['capabilities'])}")
        print("\nConfiguration Sources:")
        print(f"  Provider: {stats['config']['provider_source']}")
        print(f"  Base: {stats['config']['base_source']}")
        print(f"  Roots: {stats['config']['roots_source']}")
        if stats["config"].get("config_file"):
            print(f"  Config file: {stats['config']['config_file']}")

    return 0


def config_command(args: argparse.Namespace) -> int:
    """
    Show current configuration with priority resolution.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success)
    """
    config = get_config_priority()

    # Show resolution order
    print("Configuration Priority Order:")
    print("1. CLI arguments (highest)")
    print("2. Environment variables (SR_INDEX_*)")
    print("3. Config file (.strataregula.json)")
    print("4. Defaults (lowest)")
    print()

    print("Current Configuration:")
    print(f"  Provider: {config['provider'] or 'default (builtin:fastindex)'}")
    print(f"  Base: {config['base'] or 'auto'}")
    print(f"  Roots: {', '.join(config['roots'])}")

    if config.get("config_file"):
        print(f"  Config file: {config['config_file']}")
    else:
        print("  Config file: none")

    print()
    print("Environment Variables:")
    print(f"  SR_INDEX_PROVIDER: {os.environ.get('SR_INDEX_PROVIDER', '(not set)')}")
    print(f"  SR_INDEX_BASE: {os.environ.get('SR_INDEX_BASE', '(not set)')}")
    print(f"  SR_INDEX_ROOTS: {os.environ.get('SR_INDEX_ROOTS', '(not set)')}")

    return 0


def main():
    """Main entry point for sr-index CLI."""
    parser = argparse.ArgumentParser(
        prog="sr-index", description="Index provider statistics and diagnostics"
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show index provider statistics")
    stats_parser.add_argument(
        "--provider", help="Provider name (e.g., builtin:fastindex, plugin:learned)"
    )
    stats_parser.add_argument("--base", help="Base commit for comparison")
    stats_parser.add_argument("--roots", nargs="+", help="Root directories to scan")
    stats_parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )

    # Config command
    config_parser = subparsers.add_parser(
        "config", help="Show configuration with priority"
    )

    args = parser.parse_args()

    # Dispatch to command handler
    if args.command == "stats":
        return stats_command(args)
    elif args.command == "config":
        return config_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

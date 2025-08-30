"""Content search with automatic fallback to rg/grep."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def search_content(
    pattern: str,
    files: list[Path],
    provider: object | None = None,
    verbose: bool = False,
) -> list[str]:
    """
    Search for pattern in files, with automatic fallback chain.

    1. Use provider.search() if provider has 'content' capability
    2. Fall back to ripgrep (rg) if available
    3. Fall back to grep as last resort

    Args:
        pattern: Regex pattern to search for
        files: List of files to search
        provider: Optional index provider with search capability
        verbose: Print debug information

    Returns:
        List of matching lines in format "file:line_num:content"
    """
    results = []

    # Try provider first if it has content capability
    if (
        provider
        and hasattr(provider, "capabilities")
        and "content" in provider.capabilities
    ):
        if verbose:
            print(f"Using provider {provider.name} for content search")
        try:
            results = provider.search(pattern, files)
            if results:
                return results
        except Exception as e:
            if verbose:
                print(f"Provider search failed: {e}")

    # Fallback to ripgrep
    if shutil.which("rg"):
        if verbose:
            print("Using ripgrep for content search")
        try:
            # Build rg command
            cmd = ["rg", "-n", "--no-heading", pattern]
            cmd.extend(str(f) for f in files)

            output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
            results = output.strip().split("\n") if output.strip() else []
            return results
        except subprocess.CalledProcessError:
            # No matches found
            return []
        except Exception as e:
            if verbose:
                print(f"ripgrep failed: {e}")

    # Final fallback to grep
    if verbose:
        print("Using grep for content search")
    try:
        # Build grep command
        cmd = ["grep", "-n", pattern]
        cmd.extend(str(f) for f in files)

        output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        results = output.strip().split("\n") if output.strip() else []
        return results
    except subprocess.CalledProcessError:
        # No matches found
        return []
    except FileNotFoundError:
        if verbose:
            print("ERROR: Neither rg nor grep available for content search")
        return []
    except Exception as e:
        if verbose:
            print(f"grep failed: {e}")
        return []


def has_content_capability(provider: object) -> bool:
    """Check if provider has content search capability."""
    if not provider:
        return False
    if not hasattr(provider, "capabilities"):
        return False
    return "content" in provider.capabilities

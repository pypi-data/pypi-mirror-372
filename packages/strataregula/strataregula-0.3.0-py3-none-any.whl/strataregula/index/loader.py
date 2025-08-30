from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from typing import Any

from .base import IndexProvider


def _load_by_string(name: str) -> IndexProvider:
    if name.startswith("builtin:"):
        mod = importlib.import_module(f"strataregula.index.providers.{name[8:]}")
    elif name.startswith("plugin:"):
        mod = importlib.import_module(f"sr_index_{name[7:]}")  # 外部プラグイン命名規約
    else:
        mod = importlib.import_module(name)  # 完全修飾名OK
    provider_cls = mod.Provider
    return provider_cls()


def _load_config_file() -> dict[str, Any] | None:
    """Load configuration from .strataregula.json if it exists."""
    config_path = Path.cwd() / ".strataregula.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception:
            pass
    return None


def resolve_provider(
    cli_arg: str | None = None, cfg: dict[str, Any] | None = None
) -> IndexProvider:
    """
    Resolve index provider with priority: CLI > env > config file > default

    Args:
        cli_arg: Provider name from CLI argument
        cfg: Configuration dictionary (optional)

    Returns:
        IndexProvider instance
    """
    # Load config file if not provided
    if cfg is None:
        cfg = _load_config_file()

    # Priority order: CLI > env > config file > default
    name = (
        cli_arg
        or os.getenv("SR_INDEX_PROVIDER")
        or (cfg or {}).get("index", {}).get("provider")
        or "builtin:fastindex"
    )
    try:
        return _load_by_string(name)
    except Exception:
        # 常に成功する既定フォールバック
        from .providers.fastindex import Provider

        return Provider()

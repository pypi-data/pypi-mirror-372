from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from collections.abc import Iterable
from pathlib import Path
from typing import Any


class Provider:
    """
    既定の軽量インデックス（パス列挙に特化）。capabilities={'paths'}。
    """

    name = "fastindex"
    version = "0.1.0"
    capabilities: set[str] = {"paths"}

    def __init__(self) -> None:
        self._last_stats: dict[str, Any] = {}
        self._cache_dir: Path | None = None
        self._lock_file: Path | None = None

    # no-op
    def build(self, entries: Iterable[Path] | None = None) -> None:
        self._last_stats = {"built": True}

    def _init_cache(self, repo_root: Path) -> None:
        """Initialize provider-specific cache directory."""
        cache_base = repo_root / ".cache" / "index" / self.name
        cache_base.mkdir(parents=True, exist_ok=True)
        self._cache_dir = cache_base
        self._lock_file = repo_root / ".cache" / "index" / ".lock"

    def _acquire_lock(self, timeout: int = 30) -> bool:
        """Simple PID-based lock to avoid concurrent builds."""
        if not self._lock_file:
            return True

        start = time.time()
        my_pid = str(os.getpid())

        while time.time() - start < timeout:
            try:
                # Check if lock exists and is stale
                if self._lock_file.exists():
                    lock_data = self._lock_file.read_text().strip()
                    if lock_data:
                        try:
                            lock_pid = int(lock_data)
                            # Check if process is still running (platform-specific)
                            if os.name == "nt":  # Windows
                                result = subprocess.run(
                                    ["tasklist", "/FI", f"PID eq {lock_pid}"],
                                    check=False, capture_output=True,
                                    text=True,
                                )
                                if str(lock_pid) not in result.stdout:
                                    # Process not running, remove stale lock
                                    self._lock_file.unlink()
                            else:  # Unix
                                try:
                                    os.kill(lock_pid, 0)
                                except OSError:
                                    # Process not running
                                    self._lock_file.unlink()
                        except (ValueError, subprocess.SubprocessError):
                            # Invalid lock file, remove it
                            self._lock_file.unlink()

                # Try to create lock
                if not self._lock_file.exists():
                    self._lock_file.parent.mkdir(parents=True, exist_ok=True)
                    self._lock_file.write_text(my_pid)
                    return True

            except Exception:
                pass

            time.sleep(0.5)

        return False

    def _release_lock(self) -> None:
        """Release the lock if we own it."""
        if self._lock_file and self._lock_file.exists():
            try:
                lock_pid = self._lock_file.read_text().strip()
                if lock_pid == str(os.getpid()):
                    self._lock_file.unlink()
            except Exception:
                pass

    def _get_cache_key(self, base: str, roots: list[str]) -> str:
        """Generate cache key from base and roots."""
        key_data = f"{base}:{':'.join(sorted(roots))}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _load_cache(self, base: str, roots: list[str]) -> list[Path] | None:
        """Load cached file list if valid."""
        if not self._cache_dir or not base:
            return None

        cache_key = self._get_cache_key(base, roots)
        cache_file = self._cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                # Check if HEAD has changed
                current_head = subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], text=True
                ).strip()

                if data.get("head") == current_head:
                    return [Path(p) for p in data.get("files", [])]
            except Exception:
                pass

        return None

    def _save_cache(self, base: str, roots: list[str], files: list[Path]) -> None:
        """Save file list to cache."""
        if not self._cache_dir or not base:
            return

        try:
            current_head = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip()

            cache_key = self._get_cache_key(base, roots)
            cache_file = self._cache_dir / f"{cache_key}.json"

            data = {
                "base": base,
                "head": current_head,
                "roots": roots,
                "files": [str(p) for p in files],
                "timestamp": time.time(),
            }

            cache_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def _auto_base(self, repo_root: Path, verbose: bool = False) -> str | None:
        # 可能な限り“現在の環境だけ”で解決。originが無くてもOK。
        # 1) PRイベントのpayload（省略：ここでは簡略化）
        # 2) merge-base (main/master/upstream) が無理なら
        # 3) HEAD~1、最後に None
        candidates = ["origin/main", "origin/master", "main", "master"]
        for cand in candidates:
            try:
                sha = subprocess.check_output(
                    ["git", "merge-base", cand, "HEAD"],
                    cwd=repo_root,
                    text=True,
                    stderr=subprocess.DEVNULL,
                ).strip()
                if sha:
                    return sha
            except Exception:
                pass
        try:
            sha = subprocess.check_output(
                ["git", "rev-parse", "HEAD~1"], cwd=repo_root, text=True
            ).strip()
            return sha
        except Exception:
            return None

    def changed_py(
        self,
        base: str | None,
        roots: list[str],
        repo_root: Path,
        verbose: bool = False,
    ) -> list[Path]:
        repo_root = repo_root.resolve()

        # Initialize cache on first use
        if self._cache_dir is None:
            self._init_cache(repo_root)

        base = base if base and base != "auto" else self._auto_base(repo_root, verbose)

        # Try to load from cache first
        if base:
            cached_files = self._load_cache(base, roots)
            if cached_files is not None:
                self._last_stats.update(
                    {
                        "base": base,
                        "files": len(cached_files),
                        "roots": roots,
                        "cache_hit": True,
                    }
                )
                return cached_files

        # Acquire lock for git operations
        lock_acquired = self._acquire_lock()

        try:
            files: list[Path] = []

            if base:
                try:
                    out = subprocess.check_output(
                        [
                            "git",
                            "diff",
                            "--name-only",
                            "--diff-filter=ACMRTUXB",
                            f"{base}..HEAD",
                        ],
                        cwd=repo_root,
                        text=True,
                        stderr=subprocess.DEVNULL,
                    )
                    for rel in out.splitlines():
                        p = (repo_root / rel.strip()).resolve()
                        if p.suffix == ".py" and p.exists():
                            if not roots or any(
                                (repo_root / r) in p.parents for r in roots
                            ):
                                files.append(p)
                except Exception:
                    files = []

            if not files:
                # フォールバック：指定roots配下の*.pyを全列挙（最悪でも動く）
                for r in roots:
                    root_dir = (repo_root / r).resolve()
                    if root_dir.exists():
                        files.extend(p for p in root_dir.rglob("*.py"))

            files = sorted(set(files))

            # Save to cache if we have a base
            if base and files:
                self._save_cache(base, roots, files)

            self._last_stats.update(
                {
                    "base": base or "none",
                    "files": len(files),
                    "roots": roots,
                    "cache_hit": False,
                    "lock_acquired": lock_acquired,
                }
            )

            return files

        finally:
            self._release_lock()

    def search(self, pattern: str, paths: list[Path]) -> list[str]:
        # content検索capabilityは持たない → 空返却（上位でrg/grepにフォールバックさせる想定）
        return []

    def stats(self) -> dict[str, Any]:
        return {"provider": self.name, "version": self.version, **self._last_stats}

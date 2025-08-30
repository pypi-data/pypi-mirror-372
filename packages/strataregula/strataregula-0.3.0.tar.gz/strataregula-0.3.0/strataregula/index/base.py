from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any, Protocol


class IndexProvider(Protocol):
    """
    インデックス抽象。
    - 最小要件：`changed_py` と `stats`
    - 追加機能（`search` など）は capabilities で宣言
    """

    name: str
    version: str
    capabilities: set[str]

    def build(self, entries: Iterable[Path] | None = None) -> None: ...
    def changed_py(
        self,
        base: str | None,
        roots: list[str],
        repo_root: Path,
        verbose: bool = False,
    ) -> list[Path]: ...
    def search(self, pattern: str, paths: list[Path]) -> list[str]: ...
    def stats(self) -> dict[str, Any]: ...

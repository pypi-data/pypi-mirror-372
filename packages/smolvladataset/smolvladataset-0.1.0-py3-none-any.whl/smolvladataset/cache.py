"""Cache utilities.

All artifacts are stored under ``~/.cache/smolvladataset`` by default, with
subdirectories keyed by a stable hash of the dataset list CSV.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from .utils import csv_list_hash, default_cache_dir, ensure_dir


def cache_root() -> Path:
    """Return the root cache directory, creating it if missing."""
    root = default_cache_dir()
    ensure_dir(root)
    return root


def cache_paths_for_list(csv_path: Path) -> Tuple[Path, Path, Path]:
    """Return cache paths for artifacts associated with a dataset list.

    Args:
        csv_path: Path to a CSV containing dataset repository IDs.

    Returns:
        A tuple ``(root, merged_parquet, stats_parquet)`` where ``root`` is the
        cache bucket directory and the other two are artifact paths within it.
    """
    key = csv_list_hash(csv_path)
    root = cache_root() / key
    ensure_dir(root)
    return root, root / "merged.parquet", root / "stats.parquet"

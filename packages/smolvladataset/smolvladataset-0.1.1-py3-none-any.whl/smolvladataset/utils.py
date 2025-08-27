"""Utility helpers for file IO, hashing, and Parquet normalization."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Iterable, List

import numpy as np
import pandas as pd


def ensure_dir(p: Path) -> None:
    """Create a directory and parents if they do not already exist."""
    p.mkdir(parents=True, exist_ok=True)


def read_repo_ids(csv_path: Path) -> List[str]:
    """Read first-column Hugging Face repo IDs from a CSV.

    Empty lines and rows whose first cell starts with ``#`` are ignored.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        A list of strings of the form ``"org/name"``.
    """
    ids: List[str] = []

    with open(csv_path, newline="") as f:
        for row in csv.reader(f):
            if not row:
                continue

            cell = row[0].strip()

            if not cell or cell.startswith("#"):
                continue

            if "/" in cell:
                ids.append(cell)

    return ids


def canonical_hash(ids: Iterable[str]) -> str:
    """Return a stable 12-character hash for a set of repo IDs.

    IDs are normalized by trimming whitespace, deduplicating, sorting, and
    joining with newlines before hashing with MD5.

    Args:
        ids: Iterable of repository IDs.

    Returns:
        A 12-character hexadecimal digest suitable for cache keys.
    """
    norm = "\n".join(sorted({x.strip() for x in ids if x.strip()}))
    return hashlib.md5(norm.encode("utf-8")).hexdigest()[:12]


def csv_list_hash(csv_path: Path) -> str:
    """Return a 12-character hash for a CSV of repo IDs."""
    return canonical_hash(read_repo_ids(csv_path))


def default_cache_dir() -> Path:
    """Return the default cache directory (``~/.cache/smolvladataset``)."""
    return Path.home() / ".cache" / "smolvladataset"


def save_df_parquet(df: pd.DataFrame, path: Path) -> None:
    """Write a DataFrame to Parquet with light numeric list normalization.

    Apache Arrow requires consistent element types across list-like cells. Some
    datasets mix float32/float64 or int/float in columns like ``action``. This
    function normalizes any list/array of numbers to a plain Python list of
    ``float64`` values before writing to stabilize schema inference.

    Args:
        df: DataFrame to persist.
        path: Output Parquet path. Parent directories are created as needed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    def _normalize_cell(v):
        if isinstance(v, (list, tuple, np.ndarray)):
            try:
                arr = np.asarray(v)
                if arr.dtype.kind in ("i", "u", "f"):
                    return [float(x) for x in arr.ravel().tolist()]
            except (ValueError, TypeError, OverflowError):
                # Only catch specific conversion errors, return original value
                return v
        return v

    # Apply normalization to all object columns
    df_norm = df.copy()
    object_cols = df_norm.select_dtypes(include=["object"]).columns
    df_norm[object_cols] = df_norm[object_cols].map(_normalize_cell)

    df_norm.to_parquet(path, index=False)


def load_df_parquet(path: Path) -> pd.DataFrame:
    """Load a DataFrame from a Parquet file."""
    return pd.read_parquet(path)

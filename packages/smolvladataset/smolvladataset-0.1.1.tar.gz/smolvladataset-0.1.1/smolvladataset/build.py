"""Build helpers for creating and fetching precompiled datasets.

This module provides utilities to:

- Convert a Hugging Face dataset repo to a single Parquet file.
- Merge per-dataset Parquet files and compute simple statistics.
- Download a precompiled merged dataset and statistics from the Hub.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from shutil import copyfile
from typing import Dict, List

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download

from datasets import concatenate_datasets, load_dataset

from .cache import cache_paths_for_list
from .utils import ensure_dir, read_repo_ids, save_df_parquet

DEFAULT_PRECOMPILED_REPO: str = "SmolVLADataset/SmolVLADataset"


def dataset_to_parquet(repo_id: str, out_dir: Path) -> str:
    """Download a Hugging Face dataset and save as a single Parquet.

    If the source dataset provides multiple splits, they are concatenated prior
    to conversion. Idempotent: if the output already exists, the operation is
    skipped.

    Args:
        repo_id: Dataset repository ID on the Hugging Face Hub (``"org/name"``).
        out_dir: Folder where the resulting ``.parquet`` file is written.

    Returns:
        A status string: ``"skipped_exists"``, ``"ok"``, or ``"error:<Name>"``.
    """
    os.environ.setdefault(
        "HF_HUB_ENABLE_HF_TRANSFER", "1"
    )  # enable hf transfer (for faster download)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{repo_id.replace('/', '_')}.parquet"

    if out_path.exists():
        return "skipped_exists"

    try:
        loaded = load_dataset(repo_id)

        if isinstance(loaded, dict) and len(loaded):
            ds = concatenate_datasets(list(loaded.values()))
        else:
            ds = loaded
    except Exception as e:
        return f"error:{e.__class__.__name__}"

    try:
        df = ds.to_pandas()
        if df is None:
            return "error:Empty"
        save_df_parquet(df, out_path)
        return "ok"
    except Exception as e2:
        return f"error:{e2.__class__.__name__}"


def list_parquets(folder: Path) -> List[Path]:
    """Return all ``*.parquet`` files directly within ``folder``."""
    return list(folder.glob("*.parquet"))


def parse_list_numbers(series: pd.Series, sample: int = 2000) -> np.ndarray:
    """Extract numeric values from list/array-like cells (best effort).

    Supports Python lists/tuples/NumPy arrays and simple string renderings such
    as ``"[1, 2]"`` or ``"array([1, 2])"``. Returns a flat ``float64`` array.

    Args:
        series: Column from a DataFrame to sample.
        sample: Maximum number of non-NA rows to inspect.

    Returns:
        A 1-D NumPy array of extracted ``float64`` values. May be empty.
    """
    vals: List[float] = []

    for v in series.dropna().head(sample):
        if isinstance(v, (list, tuple, np.ndarray)):
            arr = np.asarray(v, dtype=float).ravel()
        elif isinstance(v, str):
            s = v
            s = s.replace("array(", "").replace(")", "")
            s = s.replace("[", " ").replace("]", " ")
            s = s.replace("(", " ").replace(")", " ")
            s = s.replace(",", " ").replace("\n", " ").replace("\r", " ")
            nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)

            if not nums:
                continue

            arr = np.asarray([float(x) for x in nums], dtype=float)
        else:
            continue

        vals.extend(arr.tolist())

    return np.asarray(vals, dtype=float)


def stats_for_dataset(parquet_path: Path) -> Dict[str, float]:
    """Compute simple mean/std stats for numeric columns in a Parquet file.

    Returns a dictionary including ``"dataset"``, ``"num_rows"``, and per-column
    entries named ``"<col>_mean"`` and ``"<col>_std"``. List-like numeric columns
    are supported via :func:`parse_list_numbers`.

    Args:
        parquet_path: Path to the per-dataset Parquet file.

    Returns:
        A mapping of metric name to numeric value.
    """
    df = pd.read_parquet(parquet_path)
    out: Dict[str, float] = {"dataset": parquet_path.stem, "num_rows": float(len(df))}

    for c in df.columns:
        s = pd.to_numeric(df[c], errors="coerce").dropna()

        if len(s):
            out[f"{c}_mean"] = float(s.mean())
            out[f"{c}_std"] = float(s.std(ddof=0))

            continue

        arr = parse_list_numbers(df[c])

        if arr.size:
            out[f"{c}_mean"] = float(arr.mean())
            out[f"{c}_std"] = float(arr.std(ddof=0))

    return out


def download_precompiled(csv_list: Path, repo_id: str) -> bool:
    """Download precompiled artifacts (``merged.parquet`` and ``stats.parquet``).

    Files are downloaded from the Hugging Face Hub and materialized under the
    cache bucket keyed by the provided CSV list.

    Args:
        csv_list: CSV file used to key the cache bucket.
        repo_id: Dataset repository ID containing precompiled artifacts.

    Returns:
        True if both files were downloaded and written to cache.

    Raises:
        RuntimeError: If any step of the download or write process fails.
    """
    root, merged_parquet, stats_parquet = cache_paths_for_list(csv_list)

    try:
        mp = hf_hub_download(
            repo_type="dataset", repo_id=repo_id, filename="merged.parquet"
        )
        sp = hf_hub_download(
            repo_type="dataset", repo_id=repo_id, filename="stats.parquet"
        )

        copyfile(mp, merged_parquet)
        copyfile(sp, stats_parquet)

        if not (merged_parquet.exists() and stats_parquet.exists()):
            raise RuntimeError("Failed to materialize precompiled artifacts to cache")
        return True
    except Exception as e:
        raise RuntimeError(
            f"Failed to download precompiled dataset from '{repo_id}': {e}"
        ) from e


def build_from_repo_list(csv_list: Path, force: bool = False) -> Path:
    """Build merged Parquet and statistics from a CSV of HF repo IDs.

    Each dataset is fetched and converted to Parquet, then all are merged into
    a single table with a ``dataset`` column indicating origin. Basic
    statistics are computed per source. Results are cached and reused unless
    ``force`` is ``True``.

    Args:
        csv_list: Path to a CSV whose first column contains ``org/name`` repo IDs.
        force: Force rebuilding even if cached artifacts exist.

    Returns:
        Path to the merged Parquet file in the cache.

    Raises:
        RuntimeError: If no per-dataset Parquet files could be produced.
    """
    root, merged_parquet, stats_parquet = cache_paths_for_list(csv_list)

    if merged_parquet.exists() and not force:
        return merged_parquet

    # 1) Fetch per-dataset Parquet files to a local folder under cache
    per_ds_dir = root / "per_dataset"
    ensure_dir(per_ds_dir)

    for rid in read_repo_ids(csv_list):
        _ = dataset_to_parquet(rid, per_ds_dir)

    # 2) Merge datasets
    files = list_parquets(per_ds_dir)

    if not files:
        raise RuntimeError("No per-dataset Parquet files fetched")

    cols = set()
    dfs = []

    for f in files:
        df = pd.read_parquet(f)
        df.insert(0, "dataset", f.stem)
        dfs.append(df)
        cols.update(c for c in df.columns if c != "dataset")

    ordered = ["dataset"] + sorted(cols)
    merged = pd.concat([d.reindex(columns=ordered) for d in dfs], ignore_index=True)

    save_df_parquet(merged, merged_parquet)

    # 3) Compute statistics
    rows = [stats_for_dataset(p) for p in files]
    stats_df = pd.DataFrame(rows)
    save_df_parquet(stats_df, stats_parquet)

    return merged_parquet

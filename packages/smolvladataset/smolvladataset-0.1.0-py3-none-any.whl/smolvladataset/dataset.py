"""Dataset loading and splitting utilities.

This module exposes the public API for consumers:

- :class:`SplitConfig` — configuration for deterministic train/val/test splits.
- :class:`SmolVLADataset` — factory that returns three LeRobot-compatible split
  views (train, val, test). It transparently handles downloading/building and
  local caching of the merged dataset and basic statistics.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from lerobot.datasets.lerobot_dataset import LeRobotDataset

from .build import DEFAULT_PRECOMPILED_REPO, build_from_repo_list, download_precompiled
from .cache import cache_paths_for_list
from .utils import (
    default_cache_dir,
    ensure_dir,
    load_df_parquet,
    save_df_parquet,
)


@dataclass(frozen=True)
class SplitConfig:
    """Configuration for train/val/test splits.

    All proportions must sum to 1.0 (within a small tolerance). The same
    ``seed`` guarantees deterministic splits across runs and machines.

    Attributes:
        train: Proportion for the training split (0.0–1.0).
        val: Proportion for the validation split (0.0–1.0).
        test: Proportion for the test split (0.0–1.0).
        seed: Random seed used to shuffle indices per group.
    """

    train: float = 0.8
    val: float = 0.1
    test: float = 0.1
    seed: int = 271828


def _make_splits(
    df: pd.DataFrame, cfg: SplitConfig, by: str = "dataset"
) -> Dict[str, np.ndarray]:
    """Create deterministic train/val/test index arrays.

    Rows are partitioned per group in ``by`` (default: ``"dataset"``) to help
    preserve source balance. Within each group, indices are shuffled using the
    provided seed and then split according to ``cfg`` proportions.

    Args:
        df: Source DataFrame containing all rows.
        cfg: Split configuration with proportions and seed.
        by: Column name to group by before splitting.

    Returns:
        Mapping of split name (``"train"``, ``"val"``, ``"test"``) to a sorted
        NumPy integer index array into ``df``.

    Raises:
        AssertionError: If the configured proportions do not sum to 1.0.
    """
    assert abs(cfg.train + cfg.val + cfg.test - 1.0) < 1e-6

    rng = np.random.RandomState(cfg.seed)

    out = {"train": [], "val": [], "test": []}

    for _, sub in df.groupby(by):
        idx = sub.index.to_numpy()
        rng.shuffle(idx)
        n = len(idx)
        n_tr = int(round(cfg.train * n))
        n_va = int(round(cfg.val * n))
        tr = idx[:n_tr]
        va = idx[n_tr : n_tr + n_va]
        te = idx[n_tr + n_va :]
        out["train"].append(tr)
        out["val"].append(va)
        out["test"].append(te)

    return {
        k: np.sort(np.concatenate(v)) if v else np.array([], dtype=int)
        for k, v in out.items()
    }


class _SplitDataset(LeRobotDataset):
    """LeRobot-compatible view over a DataFrame subset.

    This lightweight wrapper exposes ``__len__`` and ``__getitem__`` to comply
    with the LeRobot dataset protocol. It also provides a read-only ``stats``
    attribute with dataset-level statistics when available.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        indices: np.ndarray,
        stats: Optional[pd.DataFrame] = None,
    ):
        self._df = df
        self._idx = np.asarray(indices, dtype=int)
        self._stats = stats

    def __len__(self) -> int:
        """Return the number of samples in this split."""
        return len(self._idx)

    def __getitem__(self, i: int) -> Dict[str, Any]:
        """Return a single sample as a column dictionary.

        Args:
            i: Position within the split (0 ≤ i < len(self)).

        Returns:
            A mapping of column name to value for the selected row.
        """
        row = self._df.iloc[self._idx[i]]
        return row.to_dict()

    @property
    def stats(self) -> Optional[pd.DataFrame]:
        """Statistics DataFrame for the full dataset, if available."""
        return self._stats


class SmolVLADataset(LeRobotDataset):
    """Factory that returns the (train, val, test) splits.

    This class overrides ``__new__`` to perform all loading/building work and
    returns three :class:`_SplitDataset` instances. It supports either
    downloading a precompiled bundle from the Hugging Face Hub or building
    from a CSV of dataset repository IDs, with automatic local caching.
    """

    def __init__(self, *args, **kwargs):
        """No-op.

        Instances are constructed in :meth:`__new__` which returns the three
        split datasets directly, so ``__init__`` intentionally does nothing.
        """
        # Do not call super().__init__() as this instance is already set up in __new__
        pass

    def __new__(
        cls,
        csv_list: Optional[str] = None,
        *,
        force_download: bool = False,
        force_build: bool = False,
        split_config: Optional[SplitConfig] = None,
    ) -> Tuple[_SplitDataset, _SplitDataset, _SplitDataset]:
        """Load or build the dataset and return all splits.

        Args:
            csv_list: Path to a CSV whose first column lists Hugging Face Hub
                dataset repository IDs (e.g. ``"org/name"``). If omitted, a
                packaged default list is used.
            force_download: Behavior depends on ``csv_list``:
                - With a custom ``csv_list``: rebuild from source even if cache exists.
                - With the default list: re-download the precompiled bundle.
            force_build: Only used when ``csv_list`` is not provided. Build from the
                default list even if a precompiled bundle is available.
            split_config: Split proportions and seed for train/val/test.

        Returns:
            A tuple ``(train, val, test)`` of :class:`_SplitDataset` objects.

        Raises:
            FileNotFoundError: If required cached artifacts could not be created
                or fetched (e.g., ``merged.parquet`` or ``stats.parquet``).
        """
        # Set default split config if not provided
        if split_config is None:
            split_config = SplitConfig()

        # Resolve dataset list; hash determines cache bucket
        csv_list_path = (
            Path(csv_list)
            if csv_list
            else Path(__file__).parent / "data" / "datasets.csv"
        )
        ensure_dir(default_cache_dir())

        # Cache paths (under hash of csv list)
        root, merged_parquet, stats_parquet = cache_paths_for_list(csv_list_path)

        # Check if data already exists in cache
        cache_exists = merged_parquet.exists() and stats_parquet.exists()

        # Decide what to do based on the 5 scenarios:
        # 1. custom CSV + force_download=True -> rebuild from HF sources
        # 2. custom CSV + force_download=False -> check cache, build if missing
        # 3. no CSV + force_download=True -> re-download precompiled
        # 4. no CSV + force_download=False -> check cache, download precompiled if missing
        # 5. no CSV + force_build=True -> build from default datasets.csv
        if csv_list is not None:
            # User provided custom CSV
            if force_download:
                # Scenario 1: custom CSV + force_download=True -> rebuild from HF sources
                build_from_repo_list(csv_list_path, force=True)
            else:
                # Scenario 2: custom CSV + force_download=False -> check cache first
                if not cache_exists:
                    build_from_repo_list(csv_list_path, force=False)
                # else: use existing cache
        else:
            # User didn't provide CSV (use default)
            if force_build:
                # Scenario 5: no CSV + force_build=True -> build from default datasets.csv
                build_from_repo_list(csv_list_path, force=True)
            else:
                if force_download:
                    # Scenario 3: no CSV + force_download=True -> re-download precompiled
                    download_precompiled(csv_list_path, DEFAULT_PRECOMPILED_REPO)
                else:
                    # Scenario 4: no CSV + force_download=False -> check cache first
                    if not cache_exists:
                        download_precompiled(csv_list_path, DEFAULT_PRECOMPILED_REPO)

        # Load merged dataframe
        if not merged_parquet.exists():
            raise FileNotFoundError(
                f"Dataset not found at {merged_parquet}. "
                "The download/build process may have failed."
            )
        df = load_df_parquet(merged_parquet)

        # Load stats dataframe
        if not stats_parquet.exists():
            raise FileNotFoundError(
                f"Stats not found at {stats_parquet}. "
                "The download/build process may have failed."
            )
        stats_df = load_df_parquet(stats_parquet)

        # Generate splits
        splits = _make_splits(df, split_config)

        # Create viewer split Parquet files
        try:
            split_files = {
                "train": root / "train.parquet",
                "val": root / "validation.parquet",  # HF expects 'validation'
                "test": root / "test.parquet",
            }
            if not split_files["train"].exists():
                save_df_parquet(df.iloc[splits["train"]], split_files["train"])
            if not split_files["val"].exists():
                save_df_parquet(df.iloc[splits["val"]], split_files["val"])
            if not split_files["test"].exists():
                save_df_parquet(df.iloc[splits["test"]], split_files["test"])
        except Exception:
            # Non-fatal: writing viewer split files is best-effort
            pass

        return (
            _SplitDataset(df, splits["train"], stats_df),
            _SplitDataset(df, splits["val"], stats_df),
            _SplitDataset(df, splits["test"], stats_df),
        )

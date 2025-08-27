"""Top-level package for smolvladataset.

This library provides a small, focused API to build, cache, and load
the SmolVLA training dataset as LeRobot-compatible splits (train, val,
test). It supports two workflows:

- Download a precompiled bundle from the Hugging Face Hub and cache it
  locally for fast start-up.
- Rebuild the dataset from source repositories listed in a CSV file and
  cache the merged results.

The primary entry point is :class:`~smolvladataset.dataset.SmolVLADataset`,
which returns three split objects implementing the ``LeRobotDataset``
interface.
"""

from .dataset import SmolVLADataset, SplitConfig

__all__ = ["SmolVLADataset", "SplitConfig"]

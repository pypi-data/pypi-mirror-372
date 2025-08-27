# smolvladataset

Simple, reliable loader for SmolVLA robotics datasets with built‑in train/val/test splits and caching.

This library accompanies the SmolVLA paper to help the community inspect how the training dataset is composed, rebuild it from source repositories, and customize the composition or split policy. It can either download a precompiled bundle from the Hugging Face Hub or rebuild locally from a CSV list of dataset repositories.

## Features

- Reproducible train/val/test splits (deterministic seed)
- LeRobot‑compatible splits (`LeRobotDataset` interface)
- Automatic download and local caching (Hugging Face Hub)
- Optional precompiled dataset for fast startup
- Efficient Parquet storage with light schema normalization

## Installation

```bash
pip install smolvladataset
# or using uv
uv add smolvladataset
```

## Requirements

- Python 3.11+
- Core deps: `pandas`, `pyarrow`, `huggingface-hub`, `lerobot`, `datasets`

## Quick Start

```python
from smolvladataset import SmolVLADataset

# Returns (train, val, test) as LeRobot‑compatible datasets
train, val, test = SmolVLADataset()
print(len(train), len(val), len(test))

# Access a row (dict of columns)
sample = train[0]
```

## API

- `SmolVLADataset(csv_list=None, *, force_download=False, force_build=False, split_config=None)`

  - Loads a precompiled bundle (default) or builds from a CSV of source repos and returns a tuple `(train, val, test)`.
  - `csv_list`: Path to CSV whose first column lists HF dataset repo IDs (e.g. `org/name`). If omitted, a packaged default is used.
  - `force_download`: With a custom `csv_list`, rebuild from sources even if cached; otherwise re‑download the precompiled bundle.
  - `force_build`: Only when `csv_list` is omitted: build from the default list instead of downloading the precompiled bundle.
  - `split_config`: Optional `SplitConfig(train=..., val=..., test=..., seed=...)`.

- `SplitConfig(train=0.8, val=0.1, test=0.1, seed=<int>)`
  - Proportions must sum to 1.0. The seed controls deterministic shuffling.
  - If no `split_config` is provided, the default configuration matches the splits published on Hugging Face.

## Advanced Usage

### Custom Dataset List

```python
# Use a CSV file with Hugging Face dataset repo IDs (a packaged default is used if omitted)
train, val, test = SmolVLADataset(csv_list="path/to/datasets.csv")
```

### Custom Split Configuration

```python
from smolvladataset import SmolVLADataset, SplitConfig

config = SplitConfig(train=0.7, val=0.15, test=0.15, seed=123)
train, val, test = SmolVLADataset(split_config=config)
```

### Force Rebuild or Re‑download

```python
# With a custom CSV, forces rebuild from sources
train, val, test = SmolVLADataset(csv_list="data/datasets.csv", force_download=True)

# With the default list, re‑download the precompiled bundle
train, val, test = SmolVLADataset(force_download=True)

# Build from default list instead of using the precompiled bundle
train, val, test = SmolVLADataset(force_build=True)
```

### Cache Directory

Artifacts are cached under `~/.cache/smolvladataset/<hash>/` by default, where `<hash>` depends on the dataset list.

## Dataset List Format

The library expects a CSV file whose first column contains Hugging Face dataset repository IDs:

```csv
dataset_repo_id
org/dataset-1
org/dataset-2
```

Lines beginning with `#` are ignored.

## Cache Layout

- `merged.parquet` — Combined dataset from all sources (includes a `dataset` column)
- `stats.parquet` — Basic per‑source statistics
- `train.parquet`, `validation.parquet`, `test.parquet` — Split files (optional, for HF viewer convenience)

See `LICENSE` for details.

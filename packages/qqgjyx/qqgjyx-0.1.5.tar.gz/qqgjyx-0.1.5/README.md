# qqgjyx

Personal utility toolkit for ML/DL workflows. Lightweight, modular, and designed for personal projects. Ships a clean, sklearn-inspired structure and a unified QQ interface for ergonomics.

## Installation

```bash
pip install qqgjyx
# or pin a version
pip install qqgjyx==0.1.2
```

Requires Python 3.9+.

## Highlights

- Concise, cohesive API with the `QQ` class
- Environment and device utilities
- Reproducibility helpers (seeding)
- Matplotlib styling (scienceplots)
- Dataset helpers (train/val split)
- Sklearn-like structure for long-term maintainability

## Quick start

```python
from qqgjyx import QQ

QQ.help()      # Show available utilities and usage
QQ.env()       # Print environment info
QQ.dev()       # Print device info and return torch.device
QQ.seed(42)    # Set seeds across numpy/torch/lightning
QQ.style()     # Set matplotlib style (scienceplots)

# Example: split a Dataset into train/val
from torch.utils.data import Dataset

class MyDataset(Dataset):
    ...

train_set, val_set = QQ.split(MyDataset(...), val_ratio=0.2, seed=42)
```

## Flat, concise functions (direct imports)

```python
from qqgjyx.helper import env, dev, seed
from qqgjyx.visual import style
from qqgjyx.data import split

env()
device = dev()
seed(123)
style()
```

Backwards-compatible aliases are available:
- `print_environment_info()` → `env()`
- `get_device_info()` → `dev()`
- `set_all_seeds()` → `seed()`
- `set_plt_style()` → `style()`
- `train_val_split()` → `split()`

## Module layout

```
qqgjyx/
  __init__.py      # version and QQ export
  qq.py            # QQ class (unified interface)
  helper.py        # env(), dev(), seed()
  data/
    __init__.py    # split()
    split.py
  visual/
    __init__.py    # style()
    plotting.py
  model/           # placeholder
  graph/           # placeholder
  validator.py     # ensure_between()
  exceptor.py      # QQGJYXError
```

## Demo notebook

See `demo.ipynb` at the repository root for a walk-through of all features.

## Development

Recommended: use a conda env (example: `pkg-dev`).

```bash
conda run -n pkg-dev python -m pip install -e .
conda run -n pkg-dev python -m pytest -q
```

### Release pipeline (script)

Use the automated script to version, test, build, upload, and tag.

```bash
python deploy.py --version 0.1.3 --message "Add new feature"

# or auto-increment patch version
python deploy.py

# options
python deploy.py --skip-tests
python deploy.py --skip-upload
python deploy.py --dry-run
```

Under the hood, it:
- updates versions in `src/qqgjyx/__init__.py` and `pyproject.toml`
- runs tests, builds sdist/wheel, validates with twine
- uploads to PyPI (using local credentials)
- commits and tags the release

## Testing

```bash
conda run -n pkg-dev python -m pytest test/ -v
```

The suite includes core tests that avoid heavy deps and optional comprehensive tests (with mocks).

## License

MIT License. See `LICENSE`.

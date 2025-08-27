"""General helper utilities for environment and reproducibility."""

import platform
import sys
from typing import Optional


def env() -> None:
    """Print information about the environment (imports on demand)."""
    # Lazy imports to avoid heavy deps at import time
    import numpy as np  # type: ignore
    import torch  # type: ignore

    print("\n=== Environment Information ===")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"PyTorch version: {getattr(torch, '__version__', 'N/A')}")
    print(f"NumPy version: {getattr(np, '__version__', 'N/A')}")
    print(f"Platform: {platform.platform()}")
    print("============================\n")


def dev() -> "object":
    """Get information about available computing devices.

    Returns
    -------
    torch.device
        The device that will be used for computations (either 'cuda' or 'cpu')
    """
    import torch  # type: ignore

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("\n=== Device Information ===")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if device.type == "cuda":
        print(f"CUDA version: {torch.version.cuda}")
        print(f"CUDA device count: {torch.cuda.device_count()}")
        print(f"Current CUDA device: {torch.cuda.current_device()}")
        print(f"GPU: {torch.cuda.get_device_name()}")
    print(f"Using device: {device}")
    print("========================\n")
    return device


def seed(seed_value: int = 42) -> int:
    """Set all seeds for reproducibility."""
    import numpy as np  # type: ignore
    import pytorch_lightning as pl  # type: ignore
    import torch  # type: ignore

    print("\n=== Setting Random Seeds ===")
    print(f"Seed value: {seed_value}")
    print("Setting torch CPU seed...")
    torch.manual_seed(seed_value)
    print("Setting torch CUDA seed...")
    torch.cuda.manual_seed_all(seed_value)
    print("Setting numpy seed...")
    np.random.seed(seed_value)
    print("Configuring CUDNN...")
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    print("Configuring PL...")
    pl.seed_everything(seed_value, workers=True)
    print("========================\n")
    return seed_value


__all__ = [
    "env",
    "dev", 
    "seed",
]

# Backward compatibility aliases
print_environment_info = env
get_device_info = dev
set_all_seeds = seed



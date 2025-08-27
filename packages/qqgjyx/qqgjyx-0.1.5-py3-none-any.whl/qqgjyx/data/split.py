"""Dataset utilities."""

from typing import Tuple

from torch.utils.data import Dataset, random_split


def split(train_set: Dataset, val_ratio: float = 0.2, seed: int = 42) -> Tuple[Dataset, Dataset]:
    """
    Split the dataset into training and validation sets.

    Parameters
    ----------
    train_set : Dataset
        The dataset to be split.
    val_ratio : float, optional
        The ratio of the dataset to be used for validation (default is 0.2).
    seed : int, optional
        The seed for random number generation (default is 42).

    Returns
    -------
    Tuple[Dataset, Dataset]
        The training and validation datasets.
    """
    train_set_size = int(len(train_set) * (1 - val_ratio))
    val_set_size = len(train_set) - train_set_size
    generator = torch.Generator().manual_seed(seed)
    train_subset, val_subset = random_split(
        train_set, [train_set_size, val_set_size], generator=generator
    )
    return train_subset, val_subset


__all__ = ["split"]

# Backward compatibility alias
train_val_split = split



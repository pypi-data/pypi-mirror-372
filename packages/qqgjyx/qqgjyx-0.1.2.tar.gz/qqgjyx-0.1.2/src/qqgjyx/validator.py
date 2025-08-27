"""Input validation helpers (placeholder for future utilities)."""

from typing import Any


def ensure_between(value: float, low: float, high: float, name: str = "value") -> float:
    if not (low <= value <= high):
        raise ValueError(f"{name} must be between {low} and {high}, got {value}")
    return value


__all__ = ["ensure_between"]



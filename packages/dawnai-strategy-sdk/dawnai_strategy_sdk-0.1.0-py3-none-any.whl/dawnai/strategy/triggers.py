"""Trigger decorator for strategy methods - only supports cron scheduling."""

from __future__ import annotations

import functools
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, ParamSpec, TypeVar, cast

P = ParamSpec("P")
T = TypeVar("T")


@dataclass
class TriggerConfig:
    """Configuration for a cron trigger."""

    interval: str
    interval_seconds: int
    method_name: str
    method: Callable[..., Any] | None = None


def cron(interval: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator for scheduling a method to run at regular intervals.

    Args:
        interval: Cron-like interval string (e.g., "1m", "5m", "1h", "1d")
                 Supports: s (seconds), m (minutes), h (hours), d (days)

    Example:
        @cron(interval="5m")
        def check_market(self):
            pass

        @cron(interval="1h")
        def hourly_analysis(self):
            pass
    """
    # Parse the interval to seconds for internal use
    match = re.match(r"^(\d+)([smhd])$", interval)
    if not match:
        raise ValueError(f"Invalid interval format: {interval}. Use format like '1m', '5h', '1d'")

    value_str, unit = match.groups()
    value: int = int(value_str)

    # Guard against zero and negative intervals
    if value <= 0:
        raise ValueError(f"Invalid interval value: {value}. Interval must be greater than 0.")

    units_to_seconds: dict[str, int] = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    interval_seconds: int = value * units_to_seconds[unit]

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        """Apply the decorator to a function."""
        # Store trigger metadata on the function
        if not hasattr(func, "_triggers"):
            func._triggers = []  # type: ignore[attr-defined]

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return func(*args, **kwargs)

        # Create trigger config with reference to the wrapper (not the original func)
        trigger_config = TriggerConfig(
            interval=interval,
            interval_seconds=interval_seconds,
            method_name=func.__name__,
            method=wrapper,  # Reference to wrapper, not original func
        )

        # Add trigger config to both original func and wrapper
        func._triggers.append(trigger_config)  # type: ignore[attr-defined]

        # Preserve the trigger metadata on the wrapper
        wrapper._triggers = func._triggers  # type: ignore[attr-defined]

        return cast(Callable[P, T], wrapper)

    return decorator

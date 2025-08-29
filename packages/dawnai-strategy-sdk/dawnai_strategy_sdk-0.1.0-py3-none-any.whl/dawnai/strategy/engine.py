"""Strategy analysis and extraction utilities."""

from __future__ import annotations

import importlib.util
import inspect
import sys
from typing import Any

from .base import Strategy
from .triggers import TriggerConfig


class StrategyAnalyzer:
    """Analyzes a strategy class to extract trigger configurations and methods.

    This class provides utilities to:
    - Extract all triggers from a strategy
    - Map triggers to their corresponding methods
    - Validate strategy configuration
    - Generate strategy metadata
    """

    def __init__(self, strategy_class: type[Strategy]) -> None:
        """Initialize the analyzer.

        Args:
            strategy_class: The strategy class to analyze
        """
        self.strategy_class = strategy_class
        self._triggers_cache: list[TriggerConfig] | None = None

    def get_triggers(self) -> list[TriggerConfig]:
        """Get all trigger configurations from the strategy.

        Returns:
            List of trigger configurations
        """
        if self._triggers_cache is None:
            self._triggers_cache = self.strategy_class._strategy_triggers
        return self._triggers_cache

    def get_trigger_map(self) -> dict[str, dict[str, Any]]:
        """Get a mapping of cron trigger configurations to their methods.

        Returns:
            Dictionary mapping method names to their cron configuration.
            Format:
            {
                "method_name": {
                    "interval": "5m",
                    "interval_seconds": 300,
                    "method_signature": "(self) -> None",
                    "docstring": "Method documentation"
                }
            }
        """
        trigger_map: dict[str, dict[str, Any]] = {}

        for trigger in self.get_triggers():
            # Get method details
            method = getattr(self.strategy_class, trigger.method_name, None)
            if method:
                sig = inspect.signature(method)
                docstring = inspect.getdoc(method) or ""

                trigger_map[trigger.method_name] = {
                    "interval": trigger.interval,
                    "interval_seconds": trigger.interval_seconds,
                    "method_signature": str(sig),
                    "docstring": docstring,
                }

        return trigger_map

    def get_cron_triggers(self) -> list[dict[str, Any]]:
        """Get all cron triggers with their intervals.

        Returns:
            List of cron trigger details
        """
        return [
            {
                "method": t.method_name,
                "interval": t.interval,
                "interval_seconds": t.interval_seconds,
            }
            for t in self.get_triggers()
        ]

    def validate(self) -> list[str]:
        """Validate the strategy configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        return self.strategy_class.validate()

    def get_strategy_info(self) -> dict[str, Any]:
        """Get comprehensive information about the strategy.

        Returns:
            Dictionary containing strategy metadata and configuration
        """
        triggers = self.get_triggers()
        info: dict[str, Any] = {
            "class_name": self.strategy_class.__name__,
            "docstring": inspect.getdoc(self.strategy_class) or "",
            "triggers": self.get_trigger_map(),
            "trigger_count": len(triggers),
            "validation_errors": self.validate(),
        }

        return info

    def create_instance(self) -> Strategy:
        """Create an instance of the strategy.

        Returns:
            Strategy instance
        """
        return self.strategy_class()


def analyze_strategy_file(filepath: str) -> dict[str, Any]:
    """Analyze a strategy from a Python file.

    Args:
        filepath: Path to the Python file containing the strategy

    Returns:
        Dictionary containing strategy information and trigger mappings
    """
    # Load the module from file
    spec = importlib.util.spec_from_file_location("user_strategy", filepath)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load strategy from {filepath}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["user_strategy"] = module
    spec.loader.exec_module(module)

    # Find the Strategy subclass
    strategy_class = None
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and issubclass(obj, Strategy) and obj is not Strategy:
            strategy_class = obj
            break

    if strategy_class is None:
        raise ValueError(f"No Strategy subclass found in {filepath}")

    # Analyze the strategy
    analyzer = StrategyAnalyzer(strategy_class)
    return analyzer.get_strategy_info()


def extract_triggers(strategy_class: type[Strategy]) -> dict[str, dict[str, Any]]:
    """Extract a simple mapping of method names to their cron configurations.

    Args:
        strategy_class: The strategy class to extract triggers from

    Returns:
        Dictionary mapping method names to their cron configuration:
        {
            "method_name": {
                "interval": "5m",
                "interval_seconds": 300,
                "method": <callable>
            }
        }
    """
    trigger_map: dict[str, dict[str, Any]] = {}

    for trigger in strategy_class._strategy_triggers:
        method = getattr(strategy_class, trigger.method_name, None)
        if method:
            trigger_map[trigger.method_name] = {
                "interval": trigger.interval,
                "interval_seconds": trigger.interval_seconds,
                "method": method,
            }

    return trigger_map

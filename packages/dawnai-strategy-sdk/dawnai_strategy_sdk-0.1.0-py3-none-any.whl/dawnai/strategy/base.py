"""Base Strategy class for building trading strategies."""

from __future__ import annotations

import inspect
from abc import ABCMeta
from typing import Any

from .triggers import TriggerConfig


class StrategyMeta(ABCMeta):
    """Metaclass for Strategy to collect trigger methods."""

    def __new__(
        mcs: type[StrategyMeta],
        name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
    ) -> StrategyMeta:
        cls = super().__new__(mcs, name, bases, namespace)

        # Collect all methods with trigger decorators
        triggers: list[TriggerConfig] = []

        for attr_name in dir(cls):
            if attr_name.startswith("_"):
                continue

            try:
                attr = getattr(cls, attr_name)
                if hasattr(attr, "_triggers"):
                    # Add all triggers from this method
                    triggers.extend(attr._triggers)
            except AttributeError:
                continue

        # Store triggers on the class
        cls._strategy_triggers = triggers  # type: ignore[attr-defined]

        return cls


class Strategy(metaclass=StrategyMeta):
    """Base class for all trading strategies.

    Subclasses should define methods decorated with triggers like @cron or @market_price_update.
    The SDK runtime will automatically detect and execute these methods based on their triggers.

    Example:
        class MyStrategy(Strategy):
            def __init__(self):
                super().__init__()
                self.position = 0

            @cron(interval="5m")
            def check_market(self):
                # This runs every 5 minutes
                pass

            @market_price_update(symbol="BTCUSDT")
            def on_price_update(self, price: float):
                # This runs when BTCUSDT price updates
                pass
    """

    _strategy_triggers: list[TriggerConfig]

    def __init__(self) -> None:
        """Initialize the strategy."""
        self._state: dict[str, Any] = {}
        self._initialized: bool = False

    def initialize(self) -> None:
        """Initialize the strategy.

        Override this method to perform any setup required before the strategy starts.
        """
        self._initialized = True

    def shutdown(self) -> None:
        """Shutdown the strategy.

        Override this method to perform any cleanup when the strategy stops.
        """
        pass

    def get_state(self) -> dict[str, Any]:
        """Get the current state of the strategy."""
        return self._state.copy()

    def set_state(self, key: str, value: Any) -> None:
        """Set a state value."""
        self._state[key] = value

    def get_triggers(self) -> list[TriggerConfig]:
        """Get all triggers defined for this strategy."""
        return getattr(self, "_strategy_triggers", [])

    def execute_trigger(self, trigger: TriggerConfig, *args: Any, **kwargs: Any) -> Any:
        """Execute a trigger method.

        Args:
            trigger: The trigger configuration
            *args: Positional arguments for the method
            **kwargs: Keyword arguments for the method

        Returns:
            Result from the trigger method
        """
        if not self._initialized:
            self.initialize()

        method = getattr(self, trigger.method_name)
        return method(*args, **kwargs)

    def buy(self, amount: float, price: float | None = None) -> None:
        """Execute a buy order.

        This is a convenience method that subclasses can override.

        Args:
            amount: Amount to buy
            price: Optional limit price
        """
        # This would need to be configured with actual market details
        raise NotImplementedError("Buy method must be implemented with market details")

    def sell(self, amount: float, price: float | None = None) -> None:
        """Execute a sell order.

        This is a convenience method that subclasses can override.

        Args:
            amount: Amount to sell
            price: Optional limit price
        """
        # This would need to be configured with actual market details
        raise NotImplementedError("Sell method must be implemented with market details")

    @classmethod
    def validate(cls) -> list[str]:
        """Validate the strategy configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors: list[str] = []

        # Check for duplicate trigger definitions
        triggers = cls._strategy_triggers
        seen: dict[str, list[str]] = {}

        for trigger in triggers:
            key = f"cron:{trigger.interval}"
            if key in seen:
                seen[key].append(trigger.method_name)
            else:
                seen[key] = [trigger.method_name]

        for key, methods in seen.items():
            if len(methods) > 1:
                errors.append(f"Duplicate trigger {key} on methods: {', '.join(methods)}")

        # Validate method signatures
        for trigger in triggers:
            method = getattr(cls, trigger.method_name, None)
            if method is None:
                errors.append(f"Method {trigger.method_name} not found")
                continue

            sig = inspect.signature(method)
            params = list(sig.parameters.keys())

            # Remove 'self' parameter
            if params and params[0] == "self":
                params = params[1:]

            # Cron methods should have no required parameters
            if params:
                # Check if all remaining params have defaults
                sig_params = sig.parameters
                for param_name in params:
                    param = sig_params[param_name]
                    if param.default == inspect.Parameter.empty:
                        errors.append(
                            f"Method {trigger.method_name} for cron trigger "
                            f"should not have required parameters (found: {param_name})"
                        )

        return errors

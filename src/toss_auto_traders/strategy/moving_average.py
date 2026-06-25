from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SignalAction = Literal["buy", "sell", "hold"]


@dataclass(frozen=True)
class MovingAverageSignal:
    action: SignalAction
    short_average: float
    long_average: float
    reason: str


def moving_average_signal(
    prices: list[float],
    *,
    short_window: int = 3,
    long_window: int = 5,
) -> MovingAverageSignal:
    if short_window <= 0 or long_window <= 0:
        raise ValueError("Moving average windows must be positive.")
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window.")
    if len(prices) < long_window:
        raise ValueError("Not enough prices for the long moving average window.")

    short_average = sum(prices[-short_window:]) / short_window
    long_average = sum(prices[-long_window:]) / long_window

    if short_average > long_average:
        return MovingAverageSignal(
            action="buy",
            short_average=short_average,
            long_average=long_average,
            reason="Short moving average is above long moving average.",
        )
    if short_average < long_average:
        return MovingAverageSignal(
            action="sell",
            short_average=short_average,
            long_average=long_average,
            reason="Short moving average is below long moving average.",
        )
    return MovingAverageSignal(
        action="hold",
        short_average=short_average,
        long_average=long_average,
        reason="Moving averages are equal.",
    )

import time
from collections.abc import Callable
from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_iso_now() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


class Clock:
    def __init__(self, monotonic: Callable[[], float] = time.monotonic):
        self._monotonic = monotonic

    def now_monotonic(self) -> float:
        return self._monotonic()

    def deadline(self, seconds: float) -> float:
        return self.now_monotonic() + seconds

    def expired(self, deadline: float) -> bool:
        return self.now_monotonic() >= deadline

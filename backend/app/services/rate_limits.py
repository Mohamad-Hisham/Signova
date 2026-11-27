"""Sliding request windows for one backend process."""

from collections import OrderedDict, deque
from math import ceil

from app.utilities.time import Clock

WINDOW_SECONDS = 60


def take_request(times: deque[float], now: float, limit: int) -> int | None:
    cutoff = now - WINDOW_SECONDS
    while times and times[0] <= cutoff:
        times.popleft()
    if len(times) >= limit:
        return max(1, ceil(times[0] + WINDOW_SECONDS - now))
    times.append(now)
    return None


class CreationRateLimiter:
    def __init__(self, clock: Clock, limit: int, max_sources: int = 2048):
        self.clock = clock
        self.limit = limit
        self.max_sources = max_sources
        self._sources: OrderedDict[str, deque[float]] = OrderedDict()

    def take(self, source: str) -> int | None:
        now = self.clock.now_monotonic()
        self.sweep(now)
        times = self._sources.get(source)
        if times is None:
            if len(self._sources) >= self.max_sources:
                return max(
                    1,
                    ceil(next(iter(self._sources.values()))[-1] + WINDOW_SECONDS - now),
                )
            times = self._sources[source] = deque()
        retry_after = take_request(times, now, self.limit)
        if retry_after is None:
            self._sources.move_to_end(source)
        return retry_after

    def sweep(self, now: float) -> None:
        while self._sources:
            source, times = next(iter(self._sources.items()))
            if times[-1] > now - WINDOW_SECONDS:
                break
            del self._sources[source]

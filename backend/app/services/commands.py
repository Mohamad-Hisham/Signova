# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve shared revision/state-version and bounded idempotency coordination.
# Owner: Ali.
# Expected inputs: Authenticated session, UUID key, canonical method/path/body and operation
#   callback intent.
# Expected outputs: Future copied cached success, authorized atomic mutation outcome or safe
#   conflict.
# Responsibilities: Under session lock check expiry/cache/fingerprint/versions/state, cache
#   successful results only, evict oldest and coordinate content-cache purge.
# Connections: All JSON mutation handlers, session/transcript/recognition services and safe
#   error utilities.
# Future implementation: Implement one command policy used by
#   capture/confirm/space/replace/clear/end.
# Rules and limitations: No failure caching, inference/socket await under lock, guessed success
#   after eviction or durable exactly-once claims.
# Expected tests or acceptance: Same key/body one success, changed request 409; parallel
#   confirms consume once; old Start cannot resume after newer Pause; Clear removes cached old
#   text.

from collections import OrderedDict
from collections.abc import Callable
from copy import deepcopy
from typing import Any


class IdempotencyConflict(Exception):
    pass


class RevisionConflict(Exception):
    pass


class StateConflict(Exception):
    pass


class CommandCache:
    def __init__(self, max_entries: int = 60):
        self.max_entries = max_entries
        self._entries: OrderedDict[str, tuple[str, Any]] = OrderedDict()

    def purge(self) -> None:
        self._entries.clear()

    def execute(
        self,
        command_id: str,
        fingerprint: str,
        operation: Callable[[], Any],
    ) -> Any:
        cached = self._entries.get(command_id)
        if cached is not None:
            cached_fingerprint, result = cached
            if cached_fingerprint != fingerprint:
                raise IdempotencyConflict
            return deepcopy(result)

        result = operation()
        self._entries[command_id] = (fingerprint, deepcopy(result))
        self._entries.move_to_end(command_id)

        while len(self._entries) > self.max_entries:
            self._entries.popitem(last=False)

        return deepcopy(result)


def check_revision(record, expected_revision: int) -> None:
    if record.transcript_revision != expected_revision:
        raise RevisionConflict


def check_state_version(record, expected_state_version: int) -> None:
    if record.state_version != expected_state_version:
        raise StateConflict

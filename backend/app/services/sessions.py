"""Temporary sessions, deadlines and content-free tombstones."""

import asyncio
from collections import OrderedDict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from app.schemas.common import ModelMode, SessionStatus
from app.services.commands import CommandCache
from app.utilities.ids import (
    hash_session_token,
    new_session_token,
    new_uuid,
    session_tokens_match,
)
from app.utilities.time import Clock, utc_now

TerminalReason = Literal["user", "idle", "absolute", "reconnect_timeout"]


@dataclass
class SessionRecord:
    session_id: str
    token_hash: str
    mode: ModelMode
    model_version: str
    idle_deadline: float
    absolute_deadline: float
    status: SessionStatus = "paused"
    state_version: int = 0
    transcript_revision: int = 0
    stream_id: str | None = None
    socket_id: str | None = None
    event_seq: int = 0
    recovery_enabled: bool = False
    reconnect_deadline: float | None = None
    end_review_deadline: float | None = None
    items: list[dict] = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    updated_at: datetime = field(default_factory=utc_now)
    command_cache: CommandCache = field(default_factory=CommandCache)
    mutation_times: deque[float] = field(default_factory=deque)


@dataclass(frozen=True)
class Tombstone:
    token_hash: str
    deadline: float
    deleted: bool


class SessionLimitExceeded(Exception):
    pass


class SessionNotFound(Exception):
    pass


class SessionExpired(Exception):
    pass


class SessionDeleted(Exception):
    pass


class SessionStore:
    def __init__(
        self,
        clock: Clock,
        *,
        idle_timeout_seconds: int = 900,
        absolute_timeout_seconds: int = 3600,
        reconnect_grace_seconds: int = 120,
        end_review_seconds: int = 300,
        max_sessions: int = 20,
        tombstone_seconds: int = 120,
        max_tombstones: int = 256,
        on_terminate: Callable[[SessionRecord, TerminalReason], None] | None = None,
    ):
        self.clock = clock
        self.idle_timeout_seconds = idle_timeout_seconds
        self.absolute_timeout_seconds = absolute_timeout_seconds
        self.reconnect_grace_seconds = reconnect_grace_seconds
        self.end_review_seconds = end_review_seconds
        self.max_sessions = max_sessions
        self.tombstone_seconds = tombstone_seconds
        self.max_tombstones = max_tombstones
        self.on_terminate = on_terminate
        self._sessions: dict[str, SessionRecord] = {}
        self._tombstones: OrderedDict[str, Tombstone] = OrderedDict()

    def create(
        self,
        mode: ModelMode,
        *,
        model_version: str,
        recovery_enabled: bool = False,
    ) -> tuple[SessionRecord, str]:
        self.sweep_expired()
        if len(self._sessions) >= self.max_sessions:
            raise SessionLimitExceeded

        session_id = new_uuid()
        token = new_session_token()
        now = self.clock.now_monotonic()
        record = SessionRecord(
            session_id=session_id,
            token_hash=hash_session_token(token),
            mode=mode,
            model_version=model_version,
            recovery_enabled=recovery_enabled,
            idle_deadline=now + self.idle_timeout_seconds,
            absolute_deadline=now + self.absolute_timeout_seconds,
        )
        self._sessions[session_id] = record
        return record, token

    def authenticate(self, session_id: str, token: str) -> SessionRecord:
        record = self._sessions.get(session_id)
        if record is None:
            tombstone = self._tombstone(session_id)
            if tombstone and session_tokens_match(token, tombstone.token_hash):
                self._raise_terminal(tombstone)
            raise SessionNotFound
        if not session_tokens_match(token, record.token_hash):
            raise SessionNotFound
        self.check_current(record)
        return record

    def check_current(self, record: SessionRecord) -> None:
        """Recheck a record after acquiring its command or socket lock."""
        if self._sessions.get(record.session_id) is not record:
            tombstone = self._tombstone(record.session_id)
            if tombstone:
                self._raise_terminal(tombstone)
            raise SessionNotFound
        deadline, reason = self.deadline(record)
        if self.clock.expired(deadline):
            self._terminate(record, reason)
            raise SessionExpired

    def touch_idle(self, record: SessionRecord) -> None:
        record.idle_deadline = self.clock.deadline(self.idle_timeout_seconds)

    def deadline(self, record: SessionRecord) -> tuple[float, TerminalReason]:
        deadlines: list[tuple[float, TerminalReason]] = [
            (record.absolute_deadline, "absolute")
        ]
        if record.end_review_deadline is not None:
            deadlines.append((record.end_review_deadline, "idle"))
        else:
            deadlines.append((record.idle_deadline, "idle"))
            if record.reconnect_deadline is not None:
                deadlines.append((record.reconnect_deadline, "reconnect_timeout"))
        return min(deadlines, key=lambda deadline: deadline[0])

    def mark_ended(self, record: SessionRecord) -> None:
        record.status = "ended"
        record.state_version += 1
        record.stream_id = None
        record.reconnect_deadline = None
        record.end_review_deadline = self.clock.deadline(self.end_review_seconds)
        record.recovery_enabled = False
        record.command_cache.purge()

    def delete(self, record: SessionRecord) -> None:
        self.check_current(record)
        self._terminate(record, "user")

    def sweep_expired(self) -> int:
        now = self.clock.now_monotonic()
        expired = []
        for record in self._sessions.values():
            deadline, reason = self.deadline(record)
            if now >= deadline:
                expired.append((record, reason))
        for record, reason in expired:
            self._terminate(record, reason)
        while self._tombstones:
            session_id, tombstone = next(iter(self._tombstones.items()))
            if now < tombstone.deadline:
                break
            del self._tombstones[session_id]
        return len(expired)

    def shutdown(self) -> None:
        for record in self._sessions.values():
            self._erase_content(record)
        self._sessions.clear()
        self._tombstones.clear()

    def _terminate(self, record: SessionRecord, reason: TerminalReason) -> None:
        del self._sessions[record.session_id]
        self._tombstones[record.session_id] = Tombstone(
            record.token_hash,
            self.clock.deadline(self.tombstone_seconds),
            reason == "user",
        )
        while len(self._tombstones) > self.max_tombstones:
            self._tombstones.popitem(last=False)

        try:
            if self.on_terminate is not None:
                self.on_terminate(record, reason)
        finally:
            self._erase_content(record)

    def _tombstone(self, session_id: str) -> Tombstone | None:
        tombstone = self._tombstones.get(session_id)
        if tombstone is not None and self.clock.expired(tombstone.deadline):
            del self._tombstones[session_id]
            return None
        return tombstone

    @staticmethod
    def _raise_terminal(tombstone: Tombstone) -> None:
        if tombstone.deleted:
            raise SessionDeleted
        raise SessionExpired

    @staticmethod
    def _erase_content(record: SessionRecord) -> None:
        record.items.clear()
        record.command_cache.purge()
        record.mutation_times.clear()
        record.stream_id = None
        record.socket_id = None
        record.recovery_enabled = False

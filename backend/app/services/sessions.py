import asyncio
from dataclasses import dataclass, field
from typing import Literal

from app.utilities.ids import (
    hash_session_token,
    new_session_token,
    new_uuid,
    session_tokens_match,
)
from app.utilities.time import Clock, utc_now


@dataclass
class SessionRecord:
    session_id: str
    token_hash: str
    mode: Literal["alphabet", "word"]
    status: Literal["paused", "capturing", "disconnected", "ended"] = "paused"
    state_version: int = 0
    transcript_revision: int = 0
    stream_id: str | None = None
    recovery_enabled: bool = False
    model_version: str = "unavailable"
    idle_deadline: float = 0
    absolute_deadline: float = 0
    reconnect_deadline: float | None = None
    items: list[dict] = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    created_at: object | None = None
    updated_at: object | None = None
    command_cache: object | None = None


class SessionLimitExceeded(Exception):
    pass


class SessionNotFound(Exception):
    pass


class SessionExpired(Exception):
    pass


class SessionStore:
    def __init__(
        self,
        clock: Clock,
        *,
        idle_timeout_seconds: int = 900,
        absolute_timeout_seconds: int = 3600,
        reconnect_grace_seconds: int = 120,
        max_sessions: int = 20,
    ):
        self.clock = clock
        self.idle_timeout_seconds = idle_timeout_seconds
        self.absolute_timeout_seconds = absolute_timeout_seconds
        self.reconnect_grace_seconds = reconnect_grace_seconds
        self.max_sessions = max_sessions
        self._sessions: dict[str, SessionRecord] = {}

    def create(
        self,
        mode: Literal["alphabet", "word"],
        *,
        recovery_enabled: bool = False,
    ) -> tuple[SessionRecord, str]:
        if len(self._sessions) >= self.max_sessions:
            raise SessionLimitExceeded

        session_id = new_uuid()
        token = new_session_token()
        now = utc_now()
        record = SessionRecord(
            session_id=session_id,
            token_hash=hash_session_token(token),
            mode=mode,
            recovery_enabled=recovery_enabled,
            idle_deadline=self.clock.deadline(self.idle_timeout_seconds),
            absolute_deadline=self.clock.deadline(self.absolute_timeout_seconds),
        )
        record.created_at = now
        record.updated_at = now
        from app.services.commands import CommandCache

        record.command_cache = CommandCache()
        self._sessions[session_id] = record
        return record, token

    def get(self, session_id: str) -> SessionRecord:
        record = self._sessions.get(session_id)
        if record is None:
            raise SessionNotFound
        if self.is_expired(record):
            del self._sessions[session_id]
            raise SessionExpired
        return record

    def authenticate(self, session_id: str, token: str) -> SessionRecord:
        record = self.get(session_id)
        if not session_tokens_match(token, record.token_hash):
            raise SessionNotFound
        return record

    def touch_idle(self, record: SessionRecord) -> None:
        record.idle_deadline = self.clock.deadline(self.idle_timeout_seconds)

    def is_expired(self, record: SessionRecord) -> bool:
        deadlines = [record.absolute_deadline, record.idle_deadline]
        if record.reconnect_deadline is not None:
            deadlines.append(record.reconnect_deadline)
        return any(self.clock.expired(deadline) for deadline in deadlines)

    def delete(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def sweep_expired(self) -> int:
        expired_ids = [
            session_id
            for session_id, record in self._sessions.items()
            if self.is_expired(record)
        ]
        for session_id in expired_ids:
            del self._sessions[session_id]
        return len(expired_ids)

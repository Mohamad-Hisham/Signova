# Owner: Ali.

import hashlib
import hmac
import secrets
import uuid


def new_uuid() -> str:
    return str(uuid.uuid4())


def validate_uuid(value: str) -> str:
    parsed = uuid.UUID(value)
    if parsed.version != 4:
        raise ValueError("UUID must be version 4")
    if str(parsed) != value.lower():
        raise ValueError("UUID must use canonical lowercase form")
    return str(parsed)


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def session_tokens_match(provided_token: str, stored_hash: str) -> bool:
    provided_hash = hash_session_token(provided_token)
    return hmac.compare_digest(provided_hash, stored_hash)

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.events import (
    AuthMessage,
    FrameMessage,
    PingMessage,
    ServerEnvelope,
)


def test_valid_auth_message():
    message = AuthMessage(
        protocol_version=1,
        type="auth",
        session_token="test-token",
        last_event_seq=4,
    )

    assert message.protocol_version == 1
    assert message.type == "auth"
    assert message.last_event_seq == 4


@pytest.mark.parametrize(
    "data",
    [
        {
            "protocol_version": 2,
            "type": "auth",
            "session_token": "test-token",
        },
        {
            "protocol_version": 1,
            "type": "auth",
            "session_token": "",
        },
        {
            "protocol_version": 1,
            "type": "auth",
            "session_token": "test-token",
            "last_event_seq": -1,
        },
        {
            "protocol_version": 1,
            "type": "auth",
            "session_token": "test-token",
            "last_event_seq": "4",
        },
        {
            "protocol_version": 1,
            "type": "auth",
            "session_token": "test-token",
            "unknown": "rejected",
        },
    ],
)
def test_invalid_auth_message(data):
    with pytest.raises(ValidationError):
        AuthMessage(**data)


def test_valid_frame_message():
    message = FrameMessage(
        protocol_version=1,
        type="frame",
        stream_id="stream-1",
        frame_seq=1,
        capture_ms=100,
        width=640,
        height=480,
        mirrored=False,
        image_b64="AAAA",
    )

    assert message.frame_seq == 1
    assert message.width == 640
    assert message.height == 480


@pytest.mark.parametrize(
    "data",
    [
        {
            "protocol_version": 2,
            "type": "frame",
            "stream_id": "stream-1",
            "frame_seq": 1,
            "capture_ms": 100,
            "width": 640,
            "height": 480,
            "mirrored": False,
            "image_b64": "AAAA",
        },
        {
            "protocol_version": 1,
            "type": "frame",
            "stream_id": "stream-1",
            "frame_seq": 0,
            "capture_ms": 100,
            "width": 640,
            "height": 480,
            "mirrored": False,
            "image_b64": "AAAA",
        },
        {
            "protocol_version": 1,
            "type": "frame",
            "stream_id": "stream-1",
            "frame_seq": 1,
            "capture_ms": -1,
            "width": 640,
            "height": 480,
            "mirrored": False,
            "image_b64": "AAAA",
        },
        {
            "protocol_version": 1,
            "type": "frame",
            "stream_id": "stream-1",
            "frame_seq": 1,
            "capture_ms": 100,
            "width": 641,
            "height": 480,
            "mirrored": False,
            "image_b64": "AAAA",
        },
        {
            "protocol_version": 1,
            "type": "frame",
            "stream_id": "stream-1",
            "frame_seq": 1,
            "capture_ms": 100,
            "width": 640,
            "height": 481,
            "mirrored": False,
            "image_b64": "AAAA",
        },
        {
            "protocol_version": 1,
            "type": "frame",
            "stream_id": "stream-1",
            "frame_seq": 1,
            "capture_ms": 100,
            "width": 640,
            "height": 480,
            "mirrored": True,
            "image_b64": "AAAA",
        },
        {
            "protocol_version": 1,
            "type": "frame",
            "stream_id": "stream-1",
            "frame_seq": 1,
            "capture_ms": 100,
            "width": 640,
            "height": 480,
            "mirrored": False,
            "image_b64": "",
        },
        {
            "protocol_version": 1,
            "type": "frame",
            "stream_id": "stream-1",
            "frame_seq": 1,
            "capture_ms": 100,
            "width": 640,
            "height": 480,
            "mirrored": False,
            "image_b64": "AAAA",
            "unknown": "rejected",
        },
    ],
)
def test_invalid_frame_message(data):
    with pytest.raises(ValidationError):
        FrameMessage(**data)


def test_valid_ping_message():
    message = PingMessage(
        protocol_version=1,
        type="ping",
        nonce="heartbeat-1",
    )

    assert message.nonce == "heartbeat-1"


@pytest.mark.parametrize(
    "nonce",
    [
        "",
        "x" * 65,
    ],
)
def test_invalid_ping_nonce(nonce):
    with pytest.raises(ValidationError):
        PingMessage(
            protocol_version=1,
            type="ping",
            nonce=nonce,
        )


def test_valid_server_envelope():
    message = ServerEnvelope(
        protocol_version=1,
        type="pong",
        event_id="event-1",
        event_seq=0,
        session_id="session-1",
        at=datetime.now(UTC),
        data={"nonce": "heartbeat-1"},
    )

    assert message.event_seq == 0
    assert message.type == "pong"


@pytest.mark.parametrize(
    "data",
    [
        {
            "protocol_version": 2,
            "type": "pong",
            "event_id": "event-1",
            "event_seq": 0,
            "session_id": "session-1",
            "at": datetime.now(UTC),
            "data": {},
        },
        {
            "protocol_version": 1,
            "type": "pong",
            "event_id": "event-1",
            "event_seq": -1,
            "session_id": "session-1",
            "at": datetime.now(UTC),
            "data": {},
        },
        {
            "protocol_version": 1,
            "type": "pong",
            "event_id": "event-1",
            "event_seq": "0",
            "session_id": "session-1",
            "at": datetime.now(UTC),
            "data": {},
        },
        {
            "protocol_version": 1,
            "type": "pong",
            "event_id": "",
            "event_seq": 0,
            "session_id": "session-1",
            "at": datetime.now(UTC),
            "data": {},
        },
        {
            "protocol_version": 1,
            "type": "pong",
            "event_id": "event-1",
            "event_seq": 0,
            "session_id": "",
            "at": datetime.now(UTC),
            "data": {},
        },
        {
            "protocol_version": 1,
            "type": "pong",
            "event_id": "event-1",
            "event_seq": 0,
            "session_id": "session-1",
            "at": datetime.now(),
            "data": {},
        },
        {
            "protocol_version": 1,
            "type": "pong",
            "event_id": "event-1",
            "event_seq": 0,
            "session_id": "session-1",
            "at": datetime.now(UTC),
            "data": {},
            "unknown": "rejected",
        },
    ],
)
def test_invalid_server_envelope(data):
    with pytest.raises(ValidationError):
        ServerEnvelope(**data)

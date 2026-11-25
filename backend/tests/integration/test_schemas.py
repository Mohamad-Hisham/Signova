from datetime import UTC, datetime

from pydantic import ValidationError

from app.schemas.common import Candidate, Item, Session, Transcript

now = datetime.now(UTC)
item = Item(
    item_id="item-1",
    text="ماء",
    kind="word",
    source="model",
    label_id="WORD_WATER",
    score=0.94,
    model_version="word-1",
    confirmed_by="manual",
    created_at=now,
)

transcript = Transcript(
    revision=1,
    items=[item],
    text="ماء",
    updated_at=now,
)

session = Session(
    session_id="session-1",
    mode="word",
    status="paused",
    state_version=0,
    expires_at=now,
    absolute_expires_at=now,
    idle_timeout_seconds=900,
    reconnect_grace_seconds=120,
    model_version="word-1",
    stream_id=None,
    recovery_enabled=False,
    transcript=transcript,
)

candidate = Candidate(
    candidate_id="candidate-1",
    stream_id="stream-1",
    mode="word",
    label_id="WORD_WATER",
    text="ماء",
    score=0.94,
    stable=True,
    eligible=True,
    expires_in_ms=2000,
    model_version="word-1",
)

assert session.transcript.items[0].text == "ماء"
assert candidate.score == 0.94

invalid_cases = [
    {"mode": "speech"},
    {"mode": "word", "text": "ماء", "score": True},
    {"mode": "word", "text": "ماء", "score": float("nan")},
]

for case in invalid_cases:
    try:
        Candidate(
            candidate_id="candidate-invalid",
            stream_id="stream-1",
            mode=case.get("mode"),
            label_id="WORD_WATER",
            text=case.get("text", "ماء"),
            score=case.get("score", 0.5),
            stable=True,
            eligible=True,
            expires_in_ms=2000,
            model_version="word-1",
            unexpected="rejected",
        )
    except ValidationError:
        pass
    else:
        raise AssertionError(f"Invalid candidate data was accepted: {case}")

try:
    Transcript(
        revision=True,
        items=[item],
        text="ماء",
        updated_at=now,
    )
except ValidationError:
    pass
else:
    raise AssertionError("Boolean transcript revision was accepted")

print("Common schemas passed all manual checks.")

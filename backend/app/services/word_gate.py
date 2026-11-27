"""Track stability and deliberate release for manual recognition."""

from enum import Enum

from app.models.base import Prediction
from app.utilities.time import Clock


class WordGateState(str, Enum):
    WAIT_RELEASE = "WAIT_RELEASE"
    IDLE = "IDLE"
    TRACKING = "TRACKING"
    ELIGIBLE = "ELIGIBLE"
    LOCKED = "LOCKED"


class WordGate:
    def __init__(
        self,
        clock: Clock,
        *,
        entry_score: float = 0.85,
        exit_score: float = 0.65,
        stability_seconds: float = 0.300,
        neutral_dwell_seconds: float = 0.300,
        minimum_observations: int = 3,
        candidate_freshness_seconds: float = 2.0,
        manual_mode: bool = True,
    ):
        self.clock = clock
        self.entry_score = entry_score
        self.exit_score = exit_score
        self.stability_seconds = stability_seconds
        self.neutral_dwell_seconds = neutral_dwell_seconds
        self.minimum_observations = minimum_observations
        self.candidate_freshness_seconds = candidate_freshness_seconds
        self.manual_mode = manual_mode
        self.reset()

    def reset(self, *, manual: bool | None = None) -> None:
        if manual is not None:
            self.manual_mode = manual
        self.state = (
            WordGateState.IDLE if self.manual_mode else WordGateState.WAIT_RELEASE
        )
        self.active_label: str | None = None
        self.observation_count = 0
        self.tracking_start = 0.0
        self.neutral_start: float | None = None
        self.candidate: Prediction | None = None
        self.candidate_deadline = 0.0

    def break_continuity(self) -> None:
        self.active_label = None
        self.observation_count = 0
        self.tracking_start = 0.0
        self.neutral_start = None
        self.candidate = None
        self.candidate_deadline = 0.0
        if self.state not in (WordGateState.LOCKED, WordGateState.WAIT_RELEASE):
            self.state = WordGateState.IDLE

    def update(self, prediction: Prediction | None) -> Prediction | None:
        now = self.clock.now_monotonic()
        if self.candidate is not None and now >= self.candidate_deadline:
            self.break_continuity()

        if prediction is not None and prediction.neutral:
            if self.state in (WordGateState.LOCKED, WordGateState.WAIT_RELEASE):
                if self.neutral_start is None:
                    self.neutral_start = now
                if now - self.neutral_start + 1e-9 >= self.neutral_dwell_seconds:
                    self.break_continuity()
                    self.state = WordGateState.IDLE
            else:
                self.break_continuity()
            return None

        self.neutral_start = None
        if self.state in (WordGateState.LOCKED, WordGateState.WAIT_RELEASE):
            return None
        if prediction is None or not prediction.usable or prediction.label_id is None:
            self.break_continuity()
            return None

        same_label = prediction.label_id == self.active_label
        if not same_label:
            self.break_continuity()
        threshold = (
            self.exit_score
            if self.state == WordGateState.ELIGIBLE
            else self.entry_score
        )
        if prediction.score < threshold:
            self.break_continuity()
            return None

        if not same_label:
            self.active_label = prediction.label_id
            self.state = WordGateState.TRACKING
            self.tracking_start = now
        self.observation_count += 1
        if (
            self.observation_count >= self.minimum_observations
            and now - self.tracking_start + 1e-9 >= self.stability_seconds
        ):
            self.state = WordGateState.ELIGIBLE
            self.candidate = prediction
            self.candidate_deadline = now + self.candidate_freshness_seconds
        return self.candidate

    def eligible_candidate(self) -> Prediction | None:
        if self.candidate is not None and self.clock.expired(self.candidate_deadline):
            self.break_continuity()
        return self.candidate

    def lock_segment(self) -> None:
        self.break_continuity()
        self.state = WordGateState.LOCKED

    def confirm_once(self) -> Prediction | None:
        candidate = self.eligible_candidate()
        if candidate is not None:
            self.lock_segment()
        return candidate

# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve deterministic word stability, evaluated release and segment-latch state
#   transitions.
# Owner: Basel.
# Expected inputs: Usable current word observations, monotonic time, approved policy and
#   explicit manual boundaries.
# Expected outputs: Future preview eligibility and at-most-once commit intention for a segment.
# Responsibilities: Track WAIT_RELEASE/IDLE/TRACKING/ELIGIBLE/LOCKED, freshness and neutral
#   dwell; preserve deliberate repeats after valid new segments.
# Connections: recognition.py, transcript atomic commit, Bavly adapter evidence and session
#   reset lifecycle.
# Future implementation: Implement timing/state gate only after Bavly neutral/live-window
#   evidence and Hisham policy approval.
# Rules and limitations: Low score/no hand/unknown/gap is not neutral; Pause/disconnect discard;
#   automatic policy disabled without evidence.
# Expected tests or acceptance: Hold→one confirm once; release→same word twice; changing label
#   while locked cannot bypass release; stale candidate/invalid continuity never auto-commit.

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
        automatic_completion: bool = False,
        entry_score: float = 0.85,
        exit_score: float = 0.65,
        stability_seconds: float = 0.300,
        neutral_dwell_seconds: float = 0.300,
        minimum_observations: int = 3,
        candidate_freshness_seconds: float = 2.0,
        manual_mode: bool = True,
    ):
        self.clock = clock
        self.automatic_completion = automatic_completion
        self.entry_score = entry_score
        self.exit_score = exit_score
        self.stability_seconds = stability_seconds
        self.neutral_dwell_seconds = neutral_dwell_seconds
        self.minimum_observations = minimum_observations
        self.candidate_freshness_seconds = candidate_freshness_seconds
        self.manual_mode = manual_mode
        self.reset(manual=manual_mode)

    def reset(self, *, manual: bool | None = None) -> None:
        if manual is not None:
            self.manual_mode = manual
        self.state = (
            WordGateState.IDLE if self.manual_mode else WordGateState.WAIT_RELEASE
        )
        self.active_label = None
        self.observation_count = 0
        self.tracking_start = 0.0
        self.neutral_start = None
        self.candidate = None
        self.candidate_deadline = 0.0
        self.committed_segment = False

    def update(self, prediction: Prediction | None) -> Prediction | None:
        now = self.clock.now_monotonic()

        if self.candidate is not None and now >= self.candidate_deadline:
            self.candidate = None
            self.candidate_deadline = 0.0
            if self.state == WordGateState.ELIGIBLE:
                self.state = WordGateState.IDLE

        if prediction is None or not prediction.usable:
            self.active_label = None
            self.observation_count = 0
            self.tracking_start = 0.0
            if self.state == WordGateState.TRACKING:
                self.state = WordGateState.IDLE
            return None

        if prediction.neutral:
            if self.state == WordGateState.LOCKED:
                if self.neutral_start is None:
                    self.neutral_start = now
                elif now - self.neutral_start + 1e-9 >= self.neutral_dwell_seconds:
                    self.state = (
                        WordGateState.IDLE
                        if self.manual_mode
                        else WordGateState.WAIT_RELEASE
                    )
                    self.active_label = None
                    self.observation_count = 0
                    self.tracking_start = 0.0
                    self.candidate = None
                    self.candidate_deadline = 0.0
                    self.committed_segment = False
                    self.neutral_start = None
            else:
                self.neutral_start = None
            return None

        if prediction.label_id is None:
            return None
        if self.state == WordGateState.LOCKED:
            return None

        if (
            self.active_label != prediction.label_id
            or prediction.score < self.exit_score
        ):
            self.active_label = prediction.label_id
            self.observation_count = 1
            self.tracking_start = now
            self.state = WordGateState.TRACKING
            return None

        if prediction.score < self.entry_score:
            self.state = WordGateState.TRACKING
            return None

        self.observation_count += 1
        elapsed = now - self.tracking_start
        if (
            self.observation_count >= self.minimum_observations
            and elapsed >= self.stability_seconds
        ):
            self.candidate = prediction
            self.candidate_deadline = now + self.candidate_freshness_seconds
            self.state = WordGateState.ELIGIBLE

        return self.candidate

    def confirm_once(self) -> Prediction | None:
        if self.candidate is None:
            return None
        now = self.clock.now_monotonic()
        if now >= self.candidate_deadline:
            self.candidate = None
            self.candidate_deadline = 0.0
            self.state = WordGateState.IDLE
            return None
        if self.committed_segment:
            return None

        confirmed = self.candidate
        self.committed_segment = True
        self.state = WordGateState.LOCKED
        self.candidate = None
        self.candidate_deadline = 0.0
        return confirmed

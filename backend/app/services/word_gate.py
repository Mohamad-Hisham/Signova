# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve deterministic word stability, evaluated release and segment-latch state
#   transitions.
# Owner: Ali.
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

# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve public /api/v1/health/live and /health/ready REST boundaries.
# Owner: Ali.
# Expected inputs: Application liveness and trusted per-mode startup/golden readiness state.
# Expected outputs: Future alive 200 or ready 200/503 with documented non-error readiness shape.
# Responsibilities: Keep process liveness separate from release-required model availability
#   without invoking inference per health request.
# Connections: main lifecycle, config release-required modes and model registry readiness.
# Future implementation: Implement thin route serialization during backend work.
# Rules and limitations: No artifact filesystem paths, secrets, fake substitutions or model
#   computation in liveness.
# Expected tests or acceptance: Unready required mode returns 503 with
#   ready/modes/required_modes; live can remain 200.

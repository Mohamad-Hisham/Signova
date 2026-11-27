import { describe, expect, it } from "vitest";
import {
  CandidateSchema,
  mergeSnapshot,
  SessionSchema,
  type Session,
} from "../api/contracts";
import {
  initialTranslatorState,
  sessionReducer,
} from "../app/sessionReducer";

const timestamp = "2026-11-27T12:00:00Z";

function session(
  revision: number,
  text: string,
  stateVersion = 2,
  status: Session["status"] = "capturing",
  streamId: string | null = "stream-1",
): Session {
  return SessionSchema.parse({
    session_id: "session-1",
    mode: "alphabet",
    status,
    state_version: stateVersion,
    expires_at: "2026-11-27T12:15:00Z",
    absolute_expires_at: "2026-11-27T13:00:00Z",
    idle_timeout_seconds: 900,
    reconnect_grace_seconds: 120,
    model_version: "alphabet-test-v1",
    stream_id: streamId,
    recovery_enabled: false,
    transcript: {
      revision,
      text,
      updated_at: timestamp,
      items: text
        ? [
            {
              item_id: "item-1",
              text,
              kind: "letter",
              source: "model",
              label_id: "letter-ba",
              score: 0.9,
              model_version: "alphabet-test-v1",
              confirmed_by: "manual",
              created_at: timestamp,
            },
          ]
        : [],
    },
  });
}

function candidate(streamId = "stream-1") {
  return CandidateSchema.parse({
    candidate_id: "candidate-1",
    stream_id: streamId,
    mode: "alphabet",
    label_id: "letter-ba",
    text: "ب",
    score: 0.9,
    stable: true,
    eligible: true,
    expires_in_ms: 1000,
    model_version: "alphabet-test-v1",
  });
}

describe("translator snapshot and preview state", () => {
  it("keeps candidate previews out of the confirmed transcript", () => {
    const active = session(0, "");
    const state = sessionReducer(
      initialTranslatorState("alphabet"),
      { type: "SNAPSHOT", session: active },
    );
    const next = sessionReducer(state, {
      type: "CANDIDATE",
      candidate: candidate(),
      deadline: 1000,
    });

    expect(next.candidate?.text).toBe("ب");
    expect(next.session?.transcript.items).toHaveLength(0);
    expect(next.session?.transcript.text).toBe("");
  });

  it("rejects a candidate from an obsolete stream", () => {
    const state = sessionReducer(
      initialTranslatorState("alphabet"),
      { type: "SNAPSHOT", session: session(0, "") },
    );
    const next = sessionReducer(state, {
      type: "CANDIDATE",
      candidate: candidate("old-stream"),
      deadline: 1000,
    });

    expect(next.candidate).toBeNull();
  });

  it("does not roll back text when a newer capture state carries an older revision", () => {
    const current = session(2, "باب", 4, "paused", null);
    const nextCaptureState = session(1, "old", 5, "capturing", "stream-2");
    const merged = mergeSnapshot(current, nextCaptureState);

    expect(merged.state_version).toBe(5);
    expect(merged.status).toBe("capturing");
    expect(merged.transcript.revision).toBe(2);
    expect(merged.transcript.text).toBe("باب");
  });

  it("does not restore content after the local deletion barrier is terminal", () => {
    const stateWithText = sessionReducer(
      initialTranslatorState("alphabet"),
      { type: "SNAPSHOT", session: session(1, "ب", 3, "paused", null) },
    );
    const deleted = sessionReducer(stateWithText, {
      type: "TERMINAL",
      value: "deleted",
    });
    const lateSnapshot = sessionReducer(deleted, {
      type: "SNAPSHOT",
      session: session(2, "باب", 4, "paused", null),
    });

    expect(lateSnapshot.session).toBeNull();
    expect(lateSnapshot.hiddenTranscript).toBe(true);
  });

  it("tracks readiness independently for each recognition mode", () => {
    const state = sessionReducer(initialTranslatorState("alphabet"), {
      type: "CATALOGUE_READY",
      models: [
        {
          mode: "alphabet",
          model_version: "alphabet-v1",
          ready: false,
          confirmation_policy: "manual",
          input: null,
          transcript_limits: { max_items: 500, max_characters: 2000 },
        },
        {
          mode: "word",
          model_version: "word-v1",
          ready: true,
          confirmation_policy: "manual",
          input: {
            format: "jpeg",
            max_width: 640,
            max_height: 480,
            max_jpeg_bytes: 163840,
            max_message_bytes: 262144,
            max_fps: 10,
            required_sample_fps: null,
            window_samples: 1,
            mirrored: false,
          },
          transcript_limits: { max_items: 500, max_characters: 2000 },
        },
      ],
    });

    expect(state.models.alphabet?.ready).toBe(false);
    expect(state.models.word?.ready).toBe(true);
    expect(state.backendStatus).toBe("online");
  });
});

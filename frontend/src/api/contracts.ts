import { z } from "zod";

export const ModeSchema = z.enum(["word", "alphabet"]);
export type Mode = z.infer<typeof ModeSchema>;

const NonNegativeInt = z.number().int().nonnegative();
const NonEmpty = z.string().min(1);

export const ItemSchema = z.object({
  item_id: NonEmpty,
  text: z.string(),
  kind: z.enum(["word", "letter", "space", "manual"]),
  source: z.enum(["model", "user"]),
  label_id: z.string().nullable(),
  score: z.number().finite().min(0).max(1).nullable(),
  model_version: z.string().nullable(),
  confirmed_by: z.enum(["auto", "manual", "edit"]),
  created_at: NonEmpty,
});

export const TranscriptSchema = z.object({
  revision: NonNegativeInt,
  items: z.array(ItemSchema),
  text: z.string(),
  updated_at: NonEmpty,
});

export const SessionSchema = z.object({
  session_id: NonEmpty,
  mode: ModeSchema,
  status: z.enum(["paused", "capturing", "disconnected", "ended"]),
  state_version: NonNegativeInt,
  expires_at: NonEmpty,
  absolute_expires_at: NonEmpty,
  idle_timeout_seconds: z.number().positive(),
  reconnect_grace_seconds: z.number().positive(),
  model_version: NonEmpty,
  stream_id: z.string().nullable(),
  recovery_enabled: z.boolean(),
  transcript: TranscriptSchema,
});

export const CandidateSchema = z.object({
  candidate_id: NonEmpty,
  stream_id: NonEmpty,
  mode: ModeSchema,
  label_id: NonEmpty,
  text: NonEmpty,
  score: z.number().finite().min(0).max(1),
  stable: z.boolean(),
  eligible: z.boolean(),
  expires_in_ms: NonNegativeInt,
  model_version: NonEmpty,
});

export const InputLimitsSchema = z.object({
  format: z.literal("jpeg"),
  max_width: z.number().int().positive(),
  max_height: z.number().int().positive(),
  max_jpeg_bytes: z.number().int().positive(),
  max_message_bytes: z.number().int().positive(),
  max_fps: z.number().int().positive(),
  required_sample_fps: z.number().positive().nullable(),
  window_samples: z.number().int().positive(),
  mirrored: z.literal(false),
});

export const ModelEntrySchema = z.object({
  mode: ModeSchema,
  model_version: NonEmpty,
  ready: z.boolean(),
  confirmation_policy: z.enum(["manual", "automatic_with_manual_fallback"]),
  input: InputLimitsSchema.nullable(),
  transcript_limits: z.object({
    max_items: z.number().int().positive(),
    max_characters: z.number().int().positive(),
  }),
});

export const ModelCatalogueSchema = z.object({
  models: z.array(ModelEntrySchema),
});

export const VocabularySchema = z.object({
  mode: ModeSchema,
  model_version: NonEmpty,
  labels: z.array(
    z.object({
      label_id: NonEmpty,
      text: NonEmpty,
      kind: z.enum(["word", "letter"]),
    }),
  ),
});

export const ServerEnvelopeSchema = z.object({
  protocol_version: z.literal(1),
  type: NonEmpty,
  event_id: NonEmpty,
  event_seq: NonNegativeInt,
  session_id: NonEmpty,
  at: NonEmpty,
  data: z.unknown(),
});

const SnapshotData = z.object({ session: SessionSchema });

export function parseLiveEvent(value: unknown, expectedSessionId: string) {
  const envelope = ServerEnvelopeSchema.parse(value);
  if (envelope.session_id !== expectedSessionId) {
    throw new Error("WRONG_SESSION");
  }

  let data: unknown;
  switch (envelope.type) {
    case "session.ready":
      data = SnapshotData.extend({
        confirmation_policy: z.enum([
          "manual",
          "automatic_with_manual_fallback",
        ]),
      }).parse(envelope.data);
      break;
    case "session.state":
      data = SnapshotData.extend({
        reason: z.enum(["start", "pause", "limit", "mode_changed"]),
      }).parse(envelope.data);
      break;
    case "candidate.updated":
      data = z.object({ candidate: CandidateSchema.nullable() }).parse(envelope.data);
      break;
    case "frame.ack":
      data = z.object({
        stream_id: NonEmpty,
        frame_seq: z.number().int().positive(),
        outcome: z.enum(["processed", "discarded"]),
        reason: z.string().nullable(),
        processing_ms: z.number().finite().nonnegative(),
      }).parse(envelope.data);
      break;
    case "transcript.updated":
      data = SnapshotData.extend({
        cause: z.enum(["commit", "replace", "clear", "space"]),
        command_id: z.string().nullable(),
        committed_item_id: z.string().nullable(),
      }).parse(envelope.data);
      break;
    case "pong":
      data = z.object({ nonce: NonEmpty }).parse(envelope.data);
      break;
    case "warning":
      data = z.object({
        code: NonEmpty,
        message: NonEmpty,
        frame_seq: z.number().int().positive().nullable(),
      }).parse(envelope.data);
      break;
    case "error":
      data = z.object({
        error: z.object({
          code: NonEmpty,
          message: NonEmpty,
          retryable: z.boolean(),
          details: z.record(z.string(), z.unknown()),
        }),
        request_id: NonEmpty,
        related_frame_seq: z.number().int().positive().nullable(),
        command_id: z.null(),
      }).parse(envelope.data);
      break;
    case "session.ended":
      data = SnapshotData.extend({ reason: z.literal("user") }).parse(envelope.data);
      break;
    case "session.expired":
      data = z.object({
        reason: z.enum(["idle", "absolute", "reconnect_timeout"]),
      }).parse(envelope.data);
      break;
    case "session.deleted":
      data = z.object({ reason: z.literal("user") }).parse(envelope.data);
      break;
    default:
      throw new Error("UNKNOWN_LIVE_EVENT");
  }

  return { ...envelope, data } as LiveEvent;
}

export type Session = z.infer<typeof SessionSchema>;
export type Transcript = z.infer<typeof TranscriptSchema>;
export type TranscriptItem = z.infer<typeof ItemSchema>;
export type Candidate = z.infer<typeof CandidateSchema>;
export type InputLimits = z.infer<typeof InputLimitsSchema>;
export type ModelEntry = z.infer<typeof ModelEntrySchema>;
export type ModelCatalogue = z.infer<typeof ModelCatalogueSchema>;
export type Vocabulary = z.infer<typeof VocabularySchema>;

type LiveBase = z.infer<typeof ServerEnvelopeSchema>;
export type LiveEvent = Omit<LiveBase, "type" | "data"> &
  (
    | {
        type: "session.ready";
        data: { session: Session; confirmation_policy: ModelEntry["confirmation_policy"] };
      }
    | {
        type: "session.state";
        data: {
          session: Session;
          reason: "start" | "pause" | "limit" | "mode_changed";
        };
      }
    | { type: "candidate.updated"; data: { candidate: Candidate | null } }
    | {
        type: "frame.ack";
        data: {
          stream_id: string;
          frame_seq: number;
          outcome: "processed" | "discarded";
          reason: string | null;
          processing_ms: number;
        };
      }
    | {
        type: "transcript.updated";
        data: {
          session: Session;
          cause: "commit" | "replace" | "clear" | "space";
          command_id: string | null;
          committed_item_id: string | null;
        };
      }
    | { type: "pong"; data: { nonce: string } }
    | {
        type: "warning";
        data: { code: string; message: string; frame_seq: number | null };
      }
    | {
        type: "error";
        data: {
          error: {
            code: string;
            message: string;
            retryable: boolean;
            details: Record<string, unknown>;
          };
          request_id: string;
          related_frame_seq: number | null;
          command_id: null;
        };
      }
    | { type: "session.ended"; data: { session: Session; reason: "user" } }
    | {
        type: "session.expired";
        data: { reason: "idle" | "absolute" | "reconnect_timeout" };
      }
    | { type: "session.deleted"; data: { reason: "user" } }
  );

export function mergeSnapshot(current: Session | null, next: Session): Session {
  if (!current || current.session_id !== next.session_id) {
    return current ?? next;
  }
  const newerState = next.state_version > current.state_version;
  return {
    ...(newerState ? next : current),
    transcript:
      next.transcript.revision > current.transcript.revision
        ? next.transcript
        : current.transcript,
  };
}

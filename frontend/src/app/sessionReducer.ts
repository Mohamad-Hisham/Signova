import {
  mergeSnapshot,
  type Candidate,
  type Mode,
  type ModelEntry,
  type Session,
} from "../api/contracts";
import type { CameraStatus } from "../camera/useCamera";

export type ConnectionStatus =
  | "checking"
  | "offline"
  | "connecting"
  | "connected"
  | "reconnecting";

export type Notice = {
  tone: "info" | "success" | "warning" | "error";
  text: string;
};

export type TranslatorState = {
  mode: Mode;
  models: Partial<Record<Mode, ModelEntry>>;
  catalogueLoading: boolean;
  backendStatus: "checking" | "online" | "offline";
  connection: ConnectionStatus;
  cameraStatus: CameraStatus;
  session: Session | null;
  candidate: Candidate | null;
  candidateDeadline: number | null;
  pending: string | null;
  editing: boolean;
  draft: string;
  hiddenTranscript: boolean;
  terminal: "expired" | "deleted" | null;
  notice: Notice | null;
};

export type SessionAction =
  | { type: "CATALOGUE_LOADING" }
  | { type: "CATALOGUE_READY"; models: ModelEntry[] }
  | { type: "CATALOGUE_FAILED"; message: string }
  | { type: "CAMERA"; status: CameraStatus }
  | { type: "CONNECTION"; status: ConnectionStatus }
  | { type: "SNAPSHOT"; session: Session }
  | { type: "CANDIDATE"; candidate: Candidate | null; deadline?: number }
  | { type: "CANDIDATE_EXPIRED"; candidateId: string }
  | { type: "PENDING"; value: string | null }
  | { type: "EDITOR_OPEN"; text: string }
  | { type: "EDITOR_DRAFT"; text: string }
  | { type: "EDITOR_CLOSE" }
  | { type: "HIDE_TRANSCRIPT" }
  | { type: "SHOW_TRANSCRIPT" }
  | { type: "TERMINAL"; value: "expired" | "deleted" }
  | { type: "NOTICE"; notice: Notice | null };

export function initialTranslatorState(mode: Mode): TranslatorState {
  return {
    mode,
    models: {},
    catalogueLoading: true,
    backendStatus: "checking",
    connection: "checking",
    cameraStatus: "off",
    session: null,
    candidate: null,
    candidateDeadline: null,
    pending: null,
    editing: false,
    draft: "",
    hiddenTranscript: false,
    terminal: null,
    notice: null,
  };
}

export function sessionReducer(
  state: TranslatorState,
  action: SessionAction,
): TranslatorState {
  switch (action.type) {
    case "CATALOGUE_LOADING":
      return { ...state, catalogueLoading: true, backendStatus: "checking" };
    case "CATALOGUE_READY":
      return {
        ...state,
        catalogueLoading: false,
        backendStatus: "online",
        models: Object.fromEntries(action.models.map(model => [model.mode, model])),
        notice: null,
      };
    case "CATALOGUE_FAILED":
      return {
        ...state,
        catalogueLoading: false,
        backendStatus: "offline",
        notice: { tone: "error", text: action.message },
      };
    case "CAMERA":
      return { ...state, cameraStatus: action.status };
    case "CONNECTION":
      return { ...state, connection: action.status };
    case "SNAPSHOT": {
      if (state.terminal) return state;
      if (state.session && state.session.session_id !== action.session.session_id) {
        return state;
      }
      const session = mergeSnapshot(state.session, action.session);
      const changedStream =
        state.session?.stream_id !== session.stream_id ||
        state.session?.state_version !== session.state_version;
      return {
        ...state,
        session,
        candidate:
          session.status === "capturing" && !changedStream
            ? state.candidate
            : null,
        candidateDeadline:
          session.status === "capturing" && !changedStream
            ? state.candidateDeadline
            : null,
        terminal: session.status === "ended" ? null : state.terminal,
      };
    }
    case "CANDIDATE": {
      const session = state.session;
      if (
        action.candidate &&
        (!session ||
          session.status !== "capturing" ||
          action.candidate.mode !== session.mode ||
          action.candidate.stream_id !== session.stream_id)
      ) {
        return state;
      }
      return {
        ...state,
        candidate: action.candidate,
        candidateDeadline: action.candidate
          ? action.deadline ?? null
          : null,
      };
    }
    case "CANDIDATE_EXPIRED":
      return state.candidate?.candidate_id === action.candidateId
        ? { ...state, candidate: null, candidateDeadline: null }
        : state;
    case "PENDING":
      return { ...state, pending: action.value };
    case "EDITOR_OPEN":
      return { ...state, editing: true, draft: action.text };
    case "EDITOR_DRAFT":
      return { ...state, draft: action.text };
    case "EDITOR_CLOSE":
      return { ...state, editing: false, draft: "" };
    case "HIDE_TRANSCRIPT":
      return {
        ...state,
        hiddenTranscript: true,
        candidate: null,
        candidateDeadline: null,
        draft: "",
        editing: false,
      };
    case "SHOW_TRANSCRIPT":
      return { ...state, hiddenTranscript: false };
    case "TERMINAL":
      return {
        ...state,
        session: action.value === "deleted" ? null : state.session,
        terminal: action.value,
        connection: "offline",
        candidate: null,
        candidateDeadline: null,
        hiddenTranscript: action.value === "deleted" || state.hiddenTranscript,
      };
    case "NOTICE":
      return { ...state, notice: action.notice };
    default:
      return state;
  }
}

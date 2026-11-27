import { useCallback, useEffect, useReducer, useRef } from "react";
import { ApiError, api, downloadText } from "../api/client";
import {
  mergeSnapshot,
  type Candidate,
  type LiveEvent,
  type Mode,
  type Session,
} from "../api/contracts";
import { connectLive, type LiveSocket } from "../api/liveSocket";
import { FrameSampler } from "../camera/frameSampler";
import { useCamera } from "../camera/useCamera";
import {
  initialTranslatorState,
  sessionReducer,
  type Notice,
} from "./sessionReducer";

function messageForError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.code) {
      case "MODEL_UNAVAILABLE":
        return "This recognition mode is not available yet. Your camera preview remains local.";
      case "SOCKET_REQUIRED":
        return "Connect to the live service before starting recognition.";
      case "REVISION_CONFLICT":
        return "The transcript changed. Refresh the session and review your draft.";
      case "STATE_CONFLICT":
        return "The capture state changed. Review it before trying again.";
      case "CANDIDATE_UNAVAILABLE":
      case "STALE_STREAM":
        return "That preview is no longer ready to confirm. Wait for a fresh letter.";
      case "SPACE_NOT_ALLOWED":
        return "A space cannot be added at the beginning or after another space.";
      case "TRANSCRIPT_LIMIT":
        return "The transcript is full. Download or clear it before continuing.";
      case "SESSION_EXPIRED":
      case "SESSION_DELETED":
        return "This temporary session is no longer available.";
      case "CAPTURE_ACTIVE":
        return "Pause recognition before editing the transcript.";
    }
    return error.message;
  }
  if (error instanceof Error && error.name === "AbortError") {
    return "The request timed out. Its outcome is being checked; do not repeat it yet.";
  }
  return "Could not communicate with Signova. Check the backend connection and try again.";
}

function safeNotice(tone: Notice["tone"], text: string): Notice {
  return { tone, text };
}

export function useSessionController(mode: Mode) {
  const [state, dispatch] = useReducer(
    sessionReducer,
    mode,
    initialTranslatorState,
  );
  const camera = useCamera();
  const samplerRef = useRef<FrameSampler | null>(null);
  const socketRef = useRef<LiveSocket | null>(null);
  const socketReadyRef = useRef(false);
  const tokenRef = useRef<string | null>(null);
  const sessionRef = useRef<Session | null>(null);
  const stateRef = useRef(state);
  const controllerGeneration = useRef(0);
  const busyRef = useRef(false);
  const retryTimer = useRef<number | null>(null);
  const retryAttempt = useRef(0);
  const scheduleReconnectRef = useRef<() => void>(() => undefined);
  const loseSocketRef = useRef<(reason: string) => void>(() => undefined);
  const lastTrafficAt = useRef(performance.now());
  const pingNonce = useRef<string | null>(null);

  stateRef.current = state;
  sessionRef.current = state.session;

  const setNotice = useCallback((tone: Notice["tone"], text: string) => {
    dispatch({ type: "NOTICE", notice: safeNotice(tone, text) });
  }, []);

  const applySnapshot = useCallback((incoming: Session) => {
    const accepted = mergeSnapshot(sessionRef.current, incoming);
    if (sessionRef.current && accepted.session_id !== sessionRef.current.session_id) {
      return;
    }
    sessionRef.current = accepted;
    dispatch({ type: "SNAPSHOT", session: accepted });
  }, []);

  const stopLocalCapture = useCallback(() => {
    samplerRef.current?.stop();
    camera.stop();
    dispatch({ type: "CAMERA", status: "off" });
  }, [camera.stop]);

  const handleEvent = useCallback(
    (event: LiveEvent) => {
      lastTrafficAt.current = performance.now();
      switch (event.type) {
        case "session.ready":
          socketReadyRef.current = true;
          applySnapshot(event.data.session);
          dispatch({ type: "CONNECTION", status: "connected" });
          return;
        case "session.state":
        case "transcript.updated":
        case "session.ended":
          applySnapshot(event.data.session);
          if (
            event.data.session.status !== "capturing"
          ) {
            stopLocalCapture();
          }
          if (event.type === "session.ended") {
            dispatch({
              type: "NOTICE",
              notice: safeNotice("info", "Session ended. Transcript is available for review."),
            });
          }
          return;
        case "candidate.updated":
          dispatch({
            type: "CANDIDATE",
            candidate: event.data.candidate,
            deadline: event.data.candidate
              ? performance.now() + event.data.candidate.expires_in_ms
              : undefined,
          });
          return;
        case "frame.ack":
          samplerRef.current?.acknowledge(
            event.data.stream_id,
            event.data.frame_seq,
          );
          if (event.data.outcome === "discarded" && event.data.reason) {
            dispatch({
              type: "NOTICE",
              notice: safeNotice(
                "warning",
                `A camera sample was skipped (${event.data.reason}).`,
              ),
            });
          }
          return;
        case "pong":
          if (event.data.nonce === pingNonce.current) {
            pingNonce.current = null;
            lastTrafficAt.current = performance.now();
          }
          return;
        case "warning":
          dispatch({
            type: "NOTICE",
            notice: safeNotice("warning", event.data.message),
          });
          if (event.data.code === "insufficient_rate") stopLocalCapture();
          return;
        case "error":
          dispatch({
            type: "NOTICE",
            notice: safeNotice(
              "error",
              `${event.data.error.message} Support ID: ${event.data.request_id}`,
            ),
          });
          return;
        case "session.expired":
          socketReadyRef.current = false;
          stopLocalCapture();
          tokenRef.current = null;
          dispatch({ type: "TERMINAL", value: "expired" });
          dispatch({
            type: "NOTICE",
            notice: safeNotice(
              "warning",
              "The temporary server session expired. You can still copy or download the visible transcript.",
            ),
          });
          return;
        case "session.deleted":
          socketReadyRef.current = false;
          stopLocalCapture();
          tokenRef.current = null;
          dispatch({ type: "HIDE_TRANSCRIPT" });
          dispatch({ type: "TERMINAL", value: "deleted" });
          return;
      }
    },
    [applySnapshot, stopLocalCapture],
  );

  const scheduleReconnect = useCallback(() => {
    if (
      retryTimer.current !== null ||
      !tokenRef.current ||
      !sessionRef.current ||
      sessionRef.current.status === "ended" ||
      stateRef.current.terminal
    ) {
      return;
    }
    dispatch({ type: "CONNECTION", status: "reconnecting" });
    const attempt = retryAttempt.current++;
    const delay = Math.min(15_000, 1000 * 2 ** attempt) * (0.8 + Math.random() * 0.4);
    retryTimer.current = window.setTimeout(async () => {
      retryTimer.current = null;
      const current = sessionRef.current;
      const token = tokenRef.current;
      if (!current || !token) return;
      try {
        applySnapshot(await api.readSession(current.session_id, token));
        const nextSocket = connectLive(
          current.session_id,
          token,
          handleEvent,
          reason => loseSocketRef.current(reason),
        );
        socketRef.current?.close(1000, "Replacing failed connection");
        socketRef.current = nextSocket;
        await nextSocket.ready;
        socketReadyRef.current = true;
        retryAttempt.current = 0;
        dispatch({ type: "CONNECTION", status: "connected" });
        setNotice("info", "Reconnected paused. Start the camera again to resume.");
      } catch {
        dispatch({ type: "CONNECTION", status: "reconnecting" });
        scheduleReconnectRef.current();
      }
    }, delay);
  }, [applySnapshot, handleEvent, setNotice]);
  scheduleReconnectRef.current = scheduleReconnect;

  const loseSocket = useCallback(
    (reason: string) => {
      const current = sessionRef.current;
      const socket = socketRef.current;
      socketRef.current = null;
      socketReadyRef.current = false;
      socket?.close(1000, "Connection lost");
      stopLocalCapture();
      dispatch({ type: "CANDIDATE", candidate: null });
      if (!current || current.status === "ended" || stateRef.current.terminal) {
        dispatch({ type: "CONNECTION", status: "offline" });
        return;
      }
      dispatch({ type: "CONNECTION", status: "reconnecting" });
      setNotice("warning", `Connection lost (${reason}). Camera stopped; reconnecting paused.`);
      scheduleReconnectRef.current();
    },
    [setNotice, stopLocalCapture],
  );
  loseSocketRef.current = loseSocket;

  const openSocket = useCallback(
    async (sessionId: string, token: string): Promise<void> => {
      socketRef.current?.close(1000, "Opening session connection");
      const generation = controllerGeneration.current;
      dispatch({ type: "CONNECTION", status: "connecting" });
      const socket = connectLive(sessionId, token, handleEvent, reason => {
        if (generation === controllerGeneration.current) {
          loseSocketRef.current(reason);
        }
      });
      socketRef.current = socket;
      await socket.ready;
      socketReadyRef.current = true;
      if (generation !== controllerGeneration.current) {
        socket.close(1000, "Session controller was replaced");
        throw new Error("STALE_CONTROLLER");
      }
    },
    [handleEvent],
  );

  const openSocketRef = useRef(openSocket);
  openSocketRef.current = openSocket;

  const startCamera = useCallback(async () => {
    const stream = await camera.start();
    dispatch({ type: "CAMERA", status: stream ? "ready" : camera.status });
    if (!stream && camera.error) {
      setNotice("error", camera.error);
    }
  }, [camera, setNotice]);

  const pauseCapture = useCallback(async () => {
    const current = sessionRef.current;
    const token = tokenRef.current;
    samplerRef.current?.stop();
    camera.stop();
    dispatch({ type: "CAMERA", status: "off" });
    dispatch({ type: "CANDIDATE", candidate: null });
    if (!current || !token || current.status !== "capturing") return;
    if (busyRef.current) return;
    busyRef.current = true;
    dispatch({ type: "PENDING", value: "Pausing capture" });
    try {
      applySnapshot(await api.capture(current, token, "pause"));
      setNotice("success", "Recognition paused. Your confirmed text is unchanged.");
    } catch (error) {
      try {
        applySnapshot(await api.readSession(current.session_id, token));
      } catch {
        setNotice("error", `${messageForError(error)} Server capture state is uncertain.`);
      }
      if (error instanceof ApiError) setNotice("error", messageForError(error));
    } finally {
      busyRef.current = false;
      dispatch({ type: "PENDING", value: null });
    }
  }, [applySnapshot, camera.stop, setNotice]);

  const startRecognition = useCallback(async () => {
    if (busyRef.current) return;
    if (camera.status !== "ready" || !camera.stream) {
      setNotice("warning", "Start the camera and wait for its preview before recognition.");
      return;
    }
    const model = stateRef.current.models[mode];
    if (
      stateRef.current.backendStatus !== "online" ||
      !model?.ready ||
      !model.input
    ) {
      setNotice("warning", "This model is currently unavailable. Camera preview remains local.");
      return;
    }
    busyRef.current = true;
    dispatch({ type: "PENDING", value: "Connecting recognition" });
    try {
      let session = sessionRef.current;
      let token = tokenRef.current;
      if (!session || !token) {
        const created = await api.createSession(mode);
        session = created.session;
        token = created.token;
        sessionRef.current = session;
        tokenRef.current = token;
        applySnapshot(session);
      }
      if (session.mode !== mode) {
        throw new Error("SESSION_MODE_MISMATCH");
      }
      if (
        !socketRef.current ||
        socketRef.current.readyState !== WebSocket.OPEN ||
        !socketReadyRef.current
      ) {
        await openSocket(session.session_id, token);
      }
      session = sessionRef.current ?? session;
      if (session.status === "capturing") {
        setNotice("info", "Recognition is already active.");
        return;
      }
      const started = await api.capture(session, token, "start");
      applySnapshot(started);
      if (!started.stream_id || !camera.videoRef.current) {
        throw new Error("CAPTURE_STREAM_MISSING");
      }
      if (!samplerRef.current) {
        samplerRef.current = new FrameSampler(reason => {
          loseSocketRef.current(reason);
        });
      }
      dispatch({ type: "CONNECTION", status: "connected" });
      const liveSocket = socketRef.current;
      if (!liveSocket) throw new Error("SOCKET_NOT_OPEN");
      samplerRef.current.start(
        camera.videoRef.current,
        liveSocket,
        started.stream_id,
        model.input,
      );
      setNotice("success", "Recognition is active. Confirm a stable preview to add it.");
    } catch (error) {
      setNotice("error", messageForError(error));
    } finally {
      busyRef.current = false;
      dispatch({ type: "PENDING", value: null });
    }
  }, [applySnapshot, camera, mode, openSocket, setNotice]);

  const confirmCandidate = useCallback(async () => {
    if (busyRef.current) return;
    const current = sessionRef.current;
    const token = tokenRef.current;
    const candidate = stateRef.current.candidate;
    if (
      !current ||
      !token ||
      !candidate ||
      !candidate.eligible ||
      !candidate.stable
    ) {
      setNotice("warning", "Wait for a stable, eligible preview.");
      return;
    }
    if (stateRef.current.candidateDeadline !== null &&
      performance.now() >= stateRef.current.candidateDeadline) {
      dispatch({ type: "CANDIDATE", candidate: null });
      setNotice("warning", "That preview expired. Wait for a fresh letter.");
      return;
    }
    busyRef.current = true;
    dispatch({ type: "PENDING", value: "Confirming letter" });
    try {
      const updated = await api.confirm(
        current,
        token,
        candidate.candidate_id,
        candidate.stream_id,
      );
      applySnapshot(updated);
      dispatch({ type: "CANDIDATE", candidate: null });
      setNotice("success", "Letter confirmed.");
    } catch (error) {
      setNotice("error", messageForError(error));
      if (error instanceof ApiError && error.code === "CANDIDATE_UNAVAILABLE") {
        dispatch({ type: "CANDIDATE", candidate: null });
      }
    } finally {
      busyRef.current = false;
      dispatch({ type: "PENDING", value: null });
    }
  }, [applySnapshot, setNotice]);

  const addSpace = useCallback(async () => {
    const current = sessionRef.current;
    const token = tokenRef.current;
    if (!current || !token || current.status !== "paused" || busyRef.current) {
      setNotice("warning", "Pause the camera before adding an alphabet space.");
      return;
    }
    busyRef.current = true;
    dispatch({ type: "PENDING", value: "Adding space" });
    try {
      applySnapshot(await api.addSpace(current, token));
      setNotice("success", "Space added.");
    } catch (error) {
      setNotice("error", messageForError(error));
    } finally {
      busyRef.current = false;
      dispatch({ type: "PENDING", value: null });
    }
  }, [applySnapshot, setNotice]);

  const openEditor = useCallback(async () => {
    if (busyRef.current) return;
    const current = sessionRef.current;
    if (!current || current.status === "ended") return;
    if (current.status === "capturing") await pauseCapture();
    const latest = sessionRef.current;
    if (!latest || latest.status === "capturing") return;
    dispatch({ type: "EDITOR_OPEN", text: latest.transcript.text });
  }, [pauseCapture]);

  const changeDraft = useCallback((text: string) => {
    dispatch({ type: "EDITOR_DRAFT", text });
  }, []);

  const closeEditor = useCallback(() => {
    dispatch({ type: "EDITOR_CLOSE" });
  }, []);

  const saveEditor = useCallback(async () => {
    const current = sessionRef.current;
    const token = tokenRef.current;
    const draft = stateRef.current.draft;
    if (!current || !token || busyRef.current) return;
    const maxCharacters =
      stateRef.current.models[mode]?.transcript_limits.max_characters ?? 2000;
    if ([...draft].length > maxCharacters) {
      setNotice(
        "error",
        `The edit must be no more than ${maxCharacters.toLocaleString()} Unicode characters.`,
      );
      return;
    }
    busyRef.current = true;
    dispatch({ type: "PENDING", value: "Saving correction" });
    try {
      applySnapshot(await api.replaceTranscript(current, token, draft));
      dispatch({ type: "EDITOR_CLOSE" });
      setNotice("success", "Transcript correction saved.");
    } catch (error) {
      setNotice("error", messageForError(error));
    } finally {
      busyRef.current = false;
      dispatch({ type: "PENDING", value: null });
    }
  }, [applySnapshot, setNotice]);

  const clearTranscript = useCallback(async () => {
    const current = sessionRef.current;
    const token = tokenRef.current;
    if (!current || !token || busyRef.current) return;
    busyRef.current = true;
    samplerRef.current?.stop();
    camera.stop();
    dispatch({ type: "CAMERA", status: "off" });
    dispatch({ type: "HIDE_TRANSCRIPT" });
    dispatch({ type: "PENDING", value: "Clearing transcript" });
    try {
      applySnapshot(await api.clearTranscript(current, token));
      dispatch({ type: "SHOW_TRANSCRIPT" });
      setNotice("success", "Transcript cleared. Recognition is paused.");
    } catch (error) {
      setNotice(
        "error",
        `Text is hidden on this page while server clear is checked. ${messageForError(error)}`,
      );
      try {
        const latest = await api.readSession(current.session_id, token);
        applySnapshot(latest);
        if (!latest.transcript.text) {
          dispatch({ type: "SHOW_TRANSCRIPT" });
          setNotice("success", "Transcript clear was confirmed by the server.");
        }
      } catch {
        setNotice(
          "error",
          "Text remains hidden on this page; server deletion is still unconfirmed.",
        );
      }
    } finally {
      busyRef.current = false;
      dispatch({ type: "PENDING", value: null });
    }
  }, [applySnapshot, camera.stop, setNotice]);

  const endSession = useCallback(async () => {
    const current = sessionRef.current;
    const token = tokenRef.current;
    if (!current || !token || busyRef.current) return false;
    busyRef.current = true;
    stopLocalCapture();
    dispatch({ type: "PENDING", value: "Ending session" });
    try {
      applySnapshot(await api.endSession(current, token));
      socketRef.current?.close(1000, "Session ended");
      socketRef.current = null;
      socketReadyRef.current = false;
      dispatch({ type: "CONNECTION", status: "offline" });
      setNotice("success", "Session ended. This transcript is now read-only.");
      return true;
    } catch (error) {
      setNotice("error", `Camera is off. ${messageForError(error)}`);
      return false;
    } finally {
      busyRef.current = false;
      dispatch({ type: "PENDING", value: null });
    }
  }, [applySnapshot, setNotice, stopLocalCapture]);

  const deleteSession = useCallback(async () => {
    const current = sessionRef.current;
    const token = tokenRef.current;
    if (!current || !token || busyRef.current) return;
    busyRef.current = true;
    stopLocalCapture();
    dispatch({ type: "HIDE_TRANSCRIPT" });
    dispatch({ type: "PENDING", value: "Deleting session" });
    try {
      await api.deleteSession(current.session_id, token);
      tokenRef.current = null;
      sessionRef.current = null;
      socketRef.current?.close(1000, "Session deleted");
      socketRef.current = null;
      socketReadyRef.current = false;
      dispatch({ type: "TERMINAL", value: "deleted" });
      setNotice("success", "Session deleted.");
    } catch (error) {
      setNotice(
        "error",
        `Text is removed from this page; server deletion is unconfirmed. ${messageForError(error)}`,
      );
    } finally {
      busyRef.current = false;
      dispatch({ type: "PENDING", value: null });
    }
  }, [setNotice, stopLocalCapture]);

  const copyTranscript = useCallback(async () => {
    const text = stateRef.current.hiddenTranscript
      ? ""
      : sessionRef.current?.transcript.text ?? "";
    if (!text) {
      setNotice("info", "There is no confirmed transcript to copy.");
      return;
    }
    try {
      await navigator.clipboard.writeText(text);
      setNotice("success", "Confirmed transcript copied.");
    } catch {
      setNotice("error", "Copy was blocked. Select the transcript text to copy it manually.");
    }
  }, [setNotice]);

  const cameraDownload = useCallback(() => {
    const text = stateRef.current.hiddenTranscript
      ? ""
      : sessionRef.current?.transcript.text ?? "";
    if (!text) {
      setNotice("info", "There is no confirmed transcript to download.");
      return;
    }
    downloadText(text);
    setNotice("success", "Transcript download requested.");
  }, [setNotice]);

  const refreshModels = useCallback(async () => {
    dispatch({ type: "CATALOGUE_LOADING" });
    try {
      const catalogue = await api.getModels();
      dispatch({ type: "CATALOGUE_READY", models: catalogue.models });
    } catch {
      dispatch({
        type: "CATALOGUE_FAILED",
        message: "Signova backend is unreachable. Retry after the service is available.",
      });
    }
  }, []);

  useEffect(() => {
    void refreshModels();
  }, [refreshModels]);

  useEffect(() => {
    dispatch({ type: "CAMERA", status: camera.status });
  }, [camera.status]);

  useEffect(() => {
    samplerRef.current = new FrameSampler(reason => {
      loseSocketRef.current(reason);
    });
    return () => {
      controllerGeneration.current += 1;
      if (retryTimer.current !== null) window.clearTimeout(retryTimer.current);
      samplerRef.current?.stop();
      const session = sessionRef.current;
      const token = tokenRef.current;
      if (
        session?.status === "capturing" &&
        token &&
        socketReadyRef.current
      ) {
        void api.capture(session, token, "pause").catch(() => {
          console.warn("Signova could not confirm capture pause on navigation.");
        });
      }
      socketRef.current?.close(1000, "Translator page closed");
      socketRef.current = null;
      socketReadyRef.current = false;
      tokenRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (state.connection !== "connected") return;
    const heartbeat = window.setInterval(() => {
      const socket = socketRef.current;
      if (!socket || socket.readyState !== WebSocket.OPEN) return;
      if (performance.now() - lastTrafficAt.current > 45_000) {
        loseSocketRef.current("HEARTBEAT_TIMEOUT");
        return;
      }
      const nonce = crypto.randomUUID();
      pingNonce.current = nonce;
      try {
        socket.send({ protocol_version: 1, type: "ping", nonce });
      } catch {
        loseSocketRef.current("PING_SEND_FAILED");
      }
    }, 15_000);
    return () => window.clearInterval(heartbeat);
  }, [state.connection]);

  const clearNotice = useCallback(() => {
    dispatch({ type: "NOTICE", notice: null });
  }, []);

  const expireCandidate = useCallback((candidateId: string) => {
    dispatch({ type: "CANDIDATE_EXPIRED", candidateId });
  }, []);

  const model = state.models[mode] ?? null;
  const candidate: Candidate | null =
    state.candidateDeadline !== null &&
    performance.now() >= state.candidateDeadline
      ? null
      : state.candidate;

  return {
    state,
    model,
    camera,
    candidate,
    startCamera,
    stopCamera: pauseCapture,
    startRecognition,
    pauseCapture,
    confirmCandidate,
    addSpace,
    openEditor,
    changeDraft,
    closeEditor,
    saveEditor,
    clearTranscript,
    endSession,
    deleteSession,
    copyTranscript,
    downloadTranscript: cameraDownload,
    refreshModels,
    clearNotice,
    expireCandidate,
    setNotice,
  };
}

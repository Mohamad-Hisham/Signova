import { parseLiveEvent, type LiveEvent } from "./contracts";

const WS_BASE = (
  import.meta.env.VITE_WS_BASE_URL ??
  (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1")
    .replace(/^http/, "ws")
).replace(/\/$/, "");

export type LiveSocket = {
  ready: Promise<LiveEvent>;
  send(value: unknown): void;
  close(code?: number, reason?: string): void;
  get readyState(): number;
  get bufferedAmount(): number;
};

export function connectLive(
  sessionId: string,
  token: string,
  onEvent: (event: LiveEvent) => void,
  onFailure: (reason: string) => void,
): LiveSocket {
  const socket = new WebSocket(
    `${WS_BASE}/ws/sessions/${encodeURIComponent(sessionId)}`,
  );
  let disposed = false;
  let failed = false;
  let readyResolve: (event: LiveEvent) => void = () => undefined;
  let readyReject: (cause: Error) => void = () => undefined;
  let authTimer = 0;

  const ready = new Promise<LiveEvent>((resolve, reject) => {
    readyResolve = resolve;
    readyReject = reject;
  });

  const fail = (reason: string) => {
    if (disposed || failed) return;
    failed = true;
    window.clearTimeout(authTimer);
    readyReject(new Error(reason));
    onFailure(reason);
  };

  const handleOpen = () => {
    if (disposed) return;
    authTimer = window.setTimeout(() => {
      fail("SOCKET_AUTH_TIMEOUT");
      socket.close(1000, "Authentication timeout");
    }, 5000);
    try {
      socket.send(
        JSON.stringify({
          protocol_version: 1,
          type: "auth",
          session_token: token,
        }),
      );
    } catch {
      fail("SOCKET_AUTH_SEND_FAILED");
    }
  };

  const handleMessage = (message: MessageEvent<unknown>) => {
    if (disposed) return;
    try {
      if (typeof message.data !== "string") {
        throw new Error("BINARY_EVENT");
      }
      const event = parseLiveEvent(JSON.parse(message.data), sessionId);
      if (event.type === "session.ready") {
        window.clearTimeout(authTimer);
        readyResolve(event);
      }
      onEvent(event);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "";
      const reason = /^[A-Z0-9_]+$/.test(message)
        ? message
        : "INVALID_LIVE_EVENT";
      fail(reason);
      socket.close(1000, "Invalid live event");
    }
  };

  const handleClose = () => {
    if (!disposed) fail("SOCKET_CLOSED");
  };

  const handleError = () => {
    if (!disposed) fail("SOCKET_ERROR");
  };

  socket.addEventListener("open", handleOpen);
  socket.addEventListener("message", handleMessage);
  socket.addEventListener("close", handleClose);
  socket.addEventListener("error", handleError);

  return {
    ready,
    send(value) {
      if (socket.readyState !== WebSocket.OPEN) {
        throw new Error("SOCKET_NOT_OPEN");
      }
      socket.send(JSON.stringify(value));
    },
    close(code = 1000, reason = "Client closed session") {
      if (disposed) return;
      disposed = true;
      window.clearTimeout(authTimer);
      socket.removeEventListener("open", handleOpen);
      socket.removeEventListener("message", handleMessage);
      socket.removeEventListener("close", handleClose);
      socket.removeEventListener("error", handleError);
      if (
        socket.readyState === WebSocket.CONNECTING ||
        socket.readyState === WebSocket.OPEN
      ) {
        socket.close(code, reason);
      }
    },
    get readyState() {
      return socket.readyState;
    },
    get bufferedAmount() {
      return socket.bufferedAmount;
    },
  };
}

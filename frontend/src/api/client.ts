import {
  ModelCatalogueSchema,
  SessionSchema,
  VocabularySchema,
  type Mode,
  type ModelCatalogue,
  type Session,
  type Vocabulary,
} from "./contracts";

const API_BASE = (
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1"
).replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message = code,
    readonly requestId: string | null = null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function commandId(): string {
  return crypto.randomUUID();
}

async function request(
  path: string,
  token?: string,
  init: RequestInit = {},
): Promise<Response> {
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const abort = new AbortController();
  const timer = window.setTimeout(() => abort.abort(), 10_000);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers,
      cache: "no-store",
      signal: abort.signal,
    });

    if (!response.ok && response.status !== 204) {
      let code = `HTTP_${response.status}`;
      let message = "The request could not be completed.";
      let requestId: string | null = null;
      try {
        const body: unknown = await response.json();
        if (typeof body === "object" && body !== null && "error" in body) {
          const error = body.error;
          if (typeof error === "object" && error !== null && "code" in error) {
            if (typeof error.code === "string") code = error.code;
            if ("message" in error && typeof error.message === "string") {
              message = error.message;
            }
          }
          if ("request_id" in body && typeof body.request_id === "string") {
            requestId = body.request_id;
          }
        }
      } catch {
        // A non-JSON error still has a useful HTTP status for the caller.
      }
      throw new ApiError(response.status, code, message, requestId);
    }

    return response;
  } finally {
    window.clearTimeout(timer);
  }
}

async function json<T>(
  path: string,
  schema: { parse(value: unknown): T },
  token?: string,
  init?: RequestInit,
): Promise<T> {
  const response = await request(path, token, init);
  if (response.status === 204) {
    throw new ApiError(204, "UNEXPECTED_EMPTY_RESPONSE");
  }
  return schema.parse(await response.json());
}

async function mutate(
  path: string,
  token: string,
  body: unknown,
  method: "POST" | "PATCH" = "POST",
): Promise<Session> {
  const response = await json(
    path,
    {
      parse(value: unknown) {
        if (
          typeof value !== "object" ||
          value === null ||
          !("session" in value)
        ) {
          throw new Error("INVALID_SESSION_RESPONSE");
        }
        return SessionSchema.parse(value.session);
      },
    },
    token,
    {
      method,
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": commandId(),
      },
      body: JSON.stringify(body),
    },
  );
  return response;
}

export const api = {
  getModels(): Promise<ModelCatalogue> {
    return json("/models", ModelCatalogueSchema);
  },

  getVocabulary(mode: Mode): Promise<Vocabulary> {
    return json(`/vocabulary?mode=${encodeURIComponent(mode)}`, VocabularySchema);
  },

  createSession(mode: Mode): Promise<{ session: Session; token: string }> {
    return json(
      "/sessions",
      {
        parse(value: unknown) {
          if (typeof value !== "object" || value === null) {
            throw new Error("INVALID_CREATE_SESSION_RESPONSE");
          }
          const result = value as Record<string, unknown>;
          if (typeof result.session_token !== "string") {
            throw new Error("INVALID_SESSION_TOKEN");
          }
          return {
            session: SessionSchema.parse(result.session),
            token: result.session_token,
          };
        },
      },
      undefined,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode, recovery_enabled: false }),
      },
    );
  },

  readSession(sessionId: string, token: string): Promise<Session> {
    return json(
      `/sessions/${encodeURIComponent(sessionId)}`,
      {
        parse(value: unknown) {
          if (typeof value !== "object" || value === null || !("session" in value)) {
            throw new Error("INVALID_SESSION_RESPONSE");
          }
          return SessionSchema.parse(value.session);
        },
      },
      token,
    );
  },

  capture(session: Session, token: string, action: "start" | "pause") {
    return mutate(`/sessions/${session.session_id}/capture`, token, {
      expected_revision: session.transcript.revision,
      expected_state_version: session.state_version,
      action,
    });
  },

  confirm(session: Session, token: string, candidateId: string, streamId: string) {
    return mutate(`/sessions/${session.session_id}/confirm`, token, {
      expected_revision: session.transcript.revision,
      candidate_id: candidateId,
      stream_id: streamId,
    });
  },

  addSpace(session: Session, token: string) {
    return mutate(`/sessions/${session.session_id}/space`, token, {
      expected_revision: session.transcript.revision,
    });
  },

  replaceTranscript(session: Session, token: string, text: string) {
    return mutate(
      `/sessions/${session.session_id}/transcript`,
      token,
      {
        expected_revision: session.transcript.revision,
        items: text ? [{ text }] : [],
      },
      "PATCH",
    );
  },

  clearTranscript(session: Session, token: string) {
    return mutate(`/sessions/${session.session_id}/transcript/clear`, token, {
      expected_revision: session.transcript.revision,
    });
  },

  endSession(session: Session, token: string) {
    return mutate(`/sessions/${session.session_id}/end`, token, {
      expected_revision: session.transcript.revision,
    });
  },

  async deleteSession(sessionId: string, token: string): Promise<void> {
    await request(`/sessions/${encodeURIComponent(sessionId)}`, token, {
      method: "DELETE",
    });
  },

  async exportTranscript(
    session: Session,
    token: string,
  ): Promise<Blob | null> {
    const response = await request(
      `/sessions/${session.session_id}/export?format=txt&revision=${session.transcript.revision}`,
      token,
    );
    if (response.status === 204) return null;
    return response.blob();
  },
};

export function downloadText(text: string): void {
  if (!text) return;
  const blob = new Blob(["\uFEFF", text], {
    type: "text/plain;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "signova-transcript.txt";
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

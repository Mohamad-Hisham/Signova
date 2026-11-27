import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import {
  Check,
  Clipboard,
  Download,
  Eraser,
  Plus,
  Save,
  SquarePen,
  Trash2,
  X,
} from "lucide-react";
import type { Mode, Session } from "../../../api/contracts";
import type { Notice } from "../../../app/sessionReducer";

type Props = {
  mode: Mode;
  session: Session | null;
  hidden: boolean;
  editing: boolean;
  draft: string;
  maxCharacters: number;
  pending: string | null;
  notice: Notice | null;
  onCopy: () => void;
  onDownload: () => void;
  onEdit: () => void;
  onDraftChange: (text: string) => void;
  onSave: () => void;
  onCancelEdit: () => void;
  onAddSpace: () => void;
  onClear: () => void;
  onEnd: () => void;
  onDelete: () => void;
};

type DialogKind = "clear" | "end" | "delete" | null;

function wordCount(text: string): number {
  const trimmed = text.trim();
  return trimmed ? trimmed.split(/\s+/u).length : 0;
}

function characterCount(text: string): number {
  return Array.from(text).filter(character => !/\s/u.test(character)).length;
}

export default function TranscriptPanel({
  mode,
  session,
  hidden,
  editing,
  draft,
  maxCharacters,
  pending,
  notice,
  onCopy,
  onDownload,
  onEdit,
  onDraftChange,
  onSave,
  onCancelEdit,
  onAddSpace,
  onClear,
  onEnd,
  onDelete,
}: Props) {
  const [dialog, setDialog] = useState<DialogKind>(null);
  const cancelRef = useRef<HTMLButtonElement>(null);
  const priorFocus = useRef<HTMLElement | null>(null);
  const text = hidden ? "" : session?.transcript.text ?? "";
  const items = hidden ? [] : session?.transcript.items ?? [];
  const terminal = session?.status === "ended" || session?.status === "disconnected";
  const isAlphabet = mode === "alphabet";
  const count = isAlphabet ? characterCount(text) : wordCount(text);

  useEffect(() => {
    if (dialog || editing) {
      priorFocus.current = document.activeElement as HTMLElement | null;
      cancelRef.current?.focus();
    } else {
      priorFocus.current?.focus();
    }
  }, [dialog, editing]);

  const closeDialog = () => setDialog(null);
  const confirmDialog = () => {
    if (dialog === "clear") onClear();
    if (dialog === "end") onEnd();
    if (dialog === "delete") onDelete();
    setDialog(null);
  };
  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") {
      closeDialog();
      onCancelEdit();
    }
  };

  return (
    <section className="translator-card transcript-panel" aria-labelledby="transcript-heading">
      <div className="panel-heading transcript-heading">
        <div>
          <span className="panel-kicker">03 · Transcript</span>
          <h2 id="transcript-heading">Confirmed {isAlphabet ? "letters" : "words"}</h2>
        </div>
        <span className="transcript-count-badge">
          {count} {isAlphabet ? "letters" : count === 1 ? "word" : "words"}
        </span>
      </div>

      <div className={`transcript-content ${text ? "transcript-content-filled" : ""}`}>
        {hidden ? (
          <div className="transcript-empty transcript-hidden" role="status">
            <Eraser size={21} aria-hidden="true" />
            <p>Transcript hidden while server removal is being confirmed.</p>
          </div>
        ) : text ? (
          <>
            <p className="transcript-text" lang="ar" dir="rtl">{text}</p>
            <div className="transcript-items" aria-label="Confirmed transcript items">
              {items.map(item => (
                <span className="transcript-item" key={item.item_id} lang="ar" dir="rtl">
                  <bdi>{item.text}</bdi>
                </span>
              ))}
            </div>
          </>
        ) : (
          <div className="transcript-empty">
            <div className="transcript-empty-icon"><Clipboard size={22} /></div>
            <p>Confirmed {isAlphabet ? "letters" : "words"} will appear here.</p>
            <span>Candidate previews are temporary and do not enter this transcript.</span>
          </div>
        )}
      </div>

      {notice && (
        <div className={`transcript-notice notice-${notice.tone}`} role="status">
          {notice.text}
        </div>
      )}

      {editing && (
        <div className="dialog-backdrop" onKeyDown={handleKeyDown}>
          <div
            className="transcript-dialog editor-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="edit-transcript-title"
          >
            <div className="dialog-title-row">
              <div>
                <span className="panel-kicker">Edit transcript</span>
                <h3 id="edit-transcript-title">Make a correction</h3>
              </div>
              <button
                type="button"
                className="translator-icon-button"
                onClick={onCancelEdit}
                aria-label="Cancel editing"
                disabled={pending !== null}
              >
                <X size={18} />
              </button>
            </div>
            <p className="dialog-description">
              The saved text becomes a user correction. Recognition stays paused until you start it again.
            </p>
            <label className="sr-only" htmlFor="transcript-draft">Transcript text</label>
            <textarea
              id="transcript-draft"
              className="transcript-editor"
              lang="ar"
              dir="rtl"
              value={draft}
              onChange={event => onDraftChange(event.target.value)}
              maxLength={maxCharacters}
              autoFocus
            />
            <div className="editor-footer">
              <span>{Array.from(draft).length} / {maxCharacters.toLocaleString()} characters</span>
              <div className="dialog-actions">
                <button className="button button-outline" type="button" onClick={onCancelEdit} disabled={pending !== null}>
                  Cancel
                </button>
                <button className="button button-primary" type="button" onClick={onSave} disabled={pending !== null}>
                  <Save size={16} />
                  {pending ?? "Save correction"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {dialog && (
        <div className="dialog-backdrop" onKeyDown={handleKeyDown}>
          <div
            className="transcript-dialog confirm-dialog"
            role="alertdialog"
            aria-modal="true"
            aria-labelledby="confirm-title"
            aria-describedby="confirm-description"
          >
            <div className="confirm-dialog-icon">
              {dialog === "delete" ? <Trash2 size={22} /> : dialog === "clear" ? <Eraser size={22} /> : <Check size={22} />}
            </div>
            <h3 id="confirm-title">
              {dialog === "clear" ? "Clear this transcript?" : dialog === "end" ? "End this session?" : "Delete this session?"}
            </h3>
            <p id="confirm-description">
              {dialog === "clear"
                ? "Confirmed text will be removed from the server session. This cannot be undone."
                : dialog === "end"
                  ? "The session becomes read-only. You can still copy or download its temporary transcript."
                  : "The server session and its transcript will be deleted. Download a copy first if you need one."}
            </p>
            <div className="dialog-actions">
              <button
                ref={cancelRef}
                className="button button-outline"
                type="button"
                onClick={closeDialog}
              >
                Cancel
              </button>
              <button
                className={`button ${dialog === "delete" ? "button-danger" : "button-primary"}`}
                type="button"
                onClick={confirmDialog}
                disabled={pending !== null}
              >
                {dialog === "clear" ? "Clear transcript" : dialog === "end" ? "End session" : "Delete session"}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="transcript-actions">
        <div className="transcript-actions-primary">
          <button className="button button-outline" type="button" onClick={onEdit} disabled={!session || Boolean(terminal) || pending !== null}>
            <SquarePen size={16} />
            Edit
          </button>
          {isAlphabet && session?.status === "paused" && (
            <button className="button button-outline" type="button" onClick={onAddSpace} disabled={pending !== null || !text || text.endsWith(" ")}>
              <Plus size={16} />
              Add space
            </button>
          )}
        </div>
        <div className="transcript-actions-secondary">
          <button className="button button-outline" type="button" onClick={onCopy} disabled={!text}>
            <Clipboard size={16} />
            Copy
          </button>
          <button className="button button-outline" type="button" onClick={onDownload} disabled={!text}>
            <Download size={16} />
            Download TXT
          </button>
          <button className="button button-danger-soft" type="button" onClick={() => setDialog("clear")} disabled={!session || Boolean(terminal) || pending !== null || !text}>
            <Eraser size={16} />
            Clear
          </button>
        </div>
      </div>

      {session && (
        <div className="session-actions">
          <span>
            Temporary session · revision {session.transcript.revision}
          </span>
          <div>
            {session.status !== "ended" && (
              <button className="text-action" type="button" onClick={() => setDialog("end")} disabled={pending !== null}>
                End session
              </button>
            )}
            <button className="text-action text-action-danger" type="button" onClick={() => setDialog("delete")} disabled={pending !== null}>
              Delete session
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

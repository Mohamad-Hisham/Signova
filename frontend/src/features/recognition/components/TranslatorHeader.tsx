import {
  ArrowLeft,
  CircleHelp,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";
import type { ReactNode } from "react";
import type { CameraStatus } from "../../../camera/useCamera";
import type { ConnectionStatus } from "../../../app/sessionReducer";
import type { Mode, ModelEntry } from "../../../api/contracts";

type Props = {
  mode: Mode;
  model: ModelEntry | null;
  backendStatus: "checking" | "online" | "offline";
  connection: ConnectionStatus;
  cameraStatus: CameraStatus;
  onHome: () => void;
  onRefresh: () => void;
};

function StatusPill({ className, children }: { className: string; children: ReactNode }) {
  return <span className={`translator-status ${className}`}>{children}</span>;
}

export default function TranslatorHeader({
  mode,
  model,
  backendStatus,
  connection,
  cameraStatus,
  onHome,
  onRefresh,
}: Props) {
  const isAlphabet = mode === "alphabet";
  const modelText = model?.ready
    ? "Model ready"
    : model
      ? "Model unavailable"
      : backendStatus === "checking"
        ? "Checking model"
        : "Model status unknown";
  const connectionText =
    connection === "checking"
      ? backendStatus === "checking"
        ? "Checking service"
        : backendStatus === "offline"
          ? "Service offline"
          : "Ready to connect"
      : {
          offline: "Offline",
          connecting: "Connecting",
          connected: "Connected",
          reconnecting: "Reconnecting",
        }[connection];

  return (
    <header className="translator-header">
      <div className="translator-header-top">
        <button className="translator-back" type="button" onClick={onHome}>
          <ArrowLeft size={17} aria-hidden="true" />
          <span>Back to Signova</span>
        </button>
        <div className="translator-header-actions">
          <button
            className="translator-icon-button"
            type="button"
            onClick={onRefresh}
            aria-label="Refresh model availability"
            title="Refresh model availability"
          >
            <RefreshCw size={16} aria-hidden="true" />
          </button>
          <a className="translator-help-link" href="#translator-help">
            <CircleHelp size={16} aria-hidden="true" />
            Help
          </a>
        </div>
      </div>
      <div className="translator-heading-row">
        <div>
          <div className="translator-eyebrow">
            <span className={`mode-tag ${isAlphabet ? "mode-tag-alphabet" : "mode-tag-word"}`}>
              {isAlphabet ? "Alphabet mode" : "Word mode"}
            </span>
            <span className="translator-eyebrow-caption">Live sign translator</span>
          </div>
          <h1>{isAlphabet ? "Arabic Alphabet Translator" : "Word Translator"}</h1>
          <p>
            {isAlphabet
              ? "Recognize supported Arabic letters, confirm each preview, and build your text."
              : "Preview supported Arabic words and confirm recognized signs into a transcript."}
          </p>
        </div>
        <div className="translator-statuses" aria-label="Translator status">
          <StatusPill
            className={model?.ready ? "status-good" : model ? "status-warning" : "status-neutral"}
          >
            <span className="status-dot" />
            {modelText}
          </StatusPill>
          <StatusPill
            className={
              backendStatus === "offline"
                ? "status-error"
                : backendStatus === "online"
                  ? connection === "connected"
                    ? "status-good"
                    : "status-neutral"
                  : "status-neutral"
            }
          >
            <span className="status-dot" />
            {connectionText}
          </StatusPill>
          <StatusPill
            className={
              cameraStatus === "ready"
                ? "status-good"
                : cameraStatus === "error"
                  ? "status-error"
                  : "status-neutral"
            }
          >
            <span className="status-dot" />
            {cameraStatus === "ready"
              ? "Camera on"
              : cameraStatus === "requesting"
                ? "Camera requesting"
                : cameraStatus === "error"
                  ? "Camera issue"
                  : "Camera off"}
          </StatusPill>
        </div>
      </div>
      <div className="temporary-note">
        <ShieldCheck size={16} aria-hidden="true" />
        <span>
          Camera samples are sent for recognition only when the model is ready and you start capture.
        </span>
      </div>
    </header>
  );
}

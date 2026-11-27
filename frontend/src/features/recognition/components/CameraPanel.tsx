import {
  Camera,
  CameraOff,
  CircleStop,
  Play,
  Video,
} from "lucide-react";
import type { RefObject } from "react";
import type { CameraStatus } from "../../../camera/useCamera";
import type { Mode, ModelEntry, Session } from "../../../api/contracts";

type Props = {
  mode: Mode;
  model: ModelEntry | null;
  backendStatus: "checking" | "online" | "offline";
  videoRef: RefObject<HTMLVideoElement | null>;
  cameraStatus: CameraStatus;
  cameraError: string | null;
  session: Session | null;
  pending: string | null;
  onStartCamera: () => void;
  onStopCamera: () => void;
  onStartRecognition: () => void;
  onPause: () => void;
};

export default function CameraPanel({
  mode,
  model,
  backendStatus,
  videoRef,
  cameraStatus,
  cameraError,
  session,
  pending,
  onStartCamera,
  onStopCamera,
  onStartRecognition,
  onPause,
}: Props) {
  const capturing = session?.status === "capturing";
  const cameraReady = cameraStatus === "ready";
  const modelReady =
    model?.ready === true &&
    model.input !== null &&
    backendStatus === "online";

  return (
    <section className="translator-card camera-panel" aria-labelledby="camera-heading">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">01 · Camera</span>
          <h2 id="camera-heading">Camera preview</h2>
        </div>
        <span className={`camera-state ${cameraReady ? "camera-state-on" : ""}`}>
          <span className="status-dot" />
          {cameraReady ? "Preview active" : cameraStatus === "requesting" ? "Requesting…" : "Preview off"}
        </span>
      </div>

      <div className={`camera-stage ${cameraReady ? "camera-stage-live" : ""}`}>
        <video
          ref={videoRef}
          className="camera-video"
          autoPlay
          muted
          playsInline
          aria-label="Live camera preview"
          hidden={!cameraReady}
        />
        {!cameraReady && (
          <div className="camera-placeholder">
            <div className="camera-placeholder-icon">
              {cameraStatus === "error" ? (
                <CameraOff size={28} aria-hidden="true" />
              ) : (
                <Camera size={28} aria-hidden="true" />
              )}
            </div>
            <h3>{cameraStatus === "error" ? "Camera needs attention" : "Your camera preview will appear here"}</h3>
            <p>
              {cameraError ??
                "Camera access starts only after you choose Start camera. No video is recorded."}
            </p>
          </div>
        )}
        {cameraReady && (
          <>
            <div className="framing-guide" aria-hidden="true">
              <i className="guide-corner guide-tl" />
              <i className="guide-corner guide-tr" />
              <i className="guide-corner guide-bl" />
              <i className="guide-corner guide-br" />
            </div>
            <span className="camera-live-badge"><span /> CAMERA PREVIEW</span>
          </>
        )}
        {capturing && <span className="capture-badge"><span /> RECOGNITION ON</span>}
      </div>

      <div className="camera-controls">
        <button
          className="button button-outline"
          type="button"
          disabled={pending !== null || cameraStatus === "requesting"}
          onClick={cameraReady ? onStopCamera : onStartCamera}
        >
          {cameraReady ? <CameraOff size={17} /> : <Video size={17} />}
          {cameraReady ? "Stop camera" : cameraStatus === "requesting" ? "Requesting camera…" : "Start camera"}
        </button>
        <button
          className={`button ${capturing ? "button-stop" : "button-primary"}`}
          type="button"
          disabled={
            pending !== null ||
            !cameraReady ||
            (!capturing && !modelReady) ||
            session?.status === "ended" ||
            session?.status === "disconnected"
          }
          onClick={capturing ? onPause : onStartRecognition}
          title={!modelReady && !capturing ? "This model is not currently available" : undefined}
        >
          {capturing ? <CircleStop size={17} /> : <Play size={17} />}
          {capturing ? "Pause recognition" : "Start recognition"}
        </button>
      </div>
      {!modelReady && (
        <div className="model-unavailable-note" role="status">
          <span className="unavailable-indicator" />
          <span>
            {mode === "word"
              ? "Word recognition is not available yet. You can check your camera preview, but no frames will be sent."
              : model
                ? "Alphabet recognition is currently unavailable. No frames will be sent."
                : "Waiting for model availability from the backend. No frames will be sent."}
          </span>
        </div>
      )}
    </section>
  );
}

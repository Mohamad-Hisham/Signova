import { useEffect } from "react";
import { motion } from "motion/react";
import type { Mode } from "../../api/contracts";
import { useSessionController } from "../../app/sessionController";
import CameraPanel from "./components/CameraPanel";
import RecognitionPanel from "./components/RecognitionPanel";
import TranscriptPanel from "./components/TranscriptPanel";
import TranslatorHeader from "./components/TranslatorHeader";
import "./translator.css";

type Props = {
  mode: Mode;
  onHome: () => void;
};

export default function RecognitionWorkspace({ mode, onHome }: Props) {
  const controller = useSessionController(mode);
  const { state, candidate } = controller;
  const session = state.session;

  useEffect(() => {
    if (!state.candidate || state.candidateDeadline === null) return;
    const candidateId = state.candidate.candidate_id;
    const remaining = Math.max(0, state.candidateDeadline - performance.now());
    const timer = window.setTimeout(
      () => controller.expireCandidate(candidateId),
      remaining,
    );
    return () => window.clearTimeout(timer);
  }, [
    controller.expireCandidate,
    state.candidate,
    state.candidateDeadline,
  ]);

  const handleHome = async () => {
    if (session && session.status !== "ended") {
      const shouldEnd = window.confirm(
        "End this temporary session before leaving? Its transcript will remain available for brief read-only review.",
      );
      if (!shouldEnd) return;
      const ended = await controller.endSession();
      if (!ended) return;
    }
    onHome();
  };

  const isAlphabet = mode === "alphabet";
  const modelReady = controller.model?.ready === true;

  return (
    <div className="translator-page">
      <div className="translator-page-glow" aria-hidden="true" />
      <div className="translator-container">
        <TranslatorHeader
          mode={mode}
          model={controller.model}
          backendStatus={state.backendStatus}
          connection={state.connection}
          cameraStatus={state.cameraStatus}
          onHome={() => void handleHome()}
          onRefresh={() => void controller.refreshModels()}
        />

        {state.catalogueLoading && (
          <div className="catalogue-loading" role="status">
            <span className="loading-spinner" />
            Checking backend and model availability…
          </div>
        )}

        {session?.status === "ended" && (
          <div className="terminal-banner terminal-ended" role="status">
            <strong>Session ended · read-only review</strong>
            <span>Copy or download the temporary transcript before you leave.</span>
          </div>
        )}
        {state.terminal === "expired" && (
          <div className="terminal-banner terminal-expired" role="status">
            <strong>Server session expired</strong>
            <span>The text below is only the copy still visible in this page.</span>
          </div>
        )}
        {state.terminal === "deleted" && (
          <div className="terminal-banner terminal-ended" role="status">
            <strong>Session deleted</strong>
            <span>The transcript has been removed from the server and this page.</span>
          </div>
        )}

        <motion.main
          className="translator-main"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="translator-grid">
            <CameraPanel
              mode={mode}
              model={controller.model}
              backendStatus={state.backendStatus}
              videoRef={controller.camera.videoRef}
              cameraStatus={controller.camera.status}
              cameraError={controller.camera.error}
              session={session}
              pending={state.pending}
              onStartCamera={() => void controller.startCamera()}
              onStopCamera={() => void controller.stopCamera()}
              onStartRecognition={() => void controller.startRecognition()}
              onPause={() => void controller.pauseCapture()}
            />
            <RecognitionPanel
              mode={mode}
              model={controller.model}
              candidate={candidate}
              capturing={session?.status === "capturing"}
              pending={state.pending}
              onConfirm={() => void controller.confirmCandidate()}
            />
          </div>

          {!modelReady && state.backendStatus === "online" && (
            <div className="readiness-explanation">
              <span className="readiness-mark">!</span>
              <div>
                <strong>
                  {isAlphabet
                    ? "Alphabet model is not ready on this backend."
                    : "Word recognition is not available yet."}
                </strong>
                <p>
                  Readiness comes from the live model catalogue. The page will not send camera frames
                  or display simulated results while this mode is unavailable.
                </p>
              </div>
              <button type="button" className="text-action" onClick={() => void controller.refreshModels()}>
                Check again
              </button>
            </div>
          )}

          {state.backendStatus === "offline" && (
            <div className="readiness-explanation readiness-offline" role="alert">
              <span className="readiness-mark">!</span>
              <div>
                <strong>Backend connection unavailable.</strong>
                <p>
                  A local camera preview can be opened, but no recognition session can be created.
                  Start the FastAPI service, then retry.
                </p>
              </div>
              <button type="button" className="text-action" onClick={() => void controller.refreshModels()}>
                Retry
              </button>
            </div>
          )}

          <TranscriptPanel
            mode={mode}
            session={session}
            hidden={state.hiddenTranscript}
            editing={state.editing}
            draft={state.draft}
            maxCharacters={controller.model?.transcript_limits.max_characters ?? 2000}
            pending={state.pending}
            notice={state.notice}
            onCopy={() => void controller.copyTranscript()}
            onDownload={controller.downloadTranscript}
            onEdit={() => void controller.openEditor()}
            onDraftChange={controller.changeDraft}
            onSave={() => void controller.saveEditor()}
            onCancelEdit={controller.closeEditor}
            onAddSpace={() => void controller.addSpace()}
            onClear={() => void controller.clearTranscript()}
            onEnd={() => void controller.endSession()}
            onDelete={() => void controller.deleteSession()}
          />
        </motion.main>

        <section className="translator-help" id="translator-help">
          <div className="help-mark">?</div>
          <div>
            <h2>Signing tips</h2>
            <p>
              Keep your hand in view and use a supported sign. A preview is temporary;
              only a confirmed candidate from the backend updates your transcript.
            </p>
          </div>
          <div className="help-scope">
            <strong>Supported scope</strong>
            <span>
              {isAlphabet
                ? "Approved Arabic letters from the active model catalogue."
                : "Approved isolated Arabic words when the word model is available."}
            </span>
          </div>
        </section>

        <footer className="translator-footer">
          <span>Signova · Temporary Arabic sign recognition</span>
          <span>Camera samples are not recorded.</span>
        </footer>
      </div>
    </div>
  );
}

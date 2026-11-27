import { AnimatePresence, motion } from "motion/react";
import { Check, Fingerprint, ScanLine, Sparkles } from "lucide-react";
import type { Candidate, Mode, ModelEntry } from "../../../api/contracts";

type Props = {
  mode: Mode;
  model: ModelEntry | null;
  candidate: Candidate | null;
  capturing: boolean;
  pending: string | null;
  onConfirm: () => void;
};

export default function RecognitionPanel({
  mode,
  model,
  candidate,
  capturing,
  pending,
  onConfirm,
}: Props) {
  const isAlphabet = mode === "alphabet";
  const enabled = Boolean(
    capturing &&
      candidate?.eligible &&
      candidate.stable &&
      model?.ready &&
      pending === null,
  );

  return (
    <section className="translator-card recognition-panel" aria-labelledby="recognition-heading">
      <div className="panel-heading">
        <div>
          <span className="panel-kicker">02 · Recognition</span>
          <h2 id="recognition-heading">Current {isAlphabet ? "letter" : "word"} candidate</h2>
        </div>
        <span className={`recognition-indicator ${capturing ? "recognition-indicator-live" : ""}`}>
          <span />
          {capturing ? "Listening" : "Paused"}
        </span>
      </div>

      <div className="candidate-stage" aria-live="polite" aria-atomic="true">
        <AnimatePresence mode="wait" initial={false}>
          {candidate && capturing ? (
            <motion.div
              key={`${candidate.stream_id}-${candidate.candidate_id}`}
              className="candidate-content"
              initial={{ opacity: 0, y: 12, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -8, scale: 0.98 }}
              transition={{ duration: 0.24, ease: [0.22, 1, 0.36, 1] }}
            >
              <span className="candidate-label">
                <Sparkles size={14} aria-hidden="true" />
                Preview from model
              </span>
              <strong lang="ar" dir="rtl" className={isAlphabet ? "candidate-letter" : "candidate-word"}>
                {candidate.text}
              </strong>
              <div className="candidate-meta">
                <span className={candidate.stable ? "meta-ready" : ""}>
                  <span className="meta-dot" />
                  {candidate.stable ? "Stable preview" : "Checking stability"}
                </span>
                <span className={candidate.eligible ? "meta-ready" : ""}>
                  <span className="meta-dot" />
                  {candidate.eligible ? "Ready to confirm" : "Not eligible yet"}
                </span>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="candidate-empty"
              className="candidate-empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="candidate-empty-icon">
                {model?.ready ? (
                  <ScanLine size={25} aria-hidden="true" />
                ) : (
                  <Fingerprint size={25} aria-hidden="true" />
                )}
              </div>
              <p>
                {!model?.ready
                  ? `${isAlphabet ? "Alphabet" : "Word"} model is unavailable.`
                  : capturing
                    ? `No confident ${isAlphabet ? "letter" : "word"} yet. Keep the sign in view.`
                    : "Start recognition to see a temporary preview here."}
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <button
        className="button button-confirm"
        type="button"
        disabled={!enabled}
        onClick={onConfirm}
      >
        <Check size={17} aria-hidden="true" />
        {pending ?? `Confirm ${isAlphabet ? "letter" : "word"}`}
      </button>
      <p className="recognition-helper">
        A preview never changes your transcript. Confirm only when the sign looks right.
      </p>
    </section>
  );
}

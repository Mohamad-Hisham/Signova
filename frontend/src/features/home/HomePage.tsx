import { useState } from "react";
import { motion } from "motion/react";
import {
  ArrowRight,
  Check,
  ChevronRight,
  CircleHelp,
  Languages,
  ShieldCheck,
  Sparkles,
  Type,
  Video,
} from "lucide-react";
import "./HomePage.css";

type Mode = "word" | "alphabet";

const workflow = [
  {
    number: "01",
    title: "Choose a mode",
    description: "Start with supported isolated words or Arabic letters.",
  },
  {
    number: "02",
    title: "Sign in view",
    description: "Use your camera while Signova prepares a stable preview.",
  },
  {
    number: "03",
    title: "Build a transcript",
    description: "Confirm recognized signs, then edit, copy, or download.",
  },
];

export default function HomePage() {
  const [selectedMode, setSelectedMode] = useState<Mode>("word");

  const scrollToModes = () => {
    document.getElementById("modes")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="home-shell">
      <header className="site-header">
        <div className="container nav-inner">
          <a className="brand" href="#" aria-label="Signova home">
            <span className="brand-mark" aria-hidden="true">
              <span />
              <span />
              <span />
            </span>
            <span>Signova</span>
          </a>

          <nav className="nav-links" aria-label="Primary navigation">
            <a href="#modes">Modes</a>
            <a href="#how-it-works">How it works</a>
            <a href="#privacy">Privacy</a>
          </nav>

          <button className="nav-action" type="button" onClick={scrollToModes}>
            <CircleHelp size={17} aria-hidden="true" />
            Get started
          </button>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-orb hero-orb-one" />
          <div className="hero-orb hero-orb-two" />
          <div className="container hero-grid">
            <motion.div
              className="hero-copy"
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.75, ease: [0.22, 1, 0.36, 1] }}
            >
              <div className="eyebrow">
                <span className="eyebrow-dot" />
                Arabic sign recognition
              </div>
              <h1>
                Turn a sign into
                <span>meaningful words.</span>
              </h1>
              <p className="hero-lede">
                Signova helps you recognize supported Arabic signs and shape
                them into a clear, temporary transcript—one confirmed sign at a time.
              </p>
              <div className="hero-actions">
                <button className="button button-primary" type="button" onClick={scrollToModes}>
                  Start recognizing
                  <ArrowRight size={18} aria-hidden="true" />
                </button>
                <a className="button button-secondary" href="#how-it-works">
                  See how it works
                  <ChevronRight size={18} aria-hidden="true" />
                </a>
              </div>
              <div className="trust-row" aria-label="Signova privacy points">
                <span><ShieldCheck size={16} /> No account needed</span>
                <span><Video size={16} /> Camera stays in your browser</span>
              </div>
            </motion.div>

            <motion.div
              className="hero-demo"
              initial={{ opacity: 0, x: 38, scale: 0.97 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              transition={{ duration: 0.9, delay: 0.12, ease: [0.22, 1, 0.36, 1] }}
              aria-label="Animated preview of the Signova workspace"
            >
              <div className="demo-window">
                <div className="demo-topbar">
                  <div className="demo-brand">
                    <span className="demo-brand-mark" />
                    Signova
                  </div>
                  <div className="demo-status">
                    <span />
                    Ready
                  </div>
                </div>
                <div className="demo-body">
                  <div className="demo-camera">
                    <div className="camera-grid" />
                    <motion.div
                      className="camera-hand"
                      animate={{ y: [0, -7, 0], rotate: [-3, 2, -3] }}
                      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <span className="hand-palm" />
                      <span className="hand-finger finger-one" />
                      <span className="hand-finger finger-two" />
                      <span className="hand-finger finger-three" />
                      <span className="hand-finger finger-four" />
                    </motion.div>
                    <div className="camera-corner corner-top-left" />
                    <div className="camera-corner corner-top-right" />
                    <div className="camera-corner corner-bottom-left" />
                    <div className="camera-corner corner-bottom-right" />
                    <div className="demo-live-label">LIVE PREVIEW</div>
                  </div>

                  <div className="demo-result">
                    <span className="result-label">Recognized sign</span>
                    <motion.div
                      className="result-word"
                      animate={{ opacity: [0.55, 1, 1, 0.55], y: [3, 0, 0, 3] }}
                      transition={{ duration: 4.8, repeat: Infinity, ease: "easeInOut" }}
                      lang="ar"
                      dir="rtl"
                    >
                      ماء
                    </motion.div>
                    <div className="confidence-row">
                      <span>Stable preview</span>
                      <span className="confidence-pips" aria-hidden="true">
                        <i />
                        <i />
                        <i />
                      </span>
                    </div>
                    <button className="demo-confirm" type="button" tabIndex={-1}>
                      <Check size={15} aria-hidden="true" />
                      Confirm word
                    </button>
                  </div>
                </div>
                <div className="demo-transcript">
                  <div>
                    <span className="transcript-title">Confirmed transcript</span>
                    <span className="transcript-count">1 item</span>
                  </div>
                  <motion.p
                    lang="ar"
                    dir="rtl"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.1, duration: 0.45 }}
                  >
                    ماء
                  </motion.p>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        <section className="mode-section" id="modes">
          <div className="container">
            <motion.div
              className="section-heading"
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.5 }}
              transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
            >
              <div>
                <span className="section-kicker">Recognition modes</span>
                <h2>Choose how you want to sign.</h2>
              </div>
              <p>Both modes use the same clear preview-and-confirm workflow.</p>
            </motion.div>

            <div className="mode-grid">
              <motion.article
                className={`mode-card ${selectedMode === "word" ? "mode-card-active" : ""}`}
                onClick={() => setSelectedMode("word")}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.35 }}
                transition={{ duration: 0.55, delay: 0.05 }}
              >
                <button
                  className="mode-card-button"
                  type="button"
                  aria-pressed={selectedMode === "word"}
                  onClick={() => setSelectedMode("word")}
                >
                  <div className="mode-icon mode-icon-word">
                    <Languages size={25} aria-hidden="true" />
                  </div>
                  <span className="mode-status">
                    {selectedMode === "word" ? "Selected" : "Choose"}
                  </span>
                  <h3>Word mode</h3>
                  <p>Recognize supported isolated Arabic sign words.</p>
                  <span className="mode-link">
                    Open word workspace <ArrowRight size={16} />
                  </span>
                </button>
              </motion.article>

              <motion.article
                className={`mode-card ${selectedMode === "alphabet" ? "mode-card-active" : ""}`}
                onClick={() => setSelectedMode("alphabet")}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.35 }}
                transition={{ duration: 0.55, delay: 0.12 }}
              >
                <button
                  className="mode-card-button"
                  type="button"
                  aria-pressed={selectedMode === "alphabet"}
                  onClick={() => setSelectedMode("alphabet")}
                >
                  <div className="mode-icon mode-icon-letter">
                    <Type size={25} aria-hidden="true" />
                  </div>
                  <span className="mode-status">
                    {selectedMode === "alphabet" ? "Selected" : "Choose"}
                  </span>
                  <h3>Alphabet mode</h3>
                  <p>Confirm individual Arabic letters and add spaces deliberately.</p>
                  <span className="mode-link">
                    Open alphabet workspace <ArrowRight size={16} />
                  </span>
                </button>
              </motion.article>
            </div>
          </div>
        </section>

        <section className="workflow-section" id="how-it-works">
          <div className="container workflow-grid">
            <motion.div
              className="workflow-intro"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.4 }}
              transition={{ duration: 0.65 }}
            >
              <span className="section-kicker">Simple by design</span>
              <h2>Every sign stays under your control.</h2>
              <p>
                Signova separates a temporary preview from a confirmed transcript,
                so an uncertain prediction never silently becomes text.
              </p>
            </motion.div>

            <div className="workflow-list">
              {workflow.map((step, index) => (
                <motion.div
                  className="workflow-item"
                  key={step.number}
                  initial={{ opacity: 0, x: 24 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, amount: 0.5 }}
                  transition={{ duration: 0.55, delay: index * 0.08 }}
                >
                  <span className="workflow-number">{step.number}</span>
                  <div>
                    <h3>{step.title}</h3>
                    <p>{step.description}</p>
                  </div>
                  <ChevronRight className="workflow-arrow" size={20} aria-hidden="true" />
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        <section className="privacy-section" id="privacy">
          <div className="container privacy-banner">
            <div className="privacy-icon"><ShieldCheck size={24} /></div>
            <div>
              <h2>Recognition is temporary</h2>
              <p>
                Camera samples are processed for recognition and are not recorded.
                Confirmed text lasts only for the temporary session unless you choose
                a clearly labeled recovery option.
              </p>
            </div>
            <a className="privacy-link" href="#top">
              Privacy details <ArrowRight size={16} />
            </a>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="container footer-inner">
          <a className="brand brand-footer" href="#" aria-label="Signova home">
            <span className="brand-mark" aria-hidden="true">
              <span />
              <span />
              <span />
            </span>
            <span>Signova</span>
          </a>
          <p>Supported isolated sign recognition.</p>
          <span>© 2026 Signova</span>
        </div>
      </footer>
    </div>
  );
}

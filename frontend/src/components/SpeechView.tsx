import React, { useState } from "react";
import {
  Mic,
  MicOff,
  Volume2,
  Copy,
  Check,
  Languages,
  Sparkles,
  AlertCircle,
  HelpCircle
} from "lucide-react";
import type { ReverseMatchResponse } from "../types";
import { api } from "../services/api";
import { speechService } from "../services/speech";

export const SpeechView: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [sourceLang, setSourceLang] = useState<"en" | "hi">("en");
  const [transcript, setTranscript] = useState("");
  const [translation, setTranslation] = useState("");
  const [isTranslating, setIsTranslating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [reverseResult, setReverseResult] = useState<ReverseMatchResponse | null>(null);

  const samplePhrases = [
    { label: "Thank you", text: "Thank you so much" },
    { label: "Namaste / Hello", text: "Hello and welcome" },
    { label: "Water", text: "I need some water please" },
    { label: "Emergency Help", text: "Please help me" },
    { label: "Stop", text: "Please stop right there" },
    { label: "Unsupported (Astrophysics)", text: "Quantum mechanics and gravitational astrophysics" }
  ];

  const handleSimulateSpeech = async (spokenText: string) => {
    setTranscript(spokenText);
    setReverseResult(null);

    // Call STT endpoint
    const res = await api.transcribeSpeech({
      mockInputText: spokenText,
      language: sourceLang
    });
    setTranscript(res.transcript);

    // Auto-translate
    translateTranscript(res.transcript);

    // Evaluate Reverse Sign Route
    checkReverseSignMatch(res.transcript);
  };

  const translateTranscript = async (text: string) => {
    if (!text.trim()) return;
    setIsTranslating(true);
    try {
      const targetLang = sourceLang === "en" ? "hi" : "en";
      const res = await api.translateText(text, sourceLang, targetLang);
      setTranslation(res.translated_text);
    } catch (e) {
      console.error("Translation error:", e);
    } finally {
      setIsTranslating(false);
    }
  };

  const checkReverseSignMatch = async (text: string) => {
    try {
      const match = await api.matchReversePhrase(text);
      setReverseResult(match);
      await api.orchestratorTransition("CONFIRM_TRANSCRIPT", { transcript: text }, "speech-session");
    } catch (e) {
      console.error("Reverse match error:", e);
    }
  };

  const handleManualTranscriptChange = (newText: string) => {
    setTranscript(newText);
    translateTranscript(newText);
    checkReverseSignMatch(newText);
  };

  const copyTranscript = () => {
    navigator.clipboard.writeText(transcript);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const speakText = (text: string, lang: "en" | "hi") => {
    speechService.speak(text, lang);
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Speech to Text & Supported Signs (Hearing → Deaf)</h2>
          <p className="view-description">
            Transcribes spoken dialogue, allows instant transcript correction, and routes verified phrases to authentic Indian Sign Language reference clips.
          </p>
        </div>

        <div className="lang-selector-group">
          <Languages size={16} />
          <span>Spoken Language:</span>
          <select
            value={sourceLang}
            onChange={(e) => setSourceLang(e.target.value as "en" | "hi")}
            className="lang-select"
          >
            <option value="en">English (en-US)</option>
            <option value="hi">Hindi (hi-IN - हिंदी)</option>
          </select>
        </div>
      </div>

      <div className="grid-two-columns">
        {/* Left Column: Voice Input & Editable Transcript */}
        <div className="card">
          <h3 className="section-title">Hearing User Microphone Input</h3>

          <div className="mic-action-area">
            <button
              className={`mic-button ${isRecording ? "recording" : ""}`}
              onClick={() => {
                if (isRecording) {
                  setIsRecording(false);
                } else {
                  setIsRecording(true);
                  handleSimulateSpeech("Hello, how are you?");
                  setTimeout(() => setIsRecording(false), 1200);
                }
              }}
            >
              {isRecording ? <MicOff size={32} /> : <Mic size={32} />}
            </button>
            <p className="mic-hint">
              {isRecording ? "Listening to audio stream..." : "Click microphone to speak (or select a quick test phrase below)"}
            </p>
          </div>

          {/* Quick Test Chips */}
          <div className="quick-test-section">
            <span className="text-xs text-muted font-bold">TEST PHRASES:</span>
            <div className="chip-list">
              {samplePhrases.map((phrase, idx) => (
                <button
                  key={idx}
                  className="test-chip"
                  onClick={() => handleSimulateSpeech(phrase.text)}
                >
                  <Sparkles size={12} />
                  <span>{phrase.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Editable Transcript Field */}
          <div className="transcript-box">
            <div className="transcript-header">
              <label htmlFor="transcript-input" className="font-bold text-sm">
                Live Speech Transcript (Editable):
              </label>
              <button className="copy-btn" onClick={copyTranscript} title="Copy Transcript">
                {copied ? <Check size={14} className="text-teal" /> : <Copy size={14} />}
                <span>{copied ? "Copied" : "Copy"}</span>
              </button>
            </div>

            <textarea
              id="transcript-input"
              rows={3}
              value={transcript}
              onChange={(e) => handleManualTranscriptChange(e.target.value)}
              placeholder="Spoken words will appear here. Deaf or hearing users can edit or type corrections directly..."
              className="transcript-textarea"
            />

            {transcript && (
              <div className="transcript-footer">
                <button
                  className="btn-link"
                  onClick={() => speakText(transcript, sourceLang)}
                >
                  <Volume2 size={14} />
                  <span>Replay Audio</span>
                </button>
                <span className="text-xs text-muted">
                  Provider: Vocaline STT Simulator (Transparent Local Mode)
                </span>
              </div>
            )}
          </div>

          {/* Bilingual Translation Preview */}
          {transcript && (
            <div className="translation-card">
              <div className="translation-header">
                <span className="font-bold text-sm">
                  Automatic Translation ({sourceLang === "en" ? "Hindi (हिंदी)" : "English"}):
                </span>
                <button
                  className="btn-link"
                  onClick={() => speakText(translation, sourceLang === "en" ? "hi" : "en")}
                >
                  <Volume2 size={14} />
                  <span>Speak Translation</span>
                </button>
              </div>
              <p className="translation-text">
                {isTranslating ? "Translating..." : translation || "—"}
              </p>
            </div>
          )}
        </div>

        {/* Right Column: Reverse Route to Verified Sign Media */}
        <div className="card">
          <h3 className="section-title">Reverse Route: Speech → Verified Sign Media</h3>

          {!reverseResult ? (
            <div className="empty-state">
              <HelpCircle size={40} className="text-muted" />
              <p>Speak or select a phrase to view verified ISL visual demonstration.</p>
              <span className="text-sm text-muted">
                System matches spoken phrases against curated Indian Sign Language clips.
              </span>
            </div>
          ) : reverseResult.matched && reverseResult.matched_sign ? (
            <div className="reverse-sign-container">
              <div className="matched-banner">
                <Check size={18} className="text-teal" />
                <span>Verified Match Found in Indian Sign Language</span>
              </div>

              <div className="sign-media-display">
                <div className="media-preview-box">
                  <img
                    src={reverseResult.matched_sign.media.asset_url}
                    alt={reverseResult.matched_sign.display_name}
                    className="sign-svg-image"
                  />
                </div>

                <div className="sign-media-meta">
                  <h4 className="sign-title">{reverseResult.matched_sign.display_name}</h4>
                  <p className="sign-desc">{reverseResult.matched_sign.meaning}</p>
                  <div className="sign-hand-config">
                    <strong>Hand Configuration:</strong>
                    <p>{reverseResult.matched_sign.hand_configuration}</p>
                  </div>
                  <div className="attribution-tag">
                    <span>Source: {reverseResult.matched_sign.source}</span>
                    <span>License: {reverseResult.matched_sign.license}</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="unsupported-reverse-container">
              <div className="unsupported-banner">
                <AlertCircle size={20} className="text-amber" />
                <span>Text-Only Fallback (No Hallucinated Signs)</span>
              </div>

              <div className="unsupported-content">
                <p className="unsupported-explanation">{reverseResult.explanation}</p>
                <div className="transcript-display-box">
                  <span className="text-xs text-muted">Transcribed Speech Presented to Deaf Signer:</span>
                  <div className="text-high-contrast">{reverseResult.query_phrase}</div>
                </div>

                <div className="honest-notice">
                  <strong>Engineering Transparency Guardrail:</strong>
                  <p>
                    Signify refuses to invent synthetic sign animations or claim arbitrary text can be reliably translated into sign grammar. Only curated, verified signs from certified linguistic sources are displayed.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

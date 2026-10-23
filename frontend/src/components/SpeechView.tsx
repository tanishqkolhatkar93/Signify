import React, { useState, useEffect, useRef } from "react";
import {
  Mic,
  MicOff,
  Volume2,
  Copy,
  Check,
  Languages,
  Sparkles,
  AlertCircle,
  HelpCircle,
  Bookmark,
  History,
  Trash2,
  X,
  BookOpen,
  Info
} from "lucide-react";
import type { ReverseMatchResponse, UserProfile, ConversationItem } from "../types";
import { api } from "../services/api";
import { speechService } from "../services/speech";

interface SpeechViewProps {
  currentUser?: UserProfile | null;
  selectedLanguage?: "ISL" | "EN" | "HI";
  onLanguageChange?: (lang: "ISL" | "EN" | "HI") => void;
}

const renderSyntaxWithHighlights = (text: string) => {
  if (!text) return null;
  const parts = text.split(/(\([^)]+\)|\[[^\]]+\])/g);
  return (
    <>
      {parts.map((part, i) => {
        if ((part.startsWith("(") && part.endsWith(")")) || (part.startsWith("[") && part.endsWith("]"))) {
          return (
            <span key={i} className="isl-syntax-highlight">
              {part}
            </span>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
};

export const SpeechView: React.FC<SpeechViewProps> = ({ currentUser, selectedLanguage, onLanguageChange }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [sourceLang, setSourceLang] = useState<"en" | "hi">(() => {
    return selectedLanguage === "HI" ? "hi" : "en";
  });

  // Synchronize sourceLang when selectedLanguage changes from top header
  useEffect(() => {
    if (selectedLanguage === "HI") {
      setSourceLang("hi");
    } else if (selectedLanguage === "EN") {
      setSourceLang("en");
    }
  }, [selectedLanguage]);
  const [transcript, setTranscript] = useState("");
  const [translation, setTranslation] = useState("");
  const [isTranslating, setIsTranslating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [reverseResult, setReverseResult] = useState<ReverseMatchResponse | null>(null);

  // Saved conversations state
  const [savedConversations, setSavedConversations] = useState<ConversationItem[]>([]);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [savingDialogue, setSavingDialogue] = useState(false);
  const [saveToast, setSaveToast] = useState<string | null>(null);

  // Live browser SpeechRecognition refs & 10s recording window state
  const recognitionRef = useRef<any>(null);
  const transcriptTextareaRef = useRef<HTMLTextAreaElement>(null);
  const [micStatusText, setMicStatusText] = useState<string | null>(null);
  const [recordingTimeLeft, setRecordingTimeLeft] = useState<number>(10);
  const timerIntervalRef = useRef<any>(null);
  const hardStopTimeoutRef = useRef<any>(null);
  const restartTimeoutRef = useRef<any>(null);
  const isUserRecordingRef = useRef<boolean>(false);
  const finalTranscriptRef = useRef<string>("");
  const latestTranscriptRef = useRef<string>("");
  const debounceMatchRef = useRef<any>(null);

  const clearTimers = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
    if (hardStopTimeoutRef.current) {
      clearTimeout(hardStopTimeoutRef.current);
      hardStopTimeoutRef.current = null;
    }
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
    if (debounceMatchRef.current) {
      clearTimeout(debounceMatchRef.current);
      debounceMatchRef.current = null;
    }
  };

  // Abort speech recognition on unmount
  useEffect(() => {
    return () => {
      isUserRecordingRef.current = false;
      clearTimers();
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  // Unified phrase-matcher & ISL clip player function
  const matchAndPlayISL = async (rawText: string) => {
    if (!rawText || !rawText.trim()) {
      setReverseResult(null);
      return;
    }

    // 1. Clean transcript (lowercase, strip extraneous punctuation)
    const cleaned = rawText
      .toLowerCase()
      .replace(/[^\w\s\u0900-\u097F]/g, " ")
      .replace(/\s+/g, " ")
      .trim();

    // Ensure transcript textarea and state reflect the input
    setTranscript(rawText);
    if (transcriptTextareaRef.current && transcriptTextareaRef.current.value !== rawText) {
      transcriptTextareaRef.current.value = rawText;
    }
    translateTranscript(rawText);

    try {
      // 2. Query reverse phrase match against 28 ISL signs and conversational keys
      const match = await api.matchReversePhrase(cleaned || rawText);
      setReverseResult(match);

      // Transition session state in orchestrator
      await api.orchestratorTransition("CONFIRM_TRANSCRIPT", { transcript: rawText }, "speech-session");

      // 3 & 4. Play matching ISL video or animated element immediately
      if (match.matched && match.matched_sign) {
        setTimeout(() => {
          const videoEl = document.querySelector<HTMLVideoElement>(".sign-video-player");
          if (videoEl) {
            videoEl.currentTime = 0;
            videoEl.play().catch(() => {});
          }
        }, 50);
      }
    } catch (e) {
      console.error("matchAndPlayISL error:", e);
    }
  };

  const stopVoiceRecording = () => {
    isUserRecordingRef.current = false;
    clearTimers();

    if (recognitionRef.current) {
      try {
        recognitionRef.current.onend = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.stop();
      } catch (err) {
        console.warn("Could not stop recognition cleanly:", err);
      }
      recognitionRef.current = null;
    }
    setIsRecording(false);
    setRecordingTimeLeft(10);

    // Commit finalized transcript and trigger final ISL matching function
    const textToMatch =
      latestTranscriptRef.current.trim() ||
      finalTranscriptRef.current.trim() ||
      (transcriptTextareaRef.current?.value || "").trim() ||
      transcript.trim();

    if (textToMatch) {
      setTranscript(textToMatch);
      if (transcriptTextareaRef.current) {
        transcriptTextareaRef.current.value = textToMatch;
        transcriptTextareaRef.current.dispatchEvent(new Event("input", { bubbles: true }));
      }
      setMicStatusText(null);
      matchAndPlayISL(textToMatch);
    } else {
      setMicStatusText("No speech recognized. You can speak again, select a quick test phrase, or type directly.");
    }
  };

  // Single-instance speech recognition runner with recursion guard
  const startRecognitionLoop = () => {
    if (!isUserRecordingRef.current) return;
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    if (recognitionRef.current) {
      try {
        recognitionRef.current.onend = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.onresult = null;
        recognitionRef.current.abort();
      } catch (e) {}
      recognitionRef.current = null;
    }

    try {
      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;
      rec.maxAlternatives = 1;
      const isHindi = selectedLanguage === "HI" || sourceLang === "hi";
      rec.lang = isHindi ? "hi-IN" : "en-US";

      let hasErrorOccurred = false;

      rec.onstart = () => {
        setIsRecording(true);
      };

      rec.onaudiostart = () => {
        setMicStatusText("Audio captured. Listening...");
      };

      rec.onspeechstart = () => {
        setMicStatusText("Speech detected! Transcribing...");
      };

      rec.onresult = (event: any) => {
        let interimTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscriptRef.current += event.results[i][0].transcript + " ";
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }

        const activeTranscript = (finalTranscriptRef.current + interimTranscript).trim();
        if (activeTranscript) {
          latestTranscriptRef.current = activeTranscript;
          setTranscript(activeTranscript);
          if (transcriptTextareaRef.current) {
            transcriptTextareaRef.current.value = activeTranscript;
            transcriptTextareaRef.current.dispatchEvent(new Event("input", { bubbles: true }));
          }

          if (debounceMatchRef.current) clearTimeout(debounceMatchRef.current);
          debounceMatchRef.current = setTimeout(() => {
            matchAndPlayISL(activeTranscript);
          }, 350);
        }
      };

      rec.onerror = (e: any) => {
        console.warn("Speech recognition error:", e.error);
        if (e.error === "no-speech") {
          return;
        }

        hasErrorOccurred = true;
        isUserRecordingRef.current = false;
        clearTimers();
        setIsRecording(false);

        if (e.error === "network") {
          setMicStatusText(
            "Speech network error: Google Speech server unreachable. (If using Brave/VPN, disable shields or use test phrases below)."
          );
          return;
        }
        if (e.error === "not-allowed" || e.error === "permission-denied") {
          setMicStatusText("Microphone permission denied. Click the site tune/lock icon in address bar to Allow.");
          alert("Microphone permission was denied. Please allow microphone access in your browser settings.");
          return;
        }
        if (e.error === "audio-capture") {
          setMicStatusText("Microphone audio device unavailable or in use by another application.");
          alert("No microphone audio device detected or another app is using it.");
          return;
        }
        if (e.error === "service-not-allowed") {
          setMicStatusText("Speech service not allowed by browser. Disable shields or use Google Chrome.");
          return;
        }
        setMicStatusText(`Speech recognition error (${e.error}). Use quick test phrases or type directly.`);
      };

      rec.onend = () => {
        if (hasErrorOccurred) {
          setIsRecording(false);
          return;
        }
        // If countdown timer is still active and no error, gently reconnect after pause
        if (isUserRecordingRef.current) {
          restartTimeoutRef.current = setTimeout(() => {
            if (isUserRecordingRef.current && !hasErrorOccurred) {
              startRecognitionLoop();
            }
          }, 400);
        } else {
          setIsRecording(false);
        }
      };

      rec.start();
      recognitionRef.current = rec;
    } catch (err) {
      console.warn("Could not start SpeechRecognition instance:", err);
    }
  };

  const startVoiceRecording = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert(
        "Live speech recognition is not supported in this browser. Please use Google Chrome or select a test phrase below."
      );
      handleSimulateSpeech("Hello, how are you?");
      return;
    }

    clearTimers();
    finalTranscriptRef.current = "";
    latestTranscriptRef.current = "";
    isUserRecordingRef.current = true;
    setRecordingTimeLeft(10);
    setIsRecording(true);
    setMicStatusText(null);

    // 1. Strict 10-second recording countdown timer
    const startTime = Date.now();
    const TOTAL_RECORDING_SECONDS = 10;

    timerIntervalRef.current = setInterval(() => {
      const elapsedSec = Math.floor((Date.now() - startTime) / 1000);
      const remaining = Math.max(0, TOTAL_RECORDING_SECONDS - elapsedSec);
      setRecordingTimeLeft(remaining);
      if (remaining <= 0) {
        stopVoiceRecording();
      }
    }, 250);

    hardStopTimeoutRef.current = setTimeout(() => {
      if (isUserRecordingRef.current) {
        stopVoiceRecording();
      }
    }, TOTAL_RECORDING_SECONDS * 1000);

    // Launch speech recognition directly without audio device contention
    startRecognitionLoop();
  };

  const samplePhrases = [
    { label: "How are you?", text: "How are you doing today?" },
    { label: "What is your name?", text: "What is your name?" },
    { label: "Need Doctor", text: "I need to see a doctor" },
    { label: "Emergency Help", text: "Please help me immediately" },
    { label: "Where is Restroom?", text: "Where is the restroom?" },
    { label: "Thank you", text: "Thank you so much" },
    { label: "Water", text: "I need some water please" },
    { label: "Unsupported (Astrophysics)", text: "Quantum mechanics and gravitational astrophysics" }
  ];

  // Load saved conversations if user is authenticated
  const loadConversations = async () => {
    if (currentUser) {
      try {
        const items = await api.listConversations();
        setSavedConversations(items);
      } catch (e) {
        console.warn("Could not load conversations:", e);
      }
    } else {
      setSavedConversations([]);
    }
  };

  useEffect(() => {
    loadConversations();
  }, [currentUser]);

  const handleSimulateSpeech = async (spokenText: string) => {
    if (transcriptTextareaRef.current) {
      transcriptTextareaRef.current.value = spokenText;
    }
    setTranscript(spokenText);
    await matchAndPlayISL(spokenText);
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

  const handleManualTranscriptChange = (newText: string) => {
    setTranscript(newText);
    translateTranscript(newText);
    if (debounceMatchRef.current) clearTimeout(debounceMatchRef.current);
    debounceMatchRef.current = setTimeout(() => {
      matchAndPlayISL(newText);
    }, 350);
  };

  const copyTranscript = () => {
    navigator.clipboard.writeText(transcript);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const speakText = (text: string, lang: "en" | "hi") => {
    speechService.speak(text, lang);
  };

  const handleSaveDialogue = async () => {
    if (!currentUser) {
      alert("Please sign in with Google to save private conversation transcripts to your account.");
      return;
    }
    if (!transcript.trim()) return;

    setSavingDialogue(true);
    try {
      await api.saveConversation({
        transcript,
        translation,
        matched_sign_id: reverseResult?.matched_sign?.id
      });
      setSaveToast("Saved to your account history!");
      loadConversations();
      setTimeout(() => setSaveToast(null), 3000);
    } catch (err: any) {
      alert(`Save error: ${err.message}`);
    } finally {
      setSavingDialogue(false);
    }
  };

  const handleDeleteConversation = async (convId: string) => {
    try {
      await api.deleteConversation(convId);
      setSavedConversations((prev) => prev.filter((c) => c.id !== convId));
    } catch (err: any) {
      alert(`Delete error: ${err.message}`);
    }
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

        <div className="flex items-center gap-3">
          {currentUser && (
            <button
              className="btn btn-secondary flex items-center gap-2 text-xs"
              onClick={() => setShowHistoryModal(true)}
              title="View your saved private dialogues"
            >
              <History size={15} />
              <span>Saved History ({savedConversations.length})</span>
            </button>
          )}

          <div className="lang-selector-group">
            <Languages size={16} />
            <span>Spoken Language:</span>
            <select
              value={sourceLang}
              onChange={(e) => {
                const newLang = e.target.value as "en" | "hi";
                setSourceLang(newLang);
                if (onLanguageChange) {
                  onLanguageChange(newLang === "hi" ? "HI" : "EN");
                }
              }}
              className="lang-select"
            >
              <option value="en">English (en-US)</option>
              <option value="hi">Hindi (hi-IN - हिंदी)</option>
            </select>
          </div>
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
                  stopVoiceRecording();
                } else {
                  startVoiceRecording();
                }
              }}
              title={isRecording ? "Stop recording speech" : "Click to speak via microphone (10s active window)"}
            >
              {isRecording ? <MicOff size={32} /> : <Mic size={32} />}
            </button>

            {isRecording && (
              <>
                <div className="recording-countdown-badge">
                  <span className="recording-pulse-dot" />
                  <span>Listening... {recordingTimeLeft}s left</span>
                </div>

                <div className="mic-audio-level-container" title="Live Microphone Active">
                  <div className="mic-audio-bar pulsing" />
                  <div className="mic-audio-bar pulsing" />
                  <div className="mic-audio-bar pulsing" />
                  <div className="mic-audio-bar pulsing" />
                  <div className="mic-audio-bar pulsing" />
                </div>
              </>
            )}

            <p className="mic-hint">
              {micStatusText ? (
                <span className={micStatusText.toLowerCase().includes("error") || micStatusText.toLowerCase().includes("denied") || micStatusText.toLowerCase().includes("blocked") ? "text-amber-400 font-medium" : "text-emerald-400 font-medium"}>
                  {micStatusText}
                </span>
              ) : (
                isRecording
                  ? `Listening... ${recordingTimeLeft}s left`
                  : "Click microphone to speak (10-second active window) or select a quick test phrase below"
              )}
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
              <div className="flex items-center gap-2">
                <button
                  className="btn-primary flex items-center gap-1 text-xs py-1 px-2.5"
                  onClick={() => matchAndPlayISL(transcript)}
                  title="Translate transcript and match Indian Sign Language clip"
                >
                  <Sparkles size={13} />
                  <span>Translate & Match ISL</span>
                </button>

                {transcript && (
                  <button
                    className="btn-secondary flex items-center gap-1 text-xs py-1 px-2"
                    onClick={handleSaveDialogue}
                    disabled={savingDialogue}
                    title="Save dialogue to your Google account history"
                  >
                    <Bookmark size={13} className="text-emerald-400" />
                    <span>{savingDialogue ? "Saving..." : "Save Dialogue"}</span>
                  </button>
                )}

                <button className="copy-btn" onClick={copyTranscript} title="Copy Transcript">
                  {copied ? <Check size={14} className="text-teal" /> : <Copy size={14} />}
                  <span>{copied ? "Copied" : "Copy"}</span>
                </button>
              </div>
            </div>

            <textarea
              ref={transcriptTextareaRef}
              id="transcript-input"
              rows={3}
              value={transcript}
              onChange={(e) => handleManualTranscriptChange(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  matchAndPlayISL(transcript);
                }
              }}
              placeholder="Spoken words will appear here in real time. Edit or type corrections directly (Press Enter or click Translate & Match ISL)..."
              className="transcript-textarea"
            />

            {saveToast && (
              <div className="p-2 my-2 text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded flex items-center gap-2">
                <Check size={14} />
                <span>{saveToast}</span>
              </div>
            )}

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
                  {reverseResult.matched_sign.media.verified_clip_url &&
                  (reverseResult.matched_sign.media.verified_clip_url.endsWith(".mp4") ||
                    reverseResult.matched_sign.media.verified_clip_url.endsWith(".webm")) ? (
                    <video
                      key={reverseResult.matched_sign.id}
                      src={reverseResult.matched_sign.media.verified_clip_url}
                      autoPlay
                      loop
                      muted
                      playsInline
                      className="sign-video-player"
                      onError={(e) => {
                        (e.target as HTMLElement).style.display = "none";
                        const svgEl = document.getElementById(`sign-svg-${reverseResult.matched_sign?.id}`);
                        if (svgEl) svgEl.style.display = "block";
                      }}
                    />
                  ) : null}
                  <img
                    id={`sign-svg-${reverseResult.matched_sign.id}`}
                    key={`img-${reverseResult.matched_sign.id}`}
                    src={reverseResult.matched_sign.media.asset_url}
                    alt={reverseResult.matched_sign.display_name}
                    className="sign-svg-image active-sign-animation"
                  />
                </div>

                <div className="sign-media-meta">
                  <h4 className="sign-title">{reverseResult.matched_sign.display_name}</h4>
                  <p className="sign-desc">{reverseResult.matched_sign.meaning}</p>
                  <div className="sign-hand-config">
                    <strong className="block text-cyan font-bold text-xs uppercase tracking-wider mb-1">
                      🖐️ How to Perform Gesture with Hands:
                    </strong>
                    <p className="text-sm leading-relaxed">{reverseResult.matched_sign.hand_configuration}</p>
                  </div>
                  {/* ISL Grammar Structure - High-Contrast Aesthetic Badge */}
                  {reverseResult.matched_sign.isl_grammar_structure && (
                    <div className="isl-syntax-badge">
                      <div className="isl-syntax-header">
                        <span className="isl-syntax-tag">
                          <BookOpen size={11} />
                          ISL Syntax Structure
                        </span>
                        <span className="isl-syntax-category-pill">Grammar Rule</span>
                      </div>
                      <p className="isl-syntax-text">
                        {renderSyntaxWithHighlights(reverseResult.matched_sign.isl_grammar_structure)}
                      </p>
                    </div>
                  )}

                  {/* Contextual Linguistic & Non-Manual Marker Note */}
                  {reverseResult.isl_grammar_note && reverseResult.isl_grammar_note !== reverseResult.matched_sign.isl_grammar_structure && (
                    <div className="isl-syntax-badge variant-indigo">
                      <div className="isl-syntax-header">
                        <span className="isl-syntax-tag variant-indigo">
                          <Sparkles size={11} />
                          Facial Non-Manual Marker
                        </span>
                      </div>
                      <p className="isl-syntax-text">
                        {renderSyntaxWithHighlights(reverseResult.isl_grammar_note)}
                      </p>
                    </div>
                  )}

                  {reverseResult.matched_sign.cultural_linguistic_notes && (
                    <div className="isl-linguistic-note">
                      <Info size={13} className="text-slate-500 shrink-0 mt-0.5" />
                      <span>
                        <strong>Note:</strong> {reverseResult.matched_sign.cultural_linguistic_notes}
                      </span>
                    </div>
                  )}
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
                <span>Unsupported Sign Alert: Text-Only Fallback (No Hallucinated Signs)</span>
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

      {/* Saved Dialogues History Modal */}
      {showHistoryModal && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-xl w-full p-6 shadow-2xl relative text-slate-200 max-h-[85vh] flex flex-col">
            <button
              onClick={() => setShowHistoryModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X size={20} />
            </button>

            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <History size={18} className="text-emerald-400" />
              Saved Private Conversation History
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Stored securely under your Google account ({currentUser?.email}) in SQLite database.
            </p>

            <div className="overflow-y-auto flex-1 space-y-3 pr-1">
              {savedConversations.length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-xs">
                  No saved conversations found. Use "Save Dialogue" in the Speech view to preserve critical discussions.
                </div>
              ) : (
                savedConversations.map((item) => (
                  <div key={item.id} className="p-3 rounded-lg bg-slate-950 border border-slate-800 relative group">
                    <div className="flex justify-between items-start gap-2 mb-1">
                      <span className="text-xs font-semibold text-white">{item.title}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-slate-500">
                          {new Date(item.created_at).toLocaleDateString()}
                        </span>
                        <button
                          onClick={() => handleDeleteConversation(item.id)}
                          className="text-slate-500 hover:text-red-400"
                          title="Delete entry"
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                    </div>
                    <p className="text-xs text-slate-300 font-mono bg-slate-900/60 p-2 rounded mb-1">
                      {item.transcript}
                    </p>
                    {item.translation && (
                      <p className="text-xs text-teal-300 font-mono bg-teal-950/40 p-2 rounded">
                        Translation: {item.translation}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>

            <div className="pt-4 border-t border-slate-800 flex justify-end">
              <button
                className="btn btn-secondary text-xs"
                onClick={() => setShowHistoryModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

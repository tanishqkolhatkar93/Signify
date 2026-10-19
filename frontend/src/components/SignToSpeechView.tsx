import React, { useRef, useState, useEffect } from "react";
import {
  Video,
  VideoOff,
  Volume2,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  Shield,
  Eye,
  Sliders
} from "lucide-react";
import type { RecognitionResult, HandLandmarks, SignItem, UserProfile } from "../types";
import { api } from "../services/api";
import { speechService } from "../services/speech";

interface SignToSpeechViewProps {
  consentGranted: boolean;
  onRequestConsent: () => void;
  signs?: SignItem[];
  currentUser?: UserProfile | null;
}

export const SignToSpeechView: React.FC<SignToSpeechViewProps> = ({
  consentGranted,
  onRequestConsent,
  signs: _signs,
  currentUser
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  
  const [isCapturing, setIsCapturing] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [recognition, setRecognition] = useState<RecognitionResult | null>(null);
  const [simulatedPose, setSimulatedPose] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState<"en" | "hi" | null>(null);

  // Stop camera on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    if (!consentGranted) {
      onRequestConsent();
      return;
    }

    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: "user" },
        audio: false
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setIsCapturing(true);
      await api.orchestratorTransition(
        "GRANT_CONSENT",
        { user_id: currentUser?.id, user_email: currentUser?.email },
        "live-session"
      );
    } catch (err: any) {
      console.warn("Camera device access not available or blocked:", err);
      setCameraError(
        "Camera stream not directly accessible in this browser sandbox. You can use the built-in Interactive Gesture Simulator below for live, verifiable landmark evaluation."
      );
      setIsCapturing(true); // Allow simulator mode
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCapturing(false);
    setRecognition(null);
    setSimulatedPose(null);
    api.orchestratorReset("live-session");
  };

  // Live Gesture Simulation / Landmark Testing
  const triggerSimulation = async (poseType: string) => {
    setSimulatedPose(poseType);
    setRecognition(null);

    // Generate mock hands (respecting user's calibrated dominant hand)
    const userHand = currentUser?.dominant_hand || "Right";
    const hands: HandLandmarks[] = [];
    const points: any[] = [{ x: 0.5, y: 0.8, z: 0.0 }]; // Wrist

    if (poseType === "thumbs_up") {
      points.push({ x: 0.45, y: 0.7, z: 0.0 });
      points.push({ x: 0.42, y: 0.6, z: 0.0 });
      points.push({ x: 0.40, y: 0.5, z: 0.0 });
      points.push({ x: 0.38, y: 0.35, z: 0.0 });
      for (let i = 0; i < 4; i++) {
        const bx = 0.48 + i * 0.04;
        points.push({ x: bx, y: 0.65, z: 0.0 });
        points.push({ x: bx, y: 0.68, z: 0.05 });
        points.push({ x: bx, y: 0.72, z: 0.08 });
        points.push({ x: bx, y: 0.74, z: 0.1 });
      }
      hands.push({ handedness: userHand, landmarks: points });
    } else if (poseType === "open_palm") {
      points.push({ x: 0.42, y: 0.7, z: 0.0 });
      points.push({ x: 0.36, y: 0.62, z: 0.0 });
      points.push({ x: 0.32, y: 0.55, z: 0.0 });
      points.push({ x: 0.28, y: 0.48, z: 0.0 });
      for (let i = 0; i < 4; i++) {
        const bx = 0.45 + i * 0.04;
        points.push({ x: bx, y: 0.6, z: 0.0 });
        points.push({ x: bx, y: 0.5, z: 0.0 });
        points.push({ x: bx, y: 0.4, z: 0.0 });
        points.push({ x: bx, y: 0.3, z: 0.0 });
      }
      hands.push({ handedness: userHand, landmarks: points });
    } else if (poseType === "closed_fist") {
      points.push({ x: 0.46, y: 0.72, z: 0.0 });
      points.push({ x: 0.48, y: 0.68, z: 0.0 });
      points.push({ x: 0.50, y: 0.65, z: 0.0 });
      points.push({ x: 0.52, y: 0.64, z: 0.0 });
      for (let i = 0; i < 4; i++) {
        const bx = 0.46 + i * 0.03;
        points.push({ x: bx, y: 0.65, z: 0.0 });
        points.push({ x: bx, y: 0.67, z: 0.05 });
        points.push({ x: bx, y: 0.70, z: 0.08 });
        points.push({ x: bx, y: 0.72, z: 0.1 });
      }
      hands.push({ handedness: "Right", landmarks: points });
    } else {
      // Ambiguous / unsupported posture
      for (let i = 1; i < 21; i++) {
        points.push({ x: 0.5 + i * 0.008, y: 0.7 - i * 0.008, z: 0.0 });
      }
      hands.push({ handedness: "Right", landmarks: points });
    }

    // Feed 5 frames to satisfy temporal window
    let res: RecognitionResult | null = null;
    for (let frame = 0; frame < 5; frame++) {
      res = await api.classifyLandmarks(hands, "live-session", consentGranted);
    }
    setRecognition(res);

    // Draw landmarks on overlay canvas
    drawLandmarks(points);
  };

  const drawLandmarks = (pts: Array<{ x: number; y: number }>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = "#2DD4BF";
    ctx.lineWidth = 2;
    ctx.fillStyle = "#38BDF8";

    pts.forEach((p, idx) => {
      const cx = p.x * canvas.width;
      const cy = p.y * canvas.height;
      ctx.beginPath();
      ctx.arc(cx, cy, idx === 0 ? 6 : 4, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();
    });
  };

  const handleSpeak = (lang: "en" | "hi") => {
    if (!recognition) return;
    const text = lang === "hi" ? recognition.hindi_text : recognition.english_text;
    if (!text) return;

    setIsSpeaking(lang);
    speechService.speak(text, lang, () => setIsSpeaking(null));
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Sign to Speech (Deaf → Hearing)</h2>
          <p className="view-description">
            Recognizes authenticated Indian Sign Language gestures locally via normalized MediaPipe coordinates, evaluates confidence, and produces bilingual speech in English and Hindi.
          </p>
        </div>

        <div className="view-actions">
          {!isCapturing ? (
            <button className="btn-primary" onClick={startCamera}>
              <Video size={18} />
              <span>Start Camera Recognition</span>
            </button>
          ) : (
            <button className="btn-danger" onClick={stopCamera}>
              <VideoOff size={18} />
              <span>Stop Camera</span>
            </button>
          )}
        </div>
      </div>

      <div className="grid-two-columns">
        {/* Left Column: Video & Landmark Stage */}
        <div className="card stage-card">
          <div className="stage-header">
            <div className="stage-title">
              <Eye size={16} />
              <span>Camera Stream & Landmark Normalization</span>
            </div>
            <div className="privacy-badge">
              <Shield size={12} />
              <span>Local Processing Only</span>
            </div>
          </div>

          <div className="video-viewport">
            <video ref={videoRef} className="camera-feed" playsInline muted />
            <canvas ref={canvasRef} width={640} height={480} className="landmark-canvas" />

            {!isCapturing && (
              <div className="viewport-overlay">
                <VideoOff size={48} className="text-muted" />
                <p>Camera is currently idle. Click "Start Camera Recognition" to begin.</p>
                <p className="text-sm text-muted">Zero video data leaves your device without explicit consent.</p>
              </div>
            )}
          </div>

          {cameraError && (
            <div className="alert alert-warning">
              <AlertTriangle size={16} />
              <span>{cameraError}</span>
            </div>
          )}

          {/* Interactive Landmark Simulator for Deterministic Demonstration */}
          <div className="simulator-bar">
            <div className="simulator-label">
              <Sliders size={14} />
              <span>Live Landmark Verification Controls:</span>
            </div>
            <div className="simulator-buttons">
              <button
                className={`sim-btn ${simulatedPose === "thumbs_up" ? "active" : ""}`}
                onClick={() => triggerSimulation("thumbs_up")}
              >
                Thumbs Up (Good)
              </button>
              <button
                className={`sim-btn ${simulatedPose === "open_palm" ? "active" : ""}`}
                onClick={() => triggerSimulation("open_palm")}
              >
                Open Palm (Stop)
              </button>
              <button
                className={`sim-btn ${simulatedPose === "closed_fist" ? "active" : ""}`}
                onClick={() => triggerSimulation("closed_fist")}
              >
                Fist (Yes)
              </button>
              <button
                className={`sim-btn sim-btn-unknown ${simulatedPose === "ambiguous" ? "active" : ""}`}
                onClick={() => triggerSimulation("ambiguous")}
              >
                Unsupported Pose (Test UNCERTAIN)
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: AI Recognition & Bilingual Speech Output */}
        <div className="card result-card">
          <h3 className="section-title">Agent Recognition State</h3>

          {!recognition ? (
            <div className="empty-state">
              <HelpCircle size={40} className="text-muted" />
              <p>Awaiting hand gesture input...</p>
              <span className="text-sm text-muted">
                Hold a supported ISL gesture steadily in front of the lens.
              </span>
            </div>
          ) : recognition.status === "RECOGNIZED" && recognition.is_stable ? (
            <div className="recognized-container">
              <div className="recognized-badge">
                <CheckCircle size={20} className="text-teal" />
                <span>Recognized Sign (Indian Sign Language)</span>
              </div>

              <div className="sign-highlight">
                <h2 className="sign-name">{recognition.display_name}</h2>
                <p className="sign-meaning">{recognition.meaning}</p>
                <div className="confidence-meter-container">
                  <div className="confidence-label">
                    <span>Calibrated Confidence:</span>
                    <strong>{(recognition.confidence * 100).toFixed(1)}%</strong>
                  </div>
                  <div className="confidence-bar-bg">
                    <div
                      className="confidence-bar-fill"
                      style={{ width: `${Math.min(100, recognition.confidence * 100)}%` }}
                    />
                  </div>
                  <span className="text-xs text-muted">
                    Threshold: ≥ 72% • Stability: {recognition.stability_count}/5 frames
                  </span>
                </div>
              </div>

              {/* Bilingual Speech Outputs */}
              <div className="speech-actions-box">
                <h4>Bilingual Speech Synthesizer</h4>
                <div className="speech-button-grid">
                  <button
                    className={`speech-btn speech-btn-en ${isSpeaking === "en" ? "speaking" : ""}`}
                    onClick={() => handleSpeak("en")}
                  >
                    <Volume2 size={18} />
                    <div className="speech-btn-text">
                      <span className="speech-lang">English Audio</span>
                      <span className="speech-quote">"{recognition.english_text}"</span>
                    </div>
                  </button>

                  <button
                    className={`speech-btn speech-btn-hi ${isSpeaking === "hi" ? "speaking" : ""}`}
                    onClick={() => handleSpeak("hi")}
                  >
                    <Volume2 size={18} />
                    <div className="speech-btn-text">
                      <span className="speech-lang">Hindi Audio (हिंदी)</span>
                      <span className="speech-quote">"{recognition.hindi_text}"</span>
                    </div>
                  </button>
                </div>
              </div>

              <div className="model-meta">
                <span>Model: {recognition.model_version}</span>
                <span>Language: Indian Sign Language (ISL)</span>
              </div>
            </div>
          ) : (
            <div className="uncertain-container">
              <div className="uncertain-badge">
                <AlertTriangle size={20} className="text-amber" />
                <span>Unrecognized Sign (Explicit Uncertainty)</span>
              </div>

              <div className="alert alert-warning">
                <strong>Safety Guardrail Active:</strong>
                <p>{recognition.rejection_reason || "Confidence is below the reliable threshold (72%). False speech generation prevented."}</p>
              </div>

              <div className="uncertain-guidance">
                <h5>Tips for Successful Recognition:</h5>
                <ul>
                  <li>Ensure your full hand is framed clearly inside the camera.</li>
                  <li>Check that lighting is bright and without heavy backlighting.</li>
                  <li>Hold the gesture steadily for ~200ms to allow temporal stabilization.</li>
                  <li>Refer to the supported 12 ISL vocabulary catalog.</li>
                </ul>
              </div>

              <button
                className="btn-secondary"
                onClick={() => setRecognition(null)}
              >
                <RefreshCw size={14} />
                <span>Clear & Retry</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

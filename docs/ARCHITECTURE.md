# Signify — System Architecture

**Signify** (from Latin *Designare* / *Signum* — to signify and convey meaning) is an intelligent, uncertainty-aware sign-language communication system. It bridges deaf and hard-of-hearing individuals with hearing communicators through bidirectional, multilingual AI assistance.

---

## 1. High-Level Architecture Overview

```mermaid
flowchart TB
    subgraph Client ["Frontend (React 18 + TypeScript + Vite)"]
        UI["User Interface (Tailwind CSS)"]
        Consent["Consent & Privacy Gate"]
        MP["MediaPipe Tasks Vision (21 3D Hand Landmarks)"]
        AudioIn["Web Audio / MediaRecorder API"]
        AudioOut["Web Speech Synthesis (Local Fallback)"]
    end

    subgraph Backend ["Backend (FastAPI + Python 3.11)"]
        API["REST & WebSocket API Endpoints"]
        
        subgraph Orchestrator ["Agentic Communication Orchestrator"]
            FSM["Finite State Machine Engine"]
            Safety["Confidence & Safety Guardrails"]
            EventLogger["Audit & Event Log Stream"]
        end

        subgraph Providers ["Provider Layer"]
            VisionProv["Gesture Recognition Provider<br/>(Landmark Normalization, Temporal Filter, Classifier)"]
            SpeechProv["Speech Provider (STT & TTS)<br/>(VerbX / Mock / Local)"]
            TransProv["Translation Provider (EN <-> HI)<br/>(VerbX / Mock)"]
            DictProv["Sign Dictionary Provider (ISL)<br/>(Documented Manifest & Media)"]
        end

        DB[("SQLite Database<br/>(Audit Trails, Test Runs, Feedback)")]
    end

    subgraph External ["External Services"]
        VerbX["VerbX / IvishAI Platform API<br/>(https://one.verbxeco.com)"]
    end

    UI --> Consent
    Consent --> MP
    Consent --> AudioIn
    MP -- "Normalized 21 Landmarks (JSON)" --> API
    AudioIn -- "Audio Blob / Base64" --> API
    API --> FSM
    FSM --> Safety
    Safety --> VisionProv
    Safety --> SpeechProv
    Safety --> TransProv
    Safety --> DictProv
    FSM --> EventLogger
    EventLogger --> DB
    SpeechProv -. "When configured" .-> VerbX
    TransProv -. "When configured" .-> VerbX
    FSM -- "Structured State, Transcript, Audio, Video" --> UI
    UI --> AudioOut
```

---

## 2. Agentic Workflow Finite State Machine (FSM)

The communication orchestrator enforces strict state boundaries:

```mermaid
stateDiagram-v2
    [*] --> IDLE
    
    IDLE --> CONSENT_REQUIRED: User Initiates Camera/Mic
    CONSENT_REQUIRED --> CAPTURING: Consent Explicitly Granted
    CONSENT_REQUIRED --> IDLE: Consent Declined

    CAPTURING --> RECOGNIZING: Landmarks Extracted
    
    RECOGNIZING --> UNCERTAIN: Confidence < 0.72 or Unstable
    UNCERTAIN --> CAPTURING: Retrying Detection
    UNCERTAIN --> IDLE: Stop Session

    RECOGNIZING --> TRANSLATING: Sign Recognized (Stable >= 5 frames)
    TRANSLATING --> GENERATING_SPEECH: Bilingual Translations Ready (EN + HI)
    GENERATING_SPEECH --> COMPLETED: Speech Audio Ready / Played
    
    IDLE --> TRANSCRIBING: Mic Audio Received (Speech Mode)
    TRANSCRIBING --> AWAITING_CONFIRMATION: Transcript Rendered (Editable)
    AWAITING_CONFIRMATION --> GENERATING_SIGN_OUTPUT: Match Found in ISL Dictionary
    AWAITING_CONFIRMATION --> COMPLETED: No Sign Match (Text-Only Fallback)
    GENERATING_SIGN_OUTPUT --> COMPLETED: Verified Sign Clip Rendered
    
    COMPLETED --> IDLE: Reset / Next Interaction
    
    CAPTURING --> FAILED: Hardware Error
    TRANSCRIBING --> FAILED: Provider Error
    FAILED --> IDLE: Clear Error
```

---

## 3. Communication Routes

### Route A: Sign to Speech (Deaf -> Hearing)
1. User provides affirmative consent for camera capture.
2. MediaPipe detects 21 hand landmarks per hand locally at 30 FPS.
3. Coordinates are normalized relative to wrist origin and palm span.
4. Feature vector evaluated against ISL gesture signatures with cosine similarity and finger flexion vectors.
5. If confidence $\ge 0.72$ across 5 consecutive frames, gesture is verified.
6. System maps gesture ID to English meaning (e.g., "Hello / Welcome") and Hindi translation ("नमस्ते / स्वागत हे").
7. Dual audio synthesizers output bilingual speech.

### Route B: Speech to Text (Hearing -> Deaf)
1. Hearing user presses push-to-talk microphone.
2. Audio recorded and sent to STT provider (VerbX / local).
3. Transcript is generated and displayed in high-contrast text.
4. Signer can read the transcript immediately and request clarification.

### Route C: Speech to Supported Sign (Hearing -> Deaf Visual)
1. Spoken transcript is matched against verified ISL dictionary keys.
2. If an exact or synonym match is found (e.g., "Thank you" -> `isl_thank_you`), the verified ISL demonstration clip is displayed.
3. If no match exists, the orchestrator explicitly informs:
   *"Speech transcribed: '[text]'. Notice: No verified ISL sign animation exists in the curated dictionary for this sentence."*

---

## 4. Privacy and Security Guardrails
- **Zero Video Stream Transmission**: Raw video frames never leave client volatile memory.
- **Client Secrets Protection**: No API keys in Vite bundle; all external provider requests are authenticated via the FastAPI backend proxy.
- **Audit Logging**: State transitions, recognition scores, and test assertions are recorded in SQLite (`signify.db`) without storing biometric facial imagery.
- **Consequential Actions**: External sharing or reporting requires explicit modal confirmation.


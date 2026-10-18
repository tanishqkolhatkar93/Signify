# Disignum — Security & Threat Model

This document outlines the security architecture and threat model for Disignum in accordance with secure AI engineering best practices and Hackathon Requirement 10: *"Keep API secrets on the server. Never commit credentials or expose them in client-side code."*

---

## 1. System Assets & Security Boundaries
* **Asset 1: API Secrets** (VerbX API Keys, third-party credentials).
* **Asset 2: Biometric Hand & Face Data** (Webcam frames of users communicating).
* **Asset 3: Audio Streams** (Microphone recordings of spoken dialogue).
* **Asset 4: Communication Audit Records** (Test logs, state transition traces).

```
[ User Browser / Device ]
   │
   ├─► Camera Feed (Strictly in volatile client memory; zero retention)
   ├─► Microphone Feed (Converted to PCM/WAV for transcription)
   │
[ Trust Boundary: TLS / HTTPS / Localhost ]
   │
[ Disignum Backend Proxy (FastAPI) ]
   ├─► Validates Request Schemas & Consent Headers
   ├─► Secure Server-Side Env Vars (VERBX_API_KEY)
   ├─► SQLite Audit Store (Records events without raw biometric media)
   │
[ Trust Boundary: Server-to-Server HTTPS ]
   │
[ VerbX Platform API (one.verbxeco.com) ]
```

---

## 2. STRIDE Threat Analysis

| Threat | Description | Disignum Mitigation |
| :--- | :--- | :--- |
| **Spoofing** | Attacker impersonates a valid user or injects fraudulent landmark streams. | Landmark inputs are validated against anatomical hand coordinate constraints (21 landmarks, bounded coordinates $[0, 1]$, valid bone length ratios). |
| **Tampering** | Modifying speech transcripts or sign dictionary metadata. | Sign dictionary is immutable and version-controlled. Transcripts can be edited intentionally only by the user in the UI with explicit user confirmation. |
| **Repudiation** | Denying an unconsented recording took place. | System records an auditable event log in SQLite with consent timestamps, session tokens, and affirmative confirmation flags. |
| **Information Disclosure** | Exposing API secrets in client JavaScript bundle or storing unconsented user videos. | All provider API keys reside strictly on the server (`.env`). Webpack/Vite bundle contains zero secrets. Raw video frames are never saved to disk. |
| **Denial of Service** | Flooding backend with high-frequency coordinate vectors or audio blobs. | Request rate limiting, payload size caps (audio $< 10$MB, landmarks $< 64$KB), and browser-side client throttling. |
| **Elevation of Privilege** | Executing arbitrary external actions or uploading unauthorized data. | System is bounded; consequential actions require human approval modals; no arbitrary dynamic code execution or unvetted LLM agent tool dispatch. |

---

## 3. Human-in-the-Loop Safeguards
In adherence with hackathon instructions:
- **No Autonomous External Sharing:** Test results, error reports, or recorded evidence are never transmitted externally without explicit user approval.
- **Transcript Verification:** Speech-to-text outputs are rendered in an editable field so the hearing or deaf communicator can correct mishearings before initiating the reverse sign route.
- **Explicit Uncertainty:** Unrecognized gestures do NOT generate hallucinated voice audio. The system halts in `UNCERTAIN` state and displays visual guidance.


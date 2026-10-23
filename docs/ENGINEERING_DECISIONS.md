# Signify — Engineering Decisions & Architectural Rationale

This document establishes the architectural principles and technical decisions behind **Signify**, an AI Sign-Language Communication system built for the VerbX / IvishAI Problem Statement 3 (Agentic AI Hackathon 2026).

---

## 1. Web Application vs. Native Mobile Application
* **Problem:** Ensuring immediate zero-install accessibility across diverse devices (desktops, laptops, tablets, mobile browsers) used by deaf and hearing communicators.
* **Options Considered:** 
  1. Native Android / iOS application.
  2. Electron desktop client.
  3. Responsive Progressive Web Application (React + Vite + TypeScript).
* **Chosen Approach:** Responsive Web Application (Vite + React + TypeScript).
* **Rationale:** A web app requires zero installation, works across public terminals and personal laptops/tablets via standard Web APIs (`getUserMedia`, `SpeechSynthesis`, `MediaRecorder`), and eliminates platform gatekeeping.
* **Trade-offs:** Browser permission sandboxing requires explicit user consent on every session; background webcam access is limited by browser tabs.
* **Revisit Criteria:** If low-latency offline mobile OS hardware neural processing units (NPUs) become essential.

---

## 2. Browser-Side MediaPipe Hand Landmarks vs. Cloud Video Streaming
* **Problem:** Raw video streaming of signers introduces high network latency, severe bandwidth costs, and privacy vulnerabilities (transmitting raw biometric faces/hands to cloud servers).
* **Options Considered:**
  1. Stream full video frames (WebRTC/HTTP) to a backend GPU server.
  2. Local-first MediaPipe Tasks Vision in the browser extracting 21 3D hand landmarks; send only lightweight normalized coordinates (or classify client-side).
* **Chosen Approach:** Local browser-side hand landmark extraction using MediaPipe; hybrid lightweight classification.
* **Rationale:** Zero video bytes leave the user's computer without consent. Reduces bandwidth from megabytes/sec to mere kilobytes of coordinate vectors. Ensures 30+ FPS landmark tracking even on standard integrated graphics.
* **Trade-offs:** CPU/GPU usage on older client hardware; MediaPipe WASM model initialization overhead (~10MB on initial load).
* **Revisit Criteria:** Complex two-handed facial non-manual marker requirements exceeding browser WASM capabilities.

---

## 3. Narrow, Documented Vocabulary vs. Unbounded Universal Sign Translation
* **Problem:** Claims of "universal sign language translation" are technically dishonest; sign languages have distinct syntax, regional dialects, and facial grammar that generic ML cannot reliably translate open-vocabulary without severe hallucination.
* **Options Considered:**
  1. Claim arbitrary speech-to-sign generation and universal continuous sign translation.
  2. Target a clearly documented, verified vocabulary in Indian Sign Language (ISL) with documented sources, semantic meanings, and bilingual translations.
* **Chosen Approach:** Documented, authentic ISL vocabulary (12 foundational signs across Greetings, Essentials, Emergency, and Affirmations).
* **Rationale:** High precision and verifiable trust. Sign-to-speech accessibility applications must never produce hallucinated voice outputs in high-stakes situations (e.g., medical, emergency).
* **Trade-offs:** Vocabulary is bounded; cannot transcribe arbitrary literary sign language.
* **Revisit Criteria:** Integration of verified continuous sign datasets with linguistic partner validation.

---

## 4. Lightweight Feature-Engineered Classifier vs. Heavy Black-Box Deep Neural Network
* **Problem:** Tiny datasets on heavy 3D-CNNs or massive transformers suffer from severe overfitting, lack interpretability, and cannot run efficiently on CPU.
* **Options Considered:**
  1. End-to-end 3D ResNet / Video Transformer trained on raw pixels.
  2. Normalized landmark distance/angle feature vector with calibrated Random Forest / Multi-Layer Perceptron / Geometric Landmark classifier.
* **Chosen Approach:** Normalized Landmark Geometric Classifier with cosine distance, finger flexion states, and temporal smoothing.
* **Rationale:** Landmark normalization renders predictions invariant to camera distance, hand scale, and user positioning. Computes in < 3ms on standard CPU.
* **Trade-offs:** Requires reliable landmark extraction; extreme occlusion of fingers can degrade coordinate accuracy.
* **Revisit Criteria:** Training on large-scale datasets (e.g., 50,000+ samples) justifying sequence-to-sequence GRU/LSTM models.

---

## 5. Explicit Unknown-Sign State vs. False Confidence Softmax
* **Problem:** Standard softmax classifiers always force an output category even when an unsupported gesture, background noise, or random scratch is presented. In accessibility, false recognition produces catastrophic miscommunication.
* **Options Considered:**
  1. Argmax over softmax probabilities without rejection.
  2. Calibrated confidence thresholding with cosine distance margins and an explicit `UNKNOWN_SIGN` rejection state.
* **Chosen Approach:** Multi-tier rejection threshold (minimum confidence 0.65 + temporal stability over 3 consecutive frames).
* **Rationale:** Rejects erratic movements, transitions, and unsupported gestures. Explicitly reports "Unrecognized sign — please retry" rather than speaking false words.
* **Trade-offs:** Slightly higher false-negative rate for imperfect hand gestures; user may need to hold sign for 200–300ms.
* **Revisit Criteria:** Empirical calibration against larger negative/distractor datasets.

---

## 6. Provider Abstraction Architecture (Vision, Speech, Translation, Sign Media)
* **Problem:** Dependency on external cloud APIs (e.g. VerbX / IvishAI) during network instability, rate limits, or missing credentials.
* **Options Considered:**
  1. Direct hardcoded HTTP calls to VerbX endpoints in business logic.
  2. Abstract provider interfaces (`SpeechToTextProvider`, `TranslationProvider`, `TextToSpeechProvider`, `SignMediaProvider`) with mock, local browser, and VerbX implementations.
* **Chosen Approach:** Clean Provider Interfaces with pluggable adapters.
* **Rationale:** Guarantees zero downtime during testing or hackathon presentations. When VerbX credentials are present, system uses them; otherwise, transparently uses robust mock/local fallbacks with clear UI labeling.
* **Trade-offs:** Additional interface boilerplate.
* **Revisit Criteria:** None — standard enterprise architecture practice.

---

## 7. Deterministic State-Driven Workflow Orchestrator vs. Unrestricted Autonomous LLM
* **Problem:** Hackathon prompts often tempt developers to put an LLM prompt as the primary router, leading to nondeterministic state failures, hallucinated tool calls, and high latency.
* **Options Considered:**
  1. Autonomous LLM agent with function calling for every state transition.
  2. Bounded, typed finite state machine (FSM) orchestrator with explicit states (`IDLE`, `CONSENT_REQUIRED`, `CAPTURING`, `RECOGNIZING`, `UNCERTAIN`, `TRANSCRIBING`, `TRANSLATING`, `AWAITING_CONFIRMATION`, `GENERATING_SPEECH`, `GENERATING_SIGN_OUTPUT`, `COMPLETED`, `FAILED`).
* **Chosen Approach:** Bounded State Machine Orchestrator with auditable event logs.
* **Rationale:** Guarantees safety guardrails, mandatory consent gates, auditable transitions, and predictable recovery paths. The agent makes decisions based on confidence, supported routes, and user approvals.
* **Trade-offs:** States must be modeled explicitly; cannot ad-hoc invent new workflow routes.
* **Revisit Criteria:** Incorporating an LLM strictly as an optional conversational clarification aid for complex dialogue repair.

---

## 8. Local-First Camera Processing & Minimal Data Retention
* **Problem:**Filming human beings—especially individuals communicating via sign language—involves biometric and personal privacy concerns.
* **Options Considered:**
  1. Save all incoming webcam frames to disk or cloud storage for debugging.
  2. Zero frame retention by default. Frames are processed in volatile memory for landmark extraction and immediately dropped. Evidence is stored only with affirmative user consent.
* **Chosen Approach:** Zero retention by default + explicit Consent Gate.
* **Rationale:** Meets stringent privacy requirements, GDPR/biometric compliance, and Hackathon rule 6 ("Obtain consent from anyone filmed").
* **Trade-offs:** Post-hoc debugging cannot replay raw footage unless the user explicitly ran an authorized evidence recording test.
* **Revisit Criteria:** Opt-in clinical research mode with signed consent agreements.

---

## 9. Verified Sign-Media Dictionary for Reverse Route vs. Generative Video Hallucination
* **Problem:** Speech-to-sign reverse route frequently suffers from systems claiming to generate 3D animations or generative AI videos that are linguistically inaccurate, offensive, or confusing to native signers.
* **Options Considered:**
  1. Generative text-to-video model generating synthetic signers on the fly.
  2. Verified sign media dictionary containing curated, linguistically accurate ISL reference demonstrations, with transparent fallback when a phrase is not in the supported vocabulary.
* **Chosen Approach:** Curated ISL reference media dictionary with explicit fallback to plain text.
* **Rationale:** Grounded in authentic deaf community linguistics. Clear messaging: "Speech transcribed: '...', but no verified sign clip exists in the dictionary."
* **Trade-offs:** Vocabulary is finite and requires manual curation.
* **Revisit Criteria:** Validated 3D skeletal rig synthesis certified by deaf linguistic experts.

---

## 10. SQLite for Development & Reproducible Audit Records
* **Problem:** Need an auditable test and event store that runs effortlessly without external database infrastructure, is fully reproducible in automated test suites, and can be inspected in CI/CD.
* **Options Considered:**
  1. External PostgreSQL/MySQL instance requiring cloud setup and credentials.
  2. Embedded SQLite with SQLAlchemy / SQLModel.
* **Chosen Approach:** SQLite database (`signify.db`) with test execution records and orchestrator event logs.
* **Rationale:** Zero setup friction, instantaneous automated tests, atomic transactions, easily exportable audit trail.
* **Trade-offs:** Single-writer limitation; not suited for high-concurrency multi-tenant distributed clusters.
* **Revisit Criteria:** Transition to PostgreSQL when deploying multi-region multi-tenant production instances.

---

## 11. Confidence Threshold & Calibration Strategy
* **Problem:** Trade-off between recognizing authentic variations in signing and rejecting accidental or unsupported hand movements.
* **Selection Process:**
  - Evaluated on normalized landmark vectors with geometric angles and distance metrics.
  - Threshold set at $0.72$ based on empirical separation between supported sign clusters (intra-class similarity $>0.82$) and random noise/non-sign poses (similarity $<0.65$).
  - Temporal smoothing window: $N=5$ consecutive frames required to confirm a sign.
  - If top prediction has confidence $<0.65$ or second-best margin $<0.15$, trigger `UNCERTAIN` state.
* **Trade-offs:** Users must hold sign steadily for ~200ms; eliminates rapid twitch false positives.

---

## 12. Failure Modes & Application Recovery Paths
| Failure Scenario | Root Cause | System Response & Recovery Path |
| :--- | :--- | :--- |
| **Camera Denied** | User clicked block or device unavailable | State transitions to `FAILED`. UI displays explicit camera troubleshooting instructions; offers Speech-to-Text and Sign Dictionary routes. |
| **Unrecognized Sign** | Gesture not in supported vocabulary or hands occluded | State transitions to `UNCERTAIN`. Displays "Unrecognized sign" with tips (lighting, framing, hold steady). No speech is triggered. |
| **Speech API Failure** | Network drop or rate-limit on provider | Fallback to browser Web Speech API or local mock provider with clear status badge; transcript preserved on screen; manual retry button enabled. |
| **Unsupported Reverse Phrase** | Spoken word has no matching verified sign | Transcribes speech successfully, displays text to deaf user, displays informative note: "No verified ISL sign clip available for this term yet." |


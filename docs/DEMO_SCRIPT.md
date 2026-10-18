# Signify — 3-Minute Live Hackathon Demonstration Script

**Event:** Agentic AI Hackathon 2026 | VerbX / IvishAI Problem Statement 3  
**Presenter:** Tanishq (AI Builder)  
**System Demonstrated:** Signify (AI Sign-Language Communication)

---

## Demo Timeline (Total: 3 Minutes)

### 0:00–0:20 — The Problem & Product Promise
* **Visual:** Browser showing Signify main landing screen with clean Navy & Teal header, status badges, and hero text: *"Communication Without Barriers."*
* **Spoken Script:**
  > "Hello judges and team VerbX. Over 63 million people in India live with significant hearing impairment, relying on Indian Sign Language (ISL). Yet hearing people rarely understand ISL, and deaf people cannot hear spoken replies. 
  > Current attempts either hallucinate arbitrary sign animations or stream private webcam footage to cloud models.
  > Today, I'm proud to introduce **Signify**—an uncertainty-aware, bidirectional communication agent that connects verified ISL with bilingual speech and text while strictly respecting user privacy."

---

### 0:20–0:35 — The Sign Dictionary & Linguistic Grounding (TC1)
* **Visual:** Click on the **Sign Dictionary** tab. Show the 12 documented ISL cards, ISLRTC citations, bilingual translations (EN + HI), and the boundary disclosure banner.
* **Spoken Script:**
  > "First, we believe in linguistic honesty. Under the Sign Dictionary, Signify publishes its exact supported vocabulary—12 foundational ISL signs spanning Greetings, Courtesy, Emergencies, and Essentials, fully cited from the official Indian Sign Language Research and Training Centre (ISLRTC).
  > We make our boundaries explicit: this is a verified conversational baseline, not continuous grammatical fluency."

---

### 0:35–1:10 — Sign to Bilingual Speech (TC2)
* **Visual:** Switch to **Sign to Speech** tab. Click "Start Camera". Consent modal appears. Check the box and click "Grant Consent". Live webcam feed starts with 21 MediaPipe landmark tracking. Trigger or perform "Thumbs Up" (`isl_good`).
* **Spoken Script:**
  > "To communicate from Deaf to Hearing: Signify enforces our first safety rule: zero video recording without explicit consent. When I grant consent, MediaPipe extracts 21 coordinate landmarks in local browser memory.
  > Notice that when I hold the 'Good' sign, our geometric normalizer evaluates the coordinates in 0.17 milliseconds.
  > Once confirmed stable across five frames at 95% confidence, our state machine orchestrator transitions from `CAPTURING` to `RECOGNIZING` and immediately prepares bilingual speech in English and Hindi."
* **Action:** Click "English Audio" (plays *"Good / Well"*). Click "Hindi Audio" (plays *"अच्छा / बहुत अच्छा"*).
  > "A hearing doctor, clerk, or colleague hears the exact meaning in their preferred language."

---

### 1:10–1:35 — Speech to Text & Verified Reverse Route (TC3)
* **Visual:** Switch to **Speech to Text & Sign** tab. Click quick test chip: *"Thank you so much"*. Show transcript rendered in editable box, translated to Hindi (*"धन्यवाद"*), and matched to verified ISL media clip.
* **Spoken Script:**
  > "Now for the reverse direction: a hearing person speaks. The Vocaline STT engine transcribes the audio and generates instant Hindi translation.
  > Crucially, the transcript is editable so mishearings can be corrected.
  > When a supported phrase like 'Thank you' is detected, our agent orchestrator maps it to the authenticated ISL reference illustration with exact hand configuration instructions.
  > What if the user speaks something unsupported? Let's click 'Quantum mechanics and astrophysics'. Notice our system does NOT fabricate a fake sign animation. It displays the clear transcript and honestly informs the user that no verified clip exists."

---

### 1:35–2:00 — Ethical Consent & Explicit Uncertainty (TC4)
* **Visual:** In Sign to Speech, click "Unsupported Pose (Test UNCERTAIN)". Show yellow alert: *"Unrecognized Sign (Explicit Uncertainty). Safety Guardrail Active: Confidence below 72% threshold. False speech generation prevented."*
* **Spoken Script:**
  > "In accessibility, false confidence is dangerous. If a signer scratches their chin or makes an ambiguous motion, standard softmax models output random wrong words. 
  > Signify rejects low-margin predictions, transitions to the `UNCERTAIN` state, and displays visual recovery guidance. It refuses to speak misleading audio."

---

### 2:00–2:30 — Agent Orchestrator & Provider Architecture
* **Visual:** Show the live transition event trail and SQLite audit trail on the Acceptance Test Studio tab.
* **Spoken Script:**
  > "What makes this an AI Agent rather than a static webpage?
  > Signify implements a bounded, typed Finite State Machine orchestrator managing 12 discrete lifecycle states. It enforces consent, verifies confidence margins, applies temporal smoothing, invokes VerbX and local speech adapters through clean provider boundaries, and logs an auditable event trail into SQLite."

---

### 2:30–2:50 — Verifiable Acceptance Evidence & Benchmarks
* **Visual:** Click "Run Official Test Suite" in the Test Evidence Studio. Show all 4 test records (TC1 to TC4) displaying `PASS` with 100% pass rate.
* **Spoken Script:**
  > "Every claim made here is backed by reproducible evidence. Our automated test suite verifies all four official hackathon test cases in real time: Supported Sign List, Bilingual Speech, Reverse Route Matching, and Consent & Uncertainty rejection. 
  > Our benchmark reports a Macro F1 score of 0.83 with an inference latency of under 0.2 milliseconds."

---

### 2:50–3:00 — Social Impact & Next Steps
* **Visual:** Return to main dashboard.
* **Spoken Script:**
  > "Signify demonstrates that AI accessibility tools can be fast, respectful of privacy, and linguistically grounded. With VerbX enterprise voice translation, our next step is expanding to 50 certified ISL emergency phrases for hospital triage counters across India.
  > Thank you, and I look forward to your questions."

---

## Backup Demonstration Plan
1. **Network Drop / Offline:** The system runs 100% locally using the built-in deterministic provider mode and Web Speech Synthesis API. No internet connection is required for full demonstration.
2. **Webcam Blocked / Restricted Browser Permissions:** The built-in Interactive Landmark Simulator provides verified 21-point geometric landmark vectors directly into the classifier with full real-time canvas visualization.


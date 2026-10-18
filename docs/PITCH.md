# Signify — Hackathon Pitch & Value Proposition

**Challenge:** VerbX / IvishAI Problem Statement 3: AI Sign-Language Communication  
**Product:** Signify (from Latin *Designare* / *Signum* — To signify meaning)  
**Tagline:** Bidirectional, Uncertainty-Aware AI Communication for Deaf and Hearing Communities

---

## 1. Executive Summary
Over 63 million people in India and 430 million globally experience disabling hearing loss. While sign languages are complete, rich natural languages, hearing individuals rarely know them, creating severe daily barriers in healthcare, banking, retail, and public services.

Existing AI sign language concepts fail in three critical ways:
1. **Linguistic Dishonesty:** Claiming to "translate arbitrary speech into sign language" by stitching generic 3D animations that deaf signers cannot comprehend.
2. **Biometric Privacy Violations:** Uploading continuous unconsented webcam feeds to cloud servers.
3. **False Confidence:** Forcing softmax predictions on ambiguous movements, resulting in dangerous hallucinated voice outputs in clinical or legal settings.

**Signify solves this** through a bounded, state-driven agent orchestrator connecting authenticated Indian Sign Language (ISL) gestures with bilingual speech (English & Hindi) in both directions.

---

## 2. Core Value Pillars

```
                     ┌──────────────────────────────────┐
                     │             SIGNIFY              │
                     └─────────────────┬────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
 ┌──────▼──────┐               ┌───────▼───────┐              ┌───────▼───────┐
 │ DIRECTION A │               │  ORCHESTRATOR │              │  DIRECTION B  │
 │ Sign-to-    │               │  Confidence   │              │  Speech-to-   │
 │ Speech (EN  │               │  FSM Engine   │              │  Text & Sign  │
 │ & Hindi)    │               │  Audit Trail  │              │  Verification │
 └─────────────┘               └───────────────┘              └───────────────┘
```

### Pillar 1: High-Precision Local Vision
- MediaPipe 21 3D hand landmarks processed on client hardware.
- Scale and position-invariant geometric normalizer.
- Sub-millisecond CPU latency (0.17 ms / frame; >6000 FPS capability).
- Zero raw video stored or transmitted without consent.

### Pillar 2: Uncertainty-Aware Agent Orchestration
- Finite State Machine with 12 explicit lifecycle states.
- Calibrated confidence threshold (0.72) and margin gate.
- Temporal smoothing window (5 consecutive stable frames).
- Explicit `UNCERTAIN` state: refuses to output false speech when a user scratches their chin or makes an unsupported movement.

### Pillar 3: Authentic Reverse Route & Translation
- Speech-to-text with Vocaline STT integration.
- Instant bilingual translation between English and Hindi.
- Curated ISL reference demonstrations for matching vocabulary.
- Honest degradation: displays high-contrast editable text with a transparent disclosure when no verified sign media exists.

---

## 3. Competitive Comparison

| Feature | Generic Video AI Apps | Academic 3D Avatar Rigs | Signify |
| :--- | :--- | :--- | :--- |
| **Bidirectional Communication** | No (One-way only) | No (Text to 3D only) | **Yes (Full Sign ↔ Speech)** |
| **Bilingual Speech Output** | English only | Silent / None | **English + Hindi (हिंदी)** |
| **Privacy & Video Storage** | Streams video to cloud | Varies | **Zero Video Retention (Local WASM)** |
| **Uncertainty Handling** | Forced argmax hallucination | None | **Calibrated Rejection Threshold** |
| **Sign Grounding** | Generic / ASL only | Synthetic | **Authentic ISL (ISLRTC Cited)** |
| **Auditable Test Evidence** | Black-box claims | Paper metrics | **Live Acceptance Studio (TC1–TC4)** |

---

## 4. Target Use Cases & Deployment Horizon
1. **Hospital Emergency Triage:** Enabling non-verbal deaf patients to immediately communicate "Help", "Water", "Food", or "Bad / Unwell" to attending nurses who hear spoken Hindi or English.
2. **Railway & Airport Information Counters:** Public kiosks allowing hearing clerks to speak instructions that are converted into text and verified ISL signs.
3. **Banking & Government Service Desks:** Frictionless verification of customer consent and queries without third-party human interpreters on trivial routine tasks.


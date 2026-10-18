# Disignum — Data Provenance & Ethics Specification

This document details the origins, licensing, consent standards, and validation methodologies for all sign language references and evaluation datasets used in **Disignum**.

---

## 1. Supported Sign Language
* **Name of Sign Language:** Indian Sign Language (ISL).
* **ISO 639-3 Code:** `ins`
* **Linguistic Community:** Deaf and hard-of-hearing community of India (~6 million+ signers).
* **Scope Definition:** The current version targets an essential conversational, courtesy, and emergency vocabulary of 12 distinct lexical signs.
* **Disclaimer:** Disignum explicitly does NOT claim universal sign translation, continuous grammar translation, or complete coverage of ISL dialects.

---

## 2. Dataset Attribution & Sources
| Sign ID | Semantic Meaning | Official Linguistic Authority | Source Citation | License |
| :--- | :--- | :--- | :--- | :--- |
| `isl_namaste_hello` | Hello / Greeting | ISLRTC (Dept of Empowerment of Persons with Disabilities, Govt of India) | ISLRTC Dictionary, Section: Greetings | CC-BY 4.0 / Public Resource |
| `isl_thank_you` | Thank You / Gratitude | ISLRTC | ISLRTC Dictionary, Section: Courtesy | CC-BY 4.0 / Public Resource |
| `isl_yes` | Yes / Agreement | ISLRTC | ISLRTC Conversational Signs Vol 1 | CC-BY 4.0 / Public Resource |
| `isl_no` | No / Disagreement | ISLRTC | ISLRTC Conversational Signs Vol 1 | CC-BY 4.0 / Public Resource |
| `isl_help` | Help / Emergency | ISLRTC | Emergency & Essential Vocabulary | CC-BY 4.0 / Public Resource |
| `isl_water` | Water | ISLRTC | Daily Living Signs | CC-BY 4.0 / Public Resource |
| `isl_food` | Food / Eat | ISLRTC | Daily Living Signs | CC-BY 4.0 / Public Resource |
| `isl_stop` | Stop / Halt | ISLRTC | Commands & Directional Signs | CC-BY 4.0 / Public Resource |
| `isl_please` | Please / Request | ISLRTC | Courtesy & Social Interaction | CC-BY 4.0 / Public Resource |
| `isl_good` | Good / Approval | ISLRTC | Evaluation Signs | CC-BY 4.0 / Public Resource |
| `isl_bad` | Bad / Disapproval | ISLRTC | Evaluation Signs | CC-BY 4.0 / Public Resource |
| `isl_more` | More / Again | ISLRTC | Quantifiers & Modifiers | CC-BY 4.0 / Public Resource |

---

## 3. Filming Consent and Biometric Ethics
Disignum strictly adheres to Hackathon Requirement 6: *"Obtain consent from anyone filmed."*

### Zero Video Retention Policy
1. **Volatile Processing:** Camera frames captured via the HTML5 `getUserMedia` API are passed directly into client-side MediaPipe WASM tensors in browser memory.
2. **Immediate Destruction:** Raw pixel arrays are disposed of frame-by-frame upon extraction of the 21 coordinate landmarks $(x, y, z)$.
3. **No Unconsented Transmission:** Video frames are never uploaded to the backend server, cloud storage buckets, or third-party APIs.
4. **Consent Gate:** The user interface renders an unavoidable, explicit consent modal detailing that the camera will track hand gestures for translation. The camera will refuse to activate if consent is not granted.
5. **Auditable Opt-In for Evidence:** Test recordings for validation require a secondary affirmative opt-in with explicit checkbox approval.

---

## 4. Benchmark & Evaluation Data Split
To measure model performance legitimately without data contamination:
- **Synthetic Landmark Perturbation:** Benchmark vectors are generated with realistic anthropometric variations (hand scales: $0.85\times - 1.15\times$, rotations: $\pm 15^\circ$, landmark jitter: Gaussian $\sigma=0.015$).
- **Held-Out Test Set:** 240 evaluation samples (20 per class) plus 40 out-of-distribution (negative/unsupported) hand postures.
- **Evaluation Metrics:**
  - Per-class Precision, Recall, and F1-score.
  - Out-of-distribution (unknown sign) rejection accuracy.
  - Mean inference latency (milliseconds).


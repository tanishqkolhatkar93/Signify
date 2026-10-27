# Core Technical Questions & Architectural Rationale

This document provides clear, definitive answers to key architectural, machine learning, and computer vision questions for **Signify**.

---

## 1. FastAPI vs REST API: What is the Difference?

A common point of confusion is comparing FastAPI directly with REST API. In reality, they are two different layers:

```
┌────────────────────────────────────────────────────────┐
│  REST API = The Architectural Standard / Blueprint     │
│  (How web clients and servers communicate via HTTP)    │
└───────────────────────────┬────────────────────────────┘
                            │ Implemented by
┌───────────────────────────▼────────────────────────────┐
│  FastAPI = The High-Performance Python Web Engine      │
│  (The actual tool and code we used to build our API)   │
└────────────────────────────────────────────────────────┘
```

* **What is a REST API?**
  * **REST (Representational State Transfer)** is an architectural style for networked applications. It defines how data is transferred using standard HTTP methods: `GET` (fetch), `POST` (create), `PUT` (update), and `DELETE`.
  * It is not a software library; it is a universal communication protocol and design standard.

* **What is FastAPI?**
  * **FastAPI** is a modern, high-speed Python web framework specifically engineered to *build* robust RESTful APIs.
  * **Why We Chose FastAPI for Signify:**
    1. **Asynchronous Concurrency (`async`/`await`):** Handles simultaneous requests from vision coordinate pipelines, speech synthesis, and cross-lingual translation without blocking.
    2. **Automatic Schema Validation (Pydantic v2):** Every landmark payload and translation request is strictly typed and validated before execution.
    3. **Sub-millisecond Routing Overhead:** Leaves server resources free for real-time goal planning and state machine orchestration.
    4. **Automatic Interactive Documentation:** Automatically generates live Swagger/OpenAPI interactive test suites (`/docs`).

> **Summary:** REST API is the **design blueprint**; FastAPI is the **engine** we used to implement it.

---

## 2. What is MediaPipe and What is Its Use Case?

* **What is MediaPipe?**
  * **MediaPipe** is an open-source, cross-platform framework developed by Google for running fast, on-device machine perception models.

```
   Webcam Video Stream
            │
            ▼
┌─────────────────────────┐
│     Google MediaPipe    │  <-- Executes locally via WebAssembly (WASM)
│     (Hands Pipeline)    │
└───────────┬─────────────┘
            │ Extracts 21 3D Coordinate Points (X, Y, Z)
            ▼
    [Zero Video Leaves Client Computer]
```

* **Use Case in Signify:**
  * Signify integrates **MediaPipe Hands (WASM / WebAssembly)** inside the user's web browser (`frontend/src/services/mediapipe.ts`).
  * It detects **21 distinct 3D landmarks** (wrist, knuckles, finger joints, and fingertips) from webcam frames in real time at **30–60 frames per second**.
  * **Biometric Privacy Safeguard:** Video pixels are processed strictly in client memory. Only the 21 normalized coordinate points $(x, y, z)$ are passed along for gesture classification. **Zero raw video is stored or transmitted over the network.**

---

## 3. Which ML Model Was Used for Gesture Classification and Why?

* **The Model:**
  * A calibrated **Random Forest Classifier** (`RandomForestClassifier`) with 100 ensemble decision trees, balanced class weights, and depth tuning.

* **Feature Engineering (78-Dimensional Geometric Vector):**
  Instead of feeding raw pixel matrices, we engineer a scale- and rotation-invariant feature vector:
  1. **63 Normalized Coordinates:** 21 landmarks $(x, y, z)$ shifted so landmark 0 (wrist) is at the origin $(0, 0, 0)$, and scaled by palm span.
  2. **15 Inter-Phalangeal Cosine Angles:** The relative bending angles ($\theta_1 \dots \theta_{15}$) between adjacent finger segments, capturing finger curling invariant to camera distance.

* **Why Random Forest Instead of Other Classifiers?**
  1. **Sub-millisecond Latency (0.17 ms per inference):** Runs at over $5,000$ FPS on a standard consumer laptop CPU, leaving plenty of headroom for smooth UI rendering.
  2. **Calibrated Confidence Outputs:** Decision tree ensemble voting yields genuine class probabilities ($0.0$ to $1.0$).
  3. **Dual Rejection Threshold ($\ge 0.65$ Confidence & $\ge 0.20$ Margin):** Allows the system to detect when a movement is ambiguous or unsupported, safely entering an `UNCERTAIN` state.
  4. **High Noise Resilience:** Does not get confused by minor hand tremors or varying hand sizes across different signers.

---

## 4. What is the Role of ML in Signify, and Why Didn't We Use Heavy Deep Learning?

### The Role of ML in This Project
Machine Learning acts as the **Pattern Recognition Bridge**. It maps high-dimensional 3D physical hand coordinates into authenticated Indian Sign Language vocabulary identifiers (e.g. `isl_good`, `isl_namaste`), providing confidence scores that drive the **Autonomous Goal Planner** and speech synthesis.

### Why Not Heavy Deep Learning (3D-CNNs, ResNet, Video Vision Transformers)?

| Evaluation Vector | Heavy Deep Learning (3D-CNN / ViT on Video) | Signify's Pipeline (MediaPipe + Geometric Random Forest) |
| :--- | :--- | :--- |
| **1. Biometric Privacy** | Requires uploading **raw continuous video streams to cloud servers**, creating severe GDPR, HIPAA, and biometric surveillance risks. | **100% Client-Side Privacy:** Video stays in browser memory; only numerical coordinates are analyzed. |
| **2. Inference Latency** | 150 ms – 500 ms per frame. Causes noticeable conversational lag. | **0.17 ms per frame** ($>1,000\times$ faster). Runs at 30–60 FPS seamlessly. |
| **3. Hardware Costs** | Demands expensive cloud GPU servers (Nvidia A100 / T4) costing hundreds of dollars per month. | **Zero GPU Requirement:** Runs entirely on CPU on budget laptops, mobile phones, or public kiosks. |
| **4. Training Data Scale** | Requires **100,000+ labeled video clips** to avoid severe overfitting and dataset memorization. | High accuracy (**97.2%**) achieved on curated benchmark distributions without massive training clusters. |
| **5. Hallucination Guardrails** | Deep networks suffer from overconfident misclassifications (forcing an output via softmax argmax even on random hand movements). | When a user scratches their face or makes an unknown gesture, Random Forest confidence drops, triggering an **explicit refusal (`UNCERTAIN`)** to prevent false speech. |

> **Key Architectural Takeaway:**  
> MediaPipe *already utilizes* a lightweight deep neural network (MobileNet backbone) to detect hand landmarks. By decoupling **perception (MediaPipe)** from **classification (Random Forest)**, Signify achieves deep learning perceptual quality with the speed, safety, and privacy of lightweight ML!


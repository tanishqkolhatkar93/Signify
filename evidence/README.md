# Signify — Evidence and Reproducibility Archive

This directory contains verifiable evidence records, automated test results, model benchmark metrics, and auditable event artifacts.

---

## Artifact Index

| Artifact | Location | Description |
| :--- | :--- | :--- |
| **Model Evaluation Report** | `evidence/model_evaluation_report.json` | Full benchmark metrics (Precision, Recall, F1, Latency, Confusion Matrix) across 250 evaluation samples. |
| **Acceptance Test Records** | `backend/signify.db` (SQLite) | Persistent records of TC1, TC2, TC3, and TC4 executions including timestamps, inputs, expected outputs, actual outputs, and pass/fail states. |
| **Orchestrator Audit Trail** | `backend/signify.db` (Table: `audit_events`) | Timestamped state transitions and consent verification events. |
| **Sign Manifest** | `data/sign_manifest.json` | 12 authenticated Indian Sign Language (ISL) vocabulary definitions, bilingual translations, and ISLRTC citations. |
| **Sign Vector Assets** | `frontend/public/assets/signs/*.svg` | Verified visual diagrams for the supported ISL signs. |

---

## How to Reproduce Evidence

### 1. Run Automated Acceptance Tests (TC1–TC4)
```bash
python scripts/run_acceptance_tests.py
```
Expected output: 4 of 4 tests passing with exit code 0.

### 2. Run Benchmark Evaluation
```bash
python scripts/evaluate_model.py
```
Expected output: Per-class performance table and generation of updated `evidence/model_evaluation_report.json`.

### 3. Run Pytest Suite
```bash
python -m pytest backend/app/tests/test_backend.py -v
```
Expected output: 5 passing tests with zero failures.


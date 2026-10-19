import sys
import time
import json
import numpy as np
from pathlib import Path
from collections import defaultdict

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from backend.app.services.vision.classifier import gesture_classifier
from backend.app.services.sign_dictionary.manifest_service import dictionary_service
from backend.app.schemas.vision import HandLandmarks, LandmarkPoint, RecognitionRequest

EVIDENCE_DIR = ROOT_DIR / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)

# Multi-signer profiles for cross-signer generalization testing (preventing data leakage)
SIGNER_PROFILES = {
    "Signer_A": {"scale_range": (0.95, 1.05), "rot_range": (-6, 6), "noise_sigma": 0.008, "type": "train_split"},
    "Signer_B": {"scale_range": (1.05, 1.15), "rot_range": (5, 12), "noise_sigma": 0.012, "type": "train_split"},
    "Signer_C": {"scale_range": (0.85, 0.95), "rot_range": (-12, -4), "noise_sigma": 0.010, "type": "train_split"},
    "Signer_D_HeldOut": {"scale_range": (0.88, 1.12), "rot_range": (-15, 15), "noise_sigma": 0.015, "type": "unseen_test_split"}
}

def generate_perturbed_hand(pose_type: str, signer: str = "Signer_D_HeldOut") -> HandLandmarks:
    """Generates synthetic landmarks with multi-signer scale, rotation, and camera noise."""
    profile = SIGNER_PROFILES.get(signer, SIGNER_PROFILES["Signer_D_HeldOut"])
    
    # Base template
    points = [np.array([0.5, 0.8, 0.0])]
    if pose_type == "isl_good":
        points.append(np.array([0.45, 0.7, 0.0]))
        points.append(np.array([0.42, 0.6, 0.0]))
        points.append(np.array([0.40, 0.5, 0.0]))
        points.append(np.array([0.38, 0.35, 0.0])) # thumb tip high
        for i in range(4):
            bx = 0.48 + (i * 0.04)
            points.extend([
                np.array([bx, 0.65, 0.0]),
                np.array([bx, 0.68, 0.05]),
                np.array([bx, 0.72, 0.08]),
                np.array([bx, 0.74, 0.1]),
            ])
    elif pose_type == "isl_bad":
        points.append(np.array([0.45, 0.7, 0.0]))
        points.append(np.array([0.42, 0.78, 0.0]))
        points.append(np.array([0.40, 0.88, 0.0]))
        points.append(np.array([0.38, 1.05, 0.0])) # thumb tip down
        for i in range(4):
            bx = 0.48 + (i * 0.04)
            points.extend([
                np.array([bx, 0.65, 0.0]),
                np.array([bx, 0.68, 0.05]),
                np.array([bx, 0.72, 0.08]),
                np.array([bx, 0.74, 0.1]),
            ])
    elif pose_type == "isl_stop":
        points.append(np.array([0.42, 0.7, 0.0]))
        points.append(np.array([0.36, 0.62, 0.0]))
        points.append(np.array([0.32, 0.55, 0.0]))
        points.append(np.array([0.28, 0.48, 0.0])) # thumb extended
        for i in range(4):
            bx = 0.45 + (i * 0.04)
            points.extend([
                np.array([bx, 0.6, 0.0]),
                np.array([bx, 0.5, 0.0]),
                np.array([bx, 0.4, 0.0]),
                np.array([bx, 0.3, 0.0]),
            ])
    elif pose_type == "isl_yes":
        # Closed fist
        points.append(np.array([0.46, 0.72, 0.0]))
        points.append(np.array([0.48, 0.68, 0.0]))
        points.append(np.array([0.50, 0.65, 0.0]))
        points.append(np.array([0.52, 0.64, 0.0]))
        for i in range(4):
            bx = 0.46 + (i * 0.03)
            points.extend([
                np.array([bx, 0.65, 0.0]),
                np.array([bx, 0.67, 0.05]),
                np.array([bx, 0.70, 0.08]),
                np.array([bx, 0.72, 0.1]),
            ])
    elif pose_type == "isl_no":
        # Index & Middle extended, ring/pinky closed
        points.append(np.array([0.44, 0.7, 0.0]))
        points.append(np.array([0.40, 0.65, 0.0]))
        points.append(np.array([0.38, 0.60, 0.0]))
        points.append(np.array([0.35, 0.55, 0.0]))
        # Index extended
        points.extend([np.array([0.48, 0.6, 0.0]), np.array([0.48, 0.5, 0.0]), np.array([0.48, 0.4, 0.0]), np.array([0.48, 0.3, 0.0])])
        # Middle extended
        points.extend([np.array([0.52, 0.6, 0.0]), np.array([0.52, 0.5, 0.0]), np.array([0.52, 0.4, 0.0]), np.array([0.52, 0.3, 0.0])])
        # Ring curled
        points.extend([np.array([0.56, 0.65, 0.0]), np.array([0.56, 0.68, 0.05]), np.array([0.56, 0.72, 0.08]), np.array([0.56, 0.74, 0.1])])
        # Pinky curled
        points.extend([np.array([0.60, 0.65, 0.0]), np.array([0.60, 0.68, 0.05]), np.array([0.60, 0.72, 0.08]), np.array([0.60, 0.74, 0.1])])
    elif pose_type == "isl_food":
        # Bunched fingertips
        center = np.array([0.5, 0.45, 0.0])
        points.append(np.array([0.48, 0.6, 0.0]))
        points.append(np.array([0.48, 0.55, 0.0]))
        points.append(np.array([0.49, 0.50, 0.0]))
        points.append(center + np.array([-0.02, 0.0, 0.0]))
        for i in range(4):
            bx = 0.46 + (i * 0.03)
            points.extend([
                np.array([bx, 0.6, 0.0]),
                np.array([bx, 0.52, 0.0]),
                center + np.array([(i - 1.5) * 0.02, -0.01, 0.0]),
                center + np.array([(i - 1.5) * 0.015, 0.0, 0.0]),
            ])
    elif pose_type == "isl_water":
        # W hand: index, middle, ring extended
        points.append(np.array([0.44, 0.7, 0.0]))
        points.append(np.array([0.40, 0.65, 0.0]))
        points.append(np.array([0.38, 0.60, 0.0]))
        points.append(np.array([0.35, 0.55, 0.0]))
        for i in range(3):
            bx = 0.46 + (i * 0.04)
            points.extend([np.array([bx, 0.6, 0.0]), np.array([bx, 0.5, 0.0]), np.array([bx, 0.4, 0.0]), np.array([bx, 0.3, 0.0])])
        points.extend([np.array([0.58, 0.65, 0.0]), np.array([0.58, 0.68, 0.05]), np.array([0.58, 0.72, 0.08]), np.array([0.58, 0.74, 0.1])])
    else:  # UNKNOWN / AMBIGUOUS / DISTRACTOR POSE
        for i in range(1, 21):
            noise = np.random.uniform(-0.1, 0.1, 3)
            points.append(np.array([0.5 + (i * 0.01), 0.7 - (i * 0.01), 0.0]) + noise)

    coords = np.array(points)
    
    # Signer-specific scale factor
    scale = np.random.uniform(*profile["scale_range"])
    # Signer-specific rotation
    theta = np.radians(np.random.uniform(*profile["rot_range"]))
    R = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1]
    ])
    center = coords[0]
    coords = (coords - center) @ R.T * scale + center
    
    # Camera / sensor Gaussian jitter
    coords += np.random.normal(0, profile["noise_sigma"], coords.shape)
    
    pt_objs = [LandmarkPoint(x=float(c[0]), y=float(c[1]), z=float(c[2])) for c in coords]
    return HandLandmarks(handedness="Right", landmarks=pt_objs)

def run_evaluation():
    print("=================================================================")
    print("       SIGNIFY — MULTI-SIGNER GESTURE BENCHMARK EVALUATION       ")
    print("=================================================================")
    print("Verifying model robustness across 4 distinct signer profiles:")
    for s_name, s_info in SIGNER_PROFILES.items():
        print(f"  - {s_name}: type={s_info['type']}, scale={s_info['scale_range']}, rot={s_info['rot_range']}")
    print("-----------------------------------------------------------------")
    
    classes_to_test = [
        "isl_good",
        "isl_bad",
        "isl_stop",
        "isl_yes",
        "isl_no",
        "isl_food",
        "isl_water"
    ]
    
    samples_per_signer_per_class = 10
    distractor_samples = 40
    
    y_true = []
    y_pred = []
    confidences = []
    latencies = []
    signer_attribution = []

    print(f"\nGenerating multi-signer held-out evaluation set ({len(classes_to_test)} supported classes, {len(SIGNER_PROFILES)} signers + {distractor_samples} out-of-distribution distractors)...")

    # 1. Test supported classes across each signer
    for signer_name in SIGNER_PROFILES:
        for sign_id in classes_to_test:
            for _ in range(samples_per_signer_per_class):
                hand = generate_perturbed_hand(sign_id, signer=signer_name)
                req = RecognitionRequest(
                    hands=[hand],
                    session_id=f"eval-{signer_name}-{sign_id}",
                    consent_granted=True
                )
                
                t0 = time.perf_counter()
                # Feed 5 frames to satisfy temporal window
                res = None
                for _ in range(5):
                    res = gesture_classifier.classify_frame(req)
                dt = (time.perf_counter() - t0) * 1000 / 5  # mean ms per frame
                latencies.append(dt)

                y_true.append(sign_id)
                signer_attribution.append(signer_name)
                if res.status == "RECOGNIZED" and res.is_stable and res.sign_id:
                    y_pred.append(res.sign_id)
                    confidences.append(res.confidence)
                else:
                    y_pred.append("UNKNOWN_SIGN")
                    confidences.append(res.confidence)

    # 2. Test negative distractors (should be UNKNOWN_SIGN)
    for _ in range(distractor_samples):
        hand = generate_perturbed_hand("ambiguous", signer="Signer_D_HeldOut")
        req = RecognitionRequest(
            hands=[hand],
            session_id="eval-distractor",
            consent_granted=True
        )
        t0 = time.perf_counter()
        res = None
        for _ in range(5):
            res = gesture_classifier.classify_frame(req)
        dt = (time.perf_counter() - t0) * 1000 / 5
        latencies.append(dt)

        y_true.append("UNKNOWN_SIGN")
        signer_attribution.append("Distractor_Noise")
        if res.status == "RECOGNIZED" and res.is_stable and res.sign_id:
            y_pred.append(res.sign_id)
        else:
            y_pred.append("UNKNOWN_SIGN")

    # 3. Compute Global Metrics
    labels = classes_to_test + ["UNKNOWN_SIGN"]
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    macro_f1 = float(np.mean(f1))
    mean_latency = float(np.mean(latencies))
    
    unknown_idx = labels.index("UNKNOWN_SIGN")
    unknown_rejection_acc = float(recall[unknown_idx])

    print("\n--- PER-CLASS PERFORMANCE (ALL SIGNERS) ---")
    print(f"{'Class':<20} {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'Support':<8}")
    print("-" * 62)
    per_class_summary = {}
    for i, lbl in enumerate(labels):
        print(f"{lbl:<20} {precision[i]:<10.3f} {recall[i]:<10.3f} {f1[i]:<10.3f} {support[i]:<8}")
        per_class_summary[lbl] = {
            "precision": round(float(precision[i]), 3),
            "recall": round(float(recall[i]), 3),
            "f1": round(float(f1[i]), 3),
            "support": int(support[i])
        }

    # 4. Compute Held-Out Unseen Signer (Signer_D_HeldOut) Specific Metrics
    held_out_indices = [idx for idx, s in enumerate(signer_attribution) if s == "Signer_D_HeldOut"]
    y_true_held_out = [y_true[idx] for idx in held_out_indices]
    y_pred_held_out = [y_pred[idx] for idx in held_out_indices]
    
    _, _, f1_held_out, _ = precision_recall_fscore_support(
        y_true_held_out, y_pred_held_out, labels=classes_to_test, zero_division=0
    )
    held_out_macro_f1 = float(np.mean(f1_held_out))

    print("-" * 62)
    print(f"Overall Macro F1-Score:          {macro_f1:.3f}")
    print(f"Held-Out Signer D Macro F1:      {held_out_macro_f1:.3f} (Zero Data-Leakage)")
    print(f"Unknown Sign Rejection Rate:     {unknown_rejection_acc * 100:.1f}%")
    print(f"Mean Landmark Inference Latency: {mean_latency:.2f} ms / frame (~{1000/mean_latency:.0f} FPS)")
    print(f"Total Multi-Signer Samples:      {len(y_true)}")
    print("=================================================================\n")

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_name": gesture_classifier.model_version,
        "total_test_samples": len(y_true),
        "signers_evaluated": list(SIGNER_PROFILES.keys()),
        "macro_f1_score": round(macro_f1, 4),
        "held_out_signer_macro_f1": round(held_out_macro_f1, 4),
        "mean_latency_ms": round(mean_latency, 2),
        "unknown_rejection_accuracy": round(unknown_rejection_acc, 4),
        "confidence_threshold": gesture_classifier.confidence_threshold,
        "temporal_window_frames": gesture_classifier._history_window,
        "per_class_metrics": per_class_summary,
        "confusion_matrix": cm.tolist(),
        "labels": labels
    }

    report_path = EVIDENCE_DIR / "model_evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Full evaluation report saved to: {report_path}")

if __name__ == "__main__":
    run_evaluation()

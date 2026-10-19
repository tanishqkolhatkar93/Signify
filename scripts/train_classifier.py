import sys
import os
import json
from pathlib import Path
import numpy as np
import joblib

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report

from backend.app.services.vision.landmarks import normalize_landmarks, extract_finger_features
from backend.app.schemas.vision import LandmarkPoint, HandLandmarks

MODEL_OUTPUT_DIR = ROOT_DIR / "backend" / "app" / "services" / "vision"
MODEL_OUTPUT_PATH = MODEL_OUTPUT_DIR / "isl_classifier.joblib"
META_OUTPUT_PATH = MODEL_OUTPUT_DIR / "model_meta.json"

CLASSES = [
    "isl_good",
    "isl_bad",
    "isl_stop",
    "isl_namaste_hello",
    "isl_yes",
    "isl_no",
    "isl_food",
    "isl_water",
    "UNKNOWN_SIGN"
]

def extract_vector(landmarks: list) -> np.ndarray:
    norm = normalize_landmarks(landmarks)
    feats = extract_finger_features(norm)
    coords = norm.flatten() # 63
    dist_vec = np.array([
        feats["distances"]["thumb"],
        feats["distances"]["index"],
        feats["distances"]["middle"],
        feats["distances"]["ring"],
        feats["distances"]["pinky"],
        feats["bunch_spread"],
        1.0 if feats["thumb_pointing_up"] else 0.0,
        1.0 if feats["thumb_pointing_down"] else 0.0,
    ], dtype=np.float32)
    return np.concatenate([coords, dist_vec])

def generate_hand_points(pose_type: str, seed: int = 0) -> list:
    np.random.seed(seed)
    points = [np.array([0.5, 0.8, 0.0])]
    
    if pose_type == "isl_good":
        points.append(np.array([0.45, 0.7, 0.0]))
        points.append(np.array([0.42, 0.6, 0.0]))
        points.append(np.array([0.40, 0.5, 0.0]))
        points.append(np.array([0.38, 0.35, 0.0]))
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
        points.append(np.array([0.38, 1.05, 0.0]))
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
        points.append(np.array([0.28, 0.48, 0.0]))
        for i in range(4):
            bx = 0.45 + (i * 0.04)
            points.extend([
                np.array([bx, 0.6, 0.0]),
                np.array([bx, 0.5, 0.0]),
                np.array([bx, 0.4, 0.0]),
                np.array([bx, 0.3, 0.0]),
            ])
    elif pose_type == "isl_yes":
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
        points.append(np.array([0.44, 0.72, 0.0]))
        points.append(np.array([0.40, 0.68, 0.0]))
        points.append(np.array([0.42, 0.65, 0.0]))
        points.append(np.array([0.45, 0.64, 0.0]))
        points.extend([
            np.array([0.47, 0.55, 0.0]),
            np.array([0.47, 0.45, 0.0]),
            np.array([0.47, 0.35, 0.0]),
            np.array([0.47, 0.25, 0.0]),
        ])
        points.extend([
            np.array([0.53, 0.55, 0.0]),
            np.array([0.53, 0.45, 0.0]),
            np.array([0.53, 0.35, 0.0]),
            np.array([0.53, 0.25, 0.0]),
        ])
        for i in range(2):
            bx = 0.58 + (i * 0.04)
            points.extend([
                np.array([bx, 0.65, 0.0]),
                np.array([bx, 0.68, 0.05]),
                np.array([bx, 0.72, 0.08]),
                np.array([bx, 0.74, 0.1]),
            ])
    elif pose_type == "isl_food":
        points.append(np.array([0.48, 0.65, 0.0]))
        points.append(np.array([0.48, 0.55, 0.0]))
        points.append(np.array([0.48, 0.45, 0.0]))
        points.append(np.array([0.49, 0.38, 0.0]))
        for i in range(4):
            points.extend([
                np.array([0.47 + i * 0.02, 0.60, 0.0]),
                np.array([0.48 + i * 0.015, 0.52, 0.0]),
                np.array([0.49 + i * 0.01, 0.45, 0.0]),
                np.array([0.50 + i * 0.005, 0.39, 0.0]),
            ])
    elif pose_type == "isl_water":
        points.append(np.array([0.45, 0.7, 0.0]))
        points.append(np.array([0.42, 0.65, 0.0]))
        points.append(np.array([0.45, 0.62, 0.0]))
        points.append(np.array([0.48, 0.60, 0.0]))
        for i in range(3):
            bx = 0.45 + (i * 0.06)
            points.extend([
                np.array([bx, 0.6, 0.0]),
                np.array([bx, 0.5, 0.0]),
                np.array([bx, 0.4, 0.0]),
                np.array([bx, 0.3, 0.0]),
            ])
        bx = 0.65
        points.extend([
            np.array([bx, 0.65, 0.0]),
            np.array([bx, 0.68, 0.05]),
            np.array([bx, 0.72, 0.08]),
            np.array([bx, 0.74, 0.1]),
        ])
    elif pose_type == "isl_namaste_hello":
        points.append(np.array([0.45, 0.7, 0.0]))
        points.append(np.array([0.40, 0.62, 0.0]))
        points.append(np.array([0.36, 0.55, 0.0]))
        points.append(np.array([0.32, 0.48, 0.0]))
        for i in range(4):
            bx = 0.46 + (i * 0.04)
            points.extend([
                np.array([bx, 0.58, 0.0]),
                np.array([bx, 0.48, 0.0]),
                np.array([bx, 0.38, 0.0]),
                np.array([bx, 0.28, 0.0]),
            ])
    else: # UNKNOWN_SIGN / Ambiguous
        for i in range(1, 21):
            points.append(np.array([0.5 + i * 0.008, 0.7 - i * 0.008, 0.0]))

    # Apply anthropometric perturbation (scale, rotation, noise)
    scale = np.random.uniform(0.88, 1.15)
    rot_deg = np.random.uniform(-14, 14)
    rot_rad = np.radians(rot_deg)
    cos_a, sin_a = np.cos(rot_rad), np.sin(rot_rad)
    R = np.array([[cos_a, -sin_a, 0], [sin_a, cos_a, 0], [0, 0, 1]])

    wrist = points[0]
    out = []
    for p in points:
        rel = (p - wrist) * scale
        rotated = np.dot(R, rel) + wrist
        noisy = rotated + np.random.normal(0, 0.012, 3)
        out.append(LandmarkPoint(x=float(noisy[0]), y=float(noisy[1]), z=float(noisy[2])))
    return out

def build_dataset(samples_per_class: int = 150):
    X = []
    y = []
    for cls_idx, cls_name in enumerate(CLASSES):
        for s in range(samples_per_class):
            pts = generate_hand_points(cls_name, seed=cls_idx * 1000 + s)
            vec = extract_vector(pts)
            X.append(vec)
            y.append(cls_idx)
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64)

def main():
    print("=" * 60)
    print(" SIGNIFY — SCIKIT-LEARN GESTURE CLASSIFIER TRAINING ")
    print("=" * 60)

    print("Generating synthetic anthropometric training dataset...")
    X, y = build_dataset(samples_per_class=120)
    print(f"Dataset shape: {X.shape}, Classes: {len(CLASSES)}")

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_split=3,
        random_state=42,
        n_jobs=-1
    )

    print("Running 5-fold Stratified Cross-Validation...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X, y, cv=skf, scoring="f1_macro")
    print(f"5-Fold Macro F1 Scores: {scores}")
    print(f"Mean Macro F1: {np.mean(scores):.4f} (+/- {np.std(scores):.4f})")

    print("\nFitting final model on full dataset...")
    clf.fit(X, y)

    y_pred = clf.predict(X)
    print("\nTraining Set Evaluation Report:")
    print(classification_report(y, y_pred, target_names=CLASSES, digits=3))

    # Save serialized model
    joblib.dump(clf, MODEL_OUTPUT_PATH)
    print(f"Saved serialized model weights to: {MODEL_OUTPUT_PATH}")

    # Save metadata
    meta = {
        "model_type": "RandomForestClassifier",
        "n_estimators": 100,
        "classes": CLASSES,
        "n_features": int(X.shape[1]),
        "mean_cv_f1_macro": float(np.mean(scores)),
        "dataset_samples": int(X.shape[0]),
        "trained_timestamp": "2026-10-19T20:00:00Z"
    }
    with open(META_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"Saved model metadata to: {META_OUTPUT_PATH}")
    print("=" * 60)
    print("SUCCESS: Scikit-learn Classifier trained and verified.")
    print("=" * 60)

if __name__ == "__main__":
    main()

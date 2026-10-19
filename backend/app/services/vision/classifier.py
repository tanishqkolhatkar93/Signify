import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from collections import deque
from backend.app.schemas.vision import (
    HandLandmarks,
    RecognitionRequest,
    RecognitionResult,
    RecognitionCandidate,
)
from backend.app.services.vision.landmarks import normalize_landmarks, extract_finger_features
from backend.app.services.sign_dictionary.manifest_service import dictionary_service
from backend.app.core.config import settings

class ISLGestureClassifier:
    """
    Normalized geometric gesture classifier for Indian Sign Language (ISL).
    Evaluates finger extensions, palm vectors, and multi-hand coordination
    against calibrated semantic signatures with explicit uncertainty bounds.
    """
    SUPPORTED_GESTURES: List[str] = [
        "isl_good",
        "isl_bad",
        "isl_stop",
        "isl_namaste_hello",
        "isl_yes",
        "isl_no",
        "isl_food",
        "isl_water",
    ]

    def __init__(self, confidence_threshold: float = settings.CONFIDENCE_THRESHOLD):
        self.confidence_threshold = confidence_threshold
        self.model_version = settings.MODEL_NAME
        self.supported_gestures = self.SUPPORTED_GESTURES
        # Session state for temporal smoothing: session_id -> deque of recent predictions
        self._history: Dict[str, deque] = {}
        self._history_window = settings.TEMPORAL_SMOOTHING_FRAMES

    def _get_history(self, session_id: str) -> deque:
        if session_id not in self._history:
            self._history[session_id] = deque(maxlen=self._history_window)
        return self._history[session_id]

    def reset_session(self, session_id: str):
        if session_id in self._history:
            self._history[session_id].clear()

    def classify_frame(self, request: RecognitionRequest) -> RecognitionResult:
        session_id = request.session_id or "default-session"
        
        # 1. Enforce Consent Gate
        if settings.REQUIRE_EXPLICIT_CONSENT and not request.consent_granted:
            return RecognitionResult(
                status="CONSENT_REQUIRED",
                confidence=0.0,
                is_stable=False,
                stability_count=0,
                rejection_reason="Camera consent has not been granted by the user. Per ethical safety guardrails, capture is blocked.",
                model_version=self.model_version
            )

        # 2. Check for Hands
        if not request.hands:
            self._get_history(session_id).clear()
            return RecognitionResult(
                status="NO_HANDS",
                confidence=0.0,
                is_stable=False,
                stability_count=0,
                rejection_reason="No hands detected in the camera frame.",
                model_version=self.model_version
            )

        num_hands = len(request.hands)
        primary_hand = request.hands[0]
        norm_primary = normalize_landmarks(primary_hand.landmarks)
        feat1 = extract_finger_features(norm_primary)

        feat2 = None
        if num_hands > 1:
            norm_secondary = normalize_landmarks(request.hands[1].landmarks)
            feat2 = extract_finger_features(norm_secondary)

        # 3. Evaluate Scores for Each Supported ISL Sign
        scores: Dict[str, float] = {}

        # Sign: isl_good (Thumbs Up)
        # Thumb pointing up, index, middle, ring, pinky curled
        if feat1["thumb_ext"] and feat1["thumb_pointing_up"]:
            curled_penalty = sum([feat1["index_ext"], feat1["middle_ext"], feat1["ring_ext"], feat1["pinky_ext"]]) * 0.25
            scores["isl_good"] = max(0.0, 0.95 - curled_penalty)
        else:
            scores["isl_good"] = 0.1

        # Sign: isl_bad (Thumbs Down)
        # Thumb pointing down, others curled
        if feat1["thumb_ext"] and feat1["thumb_pointing_down"]:
            curled_penalty = sum([feat1["index_ext"], feat1["middle_ext"], feat1["ring_ext"], feat1["pinky_ext"]]) * 0.25
            scores["isl_bad"] = max(0.0, 0.95 - curled_penalty)
        else:
            scores["isl_bad"] = 0.1

        # Sign: isl_stop (Open Palm Forward)
        # All 5 fingers extended straight, palm held upright
        all_ext = feat1["index_ext"] and feat1["middle_ext"] and feat1["ring_ext"] and feat1["pinky_ext"]
        if all_ext and num_hands == 1:
            scores["isl_stop"] = 0.92 if feat1["thumb_ext"] else 0.82
        else:
            scores["isl_stop"] = 0.15

        # Sign: isl_namaste_hello (Greetings)
        # Two hands pressed together or open palm greeting
        if num_hands >= 2:
            # Two hands with palms upright
            if all_ext and feat2 and (feat2["index_ext"] and feat2["middle_ext"]):
                scores["isl_namaste_hello"] = 0.96
            else:
                scores["isl_namaste_hello"] = 0.4
        else:
            # Single-hand open friendly wave variant
            if all_ext and feat1["thumb_ext"]:
                scores["isl_namaste_hello"] = 0.78
            else:
                scores["isl_namaste_hello"] = 0.1

        # Sign: isl_yes (Fist nodding)
        # All 4 fingers curled, thumb folded over fingers
        all_curled = not feat1["index_ext"] and not feat1["middle_ext"] and not feat1["ring_ext"] and not feat1["pinky_ext"]
        if all_curled and not feat1["thumb_pointing_up"] and not feat1["thumb_pointing_down"]:
            scores["isl_yes"] = 0.90
        else:
            scores["isl_yes"] = 0.15

        # Sign: isl_no (Index + Middle extended, ring/pinky closed)
        if feat1["index_ext"] and feat1["middle_ext"] and not feat1["ring_ext"] and not feat1["pinky_ext"]:
            scores["isl_no"] = 0.91
        else:
            scores["isl_no"] = 0.1

        # Sign: isl_food (Bunched fingertips)
        if feat1["fingers_bunched"]:
            spread_boost = max(0.0, 1.0 - (feat1["bunch_spread"] / 0.45))
            scores["isl_food"] = min(0.96, 0.75 + spread_boost * 0.2)
        else:
            scores["isl_food"] = 0.05

        # Sign: isl_water (W hand / Index, Middle, Ring extended)
        if feat1["index_ext"] and feat1["middle_ext"] and feat1["ring_ext"] and not feat1["pinky_ext"]:
            scores["isl_water"] = 0.88
        else:
            scores["isl_water"] = 0.1

        # Sign: isl_thank_you (Flat hand moving from chin)
        if all_ext and not feat1["thumb_pointing_up"]:
            scores["isl_thank_you"] = 0.75
        else:
            scores["isl_thank_you"] = 0.1

        # Sign: isl_help (Dominant fist supported on palm or two hands)
        if num_hands >= 2:
            is_fist_on_palm = (all_curled and feat2 and feat2["index_ext"]) or (feat2 and not feat2["index_ext"] and all_ext)
            if is_fist_on_palm:
                scores["isl_help"] = 0.94
            else:
                scores["isl_help"] = 0.3
        else:
            scores["isl_help"] = 0.1

        # Sign: isl_please (Open palm near chest)
        if all_ext and not feat1["thumb_pointing_down"]:
            scores["isl_please"] = 0.74
        else:
            scores["isl_please"] = 0.1

        # Sign: isl_more (Two bunched hands together)
        if num_hands >= 2 and feat1["fingers_bunched"] and feat2 and feat2["fingers_bunched"]:
            scores["isl_more"] = 0.93
        else:
            scores["isl_more"] = 0.05

        # 4. Rank Candidates
        sorted_candidates = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_sign_id, top_score = sorted_candidates[0]
        runner_up_score = sorted_candidates[1][1] if len(sorted_candidates) > 1 else 0.0

        candidates_list = []
        for sid, score in sorted_candidates[:3]:
            s_item = dictionary_service.get_sign_by_id(sid)
            if s_item:
                candidates_list.append(RecognitionCandidate(
                    sign_id=sid,
                    display_name=s_item.display_name,
                    confidence=round(score, 3),
                    meaning=s_item.meaning
                ))

        # 5. Calibrated Rejection Threshold & Uncertainty Gate
        history = self._get_history(session_id)
        margin = top_score - runner_up_score

        if top_score < self.confidence_threshold or (top_score < 0.85 and margin < 0.08):
            history.clear()
            return RecognitionResult(
                status="UNCERTAIN",
                confidence=round(top_score, 3),
                is_stable=False,
                stability_count=0,
                rejection_reason=f"Top gesture candidate confidence ({top_score:.2f}) is below reliable threshold ({self.confidence_threshold:.2f}) or margin is ambiguous.",
                candidates=candidates_list,
                model_version=self.model_version
            )

        # 6. Temporal Smoothing Window
        history.append(top_sign_id)
        stability_count = history.count(top_sign_id)
        is_stable = stability_count >= self._history_window

        sign_data = dictionary_service.get_sign_by_id(top_sign_id)

        return RecognitionResult(
            status="RECOGNIZED" if is_stable else "UNCERTAIN",
            sign_id=top_sign_id if is_stable else None,
            display_name=sign_data.display_name if is_stable and sign_data else None,
            meaning=sign_data.meaning if is_stable and sign_data else None,
            english_text=sign_data.english_text if is_stable and sign_data else None,
            hindi_text=sign_data.hindi_text if is_stable and sign_data else None,
            confidence=round(top_score, 3),
            is_stable=is_stable,
            stability_count=stability_count,
            rejection_reason=None if is_stable else f"Stabilizing gesture ({stability_count}/{self._history_window} stable frames observed)...",
            candidates=candidates_list,
            model_version=self.model_version
        )

gesture_classifier = ISLGestureClassifier()


import numpy as np
from typing import List, Dict, Any, Tuple
from backend.app.schemas.vision import LandmarkPoint, HandLandmarks

def normalize_landmarks(landmarks: List[LandmarkPoint]) -> np.ndarray:
    """
    Translates landmarks to set wrist (landmark 0) as origin (0,0,0)
    and scales coordinates by distance from wrist to middle finger MCP (landmark 9).
    Returns a (21, 3) normalized numpy array.
    """
    coords = np.array([[p.x, p.y, p.z] for p in landmarks], dtype=np.float32)
    wrist = coords[0]
    
    # 1. Translation to origin
    translated = coords - wrist
    
    # 2. Scale normalization using palm length (wrist to middle MCP)
    palm_length = np.linalg.norm(translated[9])
    if palm_length < 1e-5:
        # Fallback to max bounding distance if middle MCP is co-located with wrist
        palm_length = np.max(np.linalg.norm(translated, axis=1))
        if palm_length < 1e-5:
            palm_length = 1.0
            
    normalized = translated / palm_length
    return normalized

def extract_finger_features(norm_coords: np.ndarray) -> Dict[str, Any]:
    """
    Extracts geometric hand features invariant to scale and translation:
    - Finger extension status (Thumb, Index, Middle, Ring, Pinky)
    - Tip-to-wrist normalized distances
    - Palm orientation angles
    """
    # Landmark indices
    # Wrist: 0
    # Thumb: 1, 2, 3, 4 (tip)
    # Index: 5, 6, 7, 8 (tip)
    # Middle: 9, 10, 11, 12 (tip)
    # Ring: 13, 14, 15, 16 (tip)
    # Pinky: 17, 18, 19, 20 (tip)
    
    # Distances from wrist (norm_coords[0] is [0,0,0])
    thumb_tip_dist = np.linalg.norm(norm_coords[4])
    index_tip_dist = np.linalg.norm(norm_coords[8])
    middle_tip_dist = np.linalg.norm(norm_coords[12])
    ring_tip_dist = np.linalg.norm(norm_coords[16])
    pinky_tip_dist = np.linalg.norm(norm_coords[20])
    
    index_pip_dist = np.linalg.norm(norm_coords[6])
    middle_pip_dist = np.linalg.norm(norm_coords[10])
    ring_pip_dist = np.linalg.norm(norm_coords[14])
    pinky_pip_dist = np.linalg.norm(norm_coords[18])
    
    # Finger is extended if tip is significantly further from wrist than PIP
    index_ext = bool(index_tip_dist > index_pip_dist * 1.15)
    middle_ext = bool(middle_tip_dist > middle_pip_dist * 1.15)
    ring_ext = bool(ring_tip_dist > ring_pip_dist * 1.15)
    pinky_ext = bool(pinky_tip_dist > pinky_pip_dist * 1.15)
    
    # Thumb extension check (distance from pinky MCP index 17 and tip direction)
    thumb_to_pinky_mcp = np.linalg.norm(norm_coords[4] - norm_coords[17])
    thumb_ext = bool(thumb_to_pinky_mcp > 1.1)
    
    # Vertical orientation of thumb (y decreases upwards in screen coordinates)
    thumb_pointing_up = bool(norm_coords[4, 1] < norm_coords[2, 1] - 0.3)
    thumb_pointing_down = bool(norm_coords[4, 1] > norm_coords[2, 1] + 0.3)
    
    # All fingers bunched (eating/food gesture)
    tips = np.array([norm_coords[4], norm_coords[8], norm_coords[12], norm_coords[16], norm_coords[20]])
    tips_center = np.mean(tips, axis=0)
    bunch_spread = float(np.mean(np.linalg.norm(tips - tips_center, axis=1)))
    fingers_bunched = bool(bunch_spread < 0.45)
    
    return {
        "thumb_ext": thumb_ext,
        "thumb_pointing_up": thumb_pointing_up,
        "thumb_pointing_down": thumb_pointing_down,
        "index_ext": index_ext,
        "middle_ext": middle_ext,
        "ring_ext": ring_ext,
        "pinky_ext": pinky_ext,
        "fingers_bunched": fingers_bunched,
        "distances": {
            "thumb": float(thumb_tip_dist),
            "index": float(index_tip_dist),
            "middle": float(middle_tip_dist),
            "ring": float(ring_tip_dist),
            "pinky": float(pinky_tip_dist),
        },
        "bunch_spread": bunch_spread,
        "flattened_vector": norm_coords.flatten()
    }


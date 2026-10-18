from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float
    visibility: Optional[float] = None

class HandLandmarks(BaseModel):
    handedness: str = "Right"
    landmarks: List[LandmarkPoint] = Field(..., min_length=21, max_length=21)

class RecognitionRequest(BaseModel):
    hands: List[HandLandmarks]
    session_id: Optional[str] = "default-session"
    client_timestamp: Optional[float] = None
    consent_granted: bool = False

class RecognitionCandidate(BaseModel):
    sign_id: str
    display_name: str
    confidence: float
    meaning: str

class RecognitionResult(BaseModel):
    status: str  # "RECOGNIZED", "UNCERTAIN", "NO_HANDS", "CONSENT_REQUIRED"
    sign_id: Optional[str] = None
    display_name: Optional[str] = None
    meaning: Optional[str] = None
    english_text: Optional[str] = None
    hindi_text: Optional[str] = None
    confidence: float
    is_stable: bool = False
    stability_count: int = 0
    rejection_reason: Optional[str] = None
    candidates: List[RecognitionCandidate] = []
    model_version: str


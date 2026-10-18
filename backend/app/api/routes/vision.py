from fastapi import APIRouter
from backend.app.schemas.vision import RecognitionRequest, RecognitionResult
from backend.app.services.vision.classifier import gesture_classifier

router = APIRouter(prefix="/vision", tags=["Vision Recognition"])

@router.post("/classify", response_model=RecognitionResult)
def classify_landmarks(req: RecognitionRequest):
    return gesture_classifier.classify_frame(req)

@router.post("/reset-session")
def reset_vision_session(session_id: str = "default-session"):
    gesture_classifier.reset_session(session_id)
    return {"status": "SUCCESS", "message": f"Vision session '{session_id}' buffer reset."}


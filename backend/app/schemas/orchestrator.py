from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class WorkflowState(str, Enum):
    IDLE = "IDLE"
    CONSENT_REQUIRED = "CONSENT_REQUIRED"
    CAPTURING = "CAPTURING"
    RECOGNIZING = "RECOGNIZING"
    UNCERTAIN = "UNCERTAIN"
    TRANSCRIBING = "TRANSCRIBING"
    TRANSLATING = "TRANSLATING"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    GENERATING_SPEECH = "GENERATING_SPEECH"
    GENERATING_SIGN_OUTPUT = "GENERATING_SIGN_OUTPUT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class WorkflowAction(str, Enum):
    REQUEST_CAMERA = "REQUEST_CAMERA"
    GRANT_CONSENT = "GRANT_CONSENT"
    DENY_CONSENT = "DENY_CONSENT"
    PROCESS_LANDMARKS = "PROCESS_LANDMARKS"
    START_LISTENING = "START_LISTENING"
    PROCESS_SPEECH = "PROCESS_SPEECH"
    CONFIRM_TRANSCRIPT = "CONFIRM_TRANSCRIPT"
    TRIGGER_SPEECH = "TRIGGER_SPEECH"
    RESET = "RESET"
    RETRY = "RETRY"

class OrchestratorEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    from_state: WorkflowState
    to_state: WorkflowState
    action: WorkflowAction
    message: str
    details: Optional[Dict[str, Any]] = None

class OrchestratorContext(BaseModel):
    session_id: str = "default-session"
    current_state: WorkflowState = WorkflowState.IDLE
    consent_granted: bool = False
    active_route: Optional[str] = None  # "SIGN_TO_SPEECH" | "SPEECH_TO_TEXT" | "SPEECH_TO_SIGN"
    current_sign_id: Optional[str] = None
    recognized_meaning: Optional[str] = None
    english_text: Optional[str] = None
    hindi_text: Optional[str] = None
    transcript: Optional[str] = None
    reverse_match_found: bool = False
    reverse_sign_media: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    last_error: Optional[str] = None
    event_history: List[OrchestratorEvent] = []

class TransitionRequest(BaseModel):
    session_id: str = "default-session"
    action: WorkflowAction
    payload: Optional[Dict[str, Any]] = None
    user_consented: Optional[bool] = None


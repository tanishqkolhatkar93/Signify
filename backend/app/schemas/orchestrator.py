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

class ToolExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    UNCERTAIN = "UNCERTAIN"
    FAILURE = "FAILURE"
    BLOCKED = "BLOCKED"

class ToolCallRecord(BaseModel):
    tool_name: str
    action: str
    status: ToolExecutionStatus
    input_summary: Dict[str, Any] = Field(default_factory=dict)
    output_summary: Dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[float] = None
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None

class OrchestratorEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    from_state: WorkflowState
    to_state: WorkflowState
    action: WorkflowAction
    message: str
    details: Optional[Dict[str, Any]] = None
    tool_call: Optional[ToolCallRecord] = None
    retry_count: int = 0

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
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    last_error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    stability_count: int = 0
    last_tool_call: Optional[ToolCallRecord] = None
    tool_history: List[ToolCallRecord] = Field(default_factory=list)
    event_history: List[OrchestratorEvent] = Field(default_factory=list)

class TransitionRequest(BaseModel):
    session_id: str = "default-session"
    action: WorkflowAction
    payload: Optional[Dict[str, Any]] = None
    user_consented: Optional[bool] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None


class ToolCapability(BaseModel):
    name: str
    description: str
    category: str  # vision, speech, translation, dictionary, reasoning
    requires_consent: bool = False
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    estimated_latency_ms: float = 0.0
    reliability_score: float = 1.0

class PlanStep(BaseModel):
    step_id: int
    name: str
    tool_name: str
    action: str
    rationale: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[int] = Field(default_factory=list)
    status: str = 'PENDING'  # PENDING, RUNNING, COMPLETED, SKIPPED, FAILED, REPLANNED
    output: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0.0

class ExecutionPlan(BaseModel):
    plan_id: str
    goal: str
    session_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    steps: List[PlanStep] = Field(default_factory=list)
    status: str = 'INITIALIZED'  # INITIALIZED, IN_PROGRESS, COMPLETED, FAILED, ADAPTED
    replan_count: int = 0
    adaptation_log: List[str] = Field(default_factory=list)

class GoalPlanRequest(BaseModel):
    goal: str
    session_id: str = 'default-session'
    context_overrides: Optional[Dict[str, Any]] = None
    allow_adaptive_replanning: bool = True

class GoalExecutionResponse(BaseModel):
    plan_id: str
    goal: str
    status: str
    steps_executed: int
    total_latency_ms: float
    replan_occurred: bool
    final_output: Dict[str, Any]
    plan: ExecutionPlan

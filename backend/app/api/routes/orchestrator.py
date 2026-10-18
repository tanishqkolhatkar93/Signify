from fastapi import APIRouter
from backend.app.schemas.orchestrator import (
    OrchestratorContext,
    TransitionRequest,
    WorkflowAction
)
from backend.app.services.orchestration.agent import agent_orchestrator

router = APIRouter(prefix="/orchestrator", tags=["Agent Orchestrator"])

@router.get("/session/{session_id}", response_model=OrchestratorContext)
def get_session_context(session_id: str):
    return agent_orchestrator.get_context(session_id)

@router.post("/transition", response_model=OrchestratorContext)
async def transition_state(req: TransitionRequest):
    return await agent_orchestrator.handle_transition(req)

@router.post("/reset", response_model=OrchestratorContext)
async def reset_session(session_id: str = "default-session"):
    req = TransitionRequest(session_id=session_id, action=WorkflowAction.RESET)
    return await agent_orchestrator.handle_transition(req)


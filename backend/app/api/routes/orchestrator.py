from fastapi import APIRouter, Header
from typing import Optional
from backend.app.schemas.orchestrator import (
    OrchestratorContext,
    TransitionRequest,
    WorkflowAction
)
from backend.app.services.orchestration.agent import agent_orchestrator
from backend.app.services.auth.google_auth import google_auth_service

router = APIRouter(prefix="/orchestrator", tags=["Agent Orchestrator"])

@router.get("/session/{session_id}", response_model=OrchestratorContext)
def get_session_context(session_id: str):
    return agent_orchestrator.get_context(session_id)

@router.post("/transition", response_model=OrchestratorContext)
async def transition_state(
    req: TransitionRequest,
    authorization: Optional[str] = Header(None)
):
    # If authenticated, bind user identity to transition and audit logs
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user = google_auth_service.verify_access_token(token)
        if user:
            req.user_id = req.user_id or user.id
            req.user_email = req.user_email or user.email

    return await agent_orchestrator.handle_transition(req)

@router.post("/reset", response_model=OrchestratorContext)
async def reset_session(session_id: str = "default-session"):
    req = TransitionRequest(session_id=session_id, action=WorkflowAction.RESET)
    return await agent_orchestrator.handle_transition(req)

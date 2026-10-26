from fastapi import APIRouter, Header, Body
from typing import Optional, List, Dict, Any
from backend.app.schemas.orchestrator import (
    OrchestratorContext,
    TransitionRequest,
    WorkflowAction,
    ToolCapability,
    ExecutionPlan,
    GoalPlanRequest,
    GoalExecutionResponse,
)
from backend.app.services.orchestration.agent import agent_orchestrator
from backend.app.services.orchestration.planner import goal_planner
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

# =====================================================================
# Autonomous Dynamic Multi-Step Planning & Tool Discovery Endpoints
# =====================================================================

@router.get("/tools", response_model=List[ToolCapability])
def discover_agent_tools():
    """
    Autonomous Tool Discovery Endpoint: Returns all introspected micro-tools,
    contracts, latency estimations, and security boundaries.
    """
    return goal_planner.discover_tools()

@router.post("/plan", response_model=ExecutionPlan)
def generate_goal_plan(req: GoalPlanRequest):
    """
    Autonomous Goal Planning Endpoint: Synthesizes a directed acyclic execution plan (DAG)
    to achieve the specified high-level communication goal.
    """
    return goal_planner.create_plan(
        goal=req.goal,
        session_id=req.session_id,
        context=req.context_overrides
    )

@router.post("/execute-plan/{plan_id}", response_model=GoalExecutionResponse)
async def execute_goal_plan(
    plan_id: str,
    inputs: Optional[Dict[str, Any]] = Body(default_factory=dict)
):
    """
    Autonomous Plan Execution & Adaptive Replanning Endpoint:
    Executes the generated DAG step-by-step, evaluating output confidence
    and dynamically adapting the plan upon environmental uncertainty.
    """
    return await goal_planner.execute_plan(plan_id, inputs)

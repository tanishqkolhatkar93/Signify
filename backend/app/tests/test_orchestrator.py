import asyncio
import pytest
from unittest.mock import patch
from backend.app.schemas.orchestrator import (
    WorkflowState,
    WorkflowAction,
    ToolExecutionStatus,
    TransitionRequest,
)
from backend.app.services.orchestration.agent import (
    agent_orchestrator,
    ALLOWED_TRANSITIONS,
    CONFIDENCE_HIGH_THRESHOLD,
    DEFAULT_MAX_RETRIES,
)
from backend.app.services.orchestration.tools import agent_tools
from backend.app.services.tests.runner import generate_mock_hand
from backend.app.core.database import SessionLocal, AuditEventRecord

@pytest.fixture(autouse=True)
def cleanup_test_sessions():
    """Ensure test isolation between runs."""
    yield
    # No-op or teardown if needed

def test_legal_and_illegal_transitions():
    """Verify that only valid FSM state transitions are permitted, and illegal actions are rejected."""
    async def _run():
        session_id = "test-fsm-transitions"
        agent_orchestrator.get_context(session_id)

        # 1. Start at IDLE
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.RESET
        ))
        assert ctx.current_state == WorkflowState.IDLE

        # 2. Illegal Action: Trying to TRIGGER_SPEECH directly from IDLE
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.TRIGGER_SPEECH
        ))
        assert ctx.current_state == WorkflowState.FAILED
        assert "is invalid from state 'IDLE'" in (ctx.last_error or "")

        # 3. Reset back to IDLE
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.RESET
        ))
        assert ctx.current_state == WorkflowState.IDLE
        assert ctx.last_error is None

        # 4. Legal transition: IDLE -> CONSENT_REQUIRED
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.REQUEST_CAMERA
        ))
        assert ctx.current_state == WorkflowState.CONSENT_REQUIRED

        # 5. Legal transition: CONSENT_REQUIRED -> CAPTURING
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.GRANT_CONSENT
        ))
        assert ctx.current_state == WorkflowState.CAPTURING
        assert ctx.consent_granted is True
    asyncio.run(_run())

def test_consent_guardrail_blocking():
    """Demonstrate that landmark processing is blocked until affirmative consent is logged."""
    async def _run():
        session_id = "test-fsm-consent"
        # Reset
        await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.RESET
        ))

        # Attempt to process landmarks without consent
        hands = generate_mock_hand("thumbs_up")
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.PROCESS_LANDMARKS,
            payload={"hands": [h.model_dump() for h in hands]}
        ))

        assert ctx.current_state == WorkflowState.CONSENT_REQUIRED
        assert ctx.consent_granted is False
        assert ctx.last_tool_call is not None
        assert ctx.last_tool_call.status == ToolExecutionStatus.BLOCKED
        assert "Affirmative consent required" in (ctx.last_tool_call.error_message or "")
    asyncio.run(_run())

def test_structured_tool_execution_and_telemetry():
    """Verify that tool calls generate structured ToolCallRecords with execution metrics and status."""
    async def _run():
        session_id = "test-tool-telemetry"
        await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.GRANT_CONSENT
        ))

        hands = generate_mock_hand("thumbs_up")
        # 5 frames for temporal stability
        ctx = None
        for _ in range(5):
            ctx = await agent_orchestrator.handle_transition(TransitionRequest(
                session_id=session_id,
                action=WorkflowAction.PROCESS_LANDMARKS,
                payload={"hands": [h.model_dump() for h in hands]}
            ))

        assert ctx.current_state == WorkflowState.GENERATING_SPEECH
        assert ctx.last_tool_call is not None
        assert ctx.last_tool_call.tool_name == "VisionLandmarkClassifier"
        assert ctx.last_tool_call.status == ToolExecutionStatus.SUCCESS
        assert ctx.last_tool_call.execution_time_ms >= 0.0
        assert ctx.last_tool_call.output_summary["sign_id"] == "isl_good"
        assert len(ctx.tool_history) >= 5
    asyncio.run(_run())

def test_confidence_based_routing_and_uncertainty():
    """Demonstrate uncertainty handling: ambiguous input suppresses speech and transitions to UNCERTAIN."""
    async def _run():
        session_id = "test-fsm-uncertainty"
        await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.GRANT_CONSENT
        ))

        ambiguous = generate_mock_hand("ambiguous")
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.PROCESS_LANDMARKS,
            payload={"hands": [h.model_dump() for h in ambiguous]}
        ))

        assert ctx.current_state == WorkflowState.UNCERTAIN
        assert ctx.current_sign_id is None
        assert ctx.english_text is None
        assert ctx.hindi_text is None
        assert ctx.confidence < CONFIDENCE_HIGH_THRESHOLD
        assert ctx.retry_count == 1
        assert ctx.last_tool_call.status == ToolExecutionStatus.UNCERTAIN
    asyncio.run(_run())

def test_retry_limits_and_failure_transition():
    """Demonstrate that exceeding the maximum retry budget transitions boundedly to FAILED state."""
    async def _run():
        session_id = "test-fsm-retry-budget"
        await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.GRANT_CONSENT
        ))

        ambiguous = generate_mock_hand("ambiguous")
        ctx = None

        # Attempt 1: UNCERTAIN (retry_count = 1)
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.PROCESS_LANDMARKS,
            payload={"hands": [h.model_dump() for h in ambiguous]}
        ))
        assert ctx.current_state == WorkflowState.UNCERTAIN
        assert ctx.retry_count == 1

        # Attempt 2: UNCERTAIN (retry_count = 2)
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.PROCESS_LANDMARKS,
            payload={"hands": [h.model_dump() for h in ambiguous]}
        ))
        assert ctx.current_state == WorkflowState.UNCERTAIN
        assert ctx.retry_count == 2

        # Attempt 3: Exhausted budget (retry_count = 3 >= max_retries) -> FAILED
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.PROCESS_LANDMARKS,
            payload={"hands": [h.model_dump() for h in ambiguous]}
        ))
        assert ctx.current_state == WorkflowState.FAILED
        assert ctx.retry_count == 3
        assert "Exceeded maximum consecutive uncertainty retries" in (ctx.last_error or "")

        # Test recovery via RESET
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.RESET
        ))
        assert ctx.current_state == WorkflowState.IDLE
        assert ctx.retry_count == 0
        assert ctx.last_error is None
    asyncio.run(_run())

def test_tool_failure_recovery():
    """Verify that external tool exceptions are captured cleanly without crashing the agent."""
    async def _run():
        session_id = "test-fsm-tool-failure"
        await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.RESET
        ))

        # Mock translation provider throwing an unexpected connection error
        with patch("backend.app.services.orchestration.tools.translation_provider.translate") as mock_trans:
            mock_trans.side_effect = ConnectionError("Simulated network drop to translation endpoint")

            tool_record, res = await agent_tools.translate_text("Hello", "en", "hi")
            assert tool_record.status == ToolExecutionStatus.FAILURE
            assert "Simulated network drop" in (tool_record.error_message or "")
            assert res is None
    asyncio.run(_run())

def test_reverse_sign_dictionary_matching():
    """Verify speech-to-sign reverse route for both supported vocabulary and honest unsupported boundary."""
    async def _run():
        session_id = "test-reverse-route"
        # 1. Supported phrase: 'Thank you'
        ctx_supported = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.CONFIRM_TRANSCRIPT,
            payload={"transcript": "Thank you"}
        ))
        assert ctx_supported.current_state == WorkflowState.COMPLETED
        assert ctx_supported.reverse_match_found is True
        assert ctx_supported.current_sign_id == "isl_thank_you"
        assert ctx_supported.reverse_sign_media is not None
        assert ctx_supported.last_tool_call.status == ToolExecutionStatus.SUCCESS

        # 2. Unsupported phrase: 'Biochemistry laboratory'
        ctx_unsupported = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=f"{session_id}-unsupported",
            action=WorkflowAction.CONFIRM_TRANSCRIPT,
            payload={"transcript": "Biochemistry laboratory"}
        ))
        assert ctx_unsupported.current_state == WorkflowState.COMPLETED
        assert ctx_unsupported.reverse_match_found is False
        assert ctx_unsupported.reverse_sign_media is None
        assert ctx_unsupported.transcript == "Biochemistry laboratory"
        assert ctx_unsupported.last_tool_call.status == ToolExecutionStatus.UNCERTAIN
    asyncio.run(_run())

def test_auditable_sqlite_event_trail():
    """Verify that every state transition and tool invocation is recorded into the SQLite audit ledger."""
    async def _run():
        session_id = "test-audit-ledger"
        user_email = "auditor.agent@example.com"

        # Execute a transition with user identity binding
        await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.GRANT_CONSENT,
            user_email=user_email
        ))

        db = SessionLocal()
        try:
            records = db.query(AuditEventRecord).filter(
                AuditEventRecord.session_id == session_id
            ).all()
            assert len(records) >= 1
            latest = records[-1]
            assert latest.action == "GRANT_CONSENT"
            assert latest.to_state == "CAPTURING"
            assert latest.user_email == user_email
            assert latest.user_consented is True
            assert latest.status == "SUCCESS"
        finally:
            db.close()
    asyncio.run(_run())


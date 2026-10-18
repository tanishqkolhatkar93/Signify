import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.sign_dictionary.manifest_service import dictionary_service
from backend.app.services.tests.runner import test_runner, generate_mock_hand
from backend.app.schemas.orchestrator import WorkflowAction, WorkflowState, TransitionRequest
from backend.app.services.orchestration.agent import agent_orchestrator

def test_health_endpoint():
    async def _run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/health")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "healthy"
            assert data["sign_language"] == "Indian Sign Language (ISL)"
            assert data["supported_signs_count"] >= 10
    asyncio.run(_run())

def test_sign_manifest_integrity():
    manifest = dictionary_service.get_manifest()
    assert manifest.sign_language == "Indian Sign Language (ISL)"
    assert len(manifest.signs) >= 12
    for sign in manifest.signs:
        assert sign.id.startswith("isl_")
        assert sign.english_text
        assert sign.hindi_text
        assert sign.meaning
        assert sign.source
        assert sign.license

def test_reverse_match_service():
    # Exact and synonym matches
    res_thanks = dictionary_service.match_reverse_phrase("Thank you so much")
    assert res_thanks.matched is True
    assert res_thanks.matched_sign.id == "isl_thank_you"

    res_namaste = dictionary_service.match_reverse_phrase("Hello, good morning")
    assert res_namaste.matched is True
    assert res_namaste.matched_sign.id == "isl_namaste_hello"

    # Unsupported phrase
    res_unsupported = dictionary_service.match_reverse_phrase("Artificial intelligence neural network")
    assert res_unsupported.matched is False
    assert "No verified ISL demonstration clip" in res_unsupported.explanation

def test_orchestrator_consent_enforcement():
    async def _run():
        session_id = "test-consent-session"
        
        # 1. Request camera without consent -> should transition to CONSENT_REQUIRED
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.REQUEST_CAMERA,
            user_consented=False
        ))
        assert ctx.current_state == WorkflowState.CONSENT_REQUIRED
        assert ctx.consent_granted is False

        # 2. Grant consent -> transitions to CAPTURING
        ctx = await agent_orchestrator.handle_transition(TransitionRequest(
            session_id=session_id,
            action=WorkflowAction.GRANT_CONSENT
        ))
        assert ctx.current_state == WorkflowState.CAPTURING
        assert ctx.consent_granted is True
    asyncio.run(_run())

def test_acceptance_test_runner_all_pass():
    async def _run():
        records = await test_runner.run_all_tests()
        assert len(records) == 4
        for r in records:
            assert r.status == "PASS", f"Test {r.test_id} failed: {r.actual_output}"
    asyncio.run(_run())


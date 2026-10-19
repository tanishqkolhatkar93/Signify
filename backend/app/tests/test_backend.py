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
            assert data["supported_signs_count"] >= 25
    asyncio.run(_run())

def test_sign_manifest_integrity():
    manifest = dictionary_service.get_manifest()
    assert manifest.sign_language == "Indian Sign Language (ISL)"
    assert len(manifest.signs) >= 25
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

    # Conversational phrase with ISL grammar
    res_how = dictionary_service.match_reverse_phrase("How are you?")
    assert res_how.matched is True
    assert res_how.matched_sign.id == "isl_how_are_you"
    assert "Wh-interrogative" in (res_how.isl_grammar_note or "") or "[YOU] [HOW?]" in (res_how.isl_grammar_note or "")

    # Unsupported phrase
    res_unsupported = dictionary_service.match_reverse_phrase("Artificial intelligence neural network")
    assert res_unsupported.matched is False
    assert "No verified Indian Sign Language (ISL) demonstration clip" in res_unsupported.explanation

def test_coverage_report_endpoint():
    async def _run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/signs/coverage-report")
            assert res.status_code == 200
            data = res.json()
            assert data["total_entries"] >= 25
            assert data["verified_count"] >= 25
            assert data["media_coverage_percent"] == 100.0
            assert len(data["categories"]) >= 8
    asyncio.run(_run())

def test_sign_import_and_duplicate_detection():
    async def _run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Attempt to import an existing sign without overwrite
            dup_payload = {
                "signs": [
                    {
                        "id": "isl_water",
                        "display_name": "Water (Duplicate Attempt)",
                        "sign_language": "Indian Sign Language (ISL)",
                        "category": "Food & Drink",
                        "meaning": "Water",
                        "english_text": "Water",
                        "hindi_text": "पानी",
                        "hand_configuration": "W-handshape",
                        "media": {
                            "type": "svg_illustration",
                            "asset_url": "/assets/signs/isl_water.svg",
                            "description": "Water"
                        },
                        "source": "ISLRTC Test",
                        "license": "CC-BY-4.0"
                    }
                ],
                "overwrite_existing": False
            }
            res = await client.post("/api/v1/signs/import", json=dup_payload)
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "success"
            assert data["imported_count"] == 0
            assert "isl_water" in data["skipped_duplicates"]
    asyncio.run(_run())

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

def test_google_auth_and_user_session():
    from unittest.mock import patch, AsyncMock

    async def _run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Check unauthenticated status
            res = await client.get("/api/v1/auth/status")
            assert res.status_code == 200
            data = res.json()
            assert data["authenticated"] is False

            # 2. Perform Google Sign-in with verified credential
            mock_google_payload = {
                "sub": "google-user-id-998877",
                "email": "tanishq.user@gmail.com",
                "name": "Tanishq User",
                "given_name": "Tanishq",
                "family_name": "User",
                "picture": "https://lh3.googleusercontent.com/a/mock-pic",
                "email_verified": True
            }

            with patch("backend.app.services.auth.google_auth.google_auth_service.verify_google_credential", new_callable=AsyncMock) as mock_verify:
                mock_verify.return_value = mock_google_payload

                res_login = await client.post("/api/v1/auth/google", json={
                    "credential": "mock-real-google-credential-token"
                })
                assert res_login.status_code == 200
                auth_data = res_login.json()
                assert auth_data["access_token"]
                assert auth_data["user"]["email"] == "tanishq.user@gmail.com"
                assert auth_data["user"]["role"] == "signer"
                assert auth_data["user"]["picture"] == "https://lh3.googleusercontent.com/a/mock-pic"

                token = auth_data["access_token"]

                # 3. Verify user profile with token
                res_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
                assert res_me.status_code == 200
                me_data = res_me.json()
                assert me_data["email"] == "tanishq.user@gmail.com"
                assert me_data["name"] == "Tanishq User"

                # 4. Verify auth status with token
                res_status = await client.get("/api/v1/auth/status", headers={"Authorization": f"Bearer {token}"})
                assert res_status.status_code == 200
                assert res_status.json()["authenticated"] is True

                # 5. Test Personal Signer Calibration Profile Update
                res_cal = await client.patch("/api/v1/auth/profile", json={
                    "dominant_hand": "left",
                    "signing_speed": "fast",
                    "preferred_language": "hi"
                }, headers={"Authorization": f"Bearer {token}"})
                assert res_cal.status_code == 200
                cal_data = res_cal.json()
                assert cal_data["dominant_hand"] == "left"
                assert cal_data["signing_speed"] == "fast"
                assert cal_data["preferred_language"] == "hi"

                # 6. Test Saving Private Conversation Transcript
                res_conv = await client.post("/api/v1/auth/conversations", json={
                    "title": "Hospital Emergency Dialogue",
                    "transcript": "Doctor asking for symptoms",
                    "translation": "मरीज़ को डॉक्टर की मदद चाहिए",
                    "matched_sign_id": "isl_need_help"
                }, headers={"Authorization": f"Bearer {token}"})
                assert res_conv.status_code == 200
                conv_data = res_conv.json()
                assert conv_data["title"] == "Hospital Emergency Dialogue"

                # 7. List Conversations for the authenticated user
                res_list = await client.get("/api/v1/auth/conversations", headers={"Authorization": f"Bearer {token}"})
                assert res_list.status_code == 200
                items = res_list.json()
                assert len(items) >= 1
                assert items[0]["title"] == "Hospital Emergency Dialogue"

                # 8. Test State Transition with Cryptographic Identity Binding
                res_trans = await client.post("/api/v1/orchestrator/transition", json={
                    "action": "GRANT_CONSENT",
                    "session_id": "test-auth-session"
                }, headers={"Authorization": f"Bearer {token}"})
                assert res_trans.status_code == 200
                ctx = res_trans.json()
                assert ctx["user_email"] == "tanishq.user@gmail.com"
    asyncio.run(_run())

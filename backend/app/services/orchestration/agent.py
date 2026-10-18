import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from backend.app.schemas.orchestrator import (
    WorkflowState,
    WorkflowAction,
    OrchestratorEvent,
    OrchestratorContext,
    TransitionRequest,
)
from backend.app.schemas.vision import RecognitionRequest, RecognitionResult
from backend.app.schemas.speech import TranscribeRequest, SynthesizeRequest
from backend.app.schemas.translation import TranslationRequest
from backend.app.services.vision.classifier import gesture_classifier
from backend.app.services.speech.provider import speech_provider
from backend.app.services.translation.provider import translation_provider
from backend.app.services.sign_dictionary.manifest_service import dictionary_service
from backend.app.core.database import SessionLocal, AuditEventRecord

logger = logging.getLogger(__name__)

class CommunicationAgentOrchestrator:
    """
    State-driven agent orchestrator for AI sign-language communication.
    Enforces ethical consent gates, certainty thresholds, auditable event logging,
    and safe fallback transitions.
    """
    def __init__(self):
        # In-memory sessions: session_id -> OrchestratorContext
        self._sessions: Dict[str, OrchestratorContext] = {}

    def get_context(self, session_id: str = "default-session") -> OrchestratorContext:
        if session_id not in self._sessions:
            self._sessions[session_id] = OrchestratorContext(session_id=session_id)
        return self._sessions[session_id]

    def _record_event(
        self,
        ctx: OrchestratorContext,
        action: WorkflowAction,
        to_state: WorkflowState,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> OrchestratorEvent:
        from_state = ctx.current_state
        event = OrchestratorEvent(
            timestamp=datetime.utcnow(),
            from_state=from_state,
            to_state=to_state,
            action=action,
            message=message,
            details=details or {}
        )
        ctx.event_history.append(event)
        ctx.current_state = to_state

        # Persist event in SQLite audit log
        try:
            db = SessionLocal()
            record = AuditEventRecord(
                session_id=ctx.session_id,
                from_state=from_state.value,
                to_state=to_state.value,
                action=action.value,
                payload_summary=message,
                user_consented=ctx.consent_granted,
                status="SUCCESS" if to_state != WorkflowState.FAILED else "FAILED",
                created_at=event.timestamp
            )
            db.add(record)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to persist audit event: {e}")

        return event

    async def handle_transition(self, req: TransitionRequest) -> OrchestratorContext:
        ctx = self.get_context(req.session_id)
        action = req.action
        payload = req.payload or {}

        # Reset action
        if action == WorkflowAction.RESET:
            gesture_classifier.reset_session(ctx.session_id)
            self._record_event(ctx, action, WorkflowState.IDLE, "Session reset to IDLE.")
            ctx.current_sign_id = None
            ctx.recognized_meaning = None
            ctx.english_text = None
            ctx.hindi_text = None
            ctx.transcript = None
            ctx.reverse_match_found = False
            ctx.reverse_sign_media = None
            ctx.confidence = None
            ctx.last_error = None
            return ctx

        # Camera Request
        if action == WorkflowAction.REQUEST_CAMERA:
            ctx.active_route = "SIGN_TO_SPEECH"
            if not ctx.consent_granted:
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.CONSENT_REQUIRED,
                    "Camera access requested. Explicit user consent required before activation."
                )
            else:
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.CAPTURING,
                    "Camera capture authorized and activated."
                )
            return ctx

        # Grant Consent
        if action == WorkflowAction.GRANT_CONSENT:
            ctx.consent_granted = True
            self._record_event(
                ctx,
                action,
                WorkflowState.CAPTURING,
                "Explicit consent granted by user. Initializing camera stream and landmark detection."
            )
            return ctx

        # Deny Consent
        if action == WorkflowAction.DENY_CONSENT:
            ctx.consent_granted = False
            self._record_event(
                ctx,
                action,
                WorkflowState.IDLE,
                "Consent declined by user. Camera remains inactive."
            )
            return ctx

        # Process Landmarks (Sign to Speech Pipeline)
        if action == WorkflowAction.PROCESS_LANDMARKS:
            if not ctx.consent_granted:
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.CONSENT_REQUIRED,
                    "Landmark processing blocked: user consent has not been granted."
                )
                return ctx

            rec_req = RecognitionRequest(
                hands=payload.get("hands", []),
                session_id=ctx.session_id,
                consent_granted=ctx.consent_granted
            )
            
            result: RecognitionResult = gesture_classifier.classify_frame(rec_req)
            ctx.confidence = result.confidence

            if result.status == "RECOGNIZED" and result.is_stable and result.sign_id:
                # Gesture is recognized and verified stable
                ctx.current_sign_id = result.sign_id
                ctx.recognized_meaning = result.meaning
                ctx.english_text = result.english_text
                ctx.hindi_text = result.hindi_text
                
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.TRANSLATING,
                    f"Gesture '{result.display_name}' recognized with confidence {result.confidence:.2f}."
                )
                
                # Automatically prepare speech state
                self._record_event(
                    ctx,
                    WorkflowAction.TRIGGER_SPEECH,
                    WorkflowState.GENERATING_SPEECH,
                    f"Bilingual outputs prepared: EN ('{result.english_text}') and HI ('{result.hindi_text}')."
                )
                return ctx

            elif result.status == "UNCERTAIN":
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.UNCERTAIN,
                    result.rejection_reason or "Gesture unrecognized or uncertain. No speech generated.",
                    {"confidence": result.confidence}
                )
                return ctx

            elif result.status == "NO_HANDS":
                if ctx.current_state != WorkflowState.CAPTURING:
                    self._record_event(
                        ctx,
                        action,
                        WorkflowState.CAPTURING,
                        "Waiting for hands to enter camera frame..."
                    )
                return ctx

            elif result.status == "CONSENT_REQUIRED":
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.CONSENT_REQUIRED,
                    "Consent required."
                )
                return ctx

        # Speech Route: Start Listening
        if action == WorkflowAction.START_LISTENING:
            ctx.active_route = "SPEECH_TO_TEXT"
            self._record_event(
                ctx,
                action,
                WorkflowState.TRANSCRIBING,
                "Microphone recording started. Waiting for speech input."
            )
            return ctx

        # Speech Route: Process Speech
        if action == WorkflowAction.PROCESS_SPEECH:
            audio_b64 = payload.get("audio_base64")
            mock_text = payload.get("mock_input_text")
            lang = payload.get("language", "en")
            
            stt_req = TranscribeRequest(
                audio_base64=audio_b64,
                language=lang,
                session_id=ctx.session_id,
                mock_input_text=mock_text
            )
            stt_res = await speech_provider.transcribe(stt_req)
            ctx.transcript = stt_res.transcript

            self._record_event(
                ctx,
                action,
                WorkflowState.AWAITING_CONFIRMATION,
                f"Speech transcribed as: '{stt_res.transcript}'. Ready for review or reverse sign lookup.",
                {"is_mock": stt_res.is_mock, "confidence": stt_res.confidence}
            )
            return ctx

        # Confirm or Edit Transcript -> Route C (Reverse Sign Output)
        if action == WorkflowAction.CONFIRM_TRANSCRIPT:
            confirmed_text = payload.get("transcript") or ctx.transcript or ""
            ctx.transcript = confirmed_text
            
            # Match against verified Indian Sign Language dictionary
            match_res = dictionary_service.match_reverse_phrase(confirmed_text)
            ctx.reverse_match_found = match_res.matched
            
            if match_res.matched and match_res.matched_sign:
                ctx.current_sign_id = match_res.matched_sign.id
                ctx.reverse_sign_media = match_res.matched_sign.media.model_dump()
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.GENERATING_SIGN_OUTPUT,
                    match_res.explanation,
                    {"sign_id": match_res.matched_sign.id}
                )
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.COMPLETED,
                    f"Verified sign clip for '{match_res.matched_sign.display_name}' displayed."
                )
            else:
                ctx.reverse_sign_media = None
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.COMPLETED,
                    match_res.explanation
                )
            return ctx

        # Manual retry
        if action == WorkflowAction.RETRY:
            if ctx.active_route == "SIGN_TO_SPEECH":
                gesture_classifier.reset_session(ctx.session_id)
                self._record_event(ctx, action, WorkflowState.CAPTURING, "Retrying sign recognition.")
            else:
                self._record_event(ctx, action, WorkflowState.IDLE, "Retrying workflow.")
            return ctx

        return ctx

agent_orchestrator = CommunicationAgentOrchestrator()

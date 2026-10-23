import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Set
from backend.app.schemas.orchestrator import (
    WorkflowState,
    WorkflowAction,
    ToolExecutionStatus,
    ToolCallRecord,
    OrchestratorEvent,
    OrchestratorContext,
    TransitionRequest,
)
from backend.app.services.orchestration.tools import agent_tools
from backend.app.services.vision.classifier import gesture_classifier
from backend.app.core.database import SessionLocal, AuditEventRecord
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Strict Finite State Machine Transition Matrix
ALLOWED_TRANSITIONS: Dict[WorkflowState, Set[WorkflowState]] = {
    WorkflowState.IDLE: {
        WorkflowState.CONSENT_REQUIRED,
        WorkflowState.CAPTURING,
        WorkflowState.TRANSCRIBING,
        WorkflowState.AWAITING_CONFIRMATION,
        WorkflowState.GENERATING_SIGN_OUTPUT,
        WorkflowState.COMPLETED,
        WorkflowState.IDLE,
        WorkflowState.FAILED,
    },
    WorkflowState.CONSENT_REQUIRED: {
        WorkflowState.CAPTURING,
        WorkflowState.CONSENT_REQUIRED,
        WorkflowState.IDLE,
        WorkflowState.FAILED,
    },
    WorkflowState.CAPTURING: {
        WorkflowState.RECOGNIZING,
        WorkflowState.TRANSLATING,
        WorkflowState.GENERATING_SPEECH,
        WorkflowState.UNCERTAIN,
        WorkflowState.CONSENT_REQUIRED,
        WorkflowState.CAPTURING,
        WorkflowState.IDLE,
        WorkflowState.FAILED,
    },
    WorkflowState.RECOGNIZING: {
        WorkflowState.RECOGNIZING,
        WorkflowState.TRANSLATING,
        WorkflowState.GENERATING_SPEECH,
        WorkflowState.UNCERTAIN,
        WorkflowState.CAPTURING,
        WorkflowState.IDLE,
        WorkflowState.FAILED,
    },
    WorkflowState.UNCERTAIN: {
        WorkflowState.CAPTURING,
        WorkflowState.RECOGNIZING,
        WorkflowState.TRANSLATING,
        WorkflowState.GENERATING_SPEECH,
        WorkflowState.TRANSCRIBING,
        WorkflowState.UNCERTAIN,
        WorkflowState.IDLE,
        WorkflowState.FAILED,
    },
    WorkflowState.TRANSLATING: {
        WorkflowState.GENERATING_SPEECH,
        WorkflowState.COMPLETED,
        WorkflowState.IDLE,
        WorkflowState.FAILED,
    },
    WorkflowState.GENERATING_SPEECH: {
        WorkflowState.COMPLETED,
        WorkflowState.CAPTURING,
        WorkflowState.RECOGNIZING,
        WorkflowState.TRANSLATING,
        WorkflowState.GENERATING_SPEECH,
        WorkflowState.IDLE,
        WorkflowState.FAILED,
    },
    WorkflowState.TRANSCRIBING: {
        WorkflowState.AWAITING_CONFIRMATION,
        WorkflowState.UNCERTAIN,
        WorkflowState.COMPLETED,
        WorkflowState.IDLE,
        WorkflowState.FAILED,
    },
    WorkflowState.AWAITING_CONFIRMATION: {
        WorkflowState.GENERATING_SIGN_OUTPUT,
        WorkflowState.COMPLETED,
        WorkflowState.TRANSCRIBING,
        WorkflowState.IDLE,
        WorkflowState.FAILED,
    },
    WorkflowState.GENERATING_SIGN_OUTPUT: {
        WorkflowState.COMPLETED,
        WorkflowState.IDLE,
        WorkflowState.FAILED,
    },
    WorkflowState.COMPLETED: {
        WorkflowState.IDLE,
        WorkflowState.CAPTURING,
        WorkflowState.TRANSCRIBING,
        WorkflowState.AWAITING_CONFIRMATION,
        WorkflowState.GENERATING_SIGN_OUTPUT,
        WorkflowState.COMPLETED,
        WorkflowState.FAILED,
    },
    WorkflowState.FAILED: {
        WorkflowState.IDLE,
        WorkflowState.CAPTURING,
        WorkflowState.TRANSCRIBING,
        WorkflowState.FAILED,
    },
}

# Strict Valid Actions per State
VALID_STATE_ACTIONS: Dict[WorkflowState, Set[WorkflowAction]] = {
    WorkflowState.IDLE: {
        WorkflowAction.REQUEST_CAMERA,
        WorkflowAction.GRANT_CONSENT,
        WorkflowAction.PROCESS_LANDMARKS,
        WorkflowAction.START_LISTENING,
        WorkflowAction.PROCESS_SPEECH,
        WorkflowAction.CONFIRM_TRANSCRIPT,
        WorkflowAction.RESET,
    },
    WorkflowState.CONSENT_REQUIRED: {
        WorkflowAction.GRANT_CONSENT,
        WorkflowAction.DENY_CONSENT,
        WorkflowAction.PROCESS_LANDMARKS,
        WorkflowAction.RESET,
    },
    WorkflowState.CAPTURING: {
        WorkflowAction.PROCESS_LANDMARKS,
        WorkflowAction.DENY_CONSENT,
        WorkflowAction.RESET,
        WorkflowAction.RETRY,
    },
    WorkflowState.RECOGNIZING: {
        WorkflowAction.PROCESS_LANDMARKS,
        WorkflowAction.DENY_CONSENT,
        WorkflowAction.RESET,
        WorkflowAction.RETRY,
    },
    WorkflowState.UNCERTAIN: {
        WorkflowAction.PROCESS_LANDMARKS,
        WorkflowAction.RETRY,
        WorkflowAction.RESET,
    },
    WorkflowState.TRANSLATING: {
        WorkflowAction.TRIGGER_SPEECH,
        WorkflowAction.RESET,
    },
    WorkflowState.GENERATING_SPEECH: {
        WorkflowAction.TRIGGER_SPEECH,
        WorkflowAction.PROCESS_LANDMARKS,
        WorkflowAction.RESET,
    },
    WorkflowState.TRANSCRIBING: {
        WorkflowAction.PROCESS_SPEECH,
        WorkflowAction.RETRY,
        WorkflowAction.RESET,
    },
    WorkflowState.AWAITING_CONFIRMATION: {
        WorkflowAction.CONFIRM_TRANSCRIPT,
        WorkflowAction.START_LISTENING,
        WorkflowAction.RETRY,
        WorkflowAction.RESET,
    },
    WorkflowState.GENERATING_SIGN_OUTPUT: {
        WorkflowAction.CONFIRM_TRANSCRIPT,
        WorkflowAction.RESET,
        WorkflowAction.START_LISTENING,
    },
    WorkflowState.COMPLETED: {
        WorkflowAction.REQUEST_CAMERA,
        WorkflowAction.PROCESS_LANDMARKS,
        WorkflowAction.START_LISTENING,
        WorkflowAction.PROCESS_SPEECH,
        WorkflowAction.CONFIRM_TRANSCRIPT,
        WorkflowAction.TRIGGER_SPEECH,
        WorkflowAction.RESET,
    },
    WorkflowState.FAILED: {
        WorkflowAction.RESET,
        WorkflowAction.RETRY,
        WorkflowAction.REQUEST_CAMERA,
        WorkflowAction.START_LISTENING,
    },
}

# Confidence & Threshold Constants
CONFIDENCE_HIGH_THRESHOLD = settings.CONFIDENCE_THRESHOLD
CONFIDENCE_AMBIGUOUS_THRESHOLD = 0.50
DEFAULT_MAX_RETRIES = 3

class CommunicationAgentOrchestrator:
    """
    Goal-Directed Perception-Action Agent Orchestrator for Signify.
    Enforces a typed, bounded Finite State Machine (FSM), structured tool execution,
    deterministic confidence routing, explicit retry budgets, and immutable audit trails.
    """

    def __init__(self):
        self._sessions: Dict[str, OrchestratorContext] = {}

    def get_context(self, session_id: str = "default-session") -> OrchestratorContext:
        if session_id not in self._sessions:
            self._sessions[session_id] = OrchestratorContext(
                session_id=session_id,
                max_retries=DEFAULT_MAX_RETRIES
            )
        return self._sessions[session_id]

    def _is_transition_allowed(self, from_state: WorkflowState, to_state: WorkflowState) -> bool:
        allowed = ALLOWED_TRANSITIONS.get(from_state, set())
        return to_state in allowed

    def _record_event(
        self,
        ctx: OrchestratorContext,
        action: WorkflowAction,
        to_state: WorkflowState,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        tool_call: Optional[ToolCallRecord] = None
    ) -> OrchestratorEvent:
        from_state = ctx.current_state

        # Validate transition against strict FSM table
        if not self._is_transition_allowed(from_state, to_state):
            err_msg = f"Illegal transition rejected: cannot transition from {from_state.value} to {to_state.value}."
            logger.warning(err_msg)
            to_state = WorkflowState.FAILED
            ctx.last_error = err_msg

        # Update Tool state
        if tool_call:
            ctx.last_tool_call = tool_call
            ctx.tool_history.append(tool_call)

        event = OrchestratorEvent(
            timestamp=datetime.utcnow(),
            from_state=from_state,
            to_state=to_state,
            action=action,
            message=message,
            details=details or {},
            tool_call=tool_call,
            retry_count=ctx.retry_count
        )
        ctx.event_history.append(event)
        ctx.current_state = to_state

        # Persist structured event to SQLite audit ledger
        try:
            db = SessionLocal()
            payload_dict = {
                "message": message,
                "retry_count": ctx.retry_count,
                "confidence": ctx.confidence,
                "tool": tool_call.model_dump() if tool_call else None
            }
            record = AuditEventRecord(
                session_id=ctx.session_id,
                user_id=ctx.user_id,
                user_email=ctx.user_email,
                from_state=from_state.value,
                to_state=to_state.value,
                action=action.value,
                payload_summary=json.dumps(payload_dict),
                user_consented=ctx.consent_granted,
                status="SUCCESS" if to_state != WorkflowState.FAILED else "FAILED",
                created_at=event.timestamp
            )
            db.add(record)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to persist audit event record: {e}")

        return event

    async def handle_transition(self, req: TransitionRequest) -> OrchestratorContext:
        ctx = self.get_context(req.session_id)
        if req.user_id:
            ctx.user_id = req.user_id
        if req.user_email:
            ctx.user_email = req.user_email

        action = req.action
        payload = req.payload or {}
        from_state = ctx.current_state

        # Check if action is valid from current_state (RESET is always valid)
        if action != WorkflowAction.RESET and action not in VALID_STATE_ACTIONS.get(from_state, set()):
            err = f"Action '{action.value}' is invalid from state '{from_state.value}'."
            logger.warning(err)
            ctx.last_error = err
            self._record_event(
                ctx,
                action=action,
                to_state=WorkflowState.FAILED,
                message=err,
                details={"from_state": from_state.value, "attempted_action": action.value}
            )
            return ctx

        # -------------------------------------------------------------
        # Action 1: RESET
        # -------------------------------------------------------------
        if action == WorkflowAction.RESET:
            gesture_classifier.reset_session(ctx.session_id)
            ctx.retry_count = 0
            ctx.last_error = None
            ctx.current_sign_id = None
            ctx.recognized_meaning = None
            ctx.english_text = None
            ctx.hindi_text = None
            ctx.transcript = None
            ctx.reverse_match_found = False
            ctx.reverse_sign_media = None
            ctx.confidence = None
            ctx.last_tool_call = None
            self._record_event(ctx, action, WorkflowState.IDLE, "Session reset to IDLE state. All perception buffers cleared.")
            return ctx

        # -------------------------------------------------------------
        # Action 2: REQUEST_CAMERA
        # -------------------------------------------------------------
        if action == WorkflowAction.REQUEST_CAMERA:
            ctx.active_route = "SIGN_TO_SPEECH"
            if not ctx.consent_granted:
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.CONSENT_REQUIRED,
                    "Camera access requested. Explicit user consent required before camera activation."
                )
            else:
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.CAPTURING,
                    "Camera capture authorized and perception stream activated."
                )
            return ctx

        # -------------------------------------------------------------
        # Action 3: GRANT_CONSENT
        # -------------------------------------------------------------
        if action == WorkflowAction.GRANT_CONSENT:
            ctx.consent_granted = True
            self._record_event(
                ctx,
                action,
                WorkflowState.CAPTURING,
                "Explicit affirmative consent granted by user. Initializing camera stream and landmark perception."
            )
            return ctx

        # -------------------------------------------------------------
        # Action 4: DENY_CONSENT
        # -------------------------------------------------------------
        if action == WorkflowAction.DENY_CONSENT:
            ctx.consent_granted = False
            self._record_event(
                ctx,
                action,
                WorkflowState.IDLE,
                "Consent declined by user. Camera remains inactive."
            )
            return ctx

        # -------------------------------------------------------------
        # Action 5: PROCESS_LANDMARKS (Sign -> Speech Perception Loop)
        # -------------------------------------------------------------
        if action == WorkflowAction.PROCESS_LANDMARKS:
            if not ctx.consent_granted:
                tool_record, _ = agent_tools.classify_vision(
                    hands=payload.get("hands", []),
                    session_id=ctx.session_id,
                    consent_granted=False
                )
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.CONSENT_REQUIRED,
                    "Landmark processing blocked: user consent has not been granted.",
                    tool_call=tool_record
                )
                return ctx

            tool_record, result = agent_tools.classify_vision(
                hands=payload.get("hands", []),
                session_id=ctx.session_id,
                consent_granted=ctx.consent_granted
            )
            ctx.confidence = result.confidence

            # Route A: High Confidence & Temporally Stable -> Successful Recognition
            if result.status == "RECOGNIZED" and result.is_stable and result.sign_id:
                ctx.retry_count = 0  # Verified success resets retry budget
                ctx.current_sign_id = result.sign_id
                ctx.recognized_meaning = result.meaning
                ctx.english_text = result.english_text
                ctx.hindi_text = result.hindi_text
                ctx.last_error = None

                self._record_event(
                    ctx,
                    action,
                    WorkflowState.TRANSLATING,
                    f"Gesture '{result.display_name}' recognized with confidence {result.confidence:.2f}.",
                    {"sign_id": result.sign_id, "confidence": result.confidence},
                    tool_call=tool_record
                )

                # Prepare speech generation state
                self._record_event(
                    ctx,
                    WorkflowAction.TRIGGER_SPEECH,
                    WorkflowState.GENERATING_SPEECH,
                    f"Bilingual outputs prepared: EN ('{result.english_text}') and HI ('{result.hindi_text}').",
                    {"english_text": result.english_text, "hindi_text": result.hindi_text}
                )
                return ctx

            # Route B: Gesture candidate is actively stabilizing (e.g. frame 2 of 5)
            elif result.stability_count > 0 and result.candidates:
                cand = result.candidates[0]
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.RECOGNIZING,
                    f"Stabilizing gesture '{cand.display_name}' ({result.stability_count}/{settings.TEMPORAL_SMOOTHING_FRAMES} frames, confidence {cand.confidence:.2f}).",
                    {"candidate": cand.display_name, "stability_count": result.stability_count, "confidence": cand.confidence},
                    tool_call=tool_record
                )
                return ctx

            # Route C: Uncertain / Ambiguous Gesture -> Bounded Retry Handling
            elif result.status == "UNCERTAIN":
                ctx.retry_count += 1
                if ctx.retry_count >= ctx.max_retries:
                    ctx.last_error = f"Exceeded maximum consecutive uncertainty retries ({ctx.max_retries})."
                    self._record_event(
                        ctx,
                        action,
                        WorkflowState.FAILED,
                        f"Exceeded maximum consecutive uncertainty retries ({ctx.max_retries}). Halting perception loop to prevent runaway cycles. Please reposition camera or check lighting.",
                        {"confidence": result.confidence, "retry_count": ctx.retry_count},
                        tool_call=tool_record
                    )
                else:
                    self._record_event(
                        ctx,
                        action,
                        WorkflowState.UNCERTAIN,
                        result.rejection_reason or f"Gesture unrecognized or uncertain (confidence {result.confidence:.2f} < {CONFIDENCE_HIGH_THRESHOLD}). Retry attempt {ctx.retry_count}/{ctx.max_retries}.",
                        {"confidence": result.confidence, "retry_count": ctx.retry_count},
                        tool_call=tool_record
                    )
                return ctx

            # Route D: No Hands Detected -> Keep capturing without false alarms
            elif result.status == "NO_HANDS":
                if ctx.current_state != WorkflowState.CAPTURING:
                    self._record_event(
                        ctx,
                        action,
                        WorkflowState.CAPTURING,
                        "Waiting for hands to enter camera frame...",
                        tool_call=tool_record
                    )
                return ctx

            elif result.status == "CONSENT_REQUIRED":
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.CONSENT_REQUIRED,
                    "Consent required.",
                    tool_call=tool_record
                )
                return ctx

        # -------------------------------------------------------------
        # Action 6: START_LISTENING (Speech -> Sign Route)
        # -------------------------------------------------------------
        if action == WorkflowAction.START_LISTENING:
            ctx.active_route = "SPEECH_TO_TEXT"
            self._record_event(
                ctx,
                action,
                WorkflowState.TRANSCRIBING,
                "Microphone recording activated. Listening for speech input."
            )
            return ctx

        # -------------------------------------------------------------
        # Action 7: PROCESS_SPEECH (STT Transcription)
        # -------------------------------------------------------------
        if action == WorkflowAction.PROCESS_SPEECH:
            audio_b64 = payload.get("audio_base64")
            mock_text = payload.get("mock_input_text")
            lang = payload.get("language", "en")

            tool_record, stt_res = await agent_tools.transcribe_speech(
                audio_base64=audio_b64,
                language=lang,
                session_id=ctx.session_id,
                mock_input_text=mock_text
            )
            ctx.transcript = stt_res.transcript
            ctx.confidence = stt_res.confidence

            if tool_record.status == ToolExecutionStatus.FAILURE:
                ctx.last_error = tool_record.error_message
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.FAILED,
                    f"Speech transcription failed: {tool_record.error_message}",
                    tool_call=tool_record
                )
                return ctx

            if not stt_res.transcript or not stt_res.transcript.strip():
                ctx.retry_count += 1
                if ctx.retry_count >= ctx.max_retries:
                    self._record_event(
                        ctx,
                        action,
                        WorkflowState.FAILED,
                        f"Exceeded speech transcription retry limit ({ctx.max_retries}).",
                        tool_call=tool_record
                    )
                else:
                    self._record_event(
                        ctx,
                        action,
                        WorkflowState.UNCERTAIN,
                        "No intelligible speech detected. Please speak clearly into the microphone.",
                        tool_call=tool_record
                    )
                return ctx

            ctx.retry_count = 0
            self._record_event(
                ctx,
                action,
                WorkflowState.AWAITING_CONFIRMATION,
                f"Speech transcribed as: '{stt_res.transcript}'. Ready for confirmation or reverse sign matching.",
                {"is_mock": stt_res.is_mock, "confidence": stt_res.confidence},
                tool_call=tool_record
            )
            return ctx

        # -------------------------------------------------------------
        # Action 8: CONFIRM_TRANSCRIPT (Reverse Sign Matching)
        # -------------------------------------------------------------
        if action == WorkflowAction.CONFIRM_TRANSCRIPT:
            confirmed_text = payload.get("transcript") or ctx.transcript or ""
            ctx.transcript = confirmed_text

            tool_record, match_res = agent_tools.match_dictionary_sign(confirmed_text)
            ctx.reverse_match_found = match_res.matched

            if match_res.matched and match_res.matched_sign:
                ctx.current_sign_id = match_res.matched_sign.id
                ctx.reverse_sign_media = match_res.matched_sign.media.model_dump()
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.GENERATING_SIGN_OUTPUT,
                    match_res.explanation,
                    {"sign_id": match_res.matched_sign.id, "grammar": match_res.isl_grammar_note},
                    tool_call=tool_record
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
                    match_res.explanation,
                    tool_call=tool_record
                )
            return ctx

        # -------------------------------------------------------------
        # Action 9: TRIGGER_SPEECH (Synthesize Audio Output)
        # -------------------------------------------------------------
        if action == WorkflowAction.TRIGGER_SPEECH:
            lang = payload.get("language", "en")
            text = ctx.hindi_text if lang == "hi" else ctx.english_text
            if not text:
                text = payload.get("text", "")

            if not text:
                ctx.last_error = "Missing text for speech synthesis."
                self._record_event(ctx, action, WorkflowState.FAILED, "Speech synthesis failed: missing text.")
                return ctx

            tool_record, synth_res = await agent_tools.synthesize_speech(text, lang, ctx.session_id)
            if synth_res.status == "SUCCESS":
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.COMPLETED,
                    f"Synthesized {lang.upper()} speech successfully [{synth_res.provider_name}].",
                    tool_call=tool_record
                )
            else:
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.FAILED,
                    f"Speech synthesis failed: {synth_res.error_message}",
                    tool_call=tool_record
                )
            return ctx

        # -------------------------------------------------------------
        # Action 10: RETRY
        # -------------------------------------------------------------
        if action == WorkflowAction.RETRY:
            if ctx.retry_count >= ctx.max_retries:
                err_msg = f"Retry budget exhausted ({ctx.retry_count}/{ctx.max_retries}). Transitioning to FAILED."
                ctx.last_error = err_msg
                self._record_event(ctx, action, WorkflowState.FAILED, err_msg)
                return ctx

            ctx.retry_count += 1
            if ctx.active_route == "SIGN_TO_SPEECH":
                gesture_classifier.reset_session(ctx.session_id)
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.CAPTURING,
                    f"Retrying sign recognition (attempt {ctx.retry_count}/{ctx.max_retries})."
                )
            elif ctx.active_route == "SPEECH_TO_TEXT":
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.TRANSCRIBING,
                    f"Retrying speech recognition (attempt {ctx.retry_count}/{ctx.max_retries})."
                )
            else:
                self._record_event(
                    ctx,
                    action,
                    WorkflowState.IDLE,
                    f"Retrying workflow (attempt {ctx.retry_count}/{ctx.max_retries})."
                )
            return ctx

        return ctx

agent_orchestrator = CommunicationAgentOrchestrator()

import time
import logging
from typing import Dict, Any, Optional, Tuple, List
from backend.app.schemas.orchestrator import ToolExecutionStatus, ToolCallRecord
from backend.app.schemas.vision import RecognitionRequest, RecognitionResult, HandLandmarks
from backend.app.schemas.speech import TranscribeRequest, TranscribeResponse, SynthesizeRequest, SynthesizeResponse
from backend.app.schemas.translation import TranslationRequest, TranslationResponse
from backend.app.schemas.sign import ReverseMatchResponse
from backend.app.services.vision.classifier import gesture_classifier
from backend.app.services.speech.provider import speech_provider
from backend.app.services.translation.provider import translation_provider
from backend.app.services.sign_dictionary.manifest_service import dictionary_service

logger = logging.getLogger(__name__)

class AgentToolRegistry:
    """
    Typed, bounded tool dispatcher for the Signify Communication Agent.
    Every tool execution is metered, structured, sanitized, and isolated.
    """

    @staticmethod
    def classify_vision(
        hands: List[Dict[str, Any]],
        session_id: str,
        consent_granted: bool
    ) -> Tuple[ToolCallRecord, RecognitionResult]:
        """Tool: Evaluates normalized 3D hand coordinates via Random Forest + Anthropometric heuristic consensus."""
        start_time = time.perf_counter()
        action = "CLASSIFY_HAND_LANDMARKS"
        tool_name = "VisionLandmarkClassifier"

        if not consent_granted:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            record = ToolCallRecord(
                tool_name=tool_name,
                action=action,
                status=ToolExecutionStatus.BLOCKED,
                input_summary={"hands_count": len(hands), "consent_granted": False},
                output_summary={},
                confidence=0.0,
                execution_time_ms=round(elapsed, 2),
                error_message="Affirmative consent required before visual landmark processing."
            )
            dummy_res = RecognitionResult(
                status="CONSENT_REQUIRED",
                confidence=0.0,
                is_stable=False,
                stability_count=0,
                rejection_reason="Camera consent required.",
                candidates=[],
                model_version=gesture_classifier.model_version
            )
            return record, dummy_res

        try:
            parsed_hands = [HandLandmarks(**h) if isinstance(h, dict) else h for h in hands]
            rec_req = RecognitionRequest(
                hands=parsed_hands,
                session_id=session_id,
                consent_granted=consent_granted
            )
            result = gesture_classifier.classify_frame(rec_req)
            elapsed = (time.perf_counter() - start_time) * 1000.0

            if result.status == "RECOGNIZED" and result.is_stable and result.sign_id:
                status = ToolExecutionStatus.SUCCESS
            elif result.status in ("UNCERTAIN", "NO_HANDS"):
                status = ToolExecutionStatus.UNCERTAIN
            else:
                status = ToolExecutionStatus.BLOCKED

            record = ToolCallRecord(
                tool_name=tool_name,
                action=action,
                status=status,
                input_summary={"hands_detected": len(parsed_hands), "session_id": session_id},
                output_summary={
                    "status": result.status,
                    "sign_id": result.sign_id,
                    "display_name": result.display_name,
                    "is_stable": result.is_stable,
                    "stability_count": result.stability_count,
                    "rejection_reason": result.rejection_reason
                },
                confidence=result.confidence,
                execution_time_ms=round(elapsed, 2),
                error_message=result.rejection_reason if status == ToolExecutionStatus.UNCERTAIN else None
            )
            return record, result

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Vision tool error: {e}", exc_info=True)
            record = ToolCallRecord(
                tool_name=tool_name,
                action=action,
                status=ToolExecutionStatus.FAILURE,
                input_summary={"hands_count": len(hands)},
                output_summary={},
                confidence=0.0,
                execution_time_ms=round(elapsed, 2),
                error_message=str(e)
            )
            err_res = RecognitionResult(
                status="UNCERTAIN",
                confidence=0.0,
                is_stable=False,
                stability_count=0,
                rejection_reason=f"Classifier error: {e}",
                candidates=[],
                model_version=gesture_classifier.model_version
            )
            return record, err_res

    @staticmethod
    async def translate_text(
        text: str,
        source_lang: str = "en",
        target_lang: str = "hi"
    ) -> Tuple[ToolCallRecord, Optional[TranslationResponse]]:
        """Tool: Translates text across language boundaries via VerbX LangShift or offline engine."""
        start_time = time.perf_counter()
        action = f"TRANSLATE_{source_lang.upper()}_TO_{target_lang.upper()}"
        tool_name = "VerbXTranslationEngine"

        try:
            req = TranslationRequest(text=text, source_lang=source_lang, target_lang=target_lang)
            res = await translation_provider.translate(req)
            elapsed = (time.perf_counter() - start_time) * 1000.0

            record = ToolCallRecord(
                tool_name=tool_name,
                action=action,
                status=ToolExecutionStatus.SUCCESS,
                input_summary={"text_sample": text[:40], "source_lang": source_lang, "target_lang": target_lang},
                output_summary={"translated_text": res.translated_text, "provider": res.provider_name},
                confidence=1.0,
                execution_time_ms=round(elapsed, 2),
                error_message=None
            )
            return record, res
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Translation tool error: {e}")
            record = ToolCallRecord(
                tool_name=tool_name,
                action=action,
                status=ToolExecutionStatus.FAILURE,
                input_summary={"text_sample": text[:40]},
                output_summary={},
                confidence=0.0,
                execution_time_ms=round(elapsed, 2),
                error_message=str(e)
            )
            return record, None

    @staticmethod
    async def synthesize_speech(
        text: str,
        language: str = "en",
        session_id: str = "default-session"
    ) -> Tuple[ToolCallRecord, SynthesizeResponse]:
        """Tool: Generates audible speech waveforms via VerbX TTS or offline speech synthesis."""
        start_time = time.perf_counter()
        action = f"SYNTHESIZE_{language.upper()}_SPEECH"
        tool_name = "VerbXSpeechSynthesizer"

        try:
            req = SynthesizeRequest(text=text, language=language, session_id=session_id)
            res = await speech_provider.synthesize(req)
            elapsed = (time.perf_counter() - start_time) * 1000.0

            status = ToolExecutionStatus.SUCCESS if res.status == "SUCCESS" else ToolExecutionStatus.FAILURE
            record = ToolCallRecord(
                tool_name=tool_name,
                action=action,
                status=status,
                input_summary={"text_length": len(text), "language": language},
                output_summary={
                    "status": res.status,
                    "provider": res.provider_name,
                    "has_audio": bool(res.audio_base64)
                },
                confidence=1.0 if status == ToolExecutionStatus.SUCCESS else 0.0,
                execution_time_ms=round(elapsed, 2),
                error_message=res.error_message
            )
            return record, res
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Speech synthesis tool error: {e}")
            record = ToolCallRecord(
                tool_name=tool_name,
                action=action,
                status=ToolExecutionStatus.FAILURE,
                input_summary={"text": text[:30], "language": language},
                output_summary={},
                confidence=0.0,
                execution_time_ms=round(elapsed, 2),
                error_message=str(e)
            )
            return record, SynthesizeResponse(status="FAILED", provider_name="fallback", error_message=str(e))

    @staticmethod
    async def transcribe_speech(
        audio_base64: Optional[str] = None,
        language: str = "en",
        session_id: str = "default-session",
        mock_input_text: Optional[str] = None
    ) -> Tuple[ToolCallRecord, TranscribeResponse]:
        """Tool: Transcribes spoken acoustic signal to normalized text via VerbX Vocaline STT."""
        start_time = time.perf_counter()
        action = f"TRANSCRIBE_{language.upper()}_SPEECH"
        tool_name = "VerbXSpeechTranscriber"

        try:
            req = TranscribeRequest(
                audio_base64=audio_base64,
                language=language,
                session_id=session_id,
                mock_input_text=mock_input_text
            )
            res = await speech_provider.transcribe(req)
            elapsed = (time.perf_counter() - start_time) * 1000.0

            has_text = bool(res.transcript and res.transcript.strip())
            status = ToolExecutionStatus.SUCCESS if has_text else ToolExecutionStatus.UNCERTAIN

            record = ToolCallRecord(
                tool_name=tool_name,
                action=action,
                status=status,
                input_summary={"has_audio": bool(audio_base64), "is_mock": bool(mock_input_text), "language": language},
                output_summary={
                    "transcript": res.transcript,
                    "confidence": res.confidence,
                    "is_mock": res.is_mock
                },
                confidence=res.confidence,
                execution_time_ms=round(elapsed, 2),
                error_message=None if has_text else "Empty or unintelligible speech audio."
            )
            return record, res
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Transcription tool error: {e}")
            record = ToolCallRecord(
                tool_name=tool_name,
                action=action,
                status=ToolExecutionStatus.FAILURE,
                input_summary={"language": language},
                output_summary={},
                confidence=0.0,
                execution_time_ms=round(elapsed, 2),
                error_message=str(e)
            )
            return record, TranscribeResponse(transcript="", confidence=0.0, is_mock=False, error_message=str(e))

    @staticmethod
    def match_dictionary_sign(
        phrase: str
    ) -> Tuple[ToolCallRecord, ReverseMatchResponse]:
        """Tool: Evaluates spoken text against verified ISL dictionary; retrieves authentic visual clips and grammar."""
        start_time = time.perf_counter()
        action = "MATCH_ISL_VOCABULARY"
        tool_name = "ISLDictionaryRegistry"

        try:
            res = dictionary_service.match_reverse_phrase(phrase)
            elapsed = (time.perf_counter() - start_time) * 1000.0

            status = ToolExecutionStatus.SUCCESS if res.matched else ToolExecutionStatus.UNCERTAIN
            record = ToolCallRecord(
                tool_name=tool_name,
                action=action,
                status=status,
                input_summary={"query_phrase": phrase},
                output_summary={
                    "matched": res.matched,
                    "matched_sign_id": res.matched_sign.id if res.matched_sign else None,
                    "isl_grammar_note": res.isl_grammar_note,
                    "explanation": res.explanation
                },
                confidence=1.0 if res.matched else 0.0,
                execution_time_ms=round(elapsed, 2),
                error_message=None if res.matched else "Vocabulary limitation: No verified demonstration exists."
            )
            return record, res
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Dictionary tool error: {e}")
            record = ToolCallRecord(
                tool_name=tool_name,
                action=action,
                status=ToolExecutionStatus.FAILURE,
                input_summary={"query_phrase": phrase},
                output_summary={},
                confidence=0.0,
                execution_time_ms=round(elapsed, 2),
                error_message=str(e)
            )
            return record, ReverseMatchResponse(
                matched=False,
                matched_sign=None,
                explanation=f"Dictionary lookup error: {e}"
            )

agent_tools = AgentToolRegistry()

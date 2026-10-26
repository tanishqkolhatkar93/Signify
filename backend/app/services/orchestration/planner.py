import time
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.app.schemas.orchestrator import (
    ToolCapability,
    PlanStep,
    ExecutionPlan,
    GoalPlanRequest,
    GoalExecutionResponse,
    ToolExecutionStatus,
    ToolCallRecord,
)
from backend.app.services.orchestration.tools import agent_tools
from backend.app.core.database import SessionLocal, AuditEventRecord

logger = logging.getLogger(__name__)

class AutonomousGoalPlanner:
    """
    Autonomous Multi-Step Goal Planner and Tool Discovery Engine.
    
    Transforms high-level user intents into directed acyclic execution graphs (DAGs),
    monitors runtime step confidence, and dynamically replans upon environmental
    ambiguity or low confidence.
    """

    def __init__(self):
        self.active_plans: Dict[str, ExecutionPlan] = {}

    def discover_tools(self) -> List[ToolCapability]:
        """Dynamic Tool Reflection API: Queries live agent registry."""
        return agent_tools.discover_tools()

    def create_plan(
        self,
        goal: str,
        session_id: str = "default-session",
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """
        Synthesizes a multi-step execution plan based on introspected tool capabilities.
        """
        plan_id = f"plan-{uuid.uuid4().hex[:10]}"
        context = context or {}
        g_upper = goal.strip().upper()

        steps: List[PlanStep] = []

        if "SIGN_TO_BILINGUAL_SPEECH" in g_upper or "SIGN_TO_SPEECH" in g_upper:
            # 5-step autonomous sign translation plan
            steps = [
                PlanStep(
                    step_id=1,
                    name="Calibrate Environment & Frame",
                    tool_name="EnvironmentalCalibrationTool",
                    action="CALIBRATE_ENVIRONMENT",
                    rationale="Evaluate lighting, contrast, and stability before biometric landmark extraction.",
                    parameters={"session_id": session_id, "confidence": 0.95},
                    depends_on=[]
                ),
                PlanStep(
                    step_id=2,
                    name="Classify Hand Landmarks",
                    tool_name="VisionLandmarkClassifier",
                    action="CLASSIFY_HAND_LANDMARKS",
                    rationale="Extract scale/rotation invariant ISL gesture semantics from 21 3D landmarks.",
                    parameters={"session_id": session_id, "consent_granted": context.get("consent_granted", True)},
                    depends_on=[1]
                ),
                PlanStep(
                    step_id=3,
                    name="Cross-Lingual Hindi Translation",
                    tool_name="VerbXTranslationEngine",
                    action="TRANSLATE_EN_TO_HI",
                    rationale="Generate parallel bilingual Hindi text output from recognized English ISL concept.",
                    parameters={"source_lang": "en", "target_lang": "hi"},
                    depends_on=[2]
                ),
                PlanStep(
                    step_id=4,
                    name="Synthesize Primary English Speech",
                    tool_name="VerbXSpeechSynthesizer",
                    action="SYNTHESIZE_EN_SPEECH",
                    rationale="Synthesize spoken acoustic signal in English for hearing communicators.",
                    parameters={"language": "en", "session_id": session_id},
                    depends_on=[2]
                ),
                PlanStep(
                    step_id=5,
                    name="Synthesize Secondary Hindi Speech",
                    tool_name="VerbXSpeechSynthesizer",
                    action="SYNTHESIZE_HI_SPEECH",
                    rationale="Synthesize spoken acoustic signal in Hindi for multilingual hearing communicators.",
                    parameters={"language": "hi", "session_id": session_id},
                    depends_on=[3]
                )
            ]

        elif "SPEECH_TO_SIGN" in g_upper or "REVERSE" in g_upper or "SPEECH_TO_TEXT" in g_upper:
            # 4-step autonomous speech to sign and text plan
            steps = [
                PlanStep(
                    step_id=1,
                    name="Acoustic Speech Transcription",
                    tool_name="VerbXSpeechTranscriber",
                    action="TRANSCRIBE_EN_SPEECH",
                    rationale="Transcribe microphone input into normalized text with confidence scoring.",
                    parameters={"language": context.get("language", "en"), "session_id": session_id},
                    depends_on=[]
                ),
                PlanStep(
                    step_id=2,
                    name="ISL Syntax & Spatial Compilation",
                    tool_name="ISLGrammarCompiler",
                    action="COMPILE_ISL_GLOSS",
                    rationale="Compile linear sentence into authentic ISL Topic-Comment / Wh-final spatial gloss.",
                    parameters={"source_language": context.get("language", "en")},
                    depends_on=[1]
                ),
                PlanStep(
                    step_id=3,
                    name="Authenticated ISL Media Retrieval",
                    tool_name="ISLDictionaryRegistry",
                    action="MATCH_ISL_VOCABULARY",
                    rationale="Match semantic phrase against authenticated ISLRTC 28-sign video database.",
                    parameters={},
                    depends_on=[1]
                )
            ]

        elif "EMERGENCY_TRIAGE" in g_upper:
            steps = [
                PlanStep(
                    step_id=1,
                    name="Fast Landmark Extraction",
                    tool_name="VisionLandmarkClassifier",
                    action="CLASSIFY_HAND_LANDMARKS",
                    rationale="Urgent priority triage: evaluate hand posture with high sensitivity.",
                    parameters={"session_id": session_id, "consent_granted": True},
                    depends_on=[]
                ),
                PlanStep(
                    step_id=2,
                    name="Emergency Bilingual Broadcast",
                    tool_name="VerbXSpeechSynthesizer",
                    action="SYNTHESIZE_EN_SPEECH",
                    rationale="Immediately alert hospital triage staff in English and Hindi.",
                    parameters={"language": "en", "session_id": session_id},
                    depends_on=[1]
                )
            ]

        else:
            # General Adaptive Communication Plan
            steps = [
                PlanStep(
                    step_id=1,
                    name="Capability & Environment Audit",
                    tool_name="EnvironmentalCalibrationTool",
                    action="CALIBRATE_ENVIRONMENT",
                    rationale="Verify input channel stability and tool latency budget.",
                    parameters={"session_id": session_id},
                    depends_on=[]
                ),
                PlanStep(
                    step_id=2,
                    name="ISL Syntax Translation",
                    tool_name="ISLGrammarCompiler",
                    action="COMPILE_ISL_GLOSS",
                    rationale="Compile communication payload into authentic visual gloss.",
                    parameters={"source_language": "en"},
                    depends_on=[1]
                )
            ]

        plan = ExecutionPlan(
            plan_id=plan_id,
            goal=goal,
            session_id=session_id,
            steps=steps,
            status="INITIALIZED",
            replan_count=0,
            adaptation_log=[f"Plan synthesized with {len(steps)} steps via autonomous capability discovery."]
        )
        self.active_plans[plan_id] = plan
        return plan

    async def execute_plan(
        self,
        plan_id: str,
        inputs: Optional[Dict[str, Any]] = None
    ) -> GoalExecutionResponse:
        """
        Executes the plan DAG step-by-step, evaluating output confidence and dynamically
        replanning if an unexpected condition occurs.
        """
        plan = self.active_plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan ID {plan_id} not found.")

        inputs = inputs or {}
        start_wall = time.perf_counter()
        plan.status = "IN_PROGRESS"
        
        step_outputs: Dict[int, Any] = {}
        executed_steps = 0
        replan_occurred = False
        final_output: Dict[str, Any] = {}

        for step in plan.steps:
            if step.status == "SKIPPED":
                continue

            step.status = "RUNNING"
            step_start = time.perf_counter()

            try:
                # -------------------------------------------------------------
                # Step Execution via Tool Registry
                # -------------------------------------------------------------
                if step.tool_name == "EnvironmentalCalibrationTool":
                    rec, res = agent_tools.assess_environment(
                        session_id=plan.session_id,
                        confidence=inputs.get("confidence", 0.95),
                        jitter_std=inputs.get("jitter_std", 0.01)
                    )
                    step.output = res
                    step.status = "COMPLETED"

                elif step.tool_name == "VisionLandmarkClassifier":
                    hands = inputs.get("hands", [])
                    consent = inputs.get("consent_granted", True)
                    # Temporal frame stabilization loop
                    num_frames = 5 if inputs.get("feed_stable_sequence", True) and len(hands) > 0 else 1
                    rec = None
                    res = None
                    for _ in range(num_frames):
                        rec, res = agent_tools.classify_vision(
                            hands=hands,
                            session_id=plan.session_id,
                            consent_granted=consent
                        )
                    step.output = {
                        "status": res.status,
                        "sign_id": res.sign_id,
                        "display_name": res.display_name,
                        "confidence": res.confidence,
                        "is_stable": res.is_stable
                    }

                    # DYNAMIC ADAPTIVE REPLANNING TRIGGER:
                    # If vision classification is uncertain (<0.65) or blocked, adapt the plan!
                    if res.status != "RECOGNIZED" or res.confidence < 0.65:
                        replan_occurred = True
                        plan.replan_count += 1
                        plan.status = "ADAPTED"
                        adaptation_reason = (
                            f"Vision landmark confidence ({res.confidence:.2f}) below safety threshold (0.65). "
                            "Dynamically adapting plan: inserting Honest Uncertainty Disclosure and skipping audio hallucination."
                        )
                        plan.adaptation_log.append(adaptation_reason)
                        logger.warning(f"[AutonomousPlanner] {adaptation_reason}")

                        # Adapt subsequent speech steps to prevent false voice output
                        for future_step in plan.steps:
                            if future_step.step_id > step.step_id and "Speech" in future_step.name:
                                future_step.status = "SKIPPED"
                                future_step.rationale = "Skipped by autonomous safety replanner: prevented false speech hallucination."

                        step.status = "UNCERTAIN_ADAPTED"
                        final_output["recognition_state"] = "UNCERTAIN"
                        final_output["rejection_reason"] = res.rejection_reason or "Low confidence / unsupported gesture."
                        break
                    else:
                        step.status = "COMPLETED"
                        final_output["sign_id"] = res.sign_id
                        final_output["display_name"] = res.display_name
                        final_output["confidence"] = res.confidence

                elif step.tool_name == "VerbXTranslationEngine":
                    src_text = inputs.get("text") or final_output.get("display_name") or "Good"
                    rec, res = await agent_tools.translate_text(
                        text=src_text,
                        source_lang=step.parameters.get("source_lang", "en"),
                        target_lang=step.parameters.get("target_lang", "hi")
                    )
                    step.output = {"translated_text": res.translated_text if res else "", "provider": res.provider_name if res else ""}
                    step.status = "COMPLETED"
                    final_output["hindi_text"] = res.translated_text if res else ""

                elif step.tool_name == "VerbXSpeechSynthesizer":
                    lang = step.parameters.get("language", "en")
                    txt = final_output.get("hindi_text") if lang == "hi" else (final_output.get("display_name") or inputs.get("text", "Good"))
                    rec, res = await agent_tools.synthesize_speech(
                        text=txt,
                        language=lang,
                        session_id=plan.session_id
                    )
                    step.output = {"status": res.status, "provider": res.provider_name, "has_audio": bool(res.audio_base64)}
                    step.status = "COMPLETED"
                    final_output[f"{lang}_audio_ready"] = res.status == "SUCCESS"

                elif step.tool_name == "VerbXSpeechTranscriber":
                    rec, res = await agent_tools.transcribe_speech(
                        audio_base64=inputs.get("audio_base64"),
                        language=step.parameters.get("language", "en"),
                        session_id=plan.session_id,
                        mock_input_text=inputs.get("mock_input_text")
                    )
                    step.output = {"transcript": res.transcript, "confidence": res.confidence}
                    step.status = "COMPLETED"
                    final_output["transcript"] = res.transcript

                elif step.tool_name == "ISLGrammarCompiler":
                    text_to_compile = final_output.get("transcript") or inputs.get("text", "Thank you")
                    rec, res = agent_tools.compile_isl_syntax(text_to_compile)
                    step.output = res
                    step.status = "COMPLETED"
                    final_output["isl_gloss"] = res["isl_gloss"]
                    final_output["grammar_notes"] = res["grammar_notes"]

                elif step.tool_name == "ISLDictionaryRegistry":
                    phrase = final_output.get("transcript") or inputs.get("text", "Thank you")
                    rec, res = agent_tools.match_dictionary_sign(phrase)
                    step.output = {
                        "matched": res.matched,
                        "sign_id": res.matched_sign.id if res.matched_sign else None,
                        "explanation": res.explanation
                    }
                    step.status = "COMPLETED"
                    final_output["dictionary_matched"] = res.matched
                    final_output["matched_sign_id"] = res.matched_sign.id if res.matched_sign else None
                    final_output["dictionary_explanation"] = res.explanation

                step.execution_time_ms = round((time.perf_counter() - step_start) * 1000.0, 2)
                step_outputs[step.step_id] = step.output
                executed_steps += 1

            except Exception as e:
                logger.error(f"[AutonomousPlanner] Step {step.step_id} failed: {e}", exc_info=True)
                step.status = "FAILED"
                step.output = {"error": str(e)}
                plan.status = "FAILED"
                break

        total_latency = round((time.perf_counter() - start_wall) * 1000.0, 2)
        if plan.status != "FAILED" and not replan_occurred:
            plan.status = "COMPLETED"

        # Record autonomous cognitive decision in persistent SQLite audit ledger
        db = SessionLocal()
        try:
            audit = AuditEventRecord(
                session_id=plan.session_id,
                from_state="PLANNING",
                to_state=plan.status,
                action="EXECUTE_AUTONOMOUS_PLAN",
                payload_summary=f"Goal: {plan.goal} | Replanned: {replan_occurred} | Latency: {total_latency}ms",
                status=plan.status
            )
            db.add(audit)
            db.commit()
        except Exception as err:
            logger.warning(f"Failed to record audit event for plan: {err}")
        finally:
            db.close()

        return GoalExecutionResponse(
            plan_id=plan.plan_id,
            goal=plan.goal,
            status=plan.status,
            steps_executed=executed_steps,
            total_latency_ms=total_latency,
            replan_occurred=replan_occurred,
            final_output=final_output,
            plan=plan
        )

goal_planner = AutonomousGoalPlanner()


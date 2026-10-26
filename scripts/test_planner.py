import asyncio
import os
import sys
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ["PROVIDER_MODE"] = "mock"

from backend.app.core.config import settings
settings.PROVIDER_MODE = "mock"
from backend.app.services.speech.provider import MockSpeechProvider, speech_provider
from backend.app.services.translation.provider import MockTranslationProvider, translation_provider
import backend.app.services.speech.provider as sp_mod
import backend.app.services.translation.provider as tp_mod

sp_mod.speech_provider = MockSpeechProvider()
tp_mod.translation_provider = MockTranslationProvider()

from backend.app.services.orchestration.planner import goal_planner
from backend.app.services.tests.runner import generate_mock_hand

async def test_planner():
    # 1. Discover tools
    tools = goal_planner.discover_tools()
    print(f"Discovered {len(tools)} tools:")
    for t in tools:
        print(f" - {t.name} ({t.category}): {t.description[:60]}...")
    assert len(tools) >= 5

    # 2. Create Plan
    plan = goal_planner.create_plan("SIGN_TO_BILINGUAL_SPEECH", "session-test-plan")
    print(f"\nCreated plan {plan.plan_id} with {len(plan.steps)} steps.")
    for s in plan.steps:
        print(f" Step {s.step_id}: {s.name} -> {s.tool_name}")
    assert len(plan.steps) == 5

    # 3. Execute Plan with valid mock hands
    hands = generate_mock_hand("thumbs_up")
    inputs = {"hands": [h.model_dump() for h in hands], "consent_granted": True}
    res = await goal_planner.execute_plan(plan.plan_id, inputs)
    print(f"\nPlan executed: status={res.status}, replanned={res.replan_occurred}, latency={res.total_latency_ms}ms")
    print(f"Final output: {res.final_output}")
    assert res.status == "COMPLETED"
    assert res.replan_occurred is False
    assert res.final_output.get("sign_id") == "isl_good"

    # 4. Test Dynamic Adaptive Replanning upon uncertain sign
    plan_uncertain = goal_planner.create_plan("SIGN_TO_BILINGUAL_SPEECH", "session-test-uncertain")
    hands_distractor = generate_mock_hand("random_distractor")
    inputs_uncertain = {"hands": [h.model_dump() for h in hands_distractor], "consent_granted": True}
    res_uncertain = await goal_planner.execute_plan(plan_uncertain.plan_id, inputs_uncertain)
    print(f"\nUncertain plan executed: status={res_uncertain.status}, replanned={res_uncertain.replan_occurred}")
    print(f"Adaptation log: {res_uncertain.plan.adaptation_log}")
    assert res_uncertain.replan_occurred is True
    assert res_uncertain.final_output.get("recognition_state") == "UNCERTAIN"
    
    # 5. Speech to Sign & Text Plan
    plan_speech = goal_planner.create_plan("SPEECH_TO_SIGN_AND_TEXT", "session-test-speech")
    res_speech = await goal_planner.execute_plan(plan_speech.plan_id, {"mock_input_text": "Thank you"})
    print(f"\nSpeech plan executed: status={res_speech.status}, isl_gloss={res_speech.final_output.get('isl_gloss')}")
    assert res_speech.status == "COMPLETED"
    assert res_speech.final_output.get("dictionary_matched") is True
    assert res_speech.final_output.get("matched_sign_id") == "isl_thank_you"

    print("\n=======================================================")
    print("SUCCESS: ALL AUTONOMOUS PLANNING & REPLANNING VERIFIED!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(test_planner())

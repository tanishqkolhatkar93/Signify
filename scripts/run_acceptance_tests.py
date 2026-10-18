import sys
import asyncio
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.services.tests.runner import test_runner

async def main():
    print("=================================================================")
    print("        SIGNIFY — OFFICIAL ACCEPTANCE TEST SUITE (TC1-TC4)       ")
    print("=================================================================\n")
    
    records = await test_runner.run_all_tests()
    
    passed_all = True
    for r in records:
        status_symbol = "PASS" if r.status == "PASS" else "FAIL"
        print(f"[{status_symbol}] {r.test_id}: {r.name}")
        print(f"       Input:       {r.input_description}")
        print(f"       Expected:    {r.expected_output}")
        print(f"       Actual:      {r.actual_output}")
        print(f"       Evidence:    {r.evidence_ref} | Model: {r.model_version}")
        print(f"       Notes:       {r.notes}\n")
        if r.status != "PASS":
            passed_all = False

    print("=================================================================")
    if passed_all:
        print("RESULT: ALL 4 OFFICIAL ACCEPTANCE TESTS PASSED SUCCESSFULLY.")
    else:
        print("RESULT: ONE OR MORE TESTS FAILED.")
    print("=================================================================")
    return 0 if passed_all else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

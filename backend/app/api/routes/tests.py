from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db, TestRunRecord
from backend.app.schemas.test import TestRunResponse, AcceptanceTestSummary
from backend.app.services.tests.runner import test_runner
from backend.app.core.config import settings

router = APIRouter(prefix="/tests", tags=["Acceptance Tests"])

@router.get("/runs", response_model=List[TestRunResponse])
def get_all_test_runs(db: Session = Depends(get_db)):
    records = db.query(TestRunRecord).order_by(TestRunRecord.id.desc()).all()
    return records

@router.post("/run-all", response_model=List[TestRunResponse])
async def execute_acceptance_tests():
    records = await test_runner.run_all_tests()
    return records

@router.get("/summary", response_model=AcceptanceTestSummary)
def get_acceptance_summary(db: Session = Depends(get_db)):
    records = db.query(TestRunRecord).order_by(TestRunRecord.id.desc()).all()
    
    # Get latest run of each test ID (TC1, TC2, TC3, TC4)
    latest_by_id = {}
    for r in records:
        if r.test_id not in latest_by_id:
            latest_by_id[r.test_id] = r

    latest_list = list(latest_by_id.values())
    total = len(latest_list)
    passed = sum(1 for r in latest_list if r.status == "PASS")
    failed = sum(1 for r in latest_list if r.status == "FAIL")
    blocked = sum(1 for r in latest_list if r.status == "BLOCKED")
    rate = round((passed / total * 100), 1) if total > 0 else 0.0

    return AcceptanceTestSummary(
        total_runs=total,
        passed_count=passed,
        failed_count=failed,
        blocked_count=blocked,
        pass_rate_percent=rate,
        test_cases=latest_list,
        verified_languages=settings.SUPPORTED_LANGUAGES,
        system_version=settings.MODEL_NAME
    )


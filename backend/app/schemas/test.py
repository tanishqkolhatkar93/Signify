from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class TestRunBase(BaseModel):
    test_id: str
    name: str
    input_description: str
    expected_output: str
    actual_output: str
    status: str  # PASS, FAIL, BLOCKED
    confidence: Optional[float] = None
    model_version: str
    evidence_ref: Optional[str] = None
    notes: Optional[str] = None

class TestRunCreate(TestRunBase):
    pass

class TestRunResponse(TestRunBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

class AcceptanceTestSummary(BaseModel):
    total_runs: int
    passed_count: int
    failed_count: int
    blocked_count: int
    pass_rate_percent: float
    test_cases: List[TestRunResponse]
    verified_languages: List[str]
    system_version: str


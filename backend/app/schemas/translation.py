from typing import Optional
from pydantic import BaseModel

class TranslationRequest(BaseModel):
    text: str
    source_language: str = "en"
    target_language: str = "hi"
    session_id: Optional[str] = "default-session"

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    provider_name: str
    is_mock: bool
    status: str = "SUCCESS"


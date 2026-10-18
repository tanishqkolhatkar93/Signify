from typing import Optional
from pydantic import BaseModel, Field

class TranscribeRequest(BaseModel):
    audio_base64: Optional[str] = None
    language: str = "en"
    session_id: Optional[str] = "default-session"
    sample_rate: Optional[int] = 16000
    mock_input_text: Optional[str] = None  # Allows passing text for automated deterministic testing

class TranscribeResponse(BaseModel):
    transcript: str
    language: str
    confidence: float
    provider_name: str
    is_mock: bool
    status: str = "SUCCESS"
    notes: Optional[str] = None

class SynthesizeRequest(BaseModel):
    text: str
    language: str = "en"  # "en" or "hi"
    sign_id: Optional[str] = None
    session_id: Optional[str] = "default-session"

class SynthesizeResponse(BaseModel):
    text: str
    language: str
    audio_base64: Optional[str] = None
    audio_url: Optional[str] = None
    audio_mime: str = "audio/wav"
    provider_name: str
    is_mock: bool
    status: str = "SUCCESS"


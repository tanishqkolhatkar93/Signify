from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class SignMedia(BaseModel):
    type: str
    asset_url: str
    verified_clip_url: Optional[str] = None
    description: str

class SignItem(BaseModel):
    id: str
    display_name: str
    sign_language: str
    category: str
    is_dynamic: bool
    validation_status: str
    meaning: str
    english_text: str
    hindi_text: str
    phonetic_transcription: Optional[str] = None
    hand_configuration: str
    landmark_signature: Optional[Dict[str, Any]] = None
    media: SignMedia
    source: str
    license: str

class SignManifest(BaseModel):
    sign_language: str
    language_code: str
    version: str
    vocabulary_scope: str
    disclaimer: str
    data_attribution: Dict[str, str]
    signs: List[SignItem]

class ReverseMatchRequest(BaseModel):
    phrase: str

class ReverseMatchResponse(BaseModel):
    matched: bool
    query_phrase: str
    matched_sign: Optional[SignItem] = None
    explanation: str


from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class SignMedia(BaseModel):
    type: str = "svg_illustration"
    asset_url: str
    verified_clip_url: Optional[str] = None
    description: str

class SignItem(BaseModel):
    id: str
    canonical_phrase: Optional[str] = None
    display_name: str
    sign_language: str = "Indian Sign Language (ISL)"
    category: str
    sign_type: str = "word"  # "word", "phrase", "number", "fingerspelling"
    is_dynamic: bool = False
    validation_status: str = "verified"  # "verified", "pending_review"
    meaning: str
    english_text: str
    hindi_text: str
    phonetic_transcription: Optional[str] = None
    hand_configuration: str
    isl_grammar_structure: Optional[str] = None
    cultural_linguistic_notes: Optional[str] = None
    approved_synonyms: List[str] = Field(default_factory=list)
    landmark_signature: Optional[Dict[str, Any]] = None
    media: SignMedia
    source: str
    license: str = "CC-BY-4.0"

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
    isl_grammar_note: Optional[str] = None
    explanation: str

class SignImportRequest(BaseModel):
    signs: List[SignItem]
    overwrite_existing: bool = False

class SignImportResponse(BaseModel):
    status: str
    total_submitted: int
    imported_count: int
    updated_count: int
    skipped_duplicates: List[str]
    message: str

class CategoryCoverage(BaseModel):
    category: str
    count: int
    verified_count: int

class TypeCoverage(BaseModel):
    sign_type: str
    count: int

class VocabularyCoverageReport(BaseModel):
    sign_language: str
    total_entries: int
    verified_count: int
    pending_count: int
    categories: List[CategoryCoverage]
    sign_types: List[TypeCoverage]
    media_coverage_percent: float
    model_coverage_count: int
    source_attribution: Dict[str, str]
    disclaimer: str

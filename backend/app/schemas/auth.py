from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class GoogleAuthRequest(BaseModel):
    credential: str
    client_id: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    role: str = "signer"
    dominant_hand: str = "right"
    signing_speed: str = "normal"
    preferred_language: str = "en"

class CalibrationUpdateRequest(BaseModel):
    dominant_hand: Optional[str] = None  # "right", "left"
    signing_speed: Optional[str] = None  # "slow", "normal", "fast"
    preferred_language: Optional[str] = None  # "en", "hi"

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
    message: str = "Authentication successful"

class AuthStatusResponse(BaseModel):
    authenticated: bool = False
    user: Optional[UserProfile] = None
    google_client_id: Optional[str] = None

class ConversationCreateRequest(BaseModel):
    title: Optional[str] = None
    transcript: str
    translation: Optional[str] = None
    matched_sign_id: Optional[str] = None

class ConversationItem(BaseModel):
    id: str
    user_id: str
    title: str
    transcript: str
    translation: Optional[str] = None
    matched_sign_id: Optional[str] = None
    created_at: datetime

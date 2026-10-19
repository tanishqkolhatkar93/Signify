from typing import Optional
from pydantic import BaseModel, EmailStr

class GoogleAuthRequest(BaseModel):
    credential: str
    client_id: Optional[str] = None

class DemoLoginRequest(BaseModel):
    email: Optional[str] = "tanishq.signer@gmail.com"
    name: Optional[str] = "Tanishq (Signify Builder)"

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    role: str = "user"

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
    message: str = "Authentication successful"

class AuthStatusResponse(BaseModel):
    authenticated: bool
    user: Optional[UserProfile] = None
    google_client_id: Optional[str] = None

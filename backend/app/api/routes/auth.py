from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from backend.app.schemas.auth import (
    GoogleAuthRequest,
    AuthResponse,
    UserProfile,
    AuthStatusResponse,
)
from backend.app.services.auth.google_auth import google_auth_service
from backend.app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/status", response_model=AuthStatusResponse)
def get_auth_status(authorization: Optional[str] = Header(None)):
    user = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user = google_auth_service.verify_access_token(token)

    return AuthStatusResponse(
        authenticated=user is not None,
        user=user,
        google_client_id=settings.GOOGLE_CLIENT_ID or ""
    )

@router.post("/google", response_model=AuthResponse)
async def google_login(req: GoogleAuthRequest):
    try:
        payload = await google_auth_service.verify_google_credential(req.credential)
        user = google_auth_service.upsert_user_from_google(payload)
        token = google_auth_service.create_access_token(user)
        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user=user,
            message="Google authentication successful"
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Google authentication failed: {str(e)}"
        )

@router.get("/me", response_model=UserProfile)
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    token = authorization.split(" ")[1]
    user = google_auth_service.verify_access_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")

    return user

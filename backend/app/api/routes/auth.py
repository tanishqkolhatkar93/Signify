from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List
from backend.app.schemas.auth import (
    GoogleAuthRequest,
    AuthResponse,
    UserProfile,
    AuthStatusResponse,
    CalibrationUpdateRequest,
    ConversationCreateRequest,
    ConversationItem,
)
from backend.app.services.auth.google_auth import google_auth_service
from backend.app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_authenticated_user(authorization: Optional[str]) -> UserProfile:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in with Google.")
    token = authorization.split(" ")[1]
    user = google_auth_service.verify_access_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session token.")
    return user

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
    return get_authenticated_user(authorization)

@router.patch("/profile", response_model=UserProfile)
def update_profile_calibration(
    req: CalibrationUpdateRequest,
    authorization: Optional[str] = Header(None)
):
    user = get_authenticated_user(authorization)
    try:
        updated = google_auth_service.update_user_calibration(
            user_id=user.id,
            dominant_hand=req.dominant_hand,
            signing_speed=req.signing_speed,
            preferred_language=req.preferred_language
        )
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/conversations", response_model=ConversationItem)
def save_conversation(
    req: ConversationCreateRequest,
    authorization: Optional[str] = Header(None)
):
    user = get_authenticated_user(authorization)
    return google_auth_service.save_conversation(
        user_id=user.id,
        transcript=req.transcript,
        title=req.title,
        translation=req.translation,
        matched_sign_id=req.matched_sign_id
    )

@router.get("/conversations", response_model=List[ConversationItem])
def list_conversations(authorization: Optional[str] = Header(None)):
    user = get_authenticated_user(authorization)
    return google_auth_service.list_conversations(user.id)

@router.delete("/conversations/{conv_id}")
def delete_conversation(conv_id: str, authorization: Optional[str] = Header(None)):
    user = get_authenticated_user(authorization)
    success = google_auth_service.delete_conversation(user.id, conv_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found or not owned by user.")
    return {"status": "success", "message": f"Conversation {conv_id} deleted."}

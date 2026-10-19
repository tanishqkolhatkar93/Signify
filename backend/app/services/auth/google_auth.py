import time
import uuid
import httpx
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal, UserRecord, ConversationRecord
from backend.app.schemas.auth import UserProfile, AuthResponse, ConversationItem

def record_to_user_profile(rec: UserRecord) -> UserProfile:
    return UserProfile(
        id=rec.id,
        email=rec.email,
        name=rec.name,
        given_name=rec.given_name,
        family_name=rec.family_name,
        picture=rec.picture,
        role=rec.role or "signer",
        dominant_hand=rec.dominant_hand or "right",
        signing_speed=rec.signing_speed or "normal",
        preferred_language=rec.preferred_language or "en"
    )

class GoogleAuthService:
    def __init__(self):
        self.jwt_secret = settings.JWT_SECRET
        self.jwt_algorithm = settings.JWT_ALGORITHM
        self.jwt_expires_minutes = settings.JWT_EXPIRES_MINUTES
        self.google_client_id = settings.GOOGLE_CLIENT_ID

    async def verify_google_credential(self, credential: str) -> Dict[str, Any]:
        """
        Verifies a Google ID token against Google's public OAuth2 tokeninfo endpoint.
        Validates audience (aud) matches the configured GOOGLE_CLIENT_ID.
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
            )
            if res.status_code != 200:
                raise ValueError("Google OAuth token verification failed: Invalid token or expired.")
            
            payload = res.json()

            # Verify audience if client_id is configured
            if settings.GOOGLE_CLIENT_ID:
                aud = payload.get("aud")
                if aud != settings.GOOGLE_CLIENT_ID:
                    raise ValueError(f"Token audience ({aud}) does not match configured Google Client ID.")

            # Ensure email is verified
            if payload.get("email_verified") not in [True, "true", "True"]:
                raise ValueError("Google account email is not verified.")

            return payload

    def upsert_user_from_google(self, payload: Dict[str, Any]) -> UserProfile:
        email = payload.get("email")
        if not email:
            raise ValueError("Google user profile must contain a valid email address.")

        name = payload.get("name") or email.split("@")[0]
        google_id = payload.get("sub")
        if not google_id:
            raise ValueError("Missing Google user identifier (sub).")

        picture = payload.get("picture")
        given_name = payload.get("given_name")
        family_name = payload.get("family_name")

        db = SessionLocal()
        try:
            user = db.query(UserRecord).filter(
                (UserRecord.email == email) | (UserRecord.google_id == google_id)
            ).first()

            if user:
                user.google_id = google_id
                user.name = name
                user.picture = picture or user.picture
                user.given_name = given_name or user.given_name
                user.family_name = family_name or user.family_name
                user.last_login = datetime.utcnow()
                db.commit()
                db.refresh(user)
            else:
                user_id = f"usr_{uuid.uuid4().hex[:12]}"
                user = UserRecord(
                    id=user_id,
                    google_id=google_id,
                    email=email,
                    name=name,
                    given_name=given_name,
                    family_name=family_name,
                    picture=picture,
                    role="signer",
                    dominant_hand="right",
                    signing_speed="normal",
                    preferred_language="en",
                    created_at=datetime.utcnow(),
                    last_login=datetime.utcnow()
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            return record_to_user_profile(user)
        finally:
            db.close()

    def update_user_calibration(
        self,
        user_id: str,
        dominant_hand: Optional[str] = None,
        signing_speed: Optional[str] = None,
        preferred_language: Optional[str] = None
    ) -> UserProfile:
        db = SessionLocal()
        try:
            user = db.query(UserRecord).filter(UserRecord.id == user_id).first()
            if not user:
                raise ValueError("User not found.")

            if dominant_hand in ["right", "left"]:
                user.dominant_hand = dominant_hand
            if signing_speed in ["slow", "normal", "fast"]:
                user.signing_speed = signing_speed
            if preferred_language in ["en", "hi"]:
                user.preferred_language = preferred_language

            db.commit()
            db.refresh(user)
            return record_to_user_profile(user)
        finally:
            db.close()

    def create_access_token(self, user: UserProfile) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.jwt_expires_minutes)
        payload = {
            "sub": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def verify_access_token(self, token: str) -> Optional[UserProfile]:
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload.get("sub")
            if not user_id:
                return None

            db = SessionLocal()
            try:
                rec = db.query(UserRecord).filter(UserRecord.id == user_id).first()
                if rec:
                    return record_to_user_profile(rec)
                return None
            finally:
                db.close()
        except jwt.PyJWTError:
            return None

    # Conversation Management
    def save_conversation(
        self,
        user_id: str,
        transcript: str,
        title: Optional[str] = None,
        translation: Optional[str] = None,
        matched_sign_id: Optional[str] = None
    ) -> ConversationItem:
        db = SessionLocal()
        try:
            conv_id = f"conv_{uuid.uuid4().hex[:12]}"
            effective_title = title or (transcript[:40] + "..." if len(transcript) > 40 else transcript)
            rec = ConversationRecord(
                id=conv_id,
                user_id=user_id,
                title=effective_title,
                transcript=transcript,
                translation=translation,
                matched_sign_id=matched_sign_id,
                created_at=datetime.utcnow()
            )
            db.add(rec)
            db.commit()
            db.refresh(rec)
            return ConversationItem(
                id=rec.id,
                user_id=rec.user_id,
                title=rec.title,
                transcript=rec.transcript,
                translation=rec.translation,
                matched_sign_id=rec.matched_sign_id,
                created_at=rec.created_at
            )
        finally:
            db.close()

    def list_conversations(self, user_id: str) -> List[ConversationItem]:
        db = SessionLocal()
        try:
            records = db.query(ConversationRecord).filter(
                ConversationRecord.user_id == user_id
            ).order_by(ConversationRecord.created_at.desc()).all()
            return [
                ConversationItem(
                    id=r.id,
                    user_id=r.user_id,
                    title=r.title,
                    transcript=r.transcript,
                    translation=r.translation,
                    matched_sign_id=r.matched_sign_id,
                    created_at=r.created_at
                )
                for r in records
            ]
        finally:
            db.close()

    def delete_conversation(self, user_id: str, conv_id: str) -> bool:
        db = SessionLocal()
        try:
            rec = db.query(ConversationRecord).filter(
                ConversationRecord.id == conv_id,
                ConversationRecord.user_id == user_id
            ).first()
            if rec:
                db.delete(rec)
                db.commit()
                return True
            return False
        finally:
            db.close()

google_auth_service = GoogleAuthService()

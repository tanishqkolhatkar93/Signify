from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.services.sign_dictionary.manifest_service import dictionary_service
from backend.app.services.speech.provider import speech_provider
from backend.app.services.translation.provider import translation_provider

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def get_health():
    manifest = dictionary_service.get_manifest()
    return {
        "status": "healthy",
        "app_name": "Disignum",
        "challenge": "VerbX / IvishAI PS 3: AI Sign-Language Communication",
        "sign_language": manifest.sign_language,
        "supported_signs_count": len(manifest.signs),
        "model_version": settings.MODEL_NAME,
        "provider_mode": settings.PROVIDER_MODE,
        "speech_provider": speech_provider.provider_name,
        "translation_provider": translation_provider.provider_name,
        "supported_speech_languages": settings.SUPPORTED_LANGUAGES,
        "consent_enforced": settings.REQUIRE_EXPLICIT_CONSENT
    }


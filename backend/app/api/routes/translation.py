from fastapi import APIRouter
from backend.app.schemas.translation import TranslationRequest, TranslationResponse
from backend.app.services.translation.provider import translation_provider

router = APIRouter(prefix="/translation", tags=["Translation Services"])

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(req: TranslationRequest):
    return await translation_provider.translate(req)


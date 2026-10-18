from fastapi import APIRouter
from backend.app.schemas.speech import (
    TranscribeRequest,
    TranscribeResponse,
    SynthesizeRequest,
    SynthesizeResponse,
)
from backend.app.services.speech.provider import speech_provider

router = APIRouter(prefix="/speech", tags=["Speech Services"])

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(req: TranscribeRequest):
    return await speech_provider.transcribe(req)

@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_speech(req: SynthesizeRequest):
    return await speech_provider.synthesize(req)


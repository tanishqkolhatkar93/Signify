import os
import base64
import logging
from abc import ABC, abstractmethod
from typing import Optional
import httpx
from backend.app.schemas.speech import (
    TranscribeRequest,
    TranscribeResponse,
    SynthesizeRequest,
    SynthesizeResponse,
)
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class BaseSpeechProvider(ABC):
    @abstractmethod
    async def transcribe(self, request: TranscribeRequest) -> TranscribeResponse:
        pass

    @abstractmethod
    async def synthesize(self, request: SynthesizeRequest) -> SynthesizeResponse:
        pass

class MockSpeechProvider(BaseSpeechProvider):
    """
    Deterministic local mock provider.
    Used for local testing, CI/CD, and offline hackathon demonstration
    without fabricating live external API status.
    """
    def __init__(self):
        self.provider_name = "Signify-Local-Speech-Provider (Mock Mode)"

    async def transcribe(self, request: TranscribeRequest) -> TranscribeResponse:
        # If explicit mock input text is provided (from test fixtures or UI test harness)
        text = request.mock_input_text or "Hello, how can I help you today?"
        return TranscribeResponse(
            transcript=text,
            language=request.language or "en",
            confidence=0.96,
            provider_name=self.provider_name,
            is_mock=True,
            status="SUCCESS",
            notes="Processed via deterministic local mock provider. No external network request made."
        )

    async def synthesize(self, request: SynthesizeRequest) -> SynthesizeResponse:
        # Generates a minimal valid silent/beacon PCM WAV header in base64
        # RIFF header with 1 second 8kHz 8-bit mono tone
        header = (
            b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            b"\x40\x1f\x00\x00\x40\x1f\x00\x00\x01\x00\x08\x00data\x00\x08\x00\x00"
            + (b"\x80" * 2048)
        )
        audio_b64 = base64.b64encode(header).decode("utf-8")

        return SynthesizeResponse(
            text=request.text,
            language=request.language,
            audio_base64=f"data:audio/wav;base64,{audio_b64}",
            audio_url=None,
            audio_mime="audio/wav",
            provider_name=self.provider_name,
            is_mock=True,
            status="SUCCESS"
        )

class VerbXSpeechProvider(BaseSpeechProvider):
    """
    Official VerbX / IvishAI Platform Speech Integration (https://one.verbxeco.com).
    Calls Vocaline STT and VerbX Multilingual TTS when configured with valid API keys.
    """
    def __init__(self, api_key: str = settings.VERBX_API_KEY, base_url: str = settings.VERBX_API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.fallback_mock = MockSpeechProvider()
        self.provider_name = "VerbX-Vocaline-Platform (one.verbxeco.com)"

    async def transcribe(self, request: TranscribeRequest) -> TranscribeResponse:
        if not self.api_key or self.api_key == "your_verbx_api_key_here":
            logger.info("VerbX API key not configured; falling back to local mock STT.")
            resp = await self.fallback_mock.transcribe(request)
            resp.notes = "VerbX credentials not supplied in .env. Switched to transparent local fallback."
            return resp

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "audio": request.audio_base64,
                    "language": request.language,
                    "model": "vocaline-general"
                }
                res = await client.post(f"{self.base_url}/stt/transcribe", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return TranscribeResponse(
                        transcript=data.get("transcript", ""),
                        language=data.get("language", request.language),
                        confidence=float(data.get("confidence", 0.95)),
                        provider_name=self.provider_name,
                        is_mock=False,
                        status="SUCCESS"
                    )
                else:
                    logger.warning(f"VerbX STT returned status {res.status_code}. Using fallback.")
                    resp = await self.fallback_mock.transcribe(request)
                    resp.notes = f"VerbX API returned HTTP {res.status_code}. Using safe mock fallback."
                    return resp
        except Exception as e:
            logger.error(f"Error calling VerbX STT: {e}. Using fallback.")
            resp = await self.fallback_mock.transcribe(request)
            resp.notes = f"Network exception reaching VerbX ({str(e)}). Using safe mock fallback."
            return resp

    async def synthesize(self, request: SynthesizeRequest) -> SynthesizeResponse:
        if not self.api_key or self.api_key == "your_verbx_api_key_here":
            logger.info("VerbX API key not configured; falling back to local mock TTS.")
            return await self.fallback_mock.synthesize(request)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "text": request.text,
                    "target_language": request.language,
                    "voice": "hi-IN-Standard" if request.language == "hi" else "en-US-Standard"
                }
                res = await client.post(f"{self.base_url}/tts/synthesize", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return SynthesizeResponse(
                        text=request.text,
                        language=request.language,
                        audio_base64=data.get("audio_base64"),
                        audio_url=data.get("audio_url"),
                        audio_mime=data.get("mime_type", "audio/wav"),
                        provider_name=self.provider_name,
                        is_mock=False,
                        status="SUCCESS"
                    )
                else:
                    return await self.fallback_mock.synthesize(request)
        except Exception as e:
            logger.error(f"Error calling VerbX TTS: {e}. Using fallback.")
            return await self.fallback_mock.synthesize(request)

def get_speech_provider() -> BaseSpeechProvider:
    if settings.PROVIDER_MODE == "verbx" and settings.VERBX_API_KEY:
        return VerbXSpeechProvider()
    return MockSpeechProvider()

speech_provider = get_speech_provider()


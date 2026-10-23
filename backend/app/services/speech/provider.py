import os
import uuid
import base64
import logging
import re
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

def sanitize_text_for_speech(raw_text: Optional[str], language: str = "en") -> str:
    """
    Cleans raw text before vocalization, ensuring that delimiter slashes (e.g. 'अच्छा / बहुत अच्छा'),
    regex markers, unescaped tokens, or formatting characters are not pronounced as literal words (e.g. 'slash').
    """
    if not raw_text or not isinstance(raw_text, str):
        return "नमस्ते" if language == "hi" else "Hello"

    text = raw_text.strip()
    # If text contains bilingual or multi-option slash delimiters, select the primary phrase
    if "/" in text or "\\" in text or "|" in text:
        parts = [p.strip() for p in re.split(r'[/\\|]', text) if p.strip()]
        if parts:
            text = parts[0]

    # Strip delimiter slashes, escape characters, and regex markers
    clean_text = re.sub(r'[/\\#,+()$~%.\'":*?<>{}[\]_`^=]', ' ', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    if not clean_text:
        return "नमस्ते" if language == "hi" else "Hello"

    return clean_text

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
        clean_text = sanitize_text_for_speech(request.text, request.language or "en")

        # Generates a minimal valid silent/beacon PCM WAV header in base64
        # RIFF header with 1 second 8kHz 8-bit mono tone
        header = (
            b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            b"\x40\x1f\x00\x00\x40\x1f\x00\x00\x01\x00\x08\x00data\x00\x08\x00\x00"
            + (b"\x80" * 2048)
        )
        audio_b64 = base64.b64encode(header).decode("utf-8")

        return SynthesizeResponse(
            text=clean_text,
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
    Official VerbX / IvishAI Platform Speech Integration (https://api.verbxeco.com).
    Calls Vocaline STT and VerbX Multilingual TTS with authenticated API keys.
    """
    def __init__(self, api_key: str = settings.VERBX_API_KEY, base_url: str = settings.VERBX_API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.fallback_mock = MockSpeechProvider()
        self.provider_name = "VerbX-Vocaline-Platform (api.verbxeco.com)"

    async def transcribe(self, request: TranscribeRequest) -> TranscribeResponse:
        if not self.api_key or self.api_key == "your_verbx_api_key_here":
            logger.info("VerbX API key not configured; falling back to local mock STT.")
            resp = await self.fallback_mock.transcribe(request)
            resp.notes = "VerbX credentials not supplied in .env. Switched to transparent local fallback."
            return resp

        try:
            timeout_cfg = httpx.Timeout(2.5, connect=1.0)
            async with httpx.AsyncClient(timeout=timeout_cfg) as client:
                headers = {
                    "x-api-key": self.api_key,
                    "X-VerbX-Shell": "saas",
                    "Content-Type": "application/json",
                    "Idempotency-Key": str(uuid.uuid4())
                }
                payload = {
                    "audio_base64": request.audio_base64,
                    "language": request.language or "en"
                }
                res = await client.post(f"{self.base_url}/v1/stt", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    transcript = data.get("text", "")
                    return TranscribeResponse(
                        transcript=transcript,
                        language=data.get("language", request.language),
                        confidence=float(data.get("confidence", 0.95)),
                        provider_name="VerbX-Vocaline (api.verbxeco.com)",
                        is_mock=False,
                        status="SUCCESS"
                    )
                else:
                    logger.warning(f"VerbX STT returned status {res.status_code}: {res.text}. Using fallback.")
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

        clean_text = sanitize_text_for_speech(request.text, request.language or "en")

        try:
            timeout_cfg = httpx.Timeout(2.5, connect=1.0)
            async with httpx.AsyncClient(timeout=timeout_cfg) as client:
                headers = {
                    "x-api-key": self.api_key,
                    "X-VerbX-Shell": "saas",
                    "Content-Type": "application/json",
                    "Idempotency-Key": str(uuid.uuid4())
                }
                payload = {
                    "text": clean_text
                }
                res = await client.post(f"{self.base_url}/v1/tts", json=payload, headers=headers)
                if res.status_code == 200:
                    mime = res.headers.get("content-type", "audio/mpeg").split(";")[0]
                    audio_b64 = base64.b64encode(res.content).decode("utf-8")
                    return SynthesizeResponse(
                        text=clean_text,
                        language=request.language,
                        audio_base64=f"data:{mime};base64,{audio_b64}",
                        audio_url=None,
                        audio_mime=mime,
                        provider_name="VerbX-TTS (api.verbxeco.com)",
                        is_mock=False,
                        status="SUCCESS"
                    )
                else:
                    logger.warning(f"VerbX TTS returned HTTP {res.status_code}: {res.text}. Using fallback.")
                    return await self.fallback_mock.synthesize(request)
        except Exception as e:
            logger.error(f"Error calling VerbX TTS: {e}. Using fallback.")
            return await self.fallback_mock.synthesize(request)

def get_speech_provider() -> BaseSpeechProvider:
    if settings.PROVIDER_MODE == "verbx" and settings.VERBX_API_KEY:
        return VerbXSpeechProvider()
    return MockSpeechProvider()

speech_provider = get_speech_provider()

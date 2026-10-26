import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict
import httpx
import uuid
from backend.app.schemas.translation import TranslationRequest, TranslationResponse
from backend.app.core.config import settings
import os

logger = logging.getLogger(__name__)

# Curated English <-> Hindi glossary for conversational & sign communication
GLOSSARY_EN_TO_HI = {
    "hello": "नमस्ते",
    "namaste": "नमस्ते",
    "hello / namaste": "नमस्ते / नमस्कार",
    "thank you": "धन्यवाद",
    "thanks": "धन्यवाद",
    "yes": "हाँ",
    "yes / agreed": "हाँ / सहमत",
    "no": "नहीं",
    "no / disagree": "नहीं / असहमत",
    "help": "मदद",
    "help / need assistance": "मदद / सहायता चाहिए",
    "water": "पानी",
    "food": "खाना",
    "food / eat": "खाना / भोजन",
    "stop": "रुको",
    "stop / halt": "रुको / बंद करो",
    "please": "कृपया",
    "good": "अच्छा",
    "good / well": "अच्छा / बहुत अच्छा",
    "bad": "खराब",
    "bad / not good": "खराब / बुरा",
    "more": "और",
    "more / again": "और / ज्यादा",
    "how are you": "आप कैसे हैं?",
    "i need help": "मुझे मदद चाहिए",
    "where is water": "पानी कहाँ है?",
    "good morning": "शुभ प्रभात",
    "welcome": "स्वागत हे"
}

GLOSSARY_HI_TO_EN = {v: k.title() for k, v in GLOSSARY_EN_TO_HI.items()}

class BaseTranslationProvider(ABC):
    @abstractmethod
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        pass

class MockTranslationProvider(BaseTranslationProvider):
    """
    Deterministic English <-> Hindi translation provider for local evaluation.
    Grounds translations in authenticated ISL glosses and conversational phrases.
    """
    def __init__(self):
        self.provider_name = "Signify-Local-Translation-Engine (Mock Mode)"

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        text_clean = request.text.strip().lower()
        src = request.source_language.lower()
        tgt = request.target_language.lower()

        translated = None
        if src == "en" and tgt == "hi":
            if text_clean in GLOSSARY_EN_TO_HI:
                translated = GLOSSARY_EN_TO_HI[text_clean]
            else:
                for k, v in GLOSSARY_EN_TO_HI.items():
                    if k in text_clean:
                        translated = v
                        break
            if not translated:
                translated = f"[अनुवाद: {request.text}]"
        elif src == "hi" and tgt == "en":
            for hi_k, en_v in GLOSSARY_HI_TO_EN.items():
                if hi_k in text_clean:
                    translated = en_v
                    break
            if not translated:
                translated = f"[Translation: {request.text}]"
        else:
            translated = request.text

        return TranslationResponse(
            original_text=request.text,
            translated_text=translated,
            source_language=request.source_language,
            target_language=request.target_language,
            provider_name=self.provider_name,
            is_mock=True,
            status="SUCCESS"
        )

class VerbXTranslationProvider(BaseTranslationProvider):
    """
    Official VerbX Multilingual Translation Integration (api.verbxeco.com).
    Uses verbx-langshift model supporting English, Hindi, and 76 languages.
    Equipped with a circuit breaker for instant local fallback when offline.
    """
    def __init__(self, api_key: str = settings.VERBX_API_KEY, base_url: str = settings.VERBX_API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.fallback = MockTranslationProvider()
        self.provider_name = "VerbX-Langshift (api.verbxeco.com)"
        self._offline = False

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        if self._offline or os.environ.get("PROVIDER_MODE") == "mock" or getattr(settings, "PROVIDER_MODE", "mock") == "mock" or not self.api_key or self.api_key == "your_verbx_api_key_here":
            return await self.fallback.translate(request)

        try:
            timeout_cfg = httpx.Timeout(2.0, connect=0.5)
            async with httpx.AsyncClient(timeout=timeout_cfg) as client:
                headers = {
                    "x-api-key": self.api_key,
                    "X-VerbX-Shell": "saas",
                    "Content-Type": "application/json",
                    "Idempotency-Key": str(uuid.uuid4()),
                }
                payload = {
                    "text": request.text,
                    "source_lang": request.source_language.lower(),
                    "target_lang": request.target_language.lower(),
                }
                res = await client.post(f"{self.base_url}/v1/translate", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    translated = data.get("text") or data.get("translated_text") or request.text
                    return TranslationResponse(
                        original_text=request.text,
                        translated_text=translated,
                        source_language=request.source_language,
                        target_language=request.target_language,
                        provider_name=self.provider_name,
                        is_mock=False,
                        status="SUCCESS"
                    )
                else:
                    logger.warning(f"VerbX Translation HTTP {res.status_code}. Using fallback.")
                    return await self.fallback.translate(request)
        except Exception as e:
            self._offline = True
            logger.info(f"VerbX Translation unavailable ({e}). Switched to local fallback.")
            return await self.fallback.translate(request)

def get_translation_provider() -> BaseTranslationProvider:
    if settings.PROVIDER_MODE == "verbx" and settings.VERBX_API_KEY:
        return VerbXTranslationProvider()
    return MockTranslationProvider()

translation_provider = get_translation_provider()

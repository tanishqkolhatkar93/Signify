import logging
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, Tuple
import httpx
import uuid
from backend.app.schemas.translation import TranslationRequest, TranslationResponse
from backend.app.core.config import settings
import os

logger = logging.getLogger(__name__)

def clean_punctuation(text: str) -> str:
    """Strips punctuation, question marks, and danda from text."""
    return re.sub(r'[?!.,;:|\u0964\u0965"\']', ' ', text).strip()

def has_devanagari(text: str) -> bool:
    """Checks if text contains Hindi Devanagari script."""
    return any("\u0900" <= ch <= "\u097f" for ch in text)

# Comprehensive bidirectional conversational & ISL sign glossary
CONVERSATIONAL_HI_TO_EN = {
    # Variations of "How are you?"
    "आप कैसे हो": "How are you?",
    "आप कैसे हैं": "How are you?",
    "तुम कैसे हो": "How are you?",
    "तू कैसा है": "How are you?",
    "कैसे हो": "How are you?",
    "कैसे हैं": "How are you?",
    "क्या हाल है": "How are you?",
    "सब ठीक": "Is everything okay?",
    "सब ठीक है": "Everything is fine.",
    
    # Greetings & Courtesy
    "नमस्ते": "Hello / Greetings",
    "नमस्कार": "Hello / Namaste",
    "धन्यवाद": "Thank you",
    "बहुत धन्यवाद": "Thank you very much",
    "शुक्रिया": "Thank you",
    "कृपया": "Please",
    "स्वागत है": "Welcome",
    "शुभ प्रभात": "Good morning",
    "अलविदा": "Goodbye",
    
    # Affirmations & Negations
    "हाँ": "Yes",
    "हाँ सहमत": "Yes / Agreed",
    "नहीं": "No",
    "नहीं असहमत": "No / Disagree",
    "बिल्कुल": "Absolutely",
    
    # Essentials & Daily Living
    "पानी": "Water",
    "मुझे पानी चाहिए": "I need water",
    "खाना": "Food",
    "भोजन": "Food / Meal",
    "मुझे खाना चाहिए": "I need food",
    "भूख लगी है": "I am hungry",
    "प्यास लगी है": "I am thirsty",
    "शौचालय": "Restroom / Toilet",
    "टॉयलेट": "Restroom / Toilet",
    "शौचालय कहाँ है": "Where is the restroom?",
    "टॉयलेट कहाँ है": "Where is the restroom?",
    "पैसे": "Money",
    "रुपए": "Money / Rupees",
    "समय": "Time",
    "समय क्या हुआ": "What time is it?",
    "परिवार": "Family",
    
    # Medical & Emergency
    "मदद": "Help",
    "सहायता": "Assistance / Help",
    "मुझे मदद चाहिए": "I need help",
    "कृपया मदद करें": "Please help me",
    "मदद करो": "Help me",
    "दर्द": "Pain / Hurt",
    "तकलीफ": "Pain / Discomfort",
    "मुझे दर्द हो रहा है": "I am in pain",
    "डॉक्टर": "Doctor",
    "डॉक्टर को बुलाओ": "Call a doctor",
    "मुझे डॉक्टर चाहिए": "I need to see a doctor",
    "दवाई": "Medicine",
    "औषधि": "Medicine",
    "अस्पताल": "Hospital",
    "खतरा": "Danger / Emergency",
    "आपातकाल": "Emergency",
    "आपातकालीन": "Emergency",
    
    # Questions
    "कहाँ": "Where?",
    "कहाँ है": "Where is it?",
    "क्या": "What?",
    "क्या है": "What is it?",
    "आपका नाम क्या है": "What is your name?",
    "तुम्हारा नाम क्या है": "What is your name?",
    "नाम क्या है": "What is your name?",
    "क्यों": "Why?",
    "कब": "When?",
    "कौन": "Who?",
    
    # Evaluation & Feelings
    "अच्छा": "Good / Well",
    "बहुत अच्छा": "Very good",
    "खराब": "Bad / Unwell",
    "बुरा": "Bad",
    "और": "More",
    "ज्यादा": "More / Again",
    "रुको": "Stop",
    "बंद करो": "Halt / Stop",
    "समझ गया": "I understand",
    "समझ में आया": "Understood",
    "नहीं समझा": "I do not understand",
    "खुश": "Happy",
    "उदास": "Sad / Unhappy"
}

# Reverse mapping English to Hindi
CONVERSATIONAL_EN_TO_HI = {
    "how are you": "आप कैसे हैं?",
    "how are you doing": "आप कैसे हैं?",
    "what is your name": "आपका नाम क्या है?",
    "hello": "नमस्ते",
    "namaste": "नमस्ते",
    "thank you": "धन्यवाद",
    "thanks": "धन्यवाद",
    "please": "कृपया",
    "yes": "हाँ",
    "no": "नहीं",
    "help": "मदद",
    "i need help": "मुझे मदद चाहिए",
    "please help me": "कृपया मेरी मदद करें",
    "water": "पानी",
    "i need water": "मुझे पानी चाहिए",
    "where is water": "पानी कहाँ है?",
    "food": "खाना",
    "i need food": "मुझे खाना चाहिए",
    "doctor": "डॉक्टर",
    "i need a doctor": "मुझे डॉक्टर चाहिए",
    "pain": "दर्द",
    "i am in pain": "मुझे दर्द हो रहा है",
    "medicine": "दवाई",
    "hospital": "अस्पताल",
    "restroom": "शौचालय",
    "where is the restroom": "शौचालय कहाँ है?",
    "toilet": "शौचालय",
    "good": "अच्छा",
    "good morning": "शुभ प्रभात",
    "bad": "खराब",
    "stop": "रुको",
    "more": "और",
    "danger": "खतरा",
    "happy": "खुश",
    "sad": "उदास",
    "understand": "समझ गया",
    "i understand": "मैं समझ गया",
    "i do not understand": "मुझे समझ नहीं आया",
    "money": "पैसे",
    "time": "समय",
    "family": "परिवार"
}

class BaseTranslationProvider(ABC):
    @abstractmethod
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        pass

class MockTranslationProvider(BaseTranslationProvider):
    """
    Intelligent English <-> Hindi translation provider for local evaluation & offline fallback.
    Features smart Devanagari script detection, punctuation normalization, and semantic intent matching.
    """
    def __init__(self):
        self.provider_name = "Signify-Local-Translation-Engine (Intelligent Mock Mode)"

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        raw_text = request.text.strip()
        if not raw_text:
            return TranslationResponse(
                original_text="",
                translated_text="",
                source_language=request.source_language,
                target_language=request.target_language,
                provider_name=self.provider_name,
                is_mock=True,
                status="SUCCESS"
            )

        # Automatic Script Detection: If text contains Devanagari, it is Hindi regardless of dropdown
        is_hindi_input = has_devanagari(raw_text)
        src = "hi" if is_hindi_input else ("en" if request.source_language == "en" else "hi")
        tgt = "en" if src == "hi" else "hi"

        text_clean = clean_punctuation(raw_text.lower())
        translated = None

        if src == "hi":
            # 1. Exact match on cleaned Hindi
            if text_clean in CONVERSATIONAL_HI_TO_EN:
                translated = CONVERSATIONAL_HI_TO_EN[text_clean]
            
            # 2. Substring matching
            if not translated:
                for hi_phrase, en_phrase in CONVERSATIONAL_HI_TO_EN.items():
                    if hi_phrase in text_clean or text_clean in hi_phrase:
                        translated = en_phrase
                        break
            
            # 3. Keyword / Intent matching for common Hindi patterns
            if not translated:
                if any(w in text_clean for w in ["कैसे", "कैसा", "हाल"]):
                    translated = "How are you?"
                elif any(w in text_clean for w in ["नाम"]) and any(w in text_clean for w in ["क्या"]):
                    translated = "What is your name?"
                elif any(w in text_clean for w in ["दर्द", "तकलीफ", "चोट"]):
                    translated = "I am in pain / hurt."
                elif any(w in text_clean for w in ["डॉक्टर", "वैद्य"]):
                    translated = "I need to see a doctor."
                elif any(w in text_clean for w in ["दवाई", "गोली", "औषधि"]):
                    translated = "I need medicine."
                elif any(w in text_clean for w in ["मदद", "सहायता"]):
                    translated = "Please help me."
                elif any(w in text_clean for w in ["पानी"]):
                    translated = "Water / I need water."
                elif any(w in text_clean for w in ["खाना", "भोजन", "रोटी"]):
                    translated = "Food / I need food."
                elif any(w in text_clean for w in ["शौचालय", "टॉयलेट"]):
                    translated = "Where is the restroom?"
                elif any(w in text_clean for w in ["कहाँ"]):
                    translated = "Where is it located?"
                elif any(w in text_clean for w in ["पैसे", "रुपए"]):
                    translated = "Money / Cash."
                elif any(w in text_clean for w in ["धन्यवाद", "शुक्रिया"]):
                    translated = "Thank you so much."
                elif any(w in text_clean for w in ["नमस्ते", "नमस्कार", "प्रणाम"]):
                    translated = "Hello / Greetings."

            # 4. Final natural fallback (Never display ugly [Translation: ...])
            if not translated:
                translated = f"Translation: {raw_text}"

        else: # src == "en"
            # 1. Exact match on cleaned English
            if text_clean in CONVERSATIONAL_EN_TO_HI:
                translated = CONVERSATIONAL_EN_TO_HI[text_clean]

            # 2. Substring matching
            if not translated:
                for en_phrase, hi_phrase in CONVERSATIONAL_EN_TO_HI.items():
                    if en_phrase in text_clean or text_clean in en_phrase:
                        translated = hi_phrase
                        break

            # 3. Keyword matching
            if not translated:
                if "how are you" in text_clean or "how are" in text_clean:
                    translated = "आप कैसे हैं?"
                elif "name" in text_clean and "what" in text_clean:
                    translated = "आपका नाम क्या है?"
                elif "help" in text_clean:
                    translated = "मुझे मदद चाहिए।"
                elif "water" in text_clean:
                    translated = "मुझे पानी चाहिए।"
                elif "doctor" in text_clean:
                    translated = "मुझे डॉक्टर की जरूरत है।"
                elif "thank" in text_clean:
                    translated = "धन्यवाद।"
                elif "restroom" in text_clean or "toilet" in text_clean:
                    translated = "शौचालय कहाँ है?"

            if not translated:
                translated = f"अनुवाद: {raw_text}"

        return TranslationResponse(
            original_text=raw_text,
            translated_text=translated,
            source_language=src,
            target_language=tgt,
            provider_name=self.provider_name,
            is_mock=True,
            status="SUCCESS"
        )

class VerbXTranslationProvider(BaseTranslationProvider):
    """
    Official VerbX Multilingual Translation Integration (api.verbxeco.com).
    Uses verbx-langshift model supporting English, Hindi, and 76 languages.
    Equipped with automatic script detection and local fallback circuit breaker.
    """
    def __init__(self, api_key: str = settings.VERBX_API_KEY, base_url: str = settings.VERBX_API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.fallback = MockTranslationProvider()
        self.provider_name = "VerbX-Langshift (api.verbxeco.com)"
        self._offline = False

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        raw_text = request.text.strip()
        if not raw_text:
            return await self.fallback.translate(request)

        # Automatic Script Detection: Ensure correct source/target even if user forgot to flip dropdown
        is_hindi_input = has_devanagari(raw_text)
        src = "hi" if is_hindi_input else ("en" if request.source_language == "en" else "hi")
        tgt = "en" if src == "hi" else "hi"

        if self._offline or not self.api_key or self.api_key == "your_verbx_api_key_here":
            return await self.fallback.translate(request)

        try:
            timeout_cfg = httpx.Timeout(4.0, connect=1.0)
            async with httpx.AsyncClient(timeout=timeout_cfg) as client:
                headers = {
                    "x-api-key": self.api_key,
                    "X-VerbX-Shell": "saas",
                    "Content-Type": "application/json",
                    "Idempotency-Key": str(uuid.uuid4()),
                }
                payload = {
                    "text": raw_text,
                    "source_lang": src,
                    "target_lang": tgt,
                }
                res = await client.post(f"{self.base_url}/v1/translate", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    translated = data.get("text") or data.get("translated_text")
                    if translated:
                        return TranslationResponse(
                            original_text=raw_text,
                            translated_text=translated,
                            source_language=src,
                            target_language=tgt,
                            provider_name=self.provider_name,
                            is_mock=False,
                            status="SUCCESS"
                        )
                # If API didn't return valid text, fallback gracefully
                return await self.fallback.translate(request)
        except Exception as e:
            logger.info(f"VerbX Translation offline ({e}). Using intelligent local fallback.")
            return await self.fallback.translate(request)

def get_translation_provider() -> BaseTranslationProvider:
    if settings.PROVIDER_MODE == "verbx" and settings.VERBX_API_KEY:
        return VerbXTranslationProvider()
    return MockTranslationProvider()

translation_provider = get_translation_provider()

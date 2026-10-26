import sys
import os
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.sign_dictionary.manifest_service import dictionary_service

client = TestClient(app)

test_phrases = [
    ("आप कैसे हो?", "hi", "en"),
    ("आप कैसे हैं?", "hi", "en"),
    ("तुम कैसे हो", "hi", "en"),
    ("क्या हाल है?", "hi", "en"),
    ("धन्यवाद", "hi", "en"),
    ("नमस्ते", "hi", "en"),
    ("मुझे डॉक्टर चाहिए", "hi", "en"),
    ("How are you?", "en", "hi"),
    ("Thank you", "en", "hi"),
    ("Hello", "en", "hi"),
]

print("======================================================================")
print("              TRANSLATION & ISL REVERSE MATCH TEST                   ")
print("======================================================================\n")

all_passed = True

for text, src, tgt in test_phrases:
    # 1. Test translation API route
    # Intentionally testing mismatched dropdown (sending source_language='en' for Hindi)
    payload = {
        "text": text,
        "source_language": "en" if src == "hi" else src, # intentional test of auto-detection!
        "target_language": "hi" if src == "hi" else tgt
    }
    res = client.post("/api/v1/translation/translate", json=payload)
    if res.status_code != 200:
        print(f"[FAIL] HTTP {res.status_code} for '{text}'")
        all_passed = False
        continue

    data = res.json()
    translated = data.get("translated_text", "")
    provider = data.get("provider_name", "")
    is_mock = data.get("is_mock", False)

    # 2. Test ISL reverse dictionary matching for the phrase
    match_result = dictionary_service.match_reverse_phrase(text)
    matched_sign = match_result.matched_sign.id if (match_result and match_result.matched_sign) else "No direct sign match"
    note = match_result.isl_grammar_note if match_result else "N/A"

    print(f"Input:        {text}")
    print(f"Auto-Src/Tgt: {data.get('source_language')} -> {data.get('target_language')}")
    print(f"Translated:   {translated}")
    print(f"Provider:     {provider} (is_mock={is_mock})")
    print(f"ISL Match:    {matched_sign} (Grammar: {note})")
    print("-" * 60)

    # Sanity checks
    if not translated or translated == f"[Translation: {text}]":
        print(f"[FAIL] Untranslated raw text returned for '{text}'!")
        all_passed = False

if all_passed:
    print("\n>>> ALL TRANSLATION TESTS PASSED PERFECTLY! <<<")
else:
    print("\n>>> SOME TRANSLATION TESTS FAILED! <<<")

print("\n======================================================================")
print("             OFFLINE / LOCAL MOCK FALLBACK TEST                       ")
print("======================================================================")
from backend.app.services.translation.provider import MockTranslationProvider
from backend.app.schemas.translation import TranslationRequest
import asyncio

async def test_offline():
    mock_p = MockTranslationProvider()
    req = TranslationRequest(text="आप कैसे हो?", source_language="en", target_language="hi")
    res = await mock_p.translate(req)
    print(f"Offline Input:       {req.text}")
    print(f"Offline Output:      {res.translated_text}")
    print(f"Offline Source->Tgt: {res.source_language} -> {res.target_language}")
    print(f"Offline Provider:    {res.provider_name} (is_mock={res.is_mock})")
    assert res.translated_text == "How are you?"
    print(">>> OFFLINE FALLBACK ALSO PASSED 100%! <<<")

asyncio.run(test_offline())


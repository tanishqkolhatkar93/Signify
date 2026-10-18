import json
import re
from pathlib import Path
from typing import List, Optional
from backend.app.core.config import SIGN_MANIFEST_PATH, settings
from backend.app.schemas.sign import SignManifest, SignItem, ReverseMatchResponse

class SignDictionaryService:
    def __init__(self, manifest_path: Path = SIGN_MANIFEST_PATH):
        self.manifest_path = manifest_path
        self._manifest: Optional[SignManifest] = None
        self._load_manifest()

    def _load_manifest(self):
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Sign manifest not found at {self.manifest_path}")
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._manifest = SignManifest(**data)

    def get_manifest(self) -> SignManifest:
        if self._manifest is None:
            self._load_manifest()
        return self._manifest

    def list_signs(self, category: Optional[str] = None) -> List[SignItem]:
        manifest = self.get_manifest()
        if category:
            return [s for s in manifest.signs if s.category.lower() == category.lower()]
        return manifest.signs

    def get_sign_by_id(self, sign_id: str) -> Optional[SignItem]:
        for s in self.get_manifest().signs:
            if s.id.lower() == sign_id.lower():
                return s
        return None

    def search_signs(self, query: str) -> List[SignItem]:
        q = query.strip().lower()
        if not q:
            return self.list_signs()
        results = []
        for s in self.get_manifest().signs:
            if (
                q in s.display_name.lower()
                or q in s.meaning.lower()
                or q in s.english_text.lower()
                or q in s.hindi_text.lower()
                or q in s.category.lower()
            ):
                results.append(s)
        return results

    def match_reverse_phrase(self, phrase: str) -> ReverseMatchResponse:
        cleaned = re.sub(r"[^\w\s]", "", phrase.lower()).strip()
        tokens = set(cleaned.split())
        
        # Keyword mapping to verified ISL signs
        keyword_map = {
            "isl_namaste_hello": ["hello", "namaste", "hi", "greetings", "welcome", "namaskar"],
            "isl_thank_you": ["thank", "thanks", "gratitude", "dhanyavaad", "shukriya"],
            "isl_yes": ["yes", "yeah", "agree", "agreed", "correct", "haan"],
            "isl_no": ["no", "nope", "disagree", "dont", "nahin", "nahi"],
            "isl_help": ["help", "assist", "assistance", "emergency", "madad", "doctor"],
            "isl_water": ["water", "drink", "thirsty", "pani", "paani", "jal"],
            "isl_food": ["food", "eat", "hungry", "meal", "dinner", "lunch", "khana", "bhojan"],
            "isl_stop": ["stop", "halt", "pause", "wait", "cease", "ruko", "ruk"],
            "isl_please": ["please", "request", "kindly", "kripya", "kripayah"],
            "isl_good": ["good", "great", "fine", "well", "achha", "badhiya"],
            "isl_bad": ["bad", "poor", "unwell", "sick", "terrible", "bura", "kharab"],
            "isl_more": ["more", "again", "repeat", "extra", "aur", "zyada"]
        }

        matched_sign_id = None
        for sign_id, synonyms in keyword_map.items():
            if any(syn in tokens or syn == cleaned for syn in synonyms):
                matched_sign_id = sign_id
                break

        if matched_sign_id:
            sign = self.get_sign_by_id(matched_sign_id)
            return ReverseMatchResponse(
                matched=True,
                query_phrase=phrase,
                matched_sign=sign,
                explanation=f"Exact match found in verified Indian Sign Language dictionary: '{sign.display_name}'."
            )

        return ReverseMatchResponse(
            matched=False,
            query_phrase=phrase,
            matched_sign=None,
            explanation=f"Speech transcribed successfully. Notice: No verified ISL demonstration clip currently exists in the curated vocabulary for '{phrase}'."
        )

dictionary_service = SignDictionaryService()


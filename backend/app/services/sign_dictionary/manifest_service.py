import json
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.app.core.config import SIGN_MANIFEST_PATH, settings
from backend.app.core.database import SessionLocal, SignItemRecord
from backend.app.schemas.sign import (
    SignManifest,
    SignItem,
    SignMedia,
    ReverseMatchResponse,
    SignImportRequest,
    SignImportResponse,
    VocabularyCoverageReport,
    CategoryCoverage,
    TypeCoverage,
)

def record_to_sign_item(rec: SignItemRecord) -> SignItem:
    synonyms = []
    if rec.approved_synonyms:
        try:
            synonyms = json.loads(rec.approved_synonyms)
        except Exception:
            synonyms = []

    landmark_sig = None
    if rec.landmark_signature:
        try:
            landmark_sig = json.loads(rec.landmark_signature)
        except Exception:
            landmark_sig = None

    return SignItem(
        id=rec.id,
        canonical_phrase=rec.canonical_phrase,
        display_name=rec.display_name,
        sign_language=rec.sign_language,
        category=rec.category,
        sign_type=rec.sign_type,
        is_dynamic=rec.is_dynamic,
        validation_status=rec.validation_status,
        meaning=rec.meaning,
        english_text=rec.english_text,
        hindi_text=rec.hindi_text,
        phonetic_transcription=rec.phonetic_transcription,
        hand_configuration=rec.hand_configuration,
        isl_grammar_structure=rec.isl_grammar_structure,
        cultural_linguistic_notes=rec.cultural_linguistic_notes,
        approved_synonyms=synonyms,
        landmark_signature=landmark_sig,
        media=SignMedia(
            type=rec.media_type,
            asset_url=rec.asset_url,
            verified_clip_url=rec.verified_clip_url,
            description=rec.media_description or rec.display_name,
        ),
        source=rec.source,
        license=rec.license,
    )

def sign_item_to_record_dict(item: SignItem) -> dict:
    return {
        "id": item.id,
        "canonical_phrase": item.canonical_phrase or item.english_text,
        "display_name": item.display_name,
        "sign_language": item.sign_language,
        "category": item.category,
        "sign_type": item.sign_type,
        "is_dynamic": item.is_dynamic,
        "validation_status": item.validation_status,
        "meaning": item.meaning,
        "english_text": item.english_text,
        "hindi_text": item.hindi_text,
        "phonetic_transcription": item.phonetic_transcription,
        "hand_configuration": item.hand_configuration,
        "isl_grammar_structure": item.isl_grammar_structure,
        "cultural_linguistic_notes": item.cultural_linguistic_notes,
        "approved_synonyms": json.dumps(item.approved_synonyms),
        "landmark_signature": json.dumps(item.landmark_signature) if item.landmark_signature else None,
        "media_type": item.media.type,
        "asset_url": item.media.asset_url,
        "verified_clip_url": item.media.verified_clip_url,
        "media_description": item.media.description,
        "source": item.source,
        "license": item.license,
    }

class SignDictionaryService:
    def __init__(self, manifest_path: Path = SIGN_MANIFEST_PATH):
        self.manifest_path = manifest_path
        self._manifest_metadata: Dict[str, Any] = {}
        self._init_sync()

    def _init_sync(self):
        """Loads manifest JSON and ensures SQLite database is populated."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Sign manifest not found at {self.manifest_path}")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._manifest_metadata = {
            "sign_language": data.get("sign_language", "Indian Sign Language (ISL)"),
            "language_code": data.get("language_code", "isl"),
            "version": data.get("version", "2.1.0"),
            "vocabulary_scope": data.get("vocabulary_scope", "Curated Indian Sign Language Practical Vocabulary"),
            "disclaimer": data.get("disclaimer", ""),
            "data_attribution": data.get("data_attribution", {}),
        }

        # Seed database from manifest if records missing or outdated
        signs_in_json = [SignItem(**s) for s in data.get("signs", [])]
        self._seed_database(signs_in_json)

    def _seed_database(self, signs: List[SignItem]):
        db = SessionLocal()
        try:
            existing_ids = {r.id for r in db.query(SignItemRecord.id).all()}
            for sign in signs:
                record_data = sign_item_to_record_dict(sign)
                if sign.id in existing_ids:
                    # Update existing record
                    db.query(SignItemRecord).filter(SignItemRecord.id == sign.id).update(record_data)
                else:
                    # Insert new record
                    rec = SignItemRecord(**record_data)
                    db.add(rec)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Warning: Failed to seed signs database: {e}")
        finally:
            db.close()

    def get_manifest(self) -> SignManifest:
        signs = self.list_signs()
        return SignManifest(
            sign_language=self._manifest_metadata.get("sign_language", "Indian Sign Language (ISL)"),
            language_code=self._manifest_metadata.get("language_code", "isl"),
            version=self._manifest_metadata.get("version", "2.1.0"),
            vocabulary_scope=self._manifest_metadata.get("vocabulary_scope", "Curated ISL Practical Vocabulary"),
            disclaimer=self._manifest_metadata.get("disclaimer", ""),
            data_attribution=self._manifest_metadata.get("data_attribution", {}),
            signs=signs,
        )

    def list_signs(self, category: Optional[str] = None) -> List[SignItem]:
        db = SessionLocal()
        try:
            query = db.query(SignItemRecord)
            if category:
                query = query.filter(SignItemRecord.category.ilike(category))
            records = query.order_by(SignItemRecord.category, SignItemRecord.display_name).all()
            return [record_to_sign_item(r) for r in records]
        finally:
            db.close()

    def get_sign_by_id(self, sign_id: str) -> Optional[SignItem]:
        db = SessionLocal()
        try:
            rec = db.query(SignItemRecord).filter(SignItemRecord.id.ilike(sign_id)).first()
            if rec:
                return record_to_sign_item(rec)
            return None
        finally:
            db.close()

    def search_signs(self, query: str) -> List[SignItem]:
        q = query.strip().lower()
        if not q:
            return self.list_signs()

        db = SessionLocal()
        try:
            records = db.query(SignItemRecord).all()
            results = []
            for r in records:
                synonyms = []
                if r.approved_synonyms:
                    try:
                        synonyms = [s.lower() for s in json.loads(r.approved_synonyms)]
                    except Exception:
                        pass
                
                search_targets = [
                    r.display_name.lower(),
                    r.meaning.lower(),
                    r.english_text.lower(),
                    r.hindi_text.lower(),
                    r.category.lower(),
                    (r.canonical_phrase or "").lower(),
                    (r.isl_grammar_structure or "").lower(),
                ] + synonyms

                if any(q in target for target in search_targets):
                    results.append(record_to_sign_item(r))
            return results
        finally:
            db.close()

    def import_signs(self, request: SignImportRequest, contributor: Optional[str] = None) -> SignImportResponse:
        db = SessionLocal()
        total = len(request.signs)
        imported = 0
        updated = 0
        skipped = []

        try:
            for item in request.signs:
                existing = db.query(SignItemRecord).filter(SignItemRecord.id == item.id).first()
                if existing:
                    if request.overwrite_existing:
                        update_dict = sign_item_to_record_dict(item)
                        for k, v in update_dict.items():
                            setattr(existing, k, v)
                        if contributor:
                            existing.contributed_by = contributor
                        existing.updated_at = datetime.utcnow()
                        updated += 1
                    else:
                        skipped.append(item.id)
                else:
                    new_rec = SignItemRecord(**sign_item_to_record_dict(item))
                    if contributor:
                        new_rec.contributed_by = contributor
                    db.add(new_rec)
                    imported += 1

            db.commit()
            return SignImportResponse(
                status="success",
                total_submitted=total,
                imported_count=imported,
                updated_count=updated,
                skipped_duplicates=skipped,
                message=f"Import complete: {imported} added, {updated} updated, {len(skipped)} skipped as duplicates."
            )
        except Exception as e:
            db.rollback()
            return SignImportResponse(
                status="error",
                total_submitted=total,
                imported_count=imported,
                updated_count=updated,
                skipped_duplicates=skipped,
                message=f"Database import failed: {str(e)}"
            )
        finally:
            db.close()

    def match_reverse_phrase(self, phrase: str) -> ReverseMatchResponse:
        cleaned = re.sub(r"[^\w\s]", "", phrase.lower()).strip()
        tokens = set(cleaned.split())
        
        all_signs = self.list_signs()

        def extract_phrases(s: SignItem) -> List[str]:
            res = []
            if s.canonical_phrase:
                res.append(s.canonical_phrase)
            if s.approved_synonyms:
                res.extend(s.approved_synonyms)
            if s.english_text:
                for part in re.split(r'[/\\|,;]', s.english_text):
                    if part.strip():
                        res.append(part.strip())
            if s.hindi_text:
                for part in re.split(r'[/\\|,;]', s.hindi_text):
                    if part.strip():
                        res.append(part.strip())
            if s.display_name:
                for part in re.split(r'[/\\|,;]', s.display_name):
                    if part.strip():
                        res.append(part.strip())
            return res
        
        # 1. Exact phrase match against canonical phrase or approved synonyms / split translations
        for s in all_signs:
            phrases = extract_phrases(s)
            for p in phrases:
                p_clean = re.sub(r"[^\w\s]", "", p.lower()).strip()
                if p_clean and p_clean == cleaned:
                    return ReverseMatchResponse(
                        matched=True,
                        query_phrase=phrase,
                        matched_sign=s,
                        isl_grammar_note=s.isl_grammar_structure,
                        explanation=f"Exact match ('{p}') found for '{phrase}'. ISL Grammar: {s.isl_grammar_structure or 'Standard ISL syntax'}."
                    )

        # 2. Multi-word phrase containment in speech (e.g. "I want to ask how are you" -> "how are you")
        for s in all_signs:
            phrases = extract_phrases(s)
            for p in phrases:
                p_clean = re.sub(r"[^\w\s]", "", p.lower()).strip()
                p_tokens = p_clean.split()
                if len(p_tokens) >= 2 and p_clean in cleaned:
                    return ReverseMatchResponse(
                        matched=True,
                        query_phrase=phrase,
                        matched_sign=s,
                        isl_grammar_note=s.isl_grammar_structure,
                        explanation=f"Recognized key conversational phrase '{p}' in input. ISL Grammar: {s.isl_grammar_structure or 'Standard ISL syntax'}."
                    )

        # 3. Keyword / Single token match for high-signal nouns/verbs (English and Hindi)
        for s in all_signs:
            phrases = extract_phrases(s)
            for p in phrases:
                for word in p.split():
                    word_clean = re.sub(r"[^\w\s]", "", word.lower()).strip()
                    if len(word_clean) >= 2 and (word_clean in tokens or word_clean == cleaned):
                        return ReverseMatchResponse(
                            matched=True,
                            query_phrase=phrase,
                            matched_sign=s,
                            isl_grammar_note=s.isl_grammar_structure,
                            explanation=f"Keyword '{word}' matches verified ISL sign '{s.display_name}'. ISL Grammar: {s.isl_grammar_structure or 'Standard ISL syntax'}."
                        )

        # 4. No verified match found: explicit honest rejection
        return ReverseMatchResponse(
            matched=False,
            query_phrase=phrase,
            matched_sign=None,
            isl_grammar_note=None,
            explanation=(
                f"Speech transcribed successfully: '{phrase}'. Notice: No verified Indian Sign Language (ISL) demonstration clip "
                f"currently exists in the curated vocabulary for this sentence. Signify strictly adheres to authentic ISLRTC verified "
                f"recordings and does not fabricate unverified sign animations."
            )
        )

    def generate_coverage_report(self) -> VocabularyCoverageReport:
        all_signs = self.list_signs()
        total = len(all_signs)
        verified = sum(1 for s in all_signs if s.validation_status == "verified")
        pending = total - verified

        # Category coverage
        categories_dict: Dict[str, Dict[str, int]] = {}
        for s in all_signs:
            cat = s.category
            if cat not in categories_dict:
                categories_dict[cat] = {"count": 0, "verified": 0}
            categories_dict[cat]["count"] += 1
            if s.validation_status == "verified":
                categories_dict[cat]["verified"] += 1

        cat_list = [
            CategoryCoverage(category=k, count=v["count"], verified_count=v["verified"])
            for k, v in sorted(categories_dict.items())
        ]

        # Sign type coverage
        type_dict: Dict[str, int] = {}
        for s in all_signs:
            st = s.sign_type
            type_dict[st] = type_dict.get(st, 0) + 1

        type_list = [
            TypeCoverage(sign_type=k, count=v)
            for k, v in sorted(type_dict.items())
        ]

        # Media coverage
        media_count = sum(1 for s in all_signs if s.media and s.media.asset_url)
        media_percent = (media_count / total * 100.0) if total > 0 else 0.0

        # Model coverage
        model_count = sum(1 for s in all_signs if s.landmark_signature is not None)

        return VocabularyCoverageReport(
            sign_language=self._manifest_metadata.get("sign_language", "Indian Sign Language (ISL)"),
            total_entries=total,
            verified_count=verified,
            pending_count=pending,
            categories=cat_list,
            sign_types=type_list,
            media_coverage_percent=round(media_percent, 1),
            model_coverage_count=model_count,
            source_attribution=self._manifest_metadata.get("data_attribution", {}),
            disclaimer=self._manifest_metadata.get("disclaimer", ""),
        )

dictionary_service = SignDictionaryService()

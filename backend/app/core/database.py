from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
Base = declarative_base()

class SignItemRecord(Base):
    __tablename__ = "signs"

    id = Column(String(100), primary_key=True, index=True)
    canonical_phrase = Column(String(255), index=True)
    display_name = Column(String(200))
    sign_language = Column(String(100), default="Indian Sign Language (ISL)")
    category = Column(String(100), index=True)
    sign_type = Column(String(50), default="word")  # word, phrase, number, fingerspelling
    is_dynamic = Column(Boolean, default=False)
    validation_status = Column(String(50), default="verified")  # verified, pending_review
    meaning = Column(Text)
    english_text = Column(String(255))
    hindi_text = Column(String(255))
    phonetic_transcription = Column(String(255), nullable=True)
    hand_configuration = Column(Text)
    isl_grammar_structure = Column(Text, nullable=True)
    cultural_linguistic_notes = Column(Text, nullable=True)
    approved_synonyms = Column(Text, default="[]")  # JSON string array
    landmark_signature = Column(Text, nullable=True)  # JSON string
    media_type = Column(String(50), default="svg_illustration")
    asset_url = Column(String(255))
    verified_clip_url = Column(String(255), nullable=True)
    media_description = Column(Text, nullable=True)
    source = Column(String(255))
    license = Column(String(100), default="CC-BY-4.0")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TestRunRecord(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String(50), index=True)  # e.g., TC1, TC2, TC3, TC4
    name = Column(String(200))
    input_description = Column(Text)
    expected_output = Column(Text)
    actual_output = Column(Text)
    status = Column(String(20))  # PASS, FAIL, BLOCKED
    confidence = Column(Float, nullable=True)
    model_version = Column(String(100))
    evidence_ref = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditEventRecord(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    from_state = Column(String(50))
    to_state = Column(String(50))
    action = Column(String(100))
    payload_summary = Column(Text, nullable=True)
    user_consented = Column(Boolean, default=False)
    status = Column(String(50), default="SUCCESS")
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

# Auto-initialize SQLite tables on load
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

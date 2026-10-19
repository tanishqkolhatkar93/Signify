export interface SignMedia {
  type: string;
  asset_url: string;
  verified_clip_url?: string;
  description: string;
}

export interface SignItem {
  id: string;
  canonical_phrase?: string;
  display_name: string;
  sign_language: string;
  category: string;
  sign_type?: string; // "word" | "phrase" | "number" | "fingerspelling"
  is_dynamic: boolean;
  validation_status: string;
  meaning: string;
  english_text: string;
  hindi_text: string;
  phonetic_transcription?: string;
  hand_configuration: string;
  isl_grammar_structure?: string;
  cultural_linguistic_notes?: string;
  approved_synonyms?: string[];
  landmark_signature?: Record<string, any>;
  media: SignMedia;
  source: string;
  license: string;
}

export interface SignManifest {
  sign_language: string;
  language_code: string;
  version: string;
  vocabulary_scope: string;
  disclaimer: string;
  data_attribution: Record<string, string>;
  signs: SignItem[];
}

export interface CategoryCoverage {
  category: string;
  count: number;
  verified_count: number;
}

export interface TypeCoverage {
  sign_type: string;
  count: number;
}

export interface VocabularyCoverageReport {
  sign_language: string;
  total_entries: number;
  verified_count: number;
  pending_count: number;
  categories: CategoryCoverage[];
  sign_types: TypeCoverage[];
  media_coverage_percent: number;
  model_coverage_count: number;
  source_attribution: Record<string, string>;
  disclaimer: string;
}

export interface SignImportRequest {
  signs: SignItem[];
  overwrite_existing?: boolean;
}

export interface SignImportResponse {
  status: string;
  total_submitted: number;
  imported_count: number;
  updated_count: number;
  skipped_duplicates: string[];
  message: string;
}

export interface LandmarkPoint {
  x: number;
  y: number;
  z: number;
  visibility?: number;
}

export interface HandLandmarks {
  handedness: string;
  landmarks: LandmarkPoint[];
}

export interface RecognitionCandidate {
  sign_id: string;
  display_name: string;
  confidence: number;
  meaning: string;
}

export interface RecognitionResult {
  status: "RECOGNIZED" | "UNCERTAIN" | "NO_HANDS" | "CONSENT_REQUIRED";
  sign_id?: string;
  display_name?: string;
  meaning?: string;
  english_text?: string;
  hindi_text?: string;
  confidence: number;
  is_stable: boolean;
  stability_count: number;
  rejection_reason?: string;
  candidates: RecognitionCandidate[];
  model_version: string;
}

export type WorkflowState =
  | "IDLE"
  | "CONSENT_REQUIRED"
  | "CAPTURING"
  | "RECOGNIZING"
  | "UNCERTAIN"
  | "TRANSCRIBING"
  | "TRANSLATING"
  | "AWAITING_CONFIRMATION"
  | "GENERATING_SPEECH"
  | "GENERATING_SIGN_OUTPUT"
  | "COMPLETED"
  | "FAILED";

export type WorkflowAction =
  | "REQUEST_CAMERA"
  | "GRANT_CONSENT"
  | "DENY_CONSENT"
  | "PROCESS_LANDMARKS"
  | "START_LISTENING"
  | "PROCESS_SPEECH"
  | "CONFIRM_TRANSCRIPT"
  | "TRIGGER_SPEECH"
  | "RESET"
  | "RETRY";

export interface OrchestratorEvent {
  timestamp: string;
  from_state: WorkflowState;
  to_state: WorkflowState;
  action: WorkflowAction;
  message: string;
  details?: Record<string, any>;
}

export interface OrchestratorContext {
  session_id: string;
  current_state: WorkflowState;
  consent_granted: boolean;
  active_route?: string;
  current_sign_id?: string;
  recognized_meaning?: string;
  english_text?: string;
  hindi_text?: string;
  transcript?: string;
  reverse_match_found: boolean;
  reverse_sign_media?: SignMedia;
  confidence?: number;
  last_error?: string;
  event_history: OrchestratorEvent[];
}

export interface TestRunRecord {
  id: number;
  test_id: string;
  name: string;
  input_description: string;
  expected_output: string;
  actual_output: string;
  status: "PASS" | "FAIL" | "BLOCKED";
  confidence?: number;
  model_version: string;
  evidence_ref?: string;
  notes?: string;
  created_at: string;
}

export interface AcceptanceTestSummary {
  total_runs: number;
  passed_count: number;
  failed_count: number;
  blocked_count: number;
  pass_rate_percent: number;
  test_cases: TestRunRecord[];
  verified_languages: string[];
  system_version: string;
}

export interface ReverseMatchResponse {
  matched: boolean;
  query_phrase: string;
  matched_sign?: SignItem;
  isl_grammar_note?: string;
  explanation: string;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  given_name?: string;
  family_name?: string;
  picture?: string;
  role: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
  message: string;
}

export interface AuthStatusResponse {
  authenticated: boolean;
  user?: UserProfile;
  google_client_id?: string;
}


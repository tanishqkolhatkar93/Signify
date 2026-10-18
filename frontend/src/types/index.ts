export interface SignMedia {
  type: string;
  asset_url: string;
  verified_clip_url?: string;
  description: string;
}

export interface SignItem {
  id: string;
  display_name: string;
  sign_language: string;
  category: string;
  is_dynamic: boolean;
  validation_status: string;
  meaning: string;
  english_text: string;
  hindi_text: string;
  phonetic_transcription?: string;
  hand_configuration: string;
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
  explanation: string;
}

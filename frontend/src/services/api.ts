import type {
  SignManifest,
  SignItem,
  ReverseMatchResponse,
  RecognitionResult,
  HandLandmarks,
  OrchestratorContext,
  WorkflowAction,
  AcceptanceTestSummary,
  TestRunRecord,
  UserProfile,
  AuthResponse,
  AuthStatusResponse
} from "../types";

const API_BASE = "http://127.0.0.1:8000/api/v1";

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const token = localStorage.getItem("signify_auth_token");
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> || {})
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(url, {
      ...options,
      headers
    });
    if (!res.ok) {
      const errBody = await res.text();
      throw new Error(`API error ${res.status}: ${errBody}`);
    }
    return (await res.json()) as T;
  } catch (err: any) {
    console.error(`Request to ${endpoint} failed:`, err);
    throw err;
  }
}

export const api = {
  // Authentication
  getAuthStatus: () => request<AuthStatusResponse>("/auth/status"),
  loginGoogle: async (credential: string) => {
    const res = await request<AuthResponse>("/auth/google", {
      method: "POST",
      body: JSON.stringify({ credential })
    });
    if (res.access_token) {
      localStorage.setItem("signify_auth_token", res.access_token);
    }
    return res;
  },
  getCurrentUser: () => request<UserProfile>("/auth/me"),
  updateCalibration: (data: any) =>
    request<UserProfile>("/auth/profile", {
      method: "PATCH",
      body: JSON.stringify(data)
    }),
  saveConversation: (data: { transcript: string; title?: string; translation?: string; matched_sign_id?: string }) =>
    request<any>("/auth/conversations", {
      method: "POST",
      body: JSON.stringify(data)
    }),
  listConversations: () => request<any[]>("/auth/conversations"),
  deleteConversation: (id: string) =>
    request<any>(`/auth/conversations/${id}`, {
      method: "DELETE"
    }),
  logout: () => {
    localStorage.removeItem("signify_auth_token");
  },
  getToken: () => localStorage.getItem("signify_auth_token"),

  // Core Signify Services
  getHealth: () => request<any>("/health"),
  getManifest: () => request<SignManifest>("/signs/manifest"),
  listSigns: (category?: string, search?: string) => {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (search) params.set("search", search);
    const qs = params.toString() ? `?${params.toString()}` : "";
    return request<SignItem[]>(`/signs${qs}`);
  },
  getSignById: (id: string) => request<SignItem>(`/signs/${id}`),
  matchReversePhrase: (phrase: string) =>
    request<ReverseMatchResponse>("/signs/reverse-match", {
      method: "POST",
      body: JSON.stringify({ phrase })
    }),
  classifyLandmarks: (hands: HandLandmarks[], sessionId = "default-session", consentGranted = false) =>
    request<RecognitionResult>("/vision/classify", {
      method: "POST",
      body: JSON.stringify({
        hands,
        session_id: sessionId,
        consent_granted: consentGranted
      })
    }),
  transcribeSpeech: (params: { audioBase64?: string; language?: string; mockInputText?: string; sessionId?: string }) =>
    request<any>("/speech/transcribe", {
      method: "POST",
      body: JSON.stringify({
        audio_base64: params.audioBase64,
        language: params.language || "en",
        mock_input_text: params.mockInputText,
        session_id: params.sessionId || "default-session"
      })
    }),
  synthesizeSpeech: (text: string, language: "en" | "hi", sessionId = "default-session") =>
    request<any>("/speech/synthesize", {
      method: "POST",
      body: JSON.stringify({
        text,
        language,
        session_id: sessionId
      })
    }),
  translateText: (text: string, source_language: string, target_language: string) =>
    request<any>("/translation/translate", {
      method: "POST",
      body: JSON.stringify({
        text,
        source_language,
        target_language
      })
    }),
  orchestratorTransition: (action: WorkflowAction, payload: any = {}, sessionId = "default-session") =>
    request<OrchestratorContext>("/orchestrator/transition", {
      method: "POST",
      body: JSON.stringify({
        action,
        payload,
        session_id: sessionId
      })
    }),
  orchestratorReset: (sessionId = "default-session") =>
    request<OrchestratorContext>(`/orchestrator/reset?session_id=${sessionId}`, {
      method: "POST"
    }),
  getCoverageReport: () => request<any>("/signs/coverage-report"),
  importSigns: (signs: SignItem[], overwriteExisting = false) =>
    request<any>("/signs/import", {
      method: "POST",
      body: JSON.stringify({ signs, overwrite_existing: overwriteExisting })
    }),
  getAcceptanceSummary: () => request<AcceptanceTestSummary>("/tests/summary"),
  runAcceptanceTests: () => request<TestRunRecord[]>("/tests/run-all", { method: "POST" })
};

import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { ConsentModal } from "./components/ConsentModal";
import { SignToSpeechView } from "./components/SignToSpeechView";
import { SpeechView } from "./components/SpeechView";
import { SignDictionaryView } from "./components/SignDictionaryView";
import { TestEvidenceView } from "./components/TestEvidenceView";
import { api } from "./services/api";
import type { SignItem, SignManifest, UserProfile } from "./types";
import { ShieldCheck, Languages, Sparkles, BookOpen } from "lucide-react";
import "./App.css";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState("sign-to-speech");
  const [backendOnline, setBackendOnline] = useState(false);
  const [consentGranted, setConsentGranted] = useState(false);
  const [consentModalOpen, setConsentModalOpen] = useState(false);
  const [manifest, setManifest] = useState<SignManifest | null>(null);
  const [signs, setSigns] = useState<SignItem[]>([]);
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);

  // Initial health check and manifest loading
  useEffect(() => {
    const initApp = async () => {
      try {
        await api.getHealth();
        setBackendOnline(true);
        const manifestData = await api.getManifest();
        setManifest(manifestData);
        setSigns(manifestData.signs);
      } catch (err) {
        console.warn("Backend connection pending:", err);
        setBackendOnline(false);
      }
    };
    initApp();

    const interval = setInterval(initApp, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleGrantConsent = async () => {
    setConsentGranted(true);
    setConsentModalOpen(false);
    try {
      await api.orchestratorTransition(
        "GRANT_CONSENT",
        { user_id: currentUser?.id, user_email: currentUser?.email },
        "live-session"
      );
    } catch (e) {
      console.warn("Failed to notify backend of consent:", e);
    }
  };

  const handleDenyConsent = async () => {
    setConsentGranted(false);
    setConsentModalOpen(false);
    try {
      await api.orchestratorTransition(
        "DENY_CONSENT",
        { user_id: currentUser?.id, user_email: currentUser?.email },
        "live-session"
      );
    } catch (e) {
      console.warn("Failed to notify backend of consent denial:", e);
    }
  };

  return (
    <div className="app-layout">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendOnline={backendOnline}
        consentGranted={consentGranted}
        onRequestConsent={() => setConsentModalOpen(true)}
        currentUser={currentUser}
        onUserChange={setCurrentUser}
        signCount={signs.length || 28}
      />

      <div className="master-container max-w-7xl mx-auto px-6 py-6 w-full">
        <main className="main-content">
          {/* Hero Section */}
          <section className="hero-section">
            <div className="hero-content">
              <span className="hero-eyebrow">
                <span className="relative flex h-2 w-2 mr-0.5 inline-flex">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-teal-500"></span>
                </span>
                <Sparkles size={13} className="text-teal inline ml-1" />
                <span>Agentic AI Hackathon 2026 • VerbX / IvishAI PS 3</span>
              </span>
              <h1 className="hero-title">Communication Without Barriers.</h1>
              <p className="hero-subtitle">
                Signify bridges deaf and hearing communicators through an intelligent, uncertainty-aware assistant connecting verified <strong>Indian Sign Language (ISL)</strong> with multilingual speech and text in both directions.
              </p>

              <div className="hero-highlights">
                <div className="hero-badge">
                  <Languages size={15} className="text-teal" />
                  <span>Bilingual Speech: English + Hindi</span>
                </div>
                <div className="hero-badge">
                  <ShieldCheck size={15} className="text-teal" />
                  <span>Zero Video Upload: 100% Local Landmark Processing</span>
                </div>
                <div className="hero-badge">
                  <BookOpen size={15} className="text-teal" />
                  <span>{signs.length || 28} Verified ISL Signs • ISLRTC Grounded</span>
                </div>
              </div>
            </div>
          </section>

          {/* Tab Views */}
          <div className="view-wrapper">
            {activeTab === "sign-to-speech" && (
              <SignToSpeechView
                consentGranted={consentGranted}
                onRequestConsent={() => setConsentModalOpen(true)}
                signs={signs}
                currentUser={currentUser}
              />
            )}

            {activeTab === "speech-route" && <SpeechView currentUser={currentUser} />}

            {activeTab === "dictionary" && (
              <SignDictionaryView
                manifest={manifest}
                signs={signs}
                currentUser={currentUser}
                onSignImported={async () => {
                  const refreshed = await api.getManifest();
                  setManifest(refreshed);
                  setSigns(refreshed.signs);
                }}
              />
            )}

            {activeTab === "test-evidence" && <TestEvidenceView />}
          </div>
        </main>
      </div>

      {/* Consent Modal Gate */}
      <ConsentModal
        isOpen={consentModalOpen}
        onGrant={handleGrantConsent}
        onDeny={handleDenyConsent}
      />

      <footer className="site-footer">
        <div className="footer-container max-w-7xl mx-auto px-6">
          <p>
            <strong>Signify</strong> • AI Sign-Language Communication System. Designed for Agentic AI Hackathon 2026 powered by Ziro.Digital.
          </p>
          <p className="text-xs text-muted">
            Linguistic Grounding: Indian Sign Language (ISL) Standard Dictionary (ISLRTC) • Audio/Translation: VerbX / Vocaline Architecture.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;

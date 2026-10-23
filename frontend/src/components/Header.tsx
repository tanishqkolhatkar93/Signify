import React, { useState, useEffect } from "react";
import { ShieldAlert, Video, Mic, BookOpen, CheckCircle2, Sun, Moon } from "lucide-react";
import type { UserProfile } from "../types";
import { GoogleAuthButton } from "./GoogleAuthButton";

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  backendOnline: boolean;
  consentGranted: boolean;
  onRequestConsent?: () => void;
  currentUser: UserProfile | null;
  onUserChange: (user: UserProfile | null) => void;
  signCount?: number;
  selectedLanguage: "ISL" | "EN" | "HI";
  onLanguageChange: (lang: "ISL" | "EN" | "HI") => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  backendOnline,
  consentGranted,
  onRequestConsent,
  currentUser,
  onUserChange,
  signCount = 28,
  selectedLanguage,
  onLanguageChange
}) => {
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    const saved = localStorage.getItem("signify-theme");
    return (saved === "light" || saved === "dark") ? saved : "dark";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("signify-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  return (
    <header className="site-header">
      {/* 1. TOP NAVIGATION / HEADER (Single Horizontal Bar) */}
      <div className="header-top-bar">
        <div className="header-top-inner">
          {/* LEFT SIDE */}
          <div className="brand-group">
            <div className="brand-badge">
              <span className="brand-symbol">◈</span>
            </div>
            <div className="brand-text">
              <h1 className="brand-title">Signify</h1>
              <p className="brand-subtitle">AI Sign-Language Communication • Indian Sign Language (ISL)</p>
            </div>
          </div>

          {/* RIGHT SIDE (Grouped together horizontally with gap-4) */}
          <div className="header-right-tools">
            {/* Status indicator badge */}
            <div className={`status-indicator-badge ${backendOnline ? "online" : "offline"}`}>
              <span className="relative flex h-2 w-2">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${backendOnline ? "bg-emerald-500" : "bg-amber-500"}`} />
                <span className={`relative inline-flex rounded-full h-2 w-2 ${backendOnline ? "bg-emerald-500" : "bg-amber-500"}`} />
              </span>
              <span className="status-text">{backendOnline ? "Backend Connected (FastAPI)" : "Connecting..."}</span>
            </div>

            {/* Language switch pill selector: [ ISL | EN | HI (हिंदी) ] */}
            <div className="language-selector-control" role="group" aria-label="Language selection">
              <button
                type="button"
                className={`lang-pill-btn ${selectedLanguage === "ISL" ? "active" : ""}`}
                onClick={() => onLanguageChange("ISL")}
                title="Indian Sign Language Mode (Visual & Grammar Grounding)"
              >
                ISL
              </button>
              <button
                type="button"
                className={`lang-pill-btn ${selectedLanguage === "EN" ? "active" : ""}`}
                onClick={() => onLanguageChange("EN")}
                title="English Spoken & Voice Synthesis Mode"
              >
                EN
              </button>
              <button
                type="button"
                className={`lang-pill-btn ${selectedLanguage === "HI" ? "active" : ""}`}
                onClick={() => onLanguageChange("HI")}
                title="Hindi (हिंदी) Spoken & Voice Synthesis Mode"
              >
                HI (हिंदी)
              </button>
            </div>

            {/* Light / Dark Mode Toggle */}
            <button
              type="button"
              className="theme-toggle-btn"
              onClick={toggleTheme}
              title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
              aria-label="Toggle Theme"
            >
              {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
            </button>

            {/* Google Authentication Component */}
            <GoogleAuthButton currentUser={currentUser} onUserChange={onUserChange} currentTheme={theme} />
          </div>
        </div>
      </div>

      {/* 2. CONSENT BANNER (Directly below header) */}
      {!consentGranted && (
        <div className="consent-notification-bar">
          <div className="consent-bar-inner">
            <div className="flex items-center gap-2.5">
              <div className="consent-beacon">
                <ShieldAlert size={14} className="text-amber-400" />
              </div>
              <span className="consent-message">
                <strong className="text-amber-700 dark:text-amber-300">Camera Consent Required:</strong> Real-time ISL recognition processes video 100% locally on your device. Zero frames are uploaded.
              </span>
            </div>
            {onRequestConsent && (
              <button
                type="button"
                className="consent-trigger-btn"
                onClick={onRequestConsent}
              >
                Enable Camera & Consent
              </button>
            )}
          </div>
        </div>
      )}

      {/* 3. TAB NAVIGATION (Horizontal Button Group / Bar) */}
      <div className="header-tabs-bar">
        <div className="header-tabs-inner">
          <nav className="nav-tabs-grid" aria-label="Main Navigation">
            <button
              type="button"
              className={`nav-tab-btn ${activeTab === "sign-to-speech" ? "active" : ""}`}
              onClick={() => setActiveTab("sign-to-speech")}
            >
              <Video size={16} className="tab-icon" />
              <span className="tab-label">Sign to Speech</span>
            </button>

            <button
              type="button"
              className={`nav-tab-btn ${activeTab === "speech-route" ? "active" : ""}`}
              onClick={() => setActiveTab("speech-route")}
            >
              <Mic size={16} className="tab-icon" />
              <span className="tab-label">Speech to Text & Sign</span>
            </button>

            <button
              type="button"
              className={`nav-tab-btn ${activeTab === "dictionary" ? "active" : ""}`}
              onClick={() => setActiveTab("dictionary")}
            >
              <BookOpen size={16} className="tab-icon" />
              <span className="tab-label">Sign Dictionary ({signCount} ISL Signs)</span>
            </button>

            <button
              type="button"
              className={`nav-tab-btn ${activeTab === "test-evidence" ? "active" : ""}`}
              onClick={() => setActiveTab("test-evidence")}
            >
              <CheckCircle2 size={16} className="tab-icon" />
              <span className="tab-label">Acceptance Test Studio (TC1–TC4)</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};

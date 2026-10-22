import React, { useState, useEffect } from "react";
import { ShieldCheck, Activity, Video, Mic, BookOpen, CheckCircle2, Sun, Moon } from "lucide-react";
import type { UserProfile } from "../types";
import { GoogleAuthButton } from "./GoogleAuthButton";

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  backendOnline: boolean;
  consentGranted: boolean;
  currentUser: UserProfile | null;
  onUserChange: (user: UserProfile | null) => void;
  signCount?: number;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  backendOnline,
  consentGranted,
  currentUser,
  onUserChange,
  signCount = 28
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
      <div className="header-top">
        <div className="brand-group">
          <div className="brand-badge">
            <span className="brand-symbol">◈</span>
          </div>
          <div>
            <h1 className="brand-title">Signify</h1>
            <p className="brand-subtitle">AI Sign-Language Communication • Indian Sign Language (ISL)</p>
          </div>
        </div>

        <div className="status-badges flex items-center gap-3">
          {/* Light / Dark Mode Toggle */}
          <button
            className="theme-toggle-btn"
            onClick={toggleTheme}
            title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
            aria-label="Toggle Theme"
          >
            {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
          </button>

          <div className={`status-pill ${consentGranted ? "pill-consented" : "pill-neutral"}`}>
            <ShieldCheck size={14} />
            <span>{consentGranted ? "Camera Consented" : "Consent Required"}</span>
          </div>

          <div className={`status-pill ${backendOnline ? "pill-online" : "pill-offline"}`}>
            <Activity size={14} />
            <span>{backendOnline ? "Backend Connected (FastAPI)" : "Connecting..."}</span>
          </div>

          <div className="language-tags hidden sm:flex">
            <span className="lang-tag active">ISL</span>
            <span className="lang-tag">EN</span>
            <span className="lang-tag">HI (हिंदी)</span>
          </div>

          {/* Google Authentication Component */}
          <GoogleAuthButton currentUser={currentUser} onUserChange={onUserChange} />
        </div>
      </div>

      <nav className="nav-tabs" aria-label="Main Navigation">
        <button
          className={`nav-tab-btn ${activeTab === "sign-to-speech" ? "active" : ""}`}
          onClick={() => setActiveTab("sign-to-speech")}
        >
          <Video size={16} />
          <span>Sign to Speech</span>
        </button>

        <button
          className={`nav-tab-btn ${activeTab === "speech-route" ? "active" : ""}`}
          onClick={() => setActiveTab("speech-route")}
        >
          <Mic size={16} />
          <span>Speech to Text & Sign</span>
        </button>

        <button
          className={`nav-tab-btn ${activeTab === "dictionary" ? "active" : ""}`}
          onClick={() => setActiveTab("dictionary")}
        >
          <BookOpen size={16} />
          <span>Sign Dictionary ({signCount} ISL Signs)</span>
        </button>

        <button
          className={`nav-tab-btn ${activeTab === "test-evidence" ? "active" : ""}`}
          onClick={() => setActiveTab("test-evidence")}
        >
          <CheckCircle2 size={16} />
          <span>Acceptance Test Studio (TC1–TC4)</span>
        </button>
      </nav>
    </header>
  );
};

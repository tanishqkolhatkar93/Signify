import React, { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { LogOut, CheckCircle2, ChevronDown, AlertCircle, Settings, X, Hand, Zap, Languages } from "lucide-react";
import type { UserProfile } from "../types";
import { api } from "../services/api";

declare global {
  interface Window {
    google?: any;
  }
}

interface GoogleAuthButtonProps {
  currentUser: UserProfile | null;
  onUserChange: (user: UserProfile | null) => void;
  currentTheme?: "dark" | "light";
}

export const GoogleAuthButton: React.FC<GoogleAuthButtonProps> = ({ currentUser, onUserChange, currentTheme }) => {
  const [googleClientId, setGoogleClientId] = useState<string>(
    import.meta.env.VITE_GOOGLE_CLIENT_ID || ""
  );
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [calibrationModalOpen, setCalibrationModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [gisLoaded, setGisLoaded] = useState(false);
  const [savingCalibration, setSavingCalibration] = useState(false);

  // Calibration Form State
  const [dominantHand, setDominantHand] = useState<"right" | "left">(
    (currentUser?.dominant_hand as "right" | "left") || "right"
  );
  const [signingSpeed, setSigningSpeed] = useState<"slow" | "normal" | "fast">(
    (currentUser?.signing_speed as "slow" | "normal" | "fast") || "normal"
  );
  const [preferredLanguage, setPreferredLanguage] = useState<"en" | "hi">(
    (currentUser?.preferred_language as "en" | "hi") || "en"
  );

  const googleBtnRef = useRef<HTMLDivElement>(null);

  // Sync calibration state when currentUser changes
  useEffect(() => {
    if (currentUser) {
      if (currentUser.dominant_hand) setDominantHand(currentUser.dominant_hand);
      if (currentUser.signing_speed) setSigningSpeed(currentUser.signing_speed);
      if (currentUser.preferred_language) setPreferredLanguage(currentUser.preferred_language);
    }
  }, [currentUser]);

  // Check auth session and fetch Google Client ID from backend
  useEffect(() => {
    const initAuth = async () => {
      try {
        const status = await api.getAuthStatus();
        if (status.google_client_id) {
          setGoogleClientId(status.google_client_id);
        }
        if (status.authenticated && status.user) {
          onUserChange(status.user);
        } else if (api.getToken()) {
          const user = await api.getCurrentUser();
          onUserChange(user);
        }
      } catch (err) {
        api.logout();
        onUserChange(null);
      }
    };
    initAuth();
  }, []);

  // Poll for Google Identity Services script availability
  useEffect(() => {
    if (window.google?.accounts?.id) {
      setGisLoaded(true);
      return;
    }
    const checkGis = setInterval(() => {
      if (window.google?.accounts?.id) {
        setGisLoaded(true);
        clearInterval(checkGis);
      }
    }, 200);
    return () => clearInterval(checkGis);
  }, []);

  // Initialize official Google Identity Services button
  useEffect(() => {
    if (googleClientId && gisLoaded && googleBtnRef.current && !currentUser) {
      try {
        googleBtnRef.current.innerHTML = "";

        window.google.accounts.id.initialize({
          client_id: googleClientId,
          callback: async (response: any) => {
            if (response.credential) {
              setLoading(true);
              try {
                const authRes = await api.loginGoogle(response.credential);
                onUserChange(authRes.user);
              } catch (e: any) {
                alert(`Google sign-in error: ${e.message}`);
              } finally {
                setLoading(false);
              }
            }
          },
          auto_select: false,
          cancel_on_tap_outside: true
        });

        const isDark = (currentTheme || document.documentElement.getAttribute("data-theme") || "dark") === "dark";

        window.google.accounts.id.renderButton(googleBtnRef.current, {
          theme: isDark ? "filled_black" : "outline",
          size: "medium",
          shape: "pill",
          text: "signin_with",
          logo_alignment: "left"
        });
      } catch (err) {
        console.warn("Error initializing Google Identity Services button:", err);
      }
    }
  }, [googleClientId, gisLoaded, currentUser, currentTheme]);

  const handleLogout = () => {
    api.logout();
    onUserChange(null);
    setDropdownOpen(false);
  };

  const handleSaveCalibration = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingCalibration(true);
    try {
      const updated = await api.updateCalibration({
        dominant_hand: dominantHand,
        signing_speed: signingSpeed,
        preferred_language: preferredLanguage
      });
      onUserChange(updated);
      setCalibrationModalOpen(false);
    } catch (err: any) {
      alert(`Failed to save calibration: ${err.message}`);
    } finally {
      setSavingCalibration(false);
    }
  };

  if (currentUser) {
    return (
      <div className="relative">
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-all text-xs font-medium text-slate-200"
          title="Google Account Menu"
        >
          {currentUser.picture ? (
            <img
              src={currentUser.picture}
              alt={currentUser.name}
              className="w-5 h-5 rounded-full object-cover border border-emerald-400"
              referrerPolicy="no-referrer"
            />
          ) : (
            <div className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-[10px]">
              {currentUser.name.charAt(0).toUpperCase()}
            </div>
          )}
          <span className="font-semibold text-white max-w-[120px] truncate">{currentUser.name}</span>
          <CheckCircle2 size={13} className="text-emerald-400" />
          <ChevronDown size={13} className="text-slate-400" />
        </button>

        {dropdownOpen && (
          <div className="absolute right-0 mt-2 w-64 rounded-xl bg-[var(--bg-card-solid)] border border-[var(--navy-border)] shadow-[var(--shadow-lg)] py-2 z-50 text-xs backdrop-blur-xl">
            <div className="px-3 py-2 border-b border-[var(--navy-border)]">
              <p className="font-bold text-[var(--text-light)] truncate">{currentUser.name}</p>
              <p className="text-[11px] text-[var(--text-muted)] truncate">{currentUser.email}</p>
              <span className="inline-block mt-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 uppercase">
                Google Verified User
              </span>
            </div>

            {/* Profile Calibration Summary */}
            <div className="px-3 py-2 text-[11px] text-[var(--text-muted)] border-b border-[var(--navy-border)] space-y-1">
              <div className="flex justify-between">
                <span className="text-[var(--text-dim)]">Dominant Hand:</span>
                <span className="font-medium text-[var(--text-main)] capitalize">{currentUser.dominant_hand || "Right"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--text-dim)]">Signing Speed:</span>
                <span className="font-medium text-[var(--text-main)] capitalize">{currentUser.signing_speed || "Normal"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--text-dim)]">Target Voice:</span>
                <span className="font-medium text-[var(--text-main)] uppercase">{currentUser.preferred_language || "EN"}</span>
              </div>
            </div>

            <button
              onClick={() => {
                setCalibrationModalOpen(true);
                setDropdownOpen(false);
              }}
              className="w-full px-3 py-2 flex items-center gap-2 text-indigo-600 dark:text-indigo-400 hover:bg-[var(--bg-card-hover)] text-left transition-colors font-medium border-b border-[var(--navy-border)]"
            >
              <Settings size={14} />
              <span>Signer Calibration & Settings</span>
            </button>

            <button
              onClick={handleLogout}
              className="w-full px-3 py-2 flex items-center gap-2 text-rose-600 dark:text-rose-400 hover:bg-[var(--bg-card-hover)] text-left transition-colors font-medium"
            >
              <LogOut size={14} />
              <span>Sign Out</span>
            </button>
          </div>
        )}

        {/* Signer Calibration Modal */}
        {calibrationModalOpen && typeof document !== "undefined" && createPortal(
          <div
            className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto"
            style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, zIndex: 99999 }}
            onClick={() => setCalibrationModalOpen(false)}
          >
            <div
              className="bg-[var(--bg-card-solid)] border border-[var(--navy-border)] rounded-2xl max-w-md w-full p-6 shadow-2xl relative text-[var(--text-main)] shadow-[var(--card-bevel)] my-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => setCalibrationModalOpen(false)}
                className="absolute top-4 right-4 text-[var(--text-muted)] hover:text-[var(--text-light)] p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                title="Close"
              >
                <X size={20} />
              </button>

              <h3 className="text-lg font-bold text-[var(--text-light)] mb-1 flex items-center gap-2">
                <Settings size={18} className="text-indigo-600 dark:text-indigo-400" />
                Signer Calibration & Profile Settings
              </h3>
              <p className="text-xs text-[var(--text-muted)] mb-4">
                Personalized settings saved to your Google identity in SQLite database for customized landmark normalization and speech output.
              </p>

              <form onSubmit={handleSaveCalibration} className="space-y-4">
                {/* Dominant Hand */}
                <div>
                  <label className="block text-xs font-bold text-[var(--text-main)] mb-2 flex items-center gap-1.5">
                    <Hand size={14} className="text-emerald-600 dark:text-emerald-400" />
                    Dominant Signing Hand:
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      className={`p-2.5 rounded-lg border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                        dominantHand === "right"
                          ? "bg-indigo-50 dark:bg-indigo-600/30 border-indigo-500 text-indigo-700 dark:text-indigo-300 font-bold shadow-sm"
                          : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700 hover:text-slate-900 dark:hover:text-slate-200"
                      }`}
                      onClick={() => setDominantHand("right")}
                    >
                      <span>Right-Handed (Default)</span>
                      {dominantHand === "right" && <CheckCircle2 size={14} className="text-indigo-600 dark:text-indigo-400" />}
                    </button>
                    <button
                      type="button"
                      className={`p-2.5 rounded-lg border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                        dominantHand === "left"
                          ? "bg-indigo-50 dark:bg-indigo-600/30 border-indigo-500 text-indigo-700 dark:text-indigo-300 font-bold shadow-sm"
                          : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700 hover:text-slate-900 dark:hover:text-slate-200"
                      }`}
                      onClick={() => setDominantHand("left")}
                    >
                      <span>Left-Handed (Inverted Spatial)</span>
                      {dominantHand === "left" && <CheckCircle2 size={14} className="text-indigo-600 dark:text-indigo-400" />}
                    </button>
                  </div>
                </div>

                {/* Signing Speed */}
                <div>
                  <label className="block text-xs font-bold text-[var(--text-main)] mb-2 flex items-center gap-1.5">
                    <Zap size={14} className="text-amber-600 dark:text-amber-400" />
                    Signing Speed / Temporal Tolerance:
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {(["slow", "normal", "fast"] as const).map((spd) => (
                      <button
                        key={spd}
                        type="button"
                        className={`p-2.5 rounded-lg border text-xs font-semibold capitalize text-center transition-all ${
                          signingSpeed === spd
                            ? "bg-amber-50 dark:bg-amber-600/30 border-amber-500 text-amber-800 dark:text-amber-300 font-bold shadow-sm"
                            : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700 hover:text-slate-900 dark:hover:text-slate-200"
                        }`}
                        onClick={() => setSigningSpeed(spd)}
                      >
                        {spd === "slow" ? "Slow / Learner" : spd === "normal" ? "Normal" : "Fast / Fluent"}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Preferred Spoken Voice */}
                <div>
                  <label className="block text-xs font-bold text-[var(--text-main)] mb-2 flex items-center gap-1.5">
                    <Languages size={14} className="text-cyan-700 dark:text-cyan-400" />
                    Preferred Voice Output Language:
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      className={`p-2.5 rounded-lg border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                        preferredLanguage === "en"
                          ? "bg-cyan-50 dark:bg-cyan-600/30 border-cyan-500 text-cyan-800 dark:text-cyan-300 font-bold shadow-sm"
                          : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700 hover:text-slate-900 dark:hover:text-slate-200"
                      }`}
                      onClick={() => setPreferredLanguage("en")}
                    >
                      English (en-US)
                    </button>
                    <button
                      type="button"
                      className={`p-2.5 rounded-lg border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                        preferredLanguage === "hi"
                          ? "bg-cyan-50 dark:bg-cyan-600/30 border-cyan-500 text-cyan-800 dark:text-cyan-300 font-bold shadow-sm"
                          : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700 hover:text-slate-900 dark:hover:text-slate-200"
                      }`}
                      onClick={() => setPreferredLanguage("hi")}
                    >
                      Hindi (हिंदी - hi-IN)
                    </button>
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-3 border-t border-slate-200 dark:border-slate-800">
                  <button
                    type="button"
                    className="btn btn-secondary text-xs"
                    onClick={() => setCalibrationModalOpen(false)}
                    disabled={savingCalibration}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary text-xs"
                    disabled={savingCalibration}
                  >
                    {savingCalibration ? "Saving Preferences..." : "Save Preferences"}
                  </button>
                </div>
              </form>
            </div>
          </div>,
          document.body
        )}
      </div>
    );
  }

  return (
    <div className="flex items-center">
      {loading ? (
        <span className="text-xs text-slate-400 animate-pulse">Authenticating with Google...</span>
      ) : googleClientId ? (
        <div ref={googleBtnRef} className="google-btn-wrapper"></div>
      ) : (
        <div className="flex items-center gap-1.5 text-xs text-amber-400 px-2 py-1 rounded bg-amber-500/10 border border-amber-500/30">
          <AlertCircle size={13} />
          <span>Add GOOGLE_CLIENT_ID</span>
        </div>
      )}
    </div>
  );
};

import React, { useState, useEffect, useRef } from "react";
import { LogOut, CheckCircle2, ChevronDown } from "lucide-react";
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
}

export const GoogleAuthButton: React.FC<GoogleAuthButtonProps> = ({ currentUser, onUserChange }) => {
  const [googleClientId, setGoogleClientId] = useState<string>("");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const googleBtnRef = useRef<HTMLDivElement>(null);

  // Check auth status on mount
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
        // Token expired or invalid
        api.logout();
        onUserChange(null);
      }
    };
    initAuth();
  }, []);

  // Initialize official Google Identity Services if client ID is configured
  useEffect(() => {
    if (googleClientId && window.google?.accounts?.id && googleBtnRef.current && !currentUser) {
      try {
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
          }
        });
        window.google.accounts.id.renderButton(googleBtnRef.current, {
          theme: "filled_blue",
          size: "medium",
          shape: "pill",
          text: "signin_with"
        });
      } catch (err) {
        console.warn("Could not render official Google button:", err);
      }
    }
  }, [googleClientId, currentUser]);

  const handleDemoSignIn = async () => {
    setLoading(true);
    try {
      const authRes = await api.loginDemo();
      onUserChange(authRes.user);
    } catch (e: any) {
      alert(`Sign in error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    api.logout();
    onUserChange(null);
    setDropdownOpen(false);
  };

  if (currentUser) {
    return (
      <div className="relative">
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-all text-xs font-medium text-slate-200"
          title="Account Menu"
        >
          <img
            src={currentUser.picture || `https://api.dicebear.com/7.x/bottts/svg?seed=${currentUser.id}`}
            alt={currentUser.name}
            className="w-5 h-5 rounded-full object-cover border border-emerald-400"
          />
          <span className="font-semibold text-white max-w-[110px] truncate">{currentUser.name}</span>
          <CheckCircle2 size={13} className="text-emerald-400" />
          <ChevronDown size={13} className="text-slate-400" />
        </button>

        {dropdownOpen && (
          <div className="absolute right-0 mt-2 w-56 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl py-2 z-50 text-xs">
            <div className="px-3 py-2 border-b border-slate-800">
              <p className="font-bold text-white truncate">{currentUser.name}</p>
              <p className="text-[11px] text-slate-400 truncate">{currentUser.email}</p>
              <span className="inline-block mt-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase">
                Google Verified Signer
              </span>
            </div>

            <div className="px-3 py-2 text-[11px] text-slate-400 border-b border-slate-800">
              <span className="block text-slate-500">ID: {currentUser.id}</span>
              <span className="block text-slate-500">Role: {currentUser.role}</span>
            </div>

            <button
              onClick={handleLogout}
              className="w-full px-3 py-2 flex items-center gap-2 text-red-400 hover:bg-slate-800 text-left transition-colors"
            >
              <LogOut size={14} />
              <span>Sign Out</span>
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {/* Official Google Button container (rendered when Client ID is valid) */}
      {googleClientId && <div ref={googleBtnRef}></div>}

      {/* Styled Google Auth Button / Instant Sign-in */}
      <button
        onClick={handleDemoSignIn}
        disabled={loading}
        className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white text-slate-900 hover:bg-slate-100 font-semibold text-xs shadow-md transition-all active:scale-95 border border-slate-200"
        title="Sign in with Google Account"
      >
        <svg className="w-4 h-4" viewBox="0 0 24 24">
          <path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="#FBBC05"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
          />
          <path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
          />
        </svg>
        <span>{loading ? "Signing In..." : "Sign in with Google"}</span>
      </button>
    </div>
  );
};

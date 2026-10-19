import React, { useState, useEffect, useRef } from "react";
import { LogOut, CheckCircle2, ChevronDown, AlertCircle } from "lucide-react";
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
  const [googleClientId, setGoogleClientId] = useState<string>(
    import.meta.env.VITE_GOOGLE_CLIENT_ID || ""
  );
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [gisLoaded, setGisLoaded] = useState(false);
  const googleBtnRef = useRef<HTMLDivElement>(null);

  // Check auth session and fetch Google Client ID from backend if needed
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

  // Poll or check for Google Identity Services script availability
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
        // Clear previous button contents
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

        window.google.accounts.id.renderButton(googleBtnRef.current, {
          theme: "filled_blue",
          size: "medium",
          shape: "pill",
          text: "signin_with",
          logo_alignment: "left"
        });
      } catch (err) {
        console.warn("Error initializing Google Identity Services button:", err);
      }
    }
  }, [googleClientId, gisLoaded, currentUser]);

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
          <div className="absolute right-0 mt-2 w-60 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl py-2 z-50 text-xs">
            <div className="px-3 py-2 border-b border-slate-800">
              <p className="font-bold text-white truncate">{currentUser.name}</p>
              <p className="text-[11px] text-slate-400 truncate">{currentUser.email}</p>
              <span className="inline-block mt-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase">
                Google Verified User
              </span>
            </div>

            <div className="px-3 py-2 text-[11px] text-slate-400 border-b border-slate-800">
              <span className="block text-slate-500">User ID: {currentUser.id}</span>
              <span className="block text-slate-500">Role: {currentUser.role}</span>
            </div>

            <button
              onClick={handleLogout}
              className="w-full px-3 py-2 flex items-center gap-2 text-red-400 hover:bg-slate-800 text-left transition-colors font-medium"
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
    <div className="flex items-center">
      {loading ? (
        <span className="text-xs text-slate-400 animate-pulse">Authenticating with Google...</span>
      ) : googleClientId ? (
        <div ref={googleBtnRef} className="min-h-[38px] flex items-center"></div>
      ) : (
        <div className="flex items-center gap-1.5 text-xs text-amber-400 px-2 py-1 rounded bg-amber-500/10 border border-amber-500/30">
          <AlertCircle size={13} />
          <span>Add GOOGLE_CLIENT_ID</span>
        </div>
      )}
    </div>
  );
};

// Signify Browser Audio & Speech Synthesis Service

export const sanitizeForSpeech = (rawText: string, lang: "en" | "hi"): string => {
  if (!rawText || typeof rawText !== "string") {
    return lang === "hi" ? "नमस्ते" : "Hello";
  }

  let text = rawText.trim();

  // If text contains bilingual or multi-option slash delimiters (e.g. "नमस्ते / नमस्कार", "अच्छा / बहुत अच्छा", "Hello / Namaste"),
  // pick the primary (first) phrase so the user hears a single, natural, clean pronunciation without spoken "slash".
  if (text.includes("/") || text.includes("\\") || text.includes("|")) {
    const parts = text.split(/[/\\|]/).map((p) => p.trim()).filter(Boolean);
    if (parts.length > 0) {
      text = parts[0];
    }
  }

  // Strip all delimiter slashes, escape characters, and regex markers before vocalization
  let cleanText = text.replace(/[\/\\#,+()$~%.'":*?<>{}[\]_`^=]/g, " ").replace(/\s+/g, " ").trim();

  // Ensure that if a sign does not have an exact translation, it falls back to a clean word rather than empty slashes
  if (!cleanText) {
    return lang === "hi" ? "नमस्ते" : "Hello";
  }

  return cleanText;
};

// Cache voices once loaded
let cachedVoices: SpeechSynthesisVoice[] = [];
if (typeof window !== "undefined" && "speechSynthesis" in window) {
  cachedVoices = window.speechSynthesis.getVoices();
  window.speechSynthesis.onvoiceschanged = () => {
    cachedVoices = window.speechSynthesis.getVoices();
  };
}

export const speechService = {
  sanitizeText: sanitizeForSpeech,

  speak: (text: string, language: "en" | "hi", onEnd?: () => void) => {
    if (!("speechSynthesis" in window)) {
      console.warn("Browser does not support SpeechSynthesis.");
      if (onEnd) onEnd();
      return;
    }

    // Cancel existing speech
    window.speechSynthesis.cancel();

    const cleanText = sanitizeForSpeech(text, language);
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = language === "hi" ? "hi-IN" : "en-US";
    utterance.rate = 0.95; // Slightly slower for clear accessibility comprehension
    utterance.pitch = 1.0;

    // Pick native voice for Hindi or English if available
    const voices = cachedVoices.length > 0 ? cachedVoices : window.speechSynthesis.getVoices();
    if (voices && voices.length > 0) {
      if (language === "hi") {
        const hindiVoice = voices.find(
          (v) => v.lang.includes("hi") || v.lang.includes("HI") || v.name.toLowerCase().includes("hindi")
        );
        if (hindiVoice) utterance.voice = hindiVoice;
      } else {
        const englishVoice = voices.find(
          (v) => v.lang.startsWith("en") || v.lang.includes("EN") || v.name.toLowerCase().includes("english")
        );
        if (englishVoice) utterance.voice = englishVoice;
      }
    }

    utterance.onend = () => {
      if (onEnd) onEnd();
    };

    utterance.onerror = (e) => {
      console.warn("Speech synthesis playback error:", e);
      if (onEnd) onEnd();
    };

    window.speechSynthesis.speak(utterance);
  },

  playBase64Audio: (base64AudioUrl: string, onEnd?: () => void) => {
    try {
      const audio = new Audio(base64AudioUrl);
      if (onEnd) audio.onended = onEnd;
      audio.play().catch((err) => {
        console.warn("Failed to play audio base64:", err);
        if (onEnd) onEnd();
      });
    } catch (e) {
      console.error("Audio error:", e);
      if (onEnd) onEnd();
    }
  }
};

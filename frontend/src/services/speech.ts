// Disignum Browser Audio & Speech Synthesis Service

export const speechService = {
  speak: (text: string, language: "en" | "hi", onEnd?: () => void) => {
    if (!("speechSynthesis" in window)) {
      console.warn("Browser does not support SpeechSynthesis.");
      if (onEnd) onEnd();
      return;
    }

    // Cancel existing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === "hi" ? "hi-IN" : "en-US";
    utterance.rate = 0.95; // Slightly slower for clear accessibility comprehension
    utterance.pitch = 1.0;

    // Attempt to pick native voice for Hindi or English if available
    const voices = window.speechSynthesis.getVoices();
    if (voices && voices.length > 0) {
      const match = voices.find((v) =>
        language === "hi"
          ? v.lang.startsWith("hi") || v.name.toLowerCase().includes("hindi")
          : v.lang.startsWith("en")
      );
      if (match) utterance.voice = match;
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

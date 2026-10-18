import React, { useState } from "react";
import { Search, Volume2, ShieldCheck, AlertTriangle } from "lucide-react";
import type { SignItem, SignManifest } from "../types";
import { speechService } from "../services/speech";

interface SignDictionaryViewProps {
  manifest: SignManifest | null;
  signs: SignItem[];
}

export const SignDictionaryView: React.FC<SignDictionaryViewProps> = ({ manifest, signs }) => {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  const categories = ["all", ...Array.from(new Set(signs.map((s) => s.category)))];

  const filteredSigns = signs.filter((s) => {
    const matchesCat = selectedCategory === "all" || s.category.toLowerCase() === selectedCategory.toLowerCase();
    const q = search.toLowerCase();
    const matchesSearch =
      !q ||
      s.display_name.toLowerCase().includes(q) ||
      s.meaning.toLowerCase().includes(q) ||
      s.english_text.toLowerCase().includes(q) ||
      s.hindi_text.toLowerCase().includes(q);
    return matchesCat && matchesSearch;
  });

  const speak = (text: string, lang: "en" | "hi") => {
    speechService.speak(text, lang);
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Supported Sign Dictionary</h2>
          <p className="view-description">
            Documented baseline vocabulary for <strong>{manifest?.sign_language || "Indian Sign Language (ISL)"}</strong>.
          </p>
        </div>

        <div className="disclaimer-pill">
          <AlertTriangle size={15} />
          <span>Curated Bounded Vocabulary (12 Signs)</span>
        </div>
      </div>

      {/* Vocabulary Boundary Disclaimer Banner */}
      <div className="alert alert-info">
        <ShieldCheck size={18} />
        <div>
          <strong>Linguistic Integrity Disclosure:</strong>
          <p>{manifest?.disclaimer || "This is a curated, verified baseline vocabulary for essential communication and demonstration. It does not represent full grammatical Indian Sign Language fluency."}</p>
          <span className="text-xs text-muted">
            Primary Attribution: {manifest?.data_attribution?.primary_reference} • License: {manifest?.data_attribution?.license}
          </span>
        </div>
      </div>

      {/* Search and Category Filters */}
      <div className="filter-bar">
        <div className="search-input-box">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search by sign, English, Hindi, or meaning..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="category-chips">
          {categories.map((cat) => (
            <button
              key={cat}
              className={`cat-chip ${selectedCategory === cat ? "active" : ""}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat === "all" ? "All Categories" : cat}
            </button>
          ))}
        </div>
      </div>

      {/* Signs Grid */}
      <div className="signs-grid">
        {filteredSigns.map((sign) => (
          <div key={sign.id} className="card sign-card">
            <div className="sign-card-media">
              <img
                src={sign.media.asset_url}
                alt={sign.display_name}
                className="sign-thumbnail"
              />
              <span className="category-badge">{sign.category}</span>
            </div>

            <div className="sign-card-body">
              <div className="sign-card-title-row">
                <h4 className="sign-card-name">{sign.display_name}</h4>
                <span className="status-indicator-badge">{sign.validation_status}</span>
              </div>

              <p className="sign-card-meaning">{sign.meaning}</p>

              <div className="bilingual-pair-box">
                <div className="lang-output-row">
                  <span className="lang-label">English:</span>
                  <span className="lang-val">{sign.english_text}</span>
                  <button
                    className="speak-mini-btn"
                    onClick={() => speak(sign.english_text, "en")}
                    title="Speak English"
                  >
                    <Volume2 size={13} />
                  </button>
                </div>

                <div className="lang-output-row">
                  <span className="lang-label">Hindi:</span>
                  <span className="lang-val">{sign.hindi_text}</span>
                  <button
                    className="speak-mini-btn"
                    onClick={() => speak(sign.hindi_text, "hi")}
                    title="Speak Hindi"
                  >
                    <Volume2 size={13} />
                  </button>
                </div>
              </div>

              <div className="hand-config-box">
                <span className="text-xs font-bold text-muted">HAND FORM:</span>
                <p className="text-xs">{sign.hand_configuration}</p>
              </div>

              <div className="card-source-footer">
                <span>{sign.source}</span>
                <span>{sign.license}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

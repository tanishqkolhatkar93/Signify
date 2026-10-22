import React, { useState } from "react";
import { Search, Volume2, ShieldCheck, BookOpen, PlusCircle, CheckCircle2, X, User, Info, Maximize2 } from "lucide-react";
import type { SignItem, SignManifest, UserProfile } from "../types";
import { speechService } from "../services/speech";
import { api } from "../services/api";

interface SignDictionaryViewProps {
  manifest: SignManifest | null;
  signs: SignItem[];
  currentUser?: UserProfile | null;
  onSignImported?: () => void;
}

const renderSyntaxWithHighlights = (text: string) => {
  if (!text) return null;
  const parts = text.split(/(\([^)]+\)|\[[^\]]+\])/g);
  return (
    <>
      {parts.map((part, i) => {
        if ((part.startsWith("(") && part.endsWith(")")) || (part.startsWith("[") && part.endsWith("]"))) {
          return (
            <span key={i} className="isl-syntax-highlight">
              {part}
            </span>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
};

export const SignDictionaryView: React.FC<SignDictionaryViewProps> = ({ manifest, signs, currentUser, onSignImported }) => {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedType, setSelectedType] = useState("all");
  const [showImportModal, setShowImportModal] = useState(false);
  const [selectedSignForModal, setSelectedSignForModal] = useState<SignItem | null>(null);
  const [importJson, setImportJson] = useState("");
  const [importStatus, setImportStatus] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const categories = ["all", ...Array.from(new Set(signs.map((s) => s.category)))];
  const types = ["all", "word", "phrase", "number", "fingerspelling"];

  const filteredSigns = signs.filter((s) => {
    const matchesCat = selectedCategory === "all" || s.category.toLowerCase() === selectedCategory.toLowerCase();
    const matchesType = selectedType === "all" || (s.sign_type || "word").toLowerCase() === selectedType.toLowerCase();
    const q = search.toLowerCase();
    const matchesSearch =
      !q ||
      s.display_name.toLowerCase().includes(q) ||
      s.meaning.toLowerCase().includes(q) ||
      s.english_text.toLowerCase().includes(q) ||
      s.hindi_text.toLowerCase().includes(q) ||
      (s.canonical_phrase && s.canonical_phrase.toLowerCase().includes(q)) ||
      (s.isl_grammar_structure && s.isl_grammar_structure.toLowerCase().includes(q));
    return matchesCat && matchesType && matchesSearch;
  });

  const speak = (text: string, lang: "en" | "hi") => {
    speechService.speak(text, lang);
  };

  const handleImportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setImportStatus(null);
    try {
      const parsed = JSON.parse(importJson);
      const signArray = Array.isArray(parsed) ? parsed : [parsed];
      const res = await api.importSigns(signArray, true);
      setImportStatus(`Success: ${res.imported_count} imported, ${res.updated_count} updated.`);
      if (onSignImported) onSignImported();
      setTimeout(() => {
        setShowImportModal(false);
        setImportStatus(null);
        setImportJson("");
      }, 1800);
    } catch (err: any) {
      setImportStatus(`Import Error: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
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

        <div className="flex items-center gap-3">
          <div className="disclaimer-pill">
            <BookOpen size={15} />
            <span>Curated Bounded Vocabulary ({signs.length} Signs)</span>
          </div>
          <button
            className="btn btn-secondary flex items-center gap-2 text-sm"
            onClick={() => {
              if (!currentUser) {
                alert("Please sign in with Google to contribute verified ISL vocabulary entries.");
                return;
              }
              setShowImportModal(true);
            }}
            title="Import reviewed sign vocabulary without modifying code"
          >
            <PlusCircle size={15} />
            <span>Import Entry</span>
          </button>
        </div>
      </div>

      {/* Linguistic Integrity Disclaimer */}
      <div className="alert alert-info">
        <ShieldCheck size={18} />
        <div>
          <strong>Linguistic Integrity & Grammar Disclosure:</strong>
          <p>
            {manifest?.disclaimer ||
              "Indian Sign Language (ISL) employs independent syntactic structure (Topic-Comment order, Wh-question markers sentence-finally) and does not mirror spoken word-order. Reverse matching only presents authenticated ISLRTC signs."}
          </p>
          <span className="text-xs text-muted">
            Primary Attribution: {manifest?.data_attribution?.primary_source || "ISLRTC"} • License: {manifest?.data_attribution?.license || "CC-BY-4.0"}
          </span>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="filter-bar">
        <div className="search-input-box">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search by sign, English, Hindi, meaning, or ISL grammar..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
        </div>

        {/* Type Filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-muted uppercase">Type:</span>
          <div className="category-chips">
            {types.map((t) => (
              <button
                key={t}
                className={`cat-chip ${selectedType === t ? "active" : ""}`}
                onClick={() => setSelectedType(t)}
              >
                {t === "all" ? "All Types" : t.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Category Chips */}
        <div className="category-chips flex-wrap">
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
            <div
              className="sign-card-media group cursor-pointer relative"
              onClick={() => setSelectedSignForModal(sign)}
              title="Click to view full anatomical handshape guide"
            >
              <img
                src={sign.media.asset_url}
                alt={sign.display_name}
                className="sign-thumbnail transition-transform duration-300 group-hover:scale-105"
                loading="lazy"
              />
              <div className="absolute top-2 left-2 flex gap-1">
                <span className="category-badge">{sign.category}</span>
                {sign.sign_type && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold tracking-wider uppercase bg-slate-900/80 text-emerald-300 border border-emerald-500/30">
                    {sign.sign_type}
                  </span>
                )}
              </div>
              <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900/90 text-teal-300 border border-teal-500/40 rounded p-1.5 flex items-center gap-1 text-[11px] font-bold shadow-lg">
                <Maximize2 size={12} />
                <span>Enlarge Guide</span>
              </div>
            </div>

            <div className="sign-card-body">
              <div className="sign-card-title-row">
                <h4 className="sign-card-name">{sign.display_name}</h4>
                <span className="status-indicator-badge flex items-center gap-1">
                  <CheckCircle2 size={12} className="text-emerald-400" />
                  {sign.validation_status}
                </span>
              </div>

              <p className="sign-card-meaning">{sign.meaning}</p>

              {/* ISL Grammar Structure Note - High-Contrast Aesthetic Badge */}
              {sign.isl_grammar_structure && (
                <div className="isl-syntax-badge">
                  <div className="isl-syntax-header">
                    <span className="isl-syntax-tag">
                      <BookOpen size={11} />
                      ISL Syntax
                    </span>
                    <span className="isl-syntax-category-pill">Grammar Rule</span>
                  </div>
                  <p className="isl-syntax-text">
                    {renderSyntaxWithHighlights(sign.isl_grammar_structure)}
                  </p>
                </div>
              )}

              {/* Cultural / Linguistic Note */}
              {sign.cultural_linguistic_notes && (
                <div className="isl-linguistic-note">
                  <Info size={12} className="text-slate-400 shrink-0 mt-0.5" />
                  <span>
                    <strong>Note:</strong> {sign.cultural_linguistic_notes}
                  </span>
                </div>
              )}

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

              {/* Anatomical Gesture Breakdown Box for Common People */}
              <div className="hand-config-box">
                <div className="hand-config-header">
                  <span>🖐️ HOW TO PERFORM WITH HANDS:</span>
                </div>
                <p>{sign.hand_configuration}</p>
              </div>

              <div className="card-source-footer">
                <span title={sign.source}>{sign.source}</span>
                {sign.contributed_by && (
                  <span className="text-indigo-400 font-mono text-[10px]" title={`Contributed by ${sign.contributed_by}`}>
                    by {sign.contributed_by}
                  </span>
                )}
                <span>{sign.license}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Zero-Code Vocabulary Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-lg w-full p-6 shadow-2xl relative">
            <button
              onClick={() => setShowImportModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X size={20} />
            </button>
            <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
              <PlusCircle size={18} className="text-emerald-400" />
              Import Reviewed Vocabulary Entry
            </h3>
            <p className="text-xs text-slate-400 mb-3">
              Paste a validated ISL sign specification in JSON format to dynamically register it into the SQLite dictionary database without modifying code.
            </p>

            {currentUser && (
              <div className="flex items-center gap-2 mb-4 px-3 py-2 bg-indigo-950/40 border border-indigo-500/30 rounded text-xs text-indigo-300">
                <User size={14} className="text-indigo-400" />
                <span>Authenticated Contributor: <strong>{currentUser.name}</strong> ({currentUser.email})</span>
              </div>
            )}

            <form onSubmit={handleImportSubmit}>
              <textarea
                rows={10}
                className="w-full font-mono text-xs bg-slate-950 border border-slate-800 rounded p-3 text-slate-200 focus:outline-none focus:border-indigo-500 mb-4"
                placeholder={`{
  "id": "isl_custom_greeting",
  "display_name": "Welcome",
  "category": "Greetings",
  "sign_type": "word",
  "meaning": "Friendly welcoming gesture",
  "english_text": "Welcome",
  "hindi_text": "स्वागत है",
  "hand_configuration": "Both open palms sweeping toward chest",
  "isl_grammar_structure": "Topic-Comment lexical sign",
  "media": {
    "type": "svg_illustration",
    "asset_url": "/assets/signs/isl_namaste_hello.svg",
    "description": "Welcoming gesture"
  },
  "source": "ISLRTC Supplementary",
  "license": "CC-BY-4.0"
}`}
                value={importJson}
                onChange={(e) => setImportJson(e.target.value)}
                required
              />

              {importStatus && (
                <div
                  className={`p-3 rounded text-xs mb-3 ${
                    importStatus.startsWith("Success")
                      ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                      : "bg-red-500/20 text-red-300 border border-red-500/40"
                  }`}
                >
                  {importStatus}
                </div>
              )}

              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  className="btn btn-secondary text-sm"
                  onClick={() => setShowImportModal(false)}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary text-sm"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Importing..." : "Validate & Save"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Anatomical Sign Detail Modal (High-Res Illustration & Finger Breakdown) */}
      {selectedSignForModal && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedSignForModal(null)}
        >
          <div
            className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative overflow-hidden flex flex-col gap-4 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setSelectedSignForModal(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white bg-slate-800/80 p-1.5 rounded-full z-10 transition-colors"
              title="Close Guide"
            >
              <X size={20} />
            </button>

            {/* Header */}
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-teal-500/20 text-teal-300 border border-teal-500/30">
                  {selectedSignForModal.category}
                </span>
                {selectedSignForModal.sign_type && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-slate-800 text-slate-300 border border-slate-700">
                    {selectedSignForModal.sign_type}
                  </span>
                )}
                <span className="text-xs text-slate-400 ml-auto mr-8 font-mono">
                  {selectedSignForModal.id}
                </span>
              </div>
              <h3 className="text-2xl font-black text-white">
                {selectedSignForModal.display_name}
              </h3>
              <p className="text-sm text-slate-300 mt-1">
                {selectedSignForModal.meaning}
              </p>
            </div>

            {/* High-Res SVG Graphic Display */}
            <div className="bg-slate-950/90 rounded-xl border border-slate-800 p-2 flex items-center justify-center aspect-[4/3] max-h-[320px] overflow-hidden shadow-inner">
              <img
                src={selectedSignForModal.media.asset_url}
                alt={selectedSignForModal.display_name}
                className="w-full h-full object-contain"
              />
            </div>

            {/* Step-by-Step Anatomical Instructions */}
            <div className="bg-slate-800/60 border border-sky-500/30 rounded-xl p-4">
              <div className="flex items-center gap-2 text-sky-300 font-bold text-xs uppercase tracking-wider mb-2">
                <span>🖐️ Step-by-Step Hand & Finger Placement:</span>
              </div>
              <p className="text-sm text-slate-100 font-medium leading-relaxed">
                {selectedSignForModal.hand_configuration}
              </p>
            </div>

            {/* ISL Grammar Badge */}
            {selectedSignForModal.isl_grammar_structure && (
              <div className="isl-syntax-badge">
                <div className="isl-syntax-header">
                  <span className="isl-syntax-tag">
                    <BookOpen size={11} />
                    ISL Syntax
                  </span>
                  <span className="isl-syntax-category-pill">Grammar Rule</span>
                </div>
                <p className="isl-syntax-text">
                  {renderSyntaxWithHighlights(selectedSignForModal.isl_grammar_structure)}
                </p>
              </div>
            )}

            {/* Bilingual Translation Buttons */}
            <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800">
              <button
                className="flex items-center justify-between p-3 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 transition-all text-left"
                onClick={() => speak(selectedSignForModal.english_text, "en")}
              >
                <div>
                  <span className="text-[10px] font-bold text-teal-400 uppercase tracking-wider block">
                    English
                  </span>
                  <span className="text-sm font-semibold text-white">
                    {selectedSignForModal.english_text}
                  </span>
                </div>
                <Volume2 size={16} className="text-teal-400 shrink-0" />
              </button>

              <button
                className="flex items-center justify-between p-3 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 transition-all text-left"
                onClick={() => speak(selectedSignForModal.hindi_text, "hi")}
              >
                <div>
                  <span className="text-[10px] font-bold text-teal-400 uppercase tracking-wider block">
                    Hindi (हिंदी)
                  </span>
                  <span className="text-sm font-semibold text-white">
                    {selectedSignForModal.hindi_text}
                  </span>
                </div>
                <Volume2 size={16} className="text-teal-400 shrink-0" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

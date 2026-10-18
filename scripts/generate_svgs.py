import os
from pathlib import Path

SIGN_DIR = Path("c:/Users/tanuu/Downloads/Signify/frontend/public/assets/signs")
SIGN_DIR.mkdir(parents=True, exist_ok=True)

SVGS = {
    "isl_namaste.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Chest level guide -->
  <circle cx="100" cy="100" r="70" fill="none" stroke="#1E293B" stroke-width="2" stroke-dasharray="4"/>
  <!-- Two joined palms (Anjali Mudra) -->
  <path d="M96 150 L96 70 C96 55 90 40 85 45 C80 50 78 70 82 100 L85 150 Z" fill="#2DD4BF" opacity="0.9"/>
  <path d="M104 150 L104 70 C104 55 110 40 115 45 C120 50 122 70 118 100 L115 150 Z" fill="#14B8A6" opacity="0.9"/>
  <!-- Central alignment line -->
  <line x1="100" y1="50" x2="100" y2="155" stroke="#F8FAFC" stroke-width="2" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: NAMASTE / HELLO</text>
</svg>""",

    "isl_thank_you.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Chin outline reference -->
  <path d="M60 50 Q100 80 140 50" fill="none" stroke="#334155" stroke-width="3" stroke-linecap="round"/>
  <!-- Flat hand at chin moving forward -->
  <path d="M70 95 L130 95 C140 95 145 90 145 80 C145 70 140 65 130 65 L70 65 Z" fill="#2DD4BF"/>
  <!-- Forward motion arrow -->
  <path d="M100 110 L100 140 M90 130 L100 145 L110 130" fill="none" stroke="#38BDF8" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: THANK YOU</text>
</svg>""",

    "isl_yes.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Fist shape -->
  <rect x="75" y="70" width="50" height="55" rx="14" fill="#2DD4BF"/>
  <!-- Thumb across fingers -->
  <path d="M75 95 C65 95 65 80 75 80 L110 80" stroke="#0F766E" stroke-width="4" fill="none"/>
  <!-- Nodding vertical arrow -->
  <path d="M145 80 L145 120 M140 88 L145 80 L150 88 M140 112 L145 120 L150 112" fill="none" stroke="#38BDF8" stroke-width="3" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: YES (NODDING FIST)</text>
</svg>""",

    "isl_no.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Index and Middle finger extended -->
  <rect x="80" y="45" width="14" height="60" rx="7" fill="#2DD4BF"/>
  <rect x="100" y="48" width="14" height="57" rx="7" fill="#2DD4BF"/>
  <!-- Closed palm & thumb -->
  <rect x="75" y="95" width="50" height="40" rx="10" fill="#0D9488"/>
  <!-- Horizontal wave arrow -->
  <path d="M50 75 Q100 65 150 75 M60 70 L50 75 L60 80 M140 70 L150 75 L140 80" fill="none" stroke="#F43F5E" stroke-width="3" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: NO (TWO-FINGER WAVE)</text>
</svg>""",

    "isl_help.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Flat supporting palm -->
  <rect x="50" y="130" width="100" height="18" rx="8" fill="#64748B"/>
  <!-- Dominant thumbs-up fist resting on palm -->
  <rect x="80" y="85" width="40" height="45" rx="10" fill="#2DD4BF"/>
  <path d="M85 85 L85 60 C85 52 95 52 95 60 L95 85" fill="#2DD4BF"/>
  <!-- Upward lift arrow -->
  <path d="M145 115 L145 75 M138 85 L145 75 L152 85" fill="none" stroke="#38BDF8" stroke-width="4" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: HELP (LIFTED FIST)</text>
</svg>""",

    "isl_water.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Three extended fingers ('W' handshape) -->
  <rect x="70" y="50" width="12" height="55" rx="6" fill="#2DD4BF"/>
  <rect x="88" y="45" width="12" height="60" rx="6" fill="#2DD4BF"/>
  <rect x="106" y="50" width="12" height="55" rx="6" fill="#2DD4BF"/>
  <rect x="72" y="95" width="46" height="35" rx="8" fill="#0D9488"/>
  <!-- Water drops -->
  <circle cx="145" cy="70" r="6" fill="#38BDF8"/>
  <circle cx="155" cy="85" r="4" fill="#38BDF8"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: WATER</text>
</svg>""",

    "isl_food.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Bunched fingertips -->
  <path d="M85 110 L95 65 C97 60 103 60 105 65 L115 110 Z" fill="#2DD4BF"/>
  <circle cx="100" cy="62" r="8" fill="#14B8A6"/>
  <!-- Inward motion to mouth -->
  <path d="M100 135 L100 115 M95 123 L100 115 L105 123" fill="none" stroke="#38BDF8" stroke-width="3" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: FOOD / EAT</text>
</svg>""",

    "isl_stop.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Full vertical open palm facing forward -->
  <rect x="65" y="90" width="70" height="55" rx="12" fill="#F43F5E"/>
  <rect x="68" y="45" width="13" height="50" rx="6.5" fill="#FB7185"/>
  <rect x="85" y="40" width="13" height="55" rx="6.5" fill="#FB7185"/>
  <rect x="102" y="42" width="13" height="53" rx="6.5" fill="#FB7185"/>
  <rect x="119" y="48" width="13" height="47" rx="6.5" fill="#FB7185"/>
  <!-- Thumb extended -->
  <path d="M65 110 L50 100 C45 96 48 88 55 92 L65 98" fill="#F43F5E"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#FDA4AF" text-anchor="middle" font-weight="bold">ISL: STOP / HALT</text>
</svg>""",

    "isl_please.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Flat open hand -->
  <rect x="75" y="75" width="50" height="45" rx="10" fill="#2DD4BF"/>
  <!-- Gentle circular motion arrow -->
  <path d="M100 45 A35 35 0 1 1 65 80" fill="none" stroke="#38BDF8" stroke-width="3" stroke-linecap="round" stroke-dasharray="6"/>
  <path d="M60 70 L65 80 L75 75" fill="none" stroke="#38BDF8" stroke-width="3" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: PLEASE (CIRCULAR CHEST)</text>
</svg>""",

    "isl_good.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Fist body -->
  <rect x="80" y="90" width="45" height="50" rx="10" fill="#10B981"/>
  <!-- Upright extended thumb -->
  <rect x="75" y="45" width="16" height="50" rx="8" fill="#34D399"/>
  <!-- Positive aura / checkmark -->
  <path d="M140 70 L150 82 L170 58" fill="none" stroke="#34D399" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#A7F3D0" text-anchor="middle" font-weight="bold">ISL: GOOD / WELL</text>
</svg>""",

    "isl_bad.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Fist body -->
  <rect x="80" y="55" width="45" height="50" rx="10" fill="#EF4444"/>
  <!-- Downward extended thumb -->
  <rect x="75" y="100" width="16" height="50" rx="8" fill="#F87171"/>
  <!-- Downward warning indicator -->
  <path d="M145 80 L145 110 M140 102 L145 110 L150 102" fill="none" stroke="#F87171" stroke-width="4" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#FECACA" text-anchor="middle" font-weight="bold">ISL: BAD / UNWELL</text>
</svg>""",

    "isl_more.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Two bunched hands tapping together -->
  <path d="M50 100 L75 80 L80 100 L60 115 Z" fill="#2DD4BF"/>
  <path d="M150 100 L125 80 L120 100 L140 115 Z" fill="#14B8A6"/>
  <!-- Tapping interaction lines in center -->
  <path d="M92 90 L108 90 M92 96 L108 96 M92 102 L108 102" stroke="#38BDF8" stroke-width="2" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: MORE / REPEAT</text>
</svg>"""
}

for fname, content in SVGS.items():
    p = SIGN_DIR / fname
    p.write_text(content.strip(), encoding="utf-8")
    print(f"Wrote {p}")


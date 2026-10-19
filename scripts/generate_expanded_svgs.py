import os
from pathlib import Path

SIGN_DIR = Path("c:/Users/tanuu/Downloads/Signify/frontend/public/assets/signs")
SIGN_DIR.mkdir(parents=True, exist_ok=True)

NEW_SVGS = {
    "isl_how_are_you.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Two open hands twisting inward to outward (HOW) -->
  <path d="M50 110 C50 85 70 85 75 110 L65 140 Z" fill="#2DD4BF"/>
  <path d="M150 110 C150 85 130 85 125 110 L135 140 Z" fill="#14B8A6"/>
  <!-- Question mark arc indicating Wh-question -->
  <path d="M100 45 C115 45 125 55 120 70 C115 85 100 85 100 100" fill="none" stroke="#38BDF8" stroke-width="4" stroke-linecap="round"/>
  <circle cx="100" cy="115" r="4" fill="#38BDF8"/>
  <text x="100" y="180" font-family="sans-serif" font-size="11" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: YOU HOW? (HOW ARE YOU?)</text>
</svg>""",

    "isl_what_is_your_name.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Pointing to person (YOUR) then H-hand tap (NAME) -->
  <rect x="75" y="70" width="50" height="15" rx="7" fill="#2DD4BF"/>
  <rect x="75" y="95" width="50" height="15" rx="7" fill="#14B8A6"/>
  <path d="M100 50 L100 35 M90 42 L100 35 L110 42" stroke="#38BDF8" stroke-width="3" fill="none"/>
  <text x="100" y="180" font-family="sans-serif" font-size="10.5" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: YOUR NAME WHAT?</text>
</svg>""",

    "isl_nice_to_meet_you.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Two index fingers coming together in meeting -->
  <rect x="55" y="70" width="14" height="50" rx="7" fill="#2DD4BF"/>
  <rect x="131" y="70" width="14" height="50" rx="7" fill="#14B8A6"/>
  <!-- Motion arrows towards center -->
  <path d="M75 95 L92 95 M125 95 L108 95" stroke="#38BDF8" stroke-width="3" stroke-linecap="round"/>
  <!-- Heart / happy symbol -->
  <path d="M100 50 C95 40 85 45 85 55 C85 68 100 78 100 78 C100 78 115 68 115 55 C115 45 105 40 100 50 Z" fill="#F43F5E"/>
  <text x="100" y="180" font-family="sans-serif" font-size="11" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: MEET YOU HAPPY</text>
</svg>""",

    "isl_welcome.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Open hands sweeping inwards in welcoming gesture -->
  <path d="M40 90 Q80 120 95 100" fill="none" stroke="#2DD4BF" stroke-width="6" stroke-linecap="round"/>
  <path d="M160 90 Q120 120 105 100" fill="none" stroke="#14B8A6" stroke-width="6" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: WELCOME</text>
</svg>""",

    "isl_sorry.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Closed fist rubbing on chest -->
  <circle cx="100" cy="95" r="45" fill="none" stroke="#334155" stroke-width="2" stroke-dasharray="4"/>
  <rect x="80" y="75" width="40" height="40" rx="10" fill="#F59E0B"/>
  <path d="M125 70 A25 25 0 1 1 75 70" fill="none" stroke="#38BDF8" stroke-width="3" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: SORRY / APOLOGIES</text>
</svg>""",

    "isl_father.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Cheek / mustache location indicator -->
  <circle cx="100" cy="80" r="40" fill="none" stroke="#334155" stroke-width="2"/>
  <path d="M85 95 Q100 105 115 95" stroke="#2DD4BF" stroke-width="4" fill="none" stroke-linecap="round"/>
  <circle cx="120" cy="95" r="6" fill="#F59E0B"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: FATHER</text>
</svg>""",

    "isl_mother.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Chin / cheek touch (feminine ISL marker) -->
  <circle cx="100" cy="80" r="40" fill="none" stroke="#334155" stroke-width="2"/>
  <circle cx="80" cy="95" r="7" fill="#F43F5E"/>
  <path d="M70 120 L80 98" stroke="#38BDF8" stroke-width="3" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: MOTHER</text>
</svg>""",

    "isl_family.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Two hands creating a circular group -->
  <circle cx="100" cy="95" r="35" fill="none" stroke="#2DD4BF" stroke-width="4" stroke-dasharray="8"/>
  <circle cx="85" cy="85" r="8" fill="#38BDF8"/>
  <circle cx="115" cy="85" r="8" fill="#F43F5E"/>
  <circle cx="100" cy="110" r="6" fill="#F59E0B"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: FAMILY</text>
</svg>""",

    "isl_tea.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Cup base and dipping F-pinch -->
  <rect x="75" y="90" width="50" height="40" rx="8" fill="#0D9488"/>
  <path d="M125 100 Q140 110 125 120" stroke="#2DD4BF" stroke-width="3" fill="none"/>
  <!-- Steam lines -->
  <path d="M90 75 Q85 65 90 55 M105 75 Q110 65 105 55" stroke="#38BDF8" stroke-width="2" fill="none"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: TEA / CHAI</text>
</svg>""",

    "isl_hungry.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Curved hand tracing down stomach -->
  <path d="M100 50 L100 125" stroke="#38BDF8" stroke-width="4" stroke-dasharray="6"/>
  <path d="M85 110 L100 130 L115 110" stroke="#38BDF8" stroke-width="4" fill="none" stroke-linecap="round"/>
  <rect x="80" y="70" width="40" height="25" rx="8" fill="#2DD4BF"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: HUNGRY</text>
</svg>""",

    "isl_need_help.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Urgent two-handed lift with red alert aura -->
  <circle cx="100" cy="100" r="65" fill="none" stroke="#EF4444" stroke-width="2" stroke-dasharray="4"/>
  <rect x="50" y="130" width="100" height="18" rx="8" fill="#64748B"/>
  <rect x="80" y="80" width="40" height="45" rx="10" fill="#EF4444"/>
  <path d="M85 80 L85 55 C85 48 95 48 95 55 L95 80" fill="#F87171"/>
  <path d="M145 115 L145 65 M138 75 L145 65 L152 75" fill="none" stroke="#F87171" stroke-width="4" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="11" fill="#FCA5A5" text-anchor="middle" font-weight="bold">ISL: HELP ME NEED (EMERGENCY)</text>
</svg>""",

    "isl_doctor.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Checking pulse on wrist (Doctor sign in ISL) -->
  <rect x="40" y="110" width="120" height="22" rx="11" fill="#64748B"/>
  <!-- Two index & middle fingers tapping wrist -->
  <rect x="90" y="55" width="12" height="50" rx="6" fill="#2DD4BF"/>
  <rect x="106" y="58" width="12" height="47" rx="6" fill="#2DD4BF"/>
  <!-- Pulse wave -->
  <path d="M75 120 L85 120 L90 110 L95 130 L100 120 L115 120" stroke="#38BDF8" stroke-width="2" fill="none"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: DOCTOR (PULSE CHECK)</text>
</svg>""",

    "isl_hospital.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Red Cross symbol / H formation -->
  <rect x="88" y="50" width="24" height="70" rx="6" fill="#EF4444"/>
  <rect x="65" y="73" width="70" height="24" rx="6" fill="#EF4444"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#FCA5A5" text-anchor="middle" font-weight="bold">ISL: HOSPITAL / CLINIC</text>
</svg>""",

    "isl_pain.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Index fingers twisting towards each other -->
  <rect x="55" y="90" width="40" height="14" rx="7" fill="#F59E0B"/>
  <rect x="105" y="90" width="40" height="14" rx="7" fill="#F59E0B"/>
  <!-- Lightning bolt / pain burst in middle -->
  <path d="M100 70 L95 90 L105 92 L98 115" stroke="#EF4444" stroke-width="3" fill="none" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: PAIN / HURT / SICK</text>
</svg>""",

    "isl_restroom.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- T-handshape (thumb tucked between index & middle) shaking side to side -->
  <rect x="80" y="75" width="40" height="45" rx="10" fill="#2DD4BF"/>
  <path d="M85 75 L85 55 C85 48 95 48 95 55 L95 75" fill="#2DD4BF"/>
  <!-- Horizontal oscillation arrow -->
  <path d="M60 100 Q100 90 140 100 M68 93 L60 100 L68 107 M132 93 L140 100 L132 107" fill="none" stroke="#38BDF8" stroke-width="3" stroke-linecap="round"/>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: RESTROOM / TOILET</text>
</svg>""",

    "isl_where_location.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#0A192F"/>
  <!-- Upward palms waving side to side (WHERE) -->
  <path d="M50 110 Q80 120 95 105" fill="none" stroke="#2DD4BF" stroke-width="5" stroke-linecap="round"/>
  <path d="M150 110 Q120 120 105 105" fill="none" stroke="#14B8A6" stroke-width="5" stroke-linecap="round"/>
  <!-- Question marks -->
  <text x="100" y="75" font-family="sans-serif" font-size="36" fill="#38BDF8" text-anchor="middle" font-weight="bold">?</text>
  <text x="100" y="180" font-family="sans-serif" font-size="12" fill="#94A3B8" text-anchor="middle" font-weight="bold">ISL: WHERE? / LOCATION</text>
</svg>"""
}

for fname, content in NEW_SVGS.items():
    p = SIGN_DIR / fname
    p.write_text(content.strip(), encoding="utf-8")
    print(f"Generated {p.name}")

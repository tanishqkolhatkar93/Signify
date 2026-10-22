"""
Generate anatomically detailed, intuitive, high-contrast SVG illustrations
for all 28 Indian Sign Language (ISL) signs in Signify.

Each SVG includes:
- Clear anatomical hand shapes (palms, wrists, articulated fingers, knuckles, nails)
- Clear gesture motion arrows & action cues (ripples, direction arrows, contact points)
- Visual cues: Perspective, orientation, facial/body landmarks (chin, wrist, chest, lips)
- In-graphic instructions with high-contrast badge for common people to follow
"""

import os
import json

OUTPUT_DIR = os.path.join("frontend", "public", "assets", "signs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Shared SVG styling and defs
SVG_HEADER = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 320" width="100%" height="100%">
  <defs>
    <!-- Background Gradient -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090E1A" />
      <stop offset="100%" stop-color="#141E33" />
    </linearGradient>

    <!-- Subtle Tech Grid -->
    <pattern id="techGrid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1E293B" stroke-width="0.7" opacity="0.4" />
    </pattern>

    <!-- Hand Skin Gradients (Warm Natural Tone with Depth) -->
    <linearGradient id="skinGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FCD34D" />
      <stop offset="35%" stop-color="#F59E0B" />
      <stop offset="100%" stop-color="#D97706" />
    </linearGradient>

    <linearGradient id="skinBase" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FDE68A" />
      <stop offset="50%" stop-color="#F59E0B" />
      <stop offset="100%" stop-color="#B45309" />
    </linearGradient>

    <linearGradient id="skinSec" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E2E8F0" />
      <stop offset="60%" stop-color="#94A3B8" />
      <stop offset="100%" stop-color="#64748B" />
    </linearGradient>

    <linearGradient id="handShade" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FEF08A" />
      <stop offset="100%" stop-color="#D97706" />
    </linearGradient>

    <!-- Arrow Markers -->
    <marker id="arrowTeal" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <polygon points="0 1, 8 4, 0 7" fill="#2DD4BF" />
    </marker>
    <marker id="arrowCyan" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <polygon points="0 1, 8 4, 0 7" fill="#38BDF8" />
    </marker>
    <marker id="arrowEmerald" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <polygon points="0 1, 8 4, 0 7" fill="#34D399" />
    </marker>
    <marker id="arrowAmber" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <polygon points="0 1, 8 4, 0 7" fill="#FBBF24" />
    </marker>
    <marker id="arrowRose" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <polygon points="0 1, 8 4, 0 7" fill="#F43F5E" />
    </marker>

    <!-- Glow Filter -->
    <filter id="glowTeal" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Frame Background -->
  <rect width="400" height="320" rx="16" fill="url(#bgGrad)" stroke="#334155" stroke-width="1.5"/>
  <rect width="400" height="320" rx="16" fill="url(#techGrid)"/>
'''

SVG_FOOTER = '''</svg>'''


def card_frame(title, category, cue, steps, footer_instruction):
    """Generates standard top badges, category pills, and bottom step guide."""
    return f'''
  <!-- Top Header Bar -->
  <rect x="12" y="12" width="376" height="34" rx="8" fill="#0F172A" stroke="#334155" stroke-width="1"/>
  <circle cx="28" cy="29" r="5" fill="#2DD4BF" />
  <text x="42" y="33" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" font-weight="700" fill="#F8FAFC" letter-spacing="0.5">ISL: {title.upper()}</text>
  
  <rect x="270" y="19" width="108" height="20" rx="10" fill="#1E293B" stroke="#475569" stroke-width="1"/>
  <text x="324" y="33" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10" font-weight="600" fill="#38BDF8" text-anchor="middle">{category.upper()}</text>

  <!-- Cue Badge -->
  <g transform="translate(16, 56)">
    <rect width="130" height="22" rx="6" fill="#1E293B" stroke="#0D9488" stroke-width="1"/>
    <text x="8" y="15" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10" font-weight="600" fill="#5EEAD4">🖐️ {cue}</text>
  </g>

  <!-- Bottom Instruction Box -->
  <rect x="12" y="260" width="376" height="48" rx="10" fill="#0F172A" stroke="#1E293B" stroke-width="1.2"/>
  <rect x="18" y="266" width="364" height="20" rx="4" fill="#1E293B"/>
  <text x="26" y="280" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10" font-weight="700" fill="#FBBF24">HOW TO PERFORM WITH HANDS:</text>
  <text x="26" y="299" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" font-weight="600" fill="#F1F5F9">{footer_instruction}</text>
'''


# Define SVG vector artwork for all 28 signs
SIGNS_ART = {
    "isl_namaste.svg": {
        "title": "Namaste / Hello",
        "category": "Greetings",
        "cue": "Both Hands (Anjali)",
        "footer": "Join both palms flat together vertically at chest height. Nod politely.",
        "svg_content": '''
  <!-- Anjali Mudra / Joined Palms -->
  <g transform="translate(145, 75)">
    <!-- Aura / Ripple -->
    <ellipse cx="55" cy="85" rx="75" ry="75" fill="none" stroke="#2DD4BF" stroke-width="1.5" stroke-dasharray="4,4" opacity="0.4"/>
    <ellipse cx="55" cy="85" rx="55" ry="55" fill="none" stroke="#FBBF24" stroke-width="1.2" opacity="0.3"/>
    
    <!-- Chest / Torso Outline Hint -->
    <path d="M-30 165 C20 140, 90 140, 140 165" stroke="#334155" stroke-width="3" fill="none" stroke-linecap="round"/>

    <!-- Left Hand Palm & Fingers -->
    <path d="M42 160 L42 110 C42 95, 46 65, 52 40 C53 35, 56 35, 56 40 L56 160 Z" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
    <!-- Right Hand Palm & Fingers (Symmetric Mirror) -->
    <path d="M68 160 L68 110 C68 95, 64 65, 58 40 C57 35, 54 35, 54 40 L54 160 Z" fill="url(#skinShade)" stroke="#78350F" stroke-width="1.8"/>
    
    <!-- Joined Finger Lines -->
    <line x1="55" y1="40" x2="55" y2="135" stroke="#78350F" stroke-width="1.8"/>
    <line x1="48" y1="55" x2="48" y2="110" stroke="#B45309" stroke-width="1.2"/>
    <line x1="62" y1="55" x2="62" y2="110" stroke="#B45309" stroke-width="1.2"/>
    
    <!-- Joined Thumbs Facing Signer -->
    <path d="M38 120 C32 105, 38 95, 45 92" stroke="#78350F" stroke-width="2" fill="none"/>
    <path d="M72 120 C78 105, 72 95, 65 92" stroke="#78350F" stroke-width="2" fill="none"/>
    
    <!-- Wrists & Base -->
    <rect x="36" y="155" width="38" height="22" rx="4" fill="#D97706" stroke="#78350F" stroke-width="1.5"/>

    <!-- Golden Sparkles -->
    <path d="M55 18 L57 26 L65 28 L57 30 L55 38 L53 30 L45 28 L53 26 Z" fill="#FBBF24"/>
  </g>
'''
    },

    "isl_good.svg": {
        "title": "Good / Well",
        "category": "Feedback",
        "cue": "Upright Thumbs-Up",
        "footer": "Curl all 4 fingers tightly into your palm, extend thumb straight up.",
        "svg_content": '''
  <!-- Thumbs-up Fist with Clear Knuckle Articulation -->
  <g transform="translate(130, 65)">
    <!-- Upward Motion Indicator -->
    <path d="M35 100 L35 45" stroke="#34D399" stroke-width="3" stroke-dasharray="5,4" marker-end="url(#arrowEmerald)"/>
    <path d="M105 100 L105 45" stroke="#34D399" stroke-width="3" stroke-dasharray="5,4" marker-end="url(#arrowEmerald)"/>

    <!-- Forearm / Wrist -->
    <path d="M50 145 L50 180 L85 180 L85 145" fill="#D97706" stroke="#78350F" stroke-width="2"/>

    <!-- Curled Fingers (Knuckles: Index, Middle, Ring, Pinky) -->
    <rect x="50" y="85" width="45" height="18" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
    <rect x="50" y="101" width="47" height="17" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
    <rect x="50" y="116" width="45" height="17" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
    <rect x="52" y="131" width="41" height="16" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
    
    <!-- Finger Creases & Nails -->
    <line x1="82" y1="94" x2="90" y2="94" stroke="#92400E" stroke-width="1.5"/>
    <line x1="84" y1="109" x2="92" y2="109" stroke="#92400E" stroke-width="1.5"/>
    <line x1="82" y1="124" x2="89" y2="124" stroke="#92400E" stroke-width="1.5"/>
    
    <!-- Thumb Extended Upward -->
    <path d="M48 115 C44 95, 42 65, 43 45 C44 32, 59 32, 60 45 C61 65, 62 80, 65 92" fill="url(#skinBase)" stroke="#78350F" stroke-width="2"/>
    <!-- Thumbnail -->
    <path d="M47 42 C49 37, 55 37, 57 42" fill="#FEF08A" stroke="#78350F" stroke-width="1.2"/>
    <!-- Thumb Knuckle Joint -->
    <path d="M44 68 C49 71, 56 71, 61 68" stroke="#B45309" stroke-width="1.5" fill="none"/>

    <!-- Success Checkmark Badge -->
    <g transform="translate(100, 45)">
      <circle cx="22" cy="22" r="18" fill="#065F46" stroke="#34D399" stroke-width="2"/>
      <path d="M12 22 L19 29 L32 15" fill="none" stroke="#34D399" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    </g>
  </g>
'''
    },

    "isl_bad.svg": {
        "title": "Bad / Unwell",
        "category": "Feedback",
        "cue": "Thumbs-Down Fist",
        "footer": "Make a fist, rotate wrist 180 degrees, point thumb straight down.",
        "svg_content": '''
  <!-- Thumbs-down Fist with Downward Motion Arrows -->
  <g transform="translate(140, 65)">
    <!-- Downward Motion Indicator -->
    <path d="M35 80 L35 150" stroke="#F43F5E" stroke-width="3" stroke-dasharray="5,4" marker-end="url(#arrowRose)"/>
    <path d="M105 80 L105 150" stroke="#F43F5E" stroke-width="3" stroke-dasharray="5,4" marker-end="url(#arrowRose)"/>

    <!-- Forearm / Wrist at top -->
    <path d="M50 15 L50 45 L85 45 L85 15" fill="#D97706" stroke="#78350F" stroke-width="2"/>

    <!-- Curled Fist Body -->
    <rect x="50" y="45" width="45" height="17" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
    <rect x="50" y="60" width="47" height="17" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
    <rect x="50" y="75" width="45" height="17" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
    <rect x="52" y="90" width="41" height="16" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>

    <!-- Thumb Extended Downward -->
    <path d="M48 70 C44 95, 42 125, 43 145 C44 158, 59 158, 60 145 C61 125, 62 105, 65 92" fill="url(#skinBase)" stroke="#78350F" stroke-width="2"/>
    <!-- Thumbnail -->
    <path d="M47 148 C49 153, 55 153, 57 148" fill="#FEF08A" stroke="#78350F" stroke-width="1.2"/>

    <!-- Cross Badge -->
    <g transform="translate(100, 95)">
      <circle cx="22" cy="22" r="18" fill="#881337" stroke="#F43F5E" stroke-width="2"/>
      <path d="M14 14 L30 30 M30 14 L14 30" stroke="#F43F5E" stroke-width="3" stroke-linecap="round"/>
    </g>
  </g>
'''
    },

    "isl_doctor.svg": {
        "title": "Doctor",
        "category": "Emergency / Medical",
        "cue": "Pulse Check on Wrist",
        "footer": "Tap index and middle fingertips gently on opposite inner wrist (like taking pulse).",
        "svg_content": '''
  <!-- Doctor Pulse Check: Horizontal Arm + Two Tapping Fingers -->
  <g transform="translate(60, 65)">
    <!-- Patient Wrist / Arm (Horizontal) -->
    <g>
      <rect x="20" y="115" width="180" height="38" rx="14" fill="url(#skinSec)" stroke="#475569" stroke-width="2"/>
      <line x1="80" y1="115" x2="80" y2="153" stroke="#64748B" stroke-width="1" stroke-dasharray="2,2"/>
      <text x="35" y="138" font-family="sans-serif" font-size="10" font-weight="700" fill="#E2E8F0">INNER WRIST</text>
    </g>

    <!-- Tap Ripples at Pulse Point -->
    <circle cx="140" cy="115" r="14" fill="none" stroke="#38BDF8" stroke-width="2" opacity="0.8"/>
    <circle cx="140" cy="115" r="24" fill="none" stroke="#2DD4BF" stroke-width="1.5" stroke-dasharray="3,3" opacity="0.6"/>

    <!-- ECG Pulse Line -->
    <path d="M100 135 L115 135 L122 120 L130 150 L138 126 L145 138 L160 135" stroke="#38BDF8" stroke-width="2" fill="none" stroke-linecap="round"/>

    <!-- Dominant Hand (2 fingers extended down tapping wrist) -->
    <g transform="translate(100, -10)">
      <!-- Wrist -->
      <path d="M28 20 L28 45 L62 45 L62 20" fill="#D97706" stroke="#78350F" stroke-width="1.8"/>
      <!-- Fist Body (curled ring and pinky) -->
      <circle cx="58" cy="65" r="14" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <circle cx="60" cy="80" r="12" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Curled Thumb holding them -->
      <path d="M38 65 C44 75, 52 75, 58 70" stroke="#78350F" stroke-width="2" fill="none"/>

      <!-- Index Finger Extended Down -->
      <rect x="25" y="55" width="14" height="66" rx="7" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Middle Finger Extended Down -->
      <rect x="41" y="55" width="14" height="66" rx="7" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>

      <!-- Fingernails touching wrist -->
      <ellipse cx="32" cy="116" rx="4" ry="2" fill="#FEF08A" stroke="#78350F" stroke-width="1"/>
      <ellipse cx="48" cy="116" rx="4" ry="2" fill="#FEF08A" stroke="#78350F" stroke-width="1"/>

      <!-- Tap Down Arrow Indicator -->
      <path d="M12 60 L12 95" stroke="#38BDF8" stroke-width="2.5" marker-end="url(#arrowCyan)"/>
      <text x="-15" y="80" font-family="sans-serif" font-size="9" font-weight="700" fill="#38BDF8">TAP 2x</text>
    </g>

    <!-- Caduceus / Cross Badge -->
    <g transform="translate(225, 30)">
      <circle cx="20" cy="20" r="18" fill="#0C4A6E" stroke="#38BDF8" stroke-width="2"/>
      <rect x="17" y="8" width="6" height="24" rx="2" fill="#38BDF8"/>
      <rect x="8" y="17" width="24" height="6" rx="2" fill="#38BDF8"/>
    </g>
  </g>
'''
    },

    "isl_hospital.svg": {
        "title": "Hospital / Clinic",
        "category": "Emergency / Medical",
        "cue": "Cross Sign on Upper Arm",
        "footer": "Using index & middle finger, trace a '+' cross on opposite upper arm/shoulder.",
        "svg_content": '''
  <!-- Tracing Cross on Arm -->
  <g transform="translate(100, 65)">
    <!-- Arm Silhouette -->
    <path d="M30 40 C30 20, 90 20, 90 40 L95 160 L25 160 Z" fill="#1E293B" stroke="#475569" stroke-width="2"/>
    <text x="60" y="145" font-family="sans-serif" font-size="10" font-weight="700" fill="#94A3B8" text-anchor="middle">UPPER ARM</text>

    <!-- Drawn Red Cross -->
    <path d="M60 45 L60 115" stroke="#F43F5E" stroke-width="8" stroke-linecap="round"/>
    <path d="M25 80 L95 80" stroke="#F43F5E" stroke-width="8" stroke-linecap="round"/>

    <!-- Motion Guide Arrows -->
    <!-- Downward stroke -->
    <path d="M75 50 L75 95" stroke="#38BDF8" stroke-width="2.5" stroke-dasharray="3,3" marker-end="url(#arrowCyan)"/>
    <text x="82" y="70" font-family="sans-serif" font-size="9" font-weight="700" fill="#38BDF8">1. DOWN</text>
    <!-- Across stroke -->
    <path d="M30 100 L85 100" stroke="#FBBF24" stroke-width="2.5" stroke-dasharray="3,3" marker-end="url(#arrowAmber)"/>
    <text x="40" y="115" font-family="sans-serif" font-size="9" font-weight="700" fill="#FBBF24">2. ACROSS</text>

    <!-- Tracing Hand with 2 Fingers -->
    <g transform="translate(90, 70)">
      <rect x="15" y="10" width="13" height="45" rx="6" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
      <rect x="29" y="12" width="13" height="43" rx="6" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
      <circle cx="45" cy="30" r="12" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <rect x="25" y="45" width="30" height="25" rx="6" fill="#D97706" stroke="#78350F" stroke-width="1.8"/>
    </g>
  </g>
'''
    },

    "isl_help.svg": {
        "title": "Help / Assistance",
        "category": "Assistance",
        "cue": "Fist Lifted on Flat Palm",
        "footer": "Hold non-dominant palm flat facing up; place thumbs-up fist on it and lift both upward.",
        "svg_content": '''
  <!-- Fist Lifted on Open Palm -->
  <g transform="translate(100, 65)">
    <!-- Upward Motion Arrows -->
    <path d="M35 120 L35 50" stroke="#2DD4BF" stroke-width="3" stroke-dasharray="4,3" marker-end="url(#arrowTeal)"/>
    <path d="M165 120 L165 50" stroke="#2DD4BF" stroke-width="3" stroke-dasharray="4,3" marker-end="url(#arrowTeal)"/>
    <text x="100" y="40" font-family="sans-serif" font-size="11" font-weight="700" fill="#2DD4BF" text-anchor="middle">LIFT UPWARD TOGETHER</text>

    <!-- Base Hand (Open flat palm facing up) -->
    <g transform="translate(15, 120)">
      <path d="M15 25 L15 15 C15 10, 25 8, 45 8 L145 8 C160 8, 168 15, 165 25 L15 25 Z" fill="url(#skinSec)" stroke="#475569" stroke-width="2"/>
      <line x1="50" y1="8" x2="50" y2="22" stroke="#64748B" stroke-width="1.2"/>
      <line x1="85" y1="8" x2="85" y2="22" stroke="#64748B" stroke-width="1.2"/>
      <line x1="120" y1="8" x2="120" y2="22" stroke="#64748B" stroke-width="1.2"/>
      <text x="85" y="38" font-family="sans-serif" font-size="9" font-weight="700" fill="#94A3B8" text-anchor="middle">SUPPORTING FLAT PALM</text>
    </g>

    <!-- Dominant Hand (Thumbs-Up fist resting on base) -->
    <g transform="translate(65, 45)">
      <!-- Curled Fist Body -->
      <rect x="25" y="45" width="40" height="35" rx="10" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Knuckle Lines -->
      <line x1="30" y1="56" x2="58" y2="56" stroke="#92400E" stroke-width="1.5"/>
      <line x1="30" y1="67" x2="58" y2="67" stroke="#92400E" stroke-width="1.5"/>
      <!-- Thumb Extended Upward -->
      <path d="M22 55 C18 40, 18 20, 25 10 C32 10, 36 25, 36 45" fill="url(#skinBase)" stroke="#78350F" stroke-width="2"/>
      <ellipse cx="26" cy="14" rx="4" ry="2" fill="#FEF08A"/>
    </g>
  </g>
'''
    },

    "isl_need_help.svg": {
        "title": "Need Help (Urgent)",
        "category": "Assistance",
        "cue": "Point Me + Help Inward",
        "footer": "Point to chest (ME), then bring help fist-on-palm inward towards your chest.",
        "svg_content": '''
  <!-- Two Step Urgent Help -->
  <g transform="translate(70, 60)">
    <!-- Step 1: Point to self -->
    <g transform="translate(20, 20)">
      <circle cx="45" cy="45" r="35" fill="#1E293B" stroke="#0D9488" stroke-width="1.5"/>
      <!-- Hand pointing inward -->
      <rect x="25" y="35" width="40" height="20" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.5"/>
      <path d="M25 45 L5 45" stroke="#2DD4BF" stroke-width="3" marker-end="url(#arrowTeal)"/>
      <text x="45" y="70" font-family="sans-serif" font-size="9" font-weight="700" fill="#5EEAD4" text-anchor="middle">1. POINT "ME"</text>
    </g>

    <!-- Transition Arrow -->
    <path d="M115 65 L145 65" stroke="#FBBF24" stroke-width="3" marker-end="url(#arrowAmber)"/>

    <!-- Step 2: Help moving towards chest -->
    <g transform="translate(150, 10)">
      <circle cx="50" cy="55" r="45" fill="#1E293B" stroke="#E11D48" stroke-width="1.5"/>
      <!-- Palm + Fist -->
      <rect x="18" y="70" width="65" height="12" rx="4" fill="url(#skinSec)" stroke="#475569" stroke-width="1.5"/>
      <rect x="30" y="45" width="28" height="25" rx="6" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.5"/>
      <path d="M30 45 L30 25 C35 25, 38 35, 38 45" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <!-- Inward Arrow -->
      <path d="M85 55 L5 55" stroke="#F43F5E" stroke-width="2.5" stroke-dasharray="3,2" marker-end="url(#arrowRose)"/>
      <text x="50" y="95" font-family="sans-serif" font-size="9" font-weight="700" fill="#FDA4AF" text-anchor="middle">2. HELP TOWARDS ME</text>
    </g>

    <!-- Exclamation Alert Badge -->
    <g transform="translate(210, 5)">
      <circle cx="15" cy="15" r="12" fill="#E11D48"/>
      <text x="15" y="20" font-family="sans-serif" font-size="14" font-weight="900" fill="#FFF" text-anchor="middle">!</text>
    </g>
  </g>
'''
    },

    "isl_stop.svg": {
        "title": "Stop",
        "category": "Instruction",
        "cue": "Open Palm Facing Forward",
        "footer": "Raise dominant hand at shoulder height, all 5 fingers straight, palm facing straight ahead.",
        "svg_content": '''
  <!-- Open Flat Hand Facing Viewer with Stop Radiance -->
  <g transform="translate(130, 60)">
    <!-- Radial Stop Barrier Rings -->
    <circle cx="70" cy="80" r="75" fill="none" stroke="#E11D48" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.6"/>
    <circle cx="70" cy="80" r="60" fill="none" stroke="#F43F5E" stroke-width="2" opacity="0.4"/>

    <!-- Wrist & Forearm -->
    <rect x="52" y="145" width="36" height="35" rx="6" fill="#D97706" stroke="#78350F" stroke-width="2"/>

    <!-- Palm Base (Facing front) -->
    <path d="M42 95 L42 145 C42 152, 98 152, 98 145 L98 95 Z" fill="url(#skinGrad)" stroke="#78350F" stroke-width="2"/>
    <!-- Palm Crease Lines -->
    <path d="M48 115 C62 125, 78 120, 92 110" stroke="#B45309" stroke-width="1.5" fill="none"/>
    <path d="M48 130 C65 138, 80 135, 92 122" stroke="#B45309" stroke-width="1.5" fill="none"/>

    <!-- 4 Extended Upright Fingers -->
    <!-- Index -->
    <rect x="42" y="35" width="13" height="65" rx="6.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
    <!-- Middle -->
    <rect x="56" y="28" width="13.5" height="72" rx="6.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
    <!-- Ring -->
    <rect x="70.5" y="32" width="13" height="68" rx="6.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
    <!-- Little / Pinky -->
    <rect x="84.5" y="45" width="12" height="55" rx="6" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>

    <!-- Extended Thumb -->
    <path d="M42 115 C30 110, 18 95, 20 85 C22 78, 32 82, 42 95" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>

    <!-- Hand Stop Octagon Badge -->
    <g transform="translate(115, 25)">
      <polygon points="12 2, 28 2, 38 12, 38 28, 28 38, 12 38, 2 28, 2 12" fill="#E11D48" stroke="#FFF" stroke-width="1.5"/>
      <text x="20" y="24" font-family="sans-serif" font-size="9" font-weight="900" fill="#FFF" text-anchor="middle">HALT</text>
    </g>
  </g>
'''
    },

    "isl_yes.svg": {
        "title": "Yes / Affirmation",
        "category": "Feedback",
        "cue": "Fist Nodding Up & Down",
        "footer": "Form a closed fist at chest height, nod your wrist up and down twice like a nodding head.",
        "svg_content": '''
  <!-- Fist Nodding like a Head -->
  <g transform="translate(130, 65)">
    <!-- Curved Double-Headed Nodding Arc -->
    <path d="M25 60 C15 85, 15 115, 25 140" fill="none" stroke="#34D399" stroke-width="3" marker-end="url(#arrowEmerald)" marker-start="url(#arrowEmerald)"/>
    <text x="8" y="105" font-family="sans-serif" font-size="10" font-weight="700" fill="#34D399" transform="rotate(-90 8 105)" text-anchor="middle">NOD WRIST</text>

    <!-- Forearm -->
    <path d="M60 145 L60 180 L95 180 L95 145" fill="#D97706" stroke="#78350F" stroke-width="2"/>

    <!-- S-Fist in Mid-Nod Position -->
    <g transform="translate(10, 0)">
      <rect x="50" y="70" width="50" height="75" rx="20" fill="url(#skinGrad)" stroke="#78350F" stroke-width="2"/>
      <!-- Folded Knuckles -->
      <path d="M50 88 C65 88, 85 88, 100 88" stroke="#92400E" stroke-width="2"/>
      <path d="M50 106 C65 106, 85 106, 100 106" stroke="#92400E" stroke-width="2"/>
      <path d="M50 124 C65 124, 85 124, 100 124" stroke="#92400E" stroke-width="2"/>

      <!-- Thumb Wrapped Across Knuckles -->
      <path d="M45 105 C45 85, 65 80, 85 82 C90 84, 85 96, 75 96 L50 96" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Thumbnail -->
      <ellipse cx="78" cy="88" rx="4" ry="3" fill="#FEF08A"/>
    </g>

    <!-- Nod Trajectory Shadow -->
    <path d="M75 55 C90 60, 105 70, 110 85" stroke="#34D399" stroke-width="2" stroke-dasharray="3,3" fill="none"/>
  </g>
'''
    },

    "isl_no.svg": {
        "title": "No / Negation",
        "category": "Feedback",
        "cue": "Snap Fingers Shut / Wag",
        "footer": "Extend index & middle finger with thumb open, then snap them shut together firmly.",
        "svg_content": '''
  <!-- 2 Fingers Snapping Shut onto Thumb -->
  <g transform="translate(120, 65)">
    <!-- Snap Shut Motion Arcs -->
    <path d="M85 35 C100 50, 105 70, 100 85" fill="none" stroke="#F43F5E" stroke-width="2.5" stroke-dasharray="3,3" marker-end="url(#arrowRose)"/>
    <text x="125" y="60" font-family="sans-serif" font-size="10" font-weight="700" fill="#F43F5E">SNAP SHUT</text>

    <!-- Wrist -->
    <rect x="40" y="130" width="35" height="40" rx="6" fill="#D97706" stroke="#78350F" stroke-width="2"/>

    <!-- Hand Palm Base -->
    <path d="M35 85 L35 130 L75 130 L75 85 Z" fill="url(#skinGrad)" stroke="#78350F" stroke-width="2"/>

    <!-- Folded Ring and Little Fingers -->
    <circle cx="48" cy="115" r="10" fill="#B45309" stroke="#78350F" stroke-width="1.5"/>
    <circle cx="62" cy="115" r="9" fill="#B45309" stroke="#78350F" stroke-width="1.5"/>

    <!-- Extended Index Finger (Approaching thumb) -->
    <rect x="42" y="30" width="14" height="60" rx="7" transform="rotate(15 42 30)" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
    <!-- Extended Middle Finger (Beside index) -->
    <rect x="56" y="32" width="14" height="58" rx="7" transform="rotate(15 56 32)" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>

    <!-- Open Opposing Thumb -->
    <path d="M40 95 C55 90, 75 90, 85 96 C90 102, 75 110, 60 110" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>

    <!-- Impact Ripple -->
    <circle cx="82" cy="78" r="8" fill="none" stroke="#FBBF24" stroke-width="2" stroke-dasharray="2,2"/>
  </g>
'''
    },

    "isl_thank_you.svg": {
        "title": "Thank You",
        "category": "Courtesies",
        "cue": "Touch Chin & Move Forward",
        "footer": "Touch flat fingertips to your chin/lips, then move hand straight forward towards the other person.",
        "svg_content": '''
  <!-- Chin Touch ➔ Forward Arc -->
  <g transform="translate(90, 60)">
    <!-- Face / Chin Profile Hint -->
    <path d="M30 20 C45 35, 45 65, 30 90 L20 120" stroke="#475569" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <text x="15" y="55" font-family="sans-serif" font-size="9" font-weight="700" fill="#94A3B8">CHIN / LIPS</text>

    <!-- Touch Contact Point on Chin -->
    <circle cx="42" cy="65" r="12" fill="none" stroke="#FBBF24" stroke-width="2" stroke-dasharray="3,2"/>
    <text x="45" y="45" font-family="sans-serif" font-size="9" font-weight="700" fill="#FBBF24">1. TOUCH</text>

    <!-- Forward Trajectory Arrow -->
    <path d="M85 70 C130 65, 160 80, 195 95" fill="none" stroke="#2DD4BF" stroke-width="3.5" marker-end="url(#arrowTeal)"/>
    <text x="135" y="60" font-family="sans-serif" font-size="11" font-weight="700" fill="#2DD4BF">2. EXTEND FORWARD</text>

    <!-- Hand Moving Forward (Flat open hand) -->
    <g transform="translate(85, 75)">
      <!-- Wrist -->
      <rect x="0" y="30" width="30" height="20" rx="4" fill="#D97706" stroke="#78350F" stroke-width="1.8" transform="rotate(-15)"/>
      <!-- Palm -->
      <path d="M20 20 L55 10 L50 45 L15 40 Z" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Flat Extended Fingers pointing forward -->
      <rect x="50" y="8" width="45" height="10" rx="5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="52" y="18" width="48" height="10" rx="5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="48" y="28" width="44" height="10" rx="5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="44" y="38" width="36" height="9" rx="4.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <!-- Thumb folded slightly alongside -->
      <path d="M28 12 C35 5, 45 5, 48 12" stroke="#78350F" stroke-width="1.5" fill="none"/>
    </g>
  </g>
'''
    },

    "isl_please.svg": {
        "title": "Please",
        "category": "Courtesies",
        "cue": "Circular Rub on Chest",
        "footer": "Place open flat palm over center of chest/heart and rub in gentle clockwise circle.",
        "svg_content": '''
  <!-- Flat Palm Rubbing Chest in Circle -->
  <g transform="translate(120, 65)">
    <!-- Chest / Sternum Landmark -->
    <ellipse cx="80" cy="80" rx="75" ry="60" fill="#1E293B" stroke="#334155" stroke-width="2"/>
    <text x="80" y="35" font-family="sans-serif" font-size="9" font-weight="700" fill="#94A3B8" text-anchor="middle">CHEST / HEART AREA</text>

    <!-- Clockwise Circular Motion Indicator -->
    <path d="M80 35 A45 45 0 1 1 79 35" fill="none" stroke="#FBBF24" stroke-width="3" stroke-dasharray="6,4" marker-end="url(#arrowAmber)"/>
    <text x="135" y="85" font-family="sans-serif" font-size="10" font-weight="700" fill="#FBBF24">RUB CIRCLE</text>

    <!-- Flat Open Palm on Chest -->
    <g transform="translate(45, 40)">
      <!-- Palm body -->
      <path d="M20 40 L60 40 C65 60, 55 85, 20 85 Z" fill="url(#skinGrad)" stroke="#78350F" stroke-width="2"/>
      <!-- Fingers flat together -->
      <rect x="18" y="5" width="10" height="38" rx="5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="29" y="0" width="10" height="43" rx="5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="40" y="3" width="10" height="40" rx="5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="51" y="10" width="9" height="33" rx="4.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <!-- Thumb -->
      <path d="M15 45 C8 42, 5 35, 8 28 C12 28, 16 35, 18 42" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <!-- Palm Creases -->
      <path d="M25 55 C35 60, 45 58, 55 52" stroke="#B45309" stroke-width="1.2" fill="none"/>
    </g>
  </g>
'''
    },

    "isl_sorry.svg": {
        "title": "Sorry / Apologies",
        "category": "Courtesies",
        "cue": "Fist Rubbing on Heart",
        "footer": "Form a closed fist over your heart and rub in a gentle clockwise circle with apologetic look.",
        "svg_content": '''
  <!-- Fist Rubbing Chest in Circle -->
  <g transform="translate(120, 65)">
    <!-- Chest / Heart Landmark -->
    <ellipse cx="80" cy="80" rx="75" ry="60" fill="#1E293B" stroke="#334155" stroke-width="2"/>
    <text x="80" y="35" font-family="sans-serif" font-size="9" font-weight="700" fill="#94A3B8" text-anchor="middle">OVER CHEST / HEART</text>

    <!-- Clockwise Circular Arrow -->
    <path d="M80 32 A48 48 0 1 1 79 32" fill="none" stroke="#38BDF8" stroke-width="3" stroke-dasharray="6,4" marker-end="url(#arrowCyan)"/>
    <text x="135" y="85" font-family="sans-serif" font-size="10" font-weight="700" fill="#38BDF8">CIRCULAR RUB</text>

    <!-- Closed Fist Placed on Heart -->
    <g transform="translate(50, 48)">
      <rect x="15" y="15" width="46" height="42" rx="12" fill="url(#skinGrad)" stroke="#78350F" stroke-width="2"/>
      <!-- Folded Knuckles -->
      <line x1="20" y1="28" x2="52" y2="28" stroke="#92400E" stroke-width="1.8"/>
      <line x1="20" y1="39" x2="52" y2="39" stroke="#92400E" stroke-width="1.8"/>
      <!-- Wrapped Thumb -->
      <path d="M12 35 C12 20, 28 18, 42 20 C46 22, 42 32, 35 32 L15 32" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
    </g>
  </g>
'''
    },

    "isl_welcome.svg": {
        "title": "Welcome",
        "category": "Courtesies",
        "cue": "Open Palms Sweeping Inward",
        "footer": "Hold both open palms out facing upward/inward, sweep them warmly toward your chest.",
        "svg_content": '''
  <!-- Both Hands Sweeping Inward -->
  <g transform="translate(80, 65)">
    <!-- Left Hand Sweeping In -->
    <g transform="translate(20, 40)">
      <path d="M10 50 C30 50, 60 70, 75 90" fill="none" stroke="#2DD4BF" stroke-width="3" stroke-dasharray="4,3" marker-end="url(#arrowTeal)"/>
      <!-- Open Palm -->
      <path d="M0 20 L25 5 L35 35 L10 45 Z" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="25" y="2" width="28" height="8" rx="4" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.2"/>
      <rect x="27" y="11" width="30" height="8" rx="4" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.2"/>
      <rect x="25" y="20" width="28" height="8" rx="4" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.2"/>
    </g>

    <!-- Right Hand Sweeping In (Mirrored) -->
    <g transform="translate(160, 40)">
      <path d="M65 50 C45 50, 15 70, 0 90" fill="none" stroke="#2DD4BF" stroke-width="3" stroke-dasharray="4,3" marker-end="url(#arrowTeal)"/>
      <!-- Open Palm -->
      <path d="M75 20 L50 5 L40 35 L65 45 Z" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="22" y="2" width="28" height="8" rx="4" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.2"/>
      <rect x="18" y="11" width="30" height="8" rx="4" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.2"/>
      <rect x="22" y="20" width="28" height="8" rx="4" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.2"/>
    </g>

    <text x="120" y="145" font-family="sans-serif" font-size="11" font-weight="700" fill="#2DD4BF" text-anchor="middle">SWEEP INWARD TOWARDS CHEST</text>
  </g>
'''
    },

    "isl_water.svg": {
        "title": "Water",
        "category": "Basic Needs",
        "cue": "'W' Handshape at Lips",
        "footer": "Form 'W' handshape (3 middle fingers upright, thumb holding pinky), tap index near lips.",
        "svg_content": '''
  <!-- W-Handshape at Lips -->
  <g transform="translate(100, 60)">
    <!-- Lips / Face Profile Landmark -->
    <path d="M40 25 C55 35, 55 55, 40 70" stroke="#475569" stroke-width="2.5" fill="none"/>
    <text x="15" y="50" font-family="sans-serif" font-size="9" font-weight="700" fill="#94A3B8">LIPS</text>

    <!-- Tapping Motion Indicator -->
    <circle cx="58" cy="50" r="14" fill="none" stroke="#38BDF8" stroke-width="2" stroke-dasharray="3,2"/>
    <path d="M90 35 L65 48" stroke="#38BDF8" stroke-width="2.5" marker-end="url(#arrowCyan)"/>

    <!-- 'W' Handshape -->
    <g transform="translate(85, 30)">
      <!-- Wrist -->
      <rect x="15" y="90" width="30" height="25" rx="5" fill="#D97706" stroke="#78350F" stroke-width="1.8"/>
      <!-- Palm -->
      <rect x="10" y="45" width="40" height="50" rx="10" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      
      <!-- 3 Fingers Spread Upward in 'W' Form -->
      <!-- Index -->
      <rect x="10" y="0" width="11" height="50" rx="5.5" transform="rotate(-10 10 0)" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Middle -->
      <rect x="25" y="-5" width="11" height="55" rx="5.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Ring -->
      <rect x="40" y="0" width="11" height="50" rx="5.5" transform="rotate(10 40 0)" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>

      <!-- Folded Pinky Held by Thumb -->
      <circle cx="48" cy="65" r="7" fill="#B45309" stroke="#78350F" stroke-width="1.2"/>
      <path d="M12 60 C22 68, 35 68, 45 62" stroke="#78350F" stroke-width="2" fill="none"/>
    </g>

    <!-- Water Drop Icon Badge -->
    <g transform="translate(180, 20)">
      <circle cx="15" cy="15" r="14" fill="#0369A1" stroke="#38BDF8" stroke-width="1.5"/>
      <path d="M15 5 C15 5, 8 16, 8 20 A7 7 0 0 0 22 20 C22 16, 15 5, 15 5 Z" fill="#38BDF8"/>
    </g>
  </g>
'''
    },

    "isl_food.svg": {
        "title": "Food / Eat",
        "category": "Basic Needs",
        "cue": "Morsel Grip to Mouth",
        "footer": "Bring all 5 fingertips and thumb together (cone/morsel grip), tap repeatedly near mouth.",
        "svg_content": '''
  <!-- Pinched Fingertips (Morsel Grip) to Mouth -->
  <g transform="translate(110, 60)">
    <!-- Lips Landmark -->
    <path d="M40 35 C55 45, 55 65, 40 75" stroke="#475569" stroke-width="2.5" fill="none"/>
    <text x="15" y="58" font-family="sans-serif" font-size="9" font-weight="700" fill="#94A3B8">MOUTH</text>

    <!-- Repeated Tap Towards Mouth -->
    <path d="M100 45 L55 55" stroke="#FBBF24" stroke-width="3" stroke-dasharray="4,2" marker-end="url(#arrowAmber)"/>
    <text x="70" y="35" font-family="sans-serif" font-size="10" font-weight="700" fill="#FBBF24">TAP 2-3x</text>

    <!-- Hand with Pinched Fingertips (Indian Eating Mudra) -->
    <g transform="translate(95, 45)">
      <!-- Wrist -->
      <rect x="45" y="45" width="28" height="35" rx="5" fill="#D97706" stroke="#78350F" stroke-width="1.8" transform="rotate(25 45 45)"/>
      <!-- Hand Base -->
      <path d="M40 25 C55 35, 60 55, 40 70 L25 50 Z" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Tapered Cone Fingers -->
      <path d="M0 35 L30 15 L35 30 L0 35 Z" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
      <path d="M0 35 L30 25 L35 45 L0 35 Z" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
      <circle cx="2" cy="35" r="5" fill="#FEF08A" stroke="#78350F" stroke-width="1"/>
    </g>

    <!-- Food Bowl Badge -->
    <g transform="translate(180, 25)">
      <circle cx="15" cy="15" r="14" fill="#854D0E" stroke="#FBBF24" stroke-width="1.5"/>
      <path d="M6 14 C6 22, 24 22, 24 14 Z" fill="#FBBF24"/>
    </g>
  </g>
'''
    },

    "isl_tea.svg": {
        "title": "Tea / Chai",
        "category": "Basic Needs",
        "cue": "Dip Pinched Fingers in Cup",
        "footer": "Cup non-dominant hand like a teacup; pinch dominant thumb & index to dip like a teabag.",
        "svg_content": '''
  <!-- Dipping Teabag / Sugar into Cupped Hand -->
  <g transform="translate(110, 65)">
    <!-- Base Hand (Cupped Saucer/Mug) -->
    <g transform="translate(10, 80)">
      <path d="M15 20 C15 45, 65 45, 65 20 L75 20 C85 20, 85 35, 75 35 L70 35" fill="url(#skinSec)" stroke="#475569" stroke-width="2"/>
      <text x="40" y="58" font-family="sans-serif" font-size="9" font-weight="700" fill="#94A3B8" text-anchor="middle">CUP HAND</text>
    </g>

    <!-- Dipping Down-Up Motion Arrow -->
    <path d="M50 40 L50 82" stroke="#38BDF8" stroke-width="2.5" stroke-dasharray="3,2" marker-end="url(#arrowCyan)"/>

    <!-- Dominant Pinched Hand (Dipping teabag) -->
    <g transform="translate(45, 10)">
      <!-- Wrist -->
      <rect x="25" y="0" width="22" height="25" rx="4" fill="#D97706" stroke="#78350F" stroke-width="1.5"/>
      <!-- Hand Base -->
      <rect x="20" y="20" width="30" height="25" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.5"/>
      <!-- Pinched Index & Thumb -->
      <path d="M22 40 C15 50, 10 65, 8 72 C14 74, 20 65, 26 50" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <path d="M30 40 C25 50, 20 65, 14 72" stroke="#78350F" stroke-width="1.5" fill="none"/>
    </g>
  </g>
'''
    },

    "isl_hungry.svg": {
        "title": "Hungry",
        "category": "Basic Needs",
        "cue": "Claw Stroking Down Torso",
        "footer": "Curve hand into claw shape; stroke downward from throat to stomach with tense expression.",
        "svg_content": '''
  <!-- Claw Hand Stroking Down from Throat to Belly -->
  <g transform="translate(110, 60)">
    <!-- Torso Silhouette -->
    <path d="M40 20 L40 145 C55 145, 85 145, 100 145 L100 20 Z" fill="#1E293B" stroke="#334155" stroke-width="2"/>
    <text x="70" y="40" font-family="sans-serif" font-size="9" font-weight="700" fill="#94A3B8" text-anchor="middle">THROAT</text>
    <text x="70" y="135" font-family="sans-serif" font-size="9" font-weight="700" fill="#94A3B8" text-anchor="middle">STOMACH</text>

    <!-- Downward Motion Trajectory -->
    <path d="M70 50 L70 120" stroke="#F59E0B" stroke-width="3.5" stroke-dasharray="5,3" marker-end="url(#arrowAmber)"/>

    <!-- Curved Claw Hand -->
    <g transform="translate(75, 55)">
      <!-- Wrist -->
      <rect x="35" y="15" width="25" height="18" rx="4" fill="#D97706" stroke="#78350F" stroke-width="1.5"/>
      <!-- Palm -->
      <path d="M35 15 C20 15, 10 30, 12 45 C25 45, 35 35, 35 15 Z" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.5"/>
      <!-- Curved Claw Fingers -->
      <path d="M12 25 C-5 25, -10 40, -5 45 C2 45, 5 35, 15 32" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <path d="M12 35 C-5 35, -10 50, -5 55 C2 55, 5 45, 15 42" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
    </g>
  </g>
'''
    },

    "isl_pain.svg": {
        "title": "Pain / Sick",
        "category": "Emergency / Medical",
        "cue": "2 Index Fingers Twisting",
        "footer": "Point both index fingers towards each other near pain site; twist wrists in opposite directions.",
        "svg_content": '''
  <!-- Two Index Fingers Pointing at Each Other + Pain Bolts -->
  <g transform="translate(80, 65)">
    <!-- Pain Lightning Bolt in Center -->
    <g transform="translate(100, 30)">
      <polygon points="12 0, 0 18, 10 18, 5 32, 22 12, 12 12" fill="#F43F5E" stroke="#FFF" stroke-width="1"/>
      <circle cx="10" cy="16" r="22" fill="none" stroke="#F43F5E" stroke-width="1.5" stroke-dasharray="3,3"/>
      <text x="10" y="48" font-family="sans-serif" font-size="9" font-weight="700" fill="#FDA4AF" text-anchor="middle">PAIN LOCUS</text>
    </g>

    <!-- Left Index Pointing Right -->
    <g transform="translate(10, 35)">
      <rect x="0" y="15" width="35" height="30" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Extended Index Finger -->
      <rect x="30" y="18" width="50" height="13" rx="6.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Twist Arrow -->
      <path d="M50 10 C58 5, 68 8, 70 15" stroke="#38BDF8" stroke-width="2" marker-end="url(#arrowCyan)"/>
    </g>

    <!-- Right Index Pointing Left -->
    <g transform="translate(145, 35)">
      <rect x="55" y="15" width="35" height="30" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Extended Index Finger -->
      <rect x="10" y="18" width="50" height="13" rx="6.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Twist Arrow -->
      <path d="M40 10 C32 5, 22 8, 20 15" stroke="#38BDF8" stroke-width="2" marker-end="url(#arrowCyan)"/>
    </g>
  </g>
'''
    },

    "isl_restroom.svg": {
        "title": "Restroom / Toilet",
        "category": "Navigation",
        "cue": "'T' Handshape Shaking",
        "footer": "Form 'T' handshape (thumb between index and middle knuckles), gently shake hand side to side.",
        "svg_content": '''
  <!-- T-Handshape Shaking Side to Side -->
  <g transform="translate(130, 60)">
    <!-- Side to Side Shake Indicator -->
    <path d="M25 40 L115 40" stroke="#38BDF8" stroke-width="3" marker-start="url(#arrowCyan)" marker-end="url(#arrowCyan)"/>
    <text x="70" y="28" font-family="sans-serif" font-size="10" font-weight="700" fill="#38BDF8" text-anchor="middle">SHAKE GENTLY</text>

    <!-- Fist with Thumb Protruding Between Index and Middle -->
    <g transform="translate(35, 50)">
      <!-- Wrist -->
      <rect x="22" y="90" width="32" height="30" rx="6" fill="#D97706" stroke="#78350F" stroke-width="2"/>
      <!-- Curled Fist Body -->
      <rect x="12" y="25" width="52" height="70" rx="16" fill="url(#skinGrad)" stroke="#78350F" stroke-width="2"/>
      
      <!-- Knuckle separations -->
      <line x1="12" y1="48" x2="64" y2="48" stroke="#92400E" stroke-width="1.8"/>
      <line x1="12" y1="68" x2="64" y2="68" stroke="#92400E" stroke-width="1.8"/>

      <!-- 'T' Protruding Thumb Tip -->
      <ellipse cx="38" cy="48" rx="10" ry="12" fill="url(#skinBase)" stroke="#78350F" stroke-width="2"/>
      <ellipse cx="38" cy="46" rx="4" ry="3" fill="#FEF08A"/>
    </g>

    <!-- Restroom Icon Badge -->
    <g transform="translate(135, 45)">
      <rect width="28" height="28" rx="6" fill="#0284C7"/>
      <text x="14" y="20" font-family="sans-serif" font-size="14" font-weight="900" fill="#FFF" text-anchor="middle">WC</text>
    </g>
  </g>
'''
    },

    "isl_where_location.svg": {
        "title": "Where? / Location",
        "category": "Questions",
        "cue": "Both Open Palms Sweeping",
        "footer": "Hold both open palms up at waist height; sweep both hands horizontally left and right.",
        "svg_content": '''
  <!-- Both Open Palms Sweeping Horizontally -->
  <g transform="translate(80, 65)">
    <!-- Horizontal Sweep Indicator -->
    <path d="M30 30 L210 30" stroke="#FBBF24" stroke-width="3" marker-start="url(#arrowAmber)" marker-end="url(#arrowAmber)"/>
    <text x="120" y="20" font-family="sans-serif" font-size="10" font-weight="700" fill="#FBBF24" text-anchor="middle">SWEEP LEFT & RIGHT TOGETHER</text>

    <!-- Left Open Palm Up -->
    <g transform="translate(20, 50)">
      <path d="M10 30 L10 65 L45 65 L55 30 Z" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <rect x="8" y="5" width="9" height="30" rx="4.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="19" y="0" width="9" height="35" rx="4.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="30" y="3" width="9" height="32" rx="4.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="41" y="8" width="8" height="27" rx="4" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <!-- Thumb Outward -->
      <path d="M10 40 C0 35, -5 25, 0 18 C5 18, 8 28, 10 35" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
    </g>

    <!-- Right Open Palm Up (Mirror) -->
    <g transform="translate(150, 50)">
      <path d="M45 30 L45 65 L10 65 L0 30 Z" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <rect x="38" y="5" width="9" height="30" rx="4.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="27" y="0" width="9" height="35" rx="4.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="16" y="3" width="9" height="32" rx="4.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="6" y="8" width="8" height="27" rx="4" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
      <!-- Thumb Outward -->
      <path d="M45 40 C55 35, 60 25, 55 18 C50 18, 47 28, 45 35" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
    </g>

    <!-- Question Mark Cue -->
    <text x="120" y="85" font-family="sans-serif" font-size="28" font-weight="900" fill="#38BDF8" text-anchor="middle">?</text>
  </g>
'''
    },

    "isl_how_are_you.svg": {
        "title": "How Are You?",
        "category": "Greetings",
        "cue": "Point You + Open Palms",
        "footer": "Step 1: Point forward (YOU) ➔ Step 2: Open both palms outward with questioning smile.",
        "svg_content": '''
  <!-- Step 1: Point Forward + Step 2: Open Palms -->
  <g transform="translate(70, 60)">
    <!-- Step 1 Box -->
    <g transform="translate(15, 20)">
      <circle cx="45" cy="45" r="40" fill="#1E293B" stroke="#0D9488" stroke-width="1.5"/>
      <!-- Hand pointing at viewer -->
      <circle cx="45" cy="45" r="18" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Index pointing forward (foreshortened cylinder) -->
      <ellipse cx="45" cy="45" rx="10" ry="8" fill="url(#skinBase)" stroke="#78350F" stroke-width="2"/>
      <ellipse cx="45" cy="43" rx="5" ry="3" fill="#FEF08A"/>
      <text x="45" y="75" font-family="sans-serif" font-size="9" font-weight="700" fill="#5EEAD4" text-anchor="middle">1. POINT "YOU"</text>
    </g>

    <!-- Sequence Arrow -->
    <path d="M110 65 L145 65" stroke="#FBBF24" stroke-width="3" marker-end="url(#arrowAmber)"/>

    <!-- Step 2 Box -->
    <g transform="translate(150, 10)">
      <circle cx="50" cy="55" r="45" fill="#1E293B" stroke="#38BDF8" stroke-width="1.5"/>
      <!-- Open Palms -->
      <rect x="25" y="45" width="22" height="28" rx="6" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.2"/>
      <rect x="52" y="45" width="22" height="28" rx="6" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.2"/>
      <path d="M20 50 C20 40, 30 40, 35 45" stroke="#38BDF8" stroke-width="2" marker-end="url(#arrowCyan)"/>
      <path d="M80 50 C80 40, 70 40, 65 45" stroke="#38BDF8" stroke-width="2" marker-end="url(#arrowCyan)"/>
      <text x="50" y="85" font-family="sans-serif" font-size="9" font-weight="700" fill="#7DD3FC" text-anchor="middle">2. TWIST "HOW"</text>
    </g>
  </g>
'''
    },

    "isl_what_is_your_name.svg": {
        "title": "What is Your Name?",
        "category": "Questions",
        "cue": "Your + Tap Name + What",
        "footer": "Open palm forward (YOUR) ➔ Tap two fingers on opposite hand (NAME) ➔ Open twist (WHAT).",
        "svg_content": '''
  <!-- 3-Step Sequence: YOUR + NAME (Tap) + WHAT -->
  <g transform="translate(60, 60)">
    <!-- Step 1: Open Palm (Your) -->
    <g transform="translate(10, 25)">
      <rect width="65" height="75" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1.2"/>
      <!-- Palm icon -->
      <rect x="22" y="20" width="20" height="35" rx="5" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.2"/>
      <rect x="20" y="8" width="6" height="15" rx="3" fill="url(#skinBase)"/>
      <rect x="27" y="5" width="6" height="18" rx="3" fill="url(#skinBase)"/>
      <rect x="34" y="8" width="6" height="15" rx="3" fill="url(#skinBase)"/>
      <text x="32" y="68" font-family="sans-serif" font-size="8" font-weight="700" fill="#94A3B8" text-anchor="middle">1. YOUR</text>
    </g>

    <!-- Step 2: Two Fingers Tap (Name) -->
    <g transform="translate(105, 25)">
      <rect width="70" height="75" rx="8" fill="#1E293B" stroke="#0D9488" stroke-width="1.5"/>
      <!-- H-shape fingers tapping -->
      <rect x="18" y="32" width="34" height="8" rx="4" fill="url(#skinSec)"/>
      <rect x="28" y="15" width="8" height="30" rx="4" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.2"/>
      <rect x="38" y="15" width="8" height="30" rx="4" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.2"/>
      <circle cx="37" cy="36" r="6" fill="none" stroke="#2DD4BF" stroke-width="1.5"/>
      <text x="35" y="68" font-family="sans-serif" font-size="8" font-weight="700" fill="#2DD4BF" text-anchor="middle">2. NAME (TAP)</text>
    </g>

    <!-- Step 3: Question Hand (What) -->
    <g transform="translate(205, 25)">
      <rect width="65" height="75" rx="8" fill="#1E293B" stroke="#FBBF24" stroke-width="1.5"/>
      <text x="32" y="38" font-family="sans-serif" font-size="22" font-weight="900" fill="#FBBF24" text-anchor="middle">?</text>
      <text x="32" y="68" font-family="sans-serif" font-size="8" font-weight="700" fill="#FBBF24" text-anchor="middle">3. WHAT?</text>
    </g>
  </g>
'''
    },

    "isl_nice_to_meet_you.svg": {
        "title": "Nice to Meet You",
        "category": "Greetings",
        "cue": "Index Fingers Meet + Good",
        "footer": "Bring both upright index fingers together until touching (MEET), then show thumbs-up.",
        "svg_content": '''
  <!-- Two Index Fingers Meeting + Thumbs Up -->
  <g transform="translate(80, 60)">
    <!-- Meet Movement Indicator -->
    <path d="M40 30 L85 30" stroke="#38BDF8" stroke-width="2.5" marker-end="url(#arrowCyan)"/>
    <path d="M160 30 L115 30" stroke="#38BDF8" stroke-width="2.5" marker-end="url(#arrowCyan)"/>

    <!-- Left Hand Index Upright -->
    <g transform="translate(45, 35)">
      <rect x="0" y="25" width="30" height="35" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <rect x="15" y="0" width="13" height="40" rx="6.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
    </g>

    <!-- Meeting Point Ripple -->
    <circle cx="100" cy="50" r="14" fill="none" stroke="#FBBF24" stroke-width="2" stroke-dasharray="3,2"/>
    <text x="100" y="80" font-family="sans-serif" font-size="9" font-weight="700" fill="#FBBF24" text-anchor="middle">MEET</text>

    <!-- Right Hand Index Upright -->
    <g transform="translate(125, 35)">
      <rect x="10" y="25" width="30" height="35" rx="8" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <rect x="12" y="0" width="13" height="40" rx="6.5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
    </g>

    <!-- Followed by Thumbs Up Badge -->
    <g transform="translate(185, 25)">
      <circle cx="20" cy="20" r="18" fill="#065F46" stroke="#34D399" stroke-width="1.5"/>
      <path d="M14 26 L14 18 C14 14, 18 12, 22 12 C24 16, 26 22, 26 26" fill="url(#skinBase)" stroke="#34D399" stroke-width="1.2"/>
    </g>
  </g>
'''
    },

    "isl_father.svg": {
        "title": "Father / Dad",
        "category": "Family",
        "cue": "Mustache Stroke Line",
        "footer": "Stroke dominant index finger or thumb horizontally across the upper lip (mustache gesture).",
        "svg_content": '''
  <!-- Mustache Stroke Above Upper Lip -->
  <g transform="translate(100, 60)">
    <!-- Face / Mouth Silhouette -->
    <ellipse cx="100" cy="80" rx="60" ry="50" fill="#1E293B" stroke="#334155" stroke-width="2"/>
    <!-- Upper lip line -->
    <path d="M75 85 Q100 95 125 85" stroke="#64748B" stroke-width="2" fill="none"/>

    <!-- Mustache Stroke Gesture -->
    <path d="M70 70 Q100 80 135 70" stroke="#FBBF24" stroke-width="5" stroke-linecap="round"/>
    <!-- Motion Arrow -->
    <path d="M80 58 L125 58" stroke="#38BDF8" stroke-width="3" marker-end="url(#arrowCyan)"/>
    <text x="100" y="48" font-family="sans-serif" font-size="10" font-weight="700" fill="#38BDF8" text-anchor="middle">STROKE MUSTACHE LINE</text>

    <!-- Hand Stroking -->
    <g transform="translate(115, 60)">
      <rect x="10" y="10" width="30" height="25" rx="6" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.5"/>
      <rect x="-10" y="10" width="26" height="10" rx="5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
    </g>
  </g>
'''
    },

    "isl_mother.svg": {
        "title": "Mother / Mom",
        "category": "Family",
        "cue": "Tap Lower Cheek / Chin",
        "footer": "Gently tap index and middle fingertips on the lower cheek or side of chin twice.",
        "svg_content": '''
  <!-- Tap on Cheek / Chin Line (Nose ring / Bindi line tradition) -->
  <g transform="translate(100, 60)">
    <!-- Face Cheek Contour -->
    <path d="M60 25 C90 40, 100 80, 80 120" stroke="#475569" stroke-width="2.5" fill="none"/>
    <text x="45" y="70" font-family="sans-serif" font-size="9" font-weight="700" fill="#94A3B8">CHEEK / CHIN</text>

    <!-- Tap Ripples on Cheek -->
    <circle cx="85" cy="75" r="14" fill="none" stroke="#F43F5E" stroke-width="2" opacity="0.8"/>
    <circle cx="85" cy="75" r="24" fill="none" stroke="#FDA4AF" stroke-width="1.5" stroke-dasharray="3,2"/>
    <text x="135" y="55" font-family="sans-serif" font-size="10" font-weight="700" fill="#FDA4AF">TAP CHEEK 2x</text>

    <!-- Hand with Index & Middle Fingertips Touching Cheek -->
    <g transform="translate(90, 65)">
      <!-- Wrist -->
      <rect x="35" y="30" width="25" height="30" rx="5" fill="#D97706" stroke="#78350F" stroke-width="1.8"/>
      <circle cx="45" cy="25" r="16" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.8"/>
      <!-- Index & Middle extended to cheek -->
      <rect x="-5" y="5" width="38" height="10" rx="5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
      <rect x="-3" y="16" width="36" height="10" rx="5" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.8"/>
    </g>
  </g>
'''
    },

    "isl_family.svg": {
        "title": "Family",
        "category": "Family",
        "cue": "Circular 'F' Handshapes",
        "footer": "Form 'F' shapes with both hands (thumb & index touching), draw a circle outward until pinkies meet.",
        "svg_content": '''
  <!-- Both Hands Drawing Enclosing Circle -->
  <g transform="translate(100, 60)">
    <!-- Enclosing Circular Trajectory -->
    <ellipse cx="100" cy="80" rx="65" ry="45" fill="none" stroke="#2DD4BF" stroke-width="2.5" stroke-dasharray="5,4"/>
    <path d="M100 35 L120 37" stroke="#2DD4BF" stroke-width="2.5" marker-end="url(#arrowTeal)"/>
    <path d="M100 125 L80 123" stroke="#2DD4BF" stroke-width="2.5" marker-end="url(#arrowTeal)"/>
    <text x="100" y="85" font-family="sans-serif" font-size="10" font-weight="700" fill="#2DD4BF" text-anchor="middle">ENCLOSING CIRCLE</text>

    <!-- Left Hand 'F' Shape -->
    <g transform="translate(45, 60)">
      <circle cx="15" cy="15" r="12" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.5"/>
      <circle cx="10" cy="10" r="6" fill="#090E1A" stroke="#78350F" stroke-width="1.5"/>
      <line x1="18" y1="5" x2="28" y2="-5" stroke="#78350F" stroke-width="2"/>
    </g>

    <!-- Right Hand 'F' Shape -->
    <g transform="translate(135, 60)">
      <circle cx="15" cy="15" r="12" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.5"/>
      <circle cx="20" cy="10" r="6" fill="#090E1A" stroke="#78350F" stroke-width="1.5"/>
      <line x1="12" y1="5" x2="2" y2="-5" stroke="#78350F" stroke-width="2"/>
    </g>
  </g>
'''
    },

    "isl_more.svg": {
        "title": "More",
        "category": "Basic Needs",
        "cue": "Flattened Cones Tapping",
        "footer": "Pinch all fingertips to thumbs on both hands (flattened-O) and tap fingertips together repeatedly.",
        "svg_content": '''
  <!-- Both Hands Tapping Fingertips Together -->
  <g transform="translate(90, 65)">
    <!-- Inward Tap Motion Arrows -->
    <path d="M50 45 L85 45" stroke="#FBBF24" stroke-width="3" marker-end="url(#arrowAmber)"/>
    <path d="M170 45 L135 45" stroke="#FBBF24" stroke-width="3" marker-end="url(#arrowAmber)"/>

    <!-- Left Flattened Cone Hand -->
    <g transform="translate(40, 30)">
      <rect x="0" y="5" width="28" height="25" rx="6" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.5"/>
      <path d="M25 5 L45 15 L25 25 Z" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
    </g>

    <!-- Collision / Tap Ripple -->
    <circle cx="110" cy="45" r="12" fill="none" stroke="#2DD4BF" stroke-width="2" stroke-dasharray="3,2"/>
    <text x="110" y="75" font-family="sans-serif" font-size="10" font-weight="700" fill="#2DD4BF" text-anchor="middle">TAP 2x</text>

    <!-- Right Flattened Cone Hand -->
    <g transform="translate(140, 30)">
      <rect x="15" y="5" width="28" height="25" rx="6" fill="url(#skinGrad)" stroke="#78350F" stroke-width="1.5"/>
      <path d="M18 5 L-2 15 L18 25 Z" fill="url(#skinBase)" stroke="#78350F" stroke-width="1.5"/>
    </g>
  </g>
'''
    }
}


def build_svg_file(filename, data):
    svg = (
        SVG_HEADER
        + card_frame(
            title=data["title"],
            category=data["category"],
            cue=data["cue"],
            steps="",
            footer_instruction=data["footer"],
        )
        + data["svg_content"]
        + SVG_FOOTER
    )
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)
    return filepath


def main():
    print(f"Generating anatomical SVGs in {OUTPUT_DIR}...")
    count = 0
    for filename, data in SIGNS_ART.items():
        fp = build_svg_file(filename, data)
        count += 1
        print(f"[{count}/28] Generated {filename} -> {data['title']}")
    print(f"Successfully created {count} anatomical ISL sign illustrations!")


if __name__ == "__main__":
    main()

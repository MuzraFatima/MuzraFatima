"""Shared drawing primitives for the Code Pet profile SVGs.

The mascot is drawn once here and reused everywhere, so it is literally the
same character in every pose and section.

Two rules this module exists to enforce:

1. A CSS ``transform`` animation REPLACES an element's ``transform``
   attribute. So anything animated is wrapped: an outer <g> carries the
   static placement, an inner <g class="..."> carries the animation.
2. XML comments may not contain ``--``, and non-ASCII characters are written
   as numeric entities, so the files survive any encoding.
"""

from __future__ import annotations

import random

# ----------------------------------------------------------------- palette

BG     = "#071A33"
CARD   = "#0E2A4D"
CYAN   = "#35D6FF"
YELLOW = "#FFD54A"
CREAM  = "#FFF0D6"
PINK   = "#FF9FB2"
TEXT   = "#FFFFFF"
MUTED  = "#9FB8D6"
GREEN  = "#4ADE80"

# The mascot: a round, chubby blue cat, matching the Code Pet reference.
CAT_LIGHT = "#7FD9FB"
CAT_MID   = "#45BCF0"
CAT_DARK  = "#1F93CC"
CAT_BELLY = "#D6F2FE"
CAT_LINE  = "#1878A8"

FONT = ("'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', "
        "Arial, sans-serif")
MONO = ("ui-monospace, SFMono-Regular, 'JetBrains Mono', 'Fira Code', "
        "Consolas, monospace")


def esc(text: str) -> str:
    """XML-escape and force ASCII so encoding can never corrupt a file."""
    out = []
    for ch in str(text):
        if ch == "&":
            out.append("&amp;")
        elif ch == "<":
            out.append("&lt;")
        elif ch == ">":
            out.append("&gt;")
        elif ch == '"':
            out.append("&quot;")
        elif ord(ch) < 128:
            out.append(ch)
        else:
            out.append("&#%d;" % ord(ch))
    return "".join(out)


# -------------------------------------------------------------------- defs

def defs(extra: str = "") -> str:
    return f"""  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="0.4" y2="1">
      <stop offset="0%" stop-color="#061629"/>
      <stop offset="55%" stop-color="{BG}"/>
      <stop offset="100%" stop-color="#0B2946"/>
    </linearGradient>
    <linearGradient id="ringGrad" x1="0" y1="1" x2="1" y2="0">
      <stop offset="0%" stop-color="{CYAN}"/>
      <stop offset="55%" stop-color="#7FE4FF"/>
      <stop offset="100%" stop-color="{YELLOW}"/>
    </linearGradient>
    <radialGradient id="horizonGlow" cx="50%" cy="0%" r="75%">
      <stop offset="0%" stop-color="{CYAN}" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="ringGlow" cx="50%" cy="50%" r="50%">
      <stop offset="58%" stop-color="{CYAN}" stop-opacity="0"/>
      <stop offset="86%" stop-color="{CYAN}" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="furGrad" cx="34%" cy="26%" r="82%">
      <stop offset="0%" stop-color="{CAT_LIGHT}"/>
      <stop offset="58%" stop-color="{CAT_MID}"/>
      <stop offset="100%" stop-color="{CAT_DARK}"/>
    </radialGradient>
    <radialGradient id="bellyGrad" cx="50%" cy="34%" r="70%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="{CAT_BELLY}"/>
    </radialGradient>
    <radialGradient id="cheekGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{PINK}" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="{PINK}" stop-opacity="0"/>
    </radialGradient>
    <filter id="softGlow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="7" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="textGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="starGlow" x="-120%" y="-120%" width="340%" height="340%">
      <feGaussianBlur stdDeviation="1.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <path id="sparkle" d="M0,-6 Q1.1,-1.1 6,0 Q1.1,1.1 0,6 Q-1.1,1.1 -6,0 Q-1.1,-1.1 0,-6 Z"/>
    <g id="paw">
      <ellipse cx="0" cy="2.6" rx="4.6" ry="3.7"/>
      <ellipse cx="-4.4" cy="-2.6" rx="1.9" ry="2.5"/>
      <ellipse cx="-1.5" cy="-4.4" rx="1.9" ry="2.5"/>
      <ellipse cx="1.5" cy="-4.4" rx="1.9" ry="2.5"/>
      <ellipse cx="4.4" cy="-2.6" rx="1.9" ry="2.5"/>
    </g>
    <g id="starBadge">
      <path d="M0,-11 L3.2,-3.6 L11,-3.1 L5.1,2 L6.9,9.7 L0,5.6 L-6.9,9.7 L-5.1,2 L-11,-3.1 L-3.2,-3.6 Z"/>
    </g>
{extra}  </defs>
"""


BASE_CSS = f""".f {{ font-family: {FONT}; }}
    .m {{ font-family: {MONO}; }}
    .cat {{ animation: float 4.6s ease-in-out infinite; }}
    .tail {{ transform-box: fill-box; transform-origin: 10% 85%; animation: swish 3.4s ease-in-out infinite; }}
    .earL {{ transform-box: fill-box; transform-origin: 50% 100%; animation: twitchL 7s ease-in-out infinite; }}
    .earR {{ transform-box: fill-box; transform-origin: 50% 100%; animation: twitchR 7s ease-in-out infinite; }}
    .eye {{ transform-box: fill-box; transform-origin: 50% 50%; animation: blink 5.8s ease-in-out infinite; }}
    .ringDash {{ animation: spin 30s linear infinite; }}
    .ringDot {{ animation: spin 22s linear infinite; }}
    .glowPulse {{ transform-box: fill-box; transform-origin: 50% 50%; animation: pulse 4.6s ease-in-out infinite; }}
    .breathe {{ transform-box: fill-box; transform-origin: 50% 90%; animation: breathe 3.8s ease-in-out infinite; }}
    .zz {{ transform-box: fill-box; transform-origin: 50% 100%; animation: zzz 3.4s ease-in-out infinite; }}
    .wave {{ transform-box: fill-box; transform-origin: 22% 88%; animation: wave 1.9s ease-in-out infinite; }}
    .stA, .stB, .stC {{ transform-box: fill-box; transform-origin: 50% 50%;
                        animation: twinkle 3.6s ease-in-out infinite; }}
    .stB {{ animation-duration: 4.4s; animation-delay: -1.2s; }}
    .stC {{ animation-duration: 5.2s; animation-delay: -2.4s; }}

    @keyframes float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px); }} }}
    @keyframes swish {{ 0%,100% {{ transform: rotate(-9deg); }} 50% {{ transform: rotate(11deg); }} }}
    @keyframes blink {{ 0%,91%,100% {{ transform: scaleY(1); }} 94% {{ transform: scaleY(0.08); }} 97% {{ transform: scaleY(1); }} }}
    @keyframes twitchL {{ 0%,86%,100% {{ transform: rotate(0); }} 90% {{ transform: rotate(8deg); }} 94% {{ transform: rotate(-3deg); }} }}
    @keyframes twitchR {{ 0%,88%,100% {{ transform: rotate(0); }} 92% {{ transform: rotate(-9deg); }} 96% {{ transform: rotate(3deg); }} }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    @keyframes pulse {{ 0%,100% {{ opacity: .5; transform: scale(1); }} 50% {{ opacity: 1; transform: scale(1.05); }} }}
    @keyframes breathe {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(1.035); }} }}
    @keyframes zzz {{ 0% {{ opacity: 0; transform: translateY(4px) scale(.8); }}
                      35% {{ opacity: 1; }}
                      100% {{ opacity: 0; transform: translateY(-14px) scale(1.15); }} }}
    @keyframes wave {{ 0%,100% {{ transform: rotate(-18deg); }} 50% {{ transform: rotate(12deg); }} }}
    @keyframes twinkle {{ 0%,100% {{ opacity: .45; transform: scale(.8); }} 50% {{ opacity: 1; transform: scale(1.2); }} }}

    @media (prefers-reduced-motion: reduce) {{
      .cat, .tail, .earL, .earR, .eye, .ringDash, .ringDot, .glowPulse,
      .breathe, .zz, .wave, .stA, .stB, .stC {{ animation: none !important; }}
    }}"""


def svg_open(w: int, h: int, title: str, desc: str, extra_defs: str = "",
             extra_css: str = "") -> str:
    css = BASE_CSS + ("\n    " + extra_css if extra_css else "")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-labelledby="t d">\n'
        f'  <title id="t">{esc(title)}</title>\n'
        f'  <desc id="d">{esc(desc)}</desc>\n'
        + defs(extra_defs)
        + f"  <style>\n    {css}\n  </style>\n"
    )


def svg_close() -> str:
    return "</svg>\n"


# ------------------------------------------------------------- backgrounds

def panel(w: int, h: int, radius: int = 24, horizon: bool = False) -> str:
    s = (f'  <rect x="0" y="0" width="{w}" height="{h}" rx="{radius}" fill="url(#bgGrad)"/>\n')
    if horizon:
        # soft planet horizon arc, as in the reference banner
        s += (f'  <ellipse cx="{w/2}" cy="{h + h*0.52:.0f}" rx="{w*0.78:.0f}" '
              f'ry="{h*0.72:.0f}" fill="url(#horizonGlow)"/>\n'
              f'  <path d="M{w*0.05:.0f},{h*0.93:.0f} Q{w/2},{h*0.76:.0f} '
              f'{w*0.95:.0f},{h*0.93:.0f}" fill="none" stroke="{CYAN}" '
              f'stroke-opacity=".24" stroke-width="2"/>\n')
    s += (f'  <rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="{radius - 1.5}" '
          f'fill="none" stroke="{CYAN}" stroke-opacity="0.22" stroke-width="3"/>\n')
    return s


def card(x, y, w, h, radius: int = 18, stroke: str = CYAN,
         opacity: float = 0.30) -> str:
    return (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{CARD}" '
            f'stroke="{stroke}" stroke-opacity="{opacity}" stroke-width="2"/>\n')


def stars(w: int, h: int, count: int = 12, seed: int = 7,
          avoid: tuple | None = None) -> str:
    rnd = random.Random(seed)
    colors = [CREAM, CYAN, YELLOW, "#FFFFFF", PINK]
    classes = ["stA", "stB", "stC"]
    rows, placed, guard = [], 0, 0
    while placed < count and guard < count * 40:
        guard += 1
        x = rnd.randint(18, w - 18)
        y = rnd.randint(16, h - 16)
        if avoid:
            ax, ay, aw, ah = avoid
            if ax - 14 <= x <= ax + aw + 14 and ay - 14 <= y <= ay + ah + 14:
                continue
        sc = round(rnd.uniform(0.5, 1.0), 2)
        rows.append(
            f'    <g transform="translate({x},{y}) scale({sc})" fill="{colors[placed % 5]}">'
            f'<g class="{classes[placed % 3]}"><use href="#sparkle"/></g></g>')
        placed += 1
    return '  <g filter="url(#starGlow)">\n' + "\n".join(rows) + "\n  </g>\n"


def star_dots(w: int, h: int, count: int = 22, seed: int = 5,
              avoid: tuple | None = None) -> str:
    """Plain twinkling dots, as on the reference banner (not 4-point stars)."""
    rnd = random.Random(seed)
    classes = ["stA", "stB", "stC"]
    rows, placed, guard = [], 0, 0
    while placed < count and guard < count * 40:
        guard += 1
        x = rnd.randint(14, w - 14)
        y = rnd.randint(14, h - 14)
        if avoid:
            ax, ay, aw, ah = avoid
            if ax - 10 <= x <= ax + aw + 10 and ay - 10 <= y <= ay + ah + 10:
                continue
        r = round(rnd.uniform(0.9, 2.1), 1)
        col = "#FFFFFF" if placed % 4 else CYAN
        op = round(rnd.uniform(0.35, 0.9), 2)
        rows.append(
            f'    <g transform="translate({x},{y})"><g class="{classes[placed % 3]}">'
            f'<circle cx="0" cy="0" r="{r}" fill="{col}" opacity="{op}"/></g></g>')
        placed += 1
    return "  <g>\n" + "\n".join(rows) + "\n  </g>\n"


def orbit_ring(cx: float, cy: float, r: float, dots: int = 4) -> str:
    """Glowing gradient ring with small travelling dots, as in the reference."""
    s = (f'  <circle cx="{cx}" cy="{cy}" r="{r * 1.26:.0f}" fill="url(#ringGlow)" class="glowPulse"/>\n'
         f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#ringGrad)" '
         f'stroke-width="5" stroke-linecap="round" filter="url(#softGlow)"/>\n'
         f'  <g transform="translate({cx},{cy})"><g class="ringDash">'
         f'<circle cx="0" cy="0" r="{r + 13:.0f}" fill="none" stroke="{YELLOW}" '
         f'stroke-opacity=".5" stroke-width="2" stroke-dasharray="2 14" '
         f'stroke-linecap="round"/></g></g>\n')
    import math
    inner = []
    for i in range(dots):
        a = (2 * math.pi * i) / dots
        dx, dy = r * math.cos(a), r * math.sin(a)
        col = YELLOW if i % 2 else CYAN
        inner.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="{5 if i % 2 else 4}" '
                     f'fill="{col}"/>')
    s += (f'  <g transform="translate({cx},{cy})"><g class="ringDot">'
          + "".join(inner) + "</g></g>\n")
    return s


# -------------------------------------------------------------- the mascot

def _eyes(mood: str) -> str:
    if mood == "sleepy":
        return (f'      <path d="M-26,-8 C-22,-1 -12,-1 -8,-8" fill="none" stroke="{CAT_LINE}" '
                f'stroke-width="3" stroke-linecap="round"/>\n'
                f'      <path d="M8,-8 C12,-1 22,-1 26,-8" fill="none" stroke="{CAT_LINE}" '
                f'stroke-width="3" stroke-linecap="round"/>')
    out = []
    for sx in (-17, 17):
        out.append(f"""      <g class="eye">
        <ellipse cx="{sx}" cy="-7" rx="11" ry="12.5" fill="#FFFFFF"/>
        <ellipse cx="{sx}" cy="-6" rx="6.6" ry="7.8" fill="#0B2B42"/>
        <circle cx="{sx - 2.6}" cy="-10.2" r="3.1" fill="#FFFFFF"/>
        <circle cx="{sx + 3.0}" cy="-1.8" r="1.6" fill="#FFFFFF" opacity=".9"/>
      </g>""")
    return "\n".join(out)


def _blob_face(mood: str) -> str:
    """Face only: big eyes, blush, small smile. No whiskers, matching the
    reference art, which keeps the silhouette clean at small sizes."""
    return f"""{_eyes(mood)}
      <ellipse cx="-31" cy="9" rx="11" ry="7" fill="url(#cheekGrad)"/>
      <ellipse cx="31" cy="9" rx="11" ry="7" fill="url(#cheekGrad)"/>
      <path d="M-7,10 C-4,14.5 4,14.5 7,10" fill="none" stroke="{CAT_LINE}"
            stroke-width="2.2" stroke-linecap="round"/>"""


_EARS = f"""      <g class="earL">
        <path d="M-40,-24 C-46,-44 -40,-57 -30,-56 C-23,-54 -18,-43 -15,-32 Z"
              fill="{CAT_MID}" stroke="{CAT_LINE}" stroke-width="2" stroke-linejoin="round"/>
        <path d="M-36,-29 C-40,-42 -35,-50 -30,-49 C-26,-47 -23,-40 -21,-34 Z"
              fill="{CAT_LIGHT}" opacity=".95"/>
      </g>
      <g class="earR">
        <path d="M40,-24 C46,-44 40,-57 30,-56 C23,-54 18,-43 15,-32 Z"
              fill="{CAT_MID}" stroke="{CAT_LINE}" stroke-width="2" stroke-linejoin="round"/>
        <path d="M36,-29 C40,-42 35,-50 30,-49 C26,-47 23,-40 21,-34 Z"
              fill="{CAT_LIGHT}" opacity=".95"/>
      </g>"""

# One round blob: head and body are a single ball, as in the reference art.
_BLOB = f"""      <ellipse cx="0" cy="48" rx="40" ry="8" fill="#031120" opacity=".45"/>
      <path d="M0,-44 C31,-44 53,-24 53,2 C53,28 33,47 0,47
                C-33,47 -53,28 -53,2 C-53,-24 -31,-44 0,-44 Z"
            fill="url(#furGrad)" stroke="{CAT_LINE}" stroke-width="2.2" stroke-linejoin="round"/>
      <ellipse cx="-18" cy="-20" rx="16" ry="11" fill="#FFFFFF" opacity=".16"/>"""

_PAWS = f"""      <ellipse cx="-17" cy="45" rx="10" ry="6" fill="{CAT_MID}"
               stroke="{CAT_LINE}" stroke-width="1.6"/>
      <ellipse cx="17" cy="45" rx="10" ry="6" fill="{CAT_MID}"
               stroke="{CAT_LINE}" stroke-width="1.6"/>"""

_TAIL = f"""      <g class="tail">
        <path d="M40,30 C64,34 80,22 82,2 C83,-12 74,-22 63,-22 C54,-22 48,-15 48,-7
                 C48,0 53,4 58,4 C62,4 65,2 66,-2 C68,10 58,20 42,19 Z"
              fill="url(#furGrad)" stroke="{CAT_LINE}" stroke-width="1.9" stroke-linejoin="round"/>
        <path d="M70,-16 C76,-10 76,2 70,8" fill="none" stroke="{CAT_BELLY}"
              stroke-width="2" stroke-linecap="round" stroke-opacity=".8"/>
      </g>"""


def cat(pose: str = "sitting", mood: str = "happy", scale: float = 1.0,
        x: float = 0, y: float = 0, animate: bool = True) -> str:
    """The mascot: a round, chubby blue cat. Same character in every pose."""
    cls = ' class="cat"' if animate else ""

    if pose == "sleeping":
        inner = f"""      <g class="breathe">
        <ellipse cx="0" cy="14" rx="56" ry="34" fill="url(#furGrad)"
                 stroke="{CAT_LINE}" stroke-width="2.1"/>
        <ellipse cx="4" cy="24" rx="30" ry="17" fill="url(#bellyGrad)" opacity=".85"/>
        <path d="M50,24 C70,18 76,2 66,-6 C58,-12 49,-8 48,0 C47,7 52,11 57,10
                 C53,18 44,22 36,21 Z" fill="url(#furGrad)" stroke="{CAT_LINE}"
              stroke-width="1.9" stroke-linejoin="round"/>
        <g transform="translate(-16,-6) scale(.86)">
          <path d="M-38,-16 C-43,-34 -38,-46 -30,-46 C-23,-44 -18,-33 -15,-22 Z"
                fill="url(#furGrad)" stroke="{CAT_LINE}" stroke-width="2" stroke-linejoin="round"/>
          <path d="M26,-18 C31,-36 26,-48 18,-48 C11,-46 6,-35 3,-24 Z"
                fill="url(#furGrad)" stroke="{CAT_LINE}" stroke-width="2" stroke-linejoin="round"/>
          <ellipse cx="-6" cy="2" rx="40" ry="35" fill="url(#furGrad)"
                   stroke="{CAT_LINE}" stroke-width="2.2"/>
          <ellipse cx="-30" cy="12" rx="10" ry="6.6" fill="url(#cheekGrad)"/>
          <ellipse cx="18" cy="12" rx="10" ry="6.6" fill="url(#cheekGrad)"/>
          <path d="M-28,0 C-24,7 -14,7 -10,0" fill="none" stroke="{CAT_LINE}"
                stroke-width="3" stroke-linecap="round"/>
          <path d="M2,0 C6,7 16,7 20,0" fill="none" stroke="{CAT_LINE}"
                stroke-width="3" stroke-linecap="round"/>
          <path d="M-5,16 L-8.6,12.2 L-1.4,12.2 Z" fill="{PINK}"/>
        </g>
      </g>
      <g class="f" fill="{CYAN}" opacity=".92">
        <g class="zz"><text x="56" y="-44" font-size="19" font-weight="700">z</text></g>
        <g class="zz" style="animation-delay:-1.1s"><text x="72" y="-58" font-size="14" font-weight="700">z</text></g>
        <g class="zz" style="animation-delay:-2.2s"><text x="86" y="-70" font-size="11" font-weight="700">z</text></g>
      </g>"""

    elif pose == "peeking":
        inner = f"""{_TAIL}
{_EARS}
{_BLOB}
{_blob_face(mood)}
      <ellipse cx="-34" cy="40" rx="12" ry="8" fill="url(#bellyGrad)"
               stroke="{CAT_LINE}" stroke-width="1.6"/>
      <ellipse cx="34" cy="40" rx="12" ry="8" fill="url(#bellyGrad)"
               stroke="{CAT_LINE}" stroke-width="1.6"/>
      <rect x="-72" y="44" width="144" height="11" rx="5.5" fill="{CYAN}" opacity=".55"/>"""

    elif pose == "playing":
        inner = f"""      <g transform="rotate(-8)">
{_TAIL}
{_EARS}
{_BLOB}
{_blob_face(mood)}
{_PAWS}
      </g>
      <g class="wave">
        <ellipse cx="-54" cy="2" rx="12" ry="8.5" fill="url(#bellyGrad)"
                 stroke="{CAT_LINE}" stroke-width="1.7" transform="rotate(-26 -54 2)"/>
      </g>
      <circle cx="62" cy="40" r="13" fill="{YELLOW}" opacity=".95"/>
      <path d="M52,40 C56,33 68,33 72,40 M52,40 C56,47 68,47 72,40" fill="none"
            stroke="#B98F10" stroke-width="1.5" stroke-linecap="round" opacity=".8"/>"""

    else:  # sitting - the banner pose, kept tail-free like the reference
        inner = f"""{_EARS}
{_BLOB}
{_blob_face(mood)}
{_PAWS}"""

    return (f'  <g transform="translate({x},{y}) scale({scale})">\n'
            f'    <g{cls}>\n{inner}\n    </g>\n  </g>\n')


# --------------------------------------------------------------- text bits

def text(x, y, s, size=16, fill=TEXT, weight="400", anchor="start",
         spacing=0, extra="", mono=False):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    cls = "m" if mono else "f"
    return (f'  <text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
            f'font-weight="{weight}"{a}{ls} class="{cls}"{extra}>{esc(s)}</text>\n')


def badge_pill(x, y, label, color, h=28, size=12.5, pad=14, dot=True):
    """A small chip: coloured dot plus label, as under the reference cat."""
    w = pad * 2 + (16 if dot else 0) + len(label) * size * 0.56
    s = (f'  <g>\n'
         f'    <rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" '
         f'fill="{color}" fill-opacity="0.14" stroke="{color}" stroke-opacity="0.7" '
         f'stroke-width="1.3"/>\n')
    tx = x + pad
    if dot:
        s += f'    <rect x="{tx:.1f}" y="{y + h/2 - 4.5:.1f}" width="9" height="9" rx="2.5" fill="{color}"/>\n'
        tx += 16
    s += (f'    <text x="{tx:.1f}" y="{y + h/2 + 4.3:.1f}" fill="{color}" font-size="{size}" '
          f'font-weight="600" class="f">{esc(label)}</text>\n  </g>\n')
    return s, w


def pill(x, y, label, idx, h=30, pad=15, size=13.5):
    accent = CYAN if idx % 2 == 0 else YELLOW
    w = pad * 2 + len(label) * size * 0.58
    return (
        f'  <g>\n'
        f'    <rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" '
        f'fill="{accent}" fill-opacity="0.13" stroke="{accent}" stroke-opacity="0.75" stroke-width="1.4"/>\n'
        f'    <text x="{x + w/2:.1f}" y="{y + h/2 + 4.6:.1f}" fill="{accent}" font-size="{size}" '
        f'font-weight="600" text-anchor="middle" class="f">{esc(label)}</text>\n'
        f'  </g>\n'
    ), w


def flow_pills(labels, x0, y0, max_w, gap=9, line_h=39):
    out, x, y = [], x0, y0
    for i, lab in enumerate(labels):
        s, w = pill(x, y, lab, i)
        if x + w > x0 + max_w and x > x0:
            x = x0
            y += line_h
            s, w = pill(x, y, lab, i)
        out.append(s)
        x += w + gap
    return "".join(out), (y - y0) + line_h


def paw_row(x, y, n=3, scale=0.9, gap=28):
    cols = [PINK, CYAN, YELLOW]
    return "".join(
        f'  <g transform="translate({x + i*gap},{y}) scale({scale})" '
        f'fill="{cols[i % 3]}" opacity=".9"><use href="#paw"/></g>\n'
        for i in range(n))

"""Shared drawing primitives for the Code Pet profile SVGs.

Every SVG in assets/ is produced from this module so the mascot is literally
the same character everywhere, only its pose, size and mood change.

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

FUR_LINE  = "#E4C89E"
FUR_LIGHT = "#FFFBF2"
NOSE_LINE = "#C9A77C"

FONT = ("'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', "
        "Arial, sans-serif")


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
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{BG}"/>
      <stop offset="55%" stop-color="#0B2140"/>
      <stop offset="100%" stop-color="{CARD}"/>
    </linearGradient>
    <radialGradient id="ringGlow" cx="50%" cy="50%" r="50%">
      <stop offset="58%" stop-color="{CYAN}" stop-opacity="0"/>
      <stop offset="86%" stop-color="{CYAN}" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="furGrad" cx="36%" cy="26%" r="80%">
      <stop offset="0%" stop-color="{FUR_LIGHT}"/>
      <stop offset="58%" stop-color="{CREAM}"/>
      <stop offset="100%" stop-color="#EDD5AE"/>
    </radialGradient>
    <radialGradient id="tailGrad" cx="30%" cy="30%" r="85%">
      <stop offset="0%" stop-color="#FFF8EA"/>
      <stop offset="65%" stop-color="{CREAM}"/>
      <stop offset="100%" stop-color="#E9CFA4"/>
    </radialGradient>
    <radialGradient id="irisGrad" cx="38%" cy="30%" r="74%">
      <stop offset="0%" stop-color="#AEF2FF"/>
      <stop offset="52%" stop-color="{CYAN}"/>
      <stop offset="100%" stop-color="#0E7FAD"/>
    </radialGradient>
    <radialGradient id="cheekGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{PINK}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="{PINK}" stop-opacity="0"/>
    </radialGradient>
    <filter id="softGlow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="textGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="starGlow" x="-120%" y="-120%" width="340%" height="340%">
      <feGaussianBlur stdDeviation="1.6" result="b"/>
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
    .cat {{ animation: float 4.6s ease-in-out infinite; }}
    .tail {{ transform-box: fill-box; transform-origin: 8% 86%; animation: swish 3.4s ease-in-out infinite; }}
    .earL {{ transform-box: fill-box; transform-origin: 50% 100%; animation: twitchL 7s ease-in-out infinite; }}
    .earR {{ transform-box: fill-box; transform-origin: 50% 100%; animation: twitchR 7s ease-in-out infinite; }}
    .eye {{ transform-box: fill-box; transform-origin: 50% 50%; animation: blink 5.8s ease-in-out infinite; }}
    .ringDash {{ animation: spin 26s linear infinite; }}
    .glowPulse {{ transform-box: fill-box; transform-origin: 50% 50%; animation: pulse 4.6s ease-in-out infinite; }}
    .breathe {{ transform-box: fill-box; transform-origin: 50% 90%; animation: breathe 3.8s ease-in-out infinite; }}
    .zz {{ transform-box: fill-box; transform-origin: 50% 100%; animation: zzz 3.4s ease-in-out infinite; }}
    .wave {{ transform-box: fill-box; transform-origin: 20% 90%; animation: wave 1.9s ease-in-out infinite; }}
    .stA, .stB, .stC {{ transform-box: fill-box; transform-origin: 50% 50%;
                        animation: twinkle 3.6s ease-in-out infinite; }}
    .stB {{ animation-duration: 4.4s; animation-delay: -1.2s; }}
    .stC {{ animation-duration: 5.2s; animation-delay: -2.4s; }}

    @keyframes float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px); }} }}
    @keyframes swish {{ 0%,100% {{ transform: rotate(-8deg); }} 50% {{ transform: rotate(10deg); }} }}
    @keyframes blink {{ 0%,91%,100% {{ transform: scaleY(1); }} 94% {{ transform: scaleY(0.08); }} 97% {{ transform: scaleY(1); }} }}
    @keyframes twitchL {{ 0%,86%,100% {{ transform: rotate(0); }} 90% {{ transform: rotate(8deg); }} 94% {{ transform: rotate(-3deg); }} }}
    @keyframes twitchR {{ 0%,88%,100% {{ transform: rotate(0); }} 92% {{ transform: rotate(-9deg); }} 96% {{ transform: rotate(3deg); }} }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    @keyframes pulse {{ 0%,100% {{ opacity: .55; transform: scale(1); }} 50% {{ opacity: 1; transform: scale(1.04); }} }}
    @keyframes breathe {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(1.035); }} }}
    @keyframes zzz {{ 0% {{ opacity: 0; transform: translateY(4px) scale(.8); }}
                      35% {{ opacity: 1; }}
                      100% {{ opacity: 0; transform: translateY(-14px) scale(1.15); }} }}
    @keyframes wave {{ 0%,100% {{ transform: rotate(-16deg); }} 50% {{ transform: rotate(14deg); }} }}
    @keyframes twinkle {{ 0%,100% {{ opacity: .5; transform: scale(.85); }} 50% {{ opacity: 1; transform: scale(1.2); }} }}

    @media (prefers-reduced-motion: reduce) {{
      .cat, .tail, .earL, .earR, .eye, .ringDash, .glowPulse,
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

def panel(w: int, h: int, radius: int = 24) -> str:
    return (
        f'  <rect x="0" y="0" width="{w}" height="{h}" rx="{radius}" fill="url(#bgGrad)"/>\n'
        f'  <rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="{radius - 1.5}" '
        f'fill="none" stroke="{CYAN}" stroke-opacity="0.22" stroke-width="3"/>\n'
    )


def card(x: float, y: float, w: float, h: float, radius: int = 18,
         stroke: str = CYAN, opacity: float = 0.30) -> str:
    return (
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{CARD}" '
        f'stroke="{stroke}" stroke-opacity="{opacity}" stroke-width="2"/>\n'
    )


def stars(w: int, h: int, count: int = 12, seed: int = 7,
          avoid: tuple | None = None) -> str:
    """Scatter twinkling sparkles, optionally avoiding a rect (x,y,w,h)."""
    rnd = random.Random(seed)
    colors = [CREAM, CYAN, YELLOW, CREAM, PINK]
    classes = ["stA", "stB", "stC"]
    rows, placed = [], 0
    guard = 0
    while placed < count and guard < count * 40:
        guard += 1
        x = rnd.randint(18, w - 18)
        y = rnd.randint(16, h - 16)
        if avoid:
            ax, ay, aw, ah = avoid
            if ax - 14 <= x <= ax + aw + 14 and ay - 14 <= y <= ay + ah + 14:
                continue
        sc = round(rnd.uniform(0.55, 1.05), 2)
        col = colors[placed % len(colors)]
        cls = classes[placed % 3]
        # outer group = placement, inner group = animation (never conflict)
        rows.append(
            f'    <g transform="translate({x},{y}) scale({sc})" fill="{col}">'
            f'<g class="{cls}"><use href="#sparkle"/></g></g>'
        )
        placed += 1
    return '  <g filter="url(#starGlow)">\n' + "\n".join(rows) + "\n  </g>\n"


# -------------------------------------------------------------- the mascot

def _eyes_open() -> str:
    out = []
    for sx in (-13, 13):
        hx1 = sx - 2.7 if sx < 0 else sx - 2.7
        hx2 = sx + 2.7
        out.append(f"""      <g class="eye">
        <ellipse cx="{sx}" cy="-28" rx="8.8" ry="9.8" fill="{BG}"/>
        <ellipse cx="{sx}" cy="-27" rx="6.8" ry="7.8" fill="url(#irisGrad)"/>
        <circle cx="{sx}" cy="-26.5" r="3.5" fill="#06182E"/>
        <circle cx="{hx1}" cy="-30.6" r="2.6" fill="{TEXT}"/>
        <circle cx="{hx2}" cy="-23.6" r="1.4" fill="{TEXT}" opacity=".85"/>
      </g>""")
    return "\n".join(out)


def _eyes_closed() -> str:
    return f"""      <path d="M-20,-28 C-17,-23 -9,-23 -6,-28" fill="none"
            stroke="{NOSE_LINE}" stroke-width="2.2" stroke-linecap="round"/>
      <path d="M6,-28 C9,-23 17,-23 20,-28" fill="none"
            stroke="{NOSE_LINE}" stroke-width="2.2" stroke-linecap="round"/>"""


def _face(mood: str) -> str:
    eyes = _eyes_closed() if mood == "sleepy" else _eyes_open()
    smile = (f'      <path d="M0,-13 L0,-10 M0,-10 C-2.6,-10 -4.4,-11.6 -4.6,-13.4 '
             f'M0,-10 C2.6,-10 4.4,-11.6 4.6,-13.4" fill="none" '
             f'stroke="{NOSE_LINE}" stroke-width="1.5" stroke-linecap="round"/>')
    return f"""      <ellipse cx="-22" cy="-16" rx="10.5" ry="7.2" fill="url(#cheekGrad)"/>
      <ellipse cx="22" cy="-16" rx="10.5" ry="7.2" fill="url(#cheekGrad)"/>
{eyes}
      <path d="M0,-13 L-3.4,-16.4 L3.4,-16.4 Z" fill="{PINK}" stroke="#F08097"
            stroke-width=".7" stroke-linejoin="round"/>
{smile}
      <g stroke="{FUR_LIGHT}" stroke-width="1.6" stroke-linecap="round" opacity=".92" fill="none">
        <path d="M-17,-15 C-28,-18 -37,-18 -46,-16"/>
        <path d="M-17,-10 C-28,-10 -37,-9 -46,-6"/>
        <path d="M17,-15 C28,-18 37,-18 46,-16"/>
        <path d="M17,-10 C28,-10 37,-9 46,-6"/>
      </g>"""


_HEAD = f"""      <path d="M0,-62 C19,-62 34,-50 37,-34 C39,-23 38,-13 33,-6
               C28,2 15,7 0,7 C-15,7 -28,2 -33,-6
               C-38,-13 -39,-23 -37,-34 C-34,-50 -19,-62 0,-62 Z"
            fill="url(#furGrad)" stroke="{FUR_LINE}" stroke-width="1.9" stroke-linejoin="round"/>
      <path d="M-9,-58 C-5,-66 -1,-67 2,-60 C4,-66 9,-64 10,-58 C5,-61 -3,-61 -9,-58 Z" fill="{FUR_LIGHT}"/>"""

_EARS = f"""      <g class="earL">
        <path d="M-33,-48 C-38,-66 -35,-82 -28,-85 C-21,-82 -14,-68 -11,-54 Z"
              fill="url(#furGrad)" stroke="{FUR_LINE}" stroke-width="1.8" stroke-linejoin="round"/>
        <path d="M-30,-52 C-33,-65 -30,-75 -26,-77 C-22,-74 -18,-65 -16,-56 Z" fill="{PINK}" opacity=".8"/>
      </g>
      <g class="earR">
        <path d="M33,-48 C38,-66 35,-82 28,-85 C21,-82 14,-68 11,-54 Z"
              fill="url(#furGrad)" stroke="{FUR_LINE}" stroke-width="1.8" stroke-linejoin="round"/>
        <path d="M30,-52 C33,-65 30,-75 26,-77 C22,-74 18,-65 16,-56 Z" fill="{PINK}" opacity=".8"/>
      </g>"""

_BODY = f"""      <path d="M-30,22 C-30,2 -16,-10 0,-10 C16,-10 30,2 30,22
               C30,34 24,43 16,46 C12,43 9,46 5,47 C1,48 -3,45 -7,47
               C-12,49 -17,44 -21,45 C-27,42 -30,32 -30,22 Z"
            fill="url(#furGrad)" stroke="{FUR_LINE}" stroke-width="1.8" stroke-linejoin="round"/>
      <path d="M-11,14 C-6,22 6,22 11,14 C9,26 -9,26 -11,14 Z" fill="{FUR_LIGHT}" opacity=".85"/>
      <ellipse cx="-11" cy="44" rx="8" ry="5.5" fill="{FUR_LIGHT}" stroke="{FUR_LINE}" stroke-width="1.4"/>
      <ellipse cx="11" cy="44" rx="8" ry="5.5" fill="{FUR_LIGHT}" stroke="{FUR_LINE}" stroke-width="1.4"/>"""

_TAIL = f"""      <g class="tail">
        <path d="M20,30 C44,36 62,28 68,10 C73,-6 66,-20 54,-23 C44,-25 36,-18 36,-9
                 C36,-2 41,3 47,3 C51,3 54,1 55,-3 C57,9 46,19 22,17 Z"
              fill="url(#tailGrad)" stroke="{FUR_LINE}" stroke-width="1.6" stroke-linejoin="round"/>
        <path d="M62,-13 C67,-6 66,4 61,10" fill="none" stroke="{FUR_LINE}"
              stroke-width="1.4" stroke-linecap="round" stroke-opacity=".75"/>
        <path d="M52,-19 C58,-16 61,-10 61,-4" fill="none" stroke="{FUR_LIGHT}"
              stroke-width="1.6" stroke-linecap="round" stroke-opacity=".7"/>
      </g>"""


def cat(pose: str = "sitting", mood: str = "happy", scale: float = 1.0,
        x: float = 0, y: float = 0, animate: bool = True) -> str:
    """The mascot. Same character in every pose; only the arrangement changes.

    Poses: sitting, sleeping, peeking, playing.
    Moods: happy, sleepy.
    """
    cls = ' class="cat"' if animate else ""

    if pose == "sleeping":
        inner = f"""      <g class="breathe">
        <ellipse cx="0" cy="12" rx="46" ry="30" fill="url(#furGrad)"
                 stroke="{FUR_LINE}" stroke-width="1.8"/>
        <path d="M42,20 C58,16 64,2 56,-6 C50,-12 42,-9 41,-2 C40,4 44,8 48,7
                 C45,14 38,17 30,17 Z" fill="url(#tailGrad)" stroke="{FUR_LINE}"
              stroke-width="1.6" stroke-linejoin="round"/>
        <g transform="translate(-14,-2) scale(.82)">
          <path d="M-30,-20 C-33,-34 -30,-46 -24,-48 C-18,-45 -13,-34 -11,-24 Z"
                fill="url(#furGrad)" stroke="{FUR_LINE}" stroke-width="1.8" stroke-linejoin="round"/>
          <path d="M-27,-24 C-29,-34 -26,-41 -23,-42 C-20,-40 -17,-33 -16,-26 Z" fill="{PINK}" opacity=".8"/>
          <path d="M24,-22 C29,-36 26,-48 20,-50 C14,-47 9,-36 7,-26 Z"
                fill="url(#furGrad)" stroke="{FUR_LINE}" stroke-width="1.8" stroke-linejoin="round"/>
          <path d="M21,-26 C23,-36 20,-43 17,-44 C14,-42 11,-35 10,-28 Z" fill="{PINK}" opacity=".8"/>
          <ellipse cx="-2" cy="-2" rx="34" ry="30" fill="url(#furGrad)"
                   stroke="{FUR_LINE}" stroke-width="1.9"/>
          <ellipse cx="-20" cy="6" rx="9" ry="6" fill="url(#cheekGrad)"/>
          <ellipse cx="16" cy="6" rx="9" ry="6" fill="url(#cheekGrad)"/>
          <path d="M-20,-4 C-17,1 -9,1 -6,-4" fill="none" stroke="{NOSE_LINE}"
                stroke-width="2.2" stroke-linecap="round"/>
          <path d="M4,-4 C7,1 15,1 18,-4" fill="none" stroke="{NOSE_LINE}"
                stroke-width="2.2" stroke-linecap="round"/>
          <path d="M-1,10 L-4.4,6.6 L2.4,6.6 Z" fill="{PINK}"/>
        </g>
      </g>
      <g class="f" fill="{CYAN}" opacity=".9">
        <g class="zz"><text x="40" y="-44" font-size="17" font-weight="700">z</text></g>
        <g class="zz" style="animation-delay:-1.1s"><text x="54" y="-56" font-size="13" font-weight="700">z</text></g>
        <g class="zz" style="animation-delay:-2.2s"><text x="66" y="-66" font-size="10" font-weight="700">z</text></g>
      </g>"""

    elif pose == "peeking":
        inner = f"""{_TAIL}
{_EARS}
{_HEAD}
{_face(mood)}
      <ellipse cx="-26" cy="14" rx="9" ry="6" fill="{FUR_LIGHT}" stroke="{FUR_LINE}" stroke-width="1.4"/>
      <ellipse cx="26" cy="14" rx="9" ry="6" fill="{FUR_LIGHT}" stroke="{FUR_LINE}" stroke-width="1.4"/>
      <rect x="-54" y="18" width="108" height="9" rx="4.5" fill="{CYAN}" opacity=".55"/>"""

    elif pose == "playing":
        inner = f"""      <g transform="rotate(-9)">
{_TAIL}
{_EARS}
{_HEAD}
{_face(mood)}
{_BODY}
      </g>
      <g class="wave">
        <ellipse cx="-36" cy="4" rx="9" ry="7" fill="{FUR_LIGHT}"
                 stroke="{FUR_LINE}" stroke-width="1.5" transform="rotate(-24 -36 4)"/>
      </g>
      <circle cx="46" cy="40" r="11" fill="{YELLOW}" opacity=".92"/>
      <path d="M38,40 C42,34 50,34 54,40 M38,40 C42,46 50,46 54,40" fill="none"
            stroke="#B98F10" stroke-width="1.4" stroke-linecap="round" opacity=".8"/>"""

    else:  # sitting
        inner = f"""{_TAIL}
{_EARS}
{_BODY}
{_HEAD}
{_face(mood)}"""

    return (f'  <g transform="translate({x},{y}) scale({scale})">\n'
            f'    <g{cls}>\n{inner}\n    </g>\n  </g>\n')


# --------------------------------------------------------------- text bits

def text(x, y, s, size=16, fill=TEXT, weight="400", anchor="start",
         spacing=0, extra=""):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'  <text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
            f'font-weight="{weight}"{a}{ls} class="f"{extra}>{esc(s)}</text>\n')


def pill(x, y, label, idx, h=30, pad=15, size=13.5):
    """Tech-stack pill, alternating cyan and yellow."""
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
    """Lay pills out in wrapping rows. Returns (svg, total_height)."""
    out, x, y, start = [], x0, y0, 0
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
    out = []
    for i in range(n):
        out.append(f'  <g transform="translate({x + i*gap},{y}) scale({scale})" '
                   f'fill="{cols[i % 3]}" opacity=".9"><use href="#paw"/></g>\n')
    return "".join(out)

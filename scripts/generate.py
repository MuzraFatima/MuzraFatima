#!/usr/bin/env python3
"""Generate the Code Pet profile SVGs from real GitHub data.

Run:  python scripts/generate.py            (writes assets/*.svg)
      python scripts/generate.py --check     (fail if anything is invalid)

Auth: CODE_PET_TOKEN, else GITHUB_TOKEN, else GH_TOKEN.

All prose, project names, links and claims come from CONTENT below, which is
transcribed from README.md. Nothing here invents a skill, project, award or
number. The only values that change over time are fetched live from the
GitHub GraphQL API.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import templates as T  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
LOGIN = "MuzraFatima"
W = 880

# ---------------------------------------------------------------- content
# Transcribed from README.md. Do not add anything that is not already there.

ABOUT_LINES = [
    "Final-year B.Tech student in Artificial Intelligence & Machine Learning,",
    "based in Telangana, India. I build LLM-powered multi-agent systems,",
    "cost-aware model routing and mechanistic interpretability tooling",
    "- then measure whether they actually work.",
]
ABOUT_TAGS = ["Research-grade repos, not demos", "Agents & orchestration",
              "Interpretability & LLM internals", "Systems that run"]

TECH = [
    "Python", "Java", "C", "SQLite", "PostgreSQL",
    "PyTorch", "scikit-learn", "NumPy", "pandas", "SciPy", "Matplotlib", "Seaborn",
    "Anthropic Claude", "OpenAI", "Gemini", "Hugging Face", "Groq", "LiteLLM",
    "RAG", "Multi-agent systems",
    "FastAPI", "Node.js", "Docker", "SQLAlchemy", "Jupyter", "REST APIs", "WebSockets",
    "TypeScript", "React", "Tailwind CSS", "Vite", "three.js",
    "Git", "GitHub", "GitHub Actions", "VS Code", "Linux",
    "pytest", "Ruff", "pre-commit", "DVC",
]

FLAGSHIP = [
    {"slug": "horizonguard", "name": "HorizonGuard", "pose": "sitting",
     "tag": "Recoverability-aware early warning for long-horizon agents",
     "note": "Violation rate 65% to 10% against a 40% probability-only alarm",
     "url": "https://github.com/MuzraFatima/HorizonGuard"},
    {"slug": "neurolens", "name": "NeuroLens / TopoCircuit-SAE", "pose": "peeking",
     "tag": "Multi-parent feature absorption in sparse autoencoders",
     "note": "MPAbs benchmark and DR-SAE on real Pythia-70M activations, CPU only",
     "url": "https://github.com/MuzraFatima/NeuroLens"},
    {"slug": "compute-bazaar", "name": "Compute Bazaar", "pose": "playing",
     "tag": "A combinatorial compute market for agents that don't know their own value",
     "note": "Risk-adjusted XOR menus reach 78.0% of oracle welfare",
     "url": "https://github.com/MuzraFatima/Compute-bazar"},
    {"slug": "astrolm", "name": "AstroLM", "pose": "sleeping",
     "tag": "A decoder-only LM built from scratch, and what it memorizes",
     "note": "29.4M model reaches 1.060 test bits per byte, 23% below a 5-gram baseline",
     "url": "https://github.com/MuzraFatima/AstroLM"},
]

MORE = [
    {"slug": "whototrust", "name": "WhoToTrust", "pose": "sitting",
     "tag": "LabelTriage decides, vote by vote, error or real disagreement",
     "url": "https://github.com/MuzraFatima/WhoToTrust"},
    {"slug": "caar", "name": "Cost-Aware Agent Router", "pose": "playing",
     "tag": "Confidence-based multi-tier LLM routing, 85.3% evaluated cost savings",
     "url": "https://github.com/MuzraFatima/Cost-aware-agent"},
    {"slug": "jocky", "name": "JOCKY Forensics", "pose": "peeking",
     "tag": "A programming language for digital forensics, 540 tests passing",
     "url": "https://github.com/MuzraFatima/jocky-forensics"},
    {"slug": "phonecheck", "name": "PhoneCheck", "pose": "sleeping",
     "tag": "Smartphone-addiction risk prediction across nine models",
     "url": "https://github.com/MuzraFatima/Prediction-to-Smartphone-Addiction"},
    {"slug": "portfolio", "name": "Portfolio - The Galaxy of Intelligence", "pose": "sitting",
     "tag": "An explorable 3D galaxy where each project is a planet you fly to",
     "url": "https://github.com/MuzraFatima/portfolio"},
]

ACHIEVEMENTS = [
    "Winner, Smart India Hackathon 2026 (internal round), with JOCKY Forensics",
    "Published research paper, HBRP Publication, 2025",
    "Two pre-registered research studies: AstroLM and HorizonGuard",
]
CERTS = ["Anthropic", "AWS Academy", "Cisco Networking Academy",
         "freeCodeCamp", "TASK"]

CONTACT = [
    ("Email", "muzrafatima@gmail.com", "mailto:muzrafatima@gmail.com"),
    ("LinkedIn", "muzra-fatima", "https://www.linkedin.com/in/muzra-fatima-7150452bb/"),
    ("Portfolio", "muzraporfolio.vercel.app", "https://muzraporfolio.vercel.app/"),
]

# ------------------------------------------------------------------- data

QUERY = """
query($login:String!){
  user(login:$login){
    name login
    contributionsCollection{
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount } }
      }
    }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false){
      nodes{ languages(first:10){ edges{ size node{ name color } } } }
    }
  }
}
"""


def token() -> str:
    for name in ("CODE_PET_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"):
        v = os.environ.get(name)
        if v:
            print(f"  auth: using {name}")
            return v
    sys.exit("ERROR: no token. Set CODE_PET_TOKEN or GITHUB_TOKEN.")


def fetch() -> dict:
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": "bearer " + token(),
                 "Content-Type": "application/json",
                 "User-Agent": "code-pet-generator"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR: GitHub API returned HTTP {e.code}: {e.read()[:400]!r}")

    if payload.get("errors"):
        sys.exit("ERROR: GraphQL errors: %s" % json.dumps(payload["errors"])[:500])

    user = (payload.get("data") or {}).get("user")
    if not user or not user.get("contributionsCollection"):
        sys.exit(
            "ERROR: the token could not read contributionsCollection.\n"
            "  The default GITHUB_TOKEN often cannot read a user's contribution\n"
            "  calendar. Create a classic PAT with the 'read:user' scope and add\n"
            "  it to the repository as the secret CODE_PET_TOKEN.")
    return user


def summarise(user: dict) -> dict:
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    total = cal["totalContributions"]

    last7 = sum(d["contributionCount"] for d in days[-7:])
    weeks = cal["weeks"][-13:]
    week_active = [sum(d["contributionCount"] for d in w["contributionDays"]) > 0
                   for w in weeks]

    # pet stage from yearly contributions
    if total < 50:
        stage, pose, label = "fluffball", "sleeping", "Sleeping fluffball"
    elif total < 200:
        stage, pose, label = "kitten", "playing", "Kitten"
    elif total < 500:
        stage, pose, label = "young", "sitting", "Young cat"
    else:
        stage, pose, label = "adult", "sitting", "Adult cat"

    mood = "sleepy" if last7 == 0 else "happy"
    if mood == "sleepy":
        pose = "sleeping"

    langs: dict[tuple[str, str], int] = {}
    for repo in user["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            key = (e["node"]["name"], e["node"]["color"] or T.MUTED)
            langs[key] = langs.get(key, 0) + e["size"]
    tot = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
    top_langs = [{"name": k[0], "color": k[1], "pct": 100.0 * v / tot}
                 for k, v in top]

    nz = [d for d in days if d["contributionCount"] > 0]
    return {
        "total": total, "last7": last7, "mood": mood, "stage": stage,
        "pose": pose, "stage_label": label,
        "week_active": week_active,
        "weeks_active": sum(week_active),
        "langs": top_langs,
        "last_day": nz[-1]["date"] if nz else None,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }

# -------------------------------------------------------------- the pages


def write(name: str, body: str) -> Path:
    ASSETS.mkdir(parents=True, exist_ok=True)
    p = ASSETS / name
    p.write_text(body, encoding="utf-8", newline="\n")
    return p


def hero() -> str:
    h = 280
    s = T.svg_open(W, h, "Code Pet. Muzra Fatima, Aspiring AI/ML Engineer",
                   "A fluffy cream cat mascot with big sparkly cyan eyes, pink cheeks, "
                   "upright ears and a bushy tail, floating inside a glowing cyan ring "
                   "on a deep navy starfield, beside the heading CODE PET at MuzraFatima, "
                   "the name Muzra Fatima, and the title Aspiring AI/ML Engineer.")
    s += T.panel(W, h, 28)
    s += T.stars(W, h, 13, seed=7, avoid=(44, 36, 208, 208))
    s += (f'  <circle cx="148" cy="140" r="104" fill="url(#ringGlow)" class="glowPulse"/>\n'
          f'  <circle cx="148" cy="140" r="86" fill="{T.CARD}" stroke="{T.CYAN}" '
          f'stroke-opacity="0.95" stroke-width="3" filter="url(#softGlow)"/>\n'
          f'  <g transform="translate(148,140)"><g class="ringDash">'
          f'<circle cx="0" cy="0" r="95" fill="none" stroke="{T.YELLOW}" stroke-opacity="0.65" '
          f'stroke-width="2" stroke-dasharray="3 13" stroke-linecap="round"/></g></g>\n')
    s += T.cat("sitting", "happy", 1.0, 138, 156)
    s += T.text(286, 92, "CODE PET  ·  @" + LOGIN, 15, T.CYAN, "600",
                spacing=3.4, extra=' filter="url(#textGlow)"')
    s += T.text(284, 150, "Muzra Fatima", 46, T.TEXT, "700", spacing=0.4)
    s += T.text(286, 188, "Aspiring AI/ML Engineer", 21, T.YELLOW, "500", spacing=0.6)
    s += T.paw_row(292, 214)
    s += (f'  <line x1="372" y1="213" x2="828" y2="213" stroke="{T.MUTED}" '
          f'stroke-opacity=".35" stroke-width="1.6" stroke-linecap="round"/>\n')
    return s + T.svg_close()


def about() -> str:
    # Lay the pills out first so the card and canvas can be sized to fit them,
    # instead of clipping the last row.
    pills_y = 192
    pills, pills_h = T.flow_pills(ABOUT_TAGS, 206, pills_y, 620, gap=8, line_h=34)
    card_y, card_pad = 26, 20
    card_h = (pills_y - card_y) + pills_h + card_pad
    h = int(card_y + card_h + 26)

    s = T.svg_open(W, h, "About Muzra Fatima",
                   "A small cream cat sitting beside a card that reads: " +
                   " ".join(ABOUT_LINES))
    s += T.panel(W, h, 24)
    s += T.stars(W, h, 7, seed=11, avoid=(20, 20, 840, h - 40))
    s += T.card(176, card_y, 678, card_h)
    s += T.cat("sitting", "happy", 0.62, 92, card_y + card_h / 2 + 14)
    s += T.text(206, 64, "About Me", 23, T.CYAN, "700")
    s += T.paw_row(330, 57, 3, 0.62, 19)
    for i, line in enumerate(ABOUT_LINES):
        s += T.text(206, 100 + i * 25, line, 15, T.TEXT if i < 3 else T.MUTED, "400")
    return s + pills + T.svg_close()


def tech() -> str:
    pills, used = T.flow_pills(TECH, 36, 86, W - 72, gap=9, line_h=40)
    h = 86 + used + 28
    s = T.svg_open(W, h, "Tech stack",
                   "Rounded pills alternating cyan and yellow listing: " + ", ".join(TECH))
    s += T.panel(W, h, 24)
    s += T.text(36, 56, "Tech Stack", 23, T.CYAN, "700")
    s += T.paw_row(176, 49, 3, 0.62, 19)
    return s + pills + T.svg_close()


def project(p: dict, flagship: bool) -> str:
    h = 152 if flagship else 120
    desc = (f"A clickable card for the project {p['name']}: {p['tag']}. "
            f"Decorated with the cream cat mascot in a {p['pose']} pose.")
    s = T.svg_open(W, h, p["name"], desc)
    s += T.panel(W, h, 22)
    s += T.stars(W, h, 4, seed=sum(map(ord, p["slug"])), avoid=(18, 14, 844, h - 28))
    scale = 0.52 if flagship else 0.44
    cy = h / 2 + (16 if p["pose"] == "sitting" else 6)
    s += T.cat(p["pose"], "happy", scale, 84, cy)
    x = 168
    s += T.text(x, 50 if flagship else 46, p["name"], 21 if flagship else 18,
                T.TEXT, "700")
    s += T.text(x, 78 if flagship else 74, p["tag"], 14, T.CYAN, "500")
    if flagship and p.get("note"):
        s += T.text(x, 104, p["note"], 13, T.MUTED, "400")
    y_cta = 130 if flagship else 100
    s += (f'  <rect x="{x}" y="{y_cta - 17}" width="150" height="25" rx="12.5" '
          f'fill="{T.YELLOW}" fill-opacity=".14" stroke="{T.YELLOW}" '
          f'stroke-opacity=".7" stroke-width="1.3"/>\n')
    s += T.text(x + 75, y_cta, "View repository", 12.5, T.YELLOW, "600", anchor="middle")
    return s + T.svg_close()


def stats_contributions(d: dict) -> str:
    h = 236
    s = T.svg_open(W, h, "Yearly contributions and pet stage",
                   f"{d['total']} contributions in the last year. The pet is a "
                   f"{d['stage_label'].lower()} and is {d['mood']}.")
    s += T.panel(W, h, 24)
    s += T.stars(W, h, 8, seed=23, avoid=(40, 30, 800, 176))
    s += (f'  <circle cx="132" cy="118" r="88" fill="url(#ringGlow)" class="glowPulse"/>\n'
          f'  <circle cx="132" cy="118" r="72" fill="{T.CARD}" stroke="{T.CYAN}" '
          f'stroke-opacity=".9" stroke-width="2.5"/>\n')
    s += T.cat(d["pose"], d["mood"], 0.72,
               126, 132 if d["pose"] != "sleeping" else 124)
    s += T.text(252, 62, "Contributions this year", 15, T.MUTED, "500", spacing=1.2)
    s += T.text(250, 126, f"{d['total']:,}", 58, T.TEXT, "700")
    badge = f"{d['stage_label']}  ·  {'happy' if d['mood']=='happy' else 'sleepy'}"
    bw = 20 + len(badge) * 8.0
    s += (f'  <rect x="250" y="146" width="{bw:.0f}" height="30" rx="15" '
          f'fill="{T.PINK}" fill-opacity=".16" stroke="{T.PINK}" stroke-opacity=".8" stroke-width="1.4"/>\n')
    s += T.text(250 + bw / 2, 166, badge, 14, T.PINK, "600", anchor="middle")
    s += T.text(252, 204, f"Last contribution: {d['last_day'] or 'none recorded'}"
                          f"   ·   {d['last7']} in the last 7 days", 12.5, T.MUTED)
    return s + T.svg_close()


def stats_languages(d: dict) -> str:
    rows = d["langs"]
    h = 104 + len(rows) * 34
    s = T.svg_open(W, h, "Top languages",
                   "Top languages by bytes across owned repositories: " +
                   ", ".join(f"{r['name']} {r['pct']:.1f} percent" for r in rows))
    s += T.panel(W, h, 24)
    s += T.text(36, 56, "Top Languages", 23, T.CYAN, "700")
    s += T.paw_row(214, 49, 3, 0.62, 19)
    bar_x, bar_w = 190, 560
    for i, r in enumerate(rows):
        y = 92 + i * 34
        s += T.text(36, y + 14, r["name"], 14.5, T.TEXT, "600")
        s += (f'  <rect x="{bar_x}" y="{y}" width="{bar_w}" height="18" rx="9" '
              f'fill="{T.BG}" stroke="{T.MUTED}" stroke-opacity=".25" stroke-width="1"/>\n')
        fill_w = max(6.0, bar_w * r["pct"] / 100.0)
        s += (f'  <rect x="{bar_x}" y="{y}" width="{fill_w:.1f}" height="18" rx="9" '
              f'fill="{r["color"]}"/>\n')
        s += T.text(bar_x + bar_w + 16, y + 14, f"{r['pct']:.1f}%", 13.5, T.MUTED, "600")
    return s + T.svg_close()


def stats_streak(d: dict) -> str:
    h = 186
    act = d["week_active"]
    s = T.svg_open(W, h, "13-week contribution streak",
                   f"{d['weeks_active']} of the last 13 weeks had at least one "
                   f"contribution. Filled squares mark active weeks.")
    s += T.panel(W, h, 24)
    s += T.text(36, 54, "13-Week Streak", 23, T.CYAN, "700")
    s += T.paw_row(230, 47, 3, 0.62, 19)
    s += T.text(844, 54, f"{d['weeks_active']} / 13 weeks active", 14.5,
                T.YELLOW, "600", anchor="end")
    size, gap, x0, y0 = 52, 11, 36, 80
    for i, on in enumerate(act):
        x = x0 + i * (size + gap)
        fill = T.CYAN if on else T.BG
        op = "0.85" if on else "1"
        s += (f'  <rect x="{x}" y="{y0}" width="{size}" height="{size}" rx="13" '
              f'fill="{fill}" fill-opacity="{op}" stroke="{T.CYAN if on else T.MUTED}" '
              f'stroke-opacity="{0.9 if on else 0.3}" stroke-width="1.6"/>\n')
        if on:
            s += (f'  <g transform="translate({x + size/2},{y0 + size/2}) scale(.78)" '
                  f'fill="{T.BG}" opacity=".75"><use href="#paw"/></g>\n')
    s += T.text(36, y0 + size + 30, "A week counts when it has at least one contribution.",
                12.5, T.MUTED)
    return s + T.svg_close()


def achievements() -> str:
    h = 118 + len(ACHIEVEMENTS) * 38 + 68
    s = T.svg_open(W, h, "Achievements and certifications",
                   "Star badges listing: " + "; ".join(ACHIEVEMENTS) +
                   ". Certification issuers: " + ", ".join(CERTS) + ".")
    s += T.panel(W, h, 24)
    s += T.stars(W, h, 6, seed=31, avoid=(24, 24, 832, h - 48))
    s += T.text(36, 56, "Achievements", 23, T.CYAN, "700")
    s += T.paw_row(206, 49, 3, 0.62, 19)
    for i, a in enumerate(ACHIEVEMENTS):
        y = 94 + i * 38
        s += (f'  <g transform="translate(52,{y - 5}) scale(.92)" fill="{T.YELLOW}">'
              f'<use href="#starBadge"/></g>\n')
        s += T.text(80, y, a, 14.5, T.TEXT, "500")
    cy = 94 + len(ACHIEVEMENTS) * 38 + 16
    s += T.text(36, cy, "Certifications", 19, T.CYAN, "700")
    pills, _ = T.flow_pills(CERTS, 196, cy - 21, 630, gap=8, line_h=34)
    return s + pills + T.svg_close()


def contact() -> str:
    h = 214
    s = T.svg_open(W, h, "Contact Muzra Fatima",
                   "Paw-shaped buttons for " +
                   ", ".join(f"{k} {v}" for k, v, _ in CONTACT) +
                   ", with a waving cream cat.")
    s += T.panel(W, h, 24)
    s += T.stars(W, h, 7, seed=41, avoid=(24, 24, 832, 166))
    s += T.text(36, 56, "Let's talk", 23, T.CYAN, "700")
    s += T.text(36, 84, "Open to entry-level AI/ML and Generative AI engineering roles.",
                14.5, T.MUTED)
    x = 36
    for i, (label, value, _url) in enumerate(CONTACT):
        bw = 42 + len(value) * 7.6
        accent = [T.CYAN, T.PINK, T.YELLOW][i % 3]
        s += (f'  <rect x="{x:.0f}" y="112" width="{bw:.0f}" height="46" rx="23" '
              f'fill="{accent}" fill-opacity=".13" stroke="{accent}" '
              f'stroke-opacity=".75" stroke-width="1.6"/>\n')
        s += (f'  <g transform="translate({x + 24:.0f},135) scale(.95)" fill="{accent}">'
              f'<use href="#paw"/></g>\n')
        s += T.text(x + 42, 140, value, 14, accent, "600")
        x += bw + 14
    s += T.cat("playing", "happy", 0.46, 782, 128)
    s += T.text(36, 186, "Built with the Code Pet generator. Updated daily.", 12, T.MUTED)
    return s + T.svg_close()


# -------------------------------------------------------------- validation

def validate(paths: list[Path]) -> int:
    bad = 0
    for p in paths:
        txt = p.read_text(encoding="utf-8")
        try:
            ET.fromstring(txt)
        except ET.ParseError as e:
            print(f"  INVALID XML  {p.name}: {e}")
            bad += 1
            continue
        problems = []
        if "<title" not in txt or "<desc" not in txt:
            problems.append("missing title/desc")
        if "prefers-reduced-motion" not in txt:
            problems.append("missing reduced-motion guard")
        if "<script" in txt.lower():
            problems.append("contains script")
        if any(ord(c) > 127 for c in txt):
            problems.append("non-ASCII characters")
        if problems:
            print(f"  WARN  {p.name}: {', '.join(problems)}")
            bad += 1
        else:
            print(f"  ok    {p.name:34s} {len(txt)/1024:6.1f} KB")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if any SVG fails validation")
    args = ap.parse_args()

    print("Fetching GitHub data...")
    data = summarise(fetch())
    print(f"  {data['total']} contributions, stage={data['stage']}, "
          f"mood={data['mood']}, {data['weeks_active']}/13 weeks active")

    written = [write("hero.svg", hero()),
               write("about.svg", about()),
               write("tech.svg", tech())]
    for p in FLAGSHIP:
        written.append(write(f"project-{p['slug']}.svg", project(p, True)))
    for p in MORE:
        written.append(write(f"project-{p['slug']}.svg", project(p, False)))
    written += [write("stats-contributions.svg", stats_contributions(data)),
                write("stats-languages.svg", stats_languages(data)),
                write("stats-streak.svg", stats_streak(data)),
                write("achievements.svg", achievements()),
                write("contact.svg", contact())]

    print(f"\nWrote {len(written)} SVGs to {ASSETS}")
    print("Validating...")
    bad = validate(written)
    (ASSETS / "pet-state.json").write_text(
        json.dumps({k: v for k, v in data.items() if k != "week_active"} |
                   {"week_active": data["week_active"]}, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    if bad:
        print(f"\n{bad} file(s) had problems.")
        return 1 if args.check else 0
    print("\nAll SVGs valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

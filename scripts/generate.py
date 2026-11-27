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

try:
    from icons import ICONS  # brand logo paths, baked in - no network at runtime
except ImportError:  # pragma: no cover - icons.py is generated, not hand-written
    ICONS = {}

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

TECH_GROUPS = [
    ("Languages & core", ["Python", "Java", "C", "SQLite", "PostgreSQL"]),
    ("AI / ML", ["PyTorch", "scikit-learn", "NumPy", "pandas", "SciPy",
                 "Matplotlib", "Seaborn"]),
    ("LLM & agentic AI", ["Anthropic Claude", "OpenAI", "Gemini", "Hugging Face",
                          "Groq", "LiteLLM", "RAG", "Multi-agent systems"]),
    ("Backend & data", ["FastAPI", "Node.js", "Docker", "SQLAlchemy", "Jupyter",
                        "REST APIs", "WebSockets"]),
    ("Frontend", ["TypeScript", "React", "Tailwind CSS", "Vite", "three.js"]),
    ("Tooling & practice", ["Git", "GitHub", "GitHub Actions", "VS Code", "Linux",
                            "pytest", "Ruff", "pre-commit", "DVC"]),
]
TECH = [lab for _g, labs in TECH_GROUPS for lab in labs]

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
    name login bio avatarUrl
    followers{ totalCount }
    contributionsCollection{
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount } }
      }
    }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false,
                 orderBy:{field:PUSHED_AT, direction:DESC}){
      totalCount
      nodes{
        name description stargazerCount forkCount pushedAt
        primaryLanguage{ name color }
        languages(first:10){ edges{ size node{ name color } } }
      }
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
    weeks_all = cal["weeks"]
    days = [d for w in weeks_all for d in w["contributionDays"]]
    total = cal["totalContributions"]

    def week_sum(w):
        return sum(d["contributionCount"] for d in w["contributionDays"])

    last7 = sum(d["contributionCount"] for d in days[-7:])

    # Last 13 weeks, as the meter on the banner shows them.
    week_active = [week_sum(w) > 0 for w in weeks_all[-13:]]

    # Streak = consecutive active weeks counting back from the newest week.
    streak = 0
    for w in reversed(weeks_all):
        if week_sum(w) > 0:
            streak += 1
        else:
            break
    streak_13 = min(streak, 13)

    # Active weeks across the year; a full 52 is what "vivid" means.
    active_52 = sum(1 for w in weeks_all[-52:] if week_sum(w) > 0)

    # "Fed in a row": consecutive days with at least one contribution.
    fed = 0
    for d in reversed(days):
        if d["contributionCount"] > 0:
            fed += 1
        else:
            break

    # pet stage from yearly contributions
    if total < 50:
        stage, pose, label = "fluffball", "sleeping", "Sleeping fluffball"
    elif total < 200:
        stage, pose, label = "kitten", "playing", "Kitten"
    elif total < 500:
        stage, pose, label = "young", "sitting", "Young"
    else:
        stage, pose, label = "adult", "sitting", "Adult"

    mood = "sleepy" if last7 == 0 else "happy"
    if mood == "sleepy":
        pose = "sleeping"

    langs: dict[tuple[str, str], int] = {}
    for repo in user["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            key = (e["node"]["name"], e["node"]["color"] or T.MUTED)
            langs[key] = langs.get(key, 0) + e["size"]
    tot = sum(langs.values()) or 1
    top_langs = [{"name": k[0], "color": k[1], "pct": 100.0 * v / tot}
                 for k, v in sorted(langs.items(), key=lambda kv: -kv[1])[:5]]

    repos = [{"name": r["name"],
              "desc": (r["description"] or "").strip(),
              "stars": r["stargazerCount"], "forks": r["forkCount"],
              "lang": (r["primaryLanguage"] or {}).get("name") or "",
              "lang_color": (r["primaryLanguage"] or {}).get("color") or T.MUTED}
             for r in user["repositories"]["nodes"]
             if r["name"].lower() != LOGIN.lower()]

    # 26-week care log grid, newest last
    care = [[d["contributionCount"] for d in w["contributionDays"]]
            for w in weeks_all[-26:]]

    nz = [d for d in days if d["contributionCount"] > 0]
    return {
        "name": user.get("name") or LOGIN,
        "bio": (user.get("bio") or "").strip(),
        "followers": user["followers"]["totalCount"],
        "repo_count": user["repositories"]["totalCount"],
        "stars": sum(r["stars"] for r in repos),
        "total": total, "last7": last7, "mood": mood, "stage": stage,
        "pose": pose, "stage_label": label,
        "week_active": week_active,
        "weeks_active": sum(week_active),
        "streak": streak_13, "active_52": active_52, "fed": fed,
        "langs": top_langs, "repos": repos, "care": care,
        "last_day": nz[-1]["date"] if nz else None,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }

# -------------------------------------------------------------- the pages


def write(name: str, body: str) -> Path:
    ASSETS.mkdir(parents=True, exist_ok=True)
    p = ASSETS / name
    p.write_text(body, encoding="utf-8", newline="\n")
    return p


def hero(d: dict) -> str:
    """The Code Pet banner: pet, streak badge, languages, contributions."""
    h = 392
    langs = d["langs"][:4]

    s = T.svg_open(
        W, h, f"Code Pet. {d['name']}, @{LOGIN}",
        f"A round blue cat mascot with big eyes and pink cheeks sitting on a "
        f"starfield. Streak {d['streak']} of 13 weeks. {d['total']} contributions "
        f"this year, stage {d['stage_label'].lower()}. "
        f"{d['active_52']} of 52 weeks active. Top languages: "
        + ", ".join(x["name"] for x in langs) + ".")
    s += T.panel(W, h, 26, horizon=True)
    s += T.star_dots(W, h, 26, seed=5, avoid=(340, 96, 200, 170))

    s += T.text(34, 44, f"CODE PET · @{LOGIN.upper()}", 13, T.MUTED, "600",
                spacing=2.0, mono=True)

    badge = f"STREAK {d['streak']}/13"
    bw = 26 + len(badge) * 7.4
    s += (f'  <rect x="{W - 34 - bw:.0f}" y="28" width="{bw:.0f}" height="25" rx="12.5" '
          f'fill="{T.GREEN}" fill-opacity=".17" stroke="{T.GREEN}" stroke-opacity=".6" '
          f'stroke-width="1.2"/>\n')
    s += T.text(W - 34 - bw / 2, 45, badge, 11.5, T.GREEN, "700",
                anchor="middle", spacing=1.0, mono=True)

    s += T.cat(d["pose"], d["mood"], 0.95, 440,
               186 if d["pose"] != "sleeping" else 178)

    # language chips, centred under the pet
    widths = [T.badge_pill(0, 0, x["name"], x["color"])[1] for x in langs]
    cx = (W - (sum(widths) + 10 * (len(widths) - 1))) / 2
    for x, wpx in zip(langs, widths):
        s += T.badge_pill(cx, 262, x["name"], x["color"])[0]
        cx += wpx + 10

    s += (f'  <line x1="34" y1="306" x2="{W - 34}" y2="306" stroke="{T.MUTED}" '
          f'stroke-opacity=".18" stroke-width="1.4"/>\n')

    num = f"{d['total']:,}"
    s += T.text(34, 348, num, 31, T.TEXT, "700",
                extra=' font-style="italic"')
    s += T.text(34 + len(num) * 18.5, 348,
                f"contributions this year · {d['stage_label'].lower()}",
                14, T.MUTED, "500")
    s += T.text(34, 372, f"{d['active_52']}/52 active weeks to go vivid",
                11.5, T.MUTED, "400", mono=True, extra=' opacity=".75"')

    n, sq, gap = 13, 15, 5
    total = n * sq + (n - 1) * gap
    sx, sy = W - 34 - total, 340
    s += T.text(W - 34, 328, f"STREAK {d['streak']}/13 WEEKS", 10.5,
                T.MUTED, "600", anchor="end", spacing=1.2, mono=True)
    # The squares are the streak meter, so they must agree with the label:
    # the first `streak` of 13 are filled, not a scatter of active weeks.
    for i in range(n):
        on = i < d["streak"]
        s += (f'  <rect x="{sx + i * (sq + gap)}" y="{sy}" width="{sq}" height="{sq}" '
              f'rx="3.5" fill="{T.CYAN if on else "#13304F"}" '
              f'fill-opacity="{0.95 if on else 1}"/>\n')
    return s + T.svg_close()


def owner(d: dict) -> str:
    """The PET OWNER card."""
    h = 186
    bio = d["bio"] or "AI/ML Engineer"
    # wrap the bio to two lines without inventing any words
    words, lines, cur = bio.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 62:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    lines = lines[:2]

    s = T.svg_open(W, h, "Pet owner: " + d["name"],
                   f"Pet owner card for {d['name']}. {bio} "
                   f"{d['followers']} followers, {d['repo_count']} repositories, "
                   f"{d['stars']} stars.")
    s += T.panel(W, h, 22)
    s += T.star_dots(W, h, 7, seed=17, avoid=(24, 24, 700, 140))
    s += T.text(34, 46, "PET OWNER", 11.5, T.CYAN, "700", spacing=2.2, mono=True)
    s += T.text(34, 84, d["name"], 27, T.TEXT, "700")
    for i, ln in enumerate(lines):
        s += T.text(34, 112 + i * 21, ln, 13.5, T.MUTED, "400")
    s += T.text(34, 160,
                f"{d['followers']} followers  ·  {d['repo_count']} repositories"
                f"  ·  {d['stars']} stars", 12, T.MUTED, "500", mono=True)
    s += (f'  <circle cx="{W - 94}" cy="93" r="46" fill="{T.GREEN}" fill-opacity=".18" '
          f'stroke="{T.GREEN}" stroke-opacity=".55" stroke-width="2"/>\n')
    s += T.cat("sitting", d["mood"], 0.42, W - 94, 104)
    return s + T.svg_close()


def toy(idx: int, repo: dict, tagline: str) -> str:
    """A TOY card: one repository, with stars, forks and language."""
    h = 148
    s = T.svg_open(W, h, f"Toy {idx:02d}: {repo['name']}",
                   f"Project card {idx} for {repo['name']}. {tagline} "
                   f"{repo['stars']} stars, {repo['forks']} forks, "
                   f"language {repo['lang'] or 'not set'}.")
    s += T.panel(W, h, 20)
    s += T.star_dots(W, h, 5, seed=idx * 13 + 3, avoid=(24, 20, 700, 108))
    s += T.text(32, 42, f"TOY {idx:02d}", 11, T.CYAN, "700", spacing=2.2, mono=True)
    s += T.text(32, 76, repo["name"], 21, T.TEXT, "700", mono=True)
    s += T.text(32, 102, tagline, 13.5, T.MUTED, "400")
    s += T.text(32, 130, f"★ {repo['stars']}     ⑂ {repo['forks']}",
                12.5, T.MUTED, "600", mono=True)
    if repo["lang"]:
        s += (f'  <rect x="150" y="121" width="10" height="10" rx="2.5" '
              f'fill="{repo["lang_color"]}"/>\n')
        s += T.text(168, 130, repo["lang"], 12.5, T.MUTED, "600", mono=True)
    s += T.cat(["sitting", "playing", "peeking", "sleeping"][(idx - 1) % 4],
               "happy", 0.40, W - 92, 80)
    return s + T.svg_close()


def eats(d: dict) -> str:
    """WHAT IT EATS: language breakdown bars."""
    rows = d["langs"]
    h = 92 + len(rows) * 32 + 16
    s = T.svg_open(W, h, "What it eats: language breakdown",
                   "Language breakdown by bytes across owned repositories: " +
                   ", ".join(f"{r['name']} {r['pct']:.0f} percent" for r in rows))
    s += T.panel(W, h, 22)
    s += T.text(34, 46, "WHAT IT EATS", 11.5, T.CYAN, "700", spacing=2.2, mono=True)
    bar_x, bar_w = 232, 500
    for i, r in enumerate(rows):
        y = 78 + i * 32
        s += (f'  <rect x="34" y="{y}" width="11" height="11" rx="2.8" '
              f'fill="{r["color"]}"/>\n')
        s += T.text(56, y + 10, r["name"], 13.5, T.TEXT, "600")
        s += (f'  <rect x="{bar_x}" y="{y}" width="{bar_w}" height="11" rx="5.5" '
              f'fill="#13304F"/>\n')
        s += (f'  <rect x="{bar_x}" y="{y}" width="{max(8.0, bar_w * r["pct"] / 100):.1f}" '
              f'height="11" rx="5.5" fill="{r["color"]}"/>\n')
        s += T.text(W - 34, y + 10, f"{r['pct']:.0f}%", 12.5, T.MUTED, "600",
                    anchor="end", mono=True)
    return s + T.svg_close()


def carelog(d: dict) -> str:
    """CARE LOG: a 26-week contribution heatmap."""
    care = d["care"]
    cell, gap = 13, 4
    grid_w = len(care) * (cell + gap) - gap
    h = 70 + 7 * (cell + gap) + 40
    s = T.svg_open(W, h, "Care log: the last 26 weeks",
                   f"A heatmap of contributions over the last 26 weeks. "
                   f"Fed in a row: {d['fed']} day{'s' if d['fed'] != 1 else ''}.")
    s += T.panel(W, h, 22)
    s += T.text(34, 46, "CARE LOG · 26 WEEKS", 11.5, T.CYAN, "700",
                spacing=2.2, mono=True)
    peak = max((max(w) for w in care if w), default=0) or 1
    for xi, week in enumerate(care):
        for yi, n in enumerate(week):
            x = 34 + xi * (cell + gap)
            y = 68 + yi * (cell + gap)
            if n == 0:
                fill, op = "#13304F", "1"
            else:
                op = f"{min(1.0, 0.32 + 0.68 * (n / peak)):.2f}"
                fill = T.CYAN if n < peak * 0.6 else T.GREEN
            s += (f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" '
                  f'fill="{fill}" fill-opacity="{op}"/>\n')
    s += T.text(W - 34, 62, "FED IN A ROW", 10.5, T.MUTED, "600",
                anchor="end", spacing=1.6, mono=True)
    s += T.text(W - 34, 92, f"{d['fed']} day{'s' if d['fed'] != 1 else ''}",
                24, T.TEXT, "700", anchor="end")
    s += T.text(34, h - 20,
                "A filled square is a day with at least one contribution.",
                11.5, T.MUTED, "400", extra=' opacity=".75"')
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
    """Tech stack, grouped, each entry carrying its real brand logo."""
    y = 78
    body, flat = "", []
    for group, labels in TECH_GROUPS:
        body += T.text(36, y, group.upper(), 11.5, T.CYAN, "700",
                       spacing=2.0, mono=True)
        items = []
        for lab in labels:
            ic = ICONS.get(lab)
            if ic:
                items.append((lab, ic["d"], ic["color"]))
            else:
                # No published logo (Matplotlib, Seaborn, Groq, LiteLLM, VS Code
                # and the concept entries). Fall back to the theme rather than
                # guess at a brand colour or borrow another product's mark.
                items.append((lab, None,
                              T.CYAN if len(flat) % 2 == 0 else T.YELLOW))
            flat.append(lab)
        rows, used = T.flow_icon_pills(items, 36, y + 14, W - 72)
        body += rows
        y += 14 + used + 14
    h = y + 10

    s = T.svg_open(W, h, "Tech stack",
                   "Tech stack pills, each with its brand logo, grouped as: " +
                   "; ".join(f"{g}: {', '.join(l)}" for g, l in TECH_GROUPS) + ".")
    s += T.panel(W, h, 24)
    s += T.text(34, 46, "TECH STACK", 11.5, T.CYAN, "700", spacing=2.2, mono=True)
    return s + body + T.svg_close()


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

    written = [write("hero.svg", hero(data)),
               write("owner.svg", owner(data)),
               write("about.svg", about()),
               write("tech.svg", tech())]

    # TOY cards, one per project, in the order the README presents them.
    by_name = {r["name"].lower(): r for r in data["repos"]}
    for i, p in enumerate(FLAGSHIP + MORE, start=1):
        repo_key = p["url"].rsplit("/", 1)[-1].lower()
        repo = by_name.get(repo_key, {"name": repo_key, "stars": 0, "forks": 0,
                                      "lang": "", "lang_color": T.MUTED})
        repo = dict(repo, name=p["name"])
        written.append(write(f"toy-{i:02d}.svg", toy(i, repo, p["tag"])))
        p["asset"] = f"toy-{i:02d}.svg"

    written += [write("eats.svg", eats(data)),
                write("carelog.svg", carelog(data)),
                write("achievements.svg", achievements()),
                write("contact.svg", contact())]

    # Files from earlier layouts, and toy cards left over from a longer
    # project list, that the current design no longer uses.
    keep = {p.name for p in written}
    stale = ["stats-contributions.svg", "stats-streak.svg", "stats-languages.svg"]
    stale += [f"project-{p['slug']}.svg" for p in FLAGSHIP + MORE]
    stale += [p.name for p in ASSETS.glob("toy-*.svg")]
    for name in dict.fromkeys(stale):
        if name in keep:
            continue
        old = ASSETS / name
        if old.exists():
            old.unlink()
            print(f"  removed superseded {name}")

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

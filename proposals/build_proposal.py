#!/usr/bin/env python3
"""Build the Coach K UI/UX direction proposal PDF (WeasyPrint).

Standalone deliverable — does not touch app code. Recreates the four
direction mockups in print-ready HTML/CSS and embeds photos as data URIs.
"""

import base64
import mimetypes
from pathlib import Path

from weasyprint import HTML

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "frontend" / "public" / "images"
OUT = ROOT / "proposals" / "coach-k-ui-proposal.pdf"


def data_uri(name: str) -> str:
    p = IMAGES / name
    mime = mimetypes.guess_type(str(p))[0] or "image/jpeg"
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


IMG = {
    "training": data_uri("training-floor.jpg"),
    "chalk": data_uri("chalk-hands.jpg"),
    "speaking": data_uri("coach-dayan-speaking.jpg"),
    "hero": data_uri("hero-barbell.jpg"),
    "portrait": data_uri("coach-dayan.jpg"),
}


# ---- Phone mockups (print-faithful to the in-app previews) ----

def phone_iron() -> str:
    return f"""
    <div class="phone iron">
      <img class="ph-bg" src="{IMG['training']}"/>
      <div class="ph-fade-dark"></div>
      <div class="ph-content">
        <p class="mark red">COACH K</p>
        <h3 class="ph-h syne">Train with a coach who shows up.</h3>
        <p class="ph-sub">Dayan Kijege — from the DRC to Austin. Programs that adapt to you.</p>
        <div class="ph-btns">
          <span class="btn solid-red">Enter Coach K</span>
          <span class="btn ghost-light">My story</span>
        </div>
        <div class="ph-card dark">
          <div class="ph-nav">today &nbsp; chat &nbsp; plans &nbsp; stats</div>
          <p class="mini red">TODAY</p>
          <p class="ph-card-h syne">Day 2 — Lower Strength</p>
          <p class="ph-card-sub">Soft day · volume trimmed · 4 lifts</p>
          <div class="row dark-row"><span>Back Squat · 4×5</span><b class="red">Log</b></div>
          <div class="row dark-row"><span>RDL · 3×8</span><b class="red">Log</b></div>
        </div>
      </div>
    </div>"""


def phone_court() -> str:
    return f"""
    <div class="phone court">
      <img class="ph-bg court-bg" src="{IMG['chalk']}"/>
      <div class="ph-fade-light"></div>
      <div class="ph-content">
        <div class="court-top">
          <span class="court-word archivo">COACH K</span>
          <span class="pill green">Live</span>
        </div>
        <h3 class="ph-h archivo court-ink">Show up. Get scored. Get better.</h3>
        <p class="ph-sub court-mut">Dayan's court-to-weight-room system — readiness, load, honest feedback.</p>
        <span class="btn court-dark">Start today's session</span>
        <div class="ph-card white">
          <p class="mini green">TODAY · LOWER</p>
          <div class="court-stat"><b class="archivo">Readiness 78</b><span class="orange">ACWR 1.12</span></div>
          <div class="bar"><div class="bar-fill"></div></div>
          <div class="court-grid">
            <div class="court-chip">Squat</div>
            <div class="court-chip">RDL</div>
          </div>
        </div>
      </div>
    </div>"""


def phone_film() -> str:
    return f"""
    <div class="phone film">
      <img class="ph-bg film-bg" src="{IMG['speaking']}"/>
      <div class="ph-fade-film"></div>
      <div class="ph-content film-content">
        <p class="mark gold space">COACH K · DAYAN</p>
        <div class="film-bottom">
          <h3 class="ph-h space film-h">The cut that makes athletes.</h3>
          <p class="ph-sub film-mut">Science in the film room. Honest notes after every set.</p>
          <div class="film-btns">
            <span class="btn gold">Open session</span>
            <span class="film-link">Watch story</span>
          </div>
          <div class="film-rule"></div>
          <div class="film-meta"><span>DAY 2</span><span>SOFT DAY</span></div>
          <p class="film-day space">Lower · Strength bias</p>
          <div class="film-chips">
            <span class="fchip">Setup</span><span class="fchip on">Working</span><span class="fchip">Debrief</span>
          </div>
        </div>
      </div>
    </div>"""


def phone_signal() -> str:
    return f"""
    <div class="phone signal">
      <div class="sig-top">
        <img class="ph-bg sig-bg" src="{IMG['hero']}"/>
        <div class="sig-shade"></div>
        <div class="sig-rule"></div>
        <div class="sig-title">
          <p class="bebas sig-word">COACH K</p>
          <p class="sig-name">DAYAN KIJEGE</p>
        </div>
      </div>
      <div class="sig-body">
        <h3 class="bebas sig-h">NO FLUFF.<br/>JUST THE WORK.</h3>
        <p class="sig-sub">Periodized plans, readiness gates, and cues you can run tonight.</p>
        <div class="sig-line"></div>
        <div class="sig-grid">
          <div class="sig-stat"><span class="bebas">78</span><small>READY</small></div>
          <div class="sig-stat"><span class="bebas">1.1</span><small>ACWR</small></div>
          <div class="sig-stat"><span class="bebas">4</span><small>LIFTS</small></div>
        </div>
        <span class="sig-btn bebas">ENTER SESSION →</span>
      </div>
    </div>"""


def direction_page(num, name, mockup, positioning, best_for, strengths, watchouts, palette, type_line, moment) -> str:
    swatches = "".join(
        f'<span class="sw" style="background:{c}"></span>' for c in palette
    )
    strong = "".join(f"<li>{s}</li>" for s in strengths)
    watch = "".join(f"<li>{w}</li>" for w in watchouts)
    return f"""
    <section class="page dir">
      <div class="dir-grid">
        <div class="dir-mock">{mockup}</div>
        <div class="dir-copy">
          <p class="kicker">Direction 0{num}</p>
          <h2 class="dir-name syne">{name}</h2>
          <p class="positioning">{positioning}</p>

          <p class="lbl">The moment it creates</p>
          <p class="moment">"{moment}"</p>

          <div class="two">
            <div>
              <p class="lbl good">Strengths</p>
              <ul class="list">{strong}</ul>
            </div>
            <div>
              <p class="lbl warn">Watch-outs</p>
              <ul class="list">{watch}</ul>
            </div>
          </div>

          <p class="lbl">Best for</p>
          <p class="bestfor">{best_for}</p>

          <div class="meta-row">
            <div class="palette">{swatches}</div>
            <p class="type">{type_line}</p>
          </div>
        </div>
      </div>
    </section>"""


PAGES = [
    direction_page(
        1, "Iron Forge",
        phone_iron(),
        "A refinement of what you have — the dark gym with signal red — but with real hierarchy, one clear action per screen, and a stronger brand stamp.",
        "Positioning Coach K as a serious, private, premium coaching app for committed lifters.",
        ["Feels premium and focused", "Lowest migration risk from today", "Red accent reads as 'signal / act now'"],
        ["Dark-only can feel same-as-everyone", "Hardest to stand out in a crowded fitness market"],
        ["#09090B", "#E11D2E", "#F0F0F3", "#2C2C34"],
        "Syne (display) + Manrope (text)",
        "You open it before a heavy session and it feels like a coach, not a chatbot.",
    ),
    direction_page(
        2, "Day Court",
        phone_court(),
        "Daylight athletics. Chalk-white canvas, deep court-green, and a burnt-orange accent — bright, legible, and unmistakably athletic.",
        "Broadening appeal beyond hardcore lifters to everyday athletes who train in real gyms and outdoors.",
        ["Reads perfectly in bright gyms / sunlight", "Approachable — invites daily use", "Most differentiated from generic dark AI apps"],
        ["Biggest departure from current look", "Light UI needs disciplined contrast work"],
        ["#F3F1EC", "#0F1410", "#1F7A4C", "#C45C26"],
        "Archivo Black (display) + Outfit (text)",
        "It feels like stepping onto a bright court — energized, not intimidated.",
    ),
    direction_page(
        3, "Film Cut",
        phone_film(),
        "Cinematic and tungsten-warm. Deep blacks, a single gold accent, and Dayan's own image leading the frame — the film-room aesthetic.",
        "Making Dayan the brand — story-led, personal, and premium. The coach IS the product.",
        ["Most emotional / recruiting-ready", "Puts your real photo + story to work", "Warm gold feels crafted, not clinical"],
        ["Leans on strong photography over time", "Needs consistent image treatment to hold up"],
        ["#0C0A09", "#E8B86D", "#F5F0E8", "#3D3429"],
        "Space Grotesk (display) + Figtree (text)",
        "You trust it because you can see the person who built it.",
    ),
    direction_page(
        4, "Signal Strip",
        phone_signal(),
        "High-contrast, poster-grade athletics. Black on white, condensed display type, and thin red rules — confident and loud without looking like a newspaper.",
        "A bold, competitive brand for younger athletes who want swagger and speed.",
        ["Instantly bold and memorable", "Condensed type scans fast on a phone", "Strong on social / marketing crops"],
        ["Loud tone won't fit every athlete", "Condensed type needs care for long text"],
        ["#FFFFFF", "#111111", "#DC2626", "#E5E5E5"],
        "Bebas Neue (display) + Source Sans 3 (text)",
        "It hypes you up — like a fight-night poster with your name on it.",
    ),
]


HTML_DOC = f"""<!doctype html>
<html><head><meta charset="utf-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Bebas+Neue&family=Figtree:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&family=Outfit:wght@400;600;700;800&family=Source+Sans+3:wght@400;600;700&family=Space+Grotesk:wght@400;500;600;700&family=Syne:wght@600;700;800&display=swap');

@page {{ size: A4; margin: 0; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Manrope', sans-serif; color: #f0f0f3; }}
.page {{ position: relative; width: 210mm; height: 297mm; overflow: hidden; page-break-after: always; background: #0a0a0c; }}

/* ---- Cover ---- */
.cover {{ padding: 26mm 22mm; display: flex; flex-direction: column; }}
.cover .bg {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.32; }}
.cover .veil {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(10,10,12,.55), rgba(10,10,12,.92) 70%, #0a0a0c); }}
.cover > * {{ position: relative; }}
.mark {{ font-family: 'Syne', sans-serif; font-weight: 800; letter-spacing: .34em; font-size: 12pt; }}
.red {{ color: #e11d2e; }}
.cover h1 {{ font-family: 'Syne', sans-serif; font-weight: 800; font-size: 40pt; line-height: .98; letter-spacing: -.02em; margin-top: 12mm; max-width: 15ch; }}
.cover .lede {{ margin-top: 8mm; font-size: 13pt; line-height: 1.55; color: #c4c4cc; max-width: 46ch; }}
.cover .foot {{ position: absolute; left: 22mm; right: 22mm; bottom: 24mm; display: flex; justify-content: space-between; align-items: flex-end; font-size: 10pt; color: #8b8b94; }}
.cover .foot b {{ color: #f0f0f3; }}
.tag {{ display:inline-block; margin-top: 4mm; font-size: 9pt; letter-spacing:.28em; text-transform:uppercase; color:#e11d2e; border:1px solid rgba(225,29,46,.4); padding: 3pt 8pt; border-radius: 999px; }}

/* ---- Brief ---- */
.pad {{ padding: 22mm; }}
.kicker {{ font-family: 'Syne', sans-serif; font-weight: 800; letter-spacing: .28em; text-transform: uppercase; color: #e11d2e; font-size: 9pt; }}
.brief h2 {{ font-family:'Syne',sans-serif; font-weight: 800; font-size: 26pt; letter-spacing:-.02em; margin-top: 5mm; }}
.brief p.intro {{ color:#c4c4cc; font-size: 11.5pt; line-height: 1.6; margin-top: 5mm; max-width: 60ch; }}
.grid3 {{ display:flex; gap: 6mm; margin-top: 10mm; }}
.gcard {{ flex:1; background:#121216; border:1px solid #2c2c34; border-radius: 14px; padding: 6mm; }}
.gcard h4 {{ font-family:'Syne',sans-serif; font-size: 12pt; }}
.gcard p {{ color:#8b8b94; font-size: 9.5pt; line-height:1.5; margin-top: 3mm; }}
.steps {{ margin-top: 10mm; }}
.steps h3 {{ font-size: 12pt; font-family:'Syne',sans-serif; }}
.steps ol {{ margin-top: 4mm; padding-left: 5mm; color:#c4c4cc; font-size: 10.5pt; line-height: 1.9; }}
.how {{ margin-top: 9mm; background:#121216; border:1px solid #2c2c34; border-radius:14px; padding:6mm; }}
.how code {{ background:#000; color:#e8b86d; padding:2pt 6pt; border-radius:6px; font-size:9.5pt; }}

/* ---- Direction pages ---- */
.dir {{ padding: 16mm 16mm; }}
.dir-grid {{ display:flex; gap: 12mm; height: 100%; align-items:center; }}
.dir-mock {{ flex: 0 0 74mm; display:flex; justify-content:center; }}
.dir-copy {{ flex: 1; }}
.dir-name {{ font-weight:800; font-size: 30pt; letter-spacing:-.02em; margin-top: 3mm; }}
.positioning {{ color:#c4c4cc; font-size: 11pt; line-height:1.55; margin-top: 4mm; }}
.lbl {{ font-size: 8pt; letter-spacing:.2em; text-transform:uppercase; color:#8b8b94; margin-top: 7mm; font-weight:700; }}
.lbl.good {{ color:#34d399; }}
.lbl.warn {{ color:#f59e0b; }}
.moment {{ font-family:'Syne',sans-serif; font-size: 13pt; color:#f0f0f3; margin-top: 2mm; line-height:1.4; }}
.two {{ display:flex; gap: 8mm; }}
.two > div {{ flex:1; }}
.list {{ list-style:none; margin-top: 2mm; }}
.list li {{ font-size: 9.5pt; color:#c4c4cc; line-height:1.5; padding-left: 4mm; position:relative; margin-bottom: 1.5mm; }}
.list li:before {{ content:"·"; position:absolute; left:0; color:#e11d2e; font-weight:800; }}
.bestfor {{ font-size: 10.5pt; color:#c4c4cc; margin-top: 2mm; line-height:1.5; }}
.meta-row {{ display:flex; align-items:center; justify-content:space-between; gap: 8mm; margin-top: 8mm; padding-top:5mm; border-top:1px solid #2c2c34; }}
.palette {{ display:flex; gap: 3mm; flex: 0 0 auto; }}
.sw {{ width: 8mm; height: 8mm; border-radius: 999px; border:1px solid rgba(255,255,255,.18); }}
.type {{ font-size: 8.5pt; color:#8b8b94; text-transform:uppercase; letter-spacing:.06em; text-align:right; max-width: 42mm; line-height:1.4; }}

/* ---- Phone frame ---- */
.phone {{ position: relative; width: 70mm; height: 140mm; border-radius: 10mm; overflow:hidden; border: 1.5px solid #2c2c34; box-shadow: 0 14px 50px rgba(0,0,0,.5); }}
.ph-bg {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.ph-content {{ position:relative; height:100%; display:flex; flex-direction:column; padding: 9mm 6mm 6mm; }}
.ph-h {{ font-size: 15pt; line-height: 1.0; margin-top: 3mm; max-width: 14ch; }}
.ph-sub {{ font-size: 8.5pt; line-height:1.4; margin-top: 2.5mm; max-width: 26ch; }}
.ph-btns {{ display:flex; gap: 2mm; margin-top: 4mm; }}
.btn {{ font-size: 8pt; font-weight:700; padding: 2.4mm 3.2mm; border-radius: 8px; display:inline-block; }}
.mark.red, .mini.red {{ color:#e11d2e; }}
.mini {{ font-size: 7pt; letter-spacing:.2em; font-weight:800; }}
.syne {{ font-family:'Syne',sans-serif; font-weight:800; }}
.space {{ font-family:'Space Grotesk',sans-serif; }}
.archivo {{ font-family:'Archivo Black',sans-serif; }}
.bebas {{ font-family:'Bebas Neue',sans-serif; letter-spacing:.02em; }}

/* Iron */
.iron {{ background:#09090b; color:#f0f0f3; }}
.iron .mark {{ font-size: 8.5pt; }}
.iron .ph-fade-dark {{ position:absolute; inset:0; background: linear-gradient(180deg, rgba(9,9,11,.15), rgba(9,9,11,.6) 52%, #09090b 60%); }}
.iron .ph-sub {{ color: rgba(255,255,255,.7); }}
.solid-red {{ background:#e11d2e; color:#fff; }}
.ghost-light {{ border:1px solid rgba(255,255,255,.28); color:rgba(255,255,255,.9); }}
.ph-card {{ margin-top: auto; border-radius: 12px; padding: 4mm; }}
.ph-card.dark {{ background: rgba(18,18,22,.96); border:1px solid #2c2c34; }}
.ph-nav {{ font-size: 6.5pt; letter-spacing:.12em; text-transform:uppercase; color:#8b8b94; }}
.ph-card-h {{ font-size: 11pt; margin-top: 2mm; }}
.ph-card-sub {{ font-size: 7.5pt; color: rgba(255,255,255,.5); margin-top: 1mm; }}
.row {{ display:flex; justify-content:space-between; align-items:center; font-size: 8pt; padding: 2.2mm 3mm; border-radius: 8px; margin-top: 2mm; }}
.dark-row {{ background:#09090b; border:1px solid #2c2c34; }}

/* Court */
.court {{ background:#f3f1ec; color:#0f1410; }}
.court-bg {{ height: 52%; filter: brightness(1.08) contrast(1.05); }}
.ph-fade-light {{ position:absolute; inset:0; background: linear-gradient(180deg, rgba(243,241,236,0) 30%, #f3f1ec 52%); }}
.court-top {{ display:flex; justify-content:space-between; align-items:center; }}
.court-word {{ font-size: 15pt; text-transform:uppercase; letter-spacing:-.01em; }}
.pill {{ font-size: 7pt; font-weight:700; padding: 1.6mm 2.6mm; border-radius:999px; }}
.pill.green {{ background:#1f7a4c; color:#fff; }}
.court-ink {{ color:#0f1410; margin-top: 16mm; font-size: 17pt; text-transform:uppercase; }}
.court-mut {{ color: rgba(15,20,16,.7); }}
.btn.court-dark {{ background:#0f1410; color:#f3f1ec; border-radius:999px; margin-top: 4mm; }}
.ph-card.white {{ background:#fff; box-shadow: 0 10px 30px rgba(15,20,16,.1); }}
.mini.green {{ color:#1f7a4c; }}
.court-stat {{ display:flex; justify-content:space-between; align-items:flex-end; margin-top: 2mm; }}
.court-stat b {{ font-size: 12pt; }}
.orange {{ color:#c45c26; font-size: 8pt; }}
.bar {{ height: 2mm; background:#e8e4dc; border-radius:999px; margin-top: 3mm; overflow:hidden; }}
.bar-fill {{ width: 78%; height:100%; background:#1f7a4c; }}
.court-grid {{ display:flex; gap: 2mm; margin-top: 3mm; }}
.court-chip {{ flex:1; background:#0f1410; color:#f3f1ec; border-radius: 10px; padding: 3mm; font-size: 8.5pt; font-weight:700; }}

/* Film */
.film {{ background:#0c0a09; color:#f5f0e8; }}
.film-bg {{ opacity:.55; object-position: 30% 20%; }}
.ph-fade-film {{ position:absolute; inset:0; background: linear-gradient(180deg, rgba(12,10,9,.25), rgba(12,10,9,.75) 60%, #0c0a09); }}
.film-content {{ justify-content:flex-start; }}
.mark.gold {{ color:#e8b86d; font-weight:500; letter-spacing:.24em; font-size: 8pt; }}
.film-bottom {{ margin-top:auto; }}
.film-h {{ font-weight:500; font-size: 16pt; letter-spacing:-.02em; }}
.film-mut {{ color: rgba(245,240,232,.75); }}
.film-btns {{ display:flex; align-items:center; gap: 3mm; margin-top: 4mm; }}
.btn.gold {{ background:#e8b86d; color:#0c0a09; border-radius:5px; }}
.film-link {{ font-size: 8pt; color: rgba(245,240,232,.8); text-decoration: underline; }}
.film-rule {{ border-top:1px solid rgba(232,184,109,.25); margin-top: 6mm; padding-top: 3mm; }}
.film-meta {{ display:flex; justify-content:space-between; font-size: 6.5pt; letter-spacing:.18em; color: rgba(232,184,109,.8); }}
.film-day {{ font-size: 10pt; margin-top: 2mm; }}
.film-chips {{ display:flex; gap: 2mm; margin-top: 3mm; }}
.fchip {{ font-size: 7pt; font-weight:600; padding: 1.6mm 2.4mm; border-radius:4px; background: rgba(255,255,255,.1); color: rgba(255,255,255,.7); }}
.fchip.on {{ background:#e8b86d; color:#0c0a09; }}

/* Signal */
.signal {{ background:#fff; color:#111; }}
.sig-top {{ position:relative; height: 46%; overflow:hidden; }}
.sig-bg {{ filter: grayscale(1); }}
.sig-shade {{ position:absolute; inset:0; background: rgba(0,0,0,.35); }}
.sig-rule {{ position:absolute; left:0; top:0; height:100%; width: 2mm; background:#dc2626; }}
.sig-title {{ position:absolute; left:5mm; bottom:4mm; color:#fff; }}
.sig-word {{ font-size: 26pt; line-height:.9; }}
.sig-name {{ font-size: 8pt; font-weight:700; letter-spacing:.16em; color: rgba(255,255,255,.8); margin-top:1mm; }}
.sig-body {{ padding: 5mm; }}
.sig-h {{ font-size: 27pt; line-height:.9; }}
.sig-sub {{ font-size: 8.5pt; color:#525252; margin-top: 3mm; line-height:1.4; }}
.sig-line {{ height:1px; background:#dc2626; margin-top: 4mm; }}
.sig-grid {{ display:flex; gap: 2mm; margin-top: 4mm; text-align:center; }}
.sig-stat {{ flex:1; border:1px solid #e5e5e5; padding: 2.5mm 0; }}
.sig-stat span {{ font-size: 16pt; }}
.sig-stat small {{ display:block; font-size: 6.5pt; font-weight:700; letter-spacing:.1em; color:#737373; margin-top:1mm; }}
.sig-btn {{ display:block; text-align:center; background:#111; color:#fff; padding: 3mm; font-size: 11pt; letter-spacing:.1em; margin-top: 5mm; }}

/* ---- Compare ---- */
.cmp table {{ width:100%; border-collapse: collapse; margin-top: 8mm; font-size: 9.5pt; }}
.cmp th, .cmp td {{ text-align:left; padding: 4mm 3mm; border-bottom:1px solid #2c2c34; }}
.cmp th {{ font-family:'Syne',sans-serif; color:#8b8b94; font-size: 8pt; text-transform:uppercase; letter-spacing:.14em; }}
.cmp td b {{ color:#f0f0f3; }}
.rec {{ margin-top: 9mm; background: linear-gradient(180deg,#141013,#0f0d0f); border:1px solid rgba(232,184,109,.3); border-radius:16px; padding: 7mm; }}
.rec .kicker {{ color:#e8b86d; }}
.rec h3 {{ font-family:'Syne',sans-serif; font-size: 18pt; margin-top: 3mm; }}
.rec p {{ color:#c4c4cc; font-size: 10.5pt; line-height:1.6; margin-top: 3mm; max-width: 66ch; }}
.footer-note {{ position:absolute; bottom: 12mm; left: 22mm; right: 22mm; font-size: 8pt; color:#5a5a63; border-top:1px solid #1c1c22; padding-top: 3mm; display:flex; justify-content:space-between; }}
</style></head>
<body>

  <section class="page cover">
    <img class="bg" src="{IMG['speaking']}"/>
    <div class="veil"></div>
    <p class="mark red">COACH K</p>
    <span class="tag">UI / UX Direction Proposal</span>
    <h1 class="syne">Four ways to make Coach K unforgettable.</h1>
    <p class="lede">A design &amp; brand proposal for the Coach K app — four distinct directions, each a complete visual system for the landing experience and the daily Today screen. Pick one; we build it.</p>
    <div class="foot">
      <div>Prepared for <b>Dayan Kijege</b><br/>Coach K — Austin, TX</div>
      <div style="text-align:right">Marketing &amp; Product Design<br/><b>Direction review v1</b></div>
    </div>
  </section>

  <section class="page pad brief">
    <p class="kicker">The brief</p>
    <h2 class="syne">Same product. Four ways to be felt.</h2>
    <p class="intro">Coach K already works — living programs, readiness-aware training, honest feedback. The gap is presence: the current UI is functional but undifferentiated, with weak hierarchy and a dark-only tone that blends in. This proposal isn't four skins; each direction is a positioning decision about how an athlete should feel in the first three seconds.</p>

    <div class="grid3">
      <div class="gcard"><h4 class="syne">What we fix</h4><p>Clear one-action screens, stronger typographic hierarchy, and a brand stamp that's ownable — not generic "AI app."</p></div>
      <div class="gcard"><h4 class="syne">What stays</h4><p>The product logic, your story, the science, and the red-blooded, no-fluff coaching voice.</p></div>
      <div class="gcard"><h4 class="syne">How to choose</h4><p>Pick the feeling, not the color. Who is the athlete, and how should opening Coach K make them feel?</p></div>
    </div>

    <div class="steps">
      <h3 class="syne">How to read each direction</h3>
      <ol>
        <li>Look at the phone first — that's the real landing + Today screen, to scale.</li>
        <li>Read "the moment it creates" — the emotional job of the design.</li>
        <li>Weigh strengths vs. watch-outs against your audience.</li>
      </ol>
    </div>

    <div class="how">
      <h3 class="syne" style="font-size:11pt">See them live &amp; interactive</h3>
      <p style="color:#c4c4cc; font-size:10pt; line-height:1.7; margin-top:3mm">
      Local: <code>cd frontend &amp;&amp; npm run dev</code> → open <code>http://localhost:5173/?design=1</code><br/>
      Deployed: <code>https://your-app.ondigitalocean.app/?design=1</code><br/>
      Or on the landing page footer → <b style="color:#f0f0f3">Preview UI directions</b>.
      </p>
    </div>
    <div class="footer-note"><span>Coach K — UI/UX Direction Proposal</span><span>01 · The brief</span></div>
  </section>

  {PAGES[0]}
  {PAGES[1]}
  {PAGES[2]}
  {PAGES[3]}

  <section class="page pad cmp">
    <p class="kicker">Decision</p>
    <h2 class="syne" style="font-size:26pt; margin-top:5mm">At a glance</h2>
    <table>
      <tr><th>Direction</th><th>Feeling</th><th>Best audience</th><th>Risk</th></tr>
      <tr><td><b>Iron Forge</b></td><td>Serious, premium, private</td><td>Committed lifters</td><td>Low · looks familiar</td></tr>
      <tr><td><b>Day Court</b></td><td>Bright, athletic, daily</td><td>Everyday athletes</td><td>Med · biggest change</td></tr>
      <tr><td><b>Film Cut</b></td><td>Personal, cinematic, trusted</td><td>Story-led recruiting</td><td>Med · photo-dependent</td></tr>
      <tr><td><b>Signal Strip</b></td><td>Bold, loud, competitive</td><td>Younger athletes</td><td>Med · tone not universal</td></tr>
    </table>

    <div class="rec">
      <p class="kicker">Our recommendation</p>
      <h3 class="syne">Lead with <span style="color:#e8b86d">Film Cut</span> — with Day Court as the bright alternate.</h3>
      <p>Coach K's strongest, least-copyable asset is <b style="color:#f0f0f3">you</b> — a real coach with a real story and a real face. Film Cut turns that into the brand: cinematic, warm, and trustworthy, with your photography doing the selling. If the goal is mass, daily approachability over story, <b style="color:#f0f0f3">Day Court</b> is the pick — it's the most differentiated from the sea of dark AI apps and reads beautifully in a bright gym. Iron Forge is the safe polish; Signal Strip is the boldest brand bet.</p>
    </div>
    <div class="footer-note"><span>Coach K — UI/UX Direction Proposal</span><span>06 · Decision &amp; next steps</span></div>
  </section>

</body></html>"""


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=HTML_DOC).write_pdf(str(OUT))
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

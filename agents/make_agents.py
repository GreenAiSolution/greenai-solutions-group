#!/usr/bin/env python3
"""
Generates the four AI-employee robot portraits as SVG.

One base chassis, four sets of job equipment. Everything is drawn here rather
than fetched from an image service, so the roster can be regenerated or
restyled at any time without credits, rate limits or a network call.

    python3 agents/make_agents.py

Writes agents/agent-<name>.svg. The card renders it at ~320px wide; the
artwork is vector so it stays sharp on any display.
"""

W, H = 640, 854

# Shared palette. Brand green with amber optics and gold trim.
# The hull runs deliberately lighter than the backdrop: the chassis has to
# read as lit metal against a dark studio, not blend into it.
BG_A, BG_B = "#0f3218", "#040d07"      # backdrop, lit centre -> dark edge
HULL_HI, HULL_MID, HULL_LO = "#9db3a2", "#5f7a66", "#26352a"
GOLD = "#D4AF37"
EMER = "#4caf6e"
AMBER = "#ffb43a"


def defs(uid, hull_hi, hull_mid, hull_lo, panel):
    """Gradients and filters. Ids are suffixed per-agent so four inline SVGs
    can coexist on one page without clobbering each other's defs."""
    return f"""
  <defs>
    <radialGradient id="bg{uid}" cx="50%" cy="38%" r="78%">
      <stop offset="0%" stop-color="{BG_A}"/>
      <stop offset="100%" stop-color="{BG_B}"/>
    </radialGradient>

    <linearGradient id="hull{uid}" x1="18%" y1="0%" x2="82%" y2="100%">
      <stop offset="0%"   stop-color="{hull_hi}"/>
      <stop offset="45%"  stop-color="{hull_mid}"/>
      <stop offset="100%" stop-color="{hull_lo}"/>
    </linearGradient>

    <linearGradient id="hullv{uid}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="{hull_hi}"/>
      <stop offset="60%"  stop-color="{hull_mid}"/>
      <stop offset="100%" stop-color="{hull_lo}"/>
    </linearGradient>

    <linearGradient id="face{uid}" x1="20%" y1="0%" x2="80%" y2="100%">
      <stop offset="0%"   stop-color="#0c1a10"/>
      <stop offset="100%" stop-color="#040a06"/>
    </linearGradient>

    <linearGradient id="gold{uid}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="#8a6d1c"/>
      <stop offset="50%"  stop-color="#e8c84a"/>
      <stop offset="100%" stop-color="#8a6d1c"/>
    </linearGradient>

    <linearGradient id="panel{uid}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="{panel}" stop-opacity=".30"/>
      <stop offset="100%" stop-color="{panel}" stop-opacity=".08"/>
    </linearGradient>

    <!-- rim light spilling around the silhouette -->
    <filter id="rim{uid}" x="-45%" y="-45%" width="190%" height="190%">
      <feGaussianBlur stdDeviation="26"/>
    </filter>
    <filter id="glow{uid}" x="-90%" y="-90%" width="280%" height="280%">
      <feGaussianBlur stdDeviation="7"/>
    </filter>
    <filter id="soft{uid}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2.2"/>
    </filter>

    <!-- fine matte grain so the plating doesn't read as flat vector fill -->
    <filter id="grain{uid}" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="{uid}"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>

    <clipPath id="crop{uid}"><rect width="{W}" height="{H}" rx="0"/></clipPath>
  </defs>"""


def backdrop(uid):
    return f"""
  <rect width="{W}" height="{H}" fill="url(#bg{uid})"/>
  <!-- back rim glow -->
  <ellipse cx="320" cy="300" rx="190" ry="205" fill="{EMER}" opacity=".30" filter="url(#rim{uid})"/>
  <ellipse cx="320" cy="330" rx="120" ry="130" fill="#7de3a4" opacity=".18" filter="url(#rim{uid})"/>"""


def torso(uid):
    """Shoulders and chest deck — shared by all four."""
    return f"""
  <!-- neck, behind the shoulders -->
  <rect x="268" y="536" width="104" height="72" rx="16" fill="{HULL_LO}"/>
  <rect x="278" y="548" width="84" height="11" rx="5.5" fill="{HULL_MID}" opacity=".85"/>
  <rect x="278" y="566" width="84" height="11" rx="5.5" fill="{HULL_MID}" opacity=".85"/>
  <rect x="278" y="584" width="84" height="11" rx="5.5" fill="{HULL_MID}" opacity=".85"/>

  <!-- shoulders -->
  <path d="M78 990 L78 700 Q78 622 162 596 L244 572 L396 572 L478 596
           Q562 622 562 700 L562 990 Z" fill="url(#hull{uid})"/>
  <!-- lit left shoulder edge -->
  <path d="M78 990 L78 726 Q78 648 162 622 L206 610 Q118 664 118 742 L118 854 Z"
        fill="#ffffff" opacity=".15"/>
  <!-- shoulder caps in shadow -->
  <path d="M78 764 Q78 634 176 602 L200 680 Q128 700 122 774 Z" fill="{HULL_LO}" opacity=".6"/>
  <path d="M562 764 Q562 634 464 602 L440 680 Q512 700 518 774 Z" fill="{HULL_LO}" opacity=".6"/>
  <!-- chest deck plate -->
  <path d="M204 990 L204 690 Q204 658 240 652 L400 652 Q436 658 436 690 L436 854 Z"
        fill="url(#hullv{uid})"/>
  <path d="M204 640 Q204 610 238 604 L402 604 Q436 610 436 640 L436 650 L204 650 Z"
        fill="url(#gold{uid})" opacity=".9"/>"""


def head(uid):
    """Dome, faceplate, optics, ear housings. Framed large — it is a headshot."""
    return f"""
  <!-- ear / audio housings -->
  <ellipse cx="168" cy="392" rx="38" ry="54" fill="{HULL_LO}"/>
  <ellipse cx="168" cy="392" rx="21" ry="32" fill="#08130b"/>
  <ellipse cx="472" cy="392" rx="38" ry="54" fill="{HULL_LO}"/>
  <ellipse cx="472" cy="392" rx="21" ry="32" fill="#08130b"/>
  <circle cx="472" cy="392" r="11" fill="{GOLD}" opacity=".6"/>

  <!-- cranium -->
  <path d="M186 392 Q186 196 320 196 Q454 196 454 392 L454 462
           Q454 556 320 556 Q186 556 186 462 Z" fill="url(#hull{uid})"/>
  <!-- lit left edge: one hard highlight is what makes flat vector read as metal -->
  <path d="M186 392 Q186 196 320 196 Q356 196 384 208 Q252 214 224 396 L224 470
           Q224 520 268 540 Q206 528 192 470 Z" fill="#ffffff" opacity=".17"/>
  <!-- crown sheen -->
  <ellipse cx="300" cy="262" rx="86" ry="34" fill="#ffffff" opacity=".13"/>
  <!-- gold crown band, high on the forehead and clear of the face -->
  <path d="M198 272 Q320 244 442 272 L442 284 Q320 256 198 284 Z" fill="url(#gold{uid})" opacity=".95"/>

  <!-- faceplate recess -->
  <path d="M222 356 Q320 336 418 356 L418 470 Q418 526 320 526 Q222 526 222 470 Z"
        fill="url(#face{uid})"/>
  <path d="M222 356 Q320 336 418 356 L418 470 Q418 526 320 526 Q222 526 222 470 Z"
        fill="none" stroke="{HULL_LO}" stroke-width="3" opacity=".9"/>

  <!-- optics -->
  <ellipse cx="272" cy="418" rx="36" ry="22" fill="{AMBER}" opacity=".28" filter="url(#glow{uid})"/>
  <ellipse cx="368" cy="418" rx="36" ry="22" fill="{AMBER}" opacity=".28" filter="url(#glow{uid})"/>
  <circle cx="272" cy="418" r="19" fill="#3a2a08"/>
  <circle cx="368" cy="418" r="19" fill="#3a2a08"/>
  <circle cx="272" cy="418" r="15" fill="{AMBER}"/>
  <circle cx="368" cy="418" r="15" fill="{AMBER}"/>
  <circle cx="272" cy="418" r="6" fill="#fff6e0"/>
  <circle cx="368" cy="418" r="6" fill="#fff6e0"/>
  <circle cx="267" cy="412" r="3.5" fill="#ffffff"/>
  <circle cx="363" cy="412" r="3.5" fill="#ffffff"/>

  <!-- vent mouth -->
  <rect x="276" y="472" width="88" height="7" rx="3.5" fill="{EMER}" opacity=".55"/>
  <rect x="288" y="488" width="64" height="5" rx="2.5" fill="{EMER}" opacity=".32"/>
  <rect x="300" y="502" width="40" height="4" rx="2" fill="{EMER}" opacity=".18"/>"""


def chest_panel(uid, glyph, panel_col):
    """Glowing chest display — this is where each robot's job is written."""
    return f"""
  <g transform="translate(0,-46) scale(1)">
    <rect x="244" y="700" width="152" height="110" rx="11" fill="{panel_col}" opacity=".20" filter="url(#glow{uid})"/>
    <rect x="248" y="704" width="144" height="102" rx="9" fill="#031008"/>
    <rect x="248" y="704" width="144" height="102" rx="9" fill="url(#panel{uid})"/>
    <rect x="248" y="704" width="144" height="102" rx="9" fill="none" stroke="{panel_col}" stroke-width="2" opacity=".75"/>
    {glyph}
  </g>"""


def tracery(uid, col):
    """Circuit etching on the shoulder plating."""
    return f"""
  <g stroke="{col}" stroke-width="2" fill="none" opacity=".5" stroke-linecap="round">
    <path d="M132 720 L132 678 L172 678"/>
    <path d="M132 754 L158 754 L158 726"/>
    <path d="M508 720 L508 678 L468 678"/>
    <path d="M508 754 L482 754 L482 726"/>
  </g>
  <g fill="{col}" opacity=".8">
    <circle cx="172" cy="678" r="4"/><circle cx="158" cy="726" r="4"/>
    <circle cx="468" cy="678" r="4"/><circle cx="482" cy="726" r="4"/>
  </g>"""


def grain(uid):
    return f'  <rect width="{W}" height="{H}" filter="url(#grain{uid})" opacity=".05" style="mix-blend-mode:overlay"/>'


# ---------------------------------------------------------------- equipment

def headset_slim(uid):
    """STERLING — discreet wireless earpiece with a short mic stub."""
    return f"""
  <path d="M168 356 Q320 296 472 356" stroke="{HULL_LO}" stroke-width="13" fill="none" stroke-linecap="round"/>
  <path d="M168 352 Q320 292 472 352" stroke="{HULL_HI}" stroke-width="4" fill="none" stroke-linecap="round" opacity=".6"/>
  <path d="M172 420 Q212 458 242 468" stroke="#0e1a0c" stroke-width="9" fill="none" stroke-linecap="round"/>
  <circle cx="246" cy="463" r="9" fill="#15220f"/>
  <circle cx="246" cy="463" r="4" fill="{EMER}" opacity=".9"/>"""


def headset_boom(uid):
    """HUNTER — long boom mic and a shoulder antenna."""
    return f"""
  <path d="M168 356 Q320 296 472 356" stroke="{HULL_LO}" stroke-width="13" fill="none" stroke-linecap="round"/>
  <path d="M172 424 Q204 490 266 506" stroke="#0e1a0c" stroke-width="10" fill="none" stroke-linecap="round"/>
  <ellipse cx="278" cy="503" rx="18" ry="13" fill="#101c0d"/>
  <ellipse cx="278" cy="503" rx="10" ry="7" fill="#243019"/>
  <circle cx="278" cy="503" r="3.5" fill="{EMER}"/>
  <!-- antenna -->
  <path d="M492 630 L522 404" stroke="{HULL_LO}" stroke-width="8" stroke-linecap="round"/>
  <path d="M492 630 L522 404" stroke="{HULL_HI}" stroke-width="3" stroke-linecap="round" opacity=".55"/>
  <circle cx="522" cy="400" r="9" fill="{EMER}" opacity=".35" filter="url(#glow{uid})"/>
  <circle cx="522" cy="400" r="5" fill="{EMER}"/>"""


def headset_reception(uid):
    """MAVEN — dual-ear reception headset with a warm indicator."""
    return f"""
  <path d="M164 352 Q320 286 476 352" stroke="{HULL_LO}" stroke-width="15" fill="none" stroke-linecap="round"/>
  <path d="M164 348 Q320 282 476 348" stroke="{GOLD}" stroke-width="4" fill="none" stroke-linecap="round" opacity=".7"/>
  <ellipse cx="164" cy="392" rx="26" ry="36" fill="#101c0d"/>
  <ellipse cx="476" cy="392" rx="26" ry="36" fill="#101c0d"/>
  <ellipse cx="164" cy="392" rx="13" ry="20" fill="#20301a"/>
  <ellipse cx="476" cy="392" rx="13" ry="20" fill="#20301a"/>
  <path d="M166 428 Q202 478 236 488" stroke="#0e1a0c" stroke-width="9" fill="none" stroke-linecap="round"/>
  <ellipse cx="248" cy="482" rx="14" ry="10" fill="#131f0f"/>
  <circle cx="248" cy="482" r="4" fill="{GOLD}"/>
  <circle cx="476" cy="358" r="6" fill="{GOLD}" opacity=".9"/>"""


def visor_precision(uid):
    """LEDGER — flip-down precision visor and a data spool on the shoulder."""
    return f"""
  <path d="M168 356 Q320 296 472 356" stroke="{HULL_LO}" stroke-width="13" fill="none" stroke-linecap="round"/>
  <!-- visor arm + lens over the left optic -->
  <path d="M472 372 Q436 384 408 400" stroke="#0e1a0c" stroke-width="8" fill="none" stroke-linecap="round"/>
  <g opacity=".92">
    <ellipse cx="368" cy="418" rx="46" ry="33" fill="#0a1c12" opacity=".75"/>
    <ellipse cx="368" cy="418" rx="46" ry="33" fill="none" stroke="{EMER}" stroke-width="2.5" opacity=".8"/>
    <ellipse cx="368" cy="418" rx="29" ry="21" fill="none" stroke="{EMER}" stroke-width="1.2" opacity=".55"/>
    <path d="M322 418 L414 418" stroke="{EMER}" stroke-width="1" opacity=".45"/>
    <path d="M368 385 L368 451" stroke="{EMER}" stroke-width="1" opacity=".45"/>
  </g>
  <!-- shoulder data spool -->
  <circle cx="500" cy="700" r="26" fill="{HULL_LO}"/>
  <circle cx="500" cy="700" r="15" fill="#0a1408"/>
  <circle cx="500" cy="700" r="6" fill="{EMER}" opacity=".85"/>"""


# ---------------------------------------------------------------- chest glyphs

def glyph_calendar():
    """Booked appointments."""
    cells = ""
    for r in range(3):
        for c in range(4):
            x, y = 270 + c * 30, 738 + r * 20
            on = (r, c) in {(0, 1), (1, 3), (2, 0)}
            fill = EMER if on else "#1d4a2c"
            op = ".95" if on else ".5"
            cells += f'<rect x="{x}" y="{y}" width="22" height="13" rx="3" fill="{fill}" opacity="{op}"/>'
    return f"""
  <rect x="268" y="716" width="112" height="8" rx="4" fill="{EMER}" opacity=".8"/>
  {cells}"""


def glyph_waveform():
    """Live call audio."""
    import math
    bars = ""
    heights = [12, 26, 44, 62, 40, 70, 30, 54, 20, 38, 58, 24, 44, 16]
    for i, h in enumerate(heights):
        x = 262 + i * 9.4
        y = 752 - h / 2
        bars += f'<rect x="{x:.1f}" y="{y:.1f}" width="5" height="{h}" rx="2.5" fill="{EMER}" opacity=".9"/>'
    return f"""
  <path d="M258 752 L382 752" stroke="{EMER}" stroke-width="1" opacity=".3"/>
  {bars}"""


def glyph_clock():
    """Open hours — always."""
    return f"""
  <circle cx="320" cy="752" r="34" fill="none" stroke="{GOLD}" stroke-width="3" opacity=".85"/>
  <circle cx="320" cy="752" r="44" fill="none" stroke="{GOLD}" stroke-width="1" opacity=".35"/>
  <path d="M320 752 L320 730" stroke="{GOLD}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M320 752 L338 762" stroke="{GOLD}" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="320" cy="752" r="4" fill="{GOLD}"/>
  <text x="320" y="798" font-family="ui-monospace,Menlo,monospace" font-size="13"
        font-weight="700" fill="{GOLD}" opacity=".85" text-anchor="middle">24 / 7</text>"""


def glyph_schedule():
    """Tomorrow's grid, mostly confirmed."""
    rows = ""
    widths = [88, 64, 100, 52]
    for i, w in enumerate(widths):
        y = 724 + i * 19
        rows += f'<rect x="268" y="{y}" width="{w}" height="11" rx="3" fill="{EMER}" opacity=".8"/>'
        rows += f'<rect x="{268 + w + 6}" y="{y}" width="11" height="11" rx="3" fill="{EMER}" opacity=".28"/>'
    return f"""
  {rows}
  <path d="M268 800 L372 800" stroke="{EMER}" stroke-width="1.5" opacity=".45"/>"""


def badge(uid, mini, panel_col):
    """Forehead status strip. The card's text gradient swallows anything below
    eye level, so each robot's job is stated here, in the one band of the
    portrait that is always fully visible."""
    return f"""
  <rect x="244" y="288" width="152" height="54" rx="10" fill="{panel_col}" opacity=".26" filter="url(#glow{uid})"/>
  <rect x="248" y="292" width="144" height="46" rx="8" fill="#01120a"/>
  <rect x="248" y="292" width="144" height="46" rx="8" fill="none" stroke="{panel_col}" stroke-width="2" opacity=".85"/>
  {mini}"""


def mini_calendar():
    d = ""
    for r in range(2):
        for c in range(5):
            on = (r, c) in {(0, 2), (1, 0), (1, 4)}
            d += ('<rect x="%d" y="%d" width="15" height="9" rx="2" fill="%s" opacity="%s"/>'
                  % (268 + c * 21, 304 + r * 13, EMER, ".95" if on else ".35"))
    return d


def mini_wave():
    hs = [10, 20, 32, 22, 36, 14, 28, 18, 30, 12]
    return "".join(
        '<rect x="%d" y="%d" width="5" height="%d" rx="2.5" fill="%s" opacity=".92"/>'
        % (266 + i * 11, int(315 - h / 2), h, EMER) for i, h in enumerate(hs))


def mini_clock():
    return ('<circle cx="298" cy="315" r="13" fill="none" stroke="%(g)s" stroke-width="2.6"/>'
            '<path d="M298 315 L298 307" stroke="%(g)s" stroke-width="2.6" stroke-linecap="round"/>'
            '<path d="M298 315 L305 319" stroke="%(g)s" stroke-width="2.6" stroke-linecap="round"/>'
            '<rect x="322" y="308" width="48" height="6" rx="3" fill="%(g)s" opacity=".85"/>'
            '<rect x="322" y="319" width="34" height="6" rx="3" fill="%(g)s" opacity=".5"/>'
            % {"g": GOLD})


def mini_list():
    d = ""
    for i, w in enumerate([70, 52, 62]):
        y = 302 + i * 11
        d += '<rect x="282" y="%d" width="%d" height="6" rx="3" fill="%s" opacity=".85"/>' % (y, w, EMER)
        d += ('<path d="M266 %d l4 4 l7 -8" stroke="%s" stroke-width="2.4" fill="none" '
              'stroke-linecap="round" stroke-linejoin="round" opacity=".95"/>' % (y + 3, EMER))
    return d


AGENTS = [
    dict(uid=1, slug="sterling", hull=(HULL_HI, HULL_MID, HULL_LO), panel=EMER,
         gear=headset_slim, glyph=glyph_calendar, mini=mini_calendar, trace=EMER),
    dict(uid=2, slug="hunter", hull=("#4a6a4e", "#2c4230", "#131e0e"), panel=EMER,
         gear=headset_boom, glyph=glyph_waveform, mini=mini_wave, trace=EMER),
    dict(uid=3, slug="maven", hull=("#5c6a4e", "#41462f", "#1d2110"), panel=GOLD,
         gear=headset_reception, glyph=glyph_clock, mini=mini_clock, trace=GOLD),
    dict(uid=4, slug="ledger", hull=("#4a5f68", "#2e3f45", "#121b1f"), panel=EMER,
         gear=visor_precision, glyph=glyph_schedule, mini=mini_list, trace=EMER),
]


def build(a):
    uid = a["uid"]
    hi, mid, lo = a["hull"]
    figure = "".join([
        torso(uid),
        tracery(uid, a["trace"]),
        chest_panel(uid, a["glyph"](), a["panel"]),
        head(uid),
        badge(uid, a["mini"](), a["panel"]),
        a["gear"](uid),
    ])
    body = "".join([
        defs(uid, hi, mid, lo, a["panel"]),
        backdrop(uid),
        figure,
        grain(uid),
    ])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="104 146 432 576" '
            f'width="432" height="576" role="img">{body}\n</svg>\n')


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    for a in AGENTS:
        p = os.path.join(here, f"agent-{a['slug']}.svg")
        with open(p, "w", encoding="utf-8") as f:
            f.write(build(a))
        print(f"wrote {os.path.basename(p)}  ({os.path.getsize(p):,} bytes)")

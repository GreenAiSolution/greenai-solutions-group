#!/usr/bin/env python3
"""
Generates the two service artworks as SVG, in the same house style as the
robot portraits: dark chassis, emerald traces, gold accents, amber optics.

    python3 agents/make_panels.py

  panel-pipeline.svg  — AI Business Consulting: the automation spine, drawn as
                        the route a lead actually takes through the system.
  panel-build.svg     — Web Design: a site resolving from wireframe to built.

Neither states an outcome. They show the mechanism, which is the thing we can
actually stand behind.
"""

W = H = 640

BG_A, BG_B = "#0f3218", "#030c06"
EMER = "#4caf6e"
EMER_HI = "#7de3a4"
GOLD = "#D4AF37"
AMBER = "#ffb43a"
STEEL_HI, STEEL_MID, STEEL_LO = "#9db3a2", "#5f7a66", "#26352a"


def shell(uid, body, extra_defs=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">
  <defs>
    <radialGradient id="bg{uid}" cx="50%" cy="34%" r="82%">
      <stop offset="0%" stop-color="{BG_A}"/>
      <stop offset="100%" stop-color="{BG_B}"/>
    </radialGradient>
    <linearGradient id="steel{uid}" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="{STEEL_HI}"/>
      <stop offset="50%" stop-color="{STEEL_MID}"/>
      <stop offset="100%" stop-color="{STEEL_LO}"/>
    </linearGradient>
    <linearGradient id="gold{uid}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#8a6d1c"/>
      <stop offset="50%" stop-color="#e8c84a"/>
      <stop offset="100%" stop-color="#8a6d1c"/>
    </linearGradient>
    <filter id="glow{uid}" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="6"/>
    </filter>
    <filter id="rim{uid}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="30"/>
    </filter>
    <filter id="grain{uid}" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="{uid}"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>{extra_defs}
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg{uid})"/>
  <ellipse cx="320" cy="300" rx="230" ry="240" fill="{EMER}" opacity=".16" filter="url(#rim{uid})"/>
{body}
  <rect width="{W}" height="{H}" filter="url(#grain{uid})" opacity=".05" style="mix-blend-mode:overlay"/>
</svg>
"""


def label(x, y, text, size=15, col="#ffffff", weight=700, anchor="start", op="1", mono=False):
    fam = "ui-monospace,SFMono-Regular,Menlo,monospace" if mono else "Inter,system-ui,sans-serif"
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
            f'fill="{col}" text-anchor="{anchor}" opacity="{op}">{text}</text>')


# ---------------------------------------------------------------- pipeline

def pipeline():
    uid = "p"
    spine_x = 150
    stages = [
        ("Lead arrives",     "call, form or text",        EMER,  "in"),
        ("Qualified",        "the right questions asked", EMER,  "check"),
        ("Into the CRM",     "logged, tagged, assigned",  EMER,  "db"),
        ("Followed up",      "until they answer",         EMER,  "loop"),
        ("Booked",           "on your calendar",          GOLD,  "star"),
    ]
    ys = [110, 218, 326, 434, 542]

    icons = {
        "in":    f'<path d="M-9 0 L5 0 M0 -7 L7 0 L0 7" stroke="{EMER_HI}" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
        "check": f'<path d="M-8 0 L-2 6 L8 -6" stroke="{EMER_HI}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
        "db":    f'<ellipse cx="0" cy="-6" rx="9" ry="3.5" fill="none" stroke="{EMER_HI}" stroke-width="2.2"/><path d="M-9 -6 L-9 6 Q0 10 9 6 L9 -6" fill="none" stroke="{EMER_HI}" stroke-width="2.2"/>',
        "loop":  f'<path d="M8 -3 A8 8 0 1 1 3 -7" stroke="{EMER_HI}" stroke-width="2.6" fill="none" stroke-linecap="round"/><path d="M8 -8 L8 -2 L2 -2" stroke="{EMER_HI}" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
        "star":  f'<path d="M0 -9 L2.6 -3 L9 -2.4 L4.2 2 L5.6 8.4 L0 5.2 L-5.6 8.4 L-4.2 2 L-9 -2.4 L-2.6 -3 Z" fill="{GOLD}"/>',
    }

    out = []
    # the spine, with a pulse travelling down it
    out.append(f'<path d="M{spine_x} {ys[0]} L{spine_x} {ys[-1]}" stroke="{STEEL_LO}" stroke-width="7" stroke-linecap="round"/>')
    out.append(f'<path d="M{spine_x} {ys[0]} L{spine_x} {ys[-1]}" stroke="{EMER}" stroke-width="2.5" '
               f'stroke-linecap="round" opacity=".55" stroke-dasharray="14 18">'
               f'<animate attributeName="stroke-dashoffset" values="0;-64" dur="2.4s" repeatCount="indefinite"/></path>')

    for i, ((title, sub, col, ic), y) in enumerate(zip(stages, ys)):
        last = i == len(stages) - 1
        r = 30 if last else 26
        out.append(f'<circle cx="{spine_x}" cy="{y}" r="{r + 12}" fill="{col}" opacity=".18" filter="url(#glow{uid})"/>')
        out.append(f'<circle cx="{spine_x}" cy="{y}" r="{r}" fill="#08160d" stroke="{col}" stroke-width="2.6"/>')
        out.append(f'<g transform="translate({spine_x},{y})">{icons[ic]}</g>')
        # connector to the text block
        out.append(f'<path d="M{spine_x + r + 8} {y} L{spine_x + 62} {y}" stroke="{col}" stroke-width="1.6" opacity=".5"/>')
        out.append(f'<circle cx="{spine_x + 62}" cy="{y}" r="3" fill="{col}" opacity=".8"/>')
        out.append(label(spine_x + 78, y - 2, title, size=21, col="#ffffff", weight=700))
        out.append(label(spine_x + 78, y + 22, sub, size=14, col="#ffffff", weight=500, op=".5"))
        if last:
            out.append(f'<rect x="{spine_x + 78}" y="{y + 34}" width="112" height="4" rx="2" fill="url(#gold{uid})" opacity=".9"/>')

    out.insert(0, label(40, 52, "THE ROUTE A LEAD TAKES", size=13, col=EMER_HI, weight=800, op=".85", mono=True))
    out.insert(1, f'<path d="M40 66 L600 66" stroke="{EMER}" stroke-width="1" opacity=".2"/>')
    out.append(f'<path d="M40 600 L600 600" stroke="{EMER}" stroke-width="1" opacity=".2"/>')
    out.append(label(40, 624, "Every step runs whether you are free or not.", size=14, col="#ffffff", weight=500, op=".45"))
    return shell(uid, "\n".join("  " + s for s in out))


# ---------------------------------------------------------------- build

def build_panel():
    uid = "b"
    out = []

    # browser chrome
    out.append(f'<rect x="52" y="96" width="536" height="376" rx="16" fill="#07130c" stroke="{STEEL_LO}" stroke-width="2"/>')
    out.append(f'<path d="M52 130 L588 130" stroke="{STEEL_LO}" stroke-width="2"/>')
    for i, c in enumerate([GOLD, EMER, STEEL_MID]):
        out.append(f'<circle cx="{78 + i * 20}" cy="113" r="5.5" fill="{c}" opacity=".85"/>')
    out.append(f'<rect x="160" y="105" width="320" height="16" rx="8" fill="{STEEL_LO}" opacity=".55"/>')
    out.append(f'<rect x="172" y="110" width="120" height="6" rx="3" fill="{EMER}" opacity=".55"/>')

    # left half — wireframe, still being resolved
    wf = [(78, 154, 220, 46), (78, 214, 100, 90), (190, 214, 108, 90),
          (78, 318, 220, 18), (78, 346, 168, 18), (78, 374, 200, 18), (78, 410, 116, 30)]
    for (x, y, w, h) in wf:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" '
                   f'stroke="{EMER}" stroke-width="1.6" stroke-dasharray="6 6" opacity=".42"/>')

    # right half — the same layout, built
    bl = [(342, 154, 220, 46, GOLD, ".85"), (342, 214, 100, 90, EMER, ".55"), (454, 214, 108, 90, EMER, ".38"),
          (342, 318, 220, 18, EMER, ".5"), (342, 346, 168, 18, EMER, ".34"), (342, 374, 200, 18, EMER, ".26")]
    for (x, y, w, h, c, o) in bl:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{c}" opacity="{o}"/>')
    out.append(f'<rect x="342" y="410" width="116" height="30" rx="15" fill="url(#gold{uid})" opacity=".95"/>')
    out.append(label(400, 430, "Enquire", size=13, col="#0a0a0a", weight=800, anchor="middle"))

    # the build line sweeping between the two states
    out.append(f'<g><rect x="316" y="140" width="3" height="316" fill="{EMER_HI}" opacity=".9"/>'
               f'<rect x="310" y="140" width="15" height="316" fill="{EMER_HI}" opacity=".22" filter="url(#glow{uid})"/>'
               f'<animateTransform attributeName="transform" type="translate" values="-232 0;232 0;-232 0" '
               f'dur="6s" repeatCount="indefinite"/></g>')

    out.append(label(78, 88, "WIREFRAME", size=11, col="#ffffff", weight=800, op=".4", mono=True))
    out.append(label(562, 88, "BUILT", size=11, col=GOLD, weight=800, op=".9", anchor="end", mono=True))

    # deliverable chips — promises, not measured scores
    chips = [("~7 days", "start to live"), ("0", "templates used"), ("Yours", "you own the files")]
    for i, (big, small) in enumerate(chips):
        x = 52 + i * 182
        out.append(f'<rect x="{x}" y="506" width="168" height="94" rx="14" fill="#07130c" stroke="{STEEL_LO}" stroke-width="1.6"/>')
        out.append(label(x + 20, 552, big, size=30, col=GOLD, weight=800))
        out.append(label(x + 20, 578, small, size=13, col="#ffffff", weight=500, op=".5"))

    out.insert(0, label(52, 62, "WIREFRAME  →  BUILT", size=13, col=EMER_HI, weight=800, op=".85", mono=True))
    return shell(uid, "\n".join("  " + s for s in out))


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    for name, fn in [("panel-pipeline", pipeline), ("panel-build", build_panel)]:
        p = os.path.join(here, name + ".svg")
        with open(p, "w", encoding="utf-8") as f:
            f.write(fn())
        print(f"wrote {name}.svg  ({os.path.getsize(p):,} bytes)")

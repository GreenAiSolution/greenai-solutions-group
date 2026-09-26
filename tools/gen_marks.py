"""The seals (2026-09-26). One engraved gold dial per AI employee and per service.

Replaces every robot, mascot and 3D slab on the site. Flat vector, black enamel face,
a bezel of minute ticks, a Roman numeral at twelve for the six employees (a small
diamond for the services), and one line icon in the centre. Two cuts per key:

  art/marks/<key>.svg      full seal, fine lines, for 180px and up
  art/marks/<key>-md.svg   same seal, heavier lines, for 80-180px
  art/marks/<key>-sm.svg   simplified seal (no ticks, heavier line) for inline and small

Run from tools/:  python3 gen_marks.py
Icons are drawn on a 24-unit grid (after Lucide, ISC licence)."""
import math, os

OUT = os.path.join(os.path.dirname(__file__), "..", "art", "marks")

ICONS = {
    "ring": ['<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>'],
    "dispatch": ['<circle cx="6" cy="19" r="3"/>', '<path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/>', '<circle cx="18" cy="5" r="3"/>'],
    "inbox": ['<rect x="2" y="4" width="20" height="16" rx="2"/>', '<path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>'],
    "thread": ['<path d="M14 9a2 2 0 0 1-2 2H6l-4 4V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2z"/>', '<path d="M18 9h2a2 2 0 0 1 2 2v11l-4-4h-6a2 2 0 0 1-2-2v-1"/>'],
    "huddle": ['<circle cx="12" cy="8.2" r="5"/>', '<circle cx="7.6" cy="15.6" r="5"/>', '<circle cx="16.4" cy="15.6" r="5"/>'],
    "books": ['<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/>', '<path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/>', '<path d="M12 17.5v-11"/>'],
    "seo": ['<circle cx="10.5" cy="10.5" r="7.5"/>', '<path d="m21 21-5.2-5.2"/>'],
    "crm": ['<path d="M3 3v16a2 2 0 0 0 2 2h16"/>', '<path d="M18 17V9"/>', '<path d="M13 17V5"/>', '<path d="M8 17v-3"/>'],
    "reviews": ['<path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"/>'],
    "winback": ['<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>', '<path d="M3 3v5h5"/>'],
    "web": ['<rect x="2" y="4" width="20" height="16" rx="2"/>', '<path d="M2 9h20"/>', '<path d="M6 4v5"/>', '<path d="M10 4v5"/>'],
    "custom": ['<rect x="14" y="3" width="7" height="7" rx="1"/>', '<path d="M10 21V8a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5a1 1 0 0 0-1-1H3"/>'],
}
NUMERAL = {"ring": "I", "dispatch": "II", "inbox": "III", "thread": "IIII", "huddle": "V", "books": "VI"}
# watch dials write four as IIII; it also keeps the numerals the same visual weight.

def gold(n):
    # userSpaceOnUse: a gradient sized to a straight line's own box has zero width and
    # draws nothing (it hid the chart bars and the 12/3/6/9 ticks).
    return (f'<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{n}" y2="{n}">'
        '<stop offset="0" stop-color="#F7E6AE"/><stop offset=".38" stop-color="#E8C46A"/>'
        '<stop offset=".72" stop-color="#A9853D"/><stop offset="1" stop-color="#E3BE63"/></linearGradient>')


FACE = ('<radialGradient id="f" cx=".42" cy=".34" r=".75">'
        '<stop offset="0" stop-color="#18211B"/><stop offset=".6" stop-color="#0A100C"/>'
        '<stop offset="1" stop-color="#050806"/></radialGradient>')


def numeral(text, cx, top, h, sw):
    """Roman numeral from straight strokes, with dial bars above and below."""
    gw = {"I": 0.0, "V": h * 0.62}
    gap = h * 0.36
    width = sum(gw[c] for c in text) + gap * (len(text) - 1)
    x = cx - width / 2
    d = []
    for c in text:
        if c == "I":
            d.append(f"M{x:.2f} {top:.2f}V{top+h:.2f}")
        else:
            w = gw["V"]
            d.append(f"M{x:.2f} {top:.2f}L{x+w/2:.2f} {top+h:.2f}L{x+w:.2f} {top:.2f}")
        x += gw[c] + gap
    pad = h * 0.34
    l, r = cx - width / 2 - pad, cx + width / 2 + pad
    d.append(f"M{l:.2f} {top:.2f}H{r:.2f}M{l:.2f} {top+h:.2f}H{r:.2f}")
    return f'<path d="{"".join(d)}" stroke-width="{sw}"/>'


def diamond(cx, cy, s):
    return f'<path d="M{cx} {cy-s}L{cx+s*.72} {cy}L{cx} {cy+s}L{cx-s*.72} {cy}Z" fill="url(#g)" stroke="none"/>'


def full(key, w=1.0):
    """w = line weight; 1.0 for 180px and up, heavier for the medium cut."""
    c = 120
    ticks = []
    for i in range(60):
        a = math.radians(i * 6)
        major = i % 5 == 0
        quarter = i % 15 == 0 and i != 0
        r1, r2 = (84, 100) if quarter else (88, 100) if major else (95, 100)
        x1, y1 = c + r1 * math.sin(a), c - r1 * math.cos(a)
        x2, y2 = c + r2 * math.sin(a), c - r2 * math.cos(a)
        ticks.append(f'<path d="M{x1:.2f} {y1:.2f}L{x2:.2f} {y2:.2f}" stroke-width="{(2.4 if quarter else 1.6 if major else .7) * w:.2f}" opacity="{1 if major else .6}"/>')
    top = numeral(NUMERAL[key], c, 56, 13, 1.5 * w) if key in NUMERAL else diamond(c, 64, 5)
    icon = "".join(ICONS[key])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="240" height="240">'
            f'<defs>{gold(240)}{FACE}</defs>'
            f'<circle cx="{c}" cy="{c}" r="117" fill="url(#f)"/>'
            f'<g fill="none" stroke="url(#g)" stroke-linecap="round" stroke-linejoin="round">'
            f'<circle cx="{c}" cy="{c}" r="116" stroke-width="{2.2 * w:.2f}"/>'
            f'<circle cx="{c}" cy="{c}" r="108" stroke-width="{.6 * w:.2f}" opacity=".55"/>'
            + "".join(ticks) +
            f'<circle cx="{c}" cy="{c}" r="80" stroke-width="{.6 * w:.2f}" opacity=".32"/>'
            + top +
            f'<g transform="translate(90 98) scale(2.5)" stroke-width="{.8 * min(w, 1.5):.2f}">{icon}</g>'
            f'</g></svg>')


def small(key):
    icon = "".join(ICONS[key])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">'
            f'<defs>{gold(48)}{FACE}</defs>'
            f'<circle cx="24" cy="24" r="23" fill="url(#f)"/>'
            f'<g fill="none" stroke="url(#g)" stroke-linecap="round" stroke-linejoin="round">'
            f'<circle cx="24" cy="24" r="22.2" stroke-width="1.4"/>'
            f'<circle cx="24" cy="24" r="19" stroke-width=".5" opacity=".5"/>'
            f'<g transform="translate(13.5 13.5) scale(.875)" stroke-width="1.6">{icon}</g>'
            f'</g></svg>')


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for k in ICONS:
        open(os.path.join(OUT, f"{k}.svg"), "w").write(full(k))
        open(os.path.join(OUT, f"{k}-md.svg"), "w").write(full(k, 1.9))
        open(os.path.join(OUT, f"{k}-sm.svg"), "w").write(small(k))
    print(f"wrote {len(ICONS) * 3} seals to art/marks/")

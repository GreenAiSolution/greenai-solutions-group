"""robots.py — the six GreenAI robots, drawn as inline SVG. v2 (2026-09-17 night):
The owner wanted them "more realistic and equipped and ready to go instead of little
cartoon robots". So: seven-head proportions, armour plates with panel lines,
visible joints, a utility belt, twin-thruster pack, a narrow visor with two
light bars, and job kit bolted on. robot(key, icon, pose=) = full figure,
bust(key) = helmet and shoulders, peek(key) = helmet and hands over an edge."""
import re

ACCENT = {"ring":"#7DE3A4","dispatch":"#F0CF6B","inbox":"#7CC4F0","thread":"#C9A9F7","huddle":"#F5A38E","books":"#E8C46A"}
SHELL="#EEF2EE"; SHELL2="#B7C2BA"; SHELL3="#8E9A93"; LINE="#5F6B65"; DEEP="#0F1A14"; DEEP2="#1E2A24"; JOINT="#2A3630"

def _defs(k,a):
    return f'''<defs>
<linearGradient id="sh-{k}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="{SHELL}"/><stop offset="1" stop-color="{SHELL2}"/></linearGradient>
<linearGradient id="sd-{k}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{SHELL2}"/><stop offset="1" stop-color="{SHELL3}"/></linearGradient>
<linearGradient id="dk-{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{JOINT}"/><stop offset="1" stop-color="{DEEP}"/></linearGradient>
<linearGradient id="vi-{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#26463A"/><stop offset="1" stop-color="{DEEP}"/></linearGradient>
<radialGradient id="gl-{k}"><stop offset="0" stop-color="{a}" stop-opacity=".95"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
<filter id="glow-{k}"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>'''

# ---- poses: (left upper→elbow→hand points, right ..., figure transform, flame, legs)
POSES = {
 "stand": (((66,134),(50,192),(56,244)), ((174,134),(190,192),(184,244)), "", 1, "stand"),
 "wave":  (((66,134),(50,192),(56,244)), ((174,134),(212,166),(190,98)), "", 1, "stand"),
 "point": (((66,134),(50,192),(56,244)), ((174,134),(212,152),(238,114)), "", 1, "stand"),
 "fly":   (((66,134),(36,184),(44,238)), ((174,134),(204,184),(196,238)), "rotate(-18 120 220)", 2.4, "fly"),
 "sit":   (((66,134),(42,196),(92,252)), ((174,134),(198,196),(150,252)), "", .5, "stand"),   # braced: both hands forward on the kit
 "think": (((66,134),(40,180),(96,104)), ((174,134),(190,192),(184,244)), "", 1, "stand"),
}

def _seg(k,a,p0,p1,p2):
    (x0,y0),(x1,y1),(x2,y2)=p0,p1,p2
    return f'''<path d="M{x0} {y0} L{x1} {y1}" stroke="{LINE}" stroke-width="24" stroke-linecap="round"/><path d="M{x0} {y0} L{x1} {y1}" stroke="url(#sh-{k})" stroke-width="20" stroke-linecap="round"/>
<path d="M{x1} {y1} L{x2} {y2}" stroke="{LINE}" stroke-width="22" stroke-linecap="round"/><path d="M{x1} {y1} L{x2} {y2}" stroke="url(#sd-{k})" stroke-width="18" stroke-linecap="round"/>
<circle cx="{x1}" cy="{y1}" r="9" fill="url(#dk-{k})" stroke="{LINE}"/><circle cx="{x1}" cy="{y1}" r="3" fill="{a}"/>
<rect x="{x2-12}" y="{y2-8}" width="24" height="28" rx="8" fill="url(#dk-{k})" stroke="{LINE}"/><path d="M{x2-6} {y2+2} v12 M{x2} {y2+2} v14 M{x2+6} {y2+2} v12" stroke="{SHELL3}" stroke-width="2" stroke-linecap="round"/>'''

def _legs(k,a,mode):
    if mode=="kneel":
        return f'''<path d="M96 236 L88 296" stroke="{LINE}" stroke-width="30" stroke-linecap="round"/><path d="M96 236 L88 296" stroke="url(#sh-{k})" stroke-width="26" stroke-linecap="round"/>
<path d="M88 296 L44 306" stroke="{LINE}" stroke-width="26" stroke-linecap="round"/><path d="M88 296 L44 306" stroke="url(#sd-{k})" stroke-width="22" stroke-linecap="round"/>
<rect x="18" y="290" width="40" height="26" rx="8" fill="url(#dk-{k})" stroke="{LINE}"/>
<path d="M146 236 L166 282" stroke="{LINE}" stroke-width="30" stroke-linecap="round"/><path d="M146 236 L166 282" stroke="url(#sh-{k})" stroke-width="26" stroke-linecap="round"/>
<path d="M166 282 L154 318" stroke="{LINE}" stroke-width="26" stroke-linecap="round"/><path d="M166 282 L154 318" stroke="url(#sd-{k})" stroke-width="22" stroke-linecap="round"/>
<rect x="136" y="308" width="44" height="24" rx="8" fill="url(#dk-{k})" stroke="{LINE}"/>
<circle cx="88" cy="296" r="10" fill="url(#dk-{k})" stroke="{LINE}"/><circle cx="166" cy="282" r="10" fill="url(#dk-{k})" stroke="{LINE}"/>
<ellipse cx="110" cy="334" rx="80" ry="8" fill="{DEEP}" opacity=".18"/>'''
    sp = 0 if mode=="fly" else 0
    out=f'<ellipse cx="120" cy="392" rx="64" ry="8" fill="{DEEP}" opacity=".18"/>'
    for hx,kx,ax,bx in [(96,92,90,72),(144,148,150,128)]:
        out+=f'''<path d="M{hx} 236 L{kx} 300" stroke="{LINE}" stroke-width="30" stroke-linecap="round"/><path d="M{hx} 236 L{kx} 300" stroke="url(#sh-{k})" stroke-width="26" stroke-linecap="round"/>
<path d="M{kx} 300 L{ax} 362" stroke="{LINE}" stroke-width="26" stroke-linecap="round"/><path d="M{kx} 300 L{ax} 362" stroke="url(#sd-{k})" stroke-width="22" stroke-linecap="round"/>
<circle cx="{kx}" cy="300" r="10" fill="url(#dk-{k})" stroke="{LINE}"/><circle cx="{kx}" cy="300" r="3" fill="{a}"/>
<rect x="{bx}" y="356" width="44" height="26" rx="9" fill="url(#dk-{k})" stroke="{LINE}"/><path d="M{bx+6} 370 h32" stroke="{a}" stroke-width="2.5" stroke-linecap="round" opacity=".8"/>'''
    return out

def _torso(k,a,chest_icon,flame):
    return f'''
<!-- pack -->
<rect x="58" y="126" width="124" height="112" rx="18" fill="url(#dk-{k})" stroke="{LINE}"/>
<rect x="80" y="238" width="24" height="34" rx="7" fill="{JOINT}" stroke="{LINE}"/><rect x="136" y="238" width="24" height="34" rx="7" fill="{JOINT}" stroke="{LINE}"/>
<path d="M84 274 q8 {30*flame} 8 {30*flame} q8 -{30*flame} 8 -{30*flame}z" fill="{a}" filter="url(#glow-{k})"/><path d="M140 274 q8 {30*flame} 8 {30*flame} q8 -{30*flame} 8 -{30*flame}z" fill="{a}" filter="url(#glow-{k})"/>
<path d="M88 274 q4 {16*flame} 4 {16*flame} q4 -{16*flame} 4 -{16*flame}z" fill="#fff" opacity=".9"/><path d="M144 274 q4 {16*flame} 4 {16*flame} q4 -{16*flame} 4 -{16*flame}z" fill="#fff" opacity=".9"/>
<!-- pelvis + belt -->
<rect x="80" y="218" width="80" height="30" rx="10" fill="url(#dk-{k})" stroke="{LINE}"/>
<rect x="74" y="212" width="92" height="14" rx="5" fill="{JOINT}" stroke="{LINE}"/>
<rect x="84" y="226" width="16" height="16" rx="4" fill="{a}" opacity=".9"/><rect x="112" y="226" width="16" height="16" rx="4" fill="{SHELL3}"/><rect x="140" y="226" width="16" height="16" rx="4" fill="{a}" opacity=".9"/>
<!-- chest plate -->
<path d="M72 112 h96 q10 0 10 10 v64 q0 32 -32 32 h-52 q-32 0 -32 -32 v-64 q0-10 10-10z" fill="url(#sh-{k})" stroke="{LINE}"/>
<path d="M80 116 v60" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".55"/>
<path d="M72 176 h96 M92 196 h56" stroke="{LINE}" stroke-width="1.2" opacity=".7"/>
<path d="M120 112 v96" stroke="{LINE}" stroke-width="1.2" opacity=".35"/>
<rect x="94" y="126" width="52" height="46" rx="8" fill="url(#dk-{k})" stroke="{LINE}"/>
<g transform="translate(106,135) scale(1.15)" fill="none" stroke="{a}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow-{k})">{chest_icon}</g>
<circle cx="84" cy="188" r="3.5" fill="{a}"/><circle cx="94" cy="188" r="3.5" fill="{a}" opacity=".45"/><circle cx="104" cy="188" r="3.5" fill="{SHELL3}"/>
<!-- pauldrons -->
<path d="M46 122 q20 -18 40 -6 v22 q-20 10 -40 0z" fill="url(#sh-{k})" stroke="{LINE}"/><path d="M50 128 q16 -10 32 -4" stroke="{a}" stroke-width="3" stroke-linecap="round"/>
<path d="M194 122 q-20 -18 -40 -6 v22 q20 10 40 0z" fill="url(#sh-{k})" stroke="{LINE}"/><path d="M190 128 q-16 -10 -32 -4" stroke="{a}" stroke-width="3" stroke-linecap="round"/>
<!-- neck -->
<rect x="106" y="98" width="28" height="22" rx="6" fill="url(#dk-{k})" stroke="{LINE}"/>'''

def _head(k,a):
    return f'''
<rect x="76" y="26" width="88" height="82" rx="30" fill="url(#sh-{k})" stroke="{LINE}"/>
<path d="M84 44 q0-10 10-12" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".6"/>
<path d="M120 26 v10" stroke="{LINE}" stroke-width="1.5" opacity=".5"/>
<rect x="84" y="50" width="72" height="36" rx="14" fill="url(#vi-{k})" stroke="{JOINT}"/>
<path d="M92 58 q28 -8 56 0" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".14"/>
<rect x="96" y="64" width="18" height="6" rx="3" fill="{a}" filter="url(#glow-{k})"/><rect x="126" y="64" width="18" height="6" rx="3" fill="{a}" filter="url(#glow-{k})"/>
<path d="M98 92 h44" stroke="{JOINT}" stroke-width="5" stroke-linecap="round"/><path d="M104 92 h6 M116 92 h8 M130 92 h6" stroke="{a}" stroke-width="2" stroke-linecap="round" opacity=".8"/>
<circle cx="76" cy="70" r="9" fill="url(#dk-{k})" stroke="{LINE}"/><circle cx="164" cy="70" r="9" fill="url(#dk-{k})" stroke="{LINE}"/><circle cx="164" cy="70" r="3" fill="{a}"/>
<path d="M168 62 l6 -14" stroke="{LINE}" stroke-width="3" stroke-linecap="round"/><circle cx="175" cy="46" r="4" fill="{a}" filter="url(#glow-{k})"/>'''

KIT = {
 "ring": dict(
   hat=lambda a:f'<path d="M78 60 q42 -46 84 0" fill="none" stroke="{JOINT}" stroke-width="8" stroke-linecap="round"/><rect x="64" y="58" width="22" height="30" rx="8" fill="{JOINT}" stroke="{LINE}"/><rect x="154" y="58" width="22" height="30" rx="8" fill="{JOINT}" stroke="{LINE}"/><circle cx="75" cy="73" r="4" fill="{a}"/><path d="M76 88 q-2 20 26 18" fill="none" stroke="{JOINT}" stroke-width="4" stroke-linecap="round"/><circle cx="104" cy="106" r="4" fill="{a}"/>',
   left='', right=lambda a:f'<rect x="-12" y="-52" width="24" height="60" rx="8" transform="rotate(-20)" fill="{JOINT}" stroke="{LINE}"/><rect x="-6" y="-44" width="12" height="20" rx="3" transform="rotate(-20)" fill="{a}" opacity=".8"/><path d="M16 -44 q14 -10 22 6" fill="none" stroke="{a}" stroke-width="3" stroke-linecap="round"/><path d="M20 -58 q22 -12 34 12" fill="none" stroke="{a}" stroke-width="3" stroke-linecap="round" opacity=".55"/>'),
 "dispatch": dict(
   hat=lambda a:f'<path d="M62 42 q58 -36 116 0 v8 q-58 -24 -116 0z" fill="{a}" stroke="{LINE}"/><rect x="88" y="16" width="64" height="16" rx="6" fill="{a}" stroke="{LINE}"/><rect x="110" y="8" width="20" height="12" rx="4" fill="{JOINT}" stroke="{LINE}"/><circle cx="120" cy="14" r="3.5" fill="#fff"/>',
   left=lambda a:f'<rect x="-30" y="-44" width="48" height="60" rx="7" fill="{JOINT}" stroke="{LINE}"/><rect x="-24" y="-38" width="36" height="46" rx="4" fill="{DEEP}"/><path d="M-18 -16 q10 -16 20 0 t16 -4" fill="none" stroke="{a}" stroke-width="2.5" stroke-dasharray="4 3"/><path d="M4 -30 a4 4 0 1 1 .1 0 M4 -26 l0 6" fill="none" stroke="{a}" stroke-width="2.5"/><path d="M-18 -2 h24 M-18 4 h16" stroke="{a}" stroke-width="2" opacity=".6"/>',
   right=lambda a:f'<rect x="-6" y="-44" width="12" height="50" rx="5" transform="rotate(28)" fill="{JOINT}" stroke="{LINE}"/><path d="M-14 -50 l14 -10 l14 10 l-6 8 h-16z" transform="rotate(28)" fill="{SHELL3}" stroke="{LINE}"/>'),
 "inbox": dict(
   hat=lambda a:f'<path d="M172 104 l-78 118" stroke="{a}" stroke-width="12" stroke-linecap="round" opacity=".95"/><path d="M172 104 l-78 118" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".5"/><rect x="40" y="196" width="46" height="40" rx="8" fill="{JOINT}" stroke="{LINE}"/><path d="M40 204 h46" stroke="{a}" stroke-width="4"/><path d="M62 212 l0 14" stroke="{a}" stroke-width="3"/>',
   left=lambda a:f'<rect x="-34" y="-30" width="56" height="38" rx="5" fill="#fff" stroke="{LINE}"/><path d="M-34 -30 l28 20 l28 -20" fill="none" stroke="{a}" stroke-width="3"/>',
   right=lambda a:f'<g transform="translate(8,-62) rotate(-15)"><rect x="-16" y="-11" width="32" height="22" rx="4" fill="#fff" stroke="{LINE}"/><path d="M-16 -11 l16 11 l16 -11" fill="none" stroke="{a}" stroke-width="2.5"/></g>'),
 "thread": dict(
   hat=lambda a:f'<rect x="58" y="34" width="14" height="42" rx="5" fill="{JOINT}" stroke="{LINE}"/><path d="M52 44 q-8 12 0 24 M44 38 q-14 18 0 36" fill="none" stroke="{a}" stroke-width="3" stroke-linecap="round" opacity=".8"/><circle cx="65" cy="40" r="4" fill="{a}" filter="url(#glow-th)"/>',
   left=lambda a:f'<rect x="-22" y="-36" width="44" height="46" rx="9" fill="{JOINT}" stroke="{LINE}"/><rect x="-16" y="-30" width="32" height="30" rx="4" fill="{DEEP}"/><path d="M-10 -22 h20 M-10 -14 h20 M-10 -6 h14" stroke="{a}" stroke-width="2.5" stroke-linecap="round"/>',
   right=lambda a:f'<path d="M-128 -20 q-30 -70 30 -84 t90 4 q40 24 6 52" fill="none" stroke="{a}" stroke-width="3" stroke-linecap="round" stroke-dasharray="6 5"/><circle cx="0" cy="-6" r="9" fill="{JOINT}" stroke="{a}" stroke-width="2"/>'),
 "huddle": dict(
   hat=lambda a:f'<rect x="76" y="40" width="88" height="8" fill="{a}" opacity=".9"/><rect x="176" y="112" width="18" height="12" rx="4" fill="{JOINT}" stroke="{LINE}"/><circle cx="185" cy="118" r="3.5" fill="{a}" filter="url(#glow-hu)"/><path d="M120 120 v52" stroke="{JOINT}" stroke-width="2"/><path d="M112 172 h16 v10 h-7 l-5 7 h-4z" fill="{a}" stroke="{LINE}"/>',
   left=lambda a:f'<rect x="-34" y="-42" width="52" height="60" rx="8" fill="{JOINT}" stroke="{LINE}"/><rect x="-28" y="-36" width="40" height="48" rx="4" fill="{DEEP}"/><circle cx="-8" cy="-12" r="15" fill="none" stroke="{a}" stroke-width="1.5" stroke-dasharray="3 3"/><circle cx="-8" cy="-27" r="4" fill="{a}"/><circle cx="5" cy="-4" r="4" fill="{a}"/><circle cx="-21" cy="-4" r="4" fill="{a}"/><circle cx="-8" cy="-12" r="3" fill="#fff"/>',
   right=''),
 "books": dict(
   hat=lambda a:f'<path d="M78 48 h84 v12 q-42 10 -84 0z" fill="{a}" opacity=".45"/><path d="M78 48 h84" stroke="{a}" stroke-width="3"/><rect x="150" y="222" width="22" height="22" rx="5" fill="{JOINT}" stroke="{LINE}"/><text x="161" y="238" text-anchor="middle" font-family="Outfit, sans-serif" font-weight="700" font-size="13" fill="{a}">$</text>',
   left=lambda a:f'<rect x="-36" y="-40" width="56" height="62" rx="7" fill="{JOINT}" stroke="{LINE}"/><rect x="-30" y="-34" width="44" height="50" rx="4" fill="{DEEP}"/><path d="M-24 -26 h32 M-24 -18 h32 M-24 -10 h24 M-24 -2 h32 M-24 6 h18" stroke="{a}" stroke-width="2" stroke-linecap="round"/><path d="M-24 12 h32" stroke="#fff" stroke-width="2" opacity=".5"/>',
   right=lambda a:f'<circle cx="4" cy="-44" r="15" fill="{a}" stroke="{LINE}"/><circle cx="4" cy="-44" r="10" fill="none" stroke="#fff" stroke-width="2" opacity=".6"/><text x="4" y="-38" text-anchor="middle" font-family="Outfit, sans-serif" font-weight="700" font-size="15" fill="{DEEP}">$</text>'),
}

def _icon_inner(svg): return re.sub(r'^<svg[^>]*>|</svg>$','',svg.strip())
def _kit(v,a): return v(a) if callable(v) else v

def _extras(pose,a):
    if pose=="fly": return f'<g stroke="{a}" stroke-width="3" stroke-linecap="round" opacity=".5"><path d="M10 300 h50"/><path d="M0 322 h34"/><path d="M14 344 h58"/></g>'
    if pose=="point": return f'<path d="M238 114 q8 -16 4 -32" fill="none" stroke="{a}" stroke-width="2" stroke-dasharray="3 3"/><path d="M240 70 l3 7 7 3 -7 3 -3 7 -3 -7 -7 -3 7 -3z" fill="{a}"/>'
    if pose=="think": return f'<g transform="translate(184,30)"><rect x="-26" y="-22" width="52" height="34" rx="8" fill="{DEEP2}" stroke="{a}" stroke-opacity=".6"/><path d="M-8 12 l-8 10 v-10z" fill="{DEEP2}"/><text x="0" y="4" text-anchor="middle" font-family="Outfit, sans-serif" font-weight="700" font-size="20" fill="{a}">?</text></g>'
    return ""

def robot(key, icon_svg, cls="rb", label=None, pose="stand"):
    a=ACCENT[key]; kit=KIT[key]; k=f"{key}{pose[0]}"
    l=_kit(kit["left"],a); r=_kit(kit["right"],a)
    if pose in ("wave","point"): r=""
    if pose=="think": l=""
    L,R,tf,flame,legs = POSES[pose]
    hat=_kit(kit["hat"],a).replace("glow-th",f"glow-{k}").replace("glow-hu",f"glow-{k}")
    fig=(_legs(k,a,legs) + _torso(k,a,_icon_inner(icon_svg),flame)
         + _seg(k,a,*L) + _seg(k,a,*R)
         + f'<g transform="translate({L[2][0]},{L[2][1]+6})">{l}</g><g transform="translate({R[2][0]},{R[2][1]+6})">{r}</g>'
         + _head(k,a) + hat)
    if tf: fig=f'<g transform="{tf}">{fig}</g>'
    return (f'<svg class="{cls} rb-{key} rb--{pose}" viewBox="0 0 240 400" role="img" aria-label="{label or key.upper()+", the robot"}" xmlns="http://www.w3.org/2000/svg">'
            + _defs(k,a) + _extras(pose,a) + fig + '</svg>')

def bust(key, cls="rb-bust"):
    a=ACCENT[key]; k="b"+key
    hat=_kit(KIT[key]["hat"],a).replace("glow-th",f"glow-{k}").replace("glow-hu",f"glow-{k}")
    hat=re.sub(r'<(rect|path|circle|text)[^>]*(y="(1[2-9]\d|2\d\d)"|cy="(1[2-9]\d|2\d\d)"|M\d+ (1[2-9]\d|2\d\d))[^>]*/?>(</text>)?','',hat)  # drop belt/chest kit
    return (f'<svg class="{cls} rb-{key}" viewBox="34 0 172 150" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">'
            + _defs(k,a)
            + f'<path d="M72 150 v-20 q0-12 12-12 h72 q12 0 12 12 v20z" fill="url(#sh-{k})" stroke="{LINE}"/>'
            + f'<path d="M46 122 q20 -18 40 -6 v22 q-20 10 -40 0z" fill="url(#sh-{k})" stroke="{LINE}"/><path d="M194 122 q-20 -18 -40 -6 v22 q20 10 40 0z" fill="url(#sh-{k})" stroke="{LINE}"/>'
            + f'<rect x="106" y="98" width="28" height="22" rx="6" fill="url(#dk-{k})" stroke="{LINE}"/>'
            + _head(k,a) + hat + '</svg>')

def peek(key, cls="rb-peek"):
    a=ACCENT[key]; k="p"+key
    hat=_kit(KIT[key]["hat"],a).replace("glow-th",f"glow-{k}").replace("glow-hu",f"glow-{k}")
    hat=re.sub(r'<(rect|path|circle|text)[^>]*(y="(1[2-9]\d|2\d\d)"|cy="(1[2-9]\d|2\d\d)"|M\d+ (1[2-9]\d|2\d\d))[^>]*/?>(</text>)?','',hat)
    return (f'<svg class="{cls} rb-{key}" viewBox="34 0 172 150" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">'
            + _defs(k,a) + _head(k,a) + hat
            + f'<rect x="44" y="118" width="26" height="30" rx="8" fill="url(#dk-{k})" stroke="{LINE}"/><rect x="170" y="118" width="26" height="30" rx="8" fill="url(#dk-{k})" stroke="{LINE}"/><path d="M50 128 v14 M57 126 v16 M64 128 v14 M176 128 v14 M183 126 v16 M190 128 v14" stroke="{SHELL3}" stroke-width="2" stroke-linecap="round"/></svg>')


# ---------------------------------------------------------------- 2026-09-19: the 3D cast
# Owner: "make the agents look like this on every other page as well" (the armoured 3D
# figures from the homepage hero). robot()/bust()/peek() now return <img> tags pointing at
# renders made by tools/robots3d/fig.html (art/bots/<key>-<pose3d>.webp, 480x720, alpha).
# The SVG builders above are kept as _svg_* in case a page ever needs them again.
_svg_robot, _svg_bust, _svg_peek = robot, bust, peek
POSE3D = {"stand": "power", "think": "hips", "wave": "raise", "point": "guard", "sit": "stride", "fly": "fly"}

def robot(key, icon_svg=None, cls="rb", label=None, pose="stand"):
    alt = label or key.upper()
    return f'<img class="rb3 rb3-{key}" src="art/bots/{key}-{POSE3D.get(pose, "power")}.webp" alt="{alt}" width="480" height="720" loading="lazy" decoding="async" />'

def bust(key, cls="rb-bust"):
    return f'<img class="{cls} rb3-head" src="art/bots/{key}-head.webp" alt="" width="200" height="200" loading="lazy" decoding="async" />'

def peek(key, cls="rb-peek"):
    return f'<img class="{cls} rb3-head" src="art/bots/{key}-peek.webp" alt="" width="160" height="160" loading="lazy" decoding="async" />'

"""robots.py — the six GreenAI space robots, drawn as inline SVG.
One shared body (astronaut helmet, capsule torso, jetpack), one accent colour
and one job-specific kit per employee. robot(key) = full figure, bust(key) =
helmet-and-shoulders portrait for cards and rosters."""
import re

ACCENT = {"ring":"#7DE3A4","dispatch":"#F0CF6B","inbox":"#7CC4F0","thread":"#C9A9F7","huddle":"#F5A38E","books":"#E8C46A"}
SHELL = "#F7FAF7"; SHELL2 = "#D9E2DB"; LINE = "#B9C6BE"; DEEP = "#0F1A14"; DEEP2 = "#1E4A33"

def _defs(k, a):
    return f'''<defs>
<linearGradient id="sh-{k}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="{SHELL2}"/></linearGradient>
<linearGradient id="vi-{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{DEEP2}"/><stop offset="1" stop-color="{DEEP}"/></linearGradient>
<linearGradient id="ac-{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".9"/><stop offset="1" stop-color="{a}"/></linearGradient>
<radialGradient id="gl-{k}"><stop offset="0" stop-color="{a}" stop-opacity=".9"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
</defs>'''

def _sparkles(a):
    pts=[(28,40,7),(212,30,5),(200,150,6),(24,190,4),(222,230,4)]
    out=""
    for x,y,r in pts:
        out+=f'<path d="M{x} {y-r} L{x+r*.35} {y-r*.35} L{x+r} {y} L{x+r*.35} {y+r*.35} L{x} {y+r} L{x-r*.35} {y+r*.35} L{x-r} {y} L{x-r*.35} {y-r*.35}Z" fill="{a}" opacity=".8"/>'
    return out

POSES = {
 # name: (left arm path, left hand xy, right arm path, right hand xy, figure transform, flame scale, legs)
 "stand": ("M78 160 q-30 10-26 42", (52,204), "M162 160 q30 10 26 42", (188,204), "", 1, "stand"),
 "wave":  ("M78 160 q-30 10-26 42", (52,204), "M162 160 q44 -6 40 -52", (200,104), "", 1, "stand"),
 "point": ("M78 160 q-30 10-26 42", (52,204), "M162 160 q40 -4 60 -22", (226,134), "", 1, "stand"),
 "fly":   ("M78 160 q-34 18-22 58", (58,220), "M162 160 q34 18 22 58", (182,220), "rotate(-16 120 170)", 2.2, "trail"),
 "sit":   ("M78 160 q-6 30 20 48", (100,210), "M162 160 q6 30 -20 48", (140,210), "", .6, "sit"),
 "think": ("M78 160 q-26 -14 8 -42", (90,118), "M162 160 q30 10 26 42", (188,204), "", 1, "stand"),
}

def _legs(k, mode):
    if mode == "sit":
        return f'''<rect x="60" y="262" width="120" height="14" rx="7" fill="{SHELL2}" stroke="{LINE}"/>
<rect x="84" y="230" width="44" height="24" rx="12" fill="url(#sh-{k})" stroke="{LINE}"/><rect x="118" y="230" width="44" height="24" rx="12" fill="url(#sh-{k})" stroke="{LINE}"/>
<ellipse cx="72" cy="244" rx="9" ry="14" fill="{DEEP2}"/><ellipse cx="170" cy="244" rx="9" ry="14" fill="{DEEP2}"/>'''
    return f'''<rect x="90" y="226" width="24" height="42" rx="11" fill="url(#sh-{k})" stroke="{LINE}"/><rect x="126" y="226" width="24" height="42" rx="11" fill="url(#sh-{k})" stroke="{LINE}"/>
<ellipse cx="102" cy="270" rx="17" ry="9" fill="{DEEP2}"/><ellipse cx="138" cy="270" rx="17" ry="9" fill="{DEEP2}"/>'''

def _extras(pose, a):
    if pose == "fly":
        return f'<g stroke="{a}" stroke-width="3" stroke-linecap="round" opacity=".55"><path d="M14 236 h44"/><path d="M6 254 h30"/><path d="M22 272 h52"/></g>'
    if pose == "wave":
        return f'<g fill="none" stroke="{a}" stroke-width="3" stroke-linecap="round" opacity=".7"><path d="M214 76 q10 -8 12 -20"/><path d="M226 92 q12 -2 20 -10"/></g>'
    if pose == "think":
        return f'<g transform="translate(176,42)"><path d="M-22 -18 h44 a8 8 0 0 1 8 8 v22 a8 8 0 0 1 -8 8 h-26 l-10 8 v-8 h-8 a8 8 0 0 1 -8 -8 v-22 a8 8 0 0 1 8 -8z" fill="#fff" stroke="{LINE}"/><text x="0" y="8" text-anchor="middle" font-family="Outfit, sans-serif" font-weight="700" font-size="22" fill="{a}">?</text></g>'
    if pose == "point":
        return f'<g fill="{a}"><path d="M228 96 l3 7 7 3 -7 3 -3 7 -3 -7 -7 -3 7 -3z"/></g><path d="M226 134 q10 -14 6 -28" fill="none" stroke="{a}" stroke-width="2" stroke-dasharray="3 3"/>'
    return ""

def _body(k, a, chest_icon, flame=1, legs="stand"):
    return f'''
<ellipse cx="120" cy="290" rx="58" ry="7" fill="{DEEP}" opacity=".12"/>
<!-- jetpack -->
<rect x="66" y="146" width="108" height="76" rx="24" fill="{SHELL2}" stroke="{LINE}"/>
<rect x="84" y="214" width="18" height="16" rx="6" fill="{DEEP2}"/><rect x="138" y="214" width="18" height="16" rx="6" fill="{DEEP2}"/>
<path d="M88 231 q5 {22*flame} 5 {22*flame} q5-{22*flame} 5-{22*flame}z" fill="{a}"/><path d="M142 231 q5 {22*flame} 5 {22*flame} q5-{22*flame} 5-{22*flame}z" fill="{a}"/>
<path d="M90 231 q3 {12*flame} 3 {12*flame} q3-{12*flame} 3-{12*flame}z" fill="#fff" opacity=".8"/><path d="M144 231 q3 {12*flame} 3 {12*flame} q3-{12*flame} 3-{12*flame}z" fill="#fff" opacity=".8"/>
<!-- legs -->
{_legs(k, legs)}
<!-- torso -->
<rect x="70" y="136" width="100" height="104" rx="42" fill="url(#sh-{k})" stroke="{LINE}"/>
<rect x="70" y="196" width="100" height="10" fill="{a}" opacity=".55"/>
<rect x="94" y="156" width="52" height="46" rx="14" fill="url(#ac-{k})" stroke="{LINE}"/>
<g transform="translate(106,167) scale(1.2)" fill="none" stroke="{DEEP}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{chest_icon}</g>
<circle cx="80" cy="212" r="4" fill="{a}"/><circle cx="92" cy="212" r="4" fill="{DEEP2}" opacity=".5"/>
'''

def _head(k, a):
    return f'''
<!-- antenna -->
<line x1="120" y1="26" x2="120" y2="10" stroke="{LINE}" stroke-width="3"/>
<circle cx="120" cy="8" r="12" fill="url(#gl-{k})"/><circle cx="120" cy="8" r="5" fill="{a}"/>
<!-- helmet -->
<circle cx="120" cy="86" r="62" fill="url(#sh-{k})" stroke="{LINE}"/>
<circle cx="58" cy="90" r="11" fill="{SHELL2}" stroke="{LINE}"/><circle cx="182" cy="90" r="11" fill="{SHELL2}" stroke="{LINE}"/>
<rect x="72" y="52" width="96" height="72" rx="36" fill="url(#vi-{k})"/>
<path d="M84 66 q36-26 72-2" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".18"/>
<rect x="98" y="78" width="15" height="20" rx="7" fill="{a}"/><rect x="127" y="78" width="15" height="20" rx="7" fill="{a}"/>
<rect x="101" y="81" width="5" height="6" rx="2" fill="#fff" opacity=".85"/><rect x="130" y="81" width="5" height="6" rx="2" fill="#fff" opacity=".85"/>
<path d="M108 108 q12 8 24 0" fill="none" stroke="{a}" stroke-width="3" stroke-linecap="round"/>
'''

def _arms(k, a, left, right, pose="stand"):
    lp,(lx,ly),rp,(rx,ry),_,_,_ = POSES[pose]
    return f'''
<path d="{lp}" fill="none" stroke="{LINE}" stroke-width="20" stroke-linecap="round" opacity=".35"/><path d="{lp}" fill="none" stroke="url(#sh-{k})" stroke-width="16" stroke-linecap="round"/>
<circle cx="{lx}" cy="{ly}" r="13" fill="{SHELL2}" stroke="{LINE}"/>
<path d="{rp}" fill="none" stroke="{LINE}" stroke-width="20" stroke-linecap="round" opacity=".35"/><path d="{rp}" fill="none" stroke="url(#sh-{k})" stroke-width="16" stroke-linecap="round"/>
<circle cx="{rx}" cy="{ry}" r="13" fill="{SHELL2}" stroke="{LINE}"/>
<g transform="translate({lx},{ly})">{left}</g><g transform="translate({rx},{ry})">{right}</g>
'''

KIT = {
 "ring": dict(
   hat=f'<path d="M62 78 q58-58 116 0" fill="none" stroke="{DEEP2}" stroke-width="7" stroke-linecap="round"/><rect x="48" y="80" width="22" height="30" rx="9" fill="{DEEP2}"/><rect x="170" y="80" width="22" height="30" rx="9" fill="{DEEP2}"/><path d="M60 110 q0 22 36 20" fill="none" stroke="{DEEP2}" stroke-width="4" stroke-linecap="round"/><circle cx="98" cy="131" r="5" fill="{DEEP2}"/>',
   left='', right=lambda a:f'<rect x="-10" y="-46" width="20" height="56" rx="10" transform="rotate(-25)" fill="{DEEP2}"/><path d="M14 -40 q14 -8 22 6" fill="none" stroke="{a}" stroke-width="3" stroke-linecap="round"/><path d="M18 -52 q22 -10 32 12" fill="none" stroke="{a}" stroke-width="3" stroke-linecap="round" opacity=".6"/>'),
 "dispatch": dict(
   hat=f'<path d="M50 62 q70-44 140 0 l6 10 q-76-30-152 0z" fill="{ACCENT["dispatch"]}" stroke="{LINE}"/><rect x="108" y="30" width="24" height="14" rx="6" fill="{ACCENT["dispatch"]}" stroke="{LINE}"/><circle cx="120" cy="37" r="4" fill="#fff"/>',
   left=lambda a:f'<rect x="-30" y="-40" width="46" height="56" rx="6" fill="#fff" stroke="{LINE}"/><rect x="-16" y="-46" width="18" height="10" rx="4" fill="{DEEP2}"/><path d="M-20 -14 q10-16 20 0 t20 0" fill="none" stroke="{DEEP2}" stroke-width="2.5" stroke-dasharray="4 3"/><path d="M8 -28 a5 5 0 1 1 .1 0 M8 -23 l0 8" fill="none" stroke="{a}" stroke-width="3"/><path d="M-20 0 h30 M-20 6 h20" stroke="{LINE}" stroke-width="2"/>',
   right=f'<rect x="-6" y="-38" width="12" height="42" rx="5" transform="rotate(30)" fill="{DEEP2}"/><path d="M-14 -44 l14 -10 l14 10 l-6 8 h-16z" transform="rotate(30)" fill="{DEEP2}"/>'),
 "inbox": dict(
   hat=f'<path d="M58 62 q62-40 124 0 v10 q-62-28-124 0z" fill="{ACCENT["inbox"]}" stroke="{LINE}"/><rect x="52" y="70" width="60" height="9" rx="4" fill="{DEEP2}"/><path d="M160 140 l-70 96" stroke="{ACCENT["inbox"]}" stroke-width="10" stroke-linecap="round" opacity=".9"/>',
   left=lambda a:f'<rect x="-34" y="-26" width="52" height="36" rx="5" fill="#fff" stroke="{LINE}"/><path d="M-34 -26 l26 18 l26 -18" fill="none" stroke="{a}" stroke-width="3"/>',
   right=lambda a:f'<g transform="translate(6,-58) rotate(-15)"><rect x="-16" y="-11" width="32" height="22" rx="4" fill="#fff" stroke="{LINE}"/><path d="M-16 -11 l16 11 l16 -11" fill="none" stroke="{a}" stroke-width="2.5"/></g><g transform="translate(26,-88) rotate(-25)" opacity=".7"><rect x="-12" y="-8" width="24" height="16" rx="3" fill="#fff" stroke="{LINE}"/><path d="M-12 -8 l12 8 l12 -8" fill="none" stroke="{a}" stroke-width="2"/></g>'),
 "thread": dict(
   hat=f'<g transform="translate(120,30)"><path d="M-26 -22 h52 a8 8 0 0 1 8 8 v16 a8 8 0 0 1 -8 8 h-30 l-10 8 v-8 h-12 a8 8 0 0 1 -8 -8 v-16 a8 8 0 0 1 8 -8z" transform="translate(0,-22)" fill="{ACCENT["thread"]}" stroke="{LINE}"/><circle cx="-12" cy="-28" r="3" fill="{DEEP}"/><circle cx="0" cy="-28" r="3" fill="{DEEP}"/><circle cx="12" cy="-28" r="3" fill="{DEEP}"/></g>',
   left=lambda a:f'<rect x="-22" y="-34" width="44" height="46" rx="10" fill="{a}" stroke="{LINE}"/><rect x="-26" y="-38" width="52" height="10" rx="5" fill="{SHELL2}" stroke="{LINE}"/><rect x="-26" y="8" width="52" height="10" rx="5" fill="{SHELL2}" stroke="{LINE}"/><path d="M-20 -24 h40 M-20 -16 h40 M-20 -8 h40 M-20 0 h40" stroke="#fff" stroke-width="2" opacity=".6"/>',
   right=lambda a:f'<path d="M-136 -20 q-40 -60 20 -90 t100 -10 q60 20 12 60" fill="none" stroke="{a}" stroke-width="3" stroke-linecap="round" stroke-dasharray="6 5"/><circle cx="0" cy="-8" r="8" fill="{a}" stroke="{LINE}"/>'),
 "huddle": dict(
   hat=f'<path d="M58 60 q62-36 124 0 l-4 12 q-58-30-116 0z" fill="{DEEP2}"/><path d="M96 54 h48" stroke="{ACCENT["huddle"]}" stroke-width="4" stroke-linecap="round"/><path d="M120 150 l0 40" stroke="{DEEP2}" stroke-width="3"/><path d="M110 190 h20 v12 h-8 l-6 8 h-6z" fill="{ACCENT["huddle"]}" stroke="{LINE}"/>',
   left=lambda a:f'<rect x="-34" y="-40" width="52" height="60" rx="8" fill="#fff" stroke="{LINE}"/><circle cx="-8" cy="-10" r="17" fill="none" stroke="{LINE}" stroke-dasharray="3 3"/><circle cx="-8" cy="-27" r="5" fill="{a}"/><circle cx="7" cy="-2" r="5" fill="{a}"/><circle cx="-23" cy="-2" r="5" fill="{a}"/><circle cx="-8" cy="-10" r="4" fill="{DEEP2}"/>',
   right=f'<path d="M-8 -6 l8 -10 l8 10" fill="none" stroke="{DEEP2}" stroke-width="4" stroke-linecap="round"/><rect x="-6" y="-46" width="12" height="36" rx="6" fill="{DEEP2}"/>'),
 "books": dict(
   hat=f'<path d="M52 66 q68-30 136 0 l-6 12 q-62-26-124 0z" fill="{ACCENT["books"]}" opacity=".85" stroke="{LINE}"/><path d="M62 74 q58-22 116 0" fill="none" stroke="{DEEP2}" stroke-width="3"/>',
   left=lambda a:f'<path d="M-36 -34 h30 q6 0 6 6 v40 q0 -4 -6 -4 h-30 q-6 0 -6 4 v-40 q0-6 6-6z" fill="#fff" stroke="{LINE}"/><path d="M0 -28 h30 q6 0 6 6 v40 q0-4-6-4 h-30 q-6 0-6 4 v-40 q0-6 6-6z" transform="translate(0,-6)" fill="#fff" stroke="{LINE}"/><path d="M-30 -22 h20 M-30 -14 h20 M-30 -6 h14 M8 -28 h20 M8 -20 h20 M8 -12 h14" stroke="{a}" stroke-width="2"/><rect x="-42" y="8" width="84" height="6" rx="3" fill="{DEEP2}"/>',
   right=lambda a:f'<circle cx="4" cy="-40" r="16" fill="{a}" stroke="{LINE}"/><circle cx="4" cy="-40" r="11" fill="none" stroke="#fff" stroke-width="2" opacity=".7"/><text x="4" y="-34" text-anchor="middle" font-family="Outfit, sans-serif" font-weight="700" font-size="16" fill="{DEEP}">$</text><circle cx="30" cy="-66" r="8" fill="{a}" opacity=".7"/>'),
}

def _icon_inner(svg):
    return re.sub(r'^<svg[^>]*>|</svg>$','',svg.strip())

def robot(key, icon_svg, cls="rb", label=None, pose="stand"):
    a=ACCENT[key]; kit=KIT[key]
    l=kit["left"](a) if callable(kit["left"]) else kit["left"]
    r=kit["right"](a) if callable(kit["right"]) else kit["right"]
    if pose in ("wave","point"): r=""          # the raised hand is empty
    if pose == "think": l=""
    _,_,_,_,tf,flame,legs = POSES[pose]
    k=f"{key}{pose[0]}"
    fig = _body(k,a,_icon_inner(icon_svg),flame,legs) + _arms(k,a,l,r,pose) + _head(k,a) + kit["hat"]
    if tf: fig = f'<g transform="{tf}">{fig}</g>'
    return (f'<svg class="{cls} rb-{key} rb--{pose}" viewBox="0 0 240 300" role="img" aria-label="{label or key.upper()+", the robot"}" xmlns="http://www.w3.org/2000/svg">'
            + _defs(k,a) + _sparkles(a) + _extras(pose,a) + fig + '</svg>')

def peek(key, cls="rb-peek"):
    """helmet and one hand coming up over an edge"""
    a=ACCENT[key]; k="p"+key
    return (f'<svg class="{cls} rb-{key}" viewBox="40 0 160 150" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">'
            + _defs(k,a) + _head(k,a) + KIT[key]["hat"]
            + f'<circle cx="62" cy="138" r="14" fill="{SHELL2}" stroke="{LINE}"/><circle cx="178" cy="138" r="14" fill="{SHELL2}" stroke="{LINE}"/></svg>')

def bust(key, cls="rb-bust"):
    a=ACCENT[key]; k="b"+key
    return (f'<svg class="{cls} rb-{key}" viewBox="40 0 160 150" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">'
            + _defs(k,a)
            + f'<rect x="70" y="128" width="100" height="40" rx="30" fill="url(#sh-{k})" stroke="{LINE}"/>'
            + _head(k,a).replace(f'url(#sh-{key})',f'url(#sh-{k})')
            + KIT[key]["hat"] + '</svg>')

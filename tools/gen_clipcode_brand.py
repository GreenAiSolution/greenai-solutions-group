#!/usr/bin/env python3
"""gen_clipcode_brand.py - vector recreation of Jaden's official clipcode.ai logo
(source: assets/brand/clipcode-ai-logo-source.png, 1254x1254) and every derived file.

Writes into assets/brand/:
  clipcode-mark.svg            the folded cyan/pink ribbon C + screen + play (transparent, square)
  clipcode-wordmark.svg        horizontal lockup: mark + "clipcode.ai" (white, for dark grounds)
  clipcode-lockup-stacked.svg  his original arrangement: mark over "clipcode.ai", navy ground
  clipcode-favicon-32.png, clipcode-apple-touch-icon.png (180), clipcode-og.jpg (1200x630)

Geometry is measured off the source pixels; coordinates stay in the source's 1254px space.
The wordmark is Montserrat 800 (closest free match to his lettering), converted to outlines
so the SVGs never depend on a font being installed.  Needs: rsvg-convert, Pillow, fontTools.
Run: python3 tools/gen_clipcode_brand.py
"""
import os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from clipcode_t2p import path_for
from PIL import Image

BRAND = os.path.join(ROOT, 'assets', 'brand')
FONT = os.path.join(ROOT, 'assets', 'fonts', 'Montserrat-Variable.woff2')

NAVY = '#070B1E'      # ground
SCREEN = '#030820'    # the dark screen inside the C
CYAN, CYAN_BACK, CYAN_SHADE = '#12FBF4', '#07EDE7', '#027E8E'
PINK, PINK_BACK, PINK_SHADE = '#FC2470', '#EA1264', '#B0084A'

# ---- shapes (source pixel space) -------------------------------------------------------
C_BODY = ('M372 407A150 150 0 0 1 522 257H733A150 150 0 0 1 883 407V444'
          'A28 28 0 0 1 855 472H781A28 28 0 0 1 753 444H740V700L650 768H522'
          'A150 150 0 0 1 372 618Z')
PINK_ARM = ('M781 555H857A28 28 0 0 1 885 583V618A150 150 0 0 1 735 768H597'
            'A100 100 0 0 1 497 668V560H740V583H753A28 28 0 0 1 781 555Z')
SCREEN_P = ('M541 384H693A60 60 0 0 1 753 444V593A62 62 0 0 1 691 655H612'
            'A115 115 0 0 1 497 540V428A44 44 0 0 1 541 384Z')
# fold lines: where the ribbon turns over
FOLD_C = 'M776 249C600 295 420 440 368 622'
FOLD_P = 'M730 636C695 700 625 752 538 776'
C_BACK = FOLD_C + 'L360 800L900 800L900 249Z'          # side of the cyan fold that is the underside
P_BACK = FOLD_P + 'L480 790L480 540L760 540Z'          # side of the pink fold that is the underside
PLAY = '<path d="M575 456L690 523L575 590Z" fill="#fff" stroke="#fff" stroke-width="36" stroke-linejoin="round"/>'
VIEW = (366, 250, 524, 524)   # square around the mark (mark spans 372..885 x 257..768)


def mark_body(uid='cc'):
    """SVG fragment (defs + shapes) for the mark in source coordinates. uid keeps ids unique when inlined twice."""
    return f'''<defs>
<clipPath id="{uid}-c"><path d="{C_BODY}"/></clipPath>
<clipPath id="{uid}-cb"><path d="{C_BACK}"/></clipPath>
<clipPath id="{uid}-p"><path d="{PINK_ARM}"/></clipPath>
<clipPath id="{uid}-pb"><path d="{P_BACK}"/></clipPath>
<filter id="{uid}-s" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="26"/></filter>
<filter id="{uid}-s2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="22"/></filter>
<linearGradient id="{uid}-cg" x1="0" y1="257" x2="0" y2="768" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="#0CF4EC"/></linearGradient>
</defs>
<g clip-path="url(#{uid}-c)">
<rect x="360" y="240" width="540" height="540" fill="url(#{uid}-cg)"/>
<g clip-path="url(#{uid}-cb)"><rect x="360" y="240" width="540" height="540" fill="{CYAN_BACK}"/>
<path d="{FOLD_C}" fill="none" stroke="{CYAN_SHADE}" stroke-width="90" filter="url(#{uid}-s)"/></g>
</g>
<g clip-path="url(#{uid}-p)">
<rect x="480" y="540" width="420" height="240" fill="{PINK}"/>
<g clip-path="url(#{uid}-pb)"><rect x="480" y="540" width="420" height="240" fill="{PINK_BACK}"/>
<path d="{FOLD_P}" fill="none" stroke="{PINK_SHADE}" stroke-width="80" filter="url(#{uid}-s2)"/></g>
</g>
<path d="{SCREEN_P}" fill="{SCREEN}"/>
{PLAY}'''


def svg(view, inner, w=None, h=None, label='Clipcode'):
    vb = ' '.join(f'{v:g}' for v in view)
    size = f' width="{w:g}" height="{h:g}"' if w else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{size} role="img" aria-label="{label}">'
            f'<title>{label}</title>{inner}</svg>\n')


def word(size, x, y, fill='#fff'):
    d, w = path_for(FONT, 'clipcode.ai', size, x, y, -0.025, wght=800)
    return f'<path d="{d}" fill="{fill}"/>', w


def render(svg_text, out, w, h):
    with tempfile.NamedTemporaryFile('w', suffix='.svg', delete=False) as f:
        f.write(svg_text)
    subprocess.run(['rsvg-convert', '-w', str(w), '-h', str(h), f.name, '-o', out], check=True)
    os.unlink(f.name)


def main():
    vx, vy, vw, vh = VIEW
    # 1) mark
    mark = svg(VIEW, mark_body(), label='Clipcode')
    open(os.path.join(BRAND, 'clipcode-mark.svg'), 'w').write(mark)

    # 2) horizontal lockup: mark height 524 units, word cap-ish height ~ 0.62 of mark
    wsize = 300
    probe, ww = word(wsize, 0, 0)
    gap = 70
    tx = vx + vw + gap
    base = vy + vh / 2 + wsize * 0.27       # optical centre of the lowercase x-height on the mark
    wpath, ww = word(wsize, tx, base)
    total_w = vw + gap + ww + 8
    lock = svg((vx, vy, total_w, vh), mark_body('cw') + wpath, label='clipcode.ai')
    open(os.path.join(BRAND, 'clipcode-wordmark.svg'), 'w').write(lock)

    # 3) stacked, as on his source file (navy ground, word under the mark)
    s_word, sw = word(100, 0, 0)
    ssize = 100 * 863 / sw                  # his word spans x 195..1058
    s_word, sw = word(ssize, 627 - 863 / 2, 942)
    stacked = svg((0, 0, 1254, 1254), f'<rect width="1254" height="1254" fill="{NAVY}"/>' + mark_body('cs') + s_word,
                  label='clipcode.ai')
    open(os.path.join(BRAND, 'clipcode-lockup-stacked.svg'), 'w').write(stacked)

    # 4) favicon + touch icon: the mark alone; touch icon gets the navy ground (iOS fills transparency black)
    render(mark, os.path.join(BRAND, 'clipcode-favicon-32.png'), 32, 32)
    pad = 26  # units of breathing room on the touch icon
    touch = svg((vx - pad, vy - pad, vw + 2 * pad, vh + 2 * pad),
                f'<rect x="{vx-pad}" y="{vy-pad}" width="{vw+2*pad}" height="{vh+2*pad}" fill="{NAVY}"/>' + mark_body('ct'))
    render(touch, os.path.join(BRAND, 'clipcode-apple-touch-icon.png'), 180, 180)

    # 5) OG card 1200x630: navy ground, faint ribbon glow, mark left, word + line right
    og_mark_scale = 330 / vw
    mx, my = 96, (630 - 330) / 2
    ox = mx + 330 + 64
    _, w100 = word(100, 0, 0)
    osize = 100 * 600 / w100                 # word fills 600px
    ow, owidth = word(osize, ox, 300)
    l1, _ = path_for(FONT, 'Automation for business.', 36, ox + 3, 372, 0, wght=500)
    l2, _ = path_for(FONT, 'Premium AI ads.', 36, ox + 3, 420, 0, wght=500)
    line_d = l1 + l2
    og = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
<defs><radialGradient id="g1" cx="0.18" cy="0.2" r="0.6"><stop offset="0" stop-color="#12FBF4" stop-opacity=".16"/><stop offset="1" stop-color="#12FBF4" stop-opacity="0"/></radialGradient>
<radialGradient id="g2" cx="0.92" cy="1" r="0.6"><stop offset="0" stop-color="#FC2470" stop-opacity=".16"/><stop offset="1" stop-color="#FC2470" stop-opacity="0"/></radialGradient></defs>
<rect width="1200" height="630" fill="{NAVY}"/><rect width="1200" height="630" fill="url(#g1)"/><rect width="1200" height="630" fill="url(#g2)"/>
<g transform="translate({mx} {my}) scale({og_mark_scale:.5f}) translate({-vx} {-vy})">{mark_body('co')}</g>
{ow}<path d="{line_d}" fill="#B9C0DA"/>
<rect x="{ox+4}" y="462" width="64" height="6" rx="3" fill="#12FBF4"/><rect x="{ox+74}" y="462" width="64" height="6" rx="3" fill="#FC2470"/>
</svg>'''
    tmp = os.path.join(tempfile.gettempdir(), 'clipcode-og.png')
    render(og, tmp, 1200, 630)
    Image.open(tmp).convert('RGB').save(os.path.join(BRAND, 'clipcode-og.jpg'), quality=90, optimize=True, progressive=True)
    os.unlink(tmp)
    # preview of the mark next to the source for eyeballing
    render(svg((0, 0, 1254, 1254), f'<rect width="1254" height="1254" fill="{NAVY}"/>' + mark_body('cp') + s_word),
           os.path.join(tempfile.gettempdir(), 'clipcode-compare.png'), 1254, 1254)
    print('brand files written; compare render at', os.path.join(tempfile.gettempdir(), 'clipcode-compare.png'))


if __name__ == '__main__':
    main()

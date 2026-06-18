#!/usr/bin/env python3
"""
Definitive byte-level fix for mojibake emoji and text in all HTML files.
All patterns identified from hex dumps of the actual files.
"""

# ─── SVG ICONS ────────────────────────────────────────────────────────────────
def svg(w, h, path_data, stroke="var(--green-dark)", sw="1.8"):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            f'{path_data}</svg>')

PHONE_PATHS   = '<rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>'
ROBOT_PATHS   = '<rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><line x1="12" y1="7" x2="12" y2="11"/><line x1="8" y1="15" x2="8" y2="17"/><line x1="16" y1="15" x2="16" y2="17"/>'
CLIP_PATHS    = '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="8" y1="16" x2="14" y2="16"/>'
TARGET_PATHS  = '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>'
CHART_PATHS   = '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>'
USERS_PATHS   = '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
SHIELD_PATHS  = '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>'
SEARCH_PATHS  = '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'
BRUSH_PATHS   = '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L3 14.67V21h6.33l10.06-10.06a5.5 5.5 0 0 0 0-7.77z"/><line x1="15.91" y1="8.49" x2="19.51" y2="12.09"/>'
BOLT_PATHS    = '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>'
PIN_PATHS     = '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>'
PHONE_R_PATHS = '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.39 2 2 0 0 1 3.6 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.6a16 16 0 0 0 6 6l.91-.91a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>'
MAIL_PATHS    = '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>'

def e(icon, size=28):  return svg(size, size, icon)
def es(icon, size=16): return svg(size, size, icon, "rgba(255,255,255,.75)", "2")
def ec(icon, size=22): return svg(size, size, icon)
def ev(icon, size=52): return svg(size, size, icon, "var(--green-light)", "1.5") + ' style="opacity:.9"'
def eshield_lg():
    return svg(60, 60, SHIELD_PATHS, "rgba(255,255,255,.9)", "1.5")

# ─── EXACT BYTE PATTERNS (from hex dump analysis) ─────────────────────────────
# Emoji bytes (mojibake form stored in files)
PHONE_B   = b'\xc3\xb0\xc5\xb8\x22\xc2\xb1'          # 📱
CLIP_B    = b'\xc3\xb0\xc5\xb8\x22\xe2\x80\xb9'       # 📋
CHART_B   = b'\xc3\xb0\xc5\xb8\x22\xcb\x86'           # 📈
HANDSHAKE_B = b'\xc3\xb0\xc5\xb8\xc2\xa4\xc2\x9d'    # 🤝
SHIELD_B  = b'\xc3\xb0\xc5\xb8\xe2\x80\xba\xc2\xa1\xc3\xaf\xc2\xb8\xc2\x8f'  # 🛡️
PHONE_R_B = b'\xc3\xb0\xc5\xb8\x22\xc5\xbe'           # 📞
PIN_B     = b'\xc3\xb0\xc5\xb8\x22\xc2\x8d'           # 📍
CAMERA_B  = b'\xc3\xb0\xc5\xb8\x22\xc2\xb8'           # 📸
PIN2_B    = b'\xc3\xb0\xc5\xb8\x22\xc2\x90'           # second pin variant (📐/🔐)
MAIL_B    = b'\xc3\xa2\xc5\x93\xe2\x80\xb0\xc3\xaf\xc2\xb8\xc2\x8f'  # ✉️
FIRE_B    = b'\xc3\xb0\xc5\xb8\x22\xc2\xa5'           # 🔥 (in elite section)

# Text character bytes (mojibake form)
EM_DASH_B   = b'\xc3\xa2\xe2\x82\xac\x22'             # — or – (normalized)
APOS_B      = b'\xc3\xa2\xe2\x82\xac\xe2\x84\xa2'     # ' right single quote
LDQUOTE_B   = b'\xc3\xa2\xe2\x82\xac\xc5\x93'         # " left double quote
RDQUOTE_B   = b'\xc3\xa2\xe2\x82\xac\xc2\x9d'         # " right double quote
MIDDOT_B    = b'\xc3\x82\xc2\xb7'                      # · middle dot
REG_B       = b'\xc3\x82\xc2\xae'                      # ®
STAR_B      = b'\xc3\xa2\xcb\x9c\xe2\x80\xa6'         # ★
CHECK_BOX_B = b'\xc3\xa2\xc5\x93\xe2\x80\xa6'         # ✅
CHECK_B     = b'\xc3\xa2\xc5\x93\x22'                  # ✓ (inline check)
CROSS_BOX_B = b'\xc3\xa2\xc2\x9d\xc5\x92'             # ❌
CROSS_B     = b'\xc3\xa2\xc5\x93\xe2\x80\x94\xe2\x80\xa0'  # ✗ (heavy ballot x)
DIAMOND_B   = b'\xc3\xa2\xe2\x80\x94\xe2\x80\xa0'     # ◆
LIGHTNING_B = b'\xc3\xa2\xc5\xa1\xc2\xa1'             # ⚡
ARROW_B     = b'\xc3\xa2\xe2\x80\xa0\x92'              # →


def brep(data: bytes, old: bytes, new: bytes, count: int = 0) -> bytes:
    """Replace bytes. count=0 means replace all; count>0 means replace only first count."""
    if count == 0:
        return data.replace(old, new)
    result = data
    replaced = 0
    while replaced < count:
        idx = result.find(old)
        if idx == -1:
            break
        result = result[:idx] + new + result[idx+len(old):]
        replaced += 1
    return result


def ctx_rep(data: bytes, ctx_prefix: str, emoji_b: bytes, svg_str: str, count: int = 0) -> bytes:
    """Replace emoji within a specific HTML context (prefix + emoji + suffix)."""
    old = ctx_prefix.encode() + emoji_b
    new = ctx_prefix.encode() + svg_str.encode()
    return brep(data, old, new, count)


def fix_text(data: bytes) -> bytes:
    """Apply all text mojibake fixes."""
    fixes = [
        (EM_DASH_B,   '—'.encode()),
        (APOS_B,      '’'.encode()),   # right single quote '
        (LDQUOTE_B,   '“'.encode()),   # left double quote "
        (RDQUOTE_B,   '”'.encode()),   # right double quote "
        (MIDDOT_B,    '·'.encode()),
        (REG_B,       '®'.encode()),
        (STAR_B,      '★'.encode()),
        (CHECK_BOX_B, '✅'.encode()),
        (CHECK_B,     '✓'.encode()),
        (CROSS_BOX_B, '❌'.encode()),
        (CROSS_B,     '✗'.encode()),
        (DIAMOND_B,   '◆'.encode()),
        (LIGHTNING_B, '⚡'.encode()),
        (ARROW_B,     '→'.encode()),
        # Also fix the â€" pattern that appears in some places (different encoding path)
        ('â€"'.encode(), '—'.encode()),
        ('â€™'.encode(), '’'.encode()),
        ('â€œ'.encode(), '“'.encode()),
        ('Â·'.encode(),  '·'.encode()),
        ('Â®'.encode(),  '®'.encode()),
    ]
    for old, new in fixes:
        data = data.replace(old, new)
    return data


def fix_index(data: bytes) -> bytes:
    FI = '<div class="feature-icon" aria-hidden="true">'
    SCI = '<div class="service-card__icon" aria-hidden="true">'
    FTR = '<div class="footer__contact-icon" aria-hidden="true">'
    GUAR = '<div style="font-size:4rem;flex-shrink:0;position:relative">'

    data = ctx_rep(data, FI,  PHONE_B,    e(PHONE_PATHS))
    data = ctx_rep(data, FI,  CLIP_B,     e(CLIP_PATHS))
    data = ctx_rep(data, FI,  CHART_B,    e(CHART_PATHS))
    data = ctx_rep(data, FI,  HANDSHAKE_B,e(USERS_PATHS))
    data = ctx_rep(data, FI,  SHIELD_B,   e(SHIELD_PATHS))  # fallback

    data = ctx_rep(data, SCI, PHONE_B,    e(PHONE_PATHS))
    data = ctx_rep(data, SCI, CLIP_B,     e(CLIP_PATHS))

    data = ctx_rep(data, GUAR, SHIELD_B,  eshield_lg())

    data = ctx_rep(data, FTR, PHONE_R_B,  es(PHONE_R_PATHS))
    data = ctx_rep(data, FTR, MAIL_B,     es(MAIL_PATHS))
    data = ctx_rep(data, FTR, PIN_B,      es(PIN_PATHS))

    data = fix_text(data)
    return data


def fix_services(data: bytes) -> bytes:
    VIS = '<div class="service-detail__visual-icon" aria-hidden="true">'
    DLI = '<div class="detail-list__icon" aria-hidden="true">'
    FTR = '<div class="footer__contact-icon" aria-hidden="true">'

    data = ctx_rep(data, VIS, PHONE_B, e(PHONE_PATHS, 52))
    data = ctx_rep(data, VIS, CLIP_B,  e(CLIP_PATHS,  52))

    # Detail list check marks
    data = data.replace(DLI.encode() + CHECK_B, DLI.encode() + '✓'.encode())

    # Pricing spans
    data = data.replace(
        b'<span class="check" aria-hidden="true">' + CHECK_B,
        b'<span class="check" aria-hidden="true">\xe2\x9c\x93')  # ✓
    data = data.replace(
        b'<span class="x" aria-hidden="true">' + CROSS_B,
        b'<span class="x" aria-hidden="true">\xe2\x9c\x97')      # ✗

    # Coverage check spans
    data = data.replace(
        b'<span style="color:var(--green-light);font-weight:700">' + CHECK_B,
        b'<span style="color:var(--green-light);font-weight:700">\xe2\x9c\x93')

    # Notary credential badges
    data = data.replace(CHECK_BOX_B + b' NNA Certified',        '✅ NNA Certified'.encode())
    data = data.replace(CHECK_BOX_B + b' E&amp;O Insured',      '✅ E&amp;O Insured'.encode())
    data = data.replace(CHECK_BOX_B + b' Background Checked',   '✅ Background Checked'.encode())
    data = data.replace(CHECK_BOX_B + b' Arizona Commissioned', '✅ Arizona Commissioned'.encode())

    # Fire emoji in elite section (replace with just removing it gracefully)
    data = data.replace(FIRE_B, b'\xf0\x9f\x94\xa5')  # proper 🔥 UTF-8

    data = ctx_rep(data, FTR, PHONE_R_B, es(PHONE_R_PATHS))
    data = ctx_rep(data, FTR, MAIL_B,    es(MAIL_PATHS))
    data = ctx_rep(data, FTR, PIN_B,     es(PIN_PATHS))

    data = fix_text(data)
    return data


def fix_about(data: bytes) -> bytes:
    FI  = '<div class="feature-icon" aria-hidden="true">'
    MI  = '<div class="mission-icon" aria-hidden="true">'
    FTR = '<div class="footer__contact-icon" aria-hidden="true">'
    PIN_BADGE = b'<div style="font-size:1.5rem" aria-hidden="true">' + PIN_B + b'</div>'

    # Stat badge pin (location badge)
    data = data.replace(PIN_BADGE,
        f'<div style="display:flex;align-items:center;justify-content:center" aria-hidden="true">{e(PIN_PATHS)}</div>'.encode())

    # Mission icons
    data = ctx_rep(data, MI, HANDSHAKE_B, e(USERS_PATHS))

    # Values feature icons (ordered — Transparency=search, Custom=brush, Results=chart, Ethical=shield)
    data = ctx_rep(data, FI, PIN_B,      e(SEARCH_PATHS), 1)   # Transparency First
    data = ctx_rep(data, FI, PIN2_B,     e(BRUSH_PATHS),  1)   # Custom Over Cookie-Cutter
    data = ctx_rep(data, FI, CHART_B,    e(CHART_PATHS))       # Results-Driven
    data = ctx_rep(data, FI, SHIELD_B,   e(SHIELD_PATHS))      # Ethical AI

    data = ctx_rep(data, FTR, PHONE_R_B, es(PHONE_R_PATHS))
    data = ctx_rep(data, FTR, MAIL_B,    es(MAIL_PATHS))
    data = ctx_rep(data, FTR, PIN_B,     es(PIN_PATHS))

    data = fix_text(data)
    return data


def fix_contact(data: bytes) -> bytes:
    FTR = '<div class="footer__contact-icon" aria-hidden="true">'

    data = ctx_rep(data, '<div class="contact-detail__icon" role="img" aria-label="Phone">',
                   PHONE_R_B, ec(PHONE_R_PATHS))
    data = ctx_rep(data, '<div class="contact-detail__icon" role="img" aria-label="Email">',
                   MAIL_B, ec(MAIL_PATHS))
    data = ctx_rep(data, '<div class="contact-detail__icon" role="img" aria-label="Location">',
                   PIN_B, ec(PIN_PATHS))

    data = ctx_rep(data, FTR, PHONE_R_B, es(PHONE_R_PATHS))
    data = ctx_rep(data, FTR, MAIL_B,    es(MAIL_PATHS))
    data = ctx_rep(data, FTR, PIN_B,     es(PIN_PATHS))

    data = fix_text(data)
    return data


JOBS = [
    ('index.html',    fix_index),
    ('services.html', fix_services),
    ('about.html',    fix_about),
    ('contact.html',  fix_contact),
]

if __name__ == '__main__':
    for filename, fixer in JOBS:
        with open(filename, 'rb') as f:
            data = f.read()
        if data[:3] == b'\xef\xbb\xbf':
            data = data[3:]
        fixed = fixer(data)
        with open(filename, 'wb') as f:
            f.write(fixed)
        svg_count = fixed.count(b'<svg')
        # Check remaining garbled
        remaining = sum(1 for b in [b'\xc3\xb0\xc5\xb8', b'\xc3\xa2\xc5\x93'] if b in fixed)
        print(f'  {filename}: SVGs={svg_count}, garbled_prefixes_left={remaining}')

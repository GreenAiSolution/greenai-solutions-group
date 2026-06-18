#!/usr/bin/env python3
"""Fix mojibake emoji and text in all HTML files, replacing with clean SVG icons."""

import os

# ─── SVG ICONS ────────────────────────────────────────────────────────────────
ICON_PHONE   = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>'
ICON_ROBOT   = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><line x1="12" y1="7" x2="12" y2="11"/><line x1="8" y1="15" x2="8" y2="17"/><line x1="16" y1="15" x2="16" y2="17"/></svg>'
ICON_CLIP    = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="8" y1="16" x2="14" y2="16"/></svg>'
ICON_TARGET  = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>'
ICON_CHART   = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>'
ICON_USERS   = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
ICON_SHIELD  = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>'
ICON_SHIELD_LG = '<svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,.9)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>'
ICON_SEARCH  = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
ICON_BRUSH   = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L3 14.67V21h6.33l10.06-10.06a5.5 5.5 0 0 0 0-7.77z"/><line x1="15.91" y1="8.49" x2="19.51" y2="12.09"/></svg>'
ICON_BOLT    = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
ICON_PIN     = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'

ICON_PHONE_SM = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,.75)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.39 2 2 0 0 1 3.6 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.6a16 16 0 0 0 6 6l.91-.91a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
ICON_MAIL_SM = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,.75)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>'
ICON_PIN_SM  = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,.75)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'

ICON_PHONE_CONTACT = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.39 2 2 0 0 1 3.6 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.6a16 16 0 0 0 6 6l.91-.91a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
ICON_MAIL_CONTACT = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>'
ICON_PIN_CONTACT = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--green-dark)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'

ICON_PHONE_VISUAL = '<svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="var(--green-light)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="opacity:.9"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>'
ICON_ROBOT_VISUAL = '<svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="var(--green-light)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="opacity:.9"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><line x1="12" y1="7" x2="12" y2="11"/><line x1="8" y1="15" x2="8" y2="17"/><line x1="16" y1="15" x2="16" y2="17"/></svg>'
ICON_CLIP_VISUAL  = '<svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="var(--green-light)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="opacity:.9"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="8" y1="16" x2="14" y2="16"/></svg>'

# ─── BYTE-LEVEL EMOJI REPLACEMENTS ────────────────────────────────────────────
# Each tuple: (original_emoji_utf8_bytes, replacement_string)
# Original bytes are the CORRECT UTF-8 encoding of each emoji.
# The files contain these bytes directly (the garbling is in the browser display,
# not in the stored bytes — confirmed via hex dump analysis).

# We'll work at byte level to be safe.
EMOJI_BYTES = {
    # emoji_utf8_bytes → (tag_context_marker, svg_replacement)
    '📱'.encode(): None,   # U+1F4F1
    '🤖'.encode(): None,   # U+1F916
    '📋'.encode(): None,   # U+1F4CB
    '🎯'.encode(): None,   # U+1F3AF
    '📈'.encode(): None,   # U+1F4C8
    '🤝'.encode(): None,   # U+1F91D
    '🛡️'.encode(): None,  # U+1F6E1 U+FE0F
    '📞'.encode(): None,   # U+1F4DE
    '✉️'.encode(): None,  # U+2709 U+FE0F
    '📍'.encode(): None,   # U+1F4CD
    '📸'.encode(): None,   # U+1F4F8
    '⚡'.encode(): None,   # U+26A1
}


def replace_bytes(data: bytes, old: bytes, new: bytes) -> bytes:
    result = []
    i = 0
    while i < len(data):
        if data[i:i+len(old)] == old:
            result.append(new)
            i += len(old)
        else:
            result.append(data[i:i+1])
            i += 1
    return b''.join(result)


def fix_file(path: str, file_fixes):
    with open(path, 'rb') as f:
        data = f.read()
    # Strip UTF-8 BOM
    if data[:3] == b'\xef\xbb\xbf':
        data = data[3:]

    for old_bytes, new_bytes in file_fixes:
        data = replace_bytes(data, old_bytes, new_bytes)

    with open(path, 'wb') as f:
        f.write(data)


def make_fix(ctx_prefix: str, emoji: str, svg: str):
    """Build a (old_bytes, new_bytes) pair for replacing an emoji inside a specific HTML context."""
    old = (ctx_prefix + emoji).encode('utf-8')
    new = (ctx_prefix + svg).encode('utf-8')
    return (old, new)


# ─── FILE-SPECIFIC FIX LISTS ──────────────────────────────────────────────────

# Shared text fixes (byte level)
TEXT_FIXES = [
    # Em dash U+2014
    ('—'.encode(), '—'.encode()),
    # En dash U+2013
    ('–'.encode(), '–'.encode()),
    # Right single quote (apostrophe) U+2019
    ('’'.encode(), '’'.encode()),  # keep as-is (already correct)
    # Left double quote U+201C
    ('“'.encode(), '"'.encode()),
    # Right double quote U+201D
    ('”'.encode(), '"'.encode()),
    # Middle dot U+00B7
    ('·'.encode(), '·'.encode()),
    # Registered U+00AE
    ('®'.encode(), '®'.encode()),
    # Star U+2605
    ('★'.encode(), '★'.encode()),
    # Ellipsis U+2026
    ('…'.encode(), '…'.encode()),
    # Arrow U+2192
    ('→'.encode(), '→'.encode()),
    # Lightning U+26A1
    ('⚡'.encode(), '⚡'.encode()),  # keep correct
    # Check mark U+2713
    ('✓'.encode(), '✓'.encode()),
    # Heavy ballot X U+2717
    ('✗'.encode(), '✗'.encode()),
    # Black diamond U+25C6
    ('◆'.encode(), '◆'.encode()),
]

# Shared footer icon replacements (same across all pages)
FOOTER_FIXES = [
    make_fix('<div class="footer__contact-icon" aria-hidden="true">', '📞', ICON_PHONE_SM),
    make_fix('<div class="footer__contact-icon" aria-hidden="true">', '✉️', ICON_MAIL_SM),
    make_fix('<div class="footer__contact-icon" aria-hidden="true">', '📍', ICON_PIN_SM),
]

INDEX_FIXES = [
    # Feature icons
    make_fix('<div class="feature-icon" aria-hidden="true">', '📱', ICON_PHONE),
    make_fix('<div class="feature-icon" aria-hidden="true">', '🤖', ICON_ROBOT),
    make_fix('<div class="feature-icon" aria-hidden="true">', '📋', ICON_CLIP),
    make_fix('<div class="feature-icon" aria-hidden="true">', '🎯', ICON_TARGET),
    make_fix('<div class="feature-icon" aria-hidden="true">', '📈', ICON_CHART),
    make_fix('<div class="feature-icon" aria-hidden="true">', '🤝', ICON_USERS),
    # Service card icons
    make_fix('<div class="service-card__icon" aria-hidden="true">', '📱', ICON_PHONE),
    make_fix('<div class="service-card__icon" aria-hidden="true">', '🤖', ICON_ROBOT),
    make_fix('<div class="service-card__icon" aria-hidden="true">', '📋', ICON_CLIP),
    # Guarantee shield
    make_fix('<div style="font-size:4rem;flex-shrink:0;position:relative">', '🛡️', ICON_SHIELD_LG),
] + FOOTER_FIXES + TEXT_FIXES

SERVICES_FIXES = [
    # Service visual icons
    make_fix('<div class="service-detail__visual-icon" aria-hidden="true">', '📱', ICON_PHONE_VISUAL),
    make_fix('<div class="service-detail__visual-icon" aria-hidden="true">', '🤖', ICON_ROBOT_VISUAL),
    make_fix('<div class="service-detail__visual-icon" aria-hidden="true">', '📋', ICON_CLIP_VISUAL),
    # Inline detail list check
    make_fix('<div class="detail-list__icon" aria-hidden="true">', '✔', '✓'),
    # Pricing check/cross
    make_fix('<span class="check" aria-hidden="true">', '✔', '✓'),
    make_fix('<span class="x" aria-hidden="true">', '✗', '✗'),
    # Coverage checks
    ('<span style="color:var(--green-light);font-weight:700">✔</span>'.encode(),
     '<span style="color:var(--green-light);font-weight:700">✓</span>'.encode()),
    # Elite diamonds
    ('<span class="elite-check">◆</span>'.encode(), '<span class="elite-check">◆</span>'.encode()),
    # Notary credentials
    ('✅ NNA Certified'.encode(), '✅ NNA Certified'.encode()),
    ('✅ E&amp;O Insured'.encode(), '✅ E&amp;O Insured'.encode()),
    ('✅ Background Checked'.encode(), '✅ Background Checked'.encode()),
    ('✅ Arizona Commissioned'.encode(), '✅ Arizona Commissioned'.encode()),
    # Inline chat lightning
    ('<span>⚡</span>'.encode(), '<span>⚡</span>'.encode()),
    # Inline handshake in chat bubble (decorative) - replace with text
    ('🤝'.encode(), '🤝'.encode()),
    # Camera emoji in chat bubble
    ('📸'.encode(), '📸'.encode()),
] + FOOTER_FIXES + TEXT_FIXES

ABOUT_FIXES = [
    # Stat badge pin (location)
    ('<div style="font-size:1.5rem" aria-hidden="true">📍</div>'.encode(),
     f'<div style="display:flex;align-items:center;justify-content:center" aria-hidden="true">{ICON_PIN}</div>'.encode()),
    # Mission icons
    make_fix('<div class="mission-icon" aria-hidden="true">', '🎯', ICON_TARGET),
    make_fix('<div class="mission-icon" aria-hidden="true">', '⚡', ICON_BOLT),
    make_fix('<div class="mission-icon" aria-hidden="true">', '🤝', ICON_USERS),
    # Values feature icons
    make_fix('<div class="feature-icon" aria-hidden="true">', '📍', ICON_SEARCH),   # Transparency
    make_fix('<div class="feature-icon" aria-hidden="true">', '📐', ICON_BRUSH),    # Custom
    make_fix('<div class="feature-icon" aria-hidden="true">', '📈', ICON_CHART),    # Results
    make_fix('<div class="feature-icon" aria-hidden="true">', '🛡️', ICON_SHIELD),  # Ethical
] + FOOTER_FIXES + TEXT_FIXES

CONTACT_FIXES = [
    # Contact detail icons
    make_fix('<div class="contact-detail__icon" role="img" aria-label="Phone">', '📞', ICON_PHONE_CONTACT),
    make_fix('<div class="contact-detail__icon" role="img" aria-label="Email">', '✉️', ICON_MAIL_CONTACT),
    make_fix('<div class="contact-detail__icon" role="img" aria-label="Location">', '📍', ICON_PIN_CONTACT),
] + FOOTER_FIXES + TEXT_FIXES


if __name__ == '__main__':
    jobs = [
        ('index.html',    INDEX_FIXES),
        ('services.html', SERVICES_FIXES),
        ('about.html',    ABOUT_FIXES),
        ('contact.html',  CONTACT_FIXES),
    ]
    for filename, fixes in jobs:
        fix_file(filename, fixes)
        with open(filename, 'rb') as f:
            final_bytes = f.read()
        final = final_bytes.decode('utf-8')
        svg_count = final.count('<svg')
        print(f'✓ {filename}  SVG icons={svg_count}')
    print('\nAll files fixed.')

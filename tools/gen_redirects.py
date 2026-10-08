#!/usr/bin/env python3
"""gen_redirects.py — 2026-09-27 reset to four services. Pages for services no longer sold
become redirects so old links, emails and search results still land somewhere true."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOVES = {
    "service-web-design.html":     ("services.html", "Websites are no longer on the menu. GreenAI now runs four services for home service companies."),
    "service-ai-consulting.html":  ("services.html", "Custom systems are no longer on the menu. GreenAI now runs four services for home service companies."),
    "service-ai-seo.html":         ("services.html", "AI SEO is no longer on the menu. GreenAI now runs four services for home service companies."),
    "service-crm-dashboards.html": ("services.html", "CRM work is no longer on the menu. GreenAI now runs four services for home service companies."),
    "service-winback.html":        ("service-reviews.html", "Win-back is now part of reviews and repeat work."),
}
T = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8" />
<title>This page has moved — GreenAI Solutions</title>
<meta http-equiv="refresh" content="0; url={to}" />
<link rel="canonical" href="https://greenaidigital.com/{to}" />
<meta name="robots" content="noindex" />
</head><body style="font-family:system-ui;padding:2rem;background:#06110B;color:#EEF5F0">
<p>{why} This page moved to <a href="{to}" style="color:#E8C46A">{to}</a>.</p>
</body></html>
"""
for f, (to, why) in MOVES.items():
    open(os.path.join(ROOT, f), "w").write(T.format(to=to, why=why)); print("redirect", f, "->", to)

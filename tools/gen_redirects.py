#!/usr/bin/env python3
"""gen_redirects.py — pages for services no longer sold become noindex redirects, so old links,
emails, Stripe receipts and search results still land somewhere true.
2026-09-27: reset to four services. 2026-10-02: reset to TWO, AI agents and review automation.
The six AI employees, the receptionist, AI ads, Property Signals, the plans and the add-ons are
off the menu; their pages, the pool-era agent pages and the old ordering flow redirect here."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOVES = {
    "service-web-design.html":     ("services.html", "Websites are no longer on the menu. GreenAI now runs two services: AI agents and review automation."),
    "service-ai-consulting.html":  ("services.html", "Custom systems are no longer on the menu. GreenAI now runs two services: AI agents and review automation."),
    "service-ai-seo.html":         ("services.html", "AI SEO is no longer on the menu. GreenAI now runs two services: AI agents and review automation."),
    "service-crm-dashboards.html": ("services.html", "CRM work is no longer on the menu. GreenAI now runs two services: AI agents and review automation."),
    "service-winback.html":        ("service-reviews.html", "Win-back is now part of reviews and repeat work."),
    # 2026-10-02: two services only.
    "service-ai-ads.html":           ("services.html", "AI ads are no longer on the menu. GreenAI now runs two services: AI agents and review automation."),
    "service-property-signals.html": ("services.html", "Property Signals is no longer on the menu. GreenAI now runs two services: AI agents and review automation."),
    "ads.html":                      ("services.html", "AI ads are no longer on the menu. GreenAI now runs two services: AI agents and review automation."),
    "staff.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "hire.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "ring.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "dispatch.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "inbox.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "thread.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "huddle.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "books.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "phone.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "leads.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "support.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "billing.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "service-ai-employees.html": ("service-ai-agents.html", "The six AI employees are now one service: AI agents, $397 a month."),
    "net.html": ("service-ai-agents.html", "The pool-company agents are now one service: AI agents, $397 a month."),
    "balance.html": ("service-ai-agents.html", "The pool-company agents are now one service: AI agents, $397 a month."),
    "pump.html": ("service-ai-agents.html", "The pool-company agents are now one service: AI agents, $397 a month."),
    "pay.html": ("contact.html", "Ordering now starts with one conversation. Use the form, or call (480) 798-0753."),
    "start.html": ("contact.html", "Ordering now starts with one conversation. Use the form, or call (480) 798-0753."),
    "onboarding.html": ("contact.html", "Ordering now starts with one conversation. Use the form, or call (480) 798-0753."),
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

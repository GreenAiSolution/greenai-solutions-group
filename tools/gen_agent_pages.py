#!/usr/bin/env python3
"""
gen_agent_pages.py — writes net.html, balance.html and pump.html from the
pool-offer catalog, and keeps the shared nav + footer identical on every page.

    python3 tools/gen_agent_pages.py            # (re)write the three agent pages
    python3 tools/gen_agent_pages.py --chrome about.html faq.html ...
                                               # swap in the shared nav + footer

SOURCE OF TRUTH
  data/catalog.json is a copy of ~/greenai-pool/catalog.json (the file the
  pool MCP server is tested against). Every price, job, won't-do line,
  trained-on list and human-comparison figure on the three pages is read from
  it. Change the catalog first, copy it here, re-run this script, commit all
  four files together. Do not hand-edit net/balance/pump.html — the next run
  overwrites them.

WHAT IS NOT IN THE CATALOG
  Cadence labels and the per-agent FAQ live in EXTRAS below. They are page
  copy, worded from the catalog's own jobs/wont lines, and carry no figures
  that are not already in the catalog.

HOUSE RULES THIS FILE OBEYS
  - Every dark section states its own colour (body ink is dark grey).
  - .page-hero--night is a variant defined at the END of style.css; we only
    add the class, never redefine it.
  - Buy buttons are <a class="buy" data-sku="pool-…"> — checkout.js resolves
    them to the live Stripe links.
  - No testimonials, client names, counts, ROI or competitor pricing.
"""

import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "data", "catalog.json")

with open(CATALOG, encoding="utf-8") as fh:
    CAT = json.load(fh)

BRAND = CAT["brand"]
AGENTS = CAT["agents"]
TERMS = CAT["terms"]

CHECKOUT_V = 8
STYLE_V = 21
SCRIPT_V = 14

# Cache-busters live in one place so the chrome swap can bump every page.
STYLE_TAG = f'<link rel="stylesheet" href="style.css?v={STYLE_V}" />'
SCRIPT_TAGS = (f'<script src="script.js?v={SCRIPT_V}"></script>\n'
               f'  <script src="checkout.js?v={CHECKOUT_V}"></script>')


def esc(s):
    return html.escape(s, quote=False)


def money(n):
    return f"${n:,.0f}"


# --------------------------------------------------------------------------
# Per-agent page copy that is not a catalog field.
# --------------------------------------------------------------------------
EXTRAS = {
    "net": {
        "id": "01",
        "h1": ("Every pool lead answered in ", "8 seconds."),
        "hero_note": "Nights, weekends, the middle of a route. Web form, Google, Thumbtack, a missed call — NET picks it up, asks the four things a quote needs, quotes only from your list, and follows up until it books.",
        "day": [
            ("9:47 PM", "A form lands: “pool’s green, Gilbert 85296, how much?”", "You’re at dinner."),
            ("9:47:08 PM", "NET replies. Asks pool size and how green.", "Eight seconds after it landed."),
            ("9:49 PM", "Quotes weekly service from your price list. Offers Thursday’s first-visit slot.", "A price not on your list cannot send."),
            ("Day 1 · 3 · 7", "No answer yet? A short nudge each time, then it stops.", "The moment they say stop, it stops — and tells you."),
        ],
        "cadence_tag": "How NET follows a lead",
        "cadence": [
            ("+8 SEC", "Answers", "Any hour, any channel."),
            ("+2 MIN", "Asks", "Address, pool size, condition, how often."),
            ("SAME CHAT", "Quotes", "From your list only."),
            ("DAY 1 · 3 · 7", "Follows up", "Until it books or hears stop."),
            ("BOOKED", "Texts you", "The address and the slot."),
        ],
        "faq": [
            ("Does NET answer the phone, or just texts and forms?",
             "Both. It answers the call, or if a call is missed it texts the caller back within seconds. Website form, Google Business messages, Thumbtack, Angi, Yelp, text and email are all in the same inbox."),
            ("Can it quote a green pool or a start-up?",
             "Only in the way you tell it to. Your green-pool and start-up policy is part of what NET is trained on — if your rule is “we look first,” that is what it says, and it books the look."),
            ("What if someone asks for a price that isn’t on my list?",
             "It does not guess. It tells them the owner will confirm, and it flags you. A second checker reads every dollar figure before it sends; a price that is not on your list is blocked."),
            ("Will it pretend to be a person?",
             "No. If anyone asks, it says it is the company’s automated assistant and that you will follow up personally."),
            ("Does it promise me a number of bookings?",
             "No. It promises the reply and the follow-up. Bookings depend on your prices, your area and your season, and nobody honest can promise those for you."),
        ],
    },
    "balance": {
        "id": "02",
        "h1": ("Your customers answered. ", "You stay on the route."),
        "hero_note": "“Is my tech coming today?” “Why is the pool cloudy?” “Can you skip next week?” BALANCE answers from your schedule and house rules, sends the service note, asks for the review — and puts the complaint in front of you, not on Google.",
        "day": [
            ("6:40 AM", "You load the truck. BALANCE has today’s gate codes, dog notes and one “skip this week” on your sheet.", "Nothing to remember."),
            ("11:20 AM", "“Is my tech coming today?” — answered from the route in under a minute.", "You never saw it."),
            ("4:15 PM", "Service notes go out: what was done, the readings you entered, what to watch.", "Same day, every visit."),
            ("+2 days", "The visit went well, so it asks for a Google review. A complaint goes to you instead.", "Never the other way round."),
        ],
        "cadence_tag": "How BALANCE keeps a customer",
        "cadence": [
            ("BEFORE ROUTE", "Notes", "Reschedules, gate, dog, access — in front of you."),
            ("SAME DAY", "Service note", "What was done and what to watch."),
            ("+2 DAYS", "Review ask", "Only after a visit went well."),
            ("SEASONAL", "Notices", "Filter clean, monsoon pass, salt cell, winter hours."),
            ("QUIET / TWICE", "Flags you", "Gone quiet or complained twice — call before they cancel."),
        ],
        "faq": [
            ("Will it tell a customer how much acid or chlorine to add?",
             "No. BALANCE does not diagnose equipment or give chemical dosing over text. It books a tech visit and tells the customer when."),
            ("What does it need from me to answer “is my tech coming today?”",
             "Your weekly route schedule. A sheet or an export from your scheduling software is enough; you do not have to change tools."),
            ("Can it write the review for the customer?",
             "No. It only asks, two days after a visit that went well, with your review link. A complaint is routed to your phone instead of to Google."),
            ("What if a customer says stop?",
             "One “stop” ends every message to that customer. It does not send anything a customer has not agreed to receive."),
            ("Does it handle reschedules?",
             "It takes the request, applies your house rules on skips and credits, and puts the change in front of you before the route so you approve it."),
        ],
    },
    "pump": {
        "id": "03",
        "h1": ("Quotes chased. Invoices sent. ", "Late payers reminded."),
        "hero_note": "Every open repair quote followed up on day 2, 5 and 10. The monthly invoice out on the day you pick with your payment link. Late payers reminded at 7, 14 and 21 days — firm, never rude — and a Monday list of who still owes.",
        "day": [
            ("Tue 3:05 PM", "You flag a failing filter cartridge on a visit. PUMP sends the quote you approved, at your price.", "Written once, sent right."),
            ("Day 2 · 5 · 10", "The quote is chased until it is approved or declined.", "Nothing sits open because you forgot."),
            ("The 1st", "Monthly invoices go out with your payment link.", "On the day you pick."),
            ("Day 7 · 14 · 21", "Late payers get the reminder in the tone you approved. 30+ days: you decide whether to pause service.", "Firm, never rude, never collections."),
        ],
        "cadence_tag": "How PUMP moves the money",
        "cadence": [
            ("DAY 2 · 5 · 10", "Quote chase", "Every open repair quote."),
            ("YOUR DAY", "Invoice", "Monthly, with your payment link."),
            ("DAY 7 · 14 · 21", "Reminders", "In the tone you approve."),
            ("30+ DAYS", "Your call", "Pause service or not — you decide."),
            ("MONDAY", "The list", "Approved, paid, still owes."),
        ],
        "faq": [
            ("Does PUMP take the payment?",
             "No. It sends the link to the payment processor you already use. It never sees a card number and never processes a charge itself."),
            ("Can it offer a discount to get an invoice paid?",
             "No. It never changes a price, offers a discount or waives a fee on its own. If that decision needs making, it is yours."),
            ("Will it threaten anyone or mention collections?",
             "Never. No collections agencies, no credit talk, and it contacts nobody but the account holder. The 21-day reminder is still polite."),
            ("What is the “we noticed on today’s visit” message?",
             "An upsell you approve in advance — filter clean, cartridge replacement, acid wash — sent with your price after a visit where you flagged it. Nothing you have not listed."),
            ("What do I actually see each week?",
             "A Monday list: quotes approved, invoices paid, and who still owes and for how long. That is the whole report."),
        ],
    },
}

PORTRAIT_ALT = {
    "net": "NET, a drawn robot portrait in deep-end teal holding a skimmer net with one glowing lead caught in it",
    "balance": "BALANCE, a drawn robot portrait in plaster green with a spirit level across its crown and a balance scale on its chest",
    "pump": "PUMP, a drawn robot portrait in bronze with a pump impeller on its shoulder and a paid ledger on its chest",
}

# --------------------------------------------------------------------------
# Shared chrome — the same bytes on every page.
# --------------------------------------------------------------------------
PHONE_SVG = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.39 2 2 0 0 1 3.6 1h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.6a16 16 0 0 0 6 6l.91-.91a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>')
MAIL_SVG = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>')


def crew_submenu():
    items = "".join(
        f'<li><a href="{a["page"]}">{esc(a["name"])} &mdash; {esc(a["role"].lower())} &middot; {money(a["price_month"])}/mo</a></li>'
        for a in AGENTS)
    return ('<ul class="nav__submenu" role="list">' + items +
            '<li class="nav__submenu-label">See it work</li>'
            '<li><a href="catch.html">Watch it catch a lead</a></li>'
            '<li><a href="call.html">Hear it as your company</a></li>'
            '<li><a href="faq.html">Questions</a></li></ul>')


def contact_submenu():
    return ('<ul class="nav__submenu" role="list">'
            f'<li><a href="tel:{BRAND["phone_tel"]}" style="display:flex;align-items:center">{PHONE_SVG}{esc(BRAND["phone_display"])}</a></li>'
            f'<li><a href="mailto:{BRAND["email"]}" style="display:flex;align-items:center">{MAIL_SVG}{esc(BRAND["email"])}</a></li></ul>')


def nav_html():
    crew = crew_submenu()
    contact = contact_submenu()
    links = (
        '<li><a href="index.html"    class="nav__link" data-page="index.html">Home</a></li>\n'
        f'          <li class="nav__dropdown nav__dropdown--gold"><a href="index.html#crew" class="nav__link" data-page="crew">The Crew <span class="nav__caret" aria-hidden="true">▾</span></a>{crew}</li>\n'
        '          <li><a href="about.html"    class="nav__link" data-page="about.html">About</a></li>\n'
        f'          <li class="nav__dropdown nav__dropdown--right"><a href="contact.html" class="nav__link" data-page="contact.html">Contact <span class="nav__caret" aria-hidden="true">▾</span></a>{contact}</li>'
    )
    mobile = (
        '<li><a href="index.html"    class="nav__link" data-page="index.html">Home</a></li>\n'
        f'        <li class="nav__dropdown nav__dropdown--gold"><a href="index.html#crew" class="nav__link" data-page="crew">The Crew</a>{crew}</li>\n'
        '        <li><a href="about.html"    class="nav__link" data-page="about.html">About</a></li>\n'
        f'        <li class="nav__dropdown nav__dropdown--right"><a href="contact.html" class="nav__link" data-page="contact.html">Contact <span class="nav__caret" aria-hidden="true">▾</span></a>{contact}</li>\n'
        '        <li style="padding:.5rem 1rem"><a href="catch.html" class="btn btn-primary" style="width:100%;justify-content:center">Watch it catch a lead</a></li>'
    )
    return f'''<nav class="nav transparent" id="main-nav" aria-label="Main navigation">
    <div class="container">
      <div class="nav__inner">
        <a href="index.html" class="nav__logo" aria-label="GreenAI Solutions Team home">
          <div class="nav__logo-icon"><img src="logo-mark.png" alt="GreenAI Solutions Team crest" width="40" height="40" loading="eager" decoding="async"/></div>
          <div class="nav__logo-text">
            <span class="nav__logo-name">Green<span style="color:#D4AF37">AI</span></span>
            <span class="nav__logo-sub">Solutions Team</span>
          </div>
        </a>

        <ul class="nav__links" role="list">
          {links}
        </ul>

        <a href="catch.html" class="btn btn-primary nav__cta">Watch it catch a lead</a>

        <button class="nav__hamburger" aria-label="Toggle mobile menu" aria-expanded="false">
          <span></span><span></span><span></span>
        </button>
      </div>

      <!-- Mobile menu -->
      <ul class="nav__mobile" role="list">
        {mobile}
      </ul>
    </div>
  </nav>'''


def footer_html():
    crew_links = "".join(
        f'<li><a href="{a["page"]}" style="color:#D4AF37;font-weight:600">{esc(a["name"])} &mdash; {esc(a["role"].lower())} &middot; {money(a["price_month"])}/mo</a></li>'
        for a in AGENTS)
    ico = 'stroke="rgba(255,255,255,.75)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    return f'''<footer class="footer" aria-label="Site footer">
    <div class="container">
      <div class="footer__grid">
        <div class="footer__brand">
          <a href="index.html" class="footer__logo" aria-label="GreenAI home">
            <div class="footer__logo-icon"><img src="logo-mark.png" alt="GreenAI" width="36" height="36" loading="lazy" decoding="async"/></div>
            <span class="footer__logo-name">Green<span style="color:#D4AF37">AI</span> Solutions Team</span>
          </a>
          <p class="footer__tagline">Three AI employees for Phoenix-metro pool service companies. NET catches every lead, BALANCE keeps every customer, PUMP keeps the money moving. Month to month.</p>
          <p style="font-size:.78rem;color:rgba(255,255,255,.62)">Jaden Green, doing business as GreenAI Solutions<br/>Gilbert, Arizona</p>
        </div>

        <div>
          <h5>Navigation</h5>
          <ul class="footer__links" role="list">
            <li><a href="index.html">Home</a></li>
            <li><a href="index.html#crew">The crew</a></li>
            <li><a href="about.html">About</a></li>
            <li><a href="faq.html">Questions &amp; Answers</a></li>
            <li><a href="contact.html">Contact</a></li>
            <li><a href="pay.html">Start</a></li>
            <li><a href="testimonials.html">Past work</a></li>
          </ul>
        </div>

        <div>
          <h5>The crew</h5>
          <ul class="footer__links" role="list">
            {crew_links}
            <li style="padding-top:.4rem;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.35)">See it work</li>
            <li><a href="catch.html">Watch it catch a lead</a></li>
            <li><a href="call.html">Hear it as your company</a></li>
            <li><a href="demo.html">Try it with your own prices</a></li>
          </ul>
        </div>

        <div>
          <h5>Contact Us</h5>
          <div class="footer__contact-item">
            <div class="footer__contact-icon" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" {ico}><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.39 2 2 0 0 1 3.6 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.6a16 16 0 0 0 6 6l.91-.91a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg></div>
            <div>
              <a href="tel:{BRAND["phone_tel"]}" style="color:rgba(255,255,255,.65)">{esc(BRAND["phone_display"])}</a>
            </div>
          </div>
          <div class="footer__contact-item">
            <div class="footer__contact-icon" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" {ico}><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></div>
            <div>
              <a href="mailto:{BRAND["email"]}" style="color:rgba(255,255,255,.65)">{esc(BRAND["email"])}</a>
            </div>
          </div>
          <div class="footer__contact-item">
            <div class="footer__contact-icon" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" {ico}><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg></div>
            <div>Gilbert, Arizona 85296</div>
          </div>
          <div class="footer__contact-item">
            <div class="footer__contact-icon" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" {ico}><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg></div>
            <div>
              <div class="footer__contact-label" style="font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.68);margin-bottom:.2rem">Instagram</div>
              <div><a href="https://instagram.com/GreenAI_solutions" target="_blank" rel="noopener" style="color:rgba(255,255,255,.65)">@GreenAI_solutions</a></div>
            </div>
          </div>
        </div>
      </div>

      <div class="footer__legal">
        <a href="privacy.html">Privacy Policy</a>
        <span style="color:rgba(255,255,255,.25)">·</span>
        <a href="terms.html">Terms of Service</a>
        <span style="color:rgba(255,255,255,.25)">·</span>
        <a href="agreement.html">Service Agreement</a>
      </div>

      <div class="footer__bottom">
        <span>&copy; <span class="js-year">2026</span> Green<span style="color:#D4AF37">AI</span> Solutions Team. All rights reserved.</span>
        <span class="footer__bottom-right">Built for pool companies. Gilbert, AZ.</span>
      </div>
    </div>
  </footer>'''


# --------------------------------------------------------------------------
# Agent page template
# --------------------------------------------------------------------------
PAGE_CSS = """
    /* ---- crew page: pool water on the GreenAI night ground ------------------
       --ac is this agent's accent from the catalog. Every dark block below
       states its own colour: body ink is dark grey and would vanish. ---- */
    .crew-hero { text-align:left; padding:8.5rem 0 4.5rem; color:#fff; }
    .crew-hero__grid { display:grid; grid-template-columns:1.05fr .95fr; gap:clamp(2rem,5vw,4.5rem); align-items:center; }
    .crew-hero .badge { display:inline-flex; align-items:center; gap:.7rem; padding:.55rem .95rem .55rem .7rem; margin-bottom:1.4rem; border:1px solid color-mix(in srgb, var(--ac) 45%, transparent); border-radius:100px; background:color-mix(in srgb, var(--ac) 10%, transparent); }
    .crew-hero .badge__id { font:700 .6rem/1 ui-monospace,SFMono-Regular,Menlo,monospace; letter-spacing:.2em; color:var(--ac); }
    .crew-hero .badge__role { font-size:.78rem; color:rgba(255,255,255,.78); letter-spacing:.02em; }
    .crew-hero h1 { font-size:clamp(2.4rem,4.6vw,3.9rem); line-height:1.04; letter-spacing:-.03em; margin:0 0 1rem; max-width:16ch; }
    .crew-hero h1 em { font-style:italic; color:#e7c85f; }
    .crew-hero .page-hero-lede { margin:0; max-width:56ch; color:rgba(255,255,255,.78); font-size:1.05rem; line-height:1.7; }
    .crew-price { display:flex; align-items:baseline; gap:.6rem; margin:1.75rem 0 .4rem; }
    .crew-price b { font-family:'Playfair Display',serif; font-size:clamp(3rem,5vw,4.2rem); line-height:.9; color:#e7c85f; letter-spacing:-.02em; }
    .crew-price span { color:rgba(255,255,255,.62); font-weight:600; }
    .crew-terms { margin:0 0 1.6rem; color:rgba(255,255,255,.62); font-size:.86rem; }
    .cap-cta { display:flex; flex-wrap:wrap; gap:.85rem; }
    .cap-ghost { background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.35); color:#fff; }
    .cap-ghost:hover { background:color-mix(in srgb, var(--ac) 18%, transparent); border-color:var(--ac); color:#fff; }
    .crew-portrait { position:relative; justify-self:center; width:min(100%,400px); }
    .crew-portrait::before { content:''; position:absolute; inset:12% 6% -4%; border-radius:50%; background:var(--ac); opacity:.22; filter:blur(48px); }
    .crew-portrait img { position:relative; display:block; width:100%; height:auto; border-radius:22px; border:1px solid color-mix(in srgb, var(--ac) 40%, transparent); box-shadow:0 40px 90px rgba(0,0,0,.5); }
    .crew-portrait__tag { position:absolute; left:1rem; bottom:1rem; display:inline-flex; align-items:center; gap:.5rem; padding:.45rem .8rem; border-radius:100px; background:rgba(3,8,5,.78); border:1px solid rgba(255,255,255,.14); color:#fff; font:700 .62rem/1 ui-monospace,SFMono-Regular,Menlo,monospace; letter-spacing:.14em; text-transform:uppercase; }
    .crew-portrait__tag i { width:7px; height:7px; border-radius:50%; background:var(--ac); box-shadow:0 0 10px var(--ac); }
    .crew-hero .gv-spec { margin-top:2.25rem; }
    @media (max-width:900px) { .crew-hero__grid { grid-template-columns:1fr; } .crew-portrait { order:-1; width:min(100%,320px); } .crew-hero { padding-top:7rem; } }

    /* one day */
    .day { display:grid; grid-template-columns:repeat(4,1fr); gap:1.25rem; max-width:1100px; margin:0 auto; }
    .day__step { position:relative; padding:1.5rem 1.4rem 1.4rem; border-left:3px solid var(--ac); background:#fff; border-radius:0 14px 14px 0; box-shadow:0 10px 30px rgba(0,0,0,.05); }
    .day__step time { display:block; font:700 .72rem/1 ui-monospace,SFMono-Regular,Menlo,monospace; letter-spacing:.12em; color:var(--green-dark,#1a5c2a); text-transform:uppercase; }
    .day__step h3 { font-size:1.02rem; line-height:1.4; margin:.7rem 0 .45rem; color:var(--gray-800,#1f2937); }
    .day__step p { font-size:.88rem; color:var(--gray-600,#4b5563); margin:0; }
    @media (max-width:980px) { .day { grid-template-columns:1fr 1fr; } }
    @media (max-width:560px) { .day { grid-template-columns:1fr; } }

    /* jobs */
    .jobs { display:grid; grid-template-columns:repeat(3,1fr); gap:1.25rem; max-width:1100px; margin:0 auto; }
    .job { position:relative; padding:1.6rem 1.5rem 1.5rem 1.6rem; border-radius:14px; background:linear-gradient(180deg,#fff,#f6faf7); border:1px solid #e4ebe5; }
    .job__n { display:inline-grid; place-items:center; width:34px; height:34px; border-radius:10px; background:color-mix(in srgb, var(--ac) 22%, #fff); color:var(--green-dark,#1a5c2a); font:800 .74rem/1 ui-monospace,SFMono-Regular,Menlo,monospace; margin-bottom:.9rem; }
    .job p { margin:0; font-size:.98rem; line-height:1.55; color:var(--gray-800,#1f2937); }
    @media (max-width:900px) { .jobs { grid-template-columns:1fr 1fr; } }
    @media (max-width:560px) { .jobs { grid-template-columns:1fr; } }

    /* config sheet — the file your company becomes */
    .sheet-wrap { display:grid; grid-template-columns:.9fr 1.1fr; gap:clamp(2rem,5vw,4rem); align-items:center; max-width:1100px; margin:0 auto; color:#fff; }
    .sheet-wrap h2 { color:#fff; margin:.6rem 0 1rem; }
    .sheet-wrap p { color:rgba(255,255,255,.72); font-size:1rem; line-height:1.7; }
    .sheet { margin:0; border:1px solid rgba(255,255,255,.12); border-radius:18px; background:rgba(8,19,12,.72); overflow:hidden; box-shadow:0 30px 70px rgba(0,0,0,.35); }
    .sheet__head { display:flex; align-items:center; gap:.6rem; padding:.9rem 1.2rem; border-bottom:1px solid rgba(255,255,255,.09); color:rgba(255,255,255,.62); font:600 .7rem/1 ui-monospace,SFMono-Regular,Menlo,monospace; letter-spacing:.06em; }
    .sheet__dot { width:7px; height:7px; border-radius:50%; background:var(--ac); box-shadow:0 0 12px var(--ac); }
    .sheet ol { list-style:none; margin:0; padding:.5rem 0; }
    .sheet li { display:grid; grid-template-columns:2.2rem 1fr; gap:.8rem; align-items:baseline; padding:.8rem 1.25rem; border-bottom:1px solid rgba(255,255,255,.06); color:rgba(255,255,255,.88); font-size:.95rem; line-height:1.5; }
    .sheet li:last-child { border-bottom:0; }
    .sheet li b { font:700 .7rem/1.6 ui-monospace,SFMono-Regular,Menlo,monospace; color:var(--ac); letter-spacing:.08em; }
    .sheet__foot { padding:.9rem 1.25rem 1.1rem; border-top:1px solid rgba(255,255,255,.09); color:rgba(255,255,255,.6); font-size:.8rem; line-height:1.6; }
    @media (max-width:860px) { .sheet-wrap { grid-template-columns:1fr; } }

    /* won't do */
    .wont { background:#072E37; color:#fff; border-top:1px solid rgba(63,208,195,.18); }
    .wont .section-label { color:#3FD0C3; }
    .wont h2 { color:#fff; }
    .wont .gv-spec { --gv-line:rgba(255,255,255,.16); --gv-dim:rgba(255,255,255,.62); --gv-ink:#fff; margin-top:2rem; }
    .wont .gv-spec__k { color:#3FD0C3; }
    .wont .gv-spec__v { color:#fff; font-weight:600; }

    /* ledger: what it replaces */
    .vs { display:grid; grid-template-columns:1fr auto 1fr; align-items:stretch; gap:1rem; max-width:760px; margin:2.5rem auto 0; }
    .vs__col { border-radius:14px; padding:1.4rem 1rem; text-align:center; }
    .vs__col span { display:block; font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; margin-bottom:.5rem; line-height:1.4; }
    .vs__col b { display:block; font-family:'Playfair Display',serif; font-size:2.8rem; line-height:1; }
    .vs__col b small { font-size:1rem; font-family:Inter,sans-serif; font-weight:500; opacity:.7; }
    .vs__col em { display:block; font-style:normal; font-size:.82rem; margin-top:.6rem; }
    .vs__col--human { background:#fff; border:1px dashed rgba(26,92,42,.3); color:var(--gray-600,#4b5563); }
    .vs__col--human b { color:var(--gray-600,#4b5563); text-decoration:line-through; text-decoration-color:rgba(192,57,43,.8); text-decoration-thickness:3px; }
    .vs__col--agent { background:#0c1a0e; border:1px solid color-mix(in srgb, var(--ac) 55%, transparent); color:#fff; box-shadow:0 20px 50px rgba(6,31,16,.18); }
    .vs__col--agent span { color:rgba(255,255,255,.7); }
    .vs__col--agent b { color:#e7c85f; }
    .vs__col--agent em { color:rgba(255,255,255,.72); }
    .vs__mid { align-self:center; font:800 .8rem/1 Inter,sans-serif; letter-spacing:.2em; color:var(--gray-400,#9ca3af); }
    .vs-foot { text-align:center; max-width:60ch; margin:1.25rem auto 0; font-size:.82rem; color:var(--gray-600,#4b5563); }
    @media (max-width:640px) { .vs { grid-template-columns:1fr; } .vs__mid { display:none; } }

    /* cadence — the rail, held still (trust reads as still) */
    .cadence { background:#050b07; color:#fff; }
    .cadence .section-label { color:var(--ac); }
    .cadence h2 { color:#fff; }
    .cadence .gv { max-width:1000px; margin:2rem auto 0; }
    .cadence .gv-rail__pulse { display:none; }
    .cadence .gv-stop:first-child .gv-stop__dot { border-color:var(--ac); }
    .cadence .gv-stop__d { color:rgba(255,255,255,.66); }

    /* faq */
    .qa { max-width:820px; margin:0 auto; display:grid; gap:.75rem; }
    .qa details { border:1px solid #e4ebe5; border-radius:14px; background:#fff; padding:0; }
    .qa summary { cursor:pointer; list-style:none; padding:1.1rem 3rem 1.1rem 1.3rem; font-weight:700; color:var(--gray-800,#1f2937); position:relative; }
    .qa summary::-webkit-details-marker { display:none; }
    .qa summary::after { content:'+'; position:absolute; right:1.2rem; top:50%; transform:translateY(-50%); font-size:1.3rem; color:var(--green-dark,#1a5c2a); }
    .qa details[open] summary::after { content:'\\2013'; }
    .qa summary:focus-visible { outline:2px solid var(--green-accent,#4caf6e); outline-offset:2px; border-radius:14px; }
    .qa details p { margin:0; padding:0 1.3rem 1.2rem; color:var(--gray-600,#4b5563); line-height:1.65; font-size:.95rem; }

    /* close */
    .cap-price { text-align:center; max-width:680px; margin:0 auto; }
    .cap-price .n { font-family:'Playfair Display',serif; font-size:4rem; line-height:1; color:var(--green-dark,#1a5c2a); }
    .cap-price .n small { font-size:1.2rem; color:var(--gray-600,#4b5563); font-family:Inter,sans-serif; font-weight:500; }
    .cap-price p { color:var(--gray-600,#4b5563); margin:.75rem auto 1.5rem; }
    .cap-price .ask { display:block; margin-top:1rem; color:var(--gray-600,#4b5563); font-size:.92rem; text-decoration:underline; text-underline-offset:3px; }
    .cap-others { display:grid; grid-template-columns:repeat(2,1fr); gap:1rem; max-width:760px; margin:0 auto; }
    .cap-others a { display:block; padding:1.1rem 1.2rem; border-radius:12px; border:1px solid rgba(26,92,42,.15); text-decoration:none; color:var(--gray-800,#1f2937); background:#fff; transition:.2s; }
    .cap-others a:hover { border-color:var(--green-accent,#4caf6e); transform:translateY(-2px); }
    .cap-others a b { display:block; font-size:1rem; color:var(--green-dark,#1a5c2a); }
    .cap-others a span { font-size:.84rem; color:var(--gray-600,#4b5563); }
    @media (max-width:520px) { .cap-others { grid-template-columns:1fr; } .cap-price .n { font-size:3rem; } }
    /* buy = the one gold action on the page; the nav's green button is 'watch', not 'buy' */
    .btn-primary.buy { background:#D4AF37; border-color:#D4AF37; color:#061008; }
    .btn-primary.buy:hover { background:#e7c85f; border-color:#e7c85f; color:#061008; }
    [hidden] { display:none !important; }
"""


def jsonld(a):
    price = str(a["price_month"])
    data = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": f"{a['name']} — AI employee for pool service companies: {a['role'].lower()}",
        "serviceType": a["role"],
        "description": a["tagline"],
        "url": f"https://{BRAND['domain']}/{a['page']}",
        "provider": {
            "@type": "ProfessionalService",
            "name": BRAND["company"],
            "url": f"https://{BRAND['domain']}",
            "telephone": "+1-480-798-0753",
            "email": BRAND["email"],
            "address": {"@type": "PostalAddress", "addressLocality": "Gilbert", "addressRegion": "AZ",
                        "postalCode": "85296", "addressCountry": "US"},
        },
        "areaServed": [{"@type": "City", "name": c} for c in
                       ["Phoenix", "Mesa", "Gilbert", "Chandler", "Scottsdale", "Tempe", "Glendale", "Peoria"]],
        "audience": {"@type": "BusinessAudience", "name": "Residential pool service companies"},
        "offers": {
            "@type": "Offer",
            "name": f"{a['name']}, month to month",
            "price": price,
            "priceCurrency": "USD",
            "priceSpecification": {"@type": "UnitPriceSpecification", "price": price, "priceCurrency": "USD",
                                   "billingDuration": "P1M", "unitText": "per month"},
            "url": f"https://{BRAND['domain']}/pay.html?sku={a['sku']}",
            "availability": "https://schema.org/InStock",
        },
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def build_page(a):
    x = EXTRAS[a["id"]]
    others = [o for o in AGENTS if o["id"] != a["id"]]
    price = money(a["price_month"])
    hc = a["human_comparison"]
    title = f"{a['name']} — {a['role']} for pool companies, {price}/mo — GreenAI Solutions"
    desc = f"{a['name']}: {a['tagline']} {price} a month, month to month. Built for Phoenix-metro pool service companies."
    h1a, h1b = x["h1"]

    channels = " &middot; ".join(esc(c.split(" (")[0]) for c in a["channels"])
    day = "".join(
        f'<div class="day__step reveal"><time>{esc(t)}</time><h3>{esc(h)}</h3><p>{esc(p)}</p></div>'
        for t, h, p in x["day"])
    jobs = "".join(
        f'<div class="job reveal"><span class="job__n">{i + 1:02d}</span><p>{esc(j)}</p></div>'
        for i, j in enumerate(a["jobs"]))
    sheet = "".join(
        f'<li><b>{i + 1:02d}</b><span>{esc(t)}</span></li>' for i, t in enumerate(a["trained_on"]))
    wont = "".join(
        f'<span class="gv-spec__i"><b class="gv-spec__k">{"NEVER" if i == 0 else "AND NEVER"}</b><span class="gv-spec__v">{esc(w)}</span></span>'
        for i, w in enumerate(a["wont"]))
    cadence = "".join(
        f'<span class="gv-stop"><i class="gv-stop__dot"></i><b class="gv-stop__n">{esc(n)}</b><b class="gv-stop__t">{esc(t)}</b><span class="gv-stop__d">{esc(d)}</span></span>'
        for n, t, d in x["cadence"])
    faq = "".join(
        f'<details><summary>{esc(q)}</summary><p>{esc(ans)}</p></details>' for q, ans in x["faq"])
    others_html = "".join(
        f'<a href="{o["page"]}"><b>{esc(o["name"])} &middot; {money(o["price_month"])}/mo</b><span>{esc(o["role"])}. {esc(o["tagline"].split(".")[0])}.</span></a>'
        for o in others)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <!-- GENERATED by tools/gen_agent_pages.py from data/catalog.json — do not hand-edit. -->
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,700;0,800;1,700&display=swap" rel="stylesheet" />
  {STYLE_TAG}
  <link rel="stylesheet" href="visuals.css?v=1" />
  <link rel="icon" type="image/x-icon" href="favicon.ico" />
  <link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png" />
  <link rel="icon" type="image/png" sizes="16x16" href="favicon-16.png" />
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png" />
  <link rel="canonical" href="https://{BRAND['domain']}/{a['page']}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://{BRAND['domain']}/{a['page']}" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:image" content="https://{BRAND['domain']}/og-card.jpg" />
  <style>
    :root {{ --ac: {a['color']}; }}{PAGE_CSS}  </style>
  <script type="application/ld+json">
{jsonld(a)}
  </script>
  <script src="analytics.js?v=2"></script>
</head>
<body>
  <a href="#main" class="skip-link">Skip to content</a>
  {nav_html()}

  <header class="page-hero page-hero--night crew-hero">
    <div class="container">
      <div class="crew-hero__grid">
        <div>
          <div class="badge"><span class="badge__id">GREENAI CREW &middot; {x['id']}</span><span class="badge__role">{esc(a['name'])} &middot; {esc(a['role'])}</span></div>
          <h1>{esc(h1a)}<em>{esc(h1b)}</em></h1>
          <p class="page-hero-lede">{x['hero_note']}</p>
          <div class="crew-price"><b>{price}</b><span>per month</span></div>
          <p class="crew-terms">{esc(TERMS['billing'])}</p>
          <div class="cap-cta">
            <a href="pay.html?sku={a['sku']}" class="btn btn-primary btn-lg buy" data-sku="{a['sku']}">Hire {esc(a['name'])} &mdash; {price}/mo</a>
            <a href="call.html" class="btn btn-lg cap-ghost">Hear it as your company</a>
          </div>
          <div class="gv gv-spec" role="img" aria-label="{esc(a['name'])} works on: {esc(', '.join(c.split(' (')[0] for c in a['channels']))}. Built and trained for your company before it goes live. You approve every script.">
            <span class="gv-spec__i"><b class="gv-spec__k">WORKS ON</b><span class="gv-spec__v">{channels}</span></span>
            <span class="gv-spec__i"><b class="gv-spec__k">BEFORE IT GOES LIVE</b><span class="gv-spec__v">Built and trained for your company. You approve every script.</span></span>
          </div>
        </div>
        <figure class="crew-portrait">
          <img src="agents/agent-{a['id']}.svg" alt="{esc(PORTRAIT_ALT[a['id']])}" width="432" height="576" loading="eager" decoding="async"/>
          <figcaption class="crew-portrait__tag"><i aria-hidden="true"></i>{esc(a['name'])} &middot; on duty</figcaption>
        </figure>
      </div>
    </div>
  </header>

  <main id="main">
    <section class="section bg-pale">
      <div class="container">
        <div class="text-center" style="margin-bottom:2.5rem"><span class="section-label">One ordinary day</span><h2>What actually happens</h2></div>
        <div class="day">{day}</div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="text-center" style="margin-bottom:2.5rem"><span class="section-label">The job</span><h2>What {esc(a['name'])} does</h2></div>
        <div class="jobs">{jobs}</div>
      </div>
    </section>

    <section class="section" style="background:#050b07;color:#fff">
      <div class="container">
        <div class="sheet-wrap reveal">
          <div>
            <span class="section-label" style="color:var(--ac)">Trained on your company</span>
            <h2>Your prices. Your rules. Your name.</h2>
            <p>{esc(TERMS['setup'])} This is the whole list of what we need from you &mdash; most of it you already have on a sheet or in your head.</p>
          </div>
          <figure class="sheet">
            <figcaption class="sheet__head"><span class="sheet__dot" aria-hidden="true"></span>your-company / {a['id']}.config</figcaption>
            <ol>{sheet}</ol>
            <p class="sheet__foot">One file. You read and approve every line before {esc(a['name'])} goes live, and you own it &mdash; along with every script and transcript.</p>
          </figure>
        </div>
      </div>
    </section>

    <section class="section wont">
      <div class="container">
        <div class="text-center"><span class="section-label">The rules it works inside</span><h2>What {esc(a['name'])} will not do</h2></div>
        <div class="gv gv-spec" role="list">{wont}</div>
      </div>
    </section>

    <section class="section bg-pale">
      <div class="container">
        <div class="text-center"><span class="section-label">What it replaces</span><h2>The same job, two payrolls</h2></div>
        <div class="vs">
          <div class="vs__col vs__col--human"><span>{esc(hc['label'])}</span><b>{money(hc['usd_month'])}<small>/mo</small></b></div>
          <div class="vs__mid">vs</div>
          <div class="vs__col vs__col--agent"><span>{esc(a['name'])} &middot; {esc(a['role'].lower())}</span><b>{price}<small>/mo</small></b><em>{esc(TERMS['billing'].split('.')[0])}. {esc(TERMS['billing'].split('.')[1].strip())}.</em></div>
        </div>
        <p class="vs-foot">The left figure is a Phoenix wage plus payroll tax for that role. {esc(a['name'])} does the part of the job that is answering, sending and chasing &mdash; a person is still the one on the route.</p>
      </div>
    </section>

    <section class="section cadence">
      <div class="container">
        <div class="text-center"><span class="section-label">{esc(x['cadence_tag'])}</span><h2>Every step, on a clock you set</h2></div>
        <div class="gv gv-rail" role="img" aria-label="{esc('; '.join(f'{n}: {t} — {d}' for n, t, d in x['cadence']))}">
          <div class="gv-rail__track">
            <div class="gv-rail__line"></div>
            <div class="gv-rail__pulse"></div>
            <div class="gv-rail__stops">{cadence}</div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="text-center" style="margin-bottom:2rem"><span class="section-label">Questions pool owners ask</span><h2>Before you hire {esc(a['name'])}</h2></div>
        <div class="qa">{faq}</div>
      </div>
    </section>

    <section class="section bg-pale">
      <div class="container">
        <div class="cap-price">
          <div class="n">{price}<small>/month, flat</small></div>
          <p>{esc(TERMS['setup'])} {esc(TERMS['billing'])}</p>
          <a href="pay.html?sku={a['sku']}" class="btn btn-primary btn-lg buy" data-sku="{a['sku']}">Hire {esc(a['name'])} &mdash; {price}/mo</a>
          <a href="contact.html?want={a['sku']}" class="ask">or ask a question first &#8599;</a>
        </div>
        <div class="text-center" style="margin:3.5rem 0 1.25rem"><span class="section-label">The rest of the crew</span></div>
        <div class="cap-others">{others_html}</div>
      </div>
    </section>
  </main>

  {footer_html()}

  {SCRIPT_TAGS}
</body>
</html>
'''


# --------------------------------------------------------------------------
# Chrome swap for existing pages
# --------------------------------------------------------------------------
NAV_RE = re.compile(r'<nav class="nav transparent"[^>]*>.*?</nav>', re.S)
FOOT_RE = re.compile(r'<footer class="footer"[^>]*>.*?</footer>', re.S)


def swap_chrome(path):
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    out = src.replace('<!--NAV-->', nav_html()).replace('<!--FOOTER-->', footer_html())
    out, n_nav = NAV_RE.subn(lambda m: nav_html(), out, count=1)
    n_foot = 0
    if 'footer__grid' in out:
        out, n_foot = FOOT_RE.subn(lambda m: footer_html(), out, count=1)
    out = re.sub(r'checkout\.js\?v=\d+', f'checkout.js?v={CHECKOUT_V}', out)
    if out != src:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(out)
    return n_nav, n_foot


def main(argv):
    if argv and argv[0] == "--chrome":
        for p in argv[1:]:
            n_nav, n_foot = swap_chrome(p)
            print(f"{os.path.basename(p)}: nav={n_nav} footer={n_foot}")
        return
    for a in AGENTS:
        p = os.path.join(ROOT, a["page"])
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(build_page(a))
        print(f"wrote {a['page']}  ({os.path.getsize(p):,} bytes)")


if __name__ == "__main__":
    main(sys.argv[1:])

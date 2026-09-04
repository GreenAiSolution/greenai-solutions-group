#!/usr/bin/env python3
"""
gen_faq.py — rewrites the question list on faq.html from ONE source, so the
visible accordion and the FAQPage JSON-LD can never drift apart.

    python3 tools/gen_faq.py

It replaces three regions of faq.html, each fenced by HTML comments:
  <!--FAQ:JSONLD-->…<!--/FAQ:JSONLD-->   the schema.org FAQPage <script> block
  <!--FAQ:JUMP-->…<!--/FAQ:JUMP-->       the group jump links in the hero
  <!--FAQ:BODY-->…<!--/FAQ:BODY-->       the accordion groups
Everything else on the page (CSS, hero, CTA, nav, footer) is left alone.

Written for pool-company owners, 2026-09-03. Prices and facts come from
data/catalog.json; the questions are the ones a Phoenix pool-service owner
actually asks, including the software objections (Skimmer, Jobber, Pool Brain,
PoolDial). Never disparage or price a competitor.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(ROOT, "data", "catalog.json"), encoding="utf-8"))
A = {a["id"]: a for a in CAT["agents"]}
P = {k: f"${v['price_month']:,}" for k, v in A.items()}

GROUPS = [
    ("How it works", [
        ("What is an “AI employee”, in plain English?",
         "Software that answers your leads and customers in your company’s own words — by text, email, web form, Google messages, Thumbtack, Angi, Yelp, and on the phone. Not a chat bubble and not a person. It replies in about eight seconds, asks what a pool quote needs, quotes only from your price list, and follows up. Every conversation lands in your inbox."),
        ("Which of the three do I actually need?",
         f"Most pool companies start with NET ({P['net']}/mo) — it catches the leads you are missing while you are on the route. BALANCE ({P['balance']}/mo) is for the “is my tech coming today?” texts and the service notes. PUMP ({P['pump']}/mo) is for open repair quotes and late invoices. Hire one; add another whenever you like. There is no bundle and no minimum."),
        ("I already use Skimmer / Jobber / Pool Brain. Does this replace it?",
         "No, and it should not. Those run your route and your billing. NET, BALANCE and PUMP work from what they hold — your schedule, your prices, your invoice day — and put replies, notes and reminders in front of your customers. A sheet or an export is enough to start; you do not change software."),
        ("I already have an AI phone bot (PoolDial or similar). Why would I add NET?",
         "Keep it if it works for you. A phone bot answers the phone. NET answers every channel the phone bot does not — web form, Google messages, Thumbtack, Angi, Yelp, text and email — and then does the part a phone bot never does: follows up on day 1, 3 and 7 until the lead books or says stop. If a lead only ever called you, you would not need NET. Most leads today do not call first."),
        ("What happens when a customer asks something it does not know?",
         "It says so, and it does not guess. A price that is not on your list is blocked before it sends; a question outside your rules gets “the owner will confirm” and a flag to you. BALANCE never diagnoses equipment or gives chemical dosing over text — it books a tech visit."),
        ("Will it tell people it is a person?",
         "Never. If anyone asks, it says it is the company’s automated assistant and that you will follow up personally. That is a rule in every script."),
    ]),
    ("What it costs", [
        ("What are the prices, exactly?",
         f"NET is {P['net']} a month. BALANCE is {P['balance']} a month. PUMP is {P['pump']} a month. Each is flat, month to month, with setup included. No per-lead, per-message or per-minute charge, and no bundle — you pay for the ones you hire."),
        ("What is not included?",
         "Anything paid to someone else, never marked up: a new phone number if you want one, or the payment processor you already use for invoices. You hear about it before it is incurred."),
        ("How do I pay, and when am I charged?",
         "Card through Stripe — your details go on Stripe’s own checkout page, never on this site. First payment on order, then the same day each month. Prefer an invoice? Say so on the start form."),
        ("Can I cancel?",
         "Any time. No minimum term, no lock-in, no cancellation fee — email jaden@greenaidigital.com or call (480) 798-0753. It stops at the end of the month you have paid for, and you keep every script, transcript and configuration."),
        ("Do you guarantee I will get more pools on the route?",
         "No, and be wary of anyone who does. How many leads become customers depends on your prices, your area and the season. What we stand behind is the reply and the follow-up happening every time, the way you approved."),
        ("Is there a setup fee or a contract?",
         "No setup fee. No contract beyond month to month. The build — your price list, your route sheet, your house rules, your voice — is included, and you approve every script before it goes live."),
    ]),
    ("Getting it running", [
        ("What do you need from me?",
         "Your weekly and bi-weekly prices by pool size, your service area, your green-pool and start-up policy, your first-visit windows, and how you like to be introduced. For BALANCE, your route schedule and house rules; for PUMP, your repair prices, invoice day and payment link. Most of it is already on a sheet or in your head."),
        ("How long until it is live?",
         "Built and trained for your company before it goes live, and you approve every script first — usually inside two weeks from the day you answer the questions. If we end up waiting on you, go-live moves with you."),
        ("Do I keep my phone number?",
         "Yes. Your number stays yours. NET can answer it, or text back a call you missed — nothing is ported anywhere."),
        ("Can I change what it says after it is live?",
         "Yes, as often as you like, the same day, at no charge. A new price, a new service area, a new way of saying something — send it and it is in."),
        ("What about the busy season?",
         "That is when it matters. February through April is when the forms pile up; the follow-up cadence and the reply time do not change with volume."),
    ]),
    ("Risk, control and who you are dealing with", [
        ("Who am I actually dealing with?",
         "Jaden Green, doing business as GreenAI Solutions, in Gilbert, Arizona. You have his number — (480) 798-0753 — and his email, jaden@greenaidigital.com. There is no account manager between you and the person who built it."),
        ("Can it send something my customer did not agree to?",
         "No. BALANCE and PUMP only message people who are already your customers, about their own service and their own account, and one “stop” ends every message to that person. NET follows up a lead three times, then stops."),
        ("Can PUMP threaten a late payer or send them to collections?",
         "Never. It reminds at 7, 14 and 21 days in the tone you approve — firm, never rude — and it never mentions collections agencies or credit, never changes a price, and never contacts anyone but the account holder. At 30+ days it tells you, and you decide."),
        ("Who owns the scripts and the transcripts?",
         "You do. Every script, every transcript, every configuration file. If you leave, they leave with you."),
        ("Is any of this a real customer’s data on the site?",
         "No. The demo company on this site, Saguaro Pool Care, is fictional, and the engine proof run on the homepage used example leads against a demo company. Your customers’ data is never used as marketing."),
    ]),
]


def esc(s):
    return html.escape(s, quote=False)


def jsonld():
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for _, qs in GROUPS for q, a in qs
        ],
    }
    return ('\n  <script type="application/ld+json">\n' + json.dumps(data, indent=2, ensure_ascii=False) + '\n  </script>\n  ')


def jump():
    return "".join(
        f'\n        <a href="#g{i}">{esc(g)} <b style="opacity:.55">{len(qs)}</b></a>'
        for i, (g, qs) in enumerate(GROUPS)) + "\n      "


def body():
    out = []
    for i, (g, qs) in enumerate(GROUPS):
        items = "".join(
            f'\n        <details class="faq-q">\n          <summary>{esc(q)}</summary>\n          <div class="faq-a"><p>{esc(a)}</p></div>\n        </details>'
            for q, a in qs)
        out.append(f'\n      <div class="faq-group" id="g{i}">\n        <div class="faq-group__head">\n          <h2>{esc(g)}</h2><span>{len(qs):02d} QUESTIONS</span>\n        </div>{items}\n      </div>')
    return "".join(out) + "\n"


def main():
    p = os.path.join(ROOT, "faq.html")
    s = open(p, encoding="utf-8").read()
    for tag, fn in (("JSONLD", jsonld), ("JUMP", jump), ("BODY", body)):
        pat = re.compile(rf"<!--FAQ:{tag}-->.*?<!--/FAQ:{tag}-->", re.S)
        assert pat.search(s), f"marker FAQ:{tag} missing"
        s = pat.sub(lambda m: f"<!--FAQ:{tag}-->" + fn() + f"<!--/FAQ:{tag}-->", s, count=1)
    open(p, "w", encoding="utf-8").write(s)
    n = sum(len(qs) for _, qs in GROUPS)
    print(f"faq.html: {n} questions in {len(GROUPS)} groups")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""gen_new_services.py — writes service-ai-seo.html and service-crm-dashboards.html.
Added 2026-09-19 in place of the "Built for one trade" pool links. No prices on purpose:
pricing is Jaden's call, so both are 'quoted' until he sets a number. No ranking or traffic promises."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_platform_agents import I, NAV, head, tail, esc, ROOT
from robots import robot

CSS = """
    /* new service pages (ns-) */
    .ns-hero-grid { display: grid; grid-template-columns: minmax(0, 1fr) 210px; gap: 2rem; align-items: end; max-width: 1040px; margin: 2.8rem auto 0; text-align: left; }
    .ns-panel { border: 1px solid var(--line-2); border-radius: 22px; background: rgba(0,0,0,.45); overflow: hidden; box-shadow: var(--shadow-2); }
    .ns-panel__bar { display: flex; justify-content: space-between; gap: 1rem; padding: .8rem 1.2rem; border-bottom: 1px solid var(--line); font-family: var(--mono); font-size: .68rem; letter-spacing: .16em; text-transform: uppercase; color: var(--ink-3); }
    .ns-panel__bar b { color: var(--green); font-weight: 500; }
    .ns-log { list-style: none; margin: 0; padding: .4rem 1.2rem 1rem; }
    .ns-log li { display: grid; grid-template-columns: 1.4rem minmax(0, 1fr) auto; gap: .8rem; align-items: baseline; padding: .7rem 0; border-bottom: 1px solid rgba(232,196,106,.1); font-size: .93rem; color: var(--ink); }
    .ns-log li:last-child { border-bottom: 0; }
    .ns-log li::before { content: ""; width: .5rem; height: .5rem; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px var(--green); transform: translateY(-.05rem); }
    .ns-log small { display: block; margin-top: .15rem; font-size: .8rem; color: var(--ink-3); }
    .ns-log em { font-style: normal; font-family: var(--mono); font-size: .64rem; letter-spacing: .14em; text-transform: uppercase; color: var(--green); white-space: nowrap; }
    .ns-tiles { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1px; background: var(--line); }
    .ns-tiles div { padding: 1.1rem 1.2rem 1.2rem; background: #050B08; }
    .ns-tiles span { display: block; font-family: var(--mono); font-size: .62rem; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-3); }
    .ns-tiles b { display: block; margin: .45rem 0 .2rem; font-family: var(--font-display); font-weight: 600; font-size: 1.7rem; letter-spacing: -.02em; color: var(--ink); }
    .ns-tiles small { font-size: .76rem; color: var(--green); }
    .ns-bars { display: flex; align-items: flex-end; gap: .55rem; height: 120px; padding: 1.2rem 1.2rem 0; }
    .ns-bars i { flex: 1; border-radius: 6px 6px 0 0; background: linear-gradient(180deg, var(--green), rgba(232,196,106,.15)); }
    .ns-note { margin: 0; padding: .7rem 1.2rem 1rem; font-size: .76rem; color: var(--ink-3); }
    .ns-bot { filter: drop-shadow(0 0 40px rgba(232,196,106,.18)); }
    .ns-not { max-width: 860px; margin: 0 auto; padding: 0; list-style: none; border-top: 1px solid var(--line); }
    .ns-not li { display: grid; grid-template-columns: 14rem minmax(0, 1fr); gap: 2rem; padding: 1.4rem 0; border-bottom: 1px solid var(--line); }
    body.tk .ns-not b { font-family: var(--font-display); font-weight: 600; font-size: 1.1rem; color: var(--ink); }
    body.tk .ns-not p { margin: 0; font-size: .98rem; line-height: 1.6; color: var(--ink-2); }
    @media (max-width: 860px) { .ns-hero-grid { grid-template-columns: 1fr; } .ns-bot { display: none; } .ns-tiles { grid-template-columns: 1fr 1fr; } .ns-not li { grid-template-columns: 1fr; gap: .4rem; } }
"""

def cards(items):
    return "".join(f'<article class="sn-card"><div class="sn-card__ico">{I[ic]}</div><h3>{t}</h3><p>{p}</p></article>' for ic, t, p in items)

def steps(items):
    return "".join(f'<li><i>{n}</i><div><b>{t}</b><p>{p}</p></div></li>' for n, t, p in items)

def faq(items):
    return "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in items)

def page(fname, title, desc, og, eyebrow, h1, sub, want, visual, bot, s1_h2, s1_lede, s1_cards, state, s2_h2, s2_steps, nots, faqs, close_h2, close_p):
    P = head(title, desc, fname, CSS + """
    .ab-path { list-style: none; margin: 0 auto; padding: 0; max-width: 860px; }
    .ab-path li { display: grid; grid-template-columns: 9rem minmax(0, 1fr); gap: 2rem; padding: 1.7rem 0; border-top: 1px solid var(--line); }
    .ab-path li:last-child { border-bottom: 1px solid var(--line); }
    .ab-path i { font-style: normal; font-family: var(--mono); font-size: .74rem; letter-spacing: .16em; text-transform: uppercase; color: var(--green); padding-top: .4rem; }
    body.tk .ab-path b { display: block; margin-bottom: .45rem; font-family: var(--font-display); font-weight: 600; font-size: 1.35rem; color: var(--ink); }
    body.tk .ab-path p { margin: 0; font-size: 1rem; line-height: 1.65; color: var(--ink-2); }
    @media (max-width: 640px) { .ab-path li { grid-template-columns: 1fr; gap: .4rem; } }
""", og_title=og) + f'''
<body class="tk light-top">
  <a href="#main" class="skip-link">Skip to content</a>
  <nav class="nav transparent" id="main-nav" aria-label="Main navigation">
{NAV}
  </nav>
  <main id="main">

    <div class="sn-wrap"><header class="sn-panel sn-hero" aria-labelledby="hero-heading" style="padding-bottom:0">
      <div class="sn-hero__inner">
        <p class="tk-eyebrow">{eyebrow}</p>
        <h1 class="tk-h1" id="hero-heading">{h1}</h1>
        <p class="sn-hero__sub">{sub}</p>
        <div class="sn-hero__price"><b>Quoted</b><span>after one conversation · price in writing · month to month</span></div>
        <div class="sn-hero__cta">
          <a href="contact.html?want={want}" class="tk-btn tk-btn--inverse tk-btn--arrow">Ask for a quote</a>
          <a href="tel:4807980753" class="tk-btn tk-btn--ghost">Call (480) 798-0753</a>
        </div>
      </div>
      <div class="ns-hero-grid"><div class="ns-panel" style="margin-bottom:2.5rem">{visual}</div><div class="ns-bot">{bot}</div></div>
    </header></div>

    <section class="sn-sec" aria-labelledby="h-does">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-does">{s1_h2}</h2><p class="tk-lede">{s1_lede}</p></div>
        <div class="sn-cards sn-cards--3">{cards(s1_cards)}</div>
      </div>
    </section>

    <div class="sn-state">{"".join(f"<p>{p}</p>" for p in state)}</div>

    <section class="sn-sec" aria-labelledby="h-how">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-how">{s2_h2}</h2></div>
        <ol class="ab-path">{steps(s2_steps)}</ol>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-not" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-not">What you will <em>not get.</em></h2></div>
        <ul class="ns-not">{"".join(f"<li><b>{t}</b><p>{p}</p></li>" for t, p in nots)}</ul>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-faq" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-faq">Asked before <em>starting</em></h2></div>
        <div class="sn-faq">{faq(faqs)}</div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-cta" style="padding-top:0;padding-bottom:2rem">
      <div class="sn-inner" style="text-align:center">
        <div class="sn-head"><h2 class="tk-h2" id="h-cta">{close_h2}</h2><p class="tk-lede">{close_p}</p></div>
        <div class="sn-hero__cta"><a href="contact.html?want={want}" class="tk-btn tk-btn--solid tk-btn--arrow">Ask for a quote</a><a href="services.html" class="tk-btn tk-btn--line">See every service</a></div>
      </div>
    </section>
  </main>
  <div class="sn-sticky"><a href="contact.html?want={want}" class="tk-btn tk-btn--solid tk-btn--arrow">Ask for a quote</a></div>''' + tail()
    open(os.path.join(ROOT, fname), "w").write(P)
    print("wrote", fname, len(P))

# ------------------------------------------------------------------ AI SEO
seo_visual = '''<div class="ns-panel__bar"><span>This week · example work log</span><b>SEO agent</b></div>
<ul class="ns-log">
  <li><span>Rewrote 14 page titles and descriptions<small>each one names the service and the city</small></span><em>waiting for you</em></li>
  <li><span>Fixed 9 broken links and 3 redirect chains<small>found in the weekly crawl</small></span><em>shipped</em></li>
  <li><span>Added business and FAQ markup to 6 pages<small>so Google and AI assistants can read the facts</small></span><em>shipped</em></li>
  <li><span>Drafted "Pool pump repair in Gilbert"<small>from the questions your customers actually ask</small></span><em>waiting for you</em></li>
  <li><span>Answered 4 new Google reviews<small>in your wording, nothing posted without approval</small></span><em>waiting for you</em></li>
</ul>'''

page("service-ai-seo.html",
     "AI SEO — one AI agent does your SEO end to end | GreenAI Solutions",
     "One AI agent does the SEO work on your site end to end: the audit, the fixes, the pages, the Google Business Profile and the monthly report. No new tools to learn, no new hire. You approve what goes live. Quoted after one conversation.",
     "The AI that does your SEO. You approve it.",
     "<b>AI SEO</b> · done for you",
     "The AI that <em>does your SEO.</em>",
     "One AI agent does the work end to end: finds what is wrong, fixes it on your site, writes the pages you are missing and reports what changed. No new tools to learn and nobody new to hire. Nothing goes live until you have read it.",
     "seo", seo_visual, robot("inbox", label="The SEO agent", pose="point"),
     "What it does, <em>every week.</em>",
     "Most SEO tools hand you a list of problems. This one works the list.",
     [("search", "Audits the whole site", "Crawls every page each week for the things that quietly cost you: broken links, slow pages, missing titles, thin pages, pages Google cannot reach."),
      ("pen", "Fixes what it finds", "Titles, descriptions, headings, image text, internal links, redirects and markup. The changes are made on your site, not emailed to you as homework."),
      ("sheet", "Writes the pages you are missing", "Service pages, city pages and answers to the questions your customers type. Drafted from your real prices, area and wording. You read every one first."),
      ("star", "Keeps your Google Business Profile alive", "Hours, services, photos, posts and review replies. For a local company this is often where the call actually starts."),
      ("message", "Gets you into AI answers", "People now ask ChatGPT and Google's AI who to hire. It makes your facts easy for those systems to read and quote: who you are, what you do, where, for how much."),
      ("receipt", "Reports in plain English", "Once a month: what changed, what it did, and what Google Search Console says happened. The numbers are Google's, not ours.")],
     ["Most small companies do not have an SEO problem. They have a nobody-is-doing-it problem.",
      "The audit gets bought, the PDF gets read once, and the forty fixes in it never get made, because everyone who could make them is on a job.",
      "So this is not another report. It is <span class=\"who\">ONE AGENT</span> that does the forty fixes, then the next forty, and shows you each one before it ships."],
     "How it <em>starts.</em>",
     [("Step 1", "One conversation", "What you sell, where, and who you want calling. About twenty minutes. If SEO is not where your money is leaking, you hear that instead."),
      ("Step 2", "A first audit, free to read", "You get the full list of what is wrong and what it would do about it, in plain English, before you pay for anything."),
      ("Step 3", "A price in writing", "Based on the size of the site and how much there is to fix. Month to month, no contract."),
      ("Step 4", "It gets to work", "Access to your site, Search Console and Business Profile. Fixes ship weekly. Anything customer-facing waits for your approval."),
      ("Step 5", "A monthly report", "What changed and what Google's own numbers show. If it is not earning its keep, you cancel at the end of the month and keep every page it wrote.")],
     [("No ranking guarantee", "Nobody controls Google, and anyone who promises page one is guessing or lying. What is promised is the work: every week, visible, approved by you."),
      ("No bought links", "No link farms, no private blog networks, no spun articles. Those work until the day they get a site penalised."),
      ("No pages you have not read", "It never publishes a page, a post or a review reply over your objection. It never invents a price, a service or a review."),
      ("No lock-in", "The pages, the fixes and the accounts are yours. If you leave, everything stays where it is.")],
     [("Do I need to learn a new tool?", "No. It works inside what you already have: your website, Google Search Console and your Google Business Profile. You get an email when something needs your approval and a report once a month."),
      ("How long until it works?", "The fixes are visible the first week, because you can see them on the site. What Google does with them is on Google's schedule, and it is usually measured in months, not days. The monthly report shows you Google's own numbers either way."),
      ("My site was built by someone else. Is that a problem?", "Usually not. WordPress, Squarespace, Wix, Shopify, Webflow and hand-coded sites are all workable. If the site is the problem, you will be told, with the reason."),
      ("Is the writing going to sound like a robot?", "It is drafted from your own prices, service area and the way you talk, and you read it before it goes up. If it does not sound like you, it gets rewritten, same day."),
      ("What does it cost?", "It depends on the size of the site and how much there is to fix, so it is quoted after one conversation and the free first audit. The price is in writing before anything starts, month to month.")],
     "Find out what is <em>actually wrong first.</em>",
     "The first audit costs nothing to read. If the list is short, you will be told to keep your money.")

# ------------------------------------------------------------------ CRM + dashboards
crm_visual = '''<div class="ns-panel__bar"><span>Monday, 7:00 AM · example dashboard</span><b>One screen</b></div>
<div class="ns-tiles">
  <div><span>New leads</span><b>23</b><small>this week</small></div>
  <div><span>Answered in</span><b>0:52</b><small>median</small></div>
  <div><span>Quotes out</span><b>$18,400</b><small>11 open</small></div>
  <div><span>Owed to you</span><b>$4,120</b><small>2 late</small></div>
</div>
<div class="ns-bars" aria-hidden="true"><i style="height:38%"></i><i style="height:52%"></i><i style="height:44%"></i><i style="height:67%"></i><i style="height:58%"></i><i style="height:81%"></i><i style="height:72%"></i><i style="height:94%"></i></div>
<p class="ns-note">Example numbers, not a client's. Yours come from your own CRM and books.</p>'''

page("service-crm-dashboards.html",
     "CRM and business dashboard optimization | GreenAI Solutions",
     "Your CRM cleaned up and made to work: duplicates merged, stages that match how you sell, follow-ups that send themselves, and one dashboard with the numbers you actually run the company on. Quoted after one conversation.",
     "A CRM you trust, and one screen that runs the company.",
     "<b>CRM &amp; dashboards</b> · optimization",
     "A CRM you trust. <em>One screen that runs the company.</em>",
     "Most small companies pay for a CRM and run the business from memory. We clean up the one you already have, make it do the follow-up on its own, and put the numbers that matter on one screen you can read in a minute.",
     "crm", crm_visual, robot("books", label="BOOKS", pose="think"),
     "What gets <em>fixed.</em>",
     "In the CRM you already pay for. Nothing is migrated unless you ask for it.",
     [("user", "The mess gets cleaned", "Duplicate contacts merged, dead leads archived, missing phone numbers and emails flagged, and every contact tagged by where it came from."),
      ("repeat", "The pipeline matches how you sell", "Stages renamed to the steps you actually take, with a rule for when a deal moves. No more forty deals sitting in &quot;New&quot; since March."),
      ("send", "Follow-up sends itself", "Day one, three and seven after a quote. A reminder before an appointment. A nudge on an invoice. In your wording, stopped the moment they reply."),
      ("plug", "The tools talk to each other", "Website form to CRM, CRM to calendar, job closed to invoice. The copy-and-paste between apps is where leads get lost."),
      ("sheet", "One dashboard, the numbers that matter", "New leads, how fast they were answered, quotes out, close rate, revenue, money owed. One screen, updated on its own, readable on your phone."),
      ("sun", "A Monday summary", "The same numbers as a short message every Monday morning, with the three things that need you this week.")],
     ["Ask most owners how many leads came in last month and what happened to them, and the honest answer is a guess.",
      "The data exists. It is spread across a CRM nobody trusts, an inbox, a calendar and the accounting software.",
      "This puts it in <span class=\"who\">ONE PLACE</span> and keeps it clean, so the number on the screen is one you would bet on."],
     "How it <em>runs.</em>",
     [("Step 1", "One conversation", "What you use today, what you wish you knew every Monday, and where leads fall out. About twenty minutes."),
      ("Step 2", "A read-only look", "We look at the CRM as it is and write down what is broken, what is unused and what is costing you, in plain English."),
      ("Step 3", "A price in writing", "A fixed price for the clean-up and the dashboard, and an optional monthly price to keep it tuned. Nothing is signed until you have read it."),
      ("Step 4", "Built in the open", "You see the new stages, the automations and the dashboard on your real data before anything is switched on."),
      ("Step 5", "Handed over, and still answered", "A short walkthrough for you and your team, a one-page guide, and same-day changes while you settle in.")],
     [("No forced migration", "If your CRM can do the job, it stays. You will only hear &quot;switch&quot; when there is a reason, and you will hear the reason."),
      ("No dashboard of forty charts", "If a number does not change a decision you make, it is not on the screen."),
      ("No messages you have not read", "Every automated text and email is written with you and approved by you before it is switched on."),
      ("No lock-in", "It is your CRM, your account and your data. Everything built lives in your own tools and keeps working if you leave.")],
     [("Which CRMs do you work with?", "HubSpot, Jobber, Housecall Pro, ServiceTitan, GoHighLevel, Salesforce, Zoho, Pipedrive, monday.com and most others with an open connection. If yours is a spreadsheet, that works too, and it may be time for something better."),
      ("Where does the dashboard live?", "Wherever you will actually look at it. Inside your CRM when it can do the job, otherwise a simple private page you open on your phone. The numbers update on their own."),
      ("Will my team have to change how they work?", "A little, and on purpose: fewer fields, clearer stages, less typing. The walkthrough takes under an hour."),
      ("Is my customer data safe?", "The work is done inside your own accounts with the access you grant, and the access is removed when you say so. Your customer list is never exported for any other use."),
      ("What does it cost?", "It depends on the CRM, how many contacts are in it and how many tools need connecting, so it is quoted after one conversation and a read-only look. Fixed price in writing before anything starts.")],
     "Know your numbers <em>by Monday.</em>",
     "Start with one conversation and a read-only look. You keep the write-up whether or not you go ahead.")

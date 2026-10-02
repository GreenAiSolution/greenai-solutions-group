#!/usr/bin/env python3
"""gen_new_services.py — writes service-property-signals.html and service-reviews.html.
2026-09-27 reset: the site sells four services to Phoenix home service companies (AI ads,
AI employee, Property Signals, Reviews and repeat work). SEO, CRM and win-back pages are now
redirects (tools/gen_redirects.py). No prices on purpose: pricing is the owner's call, so
both pages are 'quoted' until he sets a number. No damage, ranking or job-count promises.
2026-10-02: two more pages, service-ai-search.html and service-ai-video.html. These two already
carry a price on pricing.html ($297 and $497 a month), so page() takes price= and shows it; the
contact form SKUs (alc-search, alc-video) already exist in contact.html. No ranking or views promises."""
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

def page(fname, title, desc, og, eyebrow, h1, sub, want, visual, bot, s1_h2, s1_lede, s1_cards, state, s2_h2, s2_steps, nots, faqs, close_h2, close_p, price=None, extra_css=""):
    # price=None: "Quoted" hero and "Ask for a quote" buttons (the owner has not set a number).
    # price="$297": the number in the hero and "Start for $297/mo" buttons, pointing at the same contact SKU.
    if price:
        price_html = f'<div class="sn-hero__price"><b>{price}</b><span>a month · month to month · no setup fee</span></div>'
        cta = f"Start for {price}/mo"
    else:
        price_html = '<div class="sn-hero__price"><b>Quoted</b><span>after one conversation · price in writing · month to month</span></div>'
        cta = "Ask for a quote"
    P = head(title, desc, fname, CSS + extra_css + """
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
        {price_html}
        <div class="sn-hero__cta">
          <a href="contact.html?want={want}" class="tk-btn tk-btn--inverse tk-btn--arrow">{cta}</a>
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
        <div class="sn-hero__cta"><a href="contact.html?want={want}" class="tk-btn tk-btn--solid tk-btn--arrow">{cta}</a><a href="services.html" class="tk-btn tk-btn--line">See every service</a></div>
      </div>
    </section>
  </main>
  <div class="sn-sticky"><a href="contact.html?want={want}" class="tk-btn tk-btn--solid tk-btn--arrow">{cta}</a></div>''' + tail()
    open(os.path.join(ROOT, fname), "w").write(P)
    print("wrote", fname, len(P))

# ------------------------------------------------------------------ Property Signals (2026-09-27)
sig_visual = """<div class="ns-panel__bar"><span>Example list · the morning after a monsoon storm</span><b>Signals</b></div>
<ul class="ns-log">
  <li><span>Storm path mapped from public storm reports<small>hail size and wind, by area</small></span><em>mapped</em></li>
  <li><span>Homes likely in the path, matched to county records<small>year built and last sale, from the county</small></span><em>matched</em></li>
  <li><span>Oldest homes first<small>the ones most likely to need you</small></span><em>sorted</em></li>
  <li><span>Addresses you already served, marked<small>so your past customers hear from you first</small></span><em>flagged</em></li>
  <li><span>An example, not a real list<small>yours is built for your service area</small></span><em></em></li>
</ul>"""

page("service-property-signals.html",
     "Property Signals — the Phoenix homes that need you next | GreenAI Solutions",
     "For roofing, HVAC, plumbing and pool companies: after a hail or monsoon storm, a list of the homes likely in its path, and every month, the homes whose systems are due by age. Built from public storm reports and county records. Quoted after a sample for your area.",
     "The homes that need you next, on a list.",
     "<b>Property Signals</b> · for Phoenix home service companies",
     "The homes that need you <em>next.</em>",
     "After a hail or monsoon storm, a list of the homes likely in its path, oldest first. Every month, the homes whose AC, roof, water heater or pool equipment is due by age. Built from public storm reports and county property records, and delivered to your inbox ready for your mailers and your door-knockers.",
     "signals", sig_visual, robot("signals", label="Property Signals", pose="point"),
     "What you <em>get.</em>",
     "Two kinds of list, both built from public records, both for your service area only.",
     [("alert", "Storm lists", "After a hail or high-wind storm, the homes likely in its path, built as soon as the storm reports are published. Oldest homes at the top."),
      ("clock", "Due-by-age lists", "Every month, the homes old enough that the AC, roof, water heater or pool equipment is near replacement, from build year and, where the city publishes them, permit records."),
      ("user", "Your past customers first", "Send your customer list and those addresses are marked, so the people who already know you hear from you before anyone else knocks."),
      ("sheet", "Ready for mail and doors", "A clean spreadsheet: the address, the owner as the county records it, and why the home is on the list. It drops straight into a mailer service or a canvassing app."),
      ("star", "Lined up with your ads", "The same neighborhoods can be targeted by your AI ads, so the mailer, the door hanger and the Facebook ad say the same thing the same week."),
      ("receipt", "Counted", "Lists sent and which addresses turned into jobs, matched against your own invoices.")],
     ["After a storm, every roofer in the valley starts knocking.",
      "The ones who win are not always the ones with the best crews. They are the ones who knew which streets to go to first.",
      "This hands you <span class=\"who\">THE STREETS</span> the morning after, with the oldest homes on them at the top."],
     "How it <em>starts.</em>",
     [("Step 1", "One conversation", "Your trade, your service area, and whether you work storms, replacements or both. About twenty minutes."),
      ("Step 2", "A sample for your area", "A real list for a recent storm or this month's due-by-age homes in your zip codes, so you can judge it before you pay anything."),
      ("Step 3", "A price in writing", "Month to month, no contract."),
      ("Step 4", "Lists arrive on their own", "Storm lists after each qualifying storm, due-by-age lists every month, straight to your inbox."),
      ("Step 5", "A monthly count", "Lists sent and the jobs they turned into. If it is not earning its keep, cancel at the end of the month.")],
     [("Not a damage report", "A storm list shows homes likely in the storm's path, from public reports. It does not say any roof is damaged. Only an inspection can."),
      ("Not for cold calls or texts", "The lists are for mail, door hangers, door-knocking and ads. Calling or texting people who never gave you their number breaks do-not-call rules, and every list says so."),
      ("No bought or scraped data", "Public storm reports and county and city records only. Nothing bought from a data broker, nothing taken from anyone's accounts."),
      ("No promise of jobs", "How many turn into work depends on your offer and your crew. You see the real count, good or bad.")],
     [("Where does the data come from?", "Storm paths from the National Weather Service's public storm reports. Home details from county property records and, where a city publishes them, building permits. All of it is public record."),
      ("How fast does a storm list arrive?", "It is built as soon as the storm reports are published, which is usually within hours of the storm passing. Most lists land the next morning."),
      ("Which areas do you cover?", "Maricopa County first, because its property records are open and detailed. Other Arizona counties on request, checked before you pay."),
      ("Can I call or text the homes on the list?", "Not cold. Use the list for mailers, door hangers, door-knocking and ads. Your own past customers are different: if they gave you their number, you can reach them the usual way."),
      ("What does it cost?", "Quoted after one conversation and a sample list for your area. In writing, month to month.")],
     "Which streets would you knock <em>tomorrow?</em>",
     "Start with a sample list for your service area. If it would not have sent your crew anywhere new, you will know before you pay.")

# ------------------------------------------------------------------ Reviews and repeat work (2026-09-27, was reviews + win-back)
rev_visual = """<div class="ns-panel__bar"><span>This month · example work log</span><b>Reviews &amp; repeat work</b></div>
<ul class="ns-log">
  <li><span>Asked 38 customers for a review<small>every finished job, the same message, two days after</small></span><em>sent</em></li>
  <li><span>Drafted replies to 7 new Google reviews<small>six happy, one not. All seven get an answer.</small></span><em>waiting for you</em></li>
  <li><span>Reminded 42 customers their AC tune-up is due<small>a year since the last visit</small></span><em>sent</em></li>
  <li><span>Wrote to 60 customers not seen in over a year<small>small batches, in your voice</small></span><em>sent</em></li>
  <li><span>Example numbers, not a client's<small>yours come from your own job records</small></span><em></em></li>
</ul>"""

page("service-reviews.html",
     "Reviews and repeat work — every customer asked, every one brought back | GreenAI Solutions",
     "For home service companies: every finished job gets a review request, every Google review gets a reply in your wording, every customer hears from you when their tune-up or replacement is due, and the ones you have not seen in a year get asked back. Quoted after one conversation.",
     "Every customer asked. Every one brought back.",
     "<b>Reviews &amp; repeat work</b> · for home service companies",
     "Every customer asked. <em>Every one brought back.</em>",
     "After every job, a short review request, one reminder, and a reply drafted for every review. Then the part most companies forget: a note when the tune-up, service or replacement is due, and a hello to the customers you have not seen in a year. In your voice, with every reply coming straight to you.",
     "reviews", rev_visual, robot("reviews", label="Reviews and repeat work", pose="wave"),
     "What it does, <em>after every job.</em>",
     "It plugs into the tool where your jobs already close: Jobber, Housecall Pro, ServiceTitan, QuickBooks or a simple list.",
     [("send", "Asks for the review at the right moment", "A short text or email a day or two after the job closes, in your wording, with one tap to your Google review page. One reminder, then it stops."),
      ("message", "Answers every review", "Good and bad. A thank-you that sounds like you, and a calm answer to the unhappy one. You approve before anything posts."),
      ("user", "Asks everyone the same way", "No sorting happy from unhappy before the ask. Google and the FTC both forbid that. Every message also carries a private way to reach you, offered to everyone."),
      ("clock", "Remembers when they are due", "AC tune-ups before summer, furnace checks before winter, pool openings in spring, water heaters at ten years. A short note at the right time, so the work comes back to you."),
      ("repeat", "Brings back the ones who drifted", "Customers you have not seen in a year get a short series of notes in your voice, in small batches, from your own records. Nothing bought."),
      ("receipt", "Counts it for you", "Once a month: reviews asked for and received, your average, reminders sent, and the jobs they booked, matched to your own invoices.")],
     ["When someone needs AC fixed tonight, they look at two things: the stars and the number next to them.",
      "And the cheapest job you will ever book is from a customer who already knows you and simply forgot to call.",
      "Both come down to the same thing: <span class=\"who\">SOMEBODY ASKED</span>, after every job and when it was due, every time."],
     "How it <em>starts.</em>",
     [("Step 1", "One conversation", "Where your jobs close today, what your customers need on a schedule, and how they like to hear from you. About twenty minutes."),
      ("Step 2", "A read-only look at your records", "How many past customers are really in there, and how many are due for something, before you pay anything."),
      ("Step 3", "You approve every message", "We draft the review ask, the reminders and the notes. You change any word you do not like."),
      ("Step 4", "Connected and tested", "Hooked to the tool where jobs close, tested on your own phone first."),
      ("Step 5", "A monthly count", "If it is not earning its keep, cancel at the end of the month.")],
     [("No fake reviews", "Never bought, never written by us, never from staff or family. That is illegal and it gets profiles removed."),
      ("No review gating or gifts for stars", "Every customer gets the same ask, and nobody is offered anything for a review. Google forbids both."),
      ("No texts without permission", "Texts go only to customers who gave you their number for updates. Everyone else gets an email, and anyone can say stop."),
      ("No bought lists", "Only people who were actually your customers. Never a purchased or scraped list.")],
     [("Will this work with how I close jobs now?", "If the job is marked done somewhere, in Jobber, Housecall Pro, ServiceTitan, QuickBooks or a spreadsheet, that is the trigger. If it lives in your head, we set up a one-tap way to mark it."),
      ("What about a bad review?", "It gets a calm, short reply drafted for you within the day, and you get told so you can call the customer. Only Google can remove a review, and only when it breaks Google's rules."),
      ("My records are a mess. Is that a problem?", "That is normal and it is half the job. Invoices, a job tool, an old spreadsheet and a phone full of contacts can be merged into one clean list."),
      ("How many more reviews and jobs will I get?", "It depends on how many jobs you finish and how your customers feel, so nobody honest can give you a number up front. What is promised is that every customer gets asked, and you see the real count."),
      ("What does it cost?", "Quoted after one conversation and a read-only look at your records. In writing, month to month.")],
     "How many jobs did you finish <em>last year?</em>",
     "Every one of them is a review you could have and a customer who will need you again. Start with one conversation.")

# ------------------------------------------------------------------ AI search visibility (2026-10-02, $297/mo, SKU alc-search)
search_visual = """<div class="ns-panel__bar"><span>This month · what the AIs said about you</span><b>AI search</b></div>
<ul class="ns-log">
  <li><span>Asked ChatGPT, Google AI and Perplexity 40 questions a Gilbert homeowner would ask<small>"AC repair near me", "best pool service in Chandler", by trade and by city</small></span><em>checked</em></li>
  <li><span>Named in 14 of the 40 answers, up from 3 at the baseline<small>which questions, which assistant, and who else they named</small></span><em>counted</em></li>
  <li><span>Fixed the facts the assistants had wrong<small>hours, service area, and a phone number from 2019 still on two directories</small></span><em>fixed</em></li>
  <li><span>Added the two pages they kept quoting from a competitor<small>a service-area page and a what-it-costs FAQ, in your words</small></span><em>published</em></li>
  <li><span>Example numbers, not a client's<small>yours come from your own monthly check</small></span><em></em></li>
</ul>"""

page("service-ai-search.html",
     "AI search visibility — be the company ChatGPT recommends in Phoenix | GreenAI Solutions",
     "For Phoenix home service companies: when someone asks ChatGPT, Google's AI or Perplexity for an AC, roofing, plumbing or pool company, your business is one of the names it gives. Your Google profile, reviews, listings and site tuned for AI assistants, with a monthly check of what they say about you. $297 a month, month to month.",
     "Be the company the AI recommends.",
     "<b>AI search visibility</b> · for Phoenix home service companies",
     "Be the company the AI <em>recommends.</em>",
     "People now ask ChatGPT and Google's AI “who should fix my AC in Gilbert?” and get three names back. This makes sure one of them is yours: your Google profile, your reviews, your listings and your own site tuned so AI assistants can find you, trust you and name you. Every month, a plain report of what they say about you.",
     "alc-search", search_visual, robot("search", label="AI search visibility", pose="point"),
     "What it <em>does.</em>",
     "AI assistants build their answers from the same public places people already look: your Google Business Profile, your reviews, the directories, and your own website. This keeps all four straight and keeps checking.",
     [("search", "Checks what the AIs say about you", "Every month, the questions your customers actually ask, put to ChatGPT, Google's AI and Perplexity for your trade and your cities. Whether you are named, where, and what they say about you."),
      ("check", "Gets your facts straight everywhere", "Name, hours, service area, phone and services, the same on Google, Apple, Bing, Yelp and the directories the assistants read. One old phone number in one place is enough to lose the mention."),
      ("star", "Puts your reviews to work", "Assistants lean on how many reviews you have, how recent they are and what people say in them. We make sure the reviews you earn are visible, answered, and found under the words customers search."),
      ("sheet", "Gives the AIs pages worth quoting", "Short, plain pages on your own site: what you do, where, roughly what it costs, and the questions people ask before they call. Written so an assistant can lift a clean answer from them."),
      ("plug", "Marks up your site for machines", "Business, service and FAQ structured data added to your pages, so the assistants read your site the way a person does: who you are, what you do, where, and how to reach you."),
      ("receipt", "A monthly report in plain English", "Which questions named you, which named a competitor, what changed since last month and what we did about it. No dashboard to learn.")],
     ["When a homeowner's AC quits at nine at night, more and more of them do not scroll ten blue links. They ask an AI and get three names.",
      "Those three names come from the public record of your business: your profile, your reviews, your listings, your site.",
      "This keeps that record <span class=\"who\">CLEAN, CURRENT AND QUOTABLE</span>, and checks every month whether the assistants noticed."],
     "How it <em>starts.</em>",
     [("Step 1", "A baseline check", "Before you pay anything, twenty of your customers' questions go to the assistants and you see who they name today. Usually it is not you, and now you know where you stand."),
      ("Step 2", "Facts fixed first", "Google Business Profile, Apple, Bing, Yelp and the main directories brought into agreement in the first two weeks."),
      ("Step 3", "Pages and markup", "The service, area and cost pages the assistants keep looking for, written for your approval and added to your site, with structured data behind them."),
      ("Step 4", "Reviews lined up", "If you run reviews and repeat work with us, the two are wired together. If not, the reviews you already have are made visible and answered."),
      ("Step 5", "A monthly check", "Same questions, same assistants, every month. You see the count move, or you cancel at the end of the month.")],
     [("No guaranteed spot", "Nobody controls what ChatGPT or Google's AI says, and anyone who promises you a place in the answer is guessing. What is promised is that every public fact about you is right, your site is quotable, and you see the real count each month."),
      ("No fake reviews or filler pages", "No bought reviews, no doorway pages, no AI-written pages stuffed with city names. The assistants are built to ignore that and Google penalises it."),
      ("No new website required", "This works on the site you have. If it genuinely cannot carry a few new pages, you will be told that plainly, not sold a rebuild."),
      ("Not a traditional SEO campaign", "No link buying, no keyword reports. It overlaps with good SEO because the assistants read the same things Google does, but the goal is to be named in an answer, not ranked on a page.")],
     [("Which AIs do you check?", "ChatGPT, Google's AI Overviews and AI Mode, and Perplexity, because those are the ones Phoenix homeowners actually use. Others can be added if your customers mention them."),
      ("How soon does it show?", "The facts are fixed within two weeks. The assistants refresh at their own pace, so the first real movement usually shows in the second or third monthly check. You get the baseline up front so there is no arguing about where you started."),
      ("Do I need your other services?", "No. It works on its own at $297 a month. It works better alongside reviews and repeat work, because reviews are a large part of what the assistants weigh, and it is included in Full System."),
      ("Will you need access to my site and Google profile?", "Yes, to edit them: a manager seat on your Google Business Profile and editor access to the site. Both stay in your name, nothing is moved, and access can be removed any day."),
      ("What does it cost?", "$297 a month, month to month, no setup fee. In writing before you sign, like everything else here.")],
     "Ask an AI for your trade in your city <em>tonight.</em>",
     "If it does not say your name, that is the whole problem. Start with the baseline check and see who it names instead, before you pay anything.",
     price="$297")

# ------------------------------------------------------------------ AI short-form video (2026-10-02, $497/mo, SKU alc-video)
REELS_CSS = """
    .ns-reels { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .7rem; padding: 1rem 1.2rem 0; }
    .ns-reels div { position: relative; aspect-ratio: 9 / 16; border-radius: 12px; overflow: hidden; background: #050B08; border: 1px solid rgba(232,196,106,.18); }
    .ns-reels video { width: 100%; height: 100%; object-fit: cover; display: block; }
    .ns-reels span { position: absolute; left: .5rem; right: .5rem; bottom: .5rem; padding: .3rem .5rem; border-radius: 6px; background: rgba(0,0,0,.62); font-family: var(--mono); font-size: .58rem; letter-spacing: .14em; text-transform: uppercase; color: var(--green); text-align: center; }
"""
video_visual = """<div class="ns-panel__bar"><span>This month · Reels &amp; TikToks</span><b>12 ready</b></div>
<div class="ns-reels">
  <div><video src="art/ad-vid-reel.mp4" muted autoplay loop playsinline preload="metadata" poster="art/ad-angle-question.webp" aria-label="An example vertical video cut from job footage"></video><span>Your footage</span></div>
  <div><video src="art/ad-vid-founder.mp4" muted autoplay loop playsinline preload="metadata" poster="art/ad-angle-founder.webp" aria-label="An example vertical video with AI b-roll"></video><span>AI b-roll</span></div>
  <div><video src="art/ad-vid-problem.mp4" muted autoplay loop playsinline preload="metadata" poster="art/ad-angle-problem.webp" aria-label="An example captioned vertical video"></video><span>Captioned</span></div>
</div>
<ul class="ns-log">
  <li><span>Cut 12 videos from the 31 clips your crew sent<small>a condenser swap, two pool clean-ups, a roof walk, one hello from the owner</small></span><em>delivered</em></li>
  <li><span>Captioned every one<small>most people watch with the sound off</small></span><em>captioned</em></li>
  <li><span>Sent to you for a yes before anything posts<small>an example month, not a client's</small></span><em>waiting for you</em></li>
</ul>"""

page("service-ai-video.html",
     "AI short-form video — 12 Reels and TikToks a month from your footage | GreenAI Solutions",
     "For Phoenix home service companies: send clips from the job and get back twelve finished, captioned vertical videos a month for Instagram Reels, TikTok, YouTube Shorts and Facebook. Your real footage plus AI b-roll, voice and captions, approved by you before anything posts. $497 a month, month to month.",
     "Twelve videos a month. You never edit one.",
     "<b>AI short-form video</b> · for Phoenix home service companies",
     "Twelve videos a month. <em>You never edit one.</em>",
     "Your crew already films the before-and-after on their phones. Send us the clips and twelve finished vertical videos come back every month: cut, captioned, with AI b-roll and a voice where it helps, ready for Reels, TikTok, Shorts and Facebook. Posted for you, or handed over as files. The same videos feed your AI ads.",
     "alc-video", video_visual, robot("video", label="AI short-form video", pose="wave"),
     "What you get, <em>every month.</em>",
     "Twelve finished vertical videos, built from footage you already have, in a style that looks like your company and not like an ad agency.",
     [("folder", "You send the raw clips", "Phone footage from the job, a walkthrough, a five-second hello from the owner. A shared album, a text thread, whatever your crew will actually use. No tripod, no script."),
      ("pen", "We cut, caption and finish", "Trimmed to the moment that matters, captions burned in, music or an AI voice where it helps, your logo and number at the end. Twelve a month, in your colours."),
      ("note", "AI b-roll where you have no footage", "How a heat pump fails, a map of your service area, a before-and-after slider. Generated to fill the gaps in a real job's footage, never passed off as your work."),
      ("check", "You approve before anything posts", "Every batch comes to you first. Change a line, cut a clip, veto one. Nothing goes out in your name without your yes."),
      ("calendar", "Posted on a schedule, or handed to you", "Scheduled to Instagram, TikTok, Facebook and YouTube Shorts for you, three a week, or delivered as files if you would rather post yourself."),
      ("repeat", "The same clips feed your ads", "The videos that do well are already cut for vertical, so they drop straight into your Meta and Google campaigns if you run AI ads with us.")],
     ["Every home service owner in the valley knows they should be posting video. Almost none of them do, because the job is the job and nobody has an evening left to edit.",
      "Meanwhile the one roofer in your zip code who posts a sixty-second roof walk every Tuesday is the one people feel they already know when they call.",
      "This makes you that company, with footage you <span class=\"who\">ALREADY HAVE</span> and about ten minutes of your time a week."],
     "How it <em>starts.</em>",
     [("Step 1", "One conversation", "Your trade, your customers, what your crew is willing to film, and where you post today. About twenty minutes."),
      ("Step 2", "Two sample videos", "Send a handful of clips and get two finished videos back before you pay anything, so you judge the style on your own footage, not a showreel."),
      ("Step 3", "Your look, written down", "Colours, logo, the words you use and the ones you never would, and whether the owner is on camera or not."),
      ("Step 4", "Clips in, videos out", "Twelve a month in weekly batches, each one to you for approval. Posted for you or handed over as files."),
      ("Step 5", "A monthly count", "Views, saves, profile visits, and the calls that mention a video. If it is not earning its keep, cancel at the end of the month.")],
     [("No promise of going viral", "Some videos take off and most do not, and nobody honest can tell you which in advance. What is promised is twelve finished videos a month and a real count of what they did."),
      ("No stock footage passed off as yours", "AI b-roll is used for diagrams, maps and illustrations, and it is shown as what it is. Your jobs are your jobs, and nobody else's footage is presented as yours."),
      ("No filming crew", "We do not come to the job site. The footage comes from your phones. If you want a filmed day, it can be arranged separately and quoted."),
      ("No posting without your yes", "Every video is approved by you before it is scheduled, and you can pull one back any time before it posts.")],
     [("What if my crew will not film anything?", "Most crews will take a ten-second clip if it is one tap into a shared album and nobody asks them to talk. We set that up with them. If after a month there is still no footage, we say so and you can stop."),
      ("Do I have to be on camera?", "No. Plenty of accounts work on hands, equipment and before-and-afters with captions and a voice. A five-second hello now and then helps, but it is your call."),
      ("Which platforms?", "Instagram Reels, TikTok, Facebook and YouTube Shorts. The same vertical file works on all four, so one video goes everywhere at once."),
      ("Who owns the videos?", "You do. Every file is yours to keep and reuse, including after you cancel."),
      ("What does it cost?", "$497 a month for twelve videos, month to month, no setup fee. Included in Full System. Posting and scheduling is part of the price; ad spend, if you run any of them as ads, is separate.")],
     "How many jobs did your crew photograph <em>this week?</em>",
     "Every one of them was a video. Send a handful of clips and get two finished ones back before you decide.",
     price="$497", extra_css=REELS_CSS)

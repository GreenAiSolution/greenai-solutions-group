#!/usr/bin/env python3
"""gen_new_services.py — writes service-property-signals.html and service-reviews.html.
2026-09-27 reset: the site sells four services to Phoenix home service companies (AI ads,
AI employee, Property Signals, Reviews and repeat work). SEO, CRM and win-back pages are now
redirects (tools/gen_redirects.py). No prices on purpose: pricing is the owner's call, so
both pages are 'quoted' until he sets a number. No damage, ranking or job-count promises.
2026-10-02: the site sells TWO services, AI agents ($397/mo) and review automation ($149/mo).
This file writes both pages. page() takes price= so a priced service shows its number instead
of "Quoted". Property Signals is retired (tools/gen_redirects.py) and its page() call is gone."""
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

def page(fname, title, desc, og, eyebrow, h1, sub, want, visual, bot, s1_h2, s1_lede, s1_cards, state, s2_h2, s2_steps, nots, faqs, close_h2, close_p, price=None, sku=None):
    # price=None: "Quoted" hero and "Ask for a quote" buttons. price="$397": the number in the
    # hero and "Start for $397/mo" buttons. sku= puts a data-sku on the buttons so checkout.js
    # can route a known SKU to its Stripe link; unknown SKUs fall through to the contact form.
    if price:
        price_html = f'<div class="sn-hero__price"><b>{price}</b><span>a month · month to month · no setup fee</span></div>'
        cta = f"Start for {price}/mo"
    else:
        price_html = '<div class="sn-hero__price"><b>Quoted</b><span>after one conversation · price in writing · month to month</span></div>'
        cta = "Ask for a quote"
    buy = f' buy" data-sku="{sku}' if sku else ""
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
        {price_html}
        <div class="sn-hero__cta">
          <a href="contact.html?want={want}" class="tk-btn tk-btn--inverse tk-btn--arrow{buy}">{cta}</a>
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
        <div class="sn-hero__cta"><a href="contact.html?want={want}" class="tk-btn tk-btn--solid tk-btn--arrow{buy}">{cta}</a><a href="services.html" class="tk-btn tk-btn--line">See both services</a></div>
      </div>
    </section>
  </main>
  <div class="sn-sticky"><a href="contact.html?want={want}" class="tk-btn tk-btn--solid tk-btn--arrow{buy}">{cta}</a></div>''' + tail()
    open(os.path.join(ROOT, fname), "w").write(P)
    print("wrote", fname, len(P))

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
     "For home service companies: every finished job gets a review request, every Google review gets a reply in your wording, every customer hears from you when their tune-up or replacement is due, and the ones you have not seen in a year get asked back. $149 a month, month to month.",
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
      ("What does it cost?", "$149 a month, month to month, no setup fee. In writing before you sign, like everything else here.")],
     "How many jobs did you finish <em>last year?</em>",
     "Every one of them is a review you could have and a customer who will need you again. Start with one conversation.",
     price="$149", sku="alc-reviews")

# ------------------------------------------------------------------ AI agents (2026-10-02, $397/mo, SKU agent-inbox)
agent_visual = """<div class="ns-panel__bar"><span>Last night · example work log</span><b>AI agent</b></div>
<ul class="ns-log">
  <li><span>Replied to a website form at 9:47 PM<small>"Do you do bathroom remodels?" Answered, two times offered, booked Thursday at 10.</small></span><em>booked</em></li>
  <li><span>Answered a Facebook message about pricing<small>from your price list, nothing invented</small></span><em>replied</em></li>
  <li><span>Day-three follow-up on Tuesday's quote<small>short, in your wording, one question</small></span><em>sent</em></li>
  <li><span>Drafted a reply to an unusual request<small>a commercial job outside your area, waiting for your yes</small></span><em>waiting for you</em></li>
  <li><span>Example numbers, not a client's<small>yours come from your own inbox</small></span><em></em></li>
</ul>"""

page("service-ai-agents.html",
     "AI agents — every lead answered in under a minute, booked and followed up | GreenAI Solutions",
     "For contractors, salons, restaurants and local service businesses: an AI agent that replies to every new lead in under a minute from your website form, Facebook, Google, Gmail or text, answers the common questions in your words and prices, books the appointment onto your calendar or Jobber, and follows up on day one, three and seven. $397 a month, month to month.",
     "Every lead answered in under a minute.",
     "<b>AI agents</b> · for contractors, salons, restaurants and local service businesses",
     "Every lead answered <em>in under a minute.</em>",
     "Most leads go to whoever answers first. Your AI agent replies to every new lead in under a minute, from your website form, Facebook, Google, Gmail or text. It answers the common questions in your words and prices, books the appointment straight onto your calendar, Jobber, Housecall Pro or ServiceTitan, and follows up on day one, three and seven until the lead answers. It never claims to be a person, and anything unusual comes to you as a draft.",
     "agents", agent_visual, robot("inbox", label="AI agents", pose="point"),
     "What it <em>does.</em>",
     "One agent, trained on your prices, hours, service area and wording. It works where your leads already arrive and books where you already book.",
     [("message", "Replies in under a minute", "Website form, Facebook and Instagram messages, Google Business messages, Gmail and text. Every new lead gets a friendly, specific answer, day or night."),
      ("note", "Answers from your price list", "The common questions, in your words and your prices. A price that is not on your list cannot go out. When it does not know, it says so and hands it to you."),
      ("calendar", "Books the appointment", "Offers two real times and books straight onto your calendar, Jobber, Housecall Pro or ServiceTitan, with a confirmation to the customer and a note to you."),
      ("repeat", "Follows up until they answer", "Day one, day three, day seven. Short, polite, in your voice. Then it stops. Most booked jobs come from the second or third message."),
      ("hand", "Hands you the unusual ones", "A commercial job, an upset customer, a question outside your rules: it drafts a reply and waits for your yes instead of guessing."),
      ("receipt", "Shows you the count", "A Monday note: leads in, replied in how long, booked, still being followed up, handed to you. Matched against your own calendar.")],
     ["A lead that waits until Thursday for a reply has usually booked someone else by Tuesday.",
      "Not because you did not care. Because you were on a roof, in a chair, or in a dinner rush when it came in.",
      "The agent answers <span class=\"who\">IN UNDER A MINUTE</span>, every time, and the booking lands on your calendar while you work."],
     "How it <em>starts.</em>",
     [("Step 1", "One conversation", "Where your leads come in today, where you book, your prices, hours and service area. About twenty minutes."),
      ("Step 2", "A price in writing", "$397 a month, month to month. What it will do, what it will not, and the number, before anything is signed."),
      ("Step 3", "You read every word", "The replies it can send are written for your approval. Change any wording you do not like, as often as you want, at no charge."),
      ("Step 4", "Connected and tested", "Hooked to your form, your pages, your inbox and your calendar, then tested against your own questions before it answers a real customer."),
      ("Step 5", "Live, and still answered", "Changes are same-day. Cancel at the end of any month and keep every script and transcript.")],
     [("Not a person, and never pretends to be", "If a customer asks, it says it is the company's automated assistant and who will follow up. That is a rule in every script."),
      ("Built for written leads", "Website forms, Facebook, Google, Gmail and text. If you need the phone line itself answered, say so in the first conversation and you get a straight answer about what is possible."),
      ("No invented prices or promises", "A number that is not on your list is blocked before it sends. Anything outside your rules comes to you as a draft, not to the customer."),
      ("No promise of more jobs", "How many leads become customers depends on your prices, your area and the season. What is promised is the reply and the follow-up happening every time, the way you approved.")],
     [("Where does it work?", "Your website form, Facebook and Instagram messages, Google Business Profile messages, Gmail and text. Jobber, Housecall Pro, ServiceTitan or a plain Google Calendar for booking. If you use something else, ask."),
      ("Do my customers know it is an AI?", "If they ask, it tells the truth. It does not pretend to be a person and does not use a fake name."),
      ("What happens when it does not know the answer?", "It says so, takes the details, and the conversation lands in your inbox with a drafted reply waiting for your yes. It never guesses a price."),
      ("I already use Jobber or Housecall Pro. Does this replace it?", "No, it feeds it. The client, the request and the booking land in the tool you already run."),
      ("How long until it is live?", "Usually inside two weeks from the day you answer the setup questions, and you approve every reply before it goes live."),
      ("What does it cost?", "$397 a month, month to month, no setup fee, no per-lead charge. In writing before you sign.")],
     "How many leads came in <em>last week?</em>",
     "Every one of them wanted an answer in the first few minutes. Start with one conversation.",
     price="$397", sku="agent-inbox")

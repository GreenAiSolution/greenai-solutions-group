#!/usr/bin/env python3
"""gen_about.py — about.html in the showroom layout with the six robots around the direct line."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_platform_agents import I, NAV, AGENTS, FULL, TM, head, tail, esc, ROOT, STARS, ICON_OF
from robots import robot, bust, peek

CSS = """
    .ab-control { display: grid; grid-template-columns: 1fr auto 1fr; gap: 1rem; align-items: center; max-width: 1040px; margin: 2.6rem auto 0; }
    .ab-control__side { display: flex; justify-content: space-around; align-items: flex-end; }
    .ab-control__side a { display: block; width: var(--w, 140px); transform: translateY(var(--dy, 0)); }
    .ab-line { position: relative; width: 340px; padding: 1.6rem 1.5rem; border-radius: 24px; background: #fff; color: var(--ink); text-align: center; box-shadow: 0 40px 90px -30px rgba(0,0,0,.65); }
    .ab-line small { display: block; font-size: .74rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--ink-3); }
    .ab-line a.num { display: block; margin: .4rem 0 .2rem; font-family: var(--font-display); font-weight: 600; font-size: 2rem; letter-spacing: -.02em; color: var(--ink); text-decoration: none; }
    .ab-line a.num:hover { color: var(--green); }
    .ab-line p { margin: .3rem 0 0; font-size: .86rem; line-height: 1.5; color: var(--ink-2); }
    .ab-line .mail { display: inline-block; margin-top: .6rem; font-size: .9rem; font-weight: 600; color: var(--green); text-decoration: none; }
    .ab-line .live { position: absolute; top: -.8rem; left: 50%; transform: translateX(-50%); padding: .3rem .7rem; border-radius: 999px; background: var(--green); color: #fff; font-size: .7rem; font-weight: 700; letter-spacing: .06em; white-space: nowrap; }
    .ab-line .live::before { content: ""; display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #fff; margin-right: .4rem; animation: hp-pulse 1.6s infinite; }
    @keyframes hp-pulse { 50% { opacity: .35; } }
    @media (max-width: 900px) { .ab-control { grid-template-columns: 1fr; } .ab-control__side a { --dy: 0px; width: 30%; } .ab-line { width: min(100%, 340px); margin: 0 auto; } }
    .ab-rule { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.25rem; max-width: 1000px; margin: 0 auto; }
    .ab-rule > div { position: relative; padding: 1.8rem 1.6rem 1.6rem; border-radius: 24px; background: #fff; border: 1px solid var(--line); box-shadow: var(--shadow); }
    .ab-rule i { display: block; font-style: normal; font-family: var(--font-display); font-weight: 600; font-size: 2.2rem; color: var(--ember); line-height: 1; margin-bottom: .6rem; }
    .ab-rule b { display: block; font-family: var(--font-display); font-weight: 600; font-size: 1.25rem; color: var(--ink); margin-bottom: .4rem; }
    .ab-rule p { margin: 0; color: var(--ink-2); font-size: .95rem; line-height: 1.55; }
    .ab-rule .rb-peek { position: absolute; top: -40px; right: 8px; width: 88px; }
    @media (max-width: 800px) { .ab-rule { grid-template-columns: 1fr; } }
    .hp-talk { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: center; max-width: 960px; margin: 0 auto; }
    .hp-talk__phone { display: block; margin: 1.2rem 0 .3rem; font-family: var(--font-display); font-weight: 600; font-size: clamp(1.8rem, 3.4vw, 2.6rem); letter-spacing: -.02em; color: var(--ink); text-decoration: none; }
    .hp-talk__mail { display: inline-block; font-size: 1.05rem; color: var(--green); text-decoration: none; border-bottom: 1.5px solid currentColor; }
    @media (max-width: 760px) { .hp-talk { grid-template-columns: 1fr; } }
"""

left = list(zip(AGENTS[:3], ["stand","think","wave"], [120,120,120], [0,-14,-28]))
right = list(zip(AGENTS[3:], ["point","think","stand"], [120,120,120], [-28,-14,0]))
def side(items):
    return "".join(f'<a href="{a["id"]}.html" class="rb-float" style="--w:{w}px;--dy:{dy}px;animation-delay:{i*.4}s" title="{a["name"]}">{robot(a["id"], I[ICON_OF[a["id"]]], label=a["name"], pose=p)}</a>' for i,(a,p,w,dy) in enumerate(items))

steps = "".join(f'<li><b>{t}</b><p>{p}</p></li>' for t,p in [
    ("The system does the work","RING answers, INBOX replies, BOOKS sends the invoice. Built from your price list, your hours, your house rules and the way you say things."),
    ("A second system grades it","Every dollar figure is read by a checker before it sends. A price that is not on your list is blocked, not sent. Whoever does the work does not grade it."),
    ("A person approves it","You read every script before a customer hears one. Anything unusual, a complaint, a refund, a legal question, is drafted and waits for you."),
    ("Built to say \"I'm not sure\"","Rather than invent an answer. That is the difference between AI you put in front of customers and AI you apologise for."),
    ("You stay the owner","You just stop being the bottleneck. Month to month, so this company has to earn next month."),
])
phone = '''
<div class="sn-phone__view is-on"><p class="sn-phone__title">Does</p><p class="sn-phone__sub">RING, 9:47 PM</p><ul class="sn-lines"><li class="them">My pump is grinding and it's Sunday.</li><li class="us" data-who="RING · 0:08">Switch it off tonight. Can I get the address? I can book tomorrow at 8.</li></ul></div>
<div class="sn-phone__view"><p class="sn-phone__title">Grades</p><p class="sn-phone__sub">the checker, same second</p><div class="sn-file"><i>$</i><span>"first visit is $285"<small>on your price list</small></span><em>PASS</em></div><div class="sn-file"><i>$</i><span>"I can do it for $3,200"<small>not on your list</small></span><em style="color:#c8102e">BLOCKED</em></div><div class="sn-file"><i>HR</i><span>"tomorrow at 8"<small>inside your hours</small></span><em>PASS</em></div></div>
<div class="sn-phone__view"><p class="sn-phone__title">Approves</p><p class="sn-phone__sub">you, before it goes live</p><ul class="sn-lines"><li class="us" data-who="RING · draft">I can hold tomorrow at 8.</li><li class="them">Say "book", not "hold".</li><li class="us" data-who="RING · v2">I can book tomorrow at 8.</li><li class="them">Approved.</li></ul></div>
<div class="sn-phone__view"><p class="sn-phone__title">"I'm not sure"</p><p class="sn-phone__sub">what it says when it does not know</p><ul class="sn-lines"><li class="them">Can you match the other guy's price?</li><li class="us" data-who="RING">I'm not sure, and I won't guess. Jaden will call you back today with an answer.</li></ul><div class="sn-file"><i>YOU</i><span>Texted to you<small>caller, number, the question</small></span><em>NOW</em></div></div>
<div class="sn-phone__view"><p class="sn-phone__title">You stay the owner</p><p class="sn-phone__sub">Monday, 7:00 AM</p><div class="sn-file"><i>RNG</i><span>11 calls answered<small>2 booked, 1 handed to you</small></span><em>RING</em></div><div class="sn-file"><i>BKS</i><span>$2,760 came in<small>2 late, 0 disputes</small></span><em>BOOKS</em></div><div class="sn-file"><i>480</i><span>Anything wrong?<small>(480) 798-0753 rings Jaden</small></span><em>CALL</em></div></div>'''

roster = "".join(f'<li><a href="{a["id"]}.html">{a["name"]}</a><span>{esc(a["inside"])}</span><b>${a["price"]:,}/mo</b></li>' for a in AGENTS)

PAGE = head("About Jaden Green and GreenAI Solutions — Gilbert, AZ",
            "One person builds the six AI employees, the websites, the ads and the custom systems, and answers the phone. Jaden Green, Gilbert, Arizona. B.S. Real Estate and Business, University of Washington. Seven years building systems for small companies.",
            "about.html", CSS, og_title="About Jaden Green, the one person you can call") + f'''
<body class="tk light-top">
  <a href="#main" class="skip-link">Skip to content</a>
  <nav class="nav transparent" id="main-nav" aria-label="Main navigation">
{NAV}
  </nav>
  <main id="main">

    <div class="sn-wrap"><header class="sn-panel sn-hero" aria-labelledby="h1">{STARS}
      <div class="sn-hero__inner">
        <p class="tk-eyebrow"><b>About</b> · Gilbert, Arizona</p>
        <h1 class="tk-h1" id="h1">Six employees. One builder. <em>One number.</em></h1>
        <p class="sn-hero__sub">Jaden Green builds every AI employee, website, ad and custom system GreenAI sells, and answers the phone himself. No photo, on purpose. The number is the trust signal.</p>
        <div class="sn-hero__cta">
          <a href="tel:4807980753" class="tk-btn tk-btn--inverse tk-btn--arrow">Call (480) 798-0753</a>
          <a href="mailto:jaden@greenaidigital.com" class="tk-btn tk-btn--ghost">jaden@greenaidigital.com</a>
        </div>
      </div>
      <div class="ab-control" aria-label="The six robots around the direct line">
        <div class="ab-control__side">{side(left)}</div>
        <div class="ab-line"><span class="live">Direct line</span><small>Rings the builder</small><a class="num" href="tel:4807980753">(480) 798-0753</a><p>Not a call centre, not a rep. You get the person who builds the system, every time.</p><a class="mail" href="mailto:jaden@greenaidigital.com">jaden@greenaidigital.com</a><p style="margin-top:.6rem"><b>Jaden Green</b> · Gilbert, AZ · works with companies anywhere</p></div>
        <div class="ab-control__side">{side(right)}</div>
      </div>
    </header></div>

    <section class="sn-sec" aria-labelledby="h-who">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-who">Who you would be <em>buying from.</em></h2></div>
        <div class="sn-cards">
          <article class="sn-card"><div class="sn-card__ico">{I['book']}</div><h3>Read a P&amp;L before automating anything</h3><p>B.S. in Real Estate and Business, University of Washington. What is sold here is not technology. It is a job that gets done faster, cheaper, or at an hour when nobody is awake.</p></article>
          <article class="sn-card"><div class="sn-card__ico">{I['clock']}</div><h3>Seven years building systems</h3><p>Systems that let a small company run like a much bigger one. GreenAI is where all of that work now lives.</p></article>
          <article class="sn-card"><div class="sn-card__ico">{I['user']}</div><h3>One person, start to finish</h3><p>Jaden scopes it, builds it, answers the phone and makes the change you asked for. No account manager, no ticket queue, no hand-off.</p></article>
          <article class="sn-card"><div class="sn-card__ico">{I['shield']}</div><h3>Transparent by default</h3><p>The <a href="staff.html">price</a>, the <a href="agreement.html">service agreement</a> and a <a href="catch.html">real run of the system</a> are public on this site. Read all three before we ever speak.</p></article>
        </div>
      </div>
    </section>

    <div class="sn-state" aria-label="The one rule">
      <p>I build the systems myself, and I do not break one rule: whoever does the work does not grade it.</p>
      <p>The system does the job. A second system checks it. A person approves it before it acts.</p>
      <p><span class="who">{bust("ring", cls="who__bust")}RING</span> is built to say "I'm not sure" rather than invent an answer. That is the difference between AI you put in front of customers and AI you apologise for.</p>
    </div>

    <section class="sn-sec" aria-labelledby="h-rule">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-rule">Does. Grades. <em>Approves.</em></h2><p class="tk-lede">How every GreenAI system is built, on the phone as you would see it. Tap a step, or scroll.</p></div>
        <div class="sn-steps">
          <div class="sn-steps__device"><div class="sn-phone" aria-hidden="true"><div class="sn-phone__screen"><div class="sn-phone__notch"></div>{phone}</div></div></div>
          <ol class="sn-steps__list">{steps}</ol>
        </div>
      </div>
    </section>

    <div class="sn-wrap"><section class="sn-panel sn-grad" aria-labelledby="h-for">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-for">Built for the small company that <em>never had an office.</em></h2><p class="tk-lede">The one-truck owner who answers from the driver's seat, and the ten-truck company where the owner still does the invoices on Sunday.</p></div>
        <div class="sn-bubbles">
          <div><div class="sn-grad__bot rb-float">{robot("huddle", I["sun"], label="HUDDLE", pose="point")}</div><div class="sn-bubble"><b>A front office, without hiring one</b>A two-truck company gets the same coverage as the outfit with a call centre. AI employees built for your area and your prices, answering while you are on a job.</div></div>
          <div class="sn-phone"><div class="sn-phone__screen"><div class="sn-phone__notch"></div><div class="sn-phone__view is-on"><p class="sn-phone__title">Sunday, 9:47 PM</p><p class="sn-phone__sub">the evening you get back</p><div class="sn-file"><i>RNG</i><span>Call answered, booked Mon 8:00<small>you were at dinner</small></span><em>RING</em></div><div class="sn-file"><i>INB</i><span>Quote request replied to<small>0:41 after it landed</small></span><em>INBOX</em></div><div class="sn-file"><i>BKS</i><span>Invoice #1051 sent<small>the day the job closed</small></span><em>BOOKS</em></div><div class="sn-file"><i>YOU</i><span>Nothing needs you tonight<small>Monday report at 7</small></span><em>REST</em></div></div></div></div>
          <div><div class="sn-bubble"><b>Your evenings back</b>Quoting at the kitchen table, answering "is my tech coming?" from the truck, chasing invoices on Sunday. The work that fills your evenings without paying for them. We hand that back.</div><div class="sn-bubble"><b>We have to earn next month</b>You approve every script before it goes live, changes are same-day and unlimited, and you have the builder's number. Month to month.</div><div class="sn-grad__bot rb-float" style="animation-delay:.6s">{robot("inbox", I["inbox"], label="INBOX", pose="fly")}</div></div>
        </div>
      </div>
    </section></div>

    <section class="sn-easy" aria-labelledby="h-shift">
      <div class="sn-inner">
        <h2 id="h-shift">The internet changed how they find you. AI changes the <span class="sn-toggle" aria-hidden="true"></span> <em>minutes after.</em></h2>
        <div class="sn-benefits">
          <div>{I['clock']}<p><b>Who answers, and how fast.</b> A customer with a problem sends more than one form. The company that replies first usually gets the job. That is the whole race, and it is winnable with software.</p></div>
          <div>{I['alert']}<p><b>Where the money leaks.</b> Not in marketing spend. In the form that sat unread while you were on a job in Chandler, and the call that rang out at 9:47 PM.</p></div>
          <div>{I['repeat']}<p><b>Whether anyone follows up.</b> Day one, three and seven, in your words, until they answer or say stop.</p></div>
          <div>{I['star']}<p><b>Close the gap</b> and the marketing you already pay for starts working harder. That gap is the whole reason this company exists.</p></div>
        </div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-rows" style="padding-top:2rem">
      <div class="sn-inner">
        <div class="sn-price">
          <p class="tk-eyebrow" style="margin-bottom:1.4rem"><b>Everything on the menu</b> · every price is the whole price</p>
          <div class="tk-big" id="h-rows">From $297<small>a month for an AI employee · all six ${FULL:,}</small></div>
          <p class="sn-price__terms">Websites from $500, a month of finished ads from $697, custom systems quoted after one conversation. Month to month, no contract, and you keep every script, transcript, page and file.</p>
          <div class="sn-price__cta"><a href="staff.html" class="tk-btn tk-btn--solid tk-btn--arrow">Meet the six</a><a href="services.html">Compare all four services</a></div>
          <ul class="sn-price__rows">{roster}</ul>
        </div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-talk" style="padding-top:0;padding-bottom:2rem">
      <div class="sn-inner">
        <div class="hp-talk">
          <div><h2 class="tk-h2" id="h-talk">Start with a <em>conversation.</em></h2><p class="tk-lede">Tell me where calls, leads, time or money are getting stuck. If what I build is a fit, you hear what it costs and how long it takes. If it is not, you hear that instead.</p><a class="hp-talk__phone" href="tel:4807980753">(480) 798-0753</a><br/><a class="hp-talk__mail" href="mailto:jaden@greenaidigital.com">jaden@greenaidigital.com</a></div>
          <div class="tk-plate"><p><b>Jaden Green</b>, Gilbert, Arizona. I read every message myself and usually reply the same business day.</p><p>Rather write it down? The contact form goes to the same place.</p><a href="contact.html" class="tk-btn tk-btn--line">Send a message</a></div>
        </div>
        <p class="ag-tm">{esc(TM)}</p>
      </div>
    </section>
  </main>
  <div class="sn-sticky"><a href="tel:4807980753" class="tk-btn tk-btn--solid tk-btn--arrow">Call Jaden, (480) 798-0753</a></div>''' + tail()

open(os.path.join(ROOT, "about.html"), "w").write(PAGE)
print("wrote about.html", len(PAGE))

#!/usr/bin/env python3
"""gen_about.py — about.html in the showroom layout with the six robots around the direct line."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_platform_agents import I, NAV, AGENTS, FULL, TM, head, tail, esc, ROOT, STARS, ICON_OF
from robots import robot, bust, peek

CSS = """
    .ab-control { display: grid; grid-template-columns: 1fr auto 1fr; gap: 1rem; align-items: center; max-width: 1040px; margin: 2.6rem auto 0; }
    .ab-control__side { display: flex; justify-content: space-around; align-items: flex-end; }
    .ab-control__side a { display: block; width: min(var(--w, 140px), 8.2vw); transform: translateY(var(--dy, 0)); }
    .ab-control__side { gap: .5rem; }
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
    .ab-path { list-style: none; margin: 0 auto; padding: 0; max-width: 860px; }
    .ab-path li { display: grid; grid-template-columns: 9rem minmax(0, 1fr); gap: 2rem; padding: 1.7rem 0; border-top: 1px solid var(--line); }
    .ab-path li:last-child { border-bottom: 1px solid var(--line); }
    .ab-path i { font-style: normal; font-family: var(--mono); font-size: .74rem; letter-spacing: .16em; text-transform: uppercase; color: var(--green); padding-top: .4rem; }
    body.tk .ab-path b { display: block; margin-bottom: .45rem; font-family: var(--font-display); font-weight: 600; font-size: 1.35rem; letter-spacing: -.01em; color: var(--ink); }
    body.tk .ab-path p { margin: 0; font-size: 1rem; line-height: 1.65; color: var(--ink-2); }
    @media (max-width: 640px) { .ab-path li { grid-template-columns: 1fr; gap: .4rem; } }
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
<div class="sn-phone__view"><p class="sn-phone__title">"I'm not sure"</p><p class="sn-phone__sub">what it says when it does not know</p><ul class="sn-lines"><li class="them">Can you match the other guy's price?</li><li class="us" data-who="RING">I'm not sure, and I won't guess. We will call you back today with an answer.</li></ul><div class="sn-file"><i>YOU</i><span>Texted to you<small>caller, number, the question</small></span><em>NOW</em></div></div>
<div class="sn-phone__view"><p class="sn-phone__title">You stay the owner</p><p class="sn-phone__sub">Monday, 7:00 AM</p><div class="sn-file"><i>RNG</i><span>11 calls answered<small>2 booked, 1 handed to you</small></span><em>RING</em></div><div class="sn-file"><i>BKS</i><span>$2,760 came in<small>2 late, 0 disputes</small></span><em>BOOKS</em></div><div class="sn-file"><i>480</i><span>Anything wrong?<small>(480) 798-0753 rings us directly</small></span><em>CALL</em></div></div>'''

roster = "".join(f'<li><a href="{a["id"]}.html">{a["name"]}</a><span>{esc(a["inside"])}</span><b>${a["price"]:,}/mo</b></li>' for a in AGENTS)

PAGE = head("About — GreenAI Solutions, Gilbert, AZ",
            "The founder: five years as a scholarship long snapper at the University of Washington, a year working a service route through a Phoenix summer, and seven years building software. He started GreenAI Solutions in 2025.",
            "about.html", CSS, og_title="About the founder of GreenAI Solutions") + f'''
<body class="tk light-top">
  <a href="#main" class="skip-link">Skip to content</a>
  <nav class="nav transparent" id="main-nav" aria-label="Main navigation">
{NAV}
  </nav>
  <main id="main">

    <div class="sn-wrap"><header class="sn-panel sn-hero" aria-labelledby="h1">
      <div class="sn-hero__inner">
        <p class="tk-eyebrow"><b>About</b> · the founder</p>
        <h1 class="tk-h1" id="h1">Five years of college football. <em>Then I built this.</em></h1>
        <p class="sn-hero__sub">I was a long snapper at the University of Washington, I've knocked doors through a Phoenix summer, and I've been building software since I was seventeen. GreenAI Solutions is where all of that ended up.</p>
        <div class="sn-hero__cta">
          <a href="tel:4807980753" class="tk-btn tk-btn--inverse tk-btn--arrow">Call (480) 798-0753</a>
          <a href="mailto:jaden@greenaidigital.com" class="tk-btn tk-btn--ghost">jaden@greenaidigital.com</a>
        </div>
      </div>
      <div class="ab-control" aria-label="The six AI employees around the direct line">
        <div class="ab-control__side">{side(left)}</div>
        <div class="ab-line"><span class="live">Direct line</span><small>Rings the founder</small><a class="num" href="tel:4807980753">(480) 798-0753</a><p>No photo of me on this site, on purpose. You get my number instead.</p><a class="mail" href="mailto:jaden@greenaidigital.com">jaden@greenaidigital.com</a><p style="margin-top:.6rem"><b>GreenAI Solutions</b> · Gilbert, AZ · works with companies anywhere</p></div>
        <div class="ab-control__side">{side(right)}</div>
      </div>
    </header></div>

    <section class="sn-sec" aria-labelledby="h-who">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-who">The short <em>version.</em></h2></div>
        <div class="sn-stats">
          <div class="sn-stat"><span>Washington football</span><b>#89</b><small>long snapper, 2020 to 2025, on a full scholarship</small></div>
          <div class="sn-stat"><span>Building software</span><b>7 yrs</b><small>since I was seventeen, mostly for small companies</small></div>
          <div class="sn-stat"><span>GreenAI Solutions</span><b>2025</b><small>started that February, in the Valley</small></div>
          <div class="sn-stat"><span>Home</span><b>Gilbert</b><small>Arizona, working with companies anywhere</small></div>
        </div>
      </div>
    </section>

    <div class="sn-state" aria-label="Why a long snapper builds this">
      <p>A long snapper has one job. Put the ball in the same place, at the same speed, every time, with someone running at you. Nobody knows your name unless you miss.</p>
      <p>I did that for five years at Washington: a Pac-12 championship, a Sugar Bowl, a national championship game. What it taught me was not football. It was how to be automatic when it matters.</p>
      <p>That is what I build now. <span class="who">{bust("ring", cls="who__bust")}RING</span> answers the phone the same way at 9:47 on a Sunday night as it does on Monday morning. Nobody notices it. That is the point.</p>
    </div>

    <section class="sn-sec" aria-labelledby="h-path">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-path">How I <em>got here.</em></h2></div>
        <ol class="ab-path">
          <li><i>Age 17</i><div><b>Started building</b><p>I started at seventeen and never stopped. Seven years on, it is systems that let a small company run like a much bigger one.</p></div></li>
          <li><i>2020 – 2025</i><div><b>University of Washington</b><p>Five years on a full football scholarship in Seattle. 5 a.m. lifts, film graded every week, performance judged in public. I finished a degree in art with a minor in real estate, which is why the sites look the way they do and why I read the numbers before I automate anything.</p></div></li>
          <li><i>Early 2025</i><div><b>The ramp at Sky Harbor</b><p>Ground crew on aircraft turns. A clock that does not move and a checklist that does not bend. I started GreenAI the same winter.</p></div></li>
          <li><i>2025 – 2026</i><div><b>A service route, and a lot of doors</b><p>A year inside a small Phoenix service company: a weekly route of homes, and door-to-door sales through a full Arizona summer. I saw from the inside what a small company's day looks like, and how much of it is the phone, the follow-up and the invoice.</p></div></li>
          <li><i>Now</i><div><b>GreenAI Solutions</b><p>An AI services workforce for small companies: AI staff inside the apps they already use, websites coded by hand, finished ads, SEO and custom systems. We are a team of 12 now, and my number is still the one on the site.</p></div></li>
        </ol>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-rules" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-rules">Three rules <em>I don't break.</em></h2></div>
        <div class="sn-trio">
          <div>{I['shield']}<h3>Whoever does the work does not grade it</h3><p>The system does the job, a second system checks it, and a person approves it before it acts. A price that is not on your list gets blocked, not sent.</p></div>
          <div>{I['hand']}<h3>"I'm not sure" beats a good guess</h3><p>Everything I build is made to say so and hand it to you, rather than invent an answer in front of your customer.</p></div>
          <div>{I['key']}<h3>You can read it all first</h3><p>The <a class="more" style="display:inline;margin:0" href="staff.html">prices</a>, the <a class="more" style="display:inline;margin:0" href="agreement.html">service agreement</a> and <a class="more" style="display:inline;margin:0" href="testimonials.html">the work</a> are public. Month to month, and everything built is yours if you leave.</p></div>
        </div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-off" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-off">Off the <em>clock.</em></h2></div>
        <div class="sn-cards sn-cards--3">
          <article class="sn-card"><div class="sn-card__ico">{I['star']}</div><h3>Still snapping</h3><p>I coach long snappers, from high school to pro prep, in Phoenix and Seattle and over film. Same idea as the day job: reps until it is automatic.</p></article>
          <article class="sn-card"><div class="sn-card__ico">{I['pen']}</div><h3>The art degree shows</h3><p>I care how things look. Every site here is drawn and coded by hand, with no themes and no page builder.</p><p style="margin-top:.8rem"><a href="testimonials.html" style="color:var(--green);font-weight:600;text-decoration:none">See the work →</a></p></article>
          <article class="sn-card"><div class="sn-card__ico">{I['sun']}</div><h3>Arizona, by choice</h3><p>After five years in Seattle I live and work in the Valley. Most of what I build is for small service companies like the ones down the street.</p></article>
        </div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-talk" style="padding-top:0;padding-bottom:2rem">
      <div class="sn-inner">
        <div class="hp-talk">
          <div><h2 class="tk-h2" id="h-talk">Start with a <em>conversation.</em></h2><p class="tk-lede">Tell me where calls, leads, time or money are getting stuck. If what I build is a fit, you hear what it costs and how long it takes. If it is not, you hear that instead.</p><a class="hp-talk__phone" href="tel:4807980753">(480) 798-0753</a><br/><a class="hp-talk__mail" href="mailto:jaden@greenaidigital.com">jaden@greenaidigital.com</a></div>
          <div class="tk-plate"><p><b>GreenAI Solutions</b>, Gilbert, Arizona. I read every message myself and usually reply the same business day.</p><p>Rather write it down? The contact form goes to the same place.</p><a href="contact.html" class="tk-btn tk-btn--line">Send a message</a></div>
        </div>
        <p class="ag-tm">{esc(TM)}</p>
      </div>
    </section>
  </main>
  <div class="sn-sticky"><a href="tel:4807980753" class="tk-btn tk-btn--solid tk-btn--arrow">Call (480) 798-0753</a></div>''' + tail()

open(os.path.join(ROOT, "about.html"), "w").write(PAGE)
print("wrote about.html", len(PAGE))

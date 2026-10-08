#!/usr/bin/env python3
"""gen_home.py — writes index.html in the showroom layout. Run after gen_platform_agents.py."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_platform_agents import I, NAV, FOOT, AGENTS, FULL, SEPARATE, TM, head, tail, esc, ROOT
from ring_demo import section as ring_demo_section
from robots import seals

JSONLD = '''{
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": "GreenAI Solutions",
    "url": "https://greenaidigital.com/",
    "telephone": "+1-480-798-0753",
    "email": "jaden@greenaidigital.com",
    "address": { "@type": "PostalAddress", "addressLocality": "Gilbert", "addressRegion": "AZ", "postalCode": "85296", "addressCountry": "US" },
    "areaServed": "US",
    "description": "An AI services workforce for Phoenix home service companies: AI ads, an AI employee that answers every call and text, Property Signals lists of the homes that need you next, and reviews and repeat work.",
    "makesOffer": [
      { "@type": "Offer", "name": "AI ads", "url": "https://greenaidigital.com/service-ai-ads.html", "priceCurrency": "USD", "price": "697" },
      { "@type": "Offer", "name": "AI employee", "url": "https://greenaidigital.com/staff.html", "priceCurrency": "USD", "price": "297" },
      { "@type": "Offer", "name": "Property Signals", "url": "https://greenaidigital.com/service-property-signals.html" },
      { "@type": "Offer", "name": "Reviews and repeat work", "url": "https://greenaidigital.com/service-reviews.html" }
    ]
  }'''

CSS = """
    /* homepage-only pieces (hp-) */
    .hp-browser { border: 1px solid var(--line); border-radius: 16px; overflow: hidden; background: #fff; }
    .hp-browser__bar { display: flex; align-items: center; gap: .4rem; padding: .55rem .8rem; background: var(--bg-3); border-bottom: 1px solid var(--line); }
    .hp-browser__bar i { width: 8px; height: 8px; border-radius: 50%; background: var(--line-2); }
    .hp-browser__url { margin-left: .5rem; font-family: var(--mono); font-size: .72rem; color: var(--ink-3); }
    .hp-browser__shots { position: relative; aspect-ratio: 16 / 10; }
    .hp-browser__shots img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: top; opacity: 0; transition: opacity .6s; }
    .hp-browser__shots img.on { opacity: 1; }
    .hp-ads { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem; }
    .hp-ads > div { position: relative; border-radius: 12px; overflow: hidden; background: var(--bg-3); }
    .hp-ads video, .hp-ads img { display: block; width: 100%; height: 100%; object-fit: cover; }
    .hp-ads .tall { grid-row: span 2; aspect-ratio: 9 / 16; }
    .hp-ads > div:not(.tall) { aspect-ratio: 1; }
    .hp-ads span { position: absolute; left: .45rem; bottom: .4rem; padding: .15rem .45rem; border-radius: 999px; background: rgba(15,26,20,.75); color: #fff; font-size: .62rem; font-weight: 700; }
    .hp-schem { display: grid; gap: .45rem; }
    .hp-schem div { display: grid; grid-template-columns: auto 1fr auto; gap: .6rem; align-items: center; padding: .55rem .7rem; border: 1px solid var(--line); border-radius: 12px; background: rgba(255,255,255,.04); border-color: rgba(232,196,106,.28); font-size: .8rem; color: #fff; }
    .hp-schem i { width: 8px; height: 8px; border-radius: 50%; background: var(--green); }
    .hp-schem em { font-style: normal; font-family: var(--mono); font-size: .66rem; color: rgba(255,255,255,.6); }
    .hp-services .sn-card { text-align: left; }
    .hp-services .sn-card__ico { margin-left: 0; }
    .hp-services .sn-card__price { display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; margin-top: 1.2rem; padding-top: 1rem; border-top: 1px solid var(--line); }
    .hp-services .sn-card__price b { font-family: var(--font-display); font-weight: 600; font-size: 1.35rem; letter-spacing: -.02em; color: var(--ink); }
    .hp-services .sn-card__price a { font-size: .9rem; font-weight: 600; color: var(--green); text-decoration: none; white-space: nowrap; }
    .hp-talk { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: center; max-width: 960px; margin: 0 auto; }
    .hp-talk__phone { display: block; margin: 1.2rem 0 .3rem; font-family: var(--font-display); font-weight: 600; font-size: clamp(1.8rem, 3.4vw, 2.6rem); letter-spacing: -.02em; color: var(--ink); text-decoration: none; }
    .hp-talk__phone:hover { color: var(--green); }
    .hp-talk__mail { display: inline-block; font-size: 1.05rem; color: var(--green); text-decoration: none; border-bottom: 1.5px solid currentColor; }
    @media (max-width: 760px) { .hp-talk { grid-template-columns: 1fr; } .hp-services[style] { grid-template-columns: 1fr !important; } }
    /* the hero: one spotlight, the six on one stage, nothing else */
    .home .sn-hero { padding-bottom: 3.6rem; background: radial-gradient(46% 62% at 50% 100%, rgba(232,196,106,.16), transparent 70%), conic-gradient(from 180deg at 50% -12%, transparent 0 157deg, rgba(232,196,106,.13) 172deg, rgba(255,255,255,.10) 180deg, rgba(232,196,106,.13) 188deg, transparent 203deg 360deg), linear-gradient(180deg, #0A1A11 0%, #050C08 100%); }
    .home .sn-more a { padding-right: 8rem; min-height: 11rem; overflow: hidden; }
    .hp-face { position: absolute; right: 1.2rem; top: 1.2rem; width: 5.6rem; height: auto; }
    @media (max-width: 560px) { .home .sn-more a { padding-right: 6rem; } .hp-face { width: 4.2rem; right: .9rem; top: .9rem; } }
"""

SIX_X = [22.0, 31.9, 43.5, 56.5, 68.0, 77.9]
SIX_C = {"ring":"#7DE3A4","dispatch":"#F0CF6B","inbox":"#7CC4F0","thread":"#C9A9F7","huddle":"#F5A38E","books":"#E8C46A"}
six_links = "".join(f'<a href="{a["id"]}.html" style="left:{x}%;--c:{SIX_C[a["id"]]}" aria-label="{a["name"]}"><span>{a["name"]}</span></a>' for a, x in zip(AGENTS, SIX_X))

four = f'''
<article class="sn-card"><div class="sn-card__ico">{I['phone']}</div><h3>Answers the phone in about eight seconds.</h3><p>Nights, weekends, the second caller. Books it and texts you.</p></article>
<article class="sn-card"><div class="sn-card__ico">{I['user']}</div><h3>Writes the job into Jobber, Housecall Pro or ServiceTitan.</h3><p>Client, request, quote and reminder, in your account.</p></article>
<article class="sn-card"><div class="sn-card__ico">{I['inbox']}</div><h3>Replies from your own Gmail in under a minute.</h3><p>Follows up on day one, three and seven. Drafts anything unusual for you.</p></article>
<article class="sn-card"><div class="sn-card__ico">{I['receipt']}</div><h3>Sends the invoice the day the job closes.</h3><p>Reminds politely on seven, fourteen and twenty-one. Never collections.</p></article>'''

phone_views = '''
<div class="sn-phone__view is-on"><p class="sn-phone__title">One conversation</p><p class="sn-phone__sub">Twenty minutes, by phone or email.</p>
<ul class="sn-lines"><li class="them">We miss calls after 5 and the inbox is a mess. Where would you start?</li><li class="us" data-who="GreenAI">Where it costs you most. Usually the phone. Here is what RING does and what it will not do.</li><li class="them">And if it is not a fit?</li><li class="us" data-who="GreenAI">Then I say so, and you have lost twenty minutes.</li></ul></div>
<div class="sn-phone__view"><p class="sn-phone__title">A price in writing</p><p class="sn-phone__sub">Before anything is signed.</p>
<div class="sn-file"><i>RNG</i><span>RING · your phone line<small>$497 a month, month to month</small></span><em>QUOTED</em></div>
<div class="sn-file"><i>WEB</i><span>Five-page website<small>$500 once, about seven business days</small></span><em>QUOTED</em></div>
<div class="sn-file"><i>DOC</i><span>Service agreement v1.2<small>public, read it first</small></span><em>LINK</em></div></div>
<div class="sn-phone__view"><p class="sn-phone__title">Built in the open</p><p class="sn-phone__sub">You see it working on real examples.</p>
<ul class="sn-lines"><li class="us" data-who="RING · draft">Thanks for calling. Can I get the address? I can hold tomorrow at 8.</li><li class="them">Say "book", not "hold".</li><li class="us" data-who="RING · v2">Can I get the address? I can book tomorrow at 8.</li><li class="them">Approved.</li></ul></div>
<div class="sn-phone__view"><p class="sn-phone__title">You read every word</p><p class="sn-phone__sub">Nothing goes live over your objection.</p>
<div class="sn-file"><i>PDF</i><span>price-list.pdf<small>every number it may quote</small></span><em>READ</em></div>
<div class="sn-file"><i>HRS</i><span>Hours &amp; service area<small>Gilbert, Mesa, Chandler, Queen Creek</small></span><em>READ</em></div>
<div class="sn-file"><i>TXT</i><span>Your wording<small>not a template</small></span><em>READ</em></div></div>
<div class="sn-phone__view"><p class="sn-phone__title">Live, and still answered</p><p class="sn-phone__sub">Changes are same-day at no charge.</p>
<div class="sn-file"><i>ON</i><span>RING is live on your line<small>cancel at the end of any month</small></span><em>LIVE</em></div>
<div class="sn-file"><i>480</i><span>(480) 798-0753<small>rings the person who built it</small></span><em>DIRECT</em></div>
<div class="sn-file"><i>MON</i><span>Monday report<small>handled · handed to you</small></span><em>WEEKLY</em></div></div>'''

steps = "".join(f'<li><b>{t}</b><p>{p}</p></li>' for t,p in [
    ("One conversation","What is stuck, what it costs you now, and what done would look like. About twenty minutes, by phone or email. If what I build is not a fit, you hear that instead."),
    ("A price in writing","What gets built, what it will not do, and the number. The service agreement is public before we speak. Nothing is signed until you have read it."),
    ("Built in the open","You see it working on real examples as it comes together. Every script, page and ad goes past you first."),
    ("You read every word","Nothing reaches a customer over your objection. If something still bothers you, it waits. No change fees, no ticket numbers."),
    ("Live, and still answered","Changes are same-day at no charge. The number on this page rings the person who built it. If you leave, you keep everything and nothing stops working."),
])

marquee1 = "".join(f'<div class="sn-mcard">{I[ic]}<b>{a["name"]}: {esc(t)}</b><p>{esc(p)}</p></div>' for a in AGENTS for ic,t,p in a["does"][:2])
marquee2 = "".join(f'<div class="sn-mcard">{I[ic]}<b>{a["name"]}: {esc(t)}</b><p>{esc(p)}</p></div>' for a in AGENTS for ic,t,p in a["does"][2:5])

roster = "".join(f'<a href="{a["id"]}.html"><img class="hp-face" src="art/marks/{a["id"]}-md.svg" alt="" width="240" height="240" loading="lazy" decoding="async" /><b>{a["name"]}</b><span>Works {esc(a["inside"])}. {esc(a["does"][0][1])}.</span><i>${a["price"]:,} a month →</i></a>' for a in AGENTS)

faq = "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in [
    ("What is an AI employee, in plain English?","A program that does one job inside a tool you already use: answers the phone, replies to leads in Gmail, writes jobs into Jobber, answers the team in Slack or Teams, sends the invoices in QuickBooks. It is trained on your prices, hours and wording, and it never invents a number."),
    ("Do my customers know they are talking to an AI?","If they ask, it tells the truth. It does not pretend to be a person and does not use a fake name."),
    ("Is there a setup fee or a per-call charge?","No. The monthly price is the whole price. Websites are priced once, up front. Anything you pay Slack, Google, Jobber or QuickBooks is your own subscription, at their price."),
    ("Can I cancel?","At the end of any month you have paid for. You keep every script, transcript, page and file. Nothing stops working when you leave."),
    ("Do you only work with Arizona businesses?","No. I am in Gilbert, Arizona, and I work with companies anywhere. Everything is built and delivered over the phone, email and your own tools."),
])

PAGE = head("GreenAI Solutions — an AI services workforce for Phoenix home service companies",
            "An AI services workforce for Phoenix HVAC, roofing, plumbing and pool companies. Four services: finished ads every month from $697, an AI employee that answers every call and text from $297 a month, Property Signals lists of the homes that need you next, and reviews and repeat work. Gilbert, Arizona.",
            "", CSS, og_title="GreenAI Solutions — your AI services workforce").replace('href="https://greenaidigital.com/"', 'href="https://greenaidigital.com/"') + f'''
<body class="tk home light-top">
  <a href="#main" class="skip-link">Skip to content</a>
  <nav class="nav transparent" id="main-nav" aria-label="Main navigation">
{NAV}
  </nav>
  <script type="application/ld+json">
  {JSONLD}
  </script>
  <main id="main">

    <div class="sn-wrap"><header class="sn-panel sn-hero" aria-labelledby="hero-heading">
      <div class="sn-hero__inner">
        <p class="tk-eyebrow"><b>GreenAI Solutions</b> · for Phoenix home service companies</p>
        <h1 class="tk-h1" id="hero-heading">Your AI services <em>workforce.</em></h1>
        <p class="sn-hero__sub">Four services for HVAC, roofing, plumbing and pool companies. Ads that bring the calls, an AI employee that answers them, lists of the homes that need you next, and reviews and repeat work from the customers you already have. Priced in writing, month to month, with a real person to call.</p>
        <div class="sn-hero__cta">
          <a href="#h-also" class="tk-btn tk-btn--inverse tk-btn--arrow">See the four services</a>
          <a href="tel:4807980753" class="tk-btn tk-btn--ghost">Call (480) 798-0753</a>
        </div>
      </div>
      {seals(AGENTS, "The six AI employees in the workforce")}
    </header></div>

    <section class="sn-sec" aria-labelledby="h-also">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-also">Four services. <em>Full schedules.</em></h2><p class="tk-lede">Bring the calls, answer every one, know which homes need you next, and keep the customers you already won. Every price is the whole price, in writing before anything is signed.</p></div>
        <div class="sn-cards sn-cards--3 hp-services">
          <article class="sn-card" style="grid-column:1/-1"><div class="sn-card__ico">{I['phone']}</div><h3>An AI employee on every call</h3><p>Answers every call and text at any hour while your crews are working, gets the address and the problem, books the visit and texts you a summary. Works inside your phone line, Jobber, Housecall Pro or ServiceTitan, and Gmail, in your prices and wording.</p>
            <div class="sn-card__price"><b>from $297/mo</b><a href="staff.html">See where it works →</a></div></article>
          <article class="sn-card"><div class="sn-card__ico">{I['star']}</div><h3>AI ads</h3><p>Fresh ads every month for the season you are in: AC before the heat, roofs after the monsoon, pool openings in spring. Seven angles, every size the platforms need.</p>
            <div class="sn-card__vis"><div class="hp-ads" aria-label="Finished ad output"><div class="tall"><video src="art/ad-vid-clock.mp4" muted autoplay loop playsinline preload="metadata" poster="art/ad-angle-clock.webp" aria-label="A fifteen-second vertical ad"></video><span>9:16</span></div><div><img src="art/ad-angle-question.webp" alt="A square ad" width="720" height="720" loading="lazy" decoding="async" /><span>1:1</span></div><div><img src="art/ad-angle-split.webp" alt="A portrait ad" width="720" height="893" loading="lazy" decoding="async" /><span>4:5</span></div></div></div>
            <div class="sn-card__price"><b>from $697/mo</b><a href="service-ai-ads.html">See the ad desk →</a></div></article>
          <article class="sn-card"><div class="sn-card__ico">{I['alert']}</div><h3>Property Signals</h3><p>After a hail or monsoon storm, the homes likely in its path, oldest first. Every month, the homes whose AC, roof, water heater or pool equipment is due by age. From public records, ready for mailers and door-knocking.</p>
            <div class="sn-card__price"><b>Quoted</b><a href="service-property-signals.html">See how Signals works →</a></div></article>
          <article class="sn-card"><div class="sn-card__ico">{I['repeat']}</div><h3>Reviews and repeat work</h3><p>A review request after every job and a reply to every review. Then a note when the tune-up or replacement is due, and a hello to the customers you have not seen in a year.</p>
            <div class="sn-card__price"><b>Quoted</b><a href="service-reviews.html">See how it runs →</a></div></article>
        </div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-roster">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-roster">Six names. <em>Six apps.</em></h2><p class="tk-lede">The staff side of the workforce, one inside each tool you already run. Hire one, or all six for ${FULL:,} a month.</p></div>
        <div class="sn-more sn-more--3">{roster}</div>
        <p style="text-align:center;margin:1.5rem 0 0"><a href="staff.html" class="tk-btn tk-btn--solid tk-btn--arrow">See all six at work</a></p>
      </div>
    </section>

{ring_demo_section()}

    <section class="sn-sec" aria-labelledby="h-film" style="padding-bottom:1rem">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-film">AI video that looks like <em>this.</em></h2><p class="tk-lede">Twenty-five seconds. No sound needed.</p></div>
        <div style="max-width:360px;margin:0 auto;border-radius:28px;overflow:hidden;border:1px solid rgba(232,196,106,.45);box-shadow:0 30px 80px rgba(0,0,0,.55);background:#060706">
          <video muted autoplay loop playsinline preload="metadata" poster="film/homepage-ad-v2-poster.jpg" width="720" height="1280" style="display:block;width:100%;height:auto" aria-label="Twenty-five-second ad: an astronaut in a nebula, swirling gold ink, a neon city at dusk and a crystal cave, captioned 'POV: you make AI videos that look like this, every single time. greenaidigital.com'">
            <source src="film/homepage-ad-v2.mp4" type="video/mp4">
          </video>
        </div>
        <p class="tk-lede" style="text-align:center;margin-top:1.25rem">More like this on Instagram: <a href="https://www.instagram.com/greenaidigitals/" target="_blank" rel="noopener" style="color:#E8C46A">@greenaidigitals</a></p>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-four">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-four">Four things that stop falling through <em>the cracks.</em></h2><p class="tk-lede">The four jobs that cost a small company the most when nobody gets to them.</p></div>
        <div class="sn-cards">{four}</div>
      </div>
    </section>

    <div class="sn-state" aria-label="Why this exists">
      <p>Most small companies do not lose the job to a competitor. They lose it to the phone that rang out at 6:40, the email answered on Thursday, and the invoice that went out three weeks late.</p>
      <p>Not because nobody cared. Because the same three people were already doing everything.</p>
      <p><span class="who">THE WORKFORCE</span> takes those off your plate. It works inside the apps you already use. Nothing new to log into.</p>
    </div>

    <section class="sn-sec" aria-labelledby="h-how">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-how">How a build runs, <em>in five steps.</em></h2><p class="tk-lede">The same five whether it is a phone line, a month of ads or a list of homes. Tap a step, or scroll.</p></div>
        <div class="sn-steps">
          <div class="sn-steps__device"><div class="sn-phone" aria-hidden="true"><div class="sn-phone__screen"><div class="sn-phone__notch"></div>{phone_views}</div></div></div>
          <ol class="sn-steps__list">{steps}</ol>
        </div>
      </div>
    </section>

    <section class="sn-easy" aria-labelledby="h-easy">
      <div class="sn-inner">
        <h2 id="h-easy">Your front office, on <span class="sn-toggle" aria-hidden="true"></span> <em>autopilot.</em></h2>
        <div class="sn-benefits">
          <div>{I['phone']}<p><b>Nothing rings out.</b> Calls, forms, texts and emails are answered in seconds, any hour, in your wording.</p></div>
          <div>{I['lock']}<p><b>Nothing new to log into.</b> Each employee lives inside a tool your company already opens every morning.</p></div>
          <div>{I['hand']}<p><b>Nothing invented.</b> A price that is not on your list cannot go out. When it does not know, it says so and hands it to you.</p></div>
          <div>{I['key']}<p><b>Nothing locked in.</b> Month to month. Cancel at the end of any month and keep every script, transcript and file.</p></div>
        </div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-work" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-work">Everything here is live. <em>Open it.</em></h2><p class="tk-lede">Three sites for real owners and two 3D concept sites built in-house. <a href="testimonials.html">All the work</a></p></div>
        <div class="tk-work">
          <a href="https://performancelab.fitness" target="_blank" rel="noopener"><figure><img src="previews/work-perflab.webp" alt="performancelab.fitness homepage" width="1100" height="687" loading="lazy" decoding="async" /><figcaption><b>Julia's Performance Lab</b><i>Website</i><span>A Seattle personal trainer. Site, brand, booking links and an events page she updates herself.</span></figcaption></figure></a>
          <a href="https://handmadebyhalle.com" target="_blank" rel="noopener"><figure><img src="previews/work-halle.webp" alt="handmadebyhalle.com homepage" width="1100" height="687" loading="lazy" decoding="async" /><figcaption><b>Handmade by Halle</b><i>Website</i><span>A one-woman home-decor studio. Fourteen pieces, seasonal collections, buying handed to her Etsy shop.</span></figcaption></figure></a>
          <a href="https://bakrjewelry.co" target="_blank" rel="noopener"><figure><img src="previews/work-bakr.webp" alt="bakrjewelry.co homepage: the BAKR wordmark with a diamond ring lying across it" width="1100" height="687" loading="lazy" decoding="async" /><figcaption><b>BAKR Jewelry</b><i>Website</i><span>A made-to-order jeweler. Paper and ink, a diamond you can recut with a click, and a gallery for every kind of piece.</span></figcaption></figure></a>
          <a href="aether/"><figure><img src="previews/work-aether.webp" alt="AETHER, a 3D site you scroll through" width="1100" height="687" loading="lazy" decoding="async" /><figcaption><b>AETHER</b><i>3D site</i><span>A concept site for AI agents. Scroll and the camera flies through a living 3D scene, or press Auto Tour and watch.</span></figcaption></figure></a>
          <a href="atrium/"><figure><img src="previews/work-atrium.webp" alt="ATRIUM, a house that builds itself in 3D as you scroll" width="1100" height="687" loading="lazy" decoding="async" /><figcaption><b>ATRIUM</b><i>3D site</i><span>A concept home-design site. The house builds itself around you as you scroll, and the estimate moves with every finish you pick.</span></figcaption></figure></a>
        </div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-stats" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-stats">
          <div class="sn-stat"><span>Services</span><b>8</b><small>three priced on this page, five quoted in writing</small></div>
          <div class="sn-stat"><span>From</span><b>$297</b><small>a month, month to month, no setup fee</small></div>
          <div class="sn-stat"><span>Picks up in about</span><b>8 sec</b><small>the target RING is built to, any hour</small></div>
          <div class="sn-stat"><span>Number to call</span><b>1</b><small>a person answers it: (480) 798-0753</small></div>
        </div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-faq" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-faq">Asked before hiring</h2><p class="tk-lede"><a href="faq.html">All the questions</a></p></div>
        <div class="sn-faq">{faq}</div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-talk" style="padding-top:0;padding-bottom:2rem">
      <div class="sn-inner">
        <div class="hp-talk">
          <div><h2 class="tk-h2" id="h-talk">Start with a <em>conversation.</em></h2><p class="tk-lede">Tell me where calls, leads, time or money are getting stuck. If what I build is a fit, you hear what it costs and how long it takes. If it is not, you hear that instead.</p><a class="hp-talk__phone" href="tel:4807980753">(480) 798-0753</a><br/><a class="hp-talk__mail" href="mailto:jaden@greenaidigital.com">jaden@greenaidigital.com</a></div>
          <div class="tk-plate"><p><b>GreenAI Solutions</b>, Gilbert, Arizona. I read every message myself and usually reply the same business day.</p><p>Rather write it down? Send the form and watch your inbox: the first reply lands within a minute, sent by the same AI that would answer your customers. The rest of the conversation is with me.</p><a href="contact.html" class="tk-btn tk-btn--line">Send a message</a></div>
        </div>
        <p class="ag-tm">{esc(TM)}</p>
      </div>
    </section>
  </main>
  <div class="sn-sticky"><a href="services.html" class="tk-btn tk-btn--solid tk-btn--arrow">See the four services</a></div>''' + tail("""
  <script>
  (function(){
    var imgs=[].slice.call(document.querySelectorAll('#hp-shots img')), url=document.getElementById('hp-url'); if(imgs.length<2||!url) return;
    if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var i=0; setInterval(function(){ imgs[i].classList.remove('on'); i=(i+1)%imgs.length; imgs[i].classList.add('on'); url.textContent=imgs[i].getAttribute('data-url'); }, 3200);
  })();
  </script>""")

# the homepage canonical is the bare domain
PAGE = PAGE.replace('href="https://greenaidigital.com/index.html"', 'href="https://greenaidigital.com/"').replace('content="https://greenaidigital.com/index.html"', 'content="https://greenaidigital.com/"')
open(os.path.join(ROOT, "index.html"), "w").write(PAGE)
print("wrote index.html", len(PAGE))

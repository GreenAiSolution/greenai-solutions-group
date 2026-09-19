#!/usr/bin/env python3
"""gen_work.py — writes testimonials.html (the Work page) in the cinema system.
Order set by Jaden 2026-09-19: the sites under "Everything here is live. Open it." lead the page."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_platform_agents import I, NAV, head, tail, esc, ROOT

CSS = """
    /* work page only (wk-) */
    .wk-row { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: clamp(1.5rem, 4vw, 4rem); align-items: center; padding: clamp(2rem, 4vw, 3.5rem) 0; border-top: 1px solid var(--line); }
    .sn-head + .wk-row { border-top: 0; padding-top: 0; }
    .wk-row--flip .wk-shot { order: 2; }
    .wk-shot { display: block; border: 1px solid var(--line-2); border-radius: 18px; overflow: hidden; background: #0A1A11; box-shadow: var(--shadow-2); transition: transform .3s, border-color .2s; text-decoration: none; }
    .wk-shot:hover { transform: translateY(-5px); border-color: var(--green); }
    .wk-shot__bar { display: flex; align-items: center; gap: .4rem; padding: .6rem .9rem; background: rgba(255,255,255,.04); border-bottom: 1px solid var(--line); }
    .wk-shot__bar i { width: 8px; height: 8px; border-radius: 50%; background: rgba(232,196,106,.35); }
    .wk-shot__bar span { margin-left: .5rem; font-family: var(--mono); font-size: .72rem; letter-spacing: .04em; color: var(--ink-3); }
    .wk-shot img { display: block; width: 100%; height: auto; aspect-ratio: 16 / 10; object-fit: cover; object-position: top; }
    body.tk .wk-kind { margin: 0 0 .9rem; font-family: var(--mono); font-size: .7rem; letter-spacing: .22em; text-transform: uppercase; color: var(--green); }
    body.tk .wk-row h3 { margin: 0 0 .8rem; font-family: var(--font-display); font-weight: 600; font-size: clamp(1.6rem, 2.6vw, 2.2rem); letter-spacing: -.02em; line-height: 1.1; color: var(--ink); }
    body.tk .wk-row p { margin: 0 0 1.1rem; font-size: 1.02rem; line-height: 1.65; color: var(--ink-2); }
    .wk-row ul { margin: 0 0 1.5rem; padding: 0; list-style: none; display: grid; gap: .55rem; }
    .wk-row li { position: relative; padding-left: 1.3rem; font-size: .95rem; line-height: 1.5; color: var(--ink-2); }
    .wk-row li::before { content: ""; position: absolute; left: 0; top: .6em; width: .55rem; height: 1px; background: var(--green); }
    .wk-two { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
    .wk-two .wk-shot img { aspect-ratio: 16 / 9.4; }
    .wk-two figure { margin: 0; }
    .wk-two figcaption { margin-top: 1.1rem; }
    .wk-two figcaption b { display: block; margin-bottom: .35rem; font-family: var(--font-display); font-weight: 600; font-size: 1.35rem; color: var(--ink); }
    .wk-two figcaption span { display: block; font-size: .95rem; line-height: 1.6; color: var(--ink-2); }
    .wk-two figcaption a { display: inline-block; margin-top: .8rem; font-weight: 600; font-size: .92rem; color: var(--green); text-decoration: none; }
    .wk-oss { margin: 0; padding: 0; list-style: none; border-top: 1px solid var(--line); }
    .wk-oss li { display: grid; grid-template-columns: 12rem minmax(0, 1fr) auto; gap: 1.5rem; align-items: start; padding: 1.5rem 0; border-bottom: 1px solid var(--line); }
    .wk-oss b { font-family: var(--font-display); font-weight: 600; font-size: 1.2rem; color: var(--ink); }
    .wk-oss small { display: block; margin-top: .3rem; font-family: var(--mono); font-weight: 400; font-size: .68rem; letter-spacing: .12em; text-transform: uppercase; color: var(--ink-3); }
    .wk-oss p { margin: 0; font-size: .95rem; line-height: 1.6; color: var(--ink-2); }
    .wk-oss a { font-weight: 600; font-size: .92rem; color: var(--green); text-decoration: none; white-space: nowrap; }
    @media (max-width: 860px) { .wk-row, .wk-two { grid-template-columns: 1fr; } .wk-row--flip .wk-shot { order: 0; } .wk-oss li { grid-template-columns: 1fr; gap: .6rem; } }
"""

def shot(href, img, alt, url, ext=True):
    t = ' target="_blank" rel="noopener"' if ext else ''
    return (f'<a class="wk-shot" href="{href}"{t} aria-label="Open {esc(url)}"><div class="wk-shot__bar"><i></i><i></i><i></i><span>{esc(url)}</span></div>'
            f'<img src="{img}" alt="{esc(alt)}" width="1100" height="687" loading="lazy" decoding="async" /></a>')

def row(flip, href, img, alt, url, kind, name, body, points):
    lis = "".join(f"<li>{p}</li>" for p in points)
    return f'''<article class="wk-row{' wk-row--flip' if flip else ''}">
          {shot(href, img, alt, url)}
          <div><p class="wk-kind">{kind}</p><h3>{name}</h3><p>{body}</p><ul>{lis}</ul><a href="{href}" target="_blank" rel="noopener" class="tk-btn tk-btn--solid tk-btn--arrow">Open {esc(url)}</a></div>
        </article>'''

sites = "".join([
    row(False, "https://bakrjewelry.co", "previews/work-bakr.webp", "bakrjewelry.co homepage: the BAKR wordmark with a diamond ring lying across it", "bakrjewelry.co",
        "Website · made-to-order jeweler", "BAKR Jewelry",
        "Boston makes rings, and everything else you would wear, one piece at a time. The site is paper and ink like his logo, with a diamond lying across the wordmark that you can recut with a click.",
        ["A gallery page for rings, chains, pendants, earrings and bracelets", "A shop carousel where every piece opens its own page", "A design-with-me form that goes straight to his inbox", "An about page in his own words"]),
    row(True, "https://performancelab.fitness", "previews/work-perflab.webp", "performancelab.fitness homepage", "performancelab.fitness",
        "Website · personal trainer", "Julia's Performance Lab",
        "A Seattle personal trainer. Her clients find her on their phones, so the site is laid out like the link pages athletes already use, with her brand carried through all of it.",
        ["Programs, booking and socials one tap from the top", "An events page she updates herself from a template", "An about page and her own domain"]),
    row(False, "https://handmadebyhalle.com", "previews/work-halle.webp", "handmadebyhalle.com homepage", "handmadebyhalle.com",
        "Website · home-decor studio", "Handmade by Halle",
        "A one-woman home-decor studio in Arizona. Every piece is made by hand, so the site was built by hand too.",
        ["Fourteen pieces, each with its own photography and description", "Seasonal collections that change with the calendar, not with a rebuild", "Buying hands off to her established Etsy shop, so there is no new account to trust"]),
])

def lab(href, img, name, text):
    return f'<a href="{href}"><figure><img src="{img}" alt="{esc(name)}" width="1100" height="687" loading="lazy" decoding="async" /><figcaption><b>{name}</b><i>Open</i><span>{text}</span></figcaption></figure></a>'

labs = "".join([
    lab("blackbox/", "previews/work-blackbox.webp", "BLACKBOX", "A flight recorder for AI agents. Every call is logged and hash-chained, and the page replays a real agent taking 150 attacks so you can scrub through what it did."),
    lab("gauntlet/", "previews/work-gauntlet.webp", "THE GAUNTLET", "A live prompt-injection lab. You write the attack, an AI assistant reads it, and you see which of eight filters caught you."),
    lab("friction/", "previews/work-friction.webp", "FRICTION", "What bad design costs, measured on you. The same sign-up form built two ways, with a timer on both."),
    lab("tesseract/", "previews/work-tesseract.webp", "TESSERACT", "Five hundred attacks on an AI agent, replayed in four dimensions with a time scrubber."),
])

PAGE = head("Work — GreenAI Solutions",
            "Everything here is live: three websites built for real owners, two 3D sites built in-house, four working systems you can open on this site, and three open-source projects you can verify from a fresh clone.",
            "testimonials.html", CSS) + f'''
<body class="tk light-top">
  <a href="#main" class="skip-link">Skip to content</a>
  <nav class="nav transparent" id="main-nav" aria-label="Main navigation">
{NAV}
  </nav>
  <main id="main">

    <div class="sn-wrap"><header class="sn-panel sn-hero" aria-labelledby="hero-heading">
      <div class="sn-hero__inner">
        <p class="tk-eyebrow"><b>Work</b> · nothing here is a mock-up</p>
        <h1 class="tk-h1" id="hero-heading">Everything here is live. <em>Open it.</em></h1>
        <p class="sn-hero__sub">Three websites for real owners, two 3D sites built in-house, four working systems running on this site and three open-source projects. Every one has a link. Click before you call.</p>
        <div class="sn-hero__cta">
          <a href="#sites" class="tk-btn tk-btn--inverse tk-btn--arrow">Start with the sites</a>
          <a href="service-web-design.html" class="tk-btn tk-btn--ghost">Websites from $500</a>
        </div>
      </div>
    </header></div>

    <section class="sn-sec" id="sites" aria-labelledby="h-sites">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-sites">Built for real owners, <em>live today.</em></h2><p class="tk-lede">Coded by hand, no themes and no page builder. The screenshots are captures of the real homepages.</p></div>
        {sites}
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-3d" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-3d">3D sites, <em>built in-house.</em></h2><p class="tk-lede">Two concept sites made to show how far a web page can go. No client is claimed for either. Best on a laptop or desktop.</p></div>
        <div class="wk-two">
          <figure>{shot("aether/", "previews/work-aether.webp", "AETHER, a 3D site you scroll through", "greenaidigital.com/aether", ext=False)}<figcaption><b>AETHER</b><span>A concept site for AI agents. Scroll and the camera flies through a living 3D scene: a reasoning core, an orbiting swarm, rings of data. Or press Auto Tour and watch.</span><a href="aether/">Open AETHER →</a></figcaption></figure>
          <figure>{shot("atrium/", "previews/work-atrium.webp", "ATRIUM, a house that builds itself in 3D as you scroll", "greenaidigital.com/atrium", ext=False)}<figcaption><b>ATRIUM</b><span>A concept home-design site. A 1,564 square foot house builds itself around you as you scroll, and the estimate moves with every finish you pick. The dollar figures are list-price assumptions for Phoenix, not a quote.</span><a href="atrium/">Open ATRIUM →</a></figcaption></figure>
        </div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-labs" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-labs">Working systems, <em>running on this site.</em></h2><p class="tk-lede">Each one opens in this browser and does something.</p></div>
        <div class="tk-work" style="grid-template-columns:repeat(2,minmax(0,1fr))">{labs}</div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-oss" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-oss">Open source, <em>independently verifiable.</em></h2><p class="tk-lede">Three engineering projects published in full. Every number reproduces from a fresh clone, and the write-ups say plainly where each one loses.</p></div>
        <ul class="wk-oss">
          <li><b>KILN<small>Tensor compiler · MIT licence</small></b><p>A tensor compiler that generates its own ARM64 machine code. 491 of 491 instructions byte-identical to Apple's own assembler. Apple's Accelerate still beats it at large matrix multiplies, and the write-up says that first.</p><a href="https://greenaisolution.github.io/kiln/" target="_blank" rel="noopener">Read the write-up →</a></li>
          <li><b>STRATA<small>Search and retrieval</small></b><p>Hybrid search written from scratch in numpy: keyword, vector, fusion and re-ranking. Measured against five public datasets, with the gap to published baselines reported to four decimal places.</p><a href="https://github.com/GreenAiSolution/greenai-strata" target="_blank" rel="noopener">View the source →</a></li>
          <li><b>CRUCIBLE<small>Agent evaluation</small></b><p>Thirty tasks where obvious automation breaks a rule that matters. An agent works one shift and ordinary Python checks what it did. No model grading another model.</p><a href="https://github.com/GreenAiSolution/crucible" target="_blank" rel="noopener">View the source →</a></li>
        </ul>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-cta" style="padding-top:0;padding-bottom:2rem">
      <div class="sn-inner" style="text-align:center">
        <div class="sn-head"><h2 class="tk-h2" id="h-cta">That is the standard. <em>Now it points at your company.</em></h2><p class="tk-lede">One AI services workforce: websites from $500, AI staff from $297 a month, a month of finished ads from $697, and custom systems quoted after one conversation. Month to month, and everything built is yours.</p></div>
        <div class="sn-hero__cta"><a href="services.html" class="tk-btn tk-btn--solid tk-btn--arrow">See the services and prices</a><a href="contact.html" class="tk-btn tk-btn--line">Talk to Jaden</a></div>
      </div>
    </section>
  </main>''' + tail()

open(os.path.join(ROOT, "testimonials.html"), "w").write(PAGE)
print("wrote testimonials.html", len(PAGE))

#!/usr/bin/env python3
"""gen_services.py — services.html as a cinematic, luxury four-scene film. Dark ground, gold titles, the robots as the cast."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_platform_agents import I, NAV, AGENTS, FULL, SEPARATE, TM, head, tail, esc, ROOT, ICON_OF
from robots import robot, bust

GOLD="#E8C46A"
CSS = f"""
    /* ---- the cinema: this page runs dark end to end ---- */
    body.tk.sv-cinema, body.tk.sv-cinema::before {{ background: #06100A; }}
    body.tk.sv-cinema::before {{ background-image: radial-gradient(60% 40% at 50% 0%, rgba(232,196,106,.10), transparent 60%); }}
    body.tk.sv-cinema .nav.transparent, body.tk.sv-cinema .nav.scrolled {{ background: rgba(6,16,10,.7); }}
    body.tk.sv-cinema .nav .nav__logo-name, body.tk.sv-cinema .nav .nav__logo-sub, body.tk.sv-cinema .nav .nav__link {{ color: rgba(255,255,255,.85); }}
    body.tk.sv-cinema .nav .nav__hamburger span {{ background: #fff; }}
    body.tk.sv-cinema .nav__cta {{ background: {GOLD}; border-color: {GOLD}; color: #06100A; }}
    .sv-grain {{ position: fixed; inset: 0; z-index: 5; pointer-events: none; opacity: .07; mix-blend-mode: screen; }}
    .sv-vig {{ position: fixed; inset: 0; z-index: 4; pointer-events: none; background: radial-gradient(80% 70% at 50% 40%, transparent 55%, rgba(0,0,0,.55)); }}
    .sv {{ color: #fff; }}
    .sv h1, .sv h2, .sv h3 {{ color: #fff; }}
    .sv h1 em, .sv h2 em, .sv h3 em {{ color: {GOLD}; font-style: italic; font-family: 'Fraunces', Georgia, serif; font-weight: 500; }}
    .sv p {{ color: rgba(255,255,255,.72); }}
    .sv-slate {{ display: inline-flex; align-items: center; gap: .8rem; margin: 0 0 1.4rem; font-family: var(--mono); font-size: .72rem; letter-spacing: .3em; text-transform: uppercase; color: {GOLD}; }}
    .sv-slate::before, .sv-slate::after {{ content: ""; width: 2.4rem; height: 1px; background: {GOLD}; opacity: .7; }}
    .sv-hero {{ position: relative; padding: 9rem 1.5rem 3rem; text-align: center; overflow: hidden; }}
    .sv-hero h1 {{ margin: 0 auto 1.2rem; max-width: 14ch; font-family: var(--font-display); font-weight: 600; font-size: clamp(3rem, 7.6vw, 6.4rem); line-height: .98; letter-spacing: -.03em; }}
    .sv-hero p {{ max-width: 58ch; margin: 0 auto 1.8rem; font-size: 1.12rem; line-height: 1.6; }}
    .sv-bars {{ height: 44px; background: #000; margin: 0 -16px; }}
    .sv-cast {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 1.2rem 2rem; margin: 3.2rem auto 0; max-width: 1000px; }}
    .sv-cast a {{ display: grid; justify-items: center; gap: .5rem; text-decoration: none; color: rgba(255,255,255,.75); font-family: var(--mono); font-size: .66rem; letter-spacing: .24em; text-transform: uppercase; }}
    .sv-cast span {{ display: grid; place-items: center; width: 92px; height: 92px; border-radius: 50%; border: 1px solid rgba(232,196,106,.55); background: radial-gradient(circle at 50% 30%, rgba(232,196,106,.18), transparent 70%); box-shadow: 0 0 0 6px rgba(232,196,106,.06), 0 30px 60px -30px rgba(0,0,0,.8); overflow: hidden; transition: transform .25s, border-color .25s; }}
    .sv-cast span img {{ width: 88px; height: 88px; border-radius: 50%; object-fit: cover; }}
    .sv-cast a:hover span {{ transform: translateY(-6px) scale(1.05); border-color: {GOLD}; }}
    .sv-cast a:hover {{ color: #fff; }}
    .sv-scene {{ position: relative; margin: 0 16px 16px; border-radius: var(--radius-lg); overflow: hidden; background: linear-gradient(180deg, #0A1A11, #06100A); border: 1px solid rgba(232,196,106,.14); }}
    .sv-scene::before {{ content: ""; position: absolute; inset: 0; background: radial-gradient(50% 60% at var(--x, 70%) 30%, color-mix(in srgb, var(--ac, {GOLD}) 22%, transparent), transparent 60%); pointer-events: none; }}
    .sv-scene__in {{ position: relative; display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: 3rem 4rem; align-items: center; max-width: 1240px; margin: 0 auto; padding: clamp(3.5rem, 7vw, 6rem) 1.5rem; }}
    .sv-scene--flip .sv-scene__in {{ grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); }}
    .sv-scene--flip .sv-scene__copy {{ order: 2; }}
    .sv-scene__num {{ font-family: 'Fraunces', Georgia, serif; font-style: italic; font-weight: 500; font-size: clamp(4rem, 9vw, 7rem); line-height: .8; color: {GOLD}; opacity: .35; margin-bottom: .6rem; }}
    .sv-scene h2 {{ margin: 0 0 .9rem; font-family: var(--font-display); font-weight: 600; font-size: clamp(2.2rem, 4.4vw, 3.6rem); line-height: 1.02; letter-spacing: -.025em; }}
    .sv-scene .lede {{ font-size: 1.08rem; line-height: 1.6; max-width: 46ch; margin: 0 0 1.4rem; }}
    .sv-price {{ display: flex; align-items: baseline; gap: .6rem; margin: 0 0 1.6rem; padding-top: 1.2rem; border-top: 1px solid rgba(232,196,106,.35); }}
    .sv-price b {{ font-family: var(--font-display); font-weight: 600; font-size: 2.4rem; letter-spacing: -.03em; color: #fff; line-height: 1; }}
    .sv-price span {{ color: rgba(255,255,255,.6); font-size: .95rem; }}
    .sv-cta {{ display: flex; flex-wrap: wrap; gap: .75rem; }}
    .sv-cta .tk-btn--solid {{ background: {GOLD}; border-color: {GOLD}; color: #06100A; box-shadow: 0 16px 40px -14px rgba(232,196,106,.7); }}
    .sv-cta .tk-btn--solid:hover {{ background: #F2D68A; border-color: #F2D68A; color: #06100A; }}
    .sv-cta .tk-btn--ghost {{ border-color: rgba(255,255,255,.35); color: #fff; }}
    .sv-stage {{ position: relative; }}
    .sv-stage .rb-float {{ position: absolute; width: 190px; z-index: 2; }}
    .sv-spot {{ position: absolute; width: 260px; height: 90px; border-radius: 50%; background: radial-gradient(closest-side, color-mix(in srgb, var(--ac, {GOLD}) 40%, transparent), transparent); filter: blur(6px); z-index: 1; }}
    .sv-screen {{ position: relative; border-radius: 18px; overflow: hidden; border: 1px solid rgba(232,196,106,.3); box-shadow: 0 0 0 1px rgba(0,0,0,.6), 0 60px 120px -40px rgba(0,0,0,.9), 0 0 80px -20px color-mix(in srgb, var(--ac, {GOLD}) 45%, transparent); background: #0B1B12; }}
    .sv-screen .tk-plate {{ border-radius: 0; border: 0; box-shadow: none; background: #0B1B12; color: #fff; }}
    .sv-screen .ag-lines .them {{ background: rgba(255,255,255,.08); color: #fff; }}
    .sv-screen .ag-lines .us {{ background: {GOLD}; color: #06100A; }}
    .sv-screen .ag-call__top, .sv-screen .ag-call__foot {{ color: rgba(255,255,255,.6); border-color: rgba(255,255,255,.1); }}
    .sv-screen .ag-call__top b {{ color: {GOLD}; }}
    .sv-screen .ag-call__top i {{ background: {GOLD}; box-shadow: 0 0 0 4px rgba(232,196,106,.2); }}
    .sv-roster {{ margin: 0; padding: 0; list-style: none; }}
    .sv-roster li {{ display: grid; grid-template-columns: 2.6rem 6.5rem minmax(0, 1fr) auto; gap: .8rem; align-items: center; padding: .6rem 0; border-bottom: 1px solid rgba(255,255,255,.08); font-size: .92rem; color: rgba(255,255,255,.7); }}
    .sv-roster li img {{ width: 2.6rem; height: 2.6rem; border-radius: 50%; object-fit: cover; }}
    .sv-roster a {{ color: #fff; font-family: var(--font-display); font-weight: 600; text-decoration: none; letter-spacing: .02em; }}
    .sv-roster a:hover {{ color: {GOLD}; }}
    .sv-roster b {{ color: {GOLD}; font-family: var(--font-display); font-weight: 600; white-space: nowrap; }}
    .sv-theatre {{ position: relative; padding: 2.2rem 2rem 2.6rem; border-radius: 22px; background: linear-gradient(180deg, #000 0, #000 100%); border: 1px solid rgba(232,196,106,.25); }}
    .sv-theatre::before {{ content: ""; position: absolute; left: 10%; right: 10%; top: 0; height: 60%; background: radial-gradient(60% 100% at 50% 0%, rgba(232,196,106,.22), transparent 70%); pointer-events: none; }}
    .sv-theatre .hp-browser {{ position: relative; border-color: rgba(232,196,106,.3); background: #000; box-shadow: 0 40px 80px -30px rgba(0,0,0,.9); }}
    .sv-theatre .hp-browser__bar {{ background: #111; border-color: #222; }}
    .sv-theatre .hp-browser__url {{ color: rgba(255,255,255,.6); }}
    .sv-theatre__cap {{ display: flex; justify-content: space-between; gap: 1rem; margin-top: 1rem; font-family: var(--mono); font-size: .68rem; letter-spacing: .22em; text-transform: uppercase; color: {GOLD}; }}
    .sv-tiers {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .8rem; margin-top: 1.4rem; }}
    .sv-tiers div {{ padding: 1rem 1rem .9rem; border-radius: 16px; border: 1px solid rgba(232,196,106,.25); background: rgba(255,255,255,.03); }}
    .sv-tiers small {{ display: block; font-family: var(--mono); font-size: .64rem; letter-spacing: .2em; text-transform: uppercase; color: {GOLD}; margin-bottom: .35rem; }}
    .sv-tiers b {{ display: block; font-family: var(--font-display); font-weight: 600; font-size: 1.5rem; letter-spacing: -.02em; color: #fff; }}
    .sv-tiers span {{ font-size: .82rem; color: rgba(255,255,255,.6); }}
    .sv-film {{ position: relative; margin: 0 -1.5rem; padding: 1.4rem 0; background: #000; overflow: hidden; border-top: 1px solid rgba(232,196,106,.25); border-bottom: 1px solid rgba(232,196,106,.25); }}
    .sv-film::before, .sv-film::after {{ content: ""; position: absolute; left: 0; right: 0; height: 14px; background: repeating-linear-gradient(90deg, transparent 0 14px, rgba(255,255,255,.25) 14px 24px, transparent 24px 36px); }}
    .sv-film::before {{ top: 5px; }} .sv-film::after {{ bottom: 5px; }}
    .sv-film__track {{ display: flex; gap: 12px; width: max-content; padding: 6px 0; animation: sn-march 40s linear infinite; }}
    .sv-film:hover .sv-film__track {{ animation-play-state: paused; }}
    .sv-film__track > div {{ position: relative; width: 150px; aspect-ratio: 9/16; border-radius: 6px; overflow: hidden; background: #111; border: 1px solid rgba(255,255,255,.12); }}
    .sv-film__track video, .sv-film__track img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
    .sv-film__track span {{ position: absolute; left: 6px; bottom: 6px; padding: .12rem .4rem; border-radius: 999px; background: rgba(0,0,0,.7); color: {GOLD}; font-family: var(--mono); font-size: .58rem; letter-spacing: .12em; }}
    @media (prefers-reduced-motion: reduce) {{ .sv-film__track {{ animation: none; flex-wrap: wrap; width: auto; }} }}
    .sv-schem {{ position: relative; padding: 1.6rem; border-radius: 22px; background: #000; border: 1px solid rgba(232,196,106,.25); }}
    .sv-schem svg {{ display: block; width: 100%; height: auto; }}
    .sv-credits {{ position: relative; max-width: 900px; margin: 0 auto; padding: clamp(4rem, 8vw, 7rem) 1.5rem 3rem; text-align: center; }}
    .sv-credits h2 {{ font-family: var(--font-display); font-weight: 600; font-size: clamp(2rem, 4vw, 3rem); letter-spacing: -.02em; margin: 0 0 2rem; }}
    .sv-credits ol {{ list-style: none; margin: 0; padding: 0; counter-reset: c; }}
    .sv-credits li {{ counter-increment: c; display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; padding: 1rem 0; border-bottom: 1px solid rgba(232,196,106,.18); text-align: right; }}
    .sv-credits li b {{ font-family: var(--mono); font-size: .72rem; letter-spacing: .26em; text-transform: uppercase; color: {GOLD}; align-self: center; }}
    .sv-credits li p {{ margin: 0; text-align: left; font-size: .98rem; line-height: 1.55; }}
    .sv-menu {{ width: 100%; border-collapse: collapse; margin: 2.5rem 0 0; text-align: left; }}
    .sv-menu td {{ padding: .85rem 0; border-bottom: 1px solid rgba(232,196,106,.18); color: rgba(255,255,255,.72); font-size: .95rem; }}
    .sv-menu td:first-child {{ font-family: var(--font-display); font-weight: 600; color: #fff; font-size: 1.1rem; }}
    .sv-menu td:last-child {{ text-align: right; color: {GOLD}; font-family: var(--font-display); font-weight: 600; white-space: nowrap; }}
    .sv-end {{ text-align: center; padding: 3rem 1.5rem 2rem; }}
    .sv-end .num {{ display: block; margin: 1rem 0 .4rem; font-family: var(--font-display); font-weight: 600; font-size: clamp(2.2rem, 5vw, 3.6rem); letter-spacing: -.03em; color: #fff; text-decoration: none; }}
    .sv-end .num:hover {{ color: {GOLD}; }}
    body.tk.sv-cinema .footer {{ background: #000; }}
    body.tk.sv-cinema .sn-sticky .tk-btn {{ background: {GOLD}; border-color: {GOLD}; color: #06100A; box-shadow: 0 20px 50px -14px rgba(232,196,106,.7); }}
    body.tk.sv-cinema .ag-tm {{ color: rgba(255,255,255,.4); }}
    body.tk.sv-cinema .sv h1, body.tk.sv-cinema .sv h2, body.tk.sv-cinema .sv h3, body.tk.sv-cinema .sv-price b, body.tk.sv-cinema .sv-tiers b, body.tk.sv-cinema .sv-menu td:first-child, body.tk.sv-cinema .sv-end .num, body.tk.sv-cinema .sv-roster a {{ color: #fff; }}
    body.tk.sv-cinema .sv h1 em, body.tk.sv-cinema .sv h2 em, body.tk.sv-cinema .sv-roster b, body.tk.sv-cinema .sv-menu td:last-child, body.tk.sv-cinema .sv-credits li b, body.tk.sv-cinema .sv-tiers small {{ color: {GOLD}; }}
    body.tk.sv-cinema .sv p, body.tk.sv-cinema .sv-menu td, body.tk.sv-cinema .sv-roster li {{ color: rgba(255,255,255,.72); }}
    body.tk.sv-cinema .sv-slate {{ color: {GOLD}; }}
    @media (max-width: 900px) {{ .sv-scene__in, .sv-scene--flip .sv-scene__in {{ grid-template-columns: 1fr; }} .sv-scene--flip .sv-scene__copy {{ order: 0; }} .sv-stage .rb-float {{ display: none; }} .sv-tiers {{ grid-template-columns: 1fr; }} .sv-credits li {{ grid-template-columns: 1fr; text-align: left; gap: .3rem; }} }}
    @media (prefers-reduced-motion: no-preference) {{ @supports (animation-timeline: view()) {{ .sv-scene__in > * {{ animation: tk-rise linear both; animation-timeline: view(); animation-range: entry 0% entry 30%; }} }} }}
"""

GRAIN = '<svg class="sv-grain" aria-hidden="true"><filter id="g"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .5 0"/></filter><rect width="100%" height="100%" filter="url(#g)"/></svg><div class="sv-vig" aria-hidden="true"></div>'

cast = "".join(f'<a href="{a["id"]}.html"><span>{bust(a["id"])}</span>{a["name"]}</a>' for a in AGENTS)
roster = "".join(f'<li>{bust(a["id"])}<a href="{a["id"]}.html">{a["name"]}</a><span>{esc(a["inside"])}</span><b>${a["price"]:,}/mo</b></li>' for a in AGENTS)
ring_mock = AGENTS[0]["mock"]
film = "".join([
 f'<div><video src="art/ad-vid-{v}.mp4" muted autoplay loop playsinline preload="metadata" poster="art/ad-angle-{p}.webp"></video><span>{lab}</span></div>'
 for v,p,lab in [("clock","clock","9:16 · 15s"),("reel","question","REEL"),("problem","problem","THE PROBLEM"),("founder","founder","THE FOUNDER"),("question","question","THE QUESTION"),("feed","split","FEED"),("wide","quote","16:9 · 30s")]])
film += f'<div><img src="art/ad-angle-quote.webp" alt="" loading="lazy"/><span>THE QUOTE</span></div><div><img src="art/ad-angle-split.webp" alt="" loading="lazy"/><span>BEFORE · AFTER</span></div>'

schem = f'''<svg viewBox="0 0 640 300" aria-label="A custom system drawn as a schematic: intake, checker, approval, log"><defs><filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<g fill="none" stroke="{GOLD}" stroke-width="1.5" filter="url(#glow)">
<rect x="30" y="110" width="130" height="70" rx="14"/><rect x="255" y="110" width="130" height="70" rx="14"/><rect x="480" y="110" width="130" height="70" rx="14"/>
<path d="M160 145 h95 M385 145 h95" stroke-dasharray="6 6"/><path d="M320 180 v50 h-200 v-50" stroke-dasharray="3 5" opacity=".7"/>
<rect x="255" y="20" width="130" height="50" rx="12" opacity=".8"/><path d="M320 70 v40" stroke-dasharray="3 5" opacity=".7"/>
<circle cx="245" cy="145" r="5" fill="{GOLD}"><animate attributeName="cx" values="160;255" dur="2.4s" repeatCount="indefinite"/></circle>
<circle cx="470" cy="145" r="5" fill="{GOLD}"><animate attributeName="cx" values="385;480" dur="2.4s" begin="1.2s" repeatCount="indefinite"/></circle>
</g>
<g font-family="Outfit, sans-serif" font-weight="600" font-size="15" fill="#fff" text-anchor="middle"><text x="95" y="140">INTAKE</text><text x="320" y="140">CHECKER</text><text x="545" y="140">APPROVAL</text><text x="320" y="50">YOUR RULES</text></g>
<g font-family="IBM Plex Mono, monospace" font-size="10" fill="rgba(255,255,255,.55)" text-anchor="middle"><text x="95" y="162">call · form · file</text><text x="320" y="162">blocks what is not on the list</text><text x="545" y="162">a person, before it acts</text><text x="320" y="252">every step logged, hash-chained, replayable</text></g></svg>'''

PAGE = head("Services — eight services from one AI workforce | GreenAI Solutions",
            "Eight services from one AI services workforce, every price the whole price. AI staff from $297 a month, hand-coded websites from $500, a month of finished ads from $697, custom systems quoted after one conversation. Gilbert, Arizona.",
            "services.html", CSS, og_title="Eight services. One workforce.").replace('<meta name="twitter:card" content="summary_large_image" />','<meta name="twitter:card" content="summary_large_image" />\n  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@1,9..144,500&display=swap" rel="stylesheet" />') + f'''
<body class="tk sv-cinema">
  <a href="#main" class="skip-link">Skip to content</a>
  <nav class="nav transparent" id="main-nav" aria-label="Main navigation">
{NAV}
  </nav>
  {GRAIN}
  <main id="main" class="sv">

    <header class="sv-hero" aria-labelledby="h1">
      <p class="sv-slate">GreenAI Solutions presents</p>
      <h1 id="h1">Eight services. <em>One workforce.</em></h1>
      <p>GreenAI is an AI services workforce: you hand over a job, and it gets done inside the tools you already use. Nothing here is a starting point that grows once you are in. The number next to each service is what it costs, the agreement you would sign is already on this site, and anything recurring is month to month.</p>
      <div class="sv-cta" style="justify-content:center"><a href="#s1" class="tk-btn tk-btn--solid tk-btn--arrow">Roll the eight</a><a href="tel:4807980753" class="tk-btn tk-btn--ghost">Call (480) 798-0753</a></div>
      <div class="sv-cast" aria-label="The cast">{cast}</div>
    </header>

    <section class="sv-scene" id="s1" style="--ac:#7DE3A4;--x:75%" aria-labelledby="h-s1">
      <div class="sv-scene__in">
        <div class="sv-scene__copy"><div class="sv-scene__num">01</div><p class="sv-slate">Scene one</p><h2 id="h-s1">AI <em>employees.</em></h2>
          <p class="lede">Six employees, one inside each app your company already runs on. Built for your company: your prices, your hours, your service area, your way of saying things. You read every reply before it goes live. It never claims to be a person, and when it does not know it says so.</p>
          <div class="sv-price"><b>from $297</b><span>a month each · all six ${FULL:,}</span></div>
          <div class="sv-cta"><a href="hire.html" class="tk-btn tk-btn--solid tk-btn--arrow">Build your staff</a><a href="staff.html" class="tk-btn tk-btn--ghost">Meet the staff</a><a href="catch.html" class="tk-btn tk-btn--ghost">Watch one catch a lead</a></div></div>
        <div class="sv-stage">
          <div class="sv-spot" style="right:-40px;top:-40px"></div><div class="rb-float" style="right:-60px;top:-90px">{robot("ring", I["phone"], label="RING", pose="wave")}</div>
          <div class="sv-screen" style="margin-right:80px"><div class="tk-plate ag-mock">{ring_mock}</div></div>
          <ul class="sv-roster" style="margin-top:1.4rem">{roster}</ul>
        </div>
      </div>
    </section>

    <section class="sv-scene sv-scene--flip" id="s2" style="--ac:#7CC4F0;--x:25%" aria-labelledby="h-s2">
      <div class="sv-scene__in">
        <div class="sv-scene__copy"><div class="sv-scene__num">02</div><p class="sv-slate">Scene two</p><h2 id="h-s2">Websites, <em>coded by hand.</em></h2>
          <p class="lede">A website has one job: someone lands on it, understands within five seconds what you do and whether it is for them, and then has an obvious next step. The build starts with the argument, not the look. Mobile first. The titles and structure Google reads go in during the build. Delivered in about seven business days, and the files are yours the day it launches.</p>
          <div class="sv-price"><b>from $500</b><span>one time · maintenance $150/mo, never required</span></div>
          <div class="sv-tiers"><div><small>Starter</small><b>$500</b><span>up to five pages</span></div><div><small>Business</small><b>$1,500</b><span>up to ten pages</span></div><div><small>Premium</small><b>$2,500+</b><span>custom scope, quoted</span></div></div>
          <div class="sv-cta" style="margin-top:1.4rem"><a href="service-web-design.html" class="tk-btn tk-btn--solid tk-btn--arrow">See the website service</a><a href="testimonials.html" class="tk-btn tk-btn--ghost">See sites that are live</a></div></div>
        <div class="sv-stage">
          <div class="sv-spot" style="right:-40px;bottom:-30px"></div><div class="rb-float" style="right:-60px;bottom:-30px">{robot("web", I["inbox"], label="Websites", pose="point")}</div>
          <div class="sv-theatre" style="margin-right:70px"><div class="hp-browser"><div class="hp-browser__bar"><i></i><i></i><i></i><span class="hp-browser__url" id="hp-url">performancelab.fitness</span></div><div class="hp-browser__shots" id="hp-shots"><img class="on" src="previews/work-perflab.webp" alt="performancelab.fitness" width="1100" height="687" loading="lazy" data-url="performancelab.fitness"/><img src="previews/work-halle.webp" alt="handmadebyhalle.com" width="1100" height="687" loading="lazy" data-url="handmadebyhalle.com"/><img src="previews/work-blackbox.webp" alt="greenaidigital.com/blackbox" width="1100" height="687" loading="lazy" data-url="greenaidigital.com/blackbox"/></div></div><div class="sv-theatre__cap"><span>Now showing · three live sites</span><span>built here</span></div></div>
        </div>
      </div>
    </section>

    <section class="sv-scene" id="s3" style="--ac:#F5A38E;--x:70%" aria-labelledby="h-s3">
      <div class="sv-scene__in" style="grid-template-columns:1fr">
        <div class="sv-scene__copy" style="max-width:60ch"><div class="sv-scene__num">03</div><p class="sv-slate">Scene three</p><h2 id="h-s3">Ad creation. <em>One idea, seven angles.</em></h2>
          <p class="lede">Targeting, bidding and placement are automated by the platforms now. Creative is the last lever left, and most businesses make exactly one ad. Here one idea gets seven angles, because nobody can tell you in advance which one your market responds to. Every batch arrives captioned, in vertical, square, fifteen-second and thirty-second cuts. You own them permanently, including after you cancel.</p>
          <div class="sv-price"><b>from $697</b><span>a month · cancel any month</span></div></div>
        <div class="sv-film" aria-label="A month of finished ads, as a film strip"><div class="sv-film__track">{film}{film}</div></div>
        <div>
          <div class="sv-tiers" style="max-width:820px"><div><small>Starter</small><b>$697/mo</b><span>ten finished ads a month</span></div><div><small>Growth · most popular</small><b>$1,297/mo</b><span>twenty-five, the whole seven-angle spread</span></div><div><small>Scale</small><b>$2,497/mo</b><span>sixty, for heavy spend across platforms</span></div></div>
          <div class="sv-cta" style="margin-top:1.4rem"><a href="service-ai-ads.html" class="tk-btn tk-btn--solid tk-btn--arrow">See the ad desk</a></div>
        </div>
      </div>
    </section>

    <section class="sv-scene sv-scene--flip" id="s4" style="--ac:#E8C46A;--x:30%" aria-labelledby="h-s4">
      <div class="sv-scene__in">
        <div class="sv-scene__copy"><div class="sv-scene__num">04</div><p class="sv-slate">Scene four</p><h2 id="h-s4">Custom systems, <em>when it has to be built.</em></h2>
          <p class="lede">An intake line for a care agency. A quoting tool that reads a set of plans. A test bench for the automations you already run, so you find out they broke before a customer does. A dashboard for the numbers nobody is watching. Scoped in a conversation, priced in writing before a line of code, built by the person you talked to. Whoever does the work does not grade it.</p>
          <div class="sv-price"><b>Quoted</b><span>after one conversation · fixed price in writing</span></div>
          <div class="sv-cta"><a href="service-ai-consulting.html" class="tk-btn tk-btn--solid tk-btn--arrow">See what has been built</a><a href="contact.html?want=custom" class="tk-btn tk-btn--ghost">Describe what you need</a></div></div>
        <div class="sv-stage">
          <div class="sv-spot" style="right:-40px;bottom:-30px"></div><div class="rb-float" style="right:-60px;bottom:-30px">{robot("custom", I["receipt"], label="Custom systems", pose="think")}</div>
          <div class="sv-schem" style="margin-right:70px">{schem}</div>
        </div>
      </div>
    </section>

    <section class="sv-scene" id="s5" style="--ac:#7CC4F0;--x:70%" aria-labelledby="h-s5">
      <div class="sv-scene__in">
        <div class="sv-scene__copy"><div class="sv-scene__num">05</div><p class="sv-slate">Scene five</p><h2 id="h-s5">AI SEO, <em>done for you.</em></h2>
          <p class="lede">One AI agent does the SEO work end to end. It crawls the site every week, fixes what it finds, writes the service and city pages you are missing, keeps your Google Business Profile alive and reports what changed in plain English. No new tools to learn, no new hire. Nothing goes live until you have read it, and nobody here will promise you page one.</p>
          <div class="sv-price"><b>Quoted</b><span>after a free first audit · month to month</span></div>
          <div class="sv-cta"><a href="service-ai-seo.html" class="tk-btn tk-btn--solid tk-btn--arrow">See how AI SEO works</a><a href="contact.html?want=seo" class="tk-btn tk-btn--ghost">Ask for the free audit</a></div></div>
        <div class="sv-stage">
          <div class="sv-spot" style="right:-40px;top:-40px"></div><div class="rb-float" style="right:-60px;top:-90px">{robot("seo", I["inbox"], label="AI SEO", pose="point")}</div>
          <div class="sv-schem" style="margin-right:70px"><ul class="sv-roster"><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Weekly crawl of every page</span><b>audit</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Titles, links, speed, markup</span><b>fixed</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Service and city pages</span><b>written</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Google Business Profile</span><b>kept alive</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Monthly report, Google's numbers</span><b>plain English</b></li></ul></div>
        </div>
      </div>
    </section>

    <section class="sv-scene sv-scene--flip" id="s6" style="--ac:#E8C46A;--x:30%" aria-labelledby="h-s6">
      <div class="sv-scene__in">
        <div class="sv-scene__copy"><div class="sv-scene__num">06</div><p class="sv-slate">Scene six</p><h2 id="h-s6">CRM and dashboards, <em>made to work.</em></h2>
          <p class="lede">Most small companies pay for a CRM and run the business from memory. The one you already have gets cleaned up: duplicates merged, stages that match how you sell, follow-ups that send themselves, your tools connected. Then the numbers that matter go on one screen you can read in a minute, with a summary every Monday.</p>
          <div class="sv-price"><b>Quoted</b><span>after a read-only look · fixed price in writing</span></div>
          <div class="sv-cta"><a href="service-crm-dashboards.html" class="tk-btn tk-btn--solid tk-btn--arrow">See what gets fixed</a><a href="contact.html?want=crm" class="tk-btn tk-btn--ghost">Tell us which CRM you use</a></div></div>
        <div class="sv-stage">
          <div class="sv-spot" style="right:-40px;bottom:-30px"></div><div class="rb-float" style="right:-60px;bottom:-30px">{robot("crm", I["sun"], label="CRM and dashboards", pose="stand")}</div>
          <div class="sv-schem" style="margin-right:70px"><ul class="sv-roster"><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">New leads this week</span><b>23</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Answered in, median</span><b>0:52</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Quotes out</span><b>$18,400</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Owed to you</span><b>$4,120</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span>Example numbers, not a client's</span><b></b></li></ul></div>
        </div>
      </div>
    </section>

    <section class="sv-scene" id="s7" style="--ac:#7DE3A4;--x:70%" aria-labelledby="h-s7">
      <div class="sv-scene__in">
        <div class="sv-scene__copy"><div class="sv-scene__num">07</div><p class="sv-slate">Scene seven</p><h2 id="h-s7">Google reviews, <em>asked for every time.</em></h2>
          <p class="lede">When someone needs you tonight they look at the stars and the number next to them. Every finished job gets a short review request and one reminder, every review gets a reply drafted in your wording, and you get the count each month. Every customer is asked the same way, because Google and the FTC both forbid sorting the happy from the unhappy first.</p>
          <div class="sv-price"><b>Quoted</b><span>after one conversation · month to month</span></div>
          <div class="sv-cta"><a href="service-reviews.html" class="tk-btn tk-btn--solid tk-btn--arrow">See the review engine</a><a href="contact.html?want=reviews" class="tk-btn tk-btn--ghost">Ask about reviews</a></div></div>
        <div class="sv-stage">
          <div class="sv-spot" style="right:-40px;top:-40px"></div><div class="rb-float" style="right:-60px;top:-90px">{robot("reviews", I["phone"], label="Reviews", pose="wave")}</div>
          <div class="sv-schem" style="margin-right:70px"><ul class="sv-roster"><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Ask after every finished job</span><b>sent</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">One reminder, then it stops</span><b>sent</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">A reply to every review</span><b>you approve</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">A private line for complaints</span><b>to you</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Monthly count, Google's numbers</span><b>report</b></li></ul></div>
        </div>
      </div>
    </section>

    <section class="sv-scene sv-scene--flip" id="s8" style="--ac:#7CC4F0;--x:30%" aria-labelledby="h-s8">
      <div class="sv-scene__in">
        <div class="sv-scene__copy"><div class="sv-scene__num">08</div><p class="sv-slate">Scene eight</p><h2 id="h-s8">Win back the customers <em>you already had.</em></h2>
          <p class="lede">Most small companies have hundreds of past customers they have not spoken to in a year. The list gets pulled from your own records and cleaned, a short series of messages is written in your voice, it goes out in small batches, and every reply comes straight to you. Nothing bought, nothing scraped, no fake urgency.</p>
          <div class="sv-price"><b>Quoted</b><span>after a read-only look at your list · fixed price in writing</span></div>
          <div class="sv-cta"><a href="service-winback.html" class="tk-btn tk-btn--solid tk-btn--arrow">See how win-back runs</a><a href="contact.html?want=winback" class="tk-btn tk-btn--ghost">Ask about win-back</a></div></div>
        <div class="sv-stage">
          <div class="sv-spot" style="right:-40px;bottom:-30px"></div><div class="rb-float" style="right:-60px;bottom:-30px">{robot("winback", I["inbox"], label="Win-back", pose="wave")}</div>
          <div class="sv-schem" style="margin-right:70px"><ul class="sv-roster"><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Past customers found and merged</span><b>cleaned</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Sorted by how long it has been</span><b>grouped</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Three messages, your voice</span><b>you approve</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Small batches, not a blast</span><b>sent</b></li><li style="grid-template-columns:minmax(0,1fr) auto"><span style="color:#fff">Sent, replied, booked</span><b>report</b></li></ul></div>
        </div>
      </div>
    </section>

    <section class="sv-credits" aria-labelledby="h-credits">
      <p class="sv-slate">How a build runs</p>
      <h2 id="h-credits">The same four steps, <em>every time.</em></h2>
      <ol>
        <li><b>One conversation</b><p>What is stuck, what it costs you now, and what done would look like. About twenty minutes.</p></li>
        <li><b>A price in writing</b><p>What gets built, what it will not do, and the number. Nothing is signed until you have read it.</p></li>
        <li><b>Built in the open</b><p>You see it working on real examples as it comes together. Every script, page and ad goes past you first.</p></li>
        <li><b>Live, and still answered</b><p>Changes are same-day at no charge. The number on this page rings the person who built it.</p></li>
      </ol>
      <table class="sv-menu" aria-label="Every price"><tbody>
        <tr><td>AI employees</td><td>one inside each app, six of them</td><td>from $297/mo · all six ${FULL:,}</td></tr>
        <tr><td>Websites</td><td>coded by hand, yours the day it launches</td><td>$500 · $1,500 · $2,500+</td></tr>
        <tr><td>Ad creation</td><td>ten, twenty-five or sixty finished ads a month</td><td>$697 · $1,297 · $2,497 /mo</td></tr>
        <tr><td>AI SEO</td><td>one agent does it end to end, you approve it</td><td>quoted</td></tr>
        <tr><td>CRM and dashboards</td><td>your CRM cleaned up, your numbers on one screen</td><td>quoted</td></tr>
        <tr><td>Google reviews</td><td>every customer asked, every review answered</td><td>quoted</td></tr>
        <tr><td>Win-back</td><td>past customers, asked back in your voice</td><td>quoted</td></tr>
        <tr><td>Custom systems</td><td>scoped in one conversation, priced in writing</td><td>quoted</td></tr>
      </tbody></table>
      <div class="sv-end"><p class="sv-slate">Not sure which one first</p><p>Calls go unanswered when you are working: start with RING. Web leads sit for hours: INBOX on Gmail, DISPATCH on Jobber. Your site is a theme with your logo dropped in: a Starter site. Running the same ad for months: Growth, twenty-five a month. Or just call and ask.</p><a class="num" href="tel:4807980753">(480) 798-0753</a><a href="mailto:jaden@greenaidigital.com" style="color:{GOLD}">jaden@greenaidigital.com</a></div>
      <p class="ag-tm">{esc(TM)}</p>
    </section>
  </main>
  <div class="sn-sticky"><a href="contact.html" class="tk-btn tk-btn--solid tk-btn--arrow">Talk to us</a></div>''' + tail("""
  <script>
  (function(){
    var imgs=[].slice.call(document.querySelectorAll('#hp-shots img')), url=document.getElementById('hp-url'); if(imgs.length<2||!url) return;
    if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var i=0; setInterval(function(){ imgs[i].classList.remove('on'); i=(i+1)%imgs.length; imgs[i].classList.add('on'); url.textContent=imgs[i].getAttribute('data-url'); }, 3200);
  })();
  </script>""")
# the browser needs the homepage's hp-browser rules
PAGE = PAGE.replace("</style>", """
    .hp-browser { border: 1px solid var(--line); border-radius: 16px; overflow: hidden; background: #fff; }
    .hp-browser__bar { display: flex; align-items: center; gap: .4rem; padding: .55rem .8rem; background: var(--bg-3); border-bottom: 1px solid var(--line); }
    .hp-browser__bar i { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,.25); }
    .hp-browser__url { margin-left: .5rem; font-family: var(--mono); font-size: .72rem; }
    .hp-browser__shots { position: relative; aspect-ratio: 16 / 10; }
    .hp-browser__shots img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: top; opacity: 0; transition: opacity .6s; }
    .hp-browser__shots img.on { opacity: 1; }
  </style>""", 1)
open(os.path.join(ROOT, "services.html"), "w").write(PAGE)
print("wrote services.html", len(PAGE))

#!/usr/bin/env python3
"""build_studio_home.py - writes index.html (Clipcode, formerly GreenAI Digital).
2026-11-01: three services for local service businesses - SEO (get found), ad management (get clicked now),
automation (don't lose them). Run from anywhere: python3 tools/build_studio_home.py
Assets: gai-ads.css, gai-ads.js, reel/{posters,previews}/. Full films stay in art/films and film/."""
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from clipcode_pricing import plans_section
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILMS = [  # slug, title, line, full film
 ('underground','Underground','Neon hoverboard, subway run','art/films/film-dreamscape-01.mp4'),
 ('deep-current','Deep Current','A submarine meets the jaws','art/films/film-dreamscape-04.mp4'),
 ('red-mile','Red Mile','Hoverbike through the canyon','art/films/film-dreamscape-05.mp4'),
 ('firestorm','Firestorm','Standing in the eye of it','art/films/film-dreamscape-06.mp4'),
 ('the-giant','The Giant','Brand film with a green footprint','art/films/film-greenai-giant.mp4'),
 ('the-magnet','The Magnet','Cloud walker, portal opening','art/films/film-magnet-portal.mp4'),
 ('starlight','Starlight','A village that glows at night','art/films/film-starlight-village.mp4'),
 ('every-time','Every. Single. Time.','Our own ad: AI video that looks like this','film/homepage-ad-v2.mp4'),
]
# the white play triangle from the mark, in the mark's own coordinates (see tools/gen_clipcode_brand.py)
PLAY_SVG = '<svg class="cmark__play" viewBox="366 250 524 524" aria-hidden="true" focusable="false"><path d="M575 456L690 523L575 590Z" fill="#fff" stroke="#fff" stroke-width="36" stroke-linejoin="round"/></svg>'

def tiles():
    out = []
    for i,(s,t,l,src) in enumerate(FILMS):
        out.append(f'''<button class="tile rv" style="--d:{(i%4)*.07:.2f}s" data-src="{src}" data-title="{t}" aria-label="Play {t}">
  <img src="reel/posters/{s}.webp" alt="{t}: {l}" width="540" height="960" loading="lazy" decoding="async">
  <video muted loop playsinline preload="none" data-src="reel/previews/{s}.mp4" aria-hidden="true" tabindex="-1"></video>
  <span class="tag">{'Brand film' if s=='every-time' else 'AI concept'} &middot; 9:16</span>
  <span class="play" aria-hidden="true"><svg viewBox="0 0 16 16"><path d="M3.5 2.2v11.6c0 .6.6 1 1.1.7l9.3-5.8c.5-.3.5-1 0-1.3L4.6 1.5c-.5-.3-1.1.1-1.1.7z" fill="#fff"/></svg></span>
  <span class="meta"><b>{t}</b><span>{l}</span></span>
</button>''')
    return '\n'.join(out)

SEO_PARTS = [  # kicker, title, line
 ('Google profile','Fix your Google Business Profile','Right categories, service areas, hours, photos and posts. It is the first thing people see when they search for you.'),
 ('Map pack','Climb into the map top 3','The three businesses under the map get most of the calls. We work on everything Google uses to pick them.'),
 ('Service + city pages','A page for every job, in every city','"AC repair Gilbert." "Pool cleaning Mesa." One real page for each service and town you work in, so you show up where people search.'),
 ('Reviews','A steady stream of reviews','More recent, honest reviews help you rank and help people pick you. Our automation asks every happy customer for one.'),
]
CITY_PAGES = ['AC repair Gilbert','Pool cleaning Mesa','Drain cleaning Chandler','Roof repair Scottsdale','Water heater install Tempe','Pool repair Queen Creek','Furnace tune-up Peoria','Leak detection Phoenix']
TIMELINE = [  # when, what
 ('Week 1-2','Google profile fixed and filled in'),
 ('Month 1','Service + city pages live'),
 ('Month 2-3','Map rankings start to climb'),
 ('Month 4+','It compounds: more calls, no extra spend'),
]

AD_CHANNELS = [  # kicker, title, line, bullets
 ('Google ads','Catch people searching right now','Someone types "AC not cooling" at 2 PM in July. Your ad is at the top with your phone number.',['Search and Local Services ads','Only the towns and jobs you want','Calls and forms tracked to the ad']),
 ('Facebook + Instagram ads','Get seen before they need you','Show up in the feed of homeowners near you, so you are the name they remember when something breaks.',['Seasonal offers and tune-ups','Built from your own photos and jobs','Fresh creative so ads do not go stale']),
]

LANES = [  # kicker, title, line, when, then
 ('After hours','Every lead gets a text back','A lead comes in at 9 PM. They get a friendly text in under a minute, with a link to book.','A form comes in at 9:41 PM','Text back at 9:41, visit booked'),
 ('Missed calls','No call goes unanswered','You are on a roof or under a sink. The caller gets an automatic text and a way to book.','Your phone rings during a job','Text back, follow-up the next morning'),
 ('Follow-up','Quotes that do not go cold','Quiet quotes get a polite nudge on day 2, 5 and 10, then a heads-up to you.','A quote goes quiet','Follow-ups sent, you get a heads-up'),
 ('Reviews','Happy customers asked for a review','When a job is marked done, the customer gets a review ask. More reviews feed your Google ranking.','A job is marked done','Review ask with a link to Google'),
]

TRADES = {  # key: (tab label, [(piece, example), ...])
 'hvac': ('HVAC',[('The page we build','"AC repair Gilbert" and "Furnace tune-up Chandler"'),('The ad that runs','Google ad for "AC not cooling" searches in your towns'),('A lead at 9 PM','Text back in a minute with a booking link'),('After the job','Review ask, and a tune-up reminder next spring')]),
 'pool': ('Pool',[('The page we build','"Pool cleaning Mesa" and "Green pool cleanup Gilbert"'),('The ad that runs','Instagram ad for weekly service before summer'),('A missed call','Text back while you are on a route'),('After the job','Review ask, and a check-in when the season turns')]),
 'plumb': ('Plumbing',[('The page we build','"Water heater install Tempe" and "Drain cleaning Chandler"'),('The ad that runs','Google ad for "burst pipe" and "no hot water" searches'),('A lead at 9 PM','Text back with emergency hours and a booking link'),('After the job','Review ask with a link to Google')]),
 'roof': ('Roofing',[('The page we build','"Roof repair Scottsdale" and "Monsoon roof inspection Mesa"'),('The ad that runs','Facebook ad for free inspections after a storm'),('A quote goes quiet','Follow-up on day 2, 5 and 10'),('After the job','Review ask, and a yearly inspection reminder')]),
}

def cards(rows):
    out=[]
    for i,(k,t,l) in enumerate(rows):
        out.append(f'<article class="lane rv" style="--d:{(i%4)*.06:.2f}s"><span class="lane__k">{k}</span><h3>{t}</h3><p>{l}</p></article>')
    return '\n'.join(out)

def chips():
    return ''.join(f'<span>{c}</span>' for c in CITY_PAGES)

def timeline():
    return ''.join(f'<li class="rv" style="--d:{i*.08:.2f}s"><b>{w}</b><span>{t}</span></li>' for i,(w,t) in enumerate(TIMELINE))

def channels():
    out=[]
    for i,(k,t,l,bul) in enumerate(AD_CHANNELS):
        lis=''.join(f'<li>{b}</li>' for b in bul)
        out.append(f'<article class="chan rv" style="--d:{i*.08:.2f}s"><span class="lane__k">{k}</span><h3>{t}</h3><p>{l}</p><ul>{lis}</ul></article>')
    return '\n'.join(out)

def lanes():
    out=[]
    for i,(k,t,l,w,th) in enumerate(LANES):
        out.append(f'<article class="lane rv" style="--d:{(i%4)*.06:.2f}s"><span class="lane__k">{k}</span><h3>{t}</h3><p>{l}</p>'
                   f'<div class="flow"><div><small>When</small>{w}</div><i aria-hidden="true"></i><div class="then"><small>Then</small>{th}</div></div></article>')
    return '\n'.join(out)

def ind_tabs():
    return ''.join(f'<button role="tab" aria-selected="{"true" if i==0 else "false"}" aria-controls="ind-{k}" id="tab-{k}" data-ind="{k}">{v[0]}</button>' for i,(k,v) in enumerate(TRADES.items()))

def ind_panels():
    out=[]
    for i,(k,(lab,rows)) in enumerate(TRADES.items()):
        items=''.join(f'<li><span class="w">{w}</span><span class="ar" aria-hidden="true"></span><span class="t">{t}</span></li>' for w,t in rows)
        out.append(f'<ol class="recipes" role="tabpanel" id="ind-{k}" aria-labelledby="tab-{k}"{"" if i==0 else " hidden"}>{items}</ol>')
    return ''.join(out)

JSONLD = json.dumps({
 "@context":"https://schema.org","@type":"ProfessionalService","name":"Clipcode","alternateName":"GreenAI Digital","url":"https://greenaidigital.com/",
 "telephone":"+1-480-798-0753","email":"jaden@greenaidigital.com",
 "address":{"@type":"PostalAddress","addressLocality":"Gilbert","addressRegion":"AZ","postalCode":"85296","addressCountry":"US"},
 "areaServed":"Phoenix metro, Arizona",
 "sameAs":["https://www.instagram.com/clipcode.ai/","https://www.instagram.com/poolprime.ai/"],
 "description":"Clipcode (formerly GreenAI Digital) helps local service businesses in the Phoenix area get found, get clicked and never lose a lead: local SEO and Google Business Profile work, Google and Facebook/Instagram ad management, and automations that text back every lead, follow up missed calls and ask for reviews.",
 "makesOffer":[{"@type":"Offer","name":"Local SEO: Google Business Profile, map rankings, service and city pages, reviews","price":"1097","priceCurrency":"USD"},{"@type":"Offer","name":"Ad management: Google ads and Facebook/Instagram ads","price":"897","priceCurrency":"USD"},{"@type":"Offer","name":"Automation: instant lead text-back, missed-call follow-up, quote follow-up, review requests","price":"347","priceCurrency":"USD"}]
}, indent=2)

HTML = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Clipcode | Get found. Get clicked. Never lose a lead.</title>
<meta name="description" content="Clipcode helps Phoenix-area service businesses grow: local SEO and Google map rankings, Google and Facebook ad management, and automations that text back every lead in under a minute. Start with a free growth check.">
<link rel="canonical" href="https://greenaidigital.com/">
<meta name="theme-color" content="#070B1E">
<meta property="og:type" content="website">
<meta property="og:title" content="Clipcode | Get found. Get clicked. Never lose a lead.">
<meta property="og:description" content="SEO that compounds, ads that bring calls now, and automation that answers every lead in under a minute.">
<meta property="og:url" content="https://greenaidigital.com/">
<meta property="og:image" content="https://greenaidigital.com/assets/brand/clipcode-og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="assets/brand/clipcode-favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="assets/brand/clipcode-apple-touch-icon.png">
<link rel="preload" href="assets/fonts/Montserrat-Variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="gai-ads.css?v=7">
<script type="application/ld+json">{JSONLD}</script>
<script>document.documentElement.classList.add('js')</script>
</head>
<body>
<div class="progress" id="progress" aria-hidden="true"></div>
<div class="cursor" id="cursor" aria-hidden="true">PLAY</div>
<a class="skip" href="#main">Skip to content</a>

<header class="nav" id="nav">
  <div class="wrap nav__in">
    <a class="brand" href="#top" aria-label="Clipcode, back to top"><img src="assets/brand/clipcode-wordmark.svg" alt="clipcode.ai" width="129" height="30"></a>
    <nav class="links" id="links" aria-label="Sections">
      <a href="#seo">SEO</a><a href="#ads">Ads</a><a href="#automations">Automation</a><a href="#plans">Pricing</a><a href="#trades">Your trade</a><a href="#contact">Contact</a>
    </nav>
    <a class="btn btn--go nav__cta" href="#contact" data-plan="check">Free growth check</a>
    <button class="burger" id="burger" aria-expanded="false" aria-controls="links" aria-label="Menu"><span></span><span></span></button>
  </div>
</header>

<main id="main">

<section class="hero is-auto" id="top">
  <div class="wrap hero__grid">
    <div>
      <span class="kicker rise" style="--d:.15s">SEO &middot; Ads &middot; Automation &middot; Gilbert, Arizona</span>
      <h1 class="rise" style="--d:.3s">Get found. Get clicked. <span class="sp">Never lose a lead.</span></h1>
      <p class="lede rise" style="--d:.5s">We help local service businesses grow three ways: SEO so customers find you on Google, ads so the phone rings this week, and automation so every lead gets an answer in under a minute.</p>
      <div class="hero__cta rise" style="--d:.7s">
        <a class="btn btn--go btn--lg" href="#contact" data-plan="check">Get a free growth check <span class="arrow">&rarr;</span></a>
        <a class="btn btn--ghost btn--lg" href="#services">See the three services</a>
      </div>
      <p class="hero__note rise" style="--d:.9s">Set up by a real person. You keep your Google and ad accounts.</p>
    </div>
    <div class="stage">
      <div class="cmark rise" style="--d:.35s">
        <img class="cmark__art" src="assets/brand/clipcode-mark.svg" alt="" width="524" height="524" decoding="async">
        <button class="cmark__screen" id="watch8" data-src="film/homepage-ad-v2.mp4" data-title="Every. Single. Time." aria-label="Play our brand film, Every. Single. Time. Made with AI.">
          <img src="reel/posters/every-time.webp" alt="" width="540" height="960" decoding="async">
          <video muted loop playsinline preload="none" data-src="reel/previews/every-time.mp4" aria-hidden="true" tabindex="-1"></video>
        </button>
        {PLAY_SVG}
      </div>
      <p class="stage__cap rise" style="--d:1s">Our own brand film, made with AI. Tap the screen to watch.</p>
    <div class="board rise" style="--d:.75s" aria-label="Example of one evening with all three services running">
      <div class="board__top"><b>One evening, all three working</b><span class="live">Running</span></div>
      <ol class="board__feed" id="feed">
        <li><time>6:12 PM</time><span><b>Map search</b> "AC repair Gilbert" finds you</span></li>
        <li><time>7:30 PM</time><span><b>Google ad</b> click, form filled out</span></li>
        <li><time>7:30 PM</time><span><b>Text back</b> sent in 40 seconds</span></li>
        <li><time>8:05 PM</time><span><b>Missed call</b> texted back, visit booked</span></li>
        <li><time>9:42 PM</time><span><b>Job done</b> review ask sent to Maria R.</span></li>
        <li><time>10:15 PM</time><span><b>New 5-star review</b> on your Google profile</span></li>
      </ol>
      <p class="board__fine">Example of a typical evening. Names and numbers are made up.</p>
    </div>
    </div>
  </div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee__in">
  <span>Google profile</span><span>Map top 3</span><span>City pages</span><span>Reviews</span><span>Google ads</span><span>Instagram ads</span><span>Text back</span><span>Missed calls</span><span>Follow-up</span>
  <span>Google profile</span><span>Map top 3</span><span>City pages</span><span>Reviews</span><span>Google ads</span><span>Instagram ads</span><span>Text back</span><span>Missed calls</span><span>Follow-up</span>
</div></div>

<section class="sec" id="services">
  <a class="anchor" id="about"></a><a class="anchor" id="how"></a>
  <div class="wrap">
    <div class="sechead sechead--row">
      <div><span class="kicker rv">The plan</span><h2 class="rv" style="--d:.05s">Three services. <span class="sp">One growth system.</span></h2></div>
      <p class="lede rv" style="--d:.1s">Each one fixes a different leak. Together, ads pay the bills while SEO warms up, and automation makes sure no click is wasted.</p>
    </div>
    <ol class="trio">
      <li class="trio__i is-seo rv"><a href="#seo"><span class="trio__n">01 &middot; SEO</span><h3>Get found</h3><p>Google profile, map top 3, a page for every service and city, and more reviews.</p><span class="trio__t">Slow to build, then it compounds</span><span class="trio__p">from $1,097/mo</span></a></li>
      <li class="trio__i is-ads rv" style="--d:.08s"><a href="#ads"><span class="trio__n">02 &middot; Ads</span><h3>Get clicked now</h3><p>Google and Facebook/Instagram ads for businesses that cannot wait for SEO.</p><span class="trio__t">Calls this week</span><span class="trio__p">from $897/mo + ad spend</span></a></li>
      <li class="trio__i is-auto rv" style="--d:.16s"><a href="#automations"><span class="trio__n">03 &middot; Automation</span><h3>Don't lose them</h3><p>Instant text back, missed-call follow-up and review asks, day or night.</p><span class="trio__t">Answered in under a minute</span><span class="trio__p">from $347/mo</span></a></li>
    </ol>
  </div>
</section>

<section class="sec is-seo" id="seo">
  <div class="wrap">
    <div class="sechead sechead--row">
      <div><span class="kicker rv">01 &middot; SEO</span><h2 class="rv" style="--d:.05s">Get found <span class="sp">on Google.</span></h2></div>
      <p class="lede rv" style="--d:.1s">When someone searches "AC repair near me", most calls go to the three businesses under the map. We work to put you there, and keep you there.</p>
    </div>
    <div class="lanes">
{cards(SEO_PARTS)}
    </div>
    <div class="seo2">
      <div class="chips rv"><b>Pages we build, one per service and city</b><div class="chips__in">{chips()}</div></div>
      <div class="tline rv"><b>Slow to build. Then it compounds.</b><ol>{timeline()}</ol><p class="m">A typical path, not a promise. Nobody can honestly guarantee a ranking, and we never will.</p></div>
    </div>
  </div>
</section>

<div class="fold" aria-hidden="true"></div>

<section class="sec is-ads" id="ads">
  <a class="anchor" id="reel"></a><a class="anchor" id="selected-work"></a><a class="anchor" id="ai-ads"></a>
  <div class="wrap">
    <div class="sechead sechead--row">
      <div><span class="kicker rv">02 &middot; Ad management</span><h2 class="rv" style="--d:.05s">Get clicked <span class="sp">now.</span></h2></div>
      <p class="lede rv" style="--d:.1s">SEO takes weeks to months. Ads bring calls this week. We build and run your Google and Facebook/Instagram campaigns while your SEO warms up.</p>
    </div>
    <div class="chans">
{channels()}
    </div>
    <div class="money rv">
      <div><b>You pay the ad platform.</b><span>Your ad budget goes straight to Google and Meta, on your own card.</span></div>
      <div><b>We charge a flat management fee.</b><span>For building, running and improving the campaigns. No markup on your spend.</span></div>
      <div><b>You own the accounts.</b><span>If you ever leave, your ads, data and history stay with you.</span></div>
    </div>
    <div class="sechead sechead--row reelhead">
      <div><h3 class="rv">And the ads look <span class="sp">like this.</span></h3></div>
      <p class="m rv">We make the creative too. Eight concept films we made with AI. Tap one to watch it with sound.</p>
    </div>
    <div class="reel">
{tiles()}
    </div>
    <p class="reel__note rv">Concept films made with AI, not client results. Your ads are built from your business: your trucks, your crew, your jobs.</p>
  </div>
</section>

<div class="fold fold--even" aria-hidden="true"></div>

<section class="sec is-auto" id="automations">
  <a class="anchor" id="employees"></a>
  <div class="wrap">
    <div class="sechead sechead--row">
      <div><span class="kicker rv">03 &middot; Automation</span><h2 class="rv" style="--d:.05s">Don't lose them. <span class="sp">Answer in a minute.</span></h2></div>
      <p class="lede rv" style="--d:.1s">This is what makes the other two worth paying for. Clicks are wasted money if nobody answers in the first 5 minutes, and most leads go to whoever replies first.</p>
    </div>
    <div class="fivemin rv"><span class="fivemin__n">5<small>min</small></span><p>The window that matters. After that, the lead has usually called someone else. Our automations answer in under one.</p></div>
    <div class="lanes">
{lanes()}
    </div>
    <p class="loopnote rv">Every review ask feeds your SEO. More reviews, better map rankings, more calls. That is how the three services work as one.</p>
  </div>
</section>

{plans_section()}

<section class="sec" id="trades">
  <a class="anchor" id="industries"></a>
  <div class="wrap ind">
    <div>
      <span class="kicker rv">Built for home services</span>
      <h2 class="rv" style="--d:.05s">What it looks like <span class="sp">for your trade.</span></h2>
      <p class="m rv">HVAC, pool, plumbing, roofing and other service businesses in the Phoenix area. Pick yours to see all three services at work.</p>
      <div class="tabs rv" role="tablist" aria-label="Type of business">{ind_tabs()}</div>
    </div>
    <div class="recipebox rv">
      <div class="recipebox__top"><span>The piece</span><span>What it looks like</span></div>
      {ind_panels()}
      <a class="btn btn--ghost" href="#contact" data-plan="check">Check mine for free <span class="arrow">&rarr;</span></a>
    </div>
  </div>
</section>

<section class="sec is-ads" id="verticals">
  <div class="wrap">
    <div class="verts verts--one">
      <a class="pp rv" href="poolprime/">
        <div><span class="tag">For pool builders &middot; Live</span><h3>PoolPrime<em>.ai</em><br>Our studio for pool companies</h3><p>Reveal videos, night-glow reels, instant lead replies and quote follow-up, made for pool builders.</p><span class="btn btn--go">See PoolPrime <span class="arrow">&rarr;</span></span></div>
        <div class="logo"><img src="assets/brand/poolprime-logo.png" alt="PoolPrime.ai water P logo" width="220" height="220" loading="lazy"></div>
      </a>
    </div>
  </div>
</section>


<section class="sec cta is-auto" id="contact">
  <div class="wrap cta__in">
    <div>
      <span class="kicker rv">Your turn</span>
      <h2 class="rv" style="--d:.05s">Let's get your phone <span class="sp">ringing.</span></h2>
      <p class="lede rv" style="--d:.1s">Tell us about your business and the towns you work in. We send back your free growth check: where you show up today, and what to fix first. A real person reads every request.</p>
      <a class="dm rv" style="--d:.15s" href="https://www.instagram.com/clipcode.ai/" target="_blank" rel="noopener"><b>DM AD</b><span>Rather use Instagram?<br>Message @clipcode.ai</span></a>
      <div class="who rv"><span>Jaden Green &middot; Gilbert, Arizona</span><a href="mailto:jaden@greenaidigital.com">jaden@greenaidigital.com</a><a href="tel:+14807980753">(480) 798-0753</a></div>
    </div>
    <form class="rv" id="form" action="https://greenai-forms-production.up.railway.app/api/submit" method="POST" novalidate aria-label="Free growth check request" data-form="greenai-sample" data-source="greenaidigital.com">
      <input type="checkbox" name="botcheck" style="display:none" tabindex="-1" autocomplete="off">
      <div class="row"><label>Your name *<input name="name" required autocomplete="name" placeholder="Alex Rivera"></label><label>Business *<input name="business" required autocomplete="organization" placeholder="Desert Blue Pools"></label></div>
      <div class="row"><label>Email *<input type="email" name="email" required autocomplete="email" placeholder="you@company.com"></label><label>Phone<input type="tel" name="phone" autocomplete="tel" placeholder="(480) 555-0100"></label></div>
      <label>Website or Instagram<input name="website" placeholder="yourbusiness.com or @yourbusiness"></label>
      <label>What would you like?<select name="interest" id="interest">
        <option value="check">A free growth check</option><optgroup label="SEO"><option value="seo-starter">SEO: Local Starter, $1,097/mo</option><option value="seo-leader">SEO: Market Leader, $1,797/mo</option><option value="seo-valley">SEO: Valley Dominator, $2,997/mo</option></optgroup><optgroup label="Ads"><option value="ads-launch">Ads: Launch, $897/mo</option><option value="ads-growth">Ads: Growth, $1,497/mo</option><option value="ads-scale">Ads: Scale, $2,497/mo</option></optgroup><optgroup label="Automation"><option value="auto-single">Automation: Single, $347/mo</option><option value="auto-front">Automation: Front Office, $697/mo</option><option value="auto-autopilot">Automation: Autopilot, $1,197/mo</option></optgroup><option value="all">Full System, all three, $3,297/mo</option>
        <option value="pool">I run a pool company (PoolPrime)</option><option value="other">Something else</option></select></label>
      <label>Anything we should know?<textarea name="message" id="message" placeholder="What you do, the towns you serve, and where your leads come from today."></textarea></label>
      <button class="btn btn--go btn--lg" type="submit" id="send">Send my request <span class="arrow">&rarr;</span></button>
      <p class="err" id="err" role="alert"></p>
      <p class="fine" style="margin:0">We use your details only to reply to this request.</p>
      <div class="ok" role="status"><h3>We got it.</h3><p class="lede" style="margin:0 auto">Watch your email. We will be in touch with your free growth check.</p></div>
    </form>
  </div>
</section>

<section class="sec is-auto" id="faq" style="padding-top:clamp(40px,6vw,80px)">
  <div class="wrap faq">
    <div class="sechead"><span class="kicker rv">Straight answers</span><h2 class="rv" style="--d:.05s">Before you <span class="sp">ask.</span></h2></div>
    <details><summary>Which service should I start with?</summary><p>If you need calls this month, start with ads plus automation. If you can wait, SEO is the cheapest long-term source of calls. The free growth check tells you which one fits your business.</p></details>
    <details><summary>How long does SEO take?</summary><p>Weeks to months. Fixing your Google profile shows up fastest. Map rankings and city pages build over two to four months, and then they keep bringing calls without more ad spend. Nobody can honestly guarantee a ranking.</p></details>
    <details><summary>How much does SEO cost?</summary><p>Local Starter is $1,097 a month for one city. Market Leader is $1,797 for up to five cities, and Valley Dominator is $2,997 for the whole Phoenix metro. No setup fee, month to month.</p></details>
    <details><summary>How does ad management pricing work?</summary><p>You pay Google and Meta directly for the ads, on your own card. We charge a flat monthly fee: $897 for one platform, $1,497 for Google plus Facebook/Instagram, or $2,497 to scale, plus a one-time $797 launch. Premium AI ad creative is included.</p></details>
    <details><summary>Why do I need automation if I already run ads?</summary><p>Because most leads go to whoever answers first. A lead that comes in at 9 PM and waits until morning has usually booked someone else. Automation texts them back in under a minute, follows up missed calls, and asks happy customers for reviews.</p></details>
    <details><summary>How much does automation cost?</summary><p>One automation is $697 to build and $347 a month. Front Office, three working together, is $1,497 and $697 a month. Autopilot, up to eight, is $2,997 and $1,197 a month. The build price is fixed in writing before any work starts.</p></details>
    <details><summary>Is there a discount for all three?</summary><p>Yes. The Full System (SEO Market Leader, Ads Growth and Automation Front Office) is $3,297 a month instead of $3,991, with a $997 setup instead of $2,294.</p></details>
    <details><summary>Why do you cost more than some agencies?</summary><p>Most local agencies charge around $1,000 a month for SEO and $500 to $1,500 to run ads. We sit just above that because premium AI ad creative is included, you talk to the people doing the work, you own every account, and there is no long contract.</p></details>
    <details><summary>Do I have to switch software?</summary><p>No. We work with your Google profile, your website, your phone and the apps you already use. If something cannot connect, we tell you before you pay.</p></details>
    <details><summary>Will the texts sound like a robot?</summary><p>Messages are written in your voice and you approve them before anything goes live. Anything unusual gets passed to you instead of guessed at.</p></details>
    <details><summary>Do I own my accounts?</summary><p>Yes. Your Google Business Profile, ad accounts and website stay in your name. If you ever leave, everything stays with you.</p></details>
    <details><summary>Who is behind Clipcode?</summary><p>Jaden Green, in Gilbert, Arizona. Clipcode used to be called GreenAI Digital; same team, same email, new name. You deal with a real person you can email or call.</p></details>
    <details><summary>Do you only work in Phoenix?</summary><p>Phoenix-area businesses come first: Gilbert, Mesa, Chandler, Tempe, Scottsdale, Queen Creek and the rest of the Valley. Businesses elsewhere can still send a request.</p></details>
  </div>
</section>
</main>

<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Film player">
  <button class="lb__nav lb__prev" id="lbPrev" aria-label="Previous film">&#8249;</button>
  <div class="lb__box"><div class="lb__bar"><b id="lbTitle"></b></div><video id="lbVideo" playsinline controls></video></div>
  <button class="lb__nav lb__next" id="lbNext" aria-label="Next film">&#8250;</button>
  <button class="lb__x" id="lbX" aria-label="Close">&times;</button>
</div>

<footer>
  <div class="wrap foot">
    <div class="l"><a class="brand" href="#top" aria-label="Clipcode, back to top"><img src="assets/brand/clipcode-wordmark.svg" alt="clipcode.ai" width="129" height="30"></a><a href="#seo">SEO</a><a href="#ads">Ads</a><a href="#automations">Automation</a><a href="poolprime/">PoolPrime.ai</a><a href="https://www.instagram.com/clipcode.ai/" target="_blank" rel="noopener">Instagram</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a></div>
    <div>&copy; <span id="yr">2026</span> Clipcode (formerly GreenAI Digital) &middot; Jaden Green, Gilbert, Arizona</div>
  </div>
</footer>
<script src="gai-ads.js?v=7"></script>
</body>
</html>
'''
open(os.path.join(ROOT,'index.html'),'w').write(HTML)
print('index.html written', len(HTML),'bytes')

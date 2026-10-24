#!/usr/bin/env python3
"""build_studio_home.py - writes index.html (Clipcode, formerly GreenAI Digital: automations for business + premium AI ads).
Run from anywhere: python3 tools/build_studio_home.py
Assets: gai-ads.css, gai-ads.js, reel/{posters,previews,frames}/. Full films stay in art/films and film/."""
import os, json
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
WALL = ['underground','deep-current','red-mile','firestorm','the-giant','the-magnet','starlight','every-time','bloom']

def wall():
    cols = []
    for c in range(7):
        seq = WALL[c*2 % 9:] + WALL[:c*2 % 9]
        imgs = ''.join(f'<img src="reel/posters/{s}.webp" alt="" width="540" height="960" decoding="async">' for s in seq*2)
        cols.append(f'<div class="col" aria-hidden="true">{imgs}</div>')
    return ''.join(cols)

def tiles():
    out = []
    for i,(s,t,l,src) in enumerate(FILMS):
        out.append(f'''<button class="tile rv" style="--d:{(i%4)*.07:.2f}s" data-src="{src}" data-title="{t}" aria-label="Play {t}">
  <img src="reel/posters/{s}.webp" alt="{t}: {l}" width="540" height="960" loading="lazy" decoding="async">
  <video muted loop playsinline preload="none" data-src="reel/previews/{s}.mp4" aria-hidden="true" tabindex="-1"></video>
  <span class="tag">{'Brand film' if s=='every-time' else 'AI concept'} &middot; 9:16</span>
  <span class="play" aria-hidden="true"><svg viewBox="0 0 16 16"><path d="M3 1.5v13l11-6.5z" fill="#000"/></svg></span>
  <span class="meta"><b>{t}</b><span>{l}</span></span>
</button>''')
    return '\n'.join(out)

def frames():
    d = 19.0; out = []
    for i in range(8):
        t = 0.6 + i*(d-1.4)/7
        out.append(f'<figure><img src="reel/frames/ug-{i+1}.webp" alt="Storyboard frame {i+1} of Underground" width="300" height="533" loading="lazy" decoding="async"><figcaption>00:{int(t):02d}</figcaption></figure>')
    return ''.join(out)

LANES = [  # kicker, title, line, when, then
 ('Leads','Every lead answered','Forms, calls, texts and DMs get a friendly reply in about a minute, day or night.','A lead fills out your form at 9:41 PM','Reply at 9:42, with a link to book'),
 ('Front desk','Missed calls, caught','When nobody can pick up, the caller gets a text back and a way to book.','Your phone rings during a job','Text back, job booked on the calendar'),
 ('Follow-up','Quotes that close','Quiet quotes get a nudge on day 2, 5 and 10 until the customer says yes or no.','A quote goes quiet','Polite follow-ups, then a heads-up to you'),
 ('Scheduling','A calendar that fills itself','Bookings land on your calendar, reminders go out, no-shows get a rebook text.','A customer books online','Confirmed, reminded the day before'),
 ('Reviews','Reviews and repeat work','After the job, happy customers get a review ask. Past customers hear from you when it is time again.','A job is marked done','Review ask sent, follow-up set for next season'),
 ('Back office','Paperwork off your plate','Invoices, payment reminders, reports and data entry between your apps.','An invoice is 7 days late','Friendly reminder, logged in your books'),
 ('Inbox and team','An inbox that sorts itself','Email sorted and drafted, a daily summary to your team chat, nothing lost in threads.','40 emails arrive overnight','Sorted, drafts ready, summary by 7 AM'),
 ('Search','Found by AI assistants','More people ask an AI who to hire. We set you up so it can find and name you.','Someone asks an AI for a roofer near Gilbert','Your business is on the list'),
]

INDUSTRIES = {  # key: (tab label, [(when, then), ...])
 'home': ('Home services',[('A call is missed during a job','Text back in a minute, visit booked'),('A quote is sent','Follow-up on day 2, 5 and 10'),('The job is marked done','Review ask with a link to Google'),('Summer is coming',"Tune-up reminder to last year's customers")]),
 'shop': ('Shops and online stores',[('A cart is left behind','Reminder with the item, an hour later'),('An order ships','Tracking text to the customer'),('Stock runs low','Reorder alert to you'),('A DM asks a question','Instant answer from your own catalog')]),
 'clinic': ('Clinics and wellness',[('An appointment is booked','Reminders 24 hours and 2 hours before'),('Someone no-shows','Rebook text the same day'),('A new client books','Intake forms sent before the visit'),('A visit ends','Thank-you and review ask')]),
 'office': ('Offices and pros',[('A new inquiry comes in','Intake questions and a calendar link'),('A document is missing','Polite chase until it arrives'),('An invoice is overdue','Reminders, then a note to you'),('It is Monday morning',"Last week's numbers in your inbox")]),
}

TOOLS = ['Gmail','Outlook','Google Calendar','QuickBooks','Stripe','Square','Slack','Microsoft Teams','Jobber','Housecall Pro','Shopify','HubSpot','Google Sheets','Your website forms','Instagram DMs','Text messages']

def lanes():
    out=[]
    for i,(k,t,l,w,th) in enumerate(LANES):
        out.append(f'<article class="lane rv" style="--d:{(i%4)*.06:.2f}s"><span class="lane__k">{k}</span><h3>{t}</h3><p>{l}</p>'
                   f'<div class="flow"><div><small>When</small>{w}</div><i aria-hidden="true"></i><div class="then"><small>Then</small>{th}</div></div></article>')
    return '\n'.join(out)

def ind_tabs():
    return ''.join(f'<button role="tab" aria-selected="{"true" if i==0 else "false"}" aria-controls="ind-{k}" id="tab-{k}" data-ind="{k}">{v[0]}</button>' for i,(k,v) in enumerate(INDUSTRIES.items()))

def ind_panels():
    out=[]
    for i,(k,(lab,rows)) in enumerate(INDUSTRIES.items()):
        items=''.join(f'<li><span class="w">{w}</span><span class="ar" aria-hidden="true">&rarr;</span><span class="t">{t}</span></li>' for w,t in rows)
        out.append(f'<ol class="recipes" role="tabpanel" id="ind-{k}" aria-labelledby="tab-{k}"{"" if i==0 else " hidden"}>{items}</ol>')
    return ''.join(out)

def tools():
    return ''.join(f'<span>{t}</span>' for t in TOOLS)

JSONLD = json.dumps({
 "@context":"https://schema.org","@type":"ProfessionalService","name":"Clipcode","alternateName":"GreenAI Digital","url":"https://greenaidigital.com/",
 "telephone":"+1-480-798-0753","email":"jaden@greenaidigital.com",
 "address":{"@type":"PostalAddress","addressLocality":"Gilbert","addressRegion":"AZ","postalCode":"85296","addressCountry":"US"},
 "areaServed":"Phoenix metro, Arizona",
 "sameAs":["https://www.instagram.com/greenaidigitals/","https://www.instagram.com/poolprime.ai/"],
 "description":"Clipcode (formerly GreenAI Digital) is an automation center in Gilbert, Arizona. We automate lead replies, missed calls, follow-up, scheduling, reviews, back office work and AI search visibility for businesses, and we make premium AI video and image ads. PoolPrime.ai is our dedicated studio for pool builders.",
 "makesOffer":[{"@type":"Offer","name":"Business automation: lead replies, missed calls, follow-up, scheduling, reviews, back office"},{"@type":"Offer","name":"AI video and image ads"},{"@type":"Offer","name":"Instant lead replies and quote follow-up"},{"@type":"Offer","name":"AI search visibility"},{"@type":"Offer","name":"PoolPrime.ai ads for pool builders","url":"https://greenaidigital.com/poolprime/"}]
}, indent=2)

HTML = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Clipcode | Automations for your business. Premium AI ads.</title>
<meta name="description" content="Clipcode (formerly GreenAI Digital) is an automation center in Gilbert, Arizona. We automate lead replies, missed calls, follow-up, scheduling, reviews and back office work, and we make premium AI ads. Start with a free automation map or a free sample ad.">
<link rel="canonical" href="https://greenaidigital.com/">
<meta name="theme-color" content="#05050a">
<meta property="og:type" content="website">
<meta property="og:title" content="Clipcode | Automations for your business. Premium AI ads.">
<meta property="og:description" content="We automate the busywork that slows a business down, and we make AI ads that bring the customers in. Start free.">
<meta property="og:url" content="https://greenaidigital.com/">
<meta property="og:image" content="https://greenaidigital.com/assets/brand/clipcode-og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="assets/brand/clipcode-favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="assets/brand/clipcode-apple-touch-icon.png">
<link rel="preload" href="poolprime/assets/fonts/Outfit.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="gai-ads.css?v=3">
<script type="application/ld+json">{JSONLD}</script>
<script>document.documentElement.classList.add('js')</script>
</head>
<body>
<div class="progress" id="progress" aria-hidden="true"></div>
<div class="cursor" id="cursor" aria-hidden="true">PLAY</div>
<a class="skip" href="#main">Skip to content</a>

<header class="nav" id="nav">
  <div class="wrap nav__in">
    <a class="brand" href="#top" aria-label="Clipcode, back to top"><img class="brand__mark" src="assets/brand/clipcode-mark.svg" alt="" width="30" height="30"><span>Clip<i>code</i></span></a>
    <nav class="links" id="links" aria-label="Sections">
      <a href="#automations">Automations</a><a href="#industries">Industries</a><a href="#how">How it works</a><a href="#reel">AI ads</a><a href="#plans">Plans</a><a href="#contact">Contact</a>
    </nav>
    <a class="btn btn--volt nav__cta" href="#contact" data-plan="map" style="padding:.6rem 1.1rem;font-size:.92rem">Free automation map</a>
    <button class="burger" id="burger" aria-expanded="false" aria-controls="links" aria-label="Menu"><span></span><span></span></button>
  </div>
</header>

<main id="main">

<section class="hero hero--auto" id="top">
  <div class="wall" aria-hidden="true"><div class="wall__in">{wall()}</div></div>
  <div class="wrap hero__grid">
    <div>
      <span class="kicker rise" style="--d:.2s">Automations + premium AI ads &middot; Gilbert, Arizona</span>
      <h1 class="rise" style="--d:.4s">Your business, <span class="sp">on autopilot.</span></h1>
      <p class="lede rise" style="--d:.7s">We automate the jobs that eat your day: answering leads, catching missed calls, following up quotes, booking, reviews and paperwork. And we make the premium AI ads that bring the customers in.</p>
      <div class="hero__cta rise" style="--d:.95s">
        <a class="btn btn--volt btn--lg" href="#contact" data-plan="map">Get a free automation map <span class="arrow">&rarr;</span></a>
        <a class="btn btn--ghost btn--lg" href="#automations">See what we automate</a>
      </div>
      <p class="hero__note rise" style="--d:1.2s">Set up by a real person. Works with the apps you already use.</p>
    </div>
    <div class="board rise" style="--d:.8s" aria-label="Example of automations running in one evening">
      <div class="board__top"><b>Tonight, while you're off</b><span class="live">Running</span></div>
      <ol class="board__feed" id="feed">
        <li><time>6:12 PM</time><span><b>Missed call</b> texted back, visit booked for Tue 8 AM</span></li>
        <li><time>7:30 PM</time><span><b>Quote #418</b> day-2 follow-up sent</span></li>
        <li><time>8:05 PM</time><span><b>Job done</b> review ask sent to Maria R.</span></li>
        <li><time>9:42 PM</time><span><b>New lead</b> from Instagram answered in 1 min</span></li>
        <li><time>11:00 PM</time><span><b>Invoice #1042</b> paid, logged in the books</span></li>
        <li><time>7:00 AM</time><span><b>Morning summary</b> sent to your phone</span></li>
      </ol>
      <p class="board__fine">Example of a typical night. Names and numbers are made up.</p>
    </div>
  </div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee__in">
  <span>Lead replies</span><span>Missed calls</span><span>Quote follow-up</span><span>Booking</span><span>Reviews</span><span>Invoices</span><span>Inbox</span><span>AI search</span><span>AI ads</span>
  <span>Lead replies</span><span>Missed calls</span><span>Quote follow-up</span><span>Booking</span><span>Reviews</span><span>Invoices</span><span>Inbox</span><span>AI search</span><span>AI ads</span>
</div></div>

<section class="sec" id="automations">
  <a class="anchor" id="services"></a><a class="anchor" id="employees"></a>
  <div class="wrap">
    <div class="sechead sechead--row">
      <div><span class="kicker rv">01 &middot; What we automate</span><h2 class="rv" style="--d:.05s;margin-top:1.2rem">Eight jobs you can <span class="sp">stop doing.</span></h2></div>
      <p class="lede rv" style="--d:.1s">Every automation is the same idea: when something happens in your business, the right thing happens next, without you. Pick one or run them all.</p>
    </div>
    <div class="lanes">
{lanes()}
    </div>
  </div>
</section>

<section class="sec" id="industries" style="background:linear-gradient(180deg,transparent,rgba(39,217,255,.05),transparent)">
  <div class="wrap ind">
    <div>
      <span class="kicker rv">02 &middot; Built around your business</span>
      <h2 class="rv" style="--d:.05s;margin:1.2rem 0 1.4rem">Different business, <span class="sp">different autopilot.</span></h2>
      <p class="m rv">A roofer, a shop and a clinic lose time in different places. Pick yours to see the first four things we would automate.</p>
      <div class="tabs rv" role="tablist" aria-label="Type of business">{ind_tabs()}</div>
    </div>
    <div class="recipebox rv">
      <div class="recipebox__top"><span>When this happens</span><span>We do this</span></div>
      {ind_panels()}
      <a class="btn btn--ghost" href="#contact" data-plan="map" style="margin-top:1.4rem">Map mine for free <span class="arrow">&rarr;</span></a>
    </div>
  </div>
</section>

<section class="sec" id="how">
  <a class="anchor" id="about"></a>
  <div class="wrap">
    <div class="sechead sechead--row">
      <div><span class="kicker rv">03 &middot; How it works</span><h2 class="rv" style="--d:.05s;margin-top:1.2rem">Three ways <span class="sp">to work with us.</span></h2></div>
      <p class="lede rv" style="--d:.1s">Start small, see it work, then add more. You always know what runs and who to call.</p>
    </div>
    <div class="ways">
      <div class="way rv"><span class="way__n">Start here</span><h3>Free automation map</h3><p>A short call about your day. You get back a plain list of the three jobs worth automating first, and what each would save you.</p><span class="way__p">$0</span></div>
      <div class="way rv" style="--d:.08s"><span class="way__n">Then</span><h3>We build it</h3><p>We set it up inside the apps you already use, test it with you, and switch it on. Fixed price agreed before we start.</p><span class="way__p">Quoted up front</span></div>
      <div class="way rv" style="--d:.16s"><span class="way__n">Ongoing</span><h3>We run it</h3><p>We watch it, tune it and add to it as you grow. One monthly price, cancel anytime.</p><span class="way__p">Monthly</span></div>
    </div>
    <div class="toolstrip rv"><b>Works with tools like</b><div class="toolstrip__in">{tools()}</div></div>
  </div>
</section>

<section class="sec" id="reel">
  <a class="anchor" id="ads"></a><a class="anchor" id="selected-work"></a><a class="anchor" id="ai-ads"></a>
  <div class="wrap">
    <div class="sechead sechead--row">
      <div><span class="kicker rv">04 &middot; Premium AI ads</span><h2 class="rv" style="--d:.05s;margin-top:1.2rem">Premium AI ads. <span class="sp">Made to stop the scroll.</span></h2></div>
      <p class="lede rv" style="--d:.1s">Automation handles every lead. Our ads bring more of them. Eight concept films we made to push what an AI ad can look like. Tap one to watch it with sound.</p>
    </div>
    <div class="reel">
{tiles()}
    </div>
    <p class="reel__note rv">Concept films made with AI, not client results. Yours is built from your business: your pools, roofs, trucks and crew.</p>
  </div>
</section>

<section class="sec" id="screens" style="background:linear-gradient(180deg,transparent,rgba(122,92,255,.06),transparent)">
  <div class="wrap screens">
    <div>
      <span class="kicker rv">AI ads &middot; One film, every screen</span>
      <h2 class="rv" style="--d:.05s;margin:1.2rem 0 1.4rem">Built for <span class="sp">the crop.</span></h2>
      <p class="m rv">A reel, a feed post and a wide spot are three different jobs. We frame every ad for each placement so the hook lands in the first three seconds, instead of just resizing one file.</p>
      <div class="tabs rv" role="tablist" aria-label="Ad format">
        <button role="tab" aria-selected="true" data-f="reel">Reel 9:16</button>
        <button role="tab" aria-selected="false" data-f="feed">Feed 1:1</button>
        <button role="tab" aria-selected="false" data-f="wide">Wide 16:9</button>
      </div>
      <p class="m rv" id="fmtnote">Reels and Shorts. Full screen, sound on, thumb-stopping from the first frame.</p>
    </div>
    <div class="stagebox rv">
      <div class="screen" id="screen" data-f="reel">
        <div class="ui"><i></i>yourbrand <small>Sponsored</small></div>
        <video muted loop playsinline preload="none" data-src="reel/previews/red-mile.mp4" aria-label="Sample ad shown in the selected format"></video>
      </div>
      <div class="fmt" id="fmtlabel">9:16 &middot; Reels, Shorts, TikTok</div>
    </div>
  </div>
</section>

<section class="sec" id="process">
  <div class="wrap">
    <div class="sechead sechead--row">
      <div><span class="kicker rv">AI ads &middot; Frame by frame</span><h2 class="rv" style="--d:.05s;margin-top:1.2rem">How an ad <span class="sp">gets made.</span></h2></div>
      <p class="lede rv" style="--d:.1s">No black box. Here is the path from a rough idea to a finished ad, and eight frames from one of our films.</p>
    </div>
    <div class="strip rv">{frames()}</div>
    <div class="steps">
      <div class="step rv"><h3>Brief</h3><p>One offer, one promise, one customer. We write it down before anyone generates a frame.</p></div>
      <div class="step rv" style="--d:.07s"><h3>Boards</h3><p>We sketch the first three seconds and the end card. The hook is decided here, not later.</p></div>
      <div class="step rv" style="--d:.14s"><h3>Generate</h3><p>Leading video models, many takes per shot. We keep what feels cinematic and throw away the rest.</p></div>
      <div class="step rv"><h3>Direct</h3><p>Fix drift, extend a shot, swap a take. Every frame is reviewed by a person.</p></div>
      <div class="step rv" style="--d:.07s"><h3>Grade and cut</h3><p>Color, pacing, captions and sound. Your logo and text go on in editing so they stay exact.</p></div>
      <div class="step rv" style="--d:.14s"><h3>Deliver</h3><p>Reel, feed and wide versions, ready to upload to Meta, TikTok, YouTube or your site.</p></div>
    </div>
  </div>
</section>

<section class="sec" id="verticals">
  <div class="wrap">
    <div class="sechead sechead--row">
      <div><span class="kicker rv">05 &middot; Built for your trade</span><h2 class="rv" style="--d:.05s;margin-top:1.2rem">One studio. <span class="sp">One trade at a time.</span></h2></div>
      <p class="lede rv" style="--d:.1s">Ads and automations work harder when they speak your customer's language. We go deep on one trade at a time.</p>
    </div>
    <div class="verts">
      <a class="pp rv" href="poolprime/">
        <div><span class="tag">Studio 01 &middot; Live</span><h3>PoolPrime<em>.ai</em><br>AI ads for pool builders</h3><p>Reveal videos, night-glow reels, instant lead replies and quote follow-up, made for pool companies.</p><span class="btn btn--volt">See PoolPrime <span class="arrow">&rarr;</span></span></div>
        <div class="logo"><img src="assets/brand/poolprime-logo.png" alt="PoolPrime.ai water P logo" width="220" height="220" loading="lazy"></div>
      </a>
      <div class="next rv" style="--d:.1s"><h3>Your trade next?</h3>
        <div class="trades">
          <a class="trade" href="#contact" data-trade="Roofing"><b>Roofing</b><span>Tell us your trade</span></a>
          <a class="trade" href="#contact" data-trade="HVAC"><b>HVAC</b><span>Tell us your trade</span></a>
          <a class="trade" href="#contact" data-trade="Landscaping"><b>Landscaping</b><span>Tell us your trade</span></a>
          <a class="trade" href="#contact" data-trade="Remodeling"><b>Remodeling</b><span>Tell us your trade</span></a>
        </div></div>
    </div>
  </div>
</section>

<section class="sec" id="plans">
  <a class="anchor" id="pricing"></a>
  <div class="wrap">
    <div class="sechead sechead--row">
      <div><span class="kicker rv">06 &middot; Pricing</span><h2 class="rv" style="--d:.05s;margin-top:1.2rem">Pick your lane. <span class="sp">Or take both.</span></h2></div>
      <p class="lede rv" style="--d:.1s">One price to build it, one monthly price to run it. Every plan starts free, so you see the work before you pay anything.</p>
    </div>
    <div class="switch rv" role="tablist" aria-label="Pricing">
      <button role="tab" aria-selected="true" id="pt-auto" aria-controls="pp-auto" data-pp="auto"><b>Automate</b><small>Run the busywork</small></button>
      <button role="tab" aria-selected="false" id="pt-ads" aria-controls="pp-ads" data-pp="ads"><b>Advertise</b><small>Premium AI ads</small></button>
      <button role="tab" aria-selected="false" id="pt-both" aria-controls="pp-both" data-pp="both"><b>Complete</b><small>Both, one bill</small></button>
      <i class="switch__pill" aria-hidden="true"></i>
    </div>

    <div class="ppanel" role="tabpanel" id="pp-auto" aria-labelledby="pt-auto">
      <div class="plans plans--4">
        <div class="plan plan--free"><h3>Automation map</h3><div class="price"><sup>$</sup>0</div><div class="per">a short call, a plain plan</div>
          <ul><li>Where your hours go</li><li>The 3 automations worth doing first</li><li>What each one saves you</li></ul><a class="btn btn--ghost" href="#contact" data-plan="map">Get my map</a></div>
        <div class="plan"><h3>Single</h3><div class="price"><sup>$</sup>197<span>/mo</span></div><div class="per">+ $497 one-time build</div>
          <ul><li>1 automation, built and run</li><li>Like missed calls texted back</li><li>Watched and fixed by us</li></ul><a class="btn btn--ghost" href="#contact" data-plan="auto-single">Start with one</a></div>
        <div class="plan hot"><span class="tag">Recommended</span><h3>Front Office</h3><div class="price"><sup>$</sup>497<span>/mo</span></div><div class="per">+ $1,497 one-time build</div>
          <ul><li>3 automations working together</li><li>Leads answered, quotes followed up, reviews asked</li><li>Monthly check-in and tuning</li></ul><a class="btn btn--volt" href="#contact" data-plan="auto-front">Build my front office <span class="arrow">&rarr;</span></a></div>
        <div class="plan"><h3>Autopilot</h3><div class="price"><sup>$</sup>997<span>/mo</span></div><div class="per">+ $2,997 one-time build</div>
          <ul><li>Up to 8 automations</li><li>Back office, inbox and AI search included</li><li>New automations added as you grow</li></ul><a class="btn btn--ghost" href="#contact" data-plan="auto-autopilot">Go on autopilot</a></div>
      </div>
    </div>

    <div class="ppanel" role="tabpanel" id="pp-ads" aria-labelledby="pt-ads" hidden>
      <div class="plans">
        <div class="plan plan--free"><h3>Sample cut</h3><div class="price"><sup>$</sup>0</div><div class="per">one ad, made for you</div>
          <ul><li>One ad for your business</li><li>No card needed</li><li>See it before you decide</li></ul><a class="btn btn--ghost" href="#contact" data-plan="sample">Get my sample</a></div>
        <div class="plan"><h3>Premiere pack</h3><div class="price"><sup>$</sup>297</div><div class="per">one time</div>
          <ul><li>5 premium ads</li><li>One round of changes</li><li>Reel, feed and wide sizes</li></ul><a class="btn btn--ghost" href="#contact" data-plan="starter">Start with a sample</a></div>
        <div class="plan hot"><span class="tag">Best for steady growth</span><h3>Studio monthly</h3><div class="price"><sup>$</sup>497<span>/mo</span></div><div class="per">cancel anytime</div>
          <ul><li>8 new premium ads every month</li><li>Fresh creative all season</li><li>Add any automation anytime</li></ul><a class="btn btn--volt" href="#contact" data-plan="monthly">Start with a sample <span class="arrow">&rarr;</span></a></div>
      </div>
      <div class="partner"><div><b>Agency or freelancer?</b><p>Need concept films or AI cutdowns for your own clients? Send us a brief and we will tell you honestly what we can do.</p></div><a class="btn btn--ghost" href="#contact" data-plan="partner">Send a brief</a></div>
    </div>

    <div class="ppanel" role="tabpanel" id="pp-both" aria-labelledby="pt-both" hidden>
      <div class="ticket">
        <div class="ticket__main">
          <span class="tag">Clipcode Complete</span>
          <h3>The ads bring them in. <span class="sp">The automations close them.</span></h3>
          <ul><li>Autopilot: up to 8 automations, built and run</li><li>Studio monthly: 8 new premium ads every month</li><li>One team, one monthly bill, one person to call</li><li>Every lead from every ad answered in about a minute</li></ul>
          <a class="btn btn--volt btn--lg" href="#contact" data-plan="complete">Get the full system <span class="arrow">&rarr;</span></a>
        </div>
        <div class="ticket__stub">
          <div class="was">$1,494/mo separately</div>
          <div class="price"><sup>$</sup>1,297<span>/mo</span></div>
          <div class="per">+ $2,997 one-time build</div>
          <div class="save">You save $197 every month</div>
        </div>
      </div>
    </div>

    <p class="fine rv">Builds are a fixed price, agreed in writing before work starts. Monthly plans cancel anytime. Ad spend on Meta, Google or TikTok is separate and goes straight to the platform. We build the ads and the automations, so we never promise a number of leads.</p>
  </div>
</section>

<section class="sec cta" id="contact">
  <div class="wrap cta__in">
    <div>
      <span class="kicker rv">07 &middot; Your turn</span>
      <h2 class="rv" style="--d:.05s">Let's take something <span class="sp">off your plate.</span></h2>
      <p class="lede rv" style="--d:.1s">Tell us about your business and what eats your day. We send back your free automation map, or your free sample ad. A real person reads every request.</p>
      <a class="dm rv" style="--d:.15s" href="https://instagram.com/greenaidigitals" target="_blank" rel="noopener"><b>DM AD</b><span>Rather use Instagram?<br>Message @greenaidigitals</span></a>
      <div class="who rv"><span>Jaden Green &middot; Gilbert, Arizona</span><a href="mailto:jaden@greenaidigital.com">jaden@greenaidigital.com</a><a href="tel:+14807980753">(480) 798-0753</a></div>
    </div>
    <form class="rv" id="form" action="https://greenai-forms-production.up.railway.app/api/submit" method="POST" novalidate aria-label="Free automation map or sample ad request" data-form="greenai-sample" data-source="greenaidigital.com">
      <input type="checkbox" name="botcheck" style="display:none" tabindex="-1" autocomplete="off">
      <div class="row"><label>Your name *<input name="name" required autocomplete="name" placeholder="Alex Rivera"></label><label>Business *<input name="business" required autocomplete="organization" placeholder="Desert Blue Pools"></label></div>
      <div class="row"><label>Email *<input type="email" name="email" required autocomplete="email" placeholder="you@company.com"></label><label>Phone<input type="tel" name="phone" autocomplete="tel" placeholder="(480) 555-0100"></label></div>
      <label>Website or Instagram<input name="website" placeholder="@yourbusiness or yourbusiness.com"></label>
      <label>What would you like?<select name="interest" id="interest">
        <option value="map">A free automation map</option><option value="auto-single">Automation: Single</option><option value="auto-front">Automation: Front Office</option><option value="auto-autopilot">Automation: Autopilot</option><option value="sample">A free sample ad</option><option value="starter">Premiere pack, 5 ads</option><option value="monthly">Studio monthly, 8 ads a month</option><option value="complete">Clipcode Complete: automation + ads</option>
        <option value="pool">I run a pool company (PoolPrime)</option><option value="trade">My trade is something else</option><option value="partner">Agency or creative partner</option><option value="other">Something else</option></select></label>
      <label>Anything we should know?<textarea name="message" id="message" placeholder="What you do, the apps you use, and the job you would love to stop doing."></textarea></label>
      <button class="btn btn--volt btn--lg" type="submit" id="send">Send my request <span class="arrow">&rarr;</span></button>
      <p class="err" id="err" role="alert"></p>
      <p class="fine" style="margin:0">We use your details only to reply to this request.</p>
      <div class="ok" role="status"><h3>We got it.</h3><p class="lede" style="margin:0 auto">Watch your email. We will be in touch about your sample ad.</p></div>
    </form>
  </div>
</section>

<section class="sec" id="faq" style="padding-top:clamp(40px,6vw,80px)">
  <div class="wrap faq">
    <div class="sechead"><span class="kicker rv">Straight answers</span><h2 class="rv" style="--d:.05s">Before you <span class="sp">ask.</span></h2></div>
    <details><summary>What can you automate?</summary><p>Most of the repeat work between a customer reaching out and you getting paid: replies to leads, missed calls, quote follow-up, booking and reminders, review asks, invoices and payment reminders, inbox sorting and daily summaries. The free map tells you which ones are worth it for you.</p></details>
    <details><summary>Do I have to switch software?</summary><p>No. We build inside the apps you already use, like your email, calendar, phone, website forms and accounting. If something you use cannot connect, we tell you before you pay.</p></details>
    <details><summary>Will it sound like a robot to my customers?</summary><p>Messages are written in your voice and you approve them before anything goes live. Anything unusual gets passed to you or your team instead of guessed at.</p></details>
    <details><summary>How much does automation cost?</summary><p>The map is free. Plans start at $497 to build one automation and $197 a month to run it. Front Office is $1,497 to build and $497 a month, and Autopilot is $2,997 and $997 a month. The build price is fixed in writing before any work starts.</p></details>
    <details><summary>Is that real footage in the ads?</summary><p>No. Every film on this site is made with AI. They are concept films, labeled as such. Your ads are built from your business details and your own photos and footage where you have them.</p></details>
    <details><summary>What does AI do badly?</summary><p>Hands, small text and logos can drift. We review every frame and add your logo and text ourselves in editing so they stay exact. If a shot does not hold up, we do not use it.</p></details>
    <details><summary>Will this get me more leads?</summary><p>We make strong ads and set up fast replies. Where you run them and how much you spend is your call, so we do not promise a number of leads. We do promise you see your own ad before paying.</p></details>
    <details><summary>What do the free map and free sample include?</summary><p>The map is a plain list of the three automations worth doing first for your business. The sample is one ad made for your business so you can judge the work. No card and no obligation for either.</p></details>
    <details><summary>Who is behind Clipcode?</summary><p>Jaden Green, in Gilbert, Arizona. Clipcode used to be called GreenAI Digital; same team, same email, new name. You deal with a real person you can email or call.</p></details>
    <details><summary>Do you only work in Phoenix?</summary><p>Phoenix businesses come first, but the work is done online, so businesses elsewhere can send a request.</p></details>
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
    <div class="l"><a class="brand" href="#top" aria-label="Clipcode, back to top"><img class="brand__mark" src="assets/brand/clipcode-mark.svg" alt="" width="30" height="30"><span>Clip<i>code</i></span></a><a href="#automations">Automations</a><a href="#reel">AI ads</a><a href="poolprime/">PoolPrime.ai</a><a href="https://instagram.com/greenaidigitals" target="_blank" rel="noopener">Instagram</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a></div>
    <div>&copy; <span id="yr">2026</span> Clipcode (formerly GreenAI Digital) &middot; Jaden Green, Gilbert, Arizona</div>
  </div>
</footer>
<script src="gai-ads.js?v=3"></script>
</body>
</html>
'''
open(os.path.join(ROOT,'index.html'),'w').write(HTML)
print('index.html written', len(HTML),'bytes')

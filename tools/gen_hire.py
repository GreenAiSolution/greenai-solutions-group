#!/usr/bin/env python3
"""gen_hire.py — hire.html, THE HIRING DESK. The owner picks AI employees off the bench
(tap or drag onto the desk), sees an example Monday built from the hires, and the whole price.
"Send this lineup" hands the picks to contact.html as ?lineup=ring,books,... (contact reads it)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_platform_agents import NAV, AGENTS, FULL, SEPARATE, head, tail, esc, ROOT
from robots import bust

GOLD = "#E8C46A"

# An example Monday per hire, clock-ordered on the desk. Labelled "example" on the page.
DAY = {
 "ring":     [("06:52", "6:52 AM", "Answered a caller before you were up. Booked Tuesday 8:00 into your calendar."),
              ("21:47", "9:47 PM", "Missed call while you were at dinner. Texted them back in under a minute; they booked Thursday.")],
 "dispatch": [("08:05", "8:05 AM", "Turned last night's web request into a client and sent the quote from your price list."),
              ("18:00", "6:00 PM", "Sent tomorrow's visit reminders. Nudged the quote that went quiet on Friday.")],
 "inbox":    [("07:30", "7:30 AM", "Replied to four new leads in Gmail, each in under a minute. Two picked a time."),
              ("13:10", "1:10 PM", "A refund question came in. Drafted a reply and left it in Drafts for you. Nothing sent.")],
 "thread":   [("07:00", "7:00 AM", "Posted the morning summary in #ops: leads overnight, quotes out, who is waiting on you."),
              ("15:20", "3:20 PM", "Answered a tech's question in Slack from your own price sheet, with the source.")],
 "huddle":   [("07:02", "7:02 AM", "Morning summary in your Teams channel: three leads, two quoted, one waiting on photos."),
              ("11:40", "11:40 AM", "Put a new request in front of you with three buttons: approve, edit, or call first.")],
 "books":    [("07:00", "7:00 AM", "Cash sheet in your inbox: what came in last week, what is late, zero disputes."),
              ("15:12", "3:12 PM", "A job closed at 3:10. The invoice went out at 3:12 with your payment link.")],
}

EMP = [{"id": a["id"], "name": a["name"], "inside": a["inside"], "price": a["price"],
        "does": [d[1] for d in a["does"][:3]], "day": DAY[a["id"]]} for a in AGENTS]

def card(a):
    does = "".join(f"<li>{esc(d)}</li>" for d in a["does"])
    return f'''<article class="hd-card" draggable="true" data-id="{a["id"]}" aria-label="{a["name"]}">
          <div class="hd-card__face">{bust(a["id"], "hd-bust")}</div>
          <div class="hd-card__body">
            <h3>{a["name"]}</h3><p class="hd-card__app">works {esc(a["inside"])}</p>
            <ul>{does}</ul>
          </div>
          <div class="hd-card__foot"><b>${a["price"]}<small>/mo</small></b>
            <button type="button" class="hd-hire" data-id="{a["id"]}" aria-pressed="false"><span class="on">Hired ✓</span><span class="off">Hire</span></button></div>
        </article>'''

bench = "\n        ".join(card(a) for a in EMP)

CSS = f"""
    body.tk.hd-page, body.tk.hd-page::before {{ background: #06100A; }}
    body.tk.hd-page::before {{ background-image: radial-gradient(60% 40% at 50% 0%, rgba(232,196,106,.10), transparent 60%); }}
    body.tk.hd-page .nav.transparent, body.tk.hd-page .nav.scrolled {{ background: rgba(6,16,10,.72); }}
    body.tk.hd-page .nav .nav__logo-name, body.tk.hd-page .nav .nav__logo-sub, body.tk.hd-page .nav .nav__link {{ color: rgba(255,255,255,.85); }}
    body.tk.hd-page .nav .nav__hamburger span {{ background: #fff; }}
    body.tk.hd-page .nav__cta {{ background: {GOLD}; border-color: {GOLD}; color: #06100A; }}
    body.tk.hd-page .footer {{ background: #000; }}
    .sv-grain {{ position: fixed; inset: 0; z-index: 5; pointer-events: none; opacity: .07; mix-blend-mode: screen; }}
    .sv-vig {{ position: fixed; inset: 0; z-index: 4; pointer-events: none; background: radial-gradient(80% 70% at 50% 40%, transparent 55%, rgba(0,0,0,.55)); }}
    .hd {{ color: #fff; }}
    .hd h1, .hd h2, .hd h3 {{ color: #fff; margin: 0; }}
    .hd em {{ color: {GOLD}; font-style: italic; font-family: 'Fraunces', Georgia, serif; font-weight: 500; }}
    .hd p {{ color: rgba(255,255,255,.72); }}
    .hd-slate {{ display: inline-flex; align-items: center; gap: .8rem; margin: 0 0 1.4rem; font-family: var(--mono); font-size: .72rem; letter-spacing: .3em; text-transform: uppercase; color: {GOLD}; }}
    .hd-slate::before, .hd-slate::after {{ content: ""; width: 2.4rem; height: 1px; background: {GOLD}; opacity: .7; }}
    .hd-hero {{ padding: 10.5rem 1.5rem 2.5rem; text-align: center; }}
    .hd-hero h1 {{ margin: 0 auto 1.1rem; max-width: 13ch; font-family: var(--font-display); font-weight: 600; font-size: clamp(2.8rem, 7vw, 6rem); line-height: .98; letter-spacing: -.03em; }}
    .hd-hero p {{ max-width: 56ch; margin: 0 auto; font-size: 1.1rem; line-height: 1.6; }}
    .hd-room {{ display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 2rem; max-width: 1280px; margin: 0 auto; padding: 1rem 1.5rem 5rem; align-items: start; }}
    .hd-label {{ font-family: var(--mono); font-size: .7rem; letter-spacing: .26em; text-transform: uppercase; color: rgba(255,255,255,.55); margin: 0 0 1rem; }}
    .hd-bench {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }}
    .hd-card {{ position: relative; display: grid; grid-template-rows: auto 1fr auto; gap: .9rem; padding: 1.2rem; border-radius: 20px; background: linear-gradient(180deg, #0C1D13, #08140D); border: 1px solid rgba(232,196,106,.16); cursor: grab; transition: border-color .2s, transform .2s, box-shadow .2s, opacity .2s; }}
    .hd-card:hover {{ border-color: rgba(232,196,106,.5); transform: translateY(-3px); }}
    .hd-card.is-hired {{ border-color: {GOLD}; box-shadow: 0 0 0 1px {GOLD}, 0 30px 60px -30px rgba(232,196,106,.55); }}
    .hd-card.is-drag {{ opacity: .45; }}
    .hd-card__face {{ display: flex; align-items: center; gap: .8rem; }}
    .hd-bust {{ width: 56px; height: 56px; border-radius: 50%; flex: none; filter: drop-shadow(0 6px 12px rgba(0,0,0,.5)); }}
    .hd-card h3 {{ font-family: var(--font-display); font-weight: 600; font-size: 1.45rem; letter-spacing: -.01em; }}
    .hd-card__app {{ margin: .15rem 0 .7rem; font-size: .85rem; color: {GOLD} !important; }}
    .hd-card ul {{ margin: 0; padding: 0; list-style: none; display: grid; gap: .35rem; }}
    .hd-card li {{ position: relative; padding-left: 1rem; font-size: .88rem; line-height: 1.45; color: rgba(255,255,255,.72); }}
    .hd-card li::before {{ content: ""; position: absolute; left: 0; top: .55em; width: 5px; height: 5px; border-radius: 50%; background: {GOLD}; }}
    .hd-card__foot {{ display: flex; align-items: center; justify-content: space-between; padding-top: .9rem; border-top: 1px solid rgba(255,255,255,.08); }}
    .hd-card__foot b {{ font-family: var(--font-display); font-size: 1.6rem; font-weight: 600; letter-spacing: -.02em; }}
    .hd-card__foot small {{ font-size: .8rem; font-weight: 500; color: rgba(255,255,255,.55); margin-left: .15rem; }}
    .hd-hire {{ min-height: 44px; padding: .55rem 1.2rem; border-radius: 999px; border: 1px solid {GOLD}; background: transparent; color: {GOLD}; font: 600 .9rem var(--font-body, inherit); cursor: pointer; transition: background .2s, color .2s; }}
    .hd-hire:hover {{ background: rgba(232,196,106,.12); }}
    .hd-hire[aria-pressed="true"] {{ background: {GOLD}; color: #06100A; }}
    .hd-hire .on, .hd-hire[aria-pressed="true"] .off {{ display: none; }}
    .hd-hire[aria-pressed="true"] .on {{ display: inline; }}
    .hd-desk {{ position: sticky; top: 90px; padding: 1.4rem; border-radius: 24px; background: linear-gradient(180deg, #10241A, #0A1811); border: 1px solid rgba(232,196,106,.3); box-shadow: 0 60px 120px -50px rgba(0,0,0,.9); transition: border-color .2s, box-shadow .2s; }}
    .hd-desk.is-over {{ border-color: {GOLD}; box-shadow: 0 0 0 2px {GOLD}, 0 0 80px -10px rgba(232,196,106,.45); }}
    .hd-desk h2 {{ font-family: var(--font-display); font-weight: 600; font-size: 1.7rem; letter-spacing: -.02em; margin-bottom: .3rem; }}
    .hd-seats {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: .5rem; margin: 1rem 0 1.2rem; }}
    .hd-seat {{ aspect-ratio: 1; border-radius: 50%; border: 1px dashed rgba(232,196,106,.35); display: grid; place-items: center; overflow: hidden; background: rgba(0,0,0,.25); padding: 0; cursor: default; }}
    .hd-seat img {{ width: 100%; height: 100%; object-fit: cover; }}
    .hd-seat.is-filled {{ border: 1px solid {GOLD}; cursor: pointer; animation: hd-pop .35s ease-out; }}
    .hd-seat.is-filled:hover {{ opacity: .7; }}
    @keyframes hd-pop {{ from {{ transform: scale(.6); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
    .hd-empty {{ margin: 0 0 1rem; padding: 1.4rem 1rem; text-align: center; border-radius: 16px; border: 1px dashed rgba(255,255,255,.18); font-size: .92rem; }}
    .hd-day {{ margin: 0 0 1.2rem; padding: 0; list-style: none; max-height: 340px; overflow: auto; }}
    .hd-day li {{ display: grid; grid-template-columns: 4.6rem minmax(0, 1fr); gap: .8rem; padding: .7rem 0; border-top: 1px solid rgba(255,255,255,.07); animation: hd-pop .35s ease-out; }}
    .hd-day time {{ font-family: var(--mono); font-size: .74rem; color: {GOLD}; padding-top: .15rem; }}
    .hd-day b {{ display: block; font-family: var(--mono); font-size: .66rem; letter-spacing: .2em; color: rgba(255,255,255,.5); margin-bottom: .15rem; }}
    .hd-day span {{ font-size: .88rem; line-height: 1.45; color: rgba(255,255,255,.82); }}
    .hd-total {{ display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; padding-top: 1rem; border-top: 1px solid rgba(232,196,106,.4); }}
    .hd-total b {{ font-family: var(--font-display); font-weight: 600; font-size: clamp(2.4rem, 4vw, 3.2rem); letter-spacing: -.03em; line-height: 1; }}
    .hd-total span {{ font-size: .88rem; color: rgba(255,255,255,.6); text-align: right; }}
    .hd-save {{ margin: .6rem 0 0; font-size: .86rem; color: {GOLD} !important; min-height: 1.3em; }}
    .hd-go {{ display: flex; flex-wrap: wrap; gap: .6rem; margin-top: 1.2rem; }}
    .hd-go .tk-btn {{ flex: 1 1 auto; justify-content: center; }}
    .hd-go .tk-btn--solid {{ background: {GOLD}; border-color: {GOLD}; color: #06100A; box-shadow: 0 16px 40px -14px rgba(232,196,106,.7); }}
    .hd-go .tk-btn--solid[aria-disabled="true"] {{ opacity: .4; pointer-events: none; box-shadow: none; }}
    .hd-go .tk-btn--ghost {{ border-color: rgba(255,255,255,.3); color: #fff; }}
    .hd-all {{ background: none; border: 0; padding: .4rem 0; color: rgba(255,255,255,.7); font: inherit; font-size: .85rem; text-decoration: underline; text-underline-offset: 3px; cursor: pointer; }}
    .hd-all:hover {{ color: #fff; }}
    .hd-fine {{ margin: 1rem 0 0; font-size: .78rem; line-height: 1.5; color: rgba(255,255,255,.45) !important; }}
    @media (max-width: 960px) {{
      .hd-room {{ grid-template-columns: 1fr; }}
      .hd-desk {{ position: relative; top: 0; order: -1; }}
      .hd-day {{ max-height: none; }}
    }}
    @media (max-width: 600px) {{ .hd-bench {{ grid-template-columns: 1fr; }} .hd-hero {{ padding-top: 8.5rem; }} }}
    @media (prefers-reduced-motion: reduce) {{ .hd-seat.is-filled, .hd-day li {{ animation: none; }} .hd-card {{ transition: none; }} }}
"""

GRAIN = '<svg class="sv-grain" aria-hidden="true"><filter id="g"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .5 0"/></filter><rect width="100%" height="100%" filter="url(#g)"/></svg><div class="sv-vig" aria-hidden="true"></div>'

JS = """
  <script>
  (function () {
    var EMP = %s, FULL = %d, SEP = %d;
    var byId = {}; EMP.forEach(function (e) { byId[e.id] = e; });
    var order = EMP.map(function (e) { return e.id; });
    var picked = [];
    try { picked = (location.hash.slice(1) || '').split(',').filter(function (id) { return byId[id]; }); } catch (e) {}
    var $ = function (s) { return document.querySelector(s); };
    var desk = $('#desk'), seats = $('#seats'), day = $('#day'), empty = $('#deskEmpty');
    var total = $('#total'), totalNote = $('#totalNote'), save = $('#save'), send = $('#send'), all = $('#hireAll');
    function money(n) { return '$' + n.toLocaleString('en-US'); }
    function render() {
      picked.sort(function (a, b) { return order.indexOf(a) - order.indexOf(b); });
      document.querySelectorAll('.hd-card').forEach(function (c) {
        var on = picked.indexOf(c.dataset.id) > -1;
        c.classList.toggle('is-hired', on);
        c.querySelector('.hd-hire').setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      var s = '';
      for (var i = 0; i < 6; i++) {
        var id = picked[i];
        s += id ? '<button type="button" class="hd-seat is-filled" data-id="' + id + '" title="Remove ' + byId[id].name + '" aria-label="Remove ' + byId[id].name + '"><img src="art/marks/' + id + '-sm.svg" alt="" width="48" height="48" /></button>'
                : '<span class="hd-seat" aria-hidden="true"></span>';
      }
      seats.innerHTML = s;
      var lines = [];
      picked.forEach(function (id) { byId[id].day.forEach(function (d) { lines.push([d[0], d[1], byId[id].name, d[2]]); }); });
      lines.sort(function (a, b) { return a[0] < b[0] ? -1 : 1; });
      day.innerHTML = lines.map(function (l) { return '<li><time>' + l[1] + '</time><div><b>' + l[2] + '</b><span>' + l[3] + '</span></div></li>'; }).join('');
      empty.hidden = picked.length > 0;
      var sum = picked.reduce(function (t, id) { return t + byId[id].price; }, 0);
      var isAll = picked.length === EMP.length;
      total.textContent = money(isAll ? FULL : sum);
      totalNote.textContent = picked.length ? (picked.length + (picked.length === 1 ? ' employee' : ' employees') + ' · a month · month to month') : 'a month · nobody hired yet';
      save.textContent = isAll ? 'The full staff: ' + money(SEP - FULL) + ' a month less than hiring all six separately.'
        : (picked.length >= 4 ? 'Hire all six and it is ' + money(FULL) + ' a month, not ' + money(SEP) + '.' : '');
      all.textContent = isAll ? 'Clear the desk' : 'Hire the full staff';
      send.setAttribute('aria-disabled', picked.length ? 'false' : 'true');
      send.href = picked.length ? 'contact.html?lineup=' + picked.join(',') : '#bench';
      try { history.replaceState(null, '', picked.length ? '#' + picked.join(',') : location.pathname); } catch (e) {}
    }
    function toggle(id) { var i = picked.indexOf(id); if (i > -1) picked.splice(i, 1); else picked.push(id); render(); }
    function add(id) { if (byId[id] && picked.indexOf(id) < 0) { picked.push(id); render(); } }
    document.querySelectorAll('.hd-hire').forEach(function (b) { b.addEventListener('click', function (e) { e.stopPropagation(); toggle(b.dataset.id); }); });
    seats.addEventListener('click', function (e) { var s = e.target.closest('.hd-seat.is-filled'); if (s) toggle(s.dataset.id); });
    all.addEventListener('click', function () { picked = picked.length === EMP.length ? [] : order.slice(); render(); });
    document.querySelectorAll('.hd-card').forEach(function (c) {
      c.addEventListener('dragstart', function (e) { e.dataTransfer.setData('text/plain', c.dataset.id); e.dataTransfer.effectAllowed = 'copy'; c.classList.add('is-drag'); });
      c.addEventListener('dragend', function () { c.classList.remove('is-drag'); desk.classList.remove('is-over'); });
    });
    desk.addEventListener('dragover', function (e) { e.preventDefault(); e.dataTransfer.dropEffect = 'copy'; desk.classList.add('is-over'); });
    desk.addEventListener('dragleave', function (e) { if (!desk.contains(e.relatedTarget)) desk.classList.remove('is-over'); });
    desk.addEventListener('drop', function (e) { e.preventDefault(); desk.classList.remove('is-over'); add(e.dataTransfer.getData('text/plain')); });
    render();
  })();
  </script>""" % (json.dumps(EMP), FULL, SEPARATE)

PAGE = head("The Hiring Desk — build your AI staff | GreenAI Solutions",
            f"Pick the AI employees who start Monday. Six of them, one inside each app you already run, from $297 a month each or all six for ${FULL:,}. See their first day and the whole price before you talk to anyone.",
            "hire.html", CSS, og_title="The Hiring Desk. Pick who starts Monday.").replace(
            '<meta name="twitter:card" content="summary_large_image" />',
            '<meta name="twitter:card" content="summary_large_image" />\n  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@1,9..144,500&display=swap" rel="stylesheet" />') + f'''
<body class="tk hd-page">
  <a href="#main" class="skip-link">Skip to content</a>
  <nav class="nav transparent" id="main-nav" aria-label="Main navigation">
{NAV}
  </nav>
  {GRAIN}
  <main id="main" class="hd">

    <header class="hd-hero" aria-labelledby="h1">
      <p class="hd-slate">The Hiring Desk</p>
      <h1 id="h1">Pick who starts <em>Monday.</em></h1>
      <p>Six AI employees, one inside each app your company already runs on. Tap one to hire it, or drag it onto the desk. The desk shows what their Monday looks like and the whole price, before you talk to anyone.</p>
    </header>

    <div class="hd-room">
      <section id="bench" aria-labelledby="h-bench">
        <p class="hd-label" id="h-bench">The bench · six employees</p>
        <div class="hd-bench">
        {bench}
        </div>
      </section>

      <aside class="hd-desk" id="desk" aria-labelledby="h-desk" aria-live="polite">
        <p class="hd-label">Your desk</p>
        <h2 id="h-desk">Your <em>staff.</em></h2>
        <div class="hd-seats" id="seats"></div>
        <p class="hd-empty" id="deskEmpty">Nobody hired yet. Tap <b>Hire</b> on anyone on the bench, or drag them here.</p>
        <p class="hd-label" style="margin-top:.4rem">Their Monday · an example</p>
        <ol class="hd-day" id="day"></ol>
        <div class="hd-total"><b id="total">$0</b><span id="totalNote">a month</span></div>
        <p class="hd-save" id="save"></p>
        <button type="button" class="hd-all" id="hireAll">Hire the full staff</button>
        <div class="hd-go">
          <a id="send" href="#bench" class="tk-btn tk-btn--solid tk-btn--arrow" aria-disabled="true">Send this lineup</a>
          <a href="tel:4807980753" class="tk-btn tk-btn--ghost">Call (480) 798-0753</a>
        </div>
        <p class="hd-fine">Nothing is charged here. Sending the lineup starts a conversation: we confirm it fits your company, then you get the price in writing. Month to month, no contract. Built on your prices, hours and wording, and you read every reply before it goes live.</p>
      </aside>
    </div>
  </main>''' + tail(JS)

open(os.path.join(ROOT, "hire.html"), "w").write(PAGE)
print("wrote hire.html", len(PAGE))

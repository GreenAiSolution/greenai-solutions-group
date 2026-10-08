/* Arizona Granite & Stone — v4 "The Build"
   One rAF loop drives every scroll effect. Reduced motion gets the still page. */
(function () {
  'use strict';

  var CONFIG = {
    formEndpoint: 'https://formsubmit.co/ajax/arizonagraniteandstone@gmail.com'
  };

  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) root.classList.add('reduce');

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };
  // 0..1 progress of v across [a, b]
  var span = function (v, a, b) { return clamp((v - a) / (b - a), 0, 1); };
  var ease = function (t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
  var vh = window.innerHeight, vw = window.innerWidth;

  /* ---------- header + call bar ---------- */
  var top = $('#top'), callbar = $('.callbar'), quote = $('#quote');

  /* ---------- 01 · the build ---------- */
  var build = $('#build');
  var B = {
    cam: $('.cam', build), intro: $('.intro', build),
    ghost: $('#l-ghost'), cab: $('#l-cab'), top: $('#l-top'), wipe: $('#wipe'), sheenTop: $('#sheen-top'),
    isl: $('#l-isl'), base: $('#l-base'), shadow: $('#isl-shadow'), sheenIsl: $('#sheen-isl'), full: $('#l-full'),
    steps: $$('.steps li', build), rail: $('.rail', build), dots: $$('.rail i', build), railFill: $('.rail-fill', build)
  };
  // where each caption takes over, as a fraction of the pinned scroll
  var STEP_AT = [0.07, 0.24, 0.43, 0.62, 0.81];
  var lastStep = -1;

  function drawBuild() {
    var r = build.getBoundingClientRect();
    var total = build.offsetHeight - vh;
    if (r.bottom < 0 || r.top > vh) return;
    var p = clamp(-r.top / total, 0, 1);

    // camera walks in
    var c = ease(p);
    B.cam.style.transform = 'translateY(' + (2.5 - 2.5 * c).toFixed(2) + '%) scale(' + (1.24 - 0.24 * c).toFixed(4) + ')';

    // intro card leaves
    var io = span(p, 0.015, 0.075);
    B.intro.style.opacity = (1 - io).toFixed(3);
    B.intro.style.transform = 'translateY(calc(-46% - ' + (io * 60).toFixed(1) + 'px))';
    B.intro.style.visibility = io >= 1 ? 'hidden' : 'visible';

    // the room, ghosted
    var g = span(p, 0.2, 0.34);
    B.ghost.setAttribute('opacity', (g * 0.26).toFixed(3));
    // cabinets
    B.cab.setAttribute('opacity', span(p, 0.25, 0.38).toFixed(3));
    // perimeter stone: fade in, wipe left to right, then a sheen
    var t = span(p, 0.43, 0.58);
    B.top.setAttribute('opacity', span(p, 0.43, 0.46).toFixed(3));
    B.wipe.setAttribute('width', (ease(t) * 1179).toFixed(1));
    var s = span(p, 0.5, 0.64);
    B.sheenTop.setAttribute('x', (-300 + s * 1900).toFixed(1));
    B.sheenTop.setAttribute('opacity', (Math.sin(s * Math.PI) * 0.8).toFixed(3));
    // island base, then the slab drops into place
    B.base.setAttribute('opacity', span(p, 0.6, 0.67).toFixed(3));
    var d = span(p, 0.63, 0.75), de = 1 - Math.pow(1 - d, 3);
    B.isl.setAttribute('opacity', span(p, 0.63, 0.67).toFixed(3));
    B.isl.setAttribute('transform', 'translate(0 ' + (-90 * (1 - de)).toFixed(2) + ')');
    B.shadow.setAttribute('opacity', (d > 0 && d < 1 ? 0.45 * Math.sin(d * Math.PI) : 0).toFixed(3));
    B.shadow.setAttribute('rx', (120 + 50 * de).toFixed(1));
    var si = span(p, 0.73, 0.81);
    B.sheenIsl.setAttribute('x', (260 + si * 760).toFixed(1));
    B.sheenIsl.setAttribute('opacity', (Math.sin(si * Math.PI) * 0.9).toFixed(3));
    // everything else: appliances, walls, light
    B.full.setAttribute('opacity', span(p, 0.81, 0.92).toFixed(3));

    // captions + rail
    var step = -1;
    for (var i = 0; i < STEP_AT.length; i++) if (p >= STEP_AT[i]) step = i;
    if (step !== lastStep) {
      B.steps.forEach(function (li, k) { li.classList.toggle('on', k === step); });
      B.dots.forEach(function (dot, k) { dot.classList.toggle('on', k <= step); });
      lastStep = step;
    }
    B.rail.classList.toggle('on', p > 0.06 && p < 0.995);
    B.railFill.style.transform = 'scaleY(' + span(p, STEP_AT[0], STEP_AT[4]).toFixed(3) + ')';
  }

  /* ---------- 02 · slogan marquee ---------- */
  var marq = $('.marq'), slogan = $('.slogan');
  function drawMarq() {
    var r = slogan.getBoundingClientRect();
    if (r.bottom < 0 || r.top > vh) return;
    var k = (vh - r.top) / (vh + r.height);
    marq.style.transform = 'translateX(' + (-k * 38).toFixed(2) + '%)';
  }

  /* ---------- 04 · what we build: the row in view picks the picture ---------- */
  var whatRows = $$('.what-list li'), whatImg = $('#what-img'), whatCur = null;
  function setWhat(li) {
    if (!li || li === whatCur) return;
    whatCur = li;
    whatRows.forEach(function (x) { x.classList.toggle('on', x === li); });
    if (!whatImg || getComputedStyle(whatImg.parentNode).display === 'none') return;
    var src = li.getAttribute('data-img');
    whatImg.classList.add('swap');
    setTimeout(function () {
      whatImg.onload = function () { whatImg.classList.remove('swap'); };
      whatImg.src = src;
      if (whatImg.complete) whatImg.classList.remove('swap');
    }, 220);
  }
  whatRows.forEach(function (li) { li.addEventListener('mouseenter', function () { setWhat(li); }); });
  // preload the five other pictures once the section is near
  var whatPre = false;
  function drawWhat() {
    var best = null, bd = 1e9, mid = vh * 0.5;
    for (var i = 0; i < whatRows.length; i++) {
      var r = whatRows[i].getBoundingClientRect();
      var dd = Math.abs(r.top + r.height / 2 - mid);
      if (dd < bd) { bd = dd; best = whatRows[i]; }
    }
    if (best && bd < vh * 0.35) setWhat(best);
    if (!whatPre && whatRows.length && whatRows[0].getBoundingClientRect().top < vh * 2) {
      whatPre = true;
      whatRows.forEach(function (li) { var im = new Image(); im.src = li.getAttribute('data-img'); });
    }
  }

  /* ---------- 05 · stone cards settle back as the next one lands ---------- */
  var cards = $$('.card');
  function drawCards() {
    for (var i = 0; i < cards.length - 1; i++) {
      var next = cards[i + 1].getBoundingClientRect();
      var k = span(vh - next.top, 0, vh * 0.8);
      cards[i].style.transform = 'scale(' + (1 - 0.07 * k).toFixed(4) + ')';
      cards[i].style.filter = 'brightness(' + (1 - 0.45 * k).toFixed(3) + ')';
    }
  }

  /* ---------- 07 · the work: pinned sideways reel on desktop ---------- */
  var work = $('#work'), reel = $('.reel', work), reelFill = $('.reel-fill', work);
  var pinX = false, reelTravel = 0;
  function layoutWork() {
    pinX = !reduce && vw >= 900;
    root.classList.toggle('pin-x', pinX);
    if (pinX) {
      reel.style.transform = '';
      reelTravel = Math.max(0, reel.scrollWidth - vw);
      work.style.height = (vh + reelTravel) + 'px';
    } else {
      work.style.height = '';
      reel.style.transform = '';
    }
  }
  function drawWork() {
    if (pinX) {
      var r = work.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      var k = span(-r.top, 0, reelTravel);
      reel.style.transform = 'translate3d(' + (-k * reelTravel).toFixed(1) + 'px,0,0)';
      reelFill.style.transform = 'scaleX(' + k.toFixed(4) + ')';
    }
  }
  reel.addEventListener('scroll', function () {
    if (pinX) return;
    var m = reel.scrollWidth - reel.clientWidth;
    reelFill.style.transform = 'scaleX(' + (m > 0 ? reel.scrollLeft / m : 0).toFixed(4) + ')';
  }, { passive: true });

  /* ---------- header, call bar ---------- */
  function drawChrome() {
    var y = window.scrollY;
    top.classList.toggle('solid', y > 40);
    var q = quote.getBoundingClientRect();
    callbar.classList.toggle('on', y > vh * 0.7 && !(q.top < vh && q.bottom > 0));
  }

  /* ---------- the loop ---------- */
  var queued = false;
  function frame() {
    queued = false;
    drawChrome();
    if (reduce) return;
    drawBuild(); drawMarq(); drawWhat(); drawCards(); drawWork();
  }
  function request() { if (!queued) { queued = true; requestAnimationFrame(frame); } }
  window.addEventListener('scroll', request, { passive: true });
  window.addEventListener('resize', function () {
    // phones fire resize when the URL bar slides; only re-measure on a real width change or a big height change
    var nw = window.innerWidth, nh = window.innerHeight;
    if (nw !== vw || Math.abs(nh - vh) > 140) { vw = nw; vh = nh; layoutWork(); }
    request();
  });
  layoutWork();
  window.addEventListener('load', function () { layoutWork(); request(); });
  frame();

  /* ---------- reveal on scroll ---------- */
  if ('IntersectionObserver' in window && !reduce) {
    var ro = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); ro.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    $$('.rv').forEach(function (el, i) { el.style.transitionDelay = ((i % 5) * 70) + 'ms'; ro.observe(el); });
  } else {
    $$('.rv').forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- Instagram: load Meta's embed script only when the strip is close ---------- */
  var ig = $('#instagram'), igLoaded = false;
  function loadIG() {
    if (igLoaded) return; igLoaded = true;
    var s = document.createElement('script');
    s.async = true; s.src = 'https://www.instagram.com/embed.js';
    s.onload = function () { if (window.instgrm) window.instgrm.Embeds.process(); };
    document.body.appendChild(s);
  }
  if ('IntersectionObserver' in window) {
    var igo = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { loadIG(); igo.disconnect(); } }, { rootMargin: '900px 0px' });
    igo.observe(ig);
  } else { loadIG(); }

  /* ---------- lightbox ---------- */
  var lb = $('#lb'), lbImg = $('#lb-img'), lbCap = $('#lb-cap');
  $$('.reel button').forEach(function (b) {
    b.addEventListener('click', function () {
      var img = $('img', b), cap = b.parentNode.querySelector('figcaption');
      lbImg.src = b.getAttribute('data-full'); lbImg.alt = img.alt;
      lbCap.innerHTML = cap ? cap.innerHTML.replace('</b>', '</b> · ') : '';
      if (lb.showModal) lb.showModal(); else window.open(lbImg.src, '_blank');
    });
  });
  $('.lb-x').addEventListener('click', function () { lb.close(); });
  lb.addEventListener('click', function (e) { if (e.target === lb || e.target.tagName === 'FIGURE') lb.close(); });

  /* ---------- quote form ---------- */
  var form = $('#quote-form'), note = $('.form-note', form);
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var bad = null;
    ['name', 'phone'].forEach(function (n) {
      var f = form.elements[n], ok = f.value.trim().length > (n === 'phone' ? 6 : 1);
      f.setAttribute('aria-invalid', ok ? 'false' : 'true');
      if (!ok && !bad) bad = f;
    });
    if (bad) { note.className = 'form-note err'; note.textContent = 'Please add your name and a phone number we can call.'; bad.focus(); return; }
    var btn = $('button[type=submit]', form);
    btn.disabled = true; note.className = 'form-note'; note.textContent = 'Sending…';
    fetch(CONFIG.formEndpoint, { method: 'POST', headers: { 'Accept': 'application/json' }, body: new FormData(form) })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function () {
        form.reset();
        note.className = 'form-note ok';
        note.textContent = 'Got it. Your request is with the shop, and we will call you at the number you gave us.';
      })
      .catch(function () {
        note.className = 'form-note err';
        note.innerHTML = 'That did not send. Please call <a href="tel:+16234989056">(623) 498-9056</a> or email <a href="mailto:arizonagraniteandstone@gmail.com">arizonagraniteandstone@gmail.com</a>.';
      })
      .then(function () { btn.disabled = false; });
  });

  var yr = $('#yr'); if (yr) yr.textContent = new Date().getFullYear();
})();

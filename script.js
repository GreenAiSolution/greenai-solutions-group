/* =============================================
   GreenAI Solutions — Next-Level JavaScript
   ============================================= */

(function () {
  'use strict';

  /* ---- NAVBAR ----
     Two generations of nav markup are live: the older pages use
     #navbar / #hamburger / #navLinks, the main pages use
     #main-nav / .nav__hamburger / .nav__mobile. Match either. */
  const navbar = document.getElementById('navbar') || document.getElementById('main-nav');
  const hamburger = document.getElementById('hamburger') || document.querySelector('.nav__hamburger');
  const navLinks = document.getElementById('navLinks') || document.querySelector('.nav__mobile');

  if (navbar) {
    const onScroll = () => {
      const scrolled = window.scrollY > 40;
      navbar.classList.toggle('scrolled', scrolled);
      // The solid bar is light, so the white "transparent" text has to go with it
      // or the links turn invisible against their own background.
      if (navbar.dataset.transparent === 'true') {
        navbar.classList.toggle('transparent', !scrolled);
      }
    };
    if (navbar.classList.contains('transparent')) navbar.dataset.transparent = 'true';
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      const open = navLinks.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', open);
      // An open menu needs a solid bar behind it even at the top of the page,
      // otherwise the panel floats over whatever it is covering.
      if (navbar && navbar.dataset.transparent === 'true') {
        navbar.classList.toggle('scrolled', open || window.scrollY > 40);
        navbar.classList.toggle('transparent', !open && window.scrollY <= 40);
      }
      hamburger.querySelectorAll('span').forEach((s, i) => {
        s.style.transform = open
          ? (i === 0 ? 'translateY(7px) rotate(45deg)' : i === 1 ? 'scaleX(0)' : 'translateY(-7px) rotate(-45deg)')
          : '';
        s.style.opacity = (open && i === 1) ? '0' : '1';
      });
    });

    navLinks.querySelectorAll('a').forEach(a =>
      a.addEventListener('click', () => {
        navLinks.classList.remove('open');
        hamburger.querySelectorAll('span').forEach(s => {
          s.style.transform = '';
          s.style.opacity = '1';
        });
      })
    );
  }

  /* ---- ACTIVE PAGE IN NAV ----
     Every nav link carries data-page. Nothing was reading it, so the bar never
     showed where you actually were. Mark the match on both the desktop and the
     mobile list, and promote a service page to light up its parent "Services"
     dropdown so the section you are in is never ambiguous. */
  (function markCurrentPage() {
    let file = window.location.pathname.split('/').pop() || 'index.html';
    if (!file.endsWith('.html')) file = 'index.html';

    // Service detail pages live under the Services dropdown.
    const parentOf = {
      'service-ai-employees.html': 'services.html',
      'service-ai-ads.html': 'services.html',
      'service-ai-consulting.html': 'services.html',
      'service-web-design.html': 'services.html'
    };

    document.querySelectorAll('.nav__link[data-page]').forEach(link => {
      const page = link.dataset.page;
      const exact = page === file;
      const section = !exact && parentOf[file] === page;
      if (exact || section) {
        link.classList.add('nav__link--current');
        // aria-current="page" only for the page you are literally on.
        if (exact) link.setAttribute('aria-current', 'page');
      }
    });

    // Mark the submenu entry for the exact page too. Entries that point at an
    // anchor (services.html#pricing) are skipped — they target a section, not
    // the page, so claiming aria-current for them would be a lie to a screen
    // reader while you sit at the top of that same page.
    document.querySelectorAll('.nav__submenu a').forEach(a => {
      const raw = a.getAttribute('href') || '';
      if (raw.includes('#')) return;
      const href = raw.split('/').pop();
      if (href && href === file) {
        a.classList.add('nav__submenu-link--current');
        a.setAttribute('aria-current', 'page');
      }
    });
  })();

  /* ---- SMOOTH ANCHOR SCROLL ---- */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href').slice(1);
      const target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        const offset = 80;
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  /* ---- CONTACT FORM (if on contact page) ---- */
  const form = document.querySelector('.js-contact-form') || document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', () => {
      const btn = form.querySelector('[type=submit]');
      if (btn) {
        btn.textContent = 'Sending…';
        btn.disabled = true;
      }
    });
  }

  /* ---- COPYRIGHT YEAR ----
     Only index.html stamped this inline, so the other footers carried a
     hardcoded year that would quietly go stale on 1 January. */
  document.querySelectorAll('.js-year').forEach(el => {
    el.textContent = new Date().getFullYear();
  });

  /* ---- ACTIVE NAV LINK (legacy markup) ----
     Only onboarding.html still uses .nav-links. The main pages are handled by
     markCurrentPage() above, which reads data-page off .nav__link. */
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = a.getAttribute('href');
    a.classList.toggle('active', href === path || (path === '' && href === 'index.html'));
  });

})();

/* Create Your Team Studio — mount the visual without touching form markup. */
(function initTeamStudioArt() {
  function buildStudioArt() {
    var hero = document.querySelector('body.cc .cc-hero');
    if (!hero || hero.querySelector('.studio-art')) return;

    if (!document.querySelector('link[data-team-studio-art]')) {
      var artStyles = document.createElement('link');
      artStyles.rel = 'stylesheet';
      artStyles.href = 'team-studio-art.css?v=1';
      artStyles.setAttribute('data-team-studio-art', '');
      document.head.appendChild(artStyles);
    }

    var grid = document.createElement('div');
    grid.className = 'cc-hero-grid';
    var copy = document.createElement('div');
    copy.className = 'cc-hero-copy';
    while (hero.firstChild) copy.appendChild(hero.firstChild);

    var art = document.createElement('figure');
    art.className = 'studio-art';
    art.innerHTML = '<img src="art/agentic-team-studio.webp" width="1536" height="1024" alt="A custom AI team assembling around a luminous orchestration core" loading="eager" fetchpriority="high">' +
      '<figcaption class="studio-art__hud"><span class="studio-art__status">Team architecture online</span><span>Built around your workflow</span></figcaption>';

    grid.appendChild(copy);
    grid.appendChild(art);
    hero.appendChild(grid);
    hero.classList.add('cc-hero--agentic');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildStudioArt);
  } else {
    buildStudioArt();
  }
})();

/* ---- Restore scroll-reveal for legacy .reveal elements (homepage & inner pages) ---- */
(function () {
  function initLegacyReveal() {
    var els = document.querySelectorAll('.reveal');
    if (!els.length) return;
    if ('IntersectionObserver' in window) {
      var ob = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add('visible'); ob.unobserve(e.target); }
        });
      }, { threshold: 0.05, rootMargin: '0px 0px -10% 0px' });
      els.forEach(function (el) { ob.observe(el); });
    } else {
      els.forEach(function (el) { el.classList.add('visible'); });
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLegacyReveal);
  } else {
    initLegacyReveal();
  }
})();

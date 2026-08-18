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

/* ---- HOMEPAGE OPPORTUNITY SCANNER ---- */
(function () {
  var lab = document.querySelector('[data-diagnostic]');
  if (!lab) return;

  var solutions = {
    calls: {
      title: 'AI Employees',
      copy: 'Answer every call, qualify the lead, and book the appointment—even after hours.',
      price: 'From $497/month',
      href: 'service-ai-employees.html'
    },
    creative: {
      title: 'AI Ad Creation',
      copy: 'Put a steady stream of finished hooks, formats, and campaign variations into market.',
      price: 'From $697/month',
      href: 'service-ai-ads.html'
    },
    followup: {
      title: 'AI Business Consulting',
      copy: 'Connect your lead flow, CRM, and follow-up so every enquiry gets a fast, consistent response.',
      price: 'From $750/month',
      href: 'service-ai-consulting.html'
    },
    website: {
      title: 'Web Design & Development',
      copy: 'Replace doubt with a fast, polished website designed around the action you want visitors to take.',
      price: 'From $500 one-time',
      href: 'service-web-design.html'
    }
  };

  var title = lab.querySelector('[data-solution-title]');
  var copy = lab.querySelector('[data-solution-copy]');
  var price = lab.querySelector('[data-solution-price]');
  var link = lab.querySelector('[data-solution-link]');
  var result = lab.querySelector('.diagnostic__result');

  lab.querySelectorAll('[data-solution]').forEach(function (button) {
    button.addEventListener('click', function () {
      var solution = solutions[button.dataset.solution];
      lab.querySelectorAll('[data-solution]').forEach(function (item) {
        var active = item === button;
        item.classList.toggle('is-active', active);
        item.setAttribute('aria-pressed', String(active));
      });
      result.classList.add('is-changing');
      window.setTimeout(function () {
        title.textContent = solution.title;
        copy.textContent = solution.copy;
        price.textContent = solution.price;
        link.href = solution.href;
        result.classList.remove('is-changing');
      }, 140);
    });
  });
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

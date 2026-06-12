/* =============================================
   GreenAI Solutions Team — Main JavaScript
   ============================================= */

(function () {
  'use strict';

  /* ---- Navbar scroll behaviour ---- */
  const nav = document.querySelector('.nav');

  function updateNav() {
    if (!nav) return;
    if (window.scrollY > 40) {
      nav.classList.add('scrolled');
      nav.classList.remove('transparent');
    } else {
      nav.classList.remove('scrolled');
      // Only re-apply transparent if the page has a hero that expects it
      if (document.querySelector('.hero, .page-hero')) {
        nav.classList.add('transparent');
      }
    }
  }

  window.addEventListener('scroll', updateNav, { passive: true });
  updateNav();

  /* ---- Mobile nav toggle ---- */
  const hamburger  = document.querySelector('.nav__hamburger');
  const mobileMenu = document.querySelector('.nav__mobile');

  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      const open = hamburger.classList.toggle('open');
      mobileMenu.classList.toggle('open', open);
      hamburger.setAttribute('aria-expanded', open);
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!nav.contains(e.target)) {
        hamburger.classList.remove('open');
        mobileMenu.classList.remove('open');
        hamburger.setAttribute('aria-expanded', false);
      }
    });

    // Close on nav link click
    mobileMenu.querySelectorAll('.nav__link').forEach(link => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('open');
        mobileMenu.classList.remove('open');
      });
    });
  }

  /* ---- Smooth scroll for anchor links ---- */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const offset = 80; // nav height
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  /* ---- Scroll-reveal animation ---- */
  const revealElements = document.querySelectorAll('.reveal');

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );

    revealElements.forEach(el => observer.observe(el));
  } else {
    // Fallback for older browsers
    revealElements.forEach(el => el.classList.add('visible'));
  }

  /* ---- Active nav link highlight ---- */
  (function setActiveLink() {
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav__link[data-page]').forEach(link => {
      if (link.dataset.page === currentPath) {
        link.classList.add('active');
      }
    });
  })();

  /* ---- Contact form handling ---- */
  const form = document.querySelector('.js-contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      const btn    = form.querySelector('.form-submit');
      const origText = btn.innerHTML;

      // Basic validation
      const required = form.querySelectorAll('[required]');
      let valid = true;
      required.forEach(field => {
        field.style.borderColor = '';
        if (!field.value.trim()) {
          field.style.borderColor = '#ef4444';
          valid = false;
        }
      });

      if (!valid) {
        showFormMessage(form, 'Please fill in all required fields.', 'error');
        return;
      }

      // Email validation
      const emailField = form.querySelector('[type="email"]');
      if (emailField && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value)) {
        emailField.style.borderColor = '#ef4444';
        showFormMessage(form, 'Please enter a valid email address.', 'error');
        return;
      }

      // Simulate submission
      btn.innerHTML = '<span class="spinner"></span> Sending…';
      btn.disabled = true;

      setTimeout(() => {
        btn.innerHTML = '✓ Message Sent!';
        btn.style.background = '#16a34a';
        showFormMessage(form, "Thanks! We'll be in touch within 24 hours.", 'success');
        form.reset();

        setTimeout(() => {
          btn.innerHTML = origText;
          btn.style.background = '';
          btn.disabled = false;
        }, 4000);
      }, 1400);
    });
  }

  function showFormMessage(form, text, type) {
    let msg = form.querySelector('.form-message');
    if (!msg) {
      msg = document.createElement('div');
      msg.className = 'form-message';
      form.appendChild(msg);
    }
    msg.textContent = text;
    msg.style.cssText = `
      padding: .75rem 1rem;
      border-radius: 8px;
      font-size: .88rem;
      font-weight: 500;
      margin-top: .75rem;
      background: ${type === 'success' ? '#dcfce7' : '#fee2e2'};
      color: ${type === 'success' ? '#15803d' : '#dc2626'};
      border: 1px solid ${type === 'success' ? '#86efac' : '#fca5a5'};
    `;
  }

  /* ---- Stat counter animation ---- */
  function animateCounters() {
    const counters = document.querySelectorAll('.js-counter');
    counters.forEach(counter => {
      const target = parseFloat(counter.dataset.target);
      const prefix = counter.dataset.prefix || '';
      const suffix = counter.dataset.suffix || '';
      const decimals = counter.dataset.decimals ? parseInt(counter.dataset.decimals) : 0;
      const duration = 1800;
      const step = 16;
      const steps = duration / step;
      let current = 0;
      const increment = target / steps;

      const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
          current = target;
          clearInterval(timer);
        }
        counter.textContent = prefix + current.toFixed(decimals) + suffix;
      }, step);
    });
  }

  // Trigger counters when hero stats come into view
  const statsSection = document.querySelector('.hero__stats');
  if (statsSection && 'IntersectionObserver' in window) {
    const statsObserver = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        animateCounters();
        statsObserver.disconnect();
      }
    }, { threshold: 0.5 });
    statsObserver.observe(statsSection);
  } else if (statsSection) {
    animateCounters();
  }

})();

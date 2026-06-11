/* =============================================
   GreenAI Solutions — Next-Level JavaScript
   ============================================= */

(function () {
  'use strict';

  /* ---- NAVBAR ---- */
  const navbar = document.getElementById('navbar');
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.getElementById('navLinks');

  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });
  }

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      const open = navLinks.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', open);
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

  /* ---- HERO CANVAS PARTICLE NETWORK ---- */
  const canvas = document.getElementById('heroCanvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let W, H, particles = [], animId;

    const resize = () => {
      W = canvas.width = canvas.offsetWidth;
      H = canvas.height = canvas.offsetHeight;
    };

    const rand = (min, max) => Math.random() * (max - min) + min;

    const createParticles = () => {
      particles = [];
      const count = Math.floor((W * H) / 14000);
      for (let i = 0; i < count; i++) {
        particles.push({
          x: rand(0, W),
          y: rand(0, H),
          vx: rand(-0.3, 0.3),
          vy: rand(-0.3, 0.3),
          r: rand(1, 2.5),
          opacity: rand(0.2, 0.8)
        });
      }
    };

    const drawParticles = () => {
      ctx.clearRect(0, 0, W, H);
      const maxDist = 120;

      particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 230, 118, ${p.opacity * 0.6})`;
        ctx.fill();
      });

      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < maxDist) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(0, 230, 118, ${0.12 * (1 - dist / maxDist)})`;
            ctx.lineWidth = 0.5;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      animId = requestAnimationFrame(drawParticles);
    };

    const init = () => {
      resize();
      createParticles();
      if (animId) cancelAnimationFrame(animId);
      drawParticles();
    };

    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(init, 200);
    }, { passive: true });

    init();
  }

  /* ---- TYPING HERO TEXT ---- */
  const typingEl = document.getElementById('typingText');
  if (typingEl) {
    const words = ['Platform.', 'Social Media.', 'Every Market.', 'The Algorithm.'];
    let wi = 0, ci = 0, deleting = false, pauseTimer = null;

    const typeStep = () => {
      const word = words[wi];
      if (!deleting) {
        ci++;
        typingEl.textContent = word.slice(0, ci);
        if (ci === word.length) {
          deleting = true;
          pauseTimer = setTimeout(typeStep, 2000);
          return;
        }
      } else {
        ci--;
        typingEl.textContent = word.slice(0, ci);
        if (ci === 0) {
          deleting = false;
          wi = (wi + 1) % words.length;
        }
      }
      pauseTimer = setTimeout(typeStep, deleting ? 50 : 90);
    };

    setTimeout(typeStep, 1200);
  }

  /* ---- SCROLL-REVEAL (AOS) ---- */
  const aosObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        const delay = entry.target.dataset.delay || (i * 80);
        setTimeout(() => entry.target.classList.add('aos-visible'), Number(delay));
        aosObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('[data-aos]').forEach((el, i) => {
    el.dataset.delay = el.dataset.delay || (i % 6) * 100;
    aosObserver.observe(el);
  });

  /* ---- COUNTER ANIMATION ---- */
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.counter').forEach(el => counterObserver.observe(el));

  function animateCounter(el) {
    const target = parseInt(el.dataset.target, 10);
    const duration = 1800;
    const start = performance.now();

    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target).toLocaleString();
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target.toLocaleString();
    };

    requestAnimationFrame(step);
  }

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

  /* ---- ROI CALCULATOR ---- */
  const calcBtn = document.getElementById('calcBtn');
  if (calcBtn) {
    const run = () => {
      const rev = parseFloat(document.getElementById('calcRevenue').value) || 0;
      const followers = parseFloat(document.getElementById('calcFollowers').value) || 0;
      const adBudget = parseFloat(document.getElementById('calcAdBudget').value) || 0;
      const pkg = document.getElementById('calcPackage').value;

      const multipliers = { starter: { rev: 3.2, fol: 7.5, leads: 60, roiBase: 380 },
                             growth: { rev: 5.3, fol: 11.4, leads: 140, roiBase: 720 },
                             dominator: { rev: 8.6, fol: 18.2, leads: 280, roiBase: 1480 } };
      const m = multipliers[pkg];
      const costs = { starter: 700, growth: 1200, dominator: 1950 };
      const cost90 = costs[pkg] * 3;

      const projRev = Math.round(rev * m.rev);
      const projFol = Math.round(followers * m.fol);
      const projLeads = Math.round(m.leads + adBudget * 0.12);
      const netGain = projRev * 3 - rev * 3;
      const roi = Math.round((netGain / cost90) * 100);

      document.getElementById('projRevenue').textContent = '$' + projRev.toLocaleString();
      document.getElementById('projFollowers').textContent = projFol.toLocaleString();
      document.getElementById('projLeads').textContent = projLeads.toLocaleString();
      document.getElementById('projROI').textContent = roi.toLocaleString() + '%';

      const results = document.getElementById('calcResults');
      results.style.animation = 'none';
      results.offsetHeight;
      results.style.animation = 'fadeUp 0.4s ease both';
    };

    calcBtn.addEventListener('click', run);
    ['calcRevenue', 'calcFollowers', 'calcAdBudget', 'calcPackage'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('input', run);
    });

    run();
  }

  /* ---- CHART BARS ANIMATION ---- */
  const chartObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.querySelectorAll('.bar').forEach((bar, i) => {
          bar.style.opacity = '0';
          bar.style.transform = 'scaleY(0)';
          bar.style.transformOrigin = 'bottom';
          setTimeout(() => {
            bar.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            bar.style.opacity = '1';
            bar.style.transform = 'scaleY(1)';
          }, i * 80);
        });
        chartObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll('.dm-chart').forEach(el => chartObserver.observe(el));

  /* ---- CONTACT FORM (if on contact page) ---- */
  const form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', e => {
      const btn = form.querySelector('[type=submit]');
      if (btn) {
        btn.textContent = 'Sending…';
        btn.disabled = true;
      }
    });
  }

  /* ---- ACTIVE NAV LINK ---- */
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = a.getAttribute('href');
    a.classList.toggle('active', href === path || (path === '' && href === 'index.html'));
  });

})();

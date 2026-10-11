/* Native-scroll enhancement. Static editorial content remains usable without JS. */
(() => {
  const section = document.querySelector('.scroll-film');
  if (!section) return;
  const video = section.querySelector('video');
  const beats = [...section.querySelectorAll('.film-beat')];
  const counter = section.querySelector('.film-counter');
  const toggle = section.querySelector('.motion-toggle');
  const preference = matchMedia('(min-width: 961px) and (prefers-reduced-motion: no-preference)');
  let enabled = false, optedOut = false, visible = false, frame = 0, progress = 0;
  const update = () => {
    frame = 0;
    if (!enabled || !visible) return;
    const rect = section.getBoundingClientRect();
    const nav = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--g3-nav-h')) || 76;
    progress = Math.min(1, Math.max(0, (nav - rect.top) / Math.max(1, rect.height - innerHeight + nav)));
    section.style.setProperty('--film-progress', progress.toFixed(4));
    const active = Math.min(2, Math.floor(progress * 3));
    beats.forEach((beat, i) => {
      beat.classList.toggle('is-active', i === active);
      beat.setAttribute('aria-hidden', String(i !== active));
    });
    counter.textContent = `0${active + 1} / 03`;
    if (Number.isFinite(video.duration) && video.readyState >= 2 && !video.seeking) {
      const target = progress * Math.max(0, video.duration - 0.08);
      if (Math.abs(video.currentTime - target) > 0.08) video.currentTime = target;
    }
  };
  const schedule = () => { if (!frame) frame = requestAnimationFrame(update); };
  const configure = () => {
    enabled = preference.matches && !optedOut;
    section.classList.toggle('is-enhanced', enabled);
    toggle.hidden = !preference.matches;
    toggle.textContent = optedOut ? 'Turn motion on' : 'Turn motion off';
    if (!enabled) { video.pause(); beats.forEach(b => b.removeAttribute('aria-hidden')); }
    if (enabled && visible && !video.getAttribute('src')) { video.src = video.dataset.src; video.preload = 'auto'; }
    schedule();
  };
  toggle.addEventListener('click', () => { optedOut = !optedOut; configure(); });
  preference.addEventListener('change', configure);
  addEventListener('scroll', schedule, { passive: true });
  addEventListener('resize', schedule, { passive: true });
  video.addEventListener('loadeddata', schedule);
  video.addEventListener('seeked', schedule);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => { visible = entries[0].isIntersecting; configure(); }, { rootMargin: '300px' }).observe(section);
  } else { visible = true; }
  configure();
})();

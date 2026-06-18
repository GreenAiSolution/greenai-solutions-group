/* GreenAI Experience — UI behaviours (vanilla, no deps) */
(function () {
  function ready(fn) { document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', fn) : fn(); }
  ready(function () {
    // nav: solid background after scrolling
    var nav = document.querySelector('.xnav');
    function onScroll() { if (nav) nav.classList.toggle('solid', window.scrollY > 40); }
    onScroll(); window.addEventListener('scroll', onScroll, { passive: true });

    // mobile menu toggle
    var burger = document.querySelector('.xburger');
    var mobile = document.querySelector('.xmobile');
    if (burger && mobile) {
      burger.addEventListener('click', function () {
        var open = mobile.classList.toggle('open');
        burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      mobile.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', function () { mobile.classList.remove('open'); });
      });
    }

    // scroll reveal (adds .in); failsafe CSS guarantees visibility regardless
    var els = document.querySelectorAll('.reveal');
    if ('IntersectionObserver' in window) {
      var ob = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); ob.unobserve(e.target); } });
      }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
      els.forEach(function (el) { ob.observe(el); });
    } else {
      els.forEach(function (el) { el.classList.add('in'); });
    }
  });
})();

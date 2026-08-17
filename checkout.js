/* ============================================================================
   checkout.js — the single place every "buy" button on this site resolves to.

   Every purchase button in the HTML is written as:

       <a class="buy" data-sku="employees-front-desk">Start — $497/mo</a>

   and nothing else. No Stripe URL is ever pasted into a page. This file maps
   the SKU to its Stripe Payment Link, and on load rewrites every [data-sku]
   element's href to match.

   WHY IT IS BUILT THIS WAY
   greenaidigital.com is a static site on GitHub Pages — there is no server to
   create a Stripe Checkout Session on. Stripe Payment Links are the supported
   way to take money from a static page: they are hosted by Stripe, handle the
   card form, tax, receipts and the customer portal, and they are just URLs.

   TO GO LIVE: paste each Payment Link into LINKS below. Until a SKU has a
   link, its button falls back to /contact.html and is labelled as such, so a
   half-finished wiring never shows a customer a dead button.

   Price IDs and Payment Links are not secrets — they are safe in this file and
   in git. A secret key never belongs here, and none is needed.
   ========================================================================= */

(function () {
  'use strict';

  /* -- Stripe Payment Links, one per purchasable thing --------------------- */
  var LINKS = {
    /* AI Employees — monthly */
    'employees-front-desk':      '', /* $497/mo   · 1 employee  */
    'employees-front-follow':    '', /* $897/mo   · 2 employees */
    'employees-full-desk':       '', /* $1,497/mo · 4 employees */

    /* AI Ad Creation — monthly */
    'ads-starter':               '', /* $697/mo   · 10 ads */
    'ads-growth':                '', /* $1,297/mo · 25 ads */
    'ads-scale':                 '', /* $2,497/mo · 60 ads */

    /* AI Business Consulting — monthly */
    'consulting':                '', /* $750/mo */

    /* Web Design — one-time, plus optional monthly care */
    'web-starter':               '', /* $500   · up to 5 pages  */
    'web-business':              '', /* $1,500 · up to 10 pages */
    'web-premium':               '', /* $2,500 · custom, deposit */
    'web-maintenance':           ''  /* $150/mo */
  };

  /* -- Fallback when a SKU has no link yet ---------------------------------
     A bare link to contact.html is a dead end: the customer clicked a price
     and landed on an empty form with no idea why. So we pass the SKU along,
     and contact.html turns it into a preselected service and a plain-English
     line explaining what happened. The click becomes a qualified lead rather
     than a bounce. */
  var FALLBACK_HREF  = 'contact.html';
  var FALLBACK_TITLE = 'Card payment is being switched on — this opens the contact form instead';

  /* -- Prefill the buyer's email when we already know it ------------------- */
  function withEmail(url, email) {
    if (!email) return url;
    return url + (url.indexOf('?') === -1 ? '?' : '&') +
           'prefilled_email=' + encodeURIComponent(email);
  }

  function wire(root) {
    var nodes = (root || document).querySelectorAll('[data-sku]');
    var email = null;
    try { email = sessionStorage.getItem('greenai_email'); } catch (e) { /* private mode */ }

    Array.prototype.forEach.call(nodes, function (el) {
      var sku  = el.getAttribute('data-sku');
      var link = LINKS[sku];

      if (link) {
        el.setAttribute('href', withEmail(link, email));
        el.removeAttribute('title');
        el.removeAttribute('aria-describedby');
        el.setAttribute('rel', 'noopener');
      } else {
        el.setAttribute('href', FALLBACK_HREF + '?want=' + encodeURIComponent(sku));
        el.setAttribute('title', FALLBACK_TITLE);
        el.setAttribute('data-sku-pending', '1');
      }
    });
  }

  /* Expose for create.html, which builds its buttons after the user picks. */
  window.GreenAICheckout = {
    links: LINKS,
    wire: wire,
    linkFor: function (sku) { return LINKS[sku] || null; },
    /* Remember the email typed into the team builder so Stripe prefills it. */
    rememberEmail: function (email) {
      try { sessionStorage.setItem('greenai_email', email || ''); } catch (e) {}
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { wire(); });
  } else {
    wire();
  }
})();

/* ============================================================================
   checkout.js — the single place every "buy" button on this site resolves to.

   Every purchase button in the HTML is written as:

       <a class="buy" data-sku="employees-front-desk">Start</a>

   and nothing else. No payment URL is ever pasted into a page. This file turns
   each [data-sku] element into a link to the payment portal, preselected on
   that plan.

   WHY IT IS BUILT THIS WAY
   greenaidigital.com is static hosting on GitHub Pages: there is no server, so
   nothing here can process a payment, and collecting card numbers in
   client-side JavaScript would require PCI DSS Level 1 compliance. So the site
   never takes card details itself. Since 2026-08-20 every SKU has a hosted
   Stripe Payment Link (card entered on buy.stripe.com, not here); pay.html
   remains the invoice / bank-transfer alternative for buyers who want 0%
   processor fees, and captures the signed service agreement for that path.
   ========================================================================= */

(function () {
  'use strict';

  var PORTAL = 'pay.html';

  /* LIVE Stripe Payment Links (created 2026-08-20 in the GreenGeniusAI
     account, acct_1TYicEKX2eavW3SQ). These are hosted checkout pages on
     buy.stripe.com — card entry happens on Stripe, never on this site, so
     the site's "no card details are entered here" promise stays true.
     Each link redirects to thankyou.html?paid=<sku> after a successful
     charge. A hosted link is not a secret and is safe in git; a secret API
     key never belongs in this file, and none is needed.
     Set a value to '' to fall back to the invoice portal / contact form. */
  var CARD_LINKS = {
    'employees-front-desk': 'https://buy.stripe.com/9B63cwfpQaKxaFdgbObZe00',
    'ads-starter': 'https://buy.stripe.com/3cIaEY7Xo9GteVt2kYbZe01',
    'ads-growth': 'https://buy.stripe.com/bJe4gA0uW9GtdRp4t6bZe02',
    'ads-scale': 'https://buy.stripe.com/8x27sMcdE6uh14D3p2bZe03'
  };

  /* SKUs quoted case-by-case route to the contact form. The ads tiers left
     this list on 2026-08-20 when their Payment Links went live. */
  var QUOTE_ONLY = {};

  /* pay.html sells exactly one plan right now (the one-price rule — see
     project memory). Any other SKU has no matching radio there, so
     pay.html?sku=X would silently land the buyer on the $497 AI Employee
     plan instead of what they clicked. Only send SKUs here that pay.html
     can actually preselect; everything else goes to the contact form,
     same as a quote. */
  var PORTAL_READY = {
    'employees-front-desk': true
  };

  function wire(root) {
    var nodes = (root || document).querySelectorAll('[data-sku]');

    Array.prototype.forEach.call(nodes, function (el) {
      var sku = el.getAttribute('data-sku');

      if (QUOTE_ONLY[sku]) {
        el.setAttribute('href', 'contact.html?want=' + encodeURIComponent(sku));
        el.setAttribute('title', 'This build is quoted, not fixed — opens the quote form');
        return;
      }

      var card = Object.prototype.hasOwnProperty.call(CARD_LINKS, sku) ? CARD_LINKS[sku] : null;

      if (card === null) {
        /* Unknown SKU — the attribute is probably a typo. Send the click
           somewhere useful rather than to a portal that will ignore it. */
        el.setAttribute('href', 'contact.html?want=' + encodeURIComponent(sku));
        el.setAttribute('data-sku-unknown', '1');
        return;
      }

      if (card) {
        el.setAttribute('href', card);
        el.setAttribute('rel', 'noopener');
        el.removeAttribute('title');
        return;
      }

      if (PORTAL_READY[sku]) {
        el.setAttribute('href', PORTAL + '?sku=' + encodeURIComponent(sku));
        el.removeAttribute('title');
      } else {
        el.setAttribute('href', 'contact.html?want=' + encodeURIComponent(sku));
        el.removeAttribute('title');
      }
    });
  }

  window.GreenAICheckout = {
    portal: PORTAL,
    cardLinks: CARD_LINKS,
    wire: wire,
    /* '' means "use the portal", null means "no such SKU". */
    cardLinkFor: function (sku) {
      return Object.prototype.hasOwnProperty.call(CARD_LINKS, sku) ? CARD_LINKS[sku] : null;
    },
    hrefFor: function (sku) {
      if (QUOTE_ONLY[sku]) { return 'contact.html?want=' + encodeURIComponent(sku); }
      var card = this.cardLinkFor(sku);
      if (card === null) { return 'contact.html?want=' + encodeURIComponent(sku); }
      if (card) { return card; }
      return PORTAL_READY[sku] ? (PORTAL + '?sku=' + encodeURIComponent(sku)) : ('contact.html?want=' + encodeURIComponent(sku));
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { wire(); });
  } else {
    wire();
  }
})();

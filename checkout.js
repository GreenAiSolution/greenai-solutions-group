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
   does not take card details at all. pay.html builds the order and captures the
   signed service agreement, then Jaden invoices and the customer pays by bank
   transfer — which also means no processor takes a percentage. A card rail can add processing fees that are better handled through a hosted checkout link when needed.

   HISTORY
   Buttons now land on a working portal instead of collecting payment details on the static site.

   IF A HOSTED CARD RAIL IS ADDED LATER
   Put its hosted link in CARD_LINKS below, keyed by SKU. Any SKU with a link
   there gets a "Pay by card" behaviour instead of the portal; anything left
   empty keeps using the portal. Hosted payment links are not secrets and are
   safe in this file and in git. A secret API key never belongs here, and none
   is needed for a hosted link.
   ========================================================================= */

(function () {
  'use strict';

  var PORTAL = 'pay.html';

  /* The core funnel has one purchasable SKU. The value is a hosted
     card-checkout URL, or '' to send the buyer to the invoice portal. */
  var CARD_LINKS = {
    'employees-front-desk': ''
  };

  /* All other service pages are quoted separately and route to the contact form. */
  var QUOTE_ONLY = {
    'ads-starter': true,
    'ads-growth': true,
    'ads-scale': true,
    'consulting': true,
    'web-sub-launch': true,
    'web-sub-growth': true,
    'web-premium': true,
    'web-sub-flagship': true,
    'web-starter': true,
    'web-business': true,
    'web-maintenance': true
  };

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

/* ============================================================================
   checkout.js — the single place every "buy" button on this site resolves to.

   Every purchase button in the HTML is written as:

       <a class="buy" data-sku="employees-front-desk">Start — $497/mo</a>

   and nothing else. No payment URL is ever pasted into a page. This file turns
   each [data-sku] element into a link to the payment portal, preselected on
   that plan.

   WHY IT IS BUILT THIS WAY
   greenaidigital.com is static hosting on GitHub Pages: there is no server, so
   nothing here can process a payment, and collecting card numbers in
   client-side JavaScript would require PCI DSS Level 1 compliance. So the site
   does not take card details at all. pay.html builds the order and captures the
   signed service agreement, then Jaden invoices and the customer pays by bank
   transfer — which also means no processor takes a percentage. On a $2,497/mo
   plan a card rail would cost roughly $75 a month.

   HISTORY
   This file used to hold a map of Stripe Payment Links, every one of them an
   empty string, so every buy button on the site fell through to a contact form
   labelled "card payment is being switched on". That had been true for months.
   Buttons now land on a working portal instead.

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

  /* Every purchasable SKU. The value is a hosted card-checkout URL, or '' to
     send the buyer to the portal (bank transfer). Kept as an explicit list so a
     typo in a data-sku attribute is caught rather than silently linking to a
     portal that cannot preselect anything. */
  var CARD_LINKS = {
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
    'web-maintenance':           ''  /* $150/mo · add-on        */
  };

  /* web-premium is deliberately absent: it is "$2,500+, quoted not fixed", so
     it is not a fixed-price purchase and must not get a pay button. Its buttons
     go to the contact form for a real quote. */
  var QUOTE_ONLY = { 'web-premium': true };

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
      } else {
        el.setAttribute('href', PORTAL + '?sku=' + encodeURIComponent(sku));
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
      return card || (PORTAL + '?sku=' + encodeURIComponent(sku));
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { wire(); });
  } else {
    wire();
  }
})();

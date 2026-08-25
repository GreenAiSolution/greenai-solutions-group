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

  /* ---- THE CARD RAIL SWITCH ------------------------------------------
     ON since 2026-08-22: every SKU below is a live Payment Link in Stripe
     account acct_1U7U3XQKwkBwdEjz — Jaden's own, verified and taking charges.

     THE SELLER IS A SOLE PROPRIETOR, NOT A CORPORATION (confirmed 2026-08-25).
     Stripe has this account as business_type "individual": no company name, no
     EIN, verified personally as Jaden Green. The account's display name had
     been typed as "Green AI Solutions Inc." and that wording had spread to the
     billing lines and to every Payment Link's agreement text, so the site was
     telling customers they were buying from a corporation that was never
     filed. All of it now reads "Jaden Green, doing business as GreenAI
     Solutions". Do not reintroduce "Inc." unless a real filing exists.

     Set it back to false to park the card rail: every SKU then falls
     through to the invoice portal / intake form below, which works on its
     own and captures the signed service agreement. No other line in this
     file needs to change either way. ---------- */
  var CARD_RAIL_LIVE = true;

  /* LIVE Stripe Payment Links, rebuilt 2026-08-22 in **Green AI Solutions
     Inc.**, acct_1U7U3XQKwkBwdEjz. These are hosted checkout pages on
     buy.stripe.com — card entry happens on Stripe, never on this site, so
     the site's "no card details are entered here" promise stays true.
     Each link redirects to thankyou.html?paid=<sku> after a successful
     charge. A hosted link is not a secret and is safe in git; a secret API
     key never belongs in this file, and none is needed.
     Set a value to '' to fall back to the invoice portal / contact form.

     WHY THE BILLING ENTITY MOVED HERE, 2026-08-22
     The rail used to run through Greenvlt, which bills as PHXGROWTH — a
     name no buyer of this site has any reason to recognise, so every page
     had to apologise for it. This account bills under a name the buyer has
     just seen, so the disclosure on index.html and thankyou.html names the
     seller directly. Each product also carries its own statement descriptor
     (GREENAI AI EMPLOYEE, GREENAI ADS STARTER / GROWTH / SCALE). Keep that
     wording matching whatever Stripe actually prints — an undisclosed
     unfamiliar descriptor is what causes chargebacks.

     GOTCHA: Managed Payments is ON by default in this account, which would
     make Stripe the merchant of record and silently drops custom_text.
     All the links were created with managed_payments[enabled]=false so Jaden
     stays the seller. Any link rebuilt by hand in the dashboard has to match,
     or the agreement line disappears. */
  var CARD_LINKS = {
    'employees-front-desk': 'https://buy.stripe.com/fZubJ397leDq4yH9KY5EY04',
    'ads-starter': 'https://buy.stripe.com/9B63cx4R57aY9T15uI5EY01',
    'ads-growth': 'https://buy.stripe.com/9B628t6Zd66U2qz2iw5EY02',
    'ads-scale': 'https://buy.stripe.com/28E9AV4R552Q2qz4qE5EY03',
    /* The Staff — created 2026-08-24 in the same account, same shape
       (managed_payments off, agreement line, redirect to thankyou). */
    'agent-reply':   'https://buy.stripe.com/3cIaEZ1ETeDq9T15uI5EY06',
    'agent-boost':   'https://buy.stripe.com/dRm5kF4R5bred5d7CQ5EY07',
    'agent-answer':  'https://buy.stripe.com/28EeVfabp9j63uD6yM5EY08',
    'agent-collect': 'https://buy.stripe.com/00w14perFeDqd5d8GU5EY09',
    'full-staff':    'https://buy.stripe.com/8x28wR3N166UaX5bT65EY0a'
  };

  /* Dormant — Greenvlt acct_1U1tvI4E6AUMDj1M, the rail this site used from
     2026-08-21 to 2026-08-22. Bills as PHXGROWTH. If it is ever switched
     back on, the PHXGROWTH disclosure has to go back on index.html and
     thankyou.html with it. */
  var CARD_LINKS_GREENVLT = {
    'employees-front-desk': 'https://buy.stripe.com/5kQ8wIdlaegEgpO3QP8EM0L',
    'ads-starter': 'https://buy.stripe.com/28E8wIa8Y2xWa1q4UT8EM0M',
    'ads-growth': 'https://buy.stripe.com/00weV65SIb4s4H6afd8EM0N',
    'ads-scale': 'https://buy.stripe.com/fZu14g6WM1tSehG1IH8EM0O'
  };

  /* Dormant — GreenGeniusAI acct_1TYicEKX2eavW3SQ, blocked on verification. */
  var CARD_LINKS_GREENGENIUSAI = {
    'employees-front-desk': 'https://buy.stripe.com/9B63cwfpQaKxaFdgbObZe00',
    'ads-starter': 'https://buy.stripe.com/3cIaEY7Xo9GteVt2kYbZe01',
    'ads-growth': 'https://buy.stripe.com/bJe4gA0uW9GtdRp4t6bZe02',
    'ads-scale': 'https://buy.stripe.com/8x27sMcdE6uh14D3p2bZe03'
  };

  /* SKUs quoted case-by-case route to the contact form. The ads tiers left
     this list on 2026-08-20 when their Payment Links went live. */
  var QUOTE_ONLY = {};

  /* pay.html knows every staff SKU (since 2026-08-24 it reads ?sku= and
     shows RING / REPLY / BOOST / ANSWER / COLLECT / Full Staff with the
     right price, then hands the SKU on to start.html). The ads tiers have
     no page there yet, so with the card rail off they go to the contact
     form, same as a quote. */
  var PORTAL_READY = {
    'employees-front-desk': true,
    'agent-reply': true,
    'agent-boost': true,
    'agent-answer': true,
    'agent-collect': true,
    'full-staff': true
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

      var card = cardLinkFor(sku);

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

  /* '' means "use the portal", null means "no such SKU". A hosted link is
     only handed out once the account can actually accept the charge. */
  function cardLinkFor(sku) {
    if (!Object.prototype.hasOwnProperty.call(CARD_LINKS, sku)) { return null; }
    return CARD_RAIL_LIVE ? CARD_LINKS[sku] : '';
  }

  window.GreenAICheckout = {
    portal: PORTAL,
    cardLinks: CARD_LINKS,
    wire: wire,
    cardRailLive: CARD_RAIL_LIVE,
    cardLinkFor: function (sku) { return cardLinkFor(sku); },
    hrefFor: function (sku) {
      if (QUOTE_ONLY[sku]) { return 'contact.html?want=' + encodeURIComponent(sku); }
      var card = cardLinkFor(sku);
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

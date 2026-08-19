/* ============================================================================
   analytics.js — the one place visitor measurement is switched on.

   WHY THIS FILE EXISTS
   Until 2026-08-19 this site had no measurement of any kind. There was no way
   to tell three visitors from three hundred, or to know whether anyone reached
   the price. Every decision about the site was being made blind.

   WHAT IT USES
   Cloudflare Web Analytics. Chosen because it is free with no visitor cap, it
   sets no cookies and stores no personal profile — so it needs no cookie
   banner and no consent flow — and its dashboard is a page of plain numbers
   rather than a reporting suite. It is a client-side beacon, so it works on
   GitHub Pages with no server and without moving DNS.

   HOW TO SWITCH IT ON
   Paste the token from the Cloudflare dashboard into TOKEN below, commit, push.
   That is the whole job. Until a token is present this file does nothing at
   all — no request, no error, no console noise.

   THE FUNNEL, READ AS FOUR PAGE-VIEW NUMBERS
       /             visitors who landed
       /catch.html   watched the demo
       /pay.html     opened the order form
       /thankyou.html completed an order
   No custom event tracking is needed to see the whole path, because each step
   of this site is its own page. Do not add event tracking to get numbers that
   are already sitting in the page-view list.
   ========================================================================= */

(function () {
  'use strict';

  var TOKEN = 'cbc0cdc361e2457e85eb95976f7d5a97'; /* greenaidigital.com, added 2026-08-19 */

  if (!TOKEN) return;

  var s = document.createElement('script');
  s.defer = true;
  s.src = 'https://static.cloudflareinsights.com/beacon.min.js';
  s.setAttribute('data-cf-beacon', JSON.stringify({ token: TOKEN }));
  document.head.appendChild(s);
})();

/* ============================================================
   GreenAI Digital — G3 interactions (v1)
   Vanilla JS. No build step. No dependencies.
   ============================================================ */
(function () {
  "use strict";

  /* ---------- Footer year ---------- */
  document.querySelectorAll(".js-year").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* ---------- Nav: scroll state, mobile menu, active link ---------- */
  var nav = document.querySelector(".g3-nav");
  if (nav) {
    var onScroll = function () {
      nav.classList.toggle("is-scrolled", window.scrollY > 24);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    var burger = nav.querySelector(".g3-nav__burger");
    if (burger) {
      burger.addEventListener("click", function () {
        var open = nav.classList.toggle("open");
        burger.setAttribute("aria-expanded", open ? "true" : "false");
      });
      nav.querySelectorAll(".g3-nav__mobile a").forEach(function (a) {
        a.addEventListener("click", function () {
          nav.classList.remove("open");
          burger.setAttribute("aria-expanded", "false");
        });
      });
    }

    var page = (location.pathname.split("/").pop() || "index.html").toLowerCase();
    nav.querySelectorAll("[data-page]").forEach(function (a) {
      if (a.getAttribute("data-page") === page) a.classList.add("is-active");
    });
  }

  /* ---------- Scroll reveal ---------- */
  var revealEls = document.querySelectorAll(".rv");
  if ("IntersectionObserver" in window && revealEls.length) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- Juno call widget ---------- */
  function fmtTime(s) {
    if (!isFinite(s) || s < 0) s = 0;
    var m = Math.floor(s / 60), sec = Math.floor(s % 60);
    return m + ":" + (sec < 10 ? "0" : "") + sec;
  }
  // Deterministic pseudo-random for stable waveforms
  function seeded(n) {
    var x = Math.sin(n * 999 + 7) * 10000;
    return x - Math.floor(x);
  }

  document.querySelectorAll(".g3-call").forEach(function (widget, wi) {
    var audio = widget.querySelector("audio");
    var playBtn = widget.querySelector(".g3-call__play");
    var waves = widget.querySelector(".g3-call__waves");
    var timeEl = widget.querySelector(".g3-call__time");
    var elapsedEl = timeEl ? timeEl.querySelector("b") : null;
    var totalEl = timeEl ? timeEl.querySelector("span") : null;
    if (!audio || !playBtn || !waves) return;

    // Build waveform bars
    var BARS = 56, bars = [];
    for (var i = 0; i < BARS; i++) {
      var b = document.createElement("i");
      var h = 18 + Math.round(seeded(wi * 100 + i) * 82); // 18%..100%
      b.style.height = h + "%";
      waves.appendChild(b);
      bars.push(b);
    }

    function paint() {
      var dur = audio.duration || 0, cur = audio.currentTime || 0;
      var frac = dur > 0 ? cur / dur : 0;
      var onCount = Math.round(frac * BARS);
      bars.forEach(function (bar, i) { bar.classList.toggle("on", i < onCount); });
      if (elapsedEl) elapsedEl.textContent = fmtTime(cur);
      if (totalEl) totalEl.textContent = fmtTime(dur);
    }

    audio.addEventListener("loadedmetadata", paint);
    audio.addEventListener("timeupdate", paint);
    audio.addEventListener("ended", function () {
      widget.classList.remove("is-playing");
      playBtn.setAttribute("aria-label", "Play sample call");
      audio.currentTime = 0;
      paint();
    });
    audio.addEventListener("play", function () {
      widget.classList.add("is-playing");
      playBtn.setAttribute("aria-label", "Pause sample call");
    });
    audio.addEventListener("pause", function () {
      widget.classList.remove("is-playing");
      playBtn.setAttribute("aria-label", "Play sample call");
    });

    playBtn.addEventListener("click", function () {
      if (audio.paused) { audio.play().catch(function () {}); }
      else { audio.pause(); }
    });

    // Click-to-seek on waveform
    waves.addEventListener("click", function (ev) {
      var rect = waves.getBoundingClientRect();
      var frac = (ev.clientX - rect.left) / rect.width;
      frac = Math.max(0, Math.min(1, frac));
      if (audio.duration) audio.currentTime = frac * audio.duration;
      paint();
    });

    paint();
  });

  /* ---------- Missed-call revenue calculator ---------- */
  var calc = document.querySelector("[data-calc]");
  if (calc) {
    var tradeSel = calc.querySelector("[data-calc-trade]");
    var missedRange = calc.querySelector("[data-calc-missed]");
    var missedVal = calc.querySelector("[data-calc-missed-val]");
    var jobInput = calc.querySelector("[data-calc-job]");
    var outMonth = calc.querySelector("[data-calc-month]");
    var outYear = calc.querySelector("[data-calc-year]");
    var outVs = calc.querySelector("[data-calc-vs]");

    function money(n) {
      return "$" + Math.round(n).toLocaleString("en-US");
    }
    function compute() {
      var missed = Math.max(0, Math.min(40, parseInt(missedRange.value, 10) || 0));
      var job = Math.max(0, parseFloat(jobInput.value) || 0);
      var BOOK_RATE = 0.30; // stated assumption: 3 in 10 missed callers would have booked
      var WEEKS = 4.33;
      var monthly = missed * job * BOOK_RATE * WEEKS;
      var yearly = monthly * 12;
      if (missedVal) missedVal.textContent = missed + (missed === 1 ? " call" : " calls");
      if (outMonth) outMonth.textContent = money(monthly);
      if (outYear) {
        outYear.innerHTML = "Annualized illustration: <b>" + money(yearly) + "</b>. This is not guaranteed revenue.";
      }
      if (outVs) {
        if (monthly <= 0) { outVs.textContent = ""; }
        else {
          var months = (monthly / 297).toFixed(1);
          outVs.textContent = "Adjust the inputs to explore a hypothetical scenario. This calculator does not predict recovered revenue.";
        }
      }
    }
    // Trade presets (illustrative defaults, editable)
    if (tradeSel) {
      tradeSel.addEventListener("change", function () {
        var preset = tradeSel.options[tradeSel.selectedIndex].getAttribute("data-job");
        if (preset && jobInput) { jobInput.value = preset; }
        compute();
      });
    }
    if (missedRange) missedRange.addEventListener("input", compute);
    if (jobInput) jobInput.addEventListener("input", compute);
    compute();
  }

  /* ---------- Contact form: JSON submit with validation, loading,
     HTTP+JSON success checks, redirect-only-on-success, visible errors.
     Never claims anything is sent before the server says so. ---------- */
  var cform = document.querySelector(".js-contact-form");
  if (cform) {
    var cbtn = cform.querySelector("[type=submit]");
    var coriginal = cbtn ? cbtn.innerHTML : "";
    var cerrBox = null;

    var showFormError = function (html) {
      if (!cerrBox) {
        cerrBox = document.createElement("p");
        cerrBox.setAttribute("role", "alert");
        cerrBox.className = "g3-form__err";
        cform.appendChild(cerrBox);
      }
      cerrBox.innerHTML = html;
      cerrBox.style.display = "block";
      cerrBox.scrollIntoView({ block: "nearest", behavior: "smooth" });
    };

    cform.addEventListener("submit", function (e) {
      e.preventDefault();
      if (cerrBox) cerrBox.style.display = "none";

      /* novalidate is on the form, so run validation explicitly. */
      if (!cform.checkValidity()) { cform.reportValidity(); return; }

      if (cbtn) { cbtn.innerHTML = "Sending&hellip;"; cbtn.disabled = true; }

      /* Slow-network note: honest "sending" state, never a success claim. */
      var cok = cform.querySelector(".g3-form__ok");
      var slowT = setTimeout(function () {
        if (!cform.dataset.done && cok) cok.style.display = "block";
      }, 2500);

      var payload = {};
      new FormData(cform).forEach(function (v, k) { payload[k] = v; });
      payload.form = cform.getAttribute("data-form") || "contact";
      payload.source = cform.getAttribute("data-source") || location.host + location.pathname;

      fetch(cform.getAttribute("action"), {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(function (r) {
          if (!r.ok) throw new Error("http-" + r.status);
          return r.json().catch(function () { return { ok: false }; });
        })
        .then(function (res) {
          if (!res || !res.ok) throw new Error("rejected");
          clearTimeout(slowT);
          if (cok) cok.style.display = "none";
          cform.dataset.done = "1";
          window.location.href = cform.getAttribute("data-redirect") || "thankyou.html";
        })
        .catch(function () {
          clearTimeout(slowT);
          if (cok) cok.style.display = "none";
          if (cbtn) { cbtn.innerHTML = coriginal; cbtn.disabled = false; }
          /* Nothing typed is lost: the email link carries every answer, so one
             tap in their own mail app sends the same message. */
          var lines = [];
          new FormData(cform).forEach(function (v, k) {
            if (k === "botcheck" || !String(v).trim()) return;
            lines.push(k.replace(/_/g, " ") + ": " + v);
          });
          var mail = "mailto:jaden@greenaidigital.com?subject=" + encodeURIComponent("Website enquiry") +
                     "&body=" + encodeURIComponent(lines.join("\n").slice(0, 1800));
          showFormError("That did not go through on our side. " +
            '<a href="' + mail + '">Send it by email instead</a> ' +
            "(your answers are already filled in), or call " +
            '<a href="tel:4807980753">(480) 798-0753</a>.');
        });
    });
  }
})();

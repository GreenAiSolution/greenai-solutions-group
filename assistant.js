/* ==========================================================================
   Juno — GreenAI site assistant
   A conversational guide that knows the whole site. Client-side, no backend.
   ========================================================================== */
(function () {
  'use strict';

  /* ---------------- Knowledge base ---------------- */
  var KB = {
    brand: 'GreenAI Digital',
    phone: '(480) 798-0753',
    email: 'hello@greenaidigital.com',
    town: 'Gilbert, Arizona',
    services: [
      { name: 'AI Employees', page: 'ai-employees.html', from: '$297/mo',
        blurb: 'Six AI staff inside the tools you already run. They answer calls, reply to leads, book jobs and follow up, at any hour.' },
      { name: 'Creative AI Ads', page: 'creative-ai-ads.html', from: '$697/mo',
        blurb: 'Finished, scroll-stopping ads made by AI, delivered every month in every size the platforms need.' }
    ],
    pricing: {
      employees: [
        { name: 'Essential', price: '$297/mo', desc: '1 AI employee of your choice' },
        { name: 'Professional', price: '$597/mo', desc: '3 AI employees', tag: 'Most popular' },
        { name: 'Workforce', price: '$997/mo', desc: 'All 6 AI employees' }
      ],
      ads: [
        { name: 'Starter', price: '$697/mo', desc: '10 finished ads a month' },
        { name: 'Growth', price: '$1,297/mo', desc: '25 finished ads a month', tag: 'Most popular' },
        { name: 'Dominate', price: '$2,497/mo', desc: '60 finished ads a month' }
      ],
      bundle: 'Bundle both services and save 15%, plus free setup (normally $497 per service).',
      terms: 'Everything is month to month. No contracts, cancel anytime.'
    },
    pages: {
      'pricing': 'pricing.html', 'price': 'pricing.html', 'cost': 'pricing.html',
      'employee': 'ai-employees.html', 'receptionist': 'ai-employees.html',
      'ads': 'creative-ai-ads.html', 'advertising': 'creative-ai-ads.html',
      'work': 'testimonials.html', 'portfolio': 'testimonials.html', 'examples': 'testimonials.html',
      'about': 'about.html', 'contact': 'contact.html', 'talk': 'contact.html',
      'faq': 'faq.html', 'question': 'faq.html'
    }
  };

  var FAQS = [
    { k: ['contract', 'locked in', 'commitment', 'cancel'], a: 'No contracts, ever. Everything is month to month and you can cancel anytime. That is the whole point, the work has to earn its keep.' },
    { k: ['how long', 'how fast', 'launch', 'start', 'setup'], a: 'Most businesses are live within 7 days of the setup call. One call, we connect to your phone, calendar and tools, and the AI goes to work.' },
    { k: ['wrong', 'mistake', 'trust', 'control'], a: 'You set the boundaries and approve the playbook before anything goes live. Nothing goes to a customer outside the rules you set.' },
    { k: ['own', 'files', 'mine'], a: 'You own everything. Every ad file delivered is yours, and your data stays yours.' },
    { k: ['trade', 'industry', 'roof', 'hvac', 'plumb'], a: 'If you serve local customers and take calls, yes. Roofing, HVAC, plumbing, pools, landscaping, salons, restaurants, and more.' },
    { k: ['human', 'person', 'real person', 'someone', 'call me'], a: 'Of course. The fastest way is the contact page, tell us what you need and we reply personally, usually the same day.' },
    { k: ['where', 'located', 'based'], a: 'We are in Gilbert, Arizona, and we work with contractors all over the US.' },
    { k: ['hour', 'open', 'when'], a: 'The AI employees work 24/7, obviously. For us humans, send a message anytime and we reply the same day.' }
  ];

  /* ---------------- Intent matching ---------------- */
  var INTENTS = [
    { id: 'greeting', k: ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'yo', 'sup'] },
    { id: 'pricing', k: ['price', 'pricing', 'cost', 'how much', 'charge', 'fee', 'expensive', 'cheap'] },
    { id: 'pricing_employees', k: ['employee price', 'employee cost', '297', '597', '997', 'staff price'] },
    { id: 'pricing_ads', k: ['ad price', 'ad cost', '697', '1297', '2497', 'ads cost'] },
    { id: 'bundle', k: ['bundle', 'both', 'discount', 'deal', 'together', 'combo', '15%'] },
    { id: 'employees', k: ['employee', 'receptionist', 'answer call', 'phone', 'staff', 'inbox', 'jobber', 'slack', 'teams', 'quickbooks'] },
    { id: 'ads', k: ['ad ', 'ads', 'advertising', 'creative', 'marketing', 'video ad', 'commercial'] },
    { id: 'services', k: ['service', 'offer', 'what do you do', 'do you do'] },
    { id: 'work', k: ['work', 'portfolio', 'example', 'show me', 'proof', 'client'] },
    { id: 'contact', k: ['contact', 'talk', 'human', 'person', 'call me', 'email', 'reach'] },
    { id: 'thanks', k: ['thank', 'thanks', 'thx', 'appreciated', 'great', 'awesome', 'perfect'] },
    { id: 'bye', k: ['bye', 'goodbye', 'see you', 'later', 'gtg'] },
    { id: 'who', k: ['who are you', 'your name', 'what are you', 'robot', 'ai ', 'bot'] }
  ];

  /* ---------------- State ---------------- */
  var state = { name: null, greeted: false, askedName: false, history: [] };

  /* ---------------- Helpers ---------------- */
  function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

  var ACKS = ['Got it.', 'Good question.', 'Sure thing.', 'Absolutely.', 'Of course.'];
  var FILLERS = ['Let me pull that up.', 'One sec.', 'Let me think about that.'];

  function matchIntent(text) {
    var t = ' ' + text.toLowerCase() + ' ';
    var best = null, bestScore = 0;
    INTENTS.forEach(function (in_) {
      var score = 0;
      in_.k.forEach(function (kw) { if (t.indexOf(kw) !== -1) score += kw.length; });
      if (score > bestScore) { bestScore = score; best = in_.id; }
    });
    if (bestScore < 3) {
      for (var i = 0; i < FAQS.length; i++) {
        var hit = FAQS[i].k.some(function (kw) { return t.indexOf(kw) !== -1; });
        if (hit) return 'faq_' + i;
      }
      return 'unknown';
    }
    return best;
  }

  /* ---------------- Responses ---------------- */
  function pricingText() {
    var e = KB.pricing.employees, a = KB.pricing.ads;
    return 'Here is the full picture.<br><br><b>AI Employees</b><br>' +
      e.map(function (t) { return t.name + ' ' + t.price + ' — ' + t.desc + (t.tag ? ' (' + t.tag + ')' : ''); }).join('<br>') +
      '<br><br><b>Creative AI Ads</b><br>' +
      a.map(function (t) { return t.name + ' ' + t.price + ' — ' + t.desc + (t.tag ? ' (' + t.tag + ')' : ''); }).join('<br>') +
      '<br><br>' + KB.pricing.bundle + '<br>' + KB.pricing.terms;
  }

  function respond(text) {
    var intent = matchIntent(text);
    var name = state.name ? ', ' + esc(state.name) : '';
    var r = { html: '', chips: [], actions: [] };

    switch (intent) {
      case 'greeting': {
        var h = new Date().getHours();
        var tod = h < 12 ? 'morning' : (h < 17 ? 'afternoon' : 'evening');
        r.html = pick([
          'Hey' + name + ', good ' + tod + '. I am Juno, I know this site inside out. What can I help you with?',
          'Hi there' + name + '. Good ' + tod + '. Ask me about the services, pricing, or anything else, I will point you the right way.'
        ]);
        r.chips = ['What do you offer?', 'Show me pricing', 'I want to talk to a human'];
        break;
      }
      case 'pricing':
        r.html = pick(ACKS) + ' ' + pricingText();
        r.actions = [{ label: 'See full pricing', href: 'pricing.html', primary: true }];
        r.chips = ['Tell me about the bundle', 'AI Employees details'];
        break;
      case 'pricing_employees': {
        var e = KB.pricing.employees;
        r.html = '<b>AI Employees</b><br>' + e.map(function (t) {
          return t.name + ' ' + t.price + ' — ' + t.desc + (t.tag ? ' (' + t.tag + ')' : '');
        }).join('<br>') + '<br><br>' + KB.pricing.terms;
        r.actions = [{ label: 'AI Employees page', href: 'ai-employees.html' }, { label: 'See all pricing', href: 'pricing.html', primary: true }];
        break;
      }
      case 'pricing_ads': {
        var a = KB.pricing.ads;
        r.html = '<b>Creative AI Ads</b><br>' + a.map(function (t) {
          return t.name + ' ' + t.price + ' — ' + t.desc + (t.tag ? ' (' + t.tag + ')' : '');
        }).join('<br>') + '<br><br>' + KB.pricing.terms;
        r.actions = [{ label: 'Creative AI Ads page', href: 'creative-ai-ads.html' }, { label: 'See all pricing', href: 'pricing.html', primary: true }];
        break;
      }
      case 'bundle':
        r.html = pick(['Smart move, that is the best value on the site. ', 'Good thinking. ']) + KB.pricing.bundle + '<br><br>' + KB.pricing.terms;
        r.actions = [{ label: 'See pricing', href: 'pricing.html', primary: true }, { label: 'Talk to us', href: 'contact.html' }];
        break;
      case 'employees':
        r.html = 'The AI Employees are six AI staff that live inside the tools you already run: your phone line, Jobber, Gmail, Slack, Teams and QuickBooks. They answer every call, reply to every lead, book the jobs and follow up, at any hour. Plans run $297 to $997 a month.';
        r.actions = [{ label: 'Meet the six', href: 'ai-employees.html', primary: true }];
        r.chips = ['How much?', 'What about the ads?'];
        break;
      case 'ads':
        r.html = 'Creative AI Ads are finished, scroll-stopping ads made by AI and directed for contractors. You get 10, 25 or 60 fresh ads every month, in every size the platforms need, and you own every file. Plans run $697 to $2,497 a month.';
        r.actions = [{ label: 'See how it works', href: 'creative-ai-ads.html', primary: true }];
        r.chips = ['How much?', 'What about AI Employees?'];
        break;
      case 'services':
        r.html = 'Two services, nothing else.<br><br><b>AI Employees</b> (from $297/mo) — AI staff that answer your calls and book your jobs 24/7.<br><br><b>Creative AI Ads</b> (from $697/mo) — finished AI-made ads delivered monthly.';
        r.actions = [{ label: 'AI Employees', href: 'ai-employees.html' }, { label: 'Creative AI Ads', href: 'creative-ai-ads.html' }];
        break;
      case 'work':
        r.html = 'You can see real sites we have built on the Work page. Every one was designed to book jobs, not just look nice.';
        r.actions = [{ label: 'See the work', href: 'testimonials.html', primary: true }];
        break;
      case 'contact':
        r.html = pick([
          'Happy to point you to a human. The contact page is the fastest way, tell us what you need and we reply personally, usually the same day. You can also call ' + KB.phone + '.',
          'Of course. Head to the contact page and send us a message, a real person replies, usually the same day. Or call ' + KB.phone + '.'
        ]);
        r.actions = [{ label: 'Contact us', href: 'contact.html', primary: true }];
        break;
      case 'thanks':
        r.html = pick(['Anytime' + name + '.', 'Happy to help' + name + '.', 'You got it' + name + '.']) + ' Anything else I can point you to?';
        r.chips = ['Show me pricing', 'Talk to a human'];
        break;
      case 'bye':
        r.html = pick(['See you soon' + name + '.', 'Talk soon' + name + '.']) + ' Good luck out there.';
        break;
      case 'who':
        r.html = 'I am Juno, GreenAI Digital\u2019s site guide. I know every page, every price and every answer on this site. Think of me as the friendly front desk, ask me anything.';
        r.chips = ['What do you offer?', 'Show me pricing'];
        break;
      default:
        if (intent.indexOf('faq_') === 0) {
          var f = FAQS[parseInt(intent.slice(4), 10)];
          r.html = f.a;
          r.chips = ['Show me pricing', 'Talk to a human'];
        } else {
          r.html = pick([
            'Hmm, I want to make sure I get you the right answer. Are you asking about pricing, the services, or something else?',
            'I am not sure I caught that. I know the services, the pricing and the whole site. What are you looking for?',
            'Let me be honest, that one is outside what I know. I can help with the services, pricing, or getting you to a human. Which sounds right?'
          ]);
          r.chips = ['Show me pricing', 'What do you offer?', 'Talk to a human'];
        }
    }
    return r;
  }

  /* ---------------- Name capture ---------------- */
  function maybeCaptureName(text) {
    if (state.name || state.askedName) return false;
    var m = /^(?:i am|i'm|im|my name is|call me|this is)\s+([a-zA-Z]{2,20})/i.exec(text.trim());
    if (m) {
      state.name = m[1].charAt(0).toUpperCase() + m[1].slice(1);
      return true;
    }
    return false;
  }

  /* ---------------- UI ---------------- */
  var panel, msgs, input, launcher;
  var opened = false;

  function buildUI() {
    launcher = document.createElement('button');
    launcher.id = 'juno-launcher';
    launcher.setAttribute('aria-label', 'Chat with Juno');
    launcher.innerHTML =
      '<span class="juno-dot"></span>' +
      '<svg class="juno-icon-chat" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>' +
      '<svg class="juno-icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>';

    panel = document.createElement('div');
    panel.id = 'juno-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Chat with Juno');
    panel.innerHTML =
      '<div class="juno-head"><div class="juno-avatar">N</div>' +
      '<div><h3>Juno</h3><p><span class="juno-online">\u25cf</span> Online — knows the whole site</p></div></div>' +
      '<div id="juno-messages"></div>' +
      '<div class="juno-inputbar"><input id="juno-input" type="text" placeholder="Ask me anything..." autocomplete="off" aria-label="Message Juno"/>' +
      '<button id="juno-send" aria-label="Send">\u2191</button></div>';

    document.body.appendChild(launcher);
    document.body.appendChild(panel);
    msgs = panel.querySelector('#juno-messages');
    input = panel.querySelector('#juno-input');

    launcher.addEventListener('click', toggle);
    panel.querySelector('#juno-send').addEventListener('click', send);
    input.addEventListener('keydown', function (e) { if (e.key === 'Enter') send(); });
  }

  function toggle() {
    opened = !opened;
    launcher.classList.toggle('juno-open', opened);
    panel.classList.toggle('juno-open', opened);
    if (opened && !state.greeted) {
      state.greeted = true;
      setTimeout(function () {
        botSay('Hey, I am Juno. I know this whole site, the services, the pricing, all of it. What are you looking for?',
          ['What do you offer?', 'Show me pricing', 'Talk to a human']);
      }, 400);
    }
    if (opened) setTimeout(function () { input.focus(); }, 350);
  }

  function addMsg(html, who, extras) {
    var d = document.createElement('div');
    d.className = 'juno-msg juno-' + who;
    d.innerHTML = html;
    if (extras) {
      if (extras.chips && extras.chips.length) {
        var c = document.createElement('div');
        c.className = 'juno-chips';
        extras.chips.forEach(function (ch) {
          var b = document.createElement('button');
          b.className = 'juno-chip'; b.textContent = ch;
          b.addEventListener('click', function () { userSay(ch); });
          c.appendChild(b);
        });
        d.appendChild(c);
      }
      if (extras.actions && extras.actions.length) {
        var a = document.createElement('div');
        a.className = 'juno-actions';
        extras.actions.forEach(function (ac) {
          var l = document.createElement('a');
          l.className = 'juno-action' + (ac.primary ? ' juno-primary' : '');
          l.href = ac.href; l.textContent = ac.label;
          a.appendChild(l);
        });
        d.appendChild(a);
      }
    }
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
    return d;
  }

  function botSay(html, chips, actions) {
    var typing = document.createElement('div');
    typing.className = 'juno-msg juno-bot juno-typing';
    typing.innerHTML = '<i></i><i></i><i></i>';
    msgs.appendChild(typing);
    msgs.scrollTop = msgs.scrollHeight;
    var delay = Math.min(700 + html.replace(/<[^>]+>/g, '').length * 18, 2600);
    setTimeout(function () {
      typing.remove();
      addMsg(html, 'bot', { chips: chips, actions: actions });
    }, delay);
  }

  function userSay(text) {
    text = text.trim();
    if (!text) return;
    addMsg(esc(text), 'user');
    input.value = '';
    state.history.push(text);

    var named = maybeCaptureName(text);
    var doFill = Math.random() < 0.25 && text.length > 40;

    setTimeout(function () {
      if (named) {
        botSay('Nice to meet you, ' + esc(state.name) + '. So, what can I help you with?',
          ['What do you offer?', 'Show me pricing']);
        return;
      }
      if (doFill) {
        var t = document.createElement('div');
        t.className = 'juno-msg juno-bot juno-typing';
        t.innerHTML = '<i></i><i></i><i></i>';
        msgs.appendChild(t); msgs.scrollTop = msgs.scrollHeight;
        setTimeout(function () {
          t.innerHTML = esc(pick(FILLERS));
          setTimeout(function () {
            t.remove();
            var r = respond(text);
            botSay(r.html, r.chips, r.actions);
          }, 900);
        }, 700);
        return;
      }
      var r = respond(text);
      botSay(r.html, r.chips, r.actions);
    }, 350);
  }

  function send() { userSay(input.value); }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildUI);
  } else { buildUI(); }
})();

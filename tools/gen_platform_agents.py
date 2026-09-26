#!/usr/bin/env python3
"""
gen_platform_agents.py — writes the six platform-agent pages (ring, dispatch,
inbox, thread, huddle, books) and staff.html in the showroom layout
(2026-09-17: the owner asked for the site to look like sintra.ai's AI-employee
pages, in GreenAI's niche).

    python3 tools/gen_platform_agents.py

Every price is the one already live on the Stripe links in checkout.js. No
customer names, counts or results anywhere: the mocks use fictional people and
say so. After running, re-inject the shared chrome if nav.html changed:
    python3 tools/shared-nav/inject.py ring.html dispatch.html inbox.html thread.html huddle.html books.html staff.html
"""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from robots import robot, bust, peek, seals, ACCENT
HERO_POSE={"ring":"wave","dispatch":"point","inbox":"fly","thread":"think","huddle":"stand","books":"sit"}
BAND_POSE={"ring":"fly","dispatch":"sit","inbox":"wave","thread":"point","huddle":"fly","books":"wave"}
STAFF_POSE={"ring":"stand","dispatch":"fly","inbox":"wave","thread":"sit","huddle":"point","books":"think"}
CARD_POSE={"ring":"think","dispatch":"wave","inbox":"point","thread":"fly","huddle":"sit","books":"stand"}
STAFF_W=[150,190,165,175,160,185]
WIN={"ring":"Phone · incoming call","dispatch":"Jobber · request #1187","inbox":"Gmail · inbox","thread":"Slack · #leads","huddle":"Teams · Ops · General","books":"QuickBooks · invoices"}
ORBIT='<svg class="ag-orbit" viewBox="0 0 300 300" aria-hidden="true"><ellipse cx="150" cy="170" rx="140" ry="44" fill="none" stroke="var(--ac,#7DE3A4)" stroke-opacity=".35" stroke-width="1.5" transform="rotate(-14 150 170)"/><circle r="6" fill="var(--ac,#7DE3A4)"><animateMotion dur="9s" repeatCount="indefinite" path="M290 135 A140 44 -14 1 1 10 205 A140 44 -14 1 1 290 135z"/></circle><circle cx="150" cy="170" r="118" fill="var(--ac,#7DE3A4)" fill-opacity=".08"/></svg>'
ICON_OF={"ring":"phone","dispatch":"user","inbox":"inbox","thread":"message","huddle":"sun","books":"receipt"}
STARS='<svg class="sn-stars" viewBox="0 0 1400 700" preserveAspectRatio="none" aria-hidden="true"><g fill="#fff">' + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" opacity="{o}"/>' for x,y,r,o in [(80,60,1.5,.7),(200,140,1,.5),(330,40,2,.6),(520,90,1,.4),(700,30,1.5,.7),(880,120,1,.5),(1040,50,2,.6),(1180,160,1,.4),(1320,70,1.5,.7),(150,300,1,.35),(1250,320,1,.35),(60,520,1.5,.4),(1350,560,1.5,.4),(640,600,1,.3)]) + '</g><circle cx="1240" cy="120" r="46" fill="none" stroke="#7DE3A4" stroke-opacity=".25" stroke-width="1.5"/><ellipse cx="1240" cy="120" rx="78" ry="22" fill="none" stroke="#7DE3A4" stroke-opacity=".3" stroke-width="1.5" transform="rotate(-18 1240 120)"/><circle cx="150" cy="150" r="24" fill="#7DE3A4" fill-opacity=".14"/><circle cx="142" cy="142" r="6" fill="#7DE3A4" fill-opacity=".25"/></svg>'

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV = open(os.path.join(ROOT, "tools/shared-nav/nav.html")).read().rstrip("\n")
FOOT = open(os.path.join(ROOT, "tools/shared-nav/footer.html")).read().rstrip("\n")
TECH_V = 12; STYLE_V = 22; SCRIPT_V = 15; CHECKOUT_V = 8

def esc(s): return html.escape(s, quote=False)

# ---------------------------------------------------------------- icons (Lucide-style, inline)
I = {
 "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
 "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.39 2 2 0 0 1 3.6 1h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.6a16 16 0 0 0 6 6l.91-.91a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
 "calendar": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="3"/><path d="M16 2v4M8 2v4M3 10h18M9 16l2 2 4-4"/></svg>',
 "message": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
 "note": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>',
 "alert": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/></svg>',
 "inbox": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.5 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.5-6.9A2 2 0 0 0 16.7 4H7.3a2 2 0 0 0-1.8 1.1z"/></svg>',
 "user": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6M22 11h-6"/></svg>',
 "send": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/></svg>',
 "bell": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>',
 "repeat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/></svg>',
 "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
 "star": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m12 2 3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/></svg>',
 "folder": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2z"/></svg>',
 "tag": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12.6 2.6 21.4 11.4a2 2 0 0 1 0 2.8l-7.2 7.2a2 2 0 0 1-2.8 0L2.6 12.6A2 2 0 0 1 2 11.2V4a2 2 0 0 1 2-2h7.2a2 2 0 0 1 1.4.6z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>',
 "pen": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.8 2.8 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5z"/></svg>',
 "book": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
 "sun": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
 "lock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
 "help": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/></svg>',
 "receipt": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1z"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8M12 17.5v-11"/></svg>',
 "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.1V12a10 10 0 1 1-5.9-9.1"/><path d="m9 11 3 3L22 4"/></svg>',
 "sheet": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18"/></svg>',
 "hand": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 11V6a2 2 0 0 0-4 0v5"/><path d="M14 10V4a2 2 0 0 0-4 0v2"/><path d="M10 10.5V6a2 2 0 0 0-4 0v8"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/></svg>',
 "pause": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M10 15V9M14 15V9"/></svg>',
 "plug": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22v-5M9 8V2M15 8V2M18 8v5a6 6 0 0 1-12 0V8z"/></svg>',
 "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>',
 "key": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m21 2-2 2m-7.6 7.6a5.5 5.5 0 1 1-7.8 7.8 5.5 5.5 0 0 1 7.8-7.8zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>',
 "off": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18.36 6.64A9 9 0 1 1 5.64 6.64"/><path d="M12 2v10"/></svg>',
}

TM = "Slack, Microsoft Teams, Google Workspace, Gmail, Jobber, Housecall Pro, ServiceTitan, QuickBooks, RingCentral, Nextiva and Zoom are trademarks of their respective owners. GreenAI Solutions builds on their published APIs and is not affiliated with or endorsed by any of them."

# ---------------------------------------------------------------- the six
AGENTS = [
 dict(id="ring", n="01", name="RING", sku="agent-ring", price=497, short="your phone line",
      inside="inside your phone line", app="your phone line", vendors="RingCentral, Nextiva, Zoom Phone, or the number you already have",
      h1='RING answers <em>your phone.</em>',
      sub="Nights, weekends, the second caller while you are on a job. It picks up in about eight seconds, sounds like your company, books the appointment and texts back anyone who hung up.",
      state=["Most small companies do not lose the job to a competitor. They lose it to a phone that rang out at 6:40 on a Tuesday while you were under a sink.",
             "The caller does not leave a voicemail. They call the next name on the list.",
             "{who} picks up in about eight seconds, every time, and books it into the calendar you already keep."],
      does=[("phone","Picks up in about eight seconds","Any hour. It never puts a caller in a queue and never says \"our office is closed\"."),
            ("calendar","Books into your calendar","Asks the questions you always ask, offers the slots you gave it, confirms by text."),
            ("message","Texts back the ones who hung up","A missed call gets a text within a minute, so the lead does not call the next company."),
            ("note","Takes a message when it does not know","It will not invent a price or a promise. It says so and gets you the details."),
            ("alert","Flags a real emergency to you","A burst pipe at 2am reaches your phone as a text with the address, not as a voicemail."),
            ("sheet","Every call in writing","Transcript and summary in your inbox, or in Slack or Teams if you run those.")],
      connect=[("key","Your number stays yours","Forward your existing line to RING, or it takes a line on RingCentral, Nextiva or Zoom Phone. You keep the number either way."),
               ("book","Trained on your business","Services, prices, hours, service area and the way you say things. You read every script before a caller hears it."),
               ("off","Off in one call","Cancel at the end of the month and the forwarding is removed the same day.")],
      faq=[("Will callers know it is not a person?","If they ask, it tells the truth. It does not pretend to be human and does not use a fake name."),
           ("What about calls it cannot handle?","It takes a message with the details and texts you. Nothing is invented to fill the gap."),
           ("Do I need a new phone system?","No. Forwarding your current number is enough. If you want a proper business line, RingCentral, Nextiva or Zoom Phone all work.")],
      bubbles=[("RING · 9:47 PM","Booked Mon 8:00 for 1412 E Palo Verde. Pump noise, told them to switch it off tonight. Transcript in your inbox."),
               ("RING · 2:12 AM","Burst pipe on Ray Rd. Texted you the address and the caller's number. Nothing booked; this one is yours."),
               ("RING · 11:05 AM","Missed call from (480) 555-0177 while you were on the line. Texted them back at 11:06; they want a quote Thursday.")],
      mock='''<div class="ag-call"><div class="ag-call__top"><span><i></i>Incoming · (480) 555-0142</span><b class="ag-t" data-from="0" data-to="8">0:00</b></div>
<ul class="ag-lines"><li class="them">Hi, is this the heating and air company? My AC is blowing warm air and it's Sunday.</li>
<li class="us" data-who="RING · answered in 0:08">It is. Sorry, that is no fun on a hot day. Can I get the address? I can book the first visit tomorrow morning.</li>
<li class="them">Yeah, 1412 E Palo Verde, Gilbert.</li>
<li class="us typing" data-who="RING"><span class="caret"></span></li></ul>
<div class="ag-call__foot">Owner texted: "AC blowing warm, 1412 E Palo Verde, booked Mon 8:00. Transcript attached."</div></div>'''),
 dict(id="dispatch", n="02", name="DISPATCH", sku="agent-dispatch", price=497, short="Jobber, Housecall Pro or ServiceTitan",
      inside="inside Jobber, Housecall Pro or ServiceTitan", app="Jobber, Housecall Pro or ServiceTitan", vendors="Jobber, Housecall Pro and ServiceTitan",
      h1='DISPATCH works inside <em>Jobber.</em> Or Housecall Pro. Or ServiceTitan.',
      sub="The tool you already run the day out of becomes the place every lead lands, every quote goes out from and every visit gets confirmed, without you typing any of it.",
      state=["The lead came in at 9:47 on a Friday night. By Monday it was a client, a request, a quote and a Thursday slot, and nobody in the office typed a word of it.",
             "The same tool you already open every morning. Nothing to copy over, nothing to log into.",
             "{who} does the typing you have been doing at the kitchen table."],
      does=[("user","Turns a lead into a client and a request","Web form, text, call or Google message: the client and the request exist in your tool within a minute."),
            ("send","Sends the quote from your price list","For the jobs you have priced, it quotes and sends. For the rest it gathers the photos and details and hands it to you."),
            ("bell","Confirms and reminds every visit","Booking confirmation, day-before reminder, on-my-way text, all from the schedule in your tool."),
            ("repeat","Chases quotes that went quiet","Day two, five and ten, politely, until they accept or say no."),
            ("clock","Answers \"when is my tech coming\"","From the live schedule, so nobody has to stop driving to check."),
            ("star","Asks for the review after the visit","Once the job is marked complete and the customer is happy.")],
      connect=[("plug","Through the platform's own API","Jobber and Housecall Pro expose an API on their higher plans; ServiceTitan grants access through its developer program. I check what your account allows before you pay anything."),
               ("folder","Your data stays in your tool","DISPATCH writes clients, requests, quotes and notes into your account. Nothing lives somewhere else."),
               ("check","You approve every message","Confirmations, reminders and quote follow-ups are read by you before a customer sees one.")],
      faq=[("Which plan of Jobber or Housecall Pro do I need?","The one that exposes their API; both gate it to higher tiers. I check your account before you pay anything, and if it will not work you hear that first."),
           ("Does it replace Jobber, Housecall Pro or ServiceTitan?","No. It works inside them. Your schedule, clients and invoices stay exactly where they are."),
           ("What if a customer asks for a job I have not priced?","It gathers the details and photos and hands the quote to you. It never guesses a number.")],
      bubbles=[("DISPATCH · 9:48 PM","New request #1187 from the website. Client created, quoted $285 from your price list, holding Thursday 9:00 on Route B."),
               ("DISPATCH · Wed 6:00 PM","Reminder sent to M. Ortega for tomorrow's 9:00. On-my-way text queued for when the job before it closes."),
               ("DISPATCH · Day 5","Henderson quote still open. Second nudge sent in your wording. Stops after day ten unless they answer.")],
      mock='''<div class="ag-job"><div class="ag-job__head"><span>Request #1187</span><b>Palo Verde · AC repair</b></div>
<ol class="ag-flow"><li class="done"><b>Lead in</b><span>Website form, 9:47 PM</span></li><li class="done"><b>Client created</b><span>M. Ortega · Gilbert 85296</span></li><li class="done"><b>Quote sent</b><span>From your price list · $285</span></li><li class="on"><b>Scheduled</b><span>Thu 9:00 · Route B</span></li><li><b>Reminder</b><span>Wed 6:00 PM, automatic</span></li></ol>
<div class="ag-job__foot">Written into your account. Nothing to copy over.</div></div>'''),
 dict(id="inbox", n="03", name="INBOX", sku="agent-inbox", price=397, short="Google Workspace",
      inside="inside Google Workspace", app="Google Workspace", vendors="Gmail, Google Calendar and Drive",
      h1='INBOX works inside <em>Gmail.</em>',
      sub="Every lead that lands in your inbox gets a reply in under a minute, a follow-up on day one, three and seven, and a spot on your Google Calendar. You see all of it in Sent.",
      state=["The email that asked for a weekly quote on Tuesday got answered on Thursday, and by then they had hired someone who answered on Tuesday.",
             "Not because you did not care. Because there were forty others above it.",
             "{who} replies in under a minute, in your words, and every message it sends is right there in Sent."],
      does=[("send","Replies to every new lead in under a minute","From the replies you approved, with the customer's details filled in and your questions asked."),
            ("calendar","Books into Google Calendar","Offers the slots you allow, sends the invite, adds the address and notes."),
            ("repeat","Follows up until they answer","Day one, three and seven. Stops the moment they say stop."),
            ("folder","Files what matters to Drive","Quotes, photos and signed forms land in the folder you chose, named the way you name things."),
            ("tag","Labels and summarises the rest","Every morning: what needs you, what it handled, what it was not sure about."),
            ("pen","Drafts, never sends, anything unusual","A complaint, a refund, a legal question: drafted and waiting for you.")],
      connect=[("user","Signs in as its own user in your Workspace","You create a user for it, or give it delegated access to the inbox you choose. Every message it sends is in Sent under that name."),
               ("shield","Google's own permissions","Gmail, Calendar and Drive scopes only, listed in writing. Revoke them in your admin console any time."),
               ("check","You read every template first","Nothing goes to a customer until you have read the wording.")],
      faq=[("Can I see what it sent?","Everything is in Sent, under its own user, the same as any employee's mail."),
           ("What does it do with a complaint?","Drafts a reply and leaves it in Drafts for you. It never sends anything unusual on its own."),
           ("Does it read my whole inbox?","Only the inbox and folders you give it access to, with Google's own permissions listed in writing.")],
      bubbles=[("INBOX · 7 min ago","Replied to Dana R. about an AC tune-up in 0:41. Asked which day works and whether someone will be home. Holding Thursday."),
               ("INBOX · 22 min ago","J. Whitfield confirmed Thursday. Calendar invite sent with the address and the note about the side gate."),
               ("INBOX · 2 hr ago","K. Alvarez is asking about a refund. Drafted a reply and left it in Drafts. Nothing sent; this one is yours.")],
      mock='''<div class="ag-mail"><div class="ag-mail__row on"><b>AC tune-up quote?</b><span>Dana R. · 7 min</span><em>Replied · 0:41</em></div><div class="ag-mail__row"><b>Re: Thursday visit</b><span>J. Whitfield · 22 min</span><em>Booked · Cal</em></div><div class="ag-mail__row"><b>Photos of the deck</b><span>M. Ortega · 1 hr</span><em>Filed · Drive</em></div><div class="ag-mail__row warn"><b>Refund for last month</b><span>K. Alvarez · 2 hr</span><em>Drafted · needs you</em></div>
<div class="ag-mail__draft"><span>To Dana R. · sent from your Gmail</span>Thanks Dana. A tune-up for a standard home system in Gilbert is on the price list at the rate you saw. Which day of the week works, and will someone be home? I can hold Thursday for you.</div></div>'''),
 dict(id="thread", n="04", name="THREAD", sku="agent-thread", price=347, short="Slack",
      inside="inside Slack", app="Slack", vendors="Slack",
      h1='THREAD works inside <em>Slack.</em>',
      sub="A teammate who reads every channel, knows your price list and job notes, posts every lead and call as it happens, and drafts the customer reply so a human only has to say yes.",
      state=["\"Did we ever finish the Henderson quote?\" gets asked in Slack at 9:52 at night, and the only person who knows is driving.",
             "The answer is in the job notes from two days ago. Nobody is going to go and look.",
             "{who} answers in the thread, with the source, and drafts the reply to the customer so someone only has to hit send."],
      does=[("help","Answers the team from your own documents","\"What did we quote the Hendersons?\" \"Are we open Saturday?\" Answered in the thread, with the source."),
            ("bell","Posts every lead, call and payment as it happens","One channel becomes the live feed of the business. Nothing gets lost in a text to one person."),
            ("pen","Drafts the customer reply in the thread","A teammate reacts with one emoji to send it, or edits it first. Nobody types from scratch."),
            ("sun","A morning summary in the channel you choose","What came in overnight, what got handled, what needs a person."),
            ("message","Takes questions in a direct message","Ask it privately what a job is worth or where a file is. Same answers, no noise in the channel."),
            ("hand","Says so when it does not know","It will not guess at a price or a policy. It says it is not sure and tags the person who knows.")],
      connect=[("lock","A private app in your own workspace","Installed by you, owned by you. Not a marketplace bot with a thousand other companies on it."),
               ("shield","Only the channels you invite it to","Slack's own permissions, listed in writing. Remove it from a channel or the workspace in one click."),
               ("book","Your documents, your rules","Price list, hours, policies and job notes you choose. It reads nothing you did not hand it.")],
      faq=[("Does it post to customers directly from Slack?","Only after a teammate reacts to send it. The draft sits in the thread until someone says yes."),
           ("What does it read?","The channels you invite it to and the documents you hand it. Nothing else in your workspace."),
           ("What if it does not know the answer?","It says so and tags the person who does. It does not guess at prices or policies.")],
      bubbles=[("THREAD · #leads · 9:47 PM","New lead from the website. Dana R., Gilbert 85296, AC tune-up. Quoted from the price list, follow-up set for Thursday."),
               ("THREAD · reply to Marcus · 9:52 PM","Yes. Henderson quote sent Tuesday, $285 for the capacitor and contactor, not accepted yet. Follow-up goes out tomorrow unless you want to call first."),
               ("THREAD · draft for Dana","Thanks Dana, Thursday is open. Will someone be home? React ✅ to send, ✏️ to edit.")],
      mock='''<div class="ag-slack"><div class="ag-slack__ch"># leads</div>
<div class="ag-msg"><b class="bot">THREAD</b><time>9:47 PM</time><p>New lead from the website. <b>Dana R.</b>, Gilbert 85296, AC tune-up. Quoted from the price list, follow-up set for Thursday.</p></div>
<div class="ag-msg reply"><b>Marcus</b><time>9:52 PM</time><p>did we ever finish the Henderson repair quote?</p></div>
<div class="ag-msg reply"><b class="bot">THREAD</b><time>9:52 PM</time><p>Yes. Sent Tuesday, $285 for the capacitor and contactor, not accepted yet. Follow-up goes out tomorrow unless you want to call them first. <span class="src">source: job notes, 2 days ago</span></p></div>
<div class="ag-msg draft"><b class="bot">THREAD</b><time>9:53 PM</time><p><span class="tag">Draft for Dana</span> Thanks Dana, Thursday is open. Will someone be home? <span class="react">✅ send</span><span class="react">✏️ edit</span></p></div></div>'''),
 dict(id="huddle", n="05", name="HUDDLE", sku="agent-huddle", price=347, short="Microsoft Teams",
      inside="inside Microsoft Teams", app="Microsoft Teams", vendors="Microsoft Teams and Microsoft 365",
      h1='HUDDLE works inside <em>Microsoft Teams.</em>',
      sub="For the companies that run on Microsoft 365. The same teammate as THREAD, living in your Teams channels, reading your SharePoint documents and posting every lead as it lands.",
      state=["Your company runs on Microsoft 365. The price list is in SharePoint, the schedule is in a spreadsheet, and the question \"is the Whitfield job still Thursday?\" still gets asked out loud.",
             "The answer is already in your files. Nobody should have to go and dig for it.",
             "{who} answers in the channel, with the source, and posts every lead where the team already looks."],
      does=[("help","Answers the team from your files","Price lists, policies and job notes in SharePoint or OneDrive. Answered in the channel, with the source."),
            ("bell","Posts every lead, call and payment into a channel","The live feed of the business, in the place your team already looks."),
            ("pen","Drafts the customer reply for one-click approval","A teammate approves or edits. Nobody types from scratch."),
            ("sun","A morning summary in the channel you choose","Overnight leads, what got handled, what needs a person."),
            ("message","Answers in a private chat too","Ask it directly what a job is worth or where the signed form is."),
            ("hand","Says so when it does not know","No guessed prices, no invented policies. It says it is not sure and tags the right person.")],
      connect=[("lock","A custom app in your own Microsoft 365 tenant","Your admin approves it once. It belongs to your organisation, not to a marketplace."),
               ("shield","Microsoft Graph permissions, listed in writing","Only the teams, channels and folders you choose. Revoke in your admin centre any time."),
               ("book","Your documents, your rules","It reads what you hand it and nothing else.")],
      faq=[("Does our admin have to approve it?","Yes, once. It is a custom app in your own tenant with the permissions listed in writing."),
           ("Is this the same as THREAD?","The same teammate, built for Teams and SharePoint instead of Slack. Hire whichever one your company actually runs."),
           ("What if it does not know the answer?","It says so and tags the person who does. It does not guess at prices or policies.")],
      bubbles=[("HUDDLE · Ops · 7:02 AM","Morning summary: 3 new leads overnight, 2 quoted from the price list, 1 waiting on photos. Invoice #1042 paid. Nothing needs you before 9."),
               ("HUDDLE · reply to Priya · 7:15 AM","Yes, Whitfield is Thursday 9:00, Route B. Confirmation went out last night. Source: schedule, updated 6:40 PM."),
               ("HUDDLE · new request","M. Ortega, AC repair, Gilbert 85296. Approve quote, edit, or call first: three buttons, one tap.")],
      mock='''<div class="ag-teams"><div class="ag-teams__ch">Ops · General</div>
<div class="ag-msg"><b class="bot">HUDDLE</b><time>7:02 AM</time><p><span class="tag">Morning summary</span> 3 new leads overnight, 2 quoted from the price list, 1 waiting on photos. Invoice #1042 paid. Nothing needs you before 9.</p></div>
<div class="ag-msg reply"><b>Priya</b><time>7:15 AM</time><p>is the Whitfield job still Thursday?</p></div>
<div class="ag-msg reply"><b class="bot">HUDDLE</b><time>7:15 AM</time><p>Yes, Thursday 9:00, Route B. Confirmation went out last night. <span class="src">source: schedule, updated 6:40 PM</span></p></div>
<div class="ag-card"><b>New request · M. Ortega</b><span>Pump repair, Gilbert 85296</span><div><span class="react">Approve quote</span><span class="react">Edit</span><span class="react">Call first</span></div></div></div>'''),
 dict(id="books", n="06", name="BOOKS", sku="agent-books", price=297, short="QuickBooks Online",
      inside="inside QuickBooks Online", app="QuickBooks Online", vendors="QuickBooks Online",
      h1='BOOKS works inside <em>QuickBooks.</em>',
      sub="The invoice goes out the day the job closes. Reminders on day seven, fourteen and twenty-one, in your words. Payments matched, a cash sheet every Monday, and nothing ever sent to collections.",
      state=["The job closed on the 3rd. The invoice went out on the 19th, because that was the first evening you sat down at the laptop.",
             "Then it sat unpaid for a month, because reminding people is the part everybody hates.",
             "{who} sends it the day the job closes, reminds politely on a schedule you set, and hands you one sheet on Monday."],
      does=[("receipt","Sends the invoice when the job closes","Built from your QuickBooks items and customers, with your payment link, the same day."),
            ("bell","Reminds late payers politely","Day seven, fourteen and twenty-one, in your tone. Never a threat, never a surprise fee."),
            ("check","Matches payments and marks them paid","Card, bank and check payments reconciled against the open invoice."),
            ("sheet","A cash sheet every Monday","What is owed, what is late, what came in last week. One page."),
            ("alert","Flags disputes to you","A customer who questions a charge gets a human, not a reminder."),
            ("pause","Stops when you say stop","Pause reminders for one customer or all of them in one message.")],
      connect=[("plug","Authorised on your QuickBooks company file","QuickBooks Online's own app connection. Your accountant sees everything exactly where they expect it."),
               ("folder","Works with your existing customers and items","No second system, no re-entering anything."),
               ("pen","You write the reminder wording, or approve mine","Three reminders, read by you before the first one is ever sent.")],
      faq=[("Does BOOKS take the payment?","No. It sends the link to the payment processor you already use through QuickBooks. It never sees a card number."),
           ("Will it ever threaten anyone or mention collections?","Never. Three polite reminders in your wording, then it hands the account to you."),
           ("Can my accountant still see everything?","Yes. It works inside your QuickBooks company file, so nothing moves anywhere else.")],
      bubbles=[("BOOKS · today","Job #1051 marked complete at 3:10. Invoice sent to M. Ortega at 3:12 with your payment link."),
               ("BOOKS · day 14","Second reminder to K. Alvarez for #1038, in your wording. One more on day 21, then it is yours."),
               ("BOOKS · Monday 7:00 AM","Cash sheet: $2,760 came in last week, 2 invoices late, 0 disputes. One page, in your inbox.")],
      mock='''<div class="ag-inv"><div class="ag-inv__head"><span>Open invoices</span><b>$4,120 owed · $1,560 late</b></div>
<div class="ag-inv__row paid"><b>#1042 · J. Whitfield</b><span>$285</span><em>Paid · matched</em></div><div class="ag-inv__row late"><b>#1038 · K. Alvarez</b><span>$620</span><em>14 days · reminder 2 sent</em></div><div class="ag-inv__row"><b>#1051 · M. Ortega</b><span>$285</span><em>Sent today · job closed</em></div><div class="ag-inv__row late"><b>#1029 · Desert Ridge HOA</b><span>$940</span><em>21 days · handed to you</em></div>
<div class="ag-inv__foot">Monday sheet: $2,760 came in last week · 2 late · 0 disputes</div></div>'''),
]
FULL = 1797
SEPARATE = sum(a["price"] for a in AGENTS)

# ---------------------------------------------------------------- shared css for the mocks (light)
MOCK_CSS = """
    .ag-mock { padding: 1.2rem 1.3rem; font-size: .9rem; }
    .ag-mock .caret { display: inline-block; width: .5em; height: 1em; vertical-align: -.15em; background: currentColor; animation: ag-blink 1s steps(1) infinite; }
    @keyframes ag-blink { 50% { opacity: 0; } }
    .ag-lines { list-style: none; margin: .9rem 0 0; padding: 0; display: flex; flex-direction: column; gap: .5rem; }
    .ag-lines li { max-width: 88%; padding: .6rem .85rem; border-radius: 14px; line-height: 1.45; }
    .ag-lines .them { align-self: flex-start; background: var(--bg-3); color: var(--ink); border-bottom-left-radius: 5px; }
    .ag-lines .us { align-self: flex-end; background: var(--green); color: var(--green-ink); border-bottom-right-radius: 5px; }
    .ag-lines .us::before { content: attr(data-who); display: block; font-size: .64rem; font-weight: 600; letter-spacing: .06em; opacity: .8; margin-bottom: .15rem; }
    .ag-call__top { display: flex; justify-content: space-between; align-items: center; font-size: .78rem; font-weight: 600; color: var(--ink-3); }
    .ag-call__top span { display: inline-flex; align-items: center; gap: .5rem; } .ag-call__top i { width: 8px; height: 8px; border-radius: 50%; background: var(--green); box-shadow: 0 0 0 4px var(--green-tint); }
    .ag-call__top b { font-family: var(--mono); font-size: 1.1rem; color: var(--green); letter-spacing: .04em; }
    .ag-call__foot, .ag-job__foot, .ag-inv__foot { margin-top: .9rem; padding-top: .7rem; border-top: 1px solid var(--line); font-size: .82rem; color: var(--ink-3); }
    .ag-job__head { display: flex; justify-content: space-between; gap: 1rem; font-size: .78rem; font-weight: 600; color: var(--ink-3); } .ag-job__head b { color: var(--ink); font-size: .92rem; }
    .ag-flow { list-style: none; margin: 1rem 0 0; padding: 0; }
    .ag-flow li { position: relative; display: grid; grid-template-columns: 1fr auto; gap: 1rem; padding: .6rem 0 .6rem 1.6rem; border-bottom: 1px solid var(--line); color: var(--ink-3); }
    .ag-flow li::before { content: ""; position: absolute; left: .3rem; top: .95rem; width: 10px; height: 10px; border-radius: 50%; border: 1.5px solid var(--line-2); background: #fff; }
    .ag-flow li.done::before { background: var(--green); border-color: var(--green); } .ag-flow li.on::before { background: #fff; border: 3px solid var(--green); box-shadow: 0 0 0 4px var(--green-tint); }
    .ag-flow li b { color: var(--ink); font-weight: 600; } .ag-flow li.done b { color: var(--ink-2); } .ag-flow li span { font-family: var(--mono); font-size: .78rem; }
    .ag-mail__row { display: grid; grid-template-columns: 1fr auto auto; gap: .8rem; align-items: baseline; padding: .55rem 0; border-bottom: 1px solid var(--line); color: var(--ink-2); }
    .ag-mail__row b { color: var(--ink); font-weight: 600; } .ag-mail__row span { font-size: .8rem; color: var(--ink-3); } .ag-mail__row em { font-style: normal; font-size: .7rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; color: var(--green); }
    .ag-mail__row.warn em { color: #B7791F; }
    .ag-mail__draft { margin-top: .9rem; padding: .85rem .95rem; border-radius: 14px; background: var(--bg-3); line-height: 1.5; color: var(--ink); }
    .ag-mail__draft span { display: block; font-size: .68rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; color: var(--ink-3); margin-bottom: .35rem; }
    .ag-slack__ch, .ag-teams__ch { font-weight: 700; font-size: .85rem; color: var(--ink); padding-bottom: .6rem; border-bottom: 1px solid var(--line); margin-bottom: .6rem; }
    .ag-msg { display: grid; grid-template-columns: auto auto; justify-content: start; column-gap: .6rem; padding: .45rem 0; }
    .ag-msg.reply { margin-left: 1.2rem; border-left: 2px solid var(--line-2); padding-left: .8rem; }
    .ag-msg b { color: var(--ink); font-weight: 700; } .ag-msg b.bot { color: var(--green); } .ag-msg b.bot::after { content: "APP"; margin-left: .4rem; font-size: .58rem; letter-spacing: .08em; padding: .1rem .3rem; border-radius: 4px; background: var(--bg-3); color: var(--ink-3); vertical-align: middle; }
    .ag-msg time { font-size: .72rem; color: var(--ink-3); align-self: baseline; } .ag-msg p { grid-column: 1 / -1; margin: .15rem 0 0; color: var(--ink-2); line-height: 1.5; }
    .ag-msg .src { display: block; margin-top: .2rem; font-size: .7rem; color: var(--ink-3); }
    .ag-msg .tag, .ag-card .react, .ag-msg .react { display: inline-block; font-size: .68rem; font-weight: 700; letter-spacing: .02em; padding: .18rem .5rem; border-radius: 999px; }
    .ag-msg .tag { background: var(--green-tint); color: var(--green); margin-right: .3rem; }
    .ag-msg .react, .ag-card .react { border: 1px solid var(--line-2); color: var(--ink); margin: .4rem .3rem 0 0; background: #fff; }
    .ag-msg.draft { background: rgba(22,165,90,.08); border-radius: 12px; padding: .5rem .7rem; margin-top: .3rem; }
    .ag-card { margin-top: .7rem; padding: .85rem .95rem; border: 1px solid var(--line-2); border-radius: 14px; background: #fff; } .ag-card b { display: block; color: var(--ink); } .ag-card span:not(.react) { color: var(--ink-3); font-size: .82rem; }
    .ag-inv__head { display: flex; justify-content: space-between; gap: 1rem; font-size: .78rem; font-weight: 600; color: var(--ink-3); } .ag-inv__head b { color: var(--ink); }
    .ag-inv__row { display: grid; grid-template-columns: 1fr auto auto; gap: .8rem; align-items: baseline; padding: .55rem 0; border-bottom: 1px solid var(--line); margin-top: .1rem; }
    .ag-inv__row b { color: var(--ink); font-weight: 600; } .ag-inv__row span { font-family: var(--mono); color: var(--ink); } .ag-inv__row em { font-style: normal; font-size: .7rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; color: var(--ink-3); }
    .ag-inv__row.paid em { color: var(--green); } .ag-inv__row.late em { color: #B7791F; }
    .ag-tm { margin: 2rem auto 0; max-width: 800px; text-align: center; font-size: .78rem; line-height: 1.5; color: var(--ink-3); }
"""

MOCK_JS = """
  <script>
  (function(){
    var t=document.querySelector('.ag-t'); if(!t) return;
    var to=+t.getAttribute('data-to')||8, s=0;
    var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(reduce){ t.textContent='0:0'+to; return; }
    var iv=setInterval(function(){ s++; t.textContent='0:'+(s<10?'0':'')+s; if(s>=to) clearInterval(iv); },380);
  })();
  </script>"""

STICKY_JS = """
  <script>
  (function(){
    var bar=document.querySelector('.sn-sticky'); if(!bar) return;
    var foot=document.querySelector('.footer'), hero=document.querySelector('.sn-hero');
    function tick(){
      var y=window.scrollY, past = hero ? y > hero.offsetTop + hero.offsetHeight - 120 : y > 480;
      var nearFoot = foot && foot.getBoundingClientRect().top < window.innerHeight - 40;
      bar.classList.toggle('is-on', past && !nearFoot);
    }
    window.addEventListener('scroll', tick, {passive:true}); window.addEventListener('resize', tick); tick();
  })();
  (function(){
    var list=document.querySelector('.sn-steps__list'); if(!list) return;
    var items=[].slice.call(list.children), views=[].slice.call(document.querySelectorAll('.sn-steps .sn-phone__view'));
    function on(i){ items.forEach(function(li,k){ li.classList.toggle('is-on',k===i); }); views.forEach(function(v,k){ v.classList.toggle('is-on',k===i); }); }
    on(0);
    items.forEach(function(li,i){ li.addEventListener('click',function(){ on(i); }); });
    if('IntersectionObserver' in window && window.innerWidth>900){
      var io=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting) on(items.indexOf(e.target)); }); },{rootMargin:'-45% 0px -45% 0px',threshold:0});
      items.forEach(function(li){ io.observe(li); });
    }
  })();
  </script>"""

def head(title, desc, canon, extra_css="", og_title=None):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="style.css?v={STYLE_V}" />
  <link rel="stylesheet" href="tech.css?v={TECH_V}" />
  <link rel="icon" type="image/x-icon" href="favicon.ico" />
  <link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png" />
  <link rel="icon" type="image/png" sizes="16x16" href="favicon-16.png" />
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png" />
  <link rel="canonical" href="https://greenaidigital.com/{canon}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://greenaidigital.com/{canon}" />
  <meta property="og:title" content="{esc(og_title or title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:image" content="https://greenaidigital.com/og-card.jpg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <style>{MOCK_CSS}{extra_css}
  </style>
</head>'''

def tail(extra_js=""):
    return f'''
  {FOOT}
  <div class="sn-pad-bottom" aria-hidden="true"></div>
  <script src="script.js?v={SCRIPT_V}"></script>
  <script src="checkout.js?v={CHECKOUT_V}"></script>
  <script src="analytics.js"></script>{MOCK_JS}{STICKY_JS}{extra_js}
</body>
</html>
'''

def jsonld(a):
    p = str(a["price"])
    d = {"@context":"https://schema.org","@type":"Service","name":f"{a['name']} — AI employee {a['inside']}","serviceType":"AI employee",
         "description":a["sub"],"url":f"https://greenaidigital.com/{a['id']}.html",
         "provider":{"@type":"ProfessionalService","name":"GreenAI Solutions","url":"https://greenaidigital.com","telephone":"+1-480-798-0753","email":"jaden@greenaidigital.com",
                     "address":{"@type":"PostalAddress","addressLocality":"Gilbert","addressRegion":"AZ","postalCode":"85296","addressCountry":"US"}},
         "areaServed":"US",
         "offers":{"@type":"Offer","name":f"{a['name']}, month to month","price":p,"priceCurrency":"USD",
                   "priceSpecification":{"@type":"UnitPriceSpecification","price":p,"priceCurrency":"USD","billingDuration":"P1M","unitText":"per month"},
                   "url":f"https://greenaidigital.com/pay.html?sku={a['sku']}","availability":"https://schema.org/InStock"}}
    return json.dumps(d, indent=2, ensure_ascii=False)

def phone_views(a):
    """Five screens, one per step, inside the sticky phone."""
    n = a["name"]; app = a["app"]
    v1 = f'''<div class="sn-phone__view is-on"><p class="sn-phone__title">One conversation</p><p class="sn-phone__sub">Twenty minutes, by phone or email.</p>
<ul class="sn-lines"><li class="them">We miss calls after 5 and every weekend. What would {n} actually do?</li><li class="us" data-who="GreenAI">Here is what it does {a['inside']}, and what it will not do. If it is not a fit I will say so.</li><li class="them">What does it cost?</li><li class="us" data-who="GreenAI">${a['price']:,} a month, month to month. That is the whole price.</li></ul></div>'''
    v2 = f'''<div class="sn-phone__view"><p class="sn-phone__title">Your account</p><p class="sn-phone__sub">{esc(a['connect'][0][1])}</p>
<div class="sn-file"><i>{esc(app.split(',')[0].split(' or ')[0][:3].upper())}</i><span>{esc(app)}<small>connected · your own account</small></span><em>OK</em></div>
<div class="sn-file"><i>KEY</i><span>Permissions listed in writing<small>revoke any time</small></span><em>OK</em></div>
<div class="sn-file"><i>YOU</i><span>Owner: you<small>nothing lives anywhere else</small></span><em>OK</em></div></div>'''
    v3 = f'''<div class="sn-phone__view"><p class="sn-phone__title">Trained on your business</p><p class="sn-phone__sub">Only what you hand it. Nothing invented.</p>
<div class="sn-file"><i>PDF</i><span>price-list.pdf<small>every number it may quote</small></span><em>READ</em></div>
<div class="sn-file"><i>HRS</i><span>Hours &amp; service area<small>Gilbert, Mesa, Chandler, Queen Creek</small></span><em>READ</em></div>
<div class="sn-file"><i>DOC</i><span>House rules<small>what to say, what to hand to you</small></span><em>READ</em></div>
<div class="sn-file"><i>TXT</i><span>The way you say things<small>your wording, not a template</small></span><em>READ</em></div></div>'''
    v4 = f'''<div class="sn-phone__view"><p class="sn-phone__title">You read every word first</p><p class="sn-phone__sub">Nothing reaches a customer over your objection.</p>
<ul class="sn-lines"><li class="us" data-who="{n} · draft">Thanks Dana, Thursday is open. Will someone be home? I can hold 9:00 for you.</li><li class="them">Change "hold" to "book". Otherwise good.</li><li class="us" data-who="{n} · v2">Thanks Dana, Thursday is open. Will someone be home? I can book 9:00 for you.</li><li class="them">Approved.</li></ul></div>'''
    v5 = f'''<div class="sn-phone__view"><p class="sn-phone__title">Live, and still answered</p><p class="sn-phone__sub">Changes are same-day at no charge.</p>
<div class="sn-file"><i>ON</i><span>{n} is live {esc(a['inside'])}<small>month to month, cancel at month end</small></span><em>LIVE</em></div>
<div class="sn-file"><i>480</i><span>(480) 798-0753<small>rings the person who built it</small></span><em>DIRECT</em></div>
<div class="sn-file"><i>MON</i><span>Monday report<small>what it handled, what it handed to you</small></span><em>WEEKLY</em></div></div>'''
    return v1+v2+v3+v4+v5

def steps(a):
    n=a["name"]; c=a["connect"]
    items=[("One conversation","What is stuck, what it costs you now, and what done would look like. About twenty minutes, by phone or email. You hear the price in writing before anything starts."),
           (c[0][1], c[0][2]),
           ("Trained on your business", f"Your prices, hours, service area and the way you say things. {n} quotes from your list and nothing else; a price that is not on it cannot go out."),
           ("You read every word first", c[2][2] if len(c)>2 else "Nothing goes to a customer until you have read the wording."),
           ("Live, and still answered", f"Changes are same-day at no charge. Cancel at the end of any month and you keep every script and transcript. The number on this page rings the person who built {n}.")]
    return "".join(f'<li><b>{esc(t)}</b><p>{esc(p)}</p></li>' for t,p in items)

from ring_demo import section as ring_demo_section

def build_agent(a):
    n=a["name"]; price=f"${a['price']:,}"
    others=[o for o in AGENTS if o["id"]!=a["id"]]
    title=f"{n} — the AI employee {a['inside']}, {price}/mo | GreenAI Solutions"
    desc=a["sub"][:155]
    who=f'<span class="who">{bust(a["id"], cls="who__bust")}{n}</span>'
    state="".join(f"<p>{esc(s).replace('{who}', who)}</p>" for s in a["state"])
    does="".join(f'<article class="sn-card"><div class="sn-card__ico">{I[ic]}</div><h3>{esc(t)}</h3><p>{esc(p)}</p></article>' for ic,t,p in a["does"])
    connect="".join(f'<div>{I[ic]}<h3>{esc(t)}</h3><p>{esc(p)}</p></div>' for ic,t,p in a["connect"])
    faq="".join(f'<details><summary>{esc(q)}</summary><p>{esc(ans)}</p></details>' for q,ans in a["faq"])
    bubbles=a["bubbles"]
    marquee1="".join(f'<div class="sn-mcard">{I[ic]}<b>{esc(t)}</b><p>{esc(p)}</p></div>' for ic,t,p in a["does"])
    marquee2="".join(f'<div class="sn-mcard">{I[ic]}<b>{esc(t)}</b><p>{esc(p)}</p></div>' for ic,t,p in a["connect"]) + "".join(f'<div class="sn-mcard">{I["check"]}<b>{esc(q)}</b><p>{esc(ans)}</p></div>' for q,ans in a["faq"])
    more="".join(f'<a href="{o["id"]}.html">{bust(o["id"], cls="sn-more__bot")}<b>{o["name"]}</b><span>Works {esc(o["inside"])}. ${o["price"]:,} a month.</span><i>See {o["name"]} →</i></a>' for o in others)
    more+=f'<a href="staff.html"><b>The full staff</b><span>All six, one invoice, one Monday report. ${FULL:,} a month.</span><i>See all six →</i></a>'
    return head(title, desc, f"{a['id']}.html", og_title=f"{n} works {a['inside']}") + f'''
<body class="tk light-top">
  <a href="#main" class="skip-link">Skip to content</a>
  <nav class="nav transparent" id="main-nav" aria-label="Main navigation">
{NAV}
  </nav>
  <script type="application/ld+json">
{jsonld(a)}
  </script>
  <main id="main">

    <div class="sn-wrap"><header class="sn-panel sn-hero sn-hero--tint" style="--ac:{ACCENT[a['id']]}" aria-labelledby="h1">{STARS}
      <div class="sn-hero__inner">
        <p class="tk-eyebrow"><b>AI employee {a['n']} of 06</b> · {esc(a['inside'])}</p>
        <h1 class="tk-h1" id="h1">{a['h1']}</h1>
        <p class="sn-hero__sub">{esc(a['sub'])}</p>
        <div class="sn-hero__price"><b>{price}</b><span>a month · month to month · no setup fee</span></div>
        <div class="sn-hero__cta">
          <a href="pay.html?sku={a['sku']}" class="tk-btn tk-btn--inverse tk-btn--arrow" data-sku="{a['sku']}">Hire {n}</a>
          <a href="contact.html?want={a['sku']}" class="tk-btn tk-btn--ghost">Ask a question first</a>
        </div>
      </div>
      <div class="sn-hero__stage ag-scene">
        <div class="ag-scene__bot">{ORBIT}<div class="rb-float">{robot(a['id'], I[ICON_OF[a['id']]], label=n+", the AI employee "+a['inside'], pose=HERO_POSE[a['id']], size="lg")}</div></div>
        <div class="ag-scene__win">
          <div class="ag-win"><div class="ag-win__bar"><i></i><i></i><i></i><span>{esc(WIN[a['id']])}</span><b>{n} · live</b></div><div class="tk-plate ag-mock" role="img" aria-label="What {n} looks like at work {esc(a['inside'])}, a mock-up with fictional names.">
{a['mock']}
          </div></div>
          <div class="ag-scene__chip ag-scene__chip--a sn-chip"><div class="sn-chip__ico">{I[a['does'][0][0]]}</div><div><b>{esc(a['does'][0][1])}</b><i>{n}</i></div></div>
          <div class="ag-scene__chip ag-scene__chip--b sn-chip"><div class="sn-chip__ico">{I[a['does'][2][0]]}</div><div><b>{esc(a['does'][2][1])}</b><i>{n}</i></div></div>
        </div>
      </div>
    </header></div>

{ring_demo_section() if a['id']=="ring" else ""}
    <section class="sn-sec" aria-labelledby="h-does">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-does">What {n} does {esc(a['inside'])}</h2><p class="tk-lede">Six things, all of them in the tool you already open every day.</p></div>
        <div class="sn-cards sn-cards--3">{does}</div>
      </div>
    </section>

    <div class="sn-state" aria-label="Why {n} exists">{state}</div>

    <section class="sn-sec" aria-labelledby="h-how">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-how">Hiring {n} is <em>five steps.</em></h2><p class="tk-lede">The same five whether it is the phone line or the books. Tap a step, or scroll.</p></div>
        <div class="sn-steps">
          <div class="sn-steps__device"><div class="sn-phone" aria-hidden="true"><div class="sn-phone__screen"><div class="sn-phone__notch"></div>{phone_views(a)}</div></div></div>
          <ol class="sn-steps__list">{steps(a)}</ol>
        </div>
      </div>
    </section>

    <div class="sn-wrap"><section class="sn-panel sn-grad" aria-labelledby="h-week">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-week">A week with {n}, <em>as you would see it.</em></h2><p class="tk-lede">Three messages you would actually get. Fictional customers, real behaviour.</p></div>
        <div class="sn-bubbles">
          <div><div class="sn-bubble"><b>{esc(bubbles[0][0])}</b>{esc(bubbles[0][1])}</div><div class="sn-grad__bot rb-float">{robot(a['id'], I[ICON_OF[a['id']]], pose=BAND_POSE[a['id']], size="lg")}</div></div>
          <div class="sn-phone"><div class="sn-phone__screen"><div class="sn-phone__notch"></div><div class="sn-phone__view is-on"><p class="sn-phone__title">{n}</p><p class="sn-phone__sub">{esc(a['inside'])}</p><ul class="sn-lines"><li class="us" data-who="{n}">{esc(bubbles[1][1])}</li><li class="them">Good. Anything else?</li><li class="us" data-who="{n}">Nothing that needs you. Monday report at 7.</li></ul></div></div></div>
          <div><div class="sn-bubble"><b>{esc(bubbles[2][0])}</b>{esc(bubbles[2][1])}</div></div>
        </div>
        <div class="sn-marquee" aria-hidden="true"><div class="sn-marquee__track">{marquee1}{marquee1}</div></div>
        <div class="sn-marquee sn-marquee--rev" aria-hidden="true"><div class="sn-marquee__track">{marquee2}{marquee2}</div></div>
      </div>
    </section></div>

    <section class="sn-sec" aria-labelledby="h-connect">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-connect">Your account. <em>Your rules.</em></h2></div>
        <div class="sn-trio">{connect}</div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-price" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-price">
          <p class="tk-eyebrow" style="margin-bottom:1.4rem"><b>Price</b> · that is the whole price</p>
          <div class="tk-big" id="h-price">{price}<small>a month, month to month</small></div>
          <p class="sn-price__terms">No setup fee, no per-call or per-message charges. Anything paid to {esc(a['vendors'])} on your behalf is your own subscription, at their price, not marked up. Cancel at the end of any month you have paid for and you keep every script, transcript and document.</p>
          <div class="sn-price__cta">
            <a href="pay.html?sku={a['sku']}" class="tk-btn tk-btn--solid tk-btn--arrow" data-sku="{a['sku']}">Hire {n}, {price}/mo</a>
            <a href="agreement.html">Read the service agreement first</a>
          </div>
        </div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-faq" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-faq">Asked before hiring {n}</h2><p class="tk-lede"><a href="faq.html">All the questions</a></p></div>
        <div class="sn-faq">{faq}</div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-rest" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-rest">{n} is one of <em>six.</em></h2><p class="tk-lede">One employee for each app you already run. Hire one, or the whole staff.</p></div>
        <div class="sn-more">{more}</div>
        <p class="ag-tm">{esc(TM)}</p>
      </div>
    </section>
  </main>
  <div class="sn-sticky"><a href="pay.html?sku={a['sku']}" class="tk-btn tk-btn--solid tk-btn--arrow" data-sku="{a['sku']}">Hire {n}, {price}/mo</a></div>''' + tail()

def build_staff():
    title=f"AI employees for the apps you already use, from $297/mo | GreenAI Solutions"
    desc=f"Six AI employees, one inside each app you already run: your phone line, Jobber, Gmail, Slack, Teams, QuickBooks. From $297 a month, or all six for ${FULL:,}. Month to month."
    cards="".join(f'''<article class="sn-card st-card" style="text-align:left">
  <div class="st-card__bot rb-float">{robot(a['id'], I[ICON_OF[a['id']]], label=a['name'], pose=CARD_POSE[a['id']])}</div>
  <p class="tk-eyebrow" style="margin-bottom:.9rem"><b>{a['n']}</b> {esc(a['inside'])}</p>
  <h3 style="font-size:1.6rem"><a href="{a['id']}.html" style="color:inherit;text-decoration:none">{a['name']}</a></h3>
  <p>{esc(a['does'][0][2])} {esc(a['does'][1][2])}</p>
  <div class="sn-card__vis"><div class="tk-plate ag-mock" style="padding:1rem 1.1rem;font-size:.82rem;box-shadow:none">{a['mock']}</div></div>
  <div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-top:1.3rem;flex-wrap:wrap"><div><b style="font-family:var(--font-display);font-size:1.7rem;font-weight:600;letter-spacing:-.02em">${a['price']:,}</b> <span style="color:var(--ink-3);font-size:.9rem">a month</span></div><div style="display:flex;gap:.5rem;flex-wrap:wrap"><a href="pay.html?sku={a['sku']}" class="tk-btn tk-btn--solid" data-sku="{a['sku']}">Hire {a['name']}</a><a href="{a['id']}.html" class="tk-btn tk-btn--line">See it at work</a></div></div>
</article>''' for a in AGENTS)
    rows="".join(f'<li><a href="{a["id"]}.html">{a["name"]}</a><span>{esc(a["inside"])}</span><b>${a["price"]:,}/mo</b></li>' for a in AGENTS)
    marquee="".join(f'<div class="sn-mcard">{I[ic]}<b>{a["name"]}: {esc(t)}</b><p>{esc(p)}</p></div>' for a in AGENTS for ic,t,p in a["does"][:3])
    bubbles=[AGENTS[0]["bubbles"][0], AGENTS[2]["bubbles"][0], AGENTS[5]["bubbles"][2]]
    faq=[("Do I have to hire all six?","No. Each one is hired on its own. The full staff is the same six on one invoice, for less than hiring them one at a time."),
         ("Do my customers know they are talking to an AI?","If they ask, it tells the truth. It does not pretend to be a person and does not use a fake name."),
         ("Is there a setup fee or a per-call charge?","No. The monthly price is the whole price. Anything you pay Slack, Google, Jobber or QuickBooks is your own subscription, at their price."),
         ("Can I cancel?","At the end of any month you have paid for. You keep every script, transcript and document."),
         ("Who builds and answers for them?","GreenAI Solutions, in Gilbert, Arizona. The number on this page rings us directly.")]
    faqh="".join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q,a in faq)
    return head(title, desc, "staff.html", og_title="Six AI employees, one inside each app you already use") + f'''
<body class="tk light-top">
  <a href="#main" class="skip-link">Skip to content</a>
  <nav class="nav transparent" id="main-nav" aria-label="Main navigation">
{NAV}
  </nav>
  <main id="main">
    <div class="sn-wrap"><header class="sn-panel sn-hero" aria-labelledby="h1">{STARS}
      <div class="sn-hero__inner">
        <p class="tk-eyebrow"><b>AI employees</b> · six of them</p>
        <h1 class="tk-h1" id="h1">One employee inside each app <em>you already use.</em></h1>
        <p class="sn-hero__sub">Not another dashboard to log into. Each one lives in a tool your company already opens every morning: the phone line, Jobber, Gmail, Slack, Teams, QuickBooks. Hire one, or the six.</p>
        <div class="sn-hero__cta">
          <a href="#roster" class="tk-btn tk-btn--inverse tk-btn--arrow">Meet the six</a>
          <a href="pay.html?sku=full-staff" class="tk-btn tk-btn--ghost" data-sku="full-staff">Hire all six, ${FULL:,}/mo</a>
        </div>
      </div>
      {seals(AGENTS)}
    </header></div>

    <section class="sn-sec" id="roster" aria-labelledby="h-roster">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-roster">Six names. <em>Six apps.</em></h2><p class="tk-lede">Each is built for your company: your prices, hours, wording and rules. You read every message before a customer or a teammate sees one.</p></div>
        <div class="sn-cards sn-cards--2">{cards}</div>
      </div>
    </section>

    <div class="sn-state" aria-label="Why the staff is shaped this way"><p>Every other AI product wants you inside its dashboard. These six live where your team already is, so they actually get used.</p><p>Flat, not metered. A good month costs you the same as a slow one.</p><p><span class="who">ONE PERSON</span> builds, maintains and answers for all six. Say the word and it changes that day.</p></div>

    <div class="sn-wrap"><section class="sn-panel sn-grad" aria-labelledby="h-week">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-week">A Monday with the full staff, <em>as you would see it.</em></h2><p class="tk-lede">Fictional customers, real behaviour.</p></div>
        <div class="sn-bubbles">
          <div><div class="sn-bubble"><b>{esc(bubbles[0][0])}</b>{esc(bubbles[0][1])}</div></div>
          <div class="sn-phone"><div class="sn-phone__screen"><div class="sn-phone__notch"></div><div class="sn-phone__view is-on"><p class="sn-phone__title">Monday report</p><p class="sn-phone__sub">all six, one page</p><div class="sn-file"><i>RNG</i><span>11 calls answered<small>2 booked, 1 emergency to you</small></span><em>RING</em></div><div class="sn-file"><i>INB</i><span>{esc(bubbles[1][1][:34])}…<small>day 1·3·7 follow-ups running</small></span><em>INBOX</em></div><div class="sn-file"><i>BKS</i><span>$2,760 came in<small>2 late, 0 disputes</small></span><em>BOOKS</em></div></div></div></div>
          <div><div class="sn-bubble"><b>{esc(bubbles[2][0])}</b>{esc(bubbles[2][1])}</div></div>
        </div>
        <div class="sn-marquee" aria-hidden="true"><div class="sn-marquee__track">{marquee}{marquee}</div></div>
      </div>
    </section></div>

    <section class="sn-sec" aria-labelledby="h-price">
      <div class="sn-inner">
        <div class="sn-price">
          <p class="tk-eyebrow" style="margin-bottom:1.4rem"><b>All six</b> · one invoice, one Monday report</p>
          <div class="tk-big" id="h-price">${FULL:,}<small>a month, all six · <s>${SEPARATE:,} separately</s></small></div>
          <p class="sn-price__terms">Phone answered, jobs dispatched, inbox handled, Slack or Teams answered, invoices paid. Everything on this page working together. Keeps ${SEPARATE-FULL:,} a month against hiring them one at a time.</p>
          <div class="sn-price__cta">
            <a href="pay.html?sku=full-staff" class="tk-btn tk-btn--solid tk-btn--arrow" data-sku="full-staff">Hire the full staff</a>
            <a href="agreement.html">Read the service agreement first</a>
          </div>
          <ul class="sn-price__rows">{rows}</ul>
        </div>
      </div>
    </section>

    <section class="sn-sec" aria-labelledby="h-faq" style="padding-top:0">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="h-faq">Asked before hiring</h2><p class="tk-lede"><a href="faq.html">All the questions</a></p></div>
        <div class="sn-faq">{faqh}</div>
        <p class="ag-tm">{esc(TM)}</p>
      </div>
    </section>
  </main>
  <div class="sn-sticky"><a href="pay.html?sku=full-staff" class="tk-btn tk-btn--solid tk-btn--arrow" data-sku="full-staff">Hire all six, ${FULL:,}/mo</a></div>''' + tail("""
  <script>
  (function(){
    var chips=[].slice.call(document.querySelectorAll('#sn-desk .sn-chip')); if(!chips.length) return;
    if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return; document.getElementById('sn-desk').classList.add('js');
    var i=0; function step(){ if(i<chips.length){ chips[i].classList.add('is-in'); i++; setTimeout(step, 550); } }
    setTimeout(step, 400);
  })();
  </script>""")

if __name__ == "__main__":
    for a in AGENTS:
        open(os.path.join(ROOT, f"{a['id']}.html"), "w").write(build_agent(a))
        print("wrote", a["id"] + ".html")
    open(os.path.join(ROOT, "staff.html"), "w").write(build_staff())
    print("wrote staff.html")

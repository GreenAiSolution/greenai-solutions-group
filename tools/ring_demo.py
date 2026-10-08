"""ring_demo.py — the "Hear RING answer a call" section, shared by the homepage
and ring.html.

The audio is film/ring-demo-call.mp3, built with the Send Desk's Kokoro voices
(~/greenai-send-desk, HVAC script). Both voices are AI and the business, caller
and address are made up; the section says so above the player, not in fine print.
"""
import html

AUDIO = "film/ring-demo-call.mp3"
LENGTH = "1:08"

TRANSCRIPT = [
    ("RING", "Thanks for calling Sample Heating and Cooling, this is the front desk. What can I help you with today?"),
    ("Caller", "Hi, my air conditioner stopped blowing cold about an hour ago and it's ninety-five in the house. Are you open?"),
    ("RING", "We are, and I can get someone out to you. Is the unit running but blowing warm, or has it shut off completely?"),
    ("Caller", "It's running, it's just warm air."),
    ("RING", "Got it. What's the address, and is there a gate code or anything the technician should know?"),
    ("Caller", "It's 1418 Maple Court, no gate. What's this going to cost me?"),
    ("RING", "I won't guess at a price for you. The technician quotes on site before any work starts, and there's no charge to look. I have a slot between two and four this afternoon, or first thing tomorrow at eight. Which works?"),
    ("Caller", "Two to four today. Are you a real person?"),
    ("RING", "No, I'm the AI front desk for Sample Heating. A person will be at your door this afternoon. I'm texting you the confirmation now, and if anything changes the technician calls you directly. Anything else?"),
    ("Caller", "No, that's it. Thanks."),
    ("RING", "You're booked. Stay cool, and we'll see you between two and four."),
]

NOTES = [
    ("Never guesses a price", "Asked what it costs, it says who quotes and when, then offers two times."),
    ("Says it is an AI", "Asked if it is a real person, it says no and who will show up."),
    ("Books and confirms", "The slot is held, the caller gets a text, you get the transcript."),
]

MAILTO = ("mailto:jaden@greenaidigital.com?subject=Record%20RING%20as%20my%20company"
          "&body=Company%20name%3A%20%0AWhat%20callers%20usually%20ask%3A%20")

CSS = """
<style>
.rd{max-width:760px;margin:0 auto;display:grid;grid-template-columns:auto 1fr;gap:1.25rem;align-items:center;padding:1.4rem 1.5rem;border-radius:22px;background:linear-gradient(180deg,#0d0f0c,#070806);border:1px solid rgba(232,196,106,.42);box-shadow:0 30px 80px rgba(0,0,0,.5)}
.rd__play{width:64px;height:64px;border-radius:50%;border:0;cursor:pointer;display:grid;place-items:center;background:#E8C46A;color:#0b0c0a;box-shadow:0 10px 30px rgba(232,196,106,.28);transition:transform .15s ease}
.rd__play:hover{transform:scale(1.05)}.rd__play:focus-visible{outline:2px solid #E8C46A;outline-offset:4px}
.rd__play svg{width:26px;height:26px}.rd__play .rd-i-pause{display:none}.rd.is-on .rd-i-play{display:none}.rd.is-on .rd-i-pause{display:block}
.rd__meta b{display:block;color:#f4efe2;font-family:var(--font-display);font-weight:600;font-size:1.05rem;letter-spacing:.01em}
.rd .rd__meta small{display:block;margin-top:.2rem;color:#E8C46A;font-size:.78rem;letter-spacing:.06em;text-transform:uppercase}
.rd__bar{position:relative;height:6px;margin-top:.9rem;border-radius:6px;background:rgba(244,239,226,.12);cursor:pointer}
.rd__bar i{position:absolute;inset:0 auto 0 0;width:0;border-radius:6px;background:#E8C46A}
.rd__time{display:flex;justify-content:space-between;margin-top:.45rem;color:rgba(244,239,226,.6);font:500 .78rem/1 'IBM Plex Mono',ui-monospace,monospace}
.rd-notes{max-width:760px;margin:1.1rem auto 0;display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;list-style:none;padding:0}
.rd-notes li{padding:1rem 1.1rem;border-radius:16px;border:1px solid rgba(244,239,226,.1);background:rgba(244,239,226,.03)}
.rd-notes b{display:block;color:#f4efe2;font-size:.95rem}.rd-notes span{display:block;margin-top:.3rem;color:rgba(244,239,226,.66);font-size:.86rem;line-height:1.45}
.rd-tx{max-width:760px;margin:.9rem auto 0}.sn-inner details.rd-tx{background:none;border:0;padding:0}.sn-inner details.rd-tx summary{cursor:pointer;color:#E8C46A;font-weight:600;background:none;padding:.2rem 0;border:0}
.rd-tx ol{list-style:none;margin:.9rem 0 0;padding:0;display:grid;gap:.55rem}
.rd-tx li{color:rgba(244,239,226,.82);line-height:1.5}.rd-tx li b{display:inline-block;min-width:4.2rem;color:#E8C46A;font-weight:600}
.rd-tx li.c b{color:rgba(244,239,226,.55)}
.rd-cta{max-width:760px;margin:1.4rem auto 0;text-align:center;color:rgba(244,239,226,.78)}.rd-cta a{color:#E8C46A;font-weight:600}
@media (max-width:640px){.rd{grid-template-columns:1fr;justify-items:start;padding:1.2rem}.rd__meta{width:100%}.rd-notes{grid-template-columns:1fr}}
</style>"""

JS = """
<script>
(function(){
  var box=document.querySelector('.rd'); if(!box) return;
  var a=box.querySelector('audio'), btn=box.querySelector('.rd__play'), bar=box.querySelector('.rd__bar'),
      fill=bar.querySelector('i'), now=box.querySelector('.rd__now');
  function t(s){s=Math.floor(s||0);return Math.floor(s/60)+':'+('0'+s%60).slice(-2)}
  btn.addEventListener('click',function(){ if(a.paused){a.play()}else{a.pause()} });
  a.addEventListener('play',function(){box.classList.add('is-on');btn.setAttribute('aria-label','Pause the demo call')});
  a.addEventListener('pause',function(){box.classList.remove('is-on');btn.setAttribute('aria-label','Play the demo call')});
  a.addEventListener('timeupdate',function(){ if(a.duration){fill.style.width=(a.currentTime/a.duration*100)+'%'} now.textContent=t(a.currentTime) });
  a.addEventListener('ended',function(){a.currentTime=0});
  bar.addEventListener('click',function(e){ if(!a.duration){return} var r=bar.getBoundingClientRect(); a.currentTime=(e.clientX-r.left)/r.width*a.duration });
})();
</script>"""


def section(heading_id="h-hear", lede=None):
    """The whole section: player, three notes, transcript, and the ask."""
    lede = lede or "Sixty-eight seconds. A Sunday, an AC blowing warm air, and a caller who wants a price."
    tx = "".join(
        f'<li class="{"r" if who == "RING" else "c"}"><b>{who}</b> {html.escape(line, quote=False)}</li>'
        for who, line in TRANSCRIPT)
    notes = "".join(f"<li><b>{html.escape(h)}</b><span>{html.escape(p)}</span></li>" for h, p in NOTES)
    return CSS + f'''
    <section class="sn-sec" aria-labelledby="{heading_id}">
      <div class="sn-inner">
        <div class="sn-head"><h2 class="tk-h2" id="{heading_id}">Hear RING <em>answer a call.</em></h2><p class="tk-lede">{html.escape(lede)}</p></div>
        <div class="rd">
          <button type="button" class="rd__play" aria-label="Play the demo call">
            <svg class="rd-i-play" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8 5.5v13l11-6.5z"/></svg>
            <svg class="rd-i-pause" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z"/></svg>
          </button>
          <div class="rd__meta">
            <b>RING, answering for Sample Heating and Cooling</b>
            <small>Demo call · both voices are AI · the business and caller are made up</small>
            <div class="rd__bar" aria-hidden="true"><i></i></div>
            <div class="rd__time"><span class="rd__now">0:00</span><span>{LENGTH}</span></div>
          </div>
          <audio preload="none" src="{AUDIO}"></audio>
        </div>
        <ul class="rd-notes">{notes}</ul>
        <details class="rd-tx"><summary>Read the transcript</summary><ol>{tx}</ol></details>
        <p class="rd-cta">Want to hear it answer as your company? <a href="{MAILTO}">Email us your company name</a> and we will send you a recording, free.</p>
      </div>
    </section>''' + JS

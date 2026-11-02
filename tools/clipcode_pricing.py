"""clipcode_pricing.py - the pricing section of index.html, imported by build_studio_home.py.
2026-11-01: priced just above the 2026 market average for each service (Jaden's call:
"make ours just a little more and premier"). Market: local SEO ~$1,000/mo, ad management
$500-$1,500/mo on small budgets, done-for-you text-back automation ~$250-$400/mo + ~$500 setup."""

PRICING = {  # key: (tab, sub, accent class, note, [(name, price, per, bullets, cta, plan, hot)])
 'seo': ('SEO','Get found','is-seo','No setup fee. Month to month. SEO builds over 4+ months, so we show you the progress every month.',[
   ('Local Starter','1,097','per month, no setup fee',['1 city','Google profile fixed, posted to weekly','4 service + city pages a month','Monthly ranking and calls report'],'Start local','seo-starter',''),
   ('Market Leader','1,797','per month, no setup fee',['Up to 5 cities','8 service + city pages a month','Directory listings cleaned up everywhere','Competitor tracking and a monthly call'],'Lead my market','seo-leader','Most chosen'),
   ('Valley Dominator','2,997','per month, no setup fee',['The whole Phoenix metro, up to 15 cities','16 pages a month, every service covered','Up to 2 locations on Google','AI search visibility and a call every 2 weeks'],'Own the Valley','seo-valley',''),
 ]),
 'ads': ('Ads','Get clicked now','is-ads','Plus a one-time $797 launch: tracking, campaign build and first ads. Your ad spend is paid straight to Google and Meta. We recommend at least $1,500 a month in spend.',[
   ('Launch','897','per month + ad spend',['One platform: Google or Facebook/Instagram','Up to $3,000 a month in ad spend managed','2 new ads a month','Monthly results report'],'Launch my ads','ads-launch',''),
   ('Growth','1,497','per month + ad spend',['Google and Facebook/Instagram','Up to $10,000 a month in ad spend managed','4 premium AI ads a month','Weekly tuning and call tracking'],'Grow with ads','ads-growth','Most chosen'),
   ('Scale','2,497','per month + ad spend',['Google, Local Services, Meta and YouTube','Up to $25,000 a month in ad spend managed','8 premium AI ads a month','Landing page tests and a call every 2 weeks'],'Scale up','ads-scale',''),
 ]),
 'auto': ('Automation',"Don't lose them",'is-auto','Builds are a fixed price, agreed in writing before work starts. Texting and phone costs are included.',[
   ('Single','347','per month + $697 one-time build',['1 automation, built and run','Like every missed call texted back','Watched and fixed by us'],'Start with one','auto-single',''),
   ('Front Office','697','per month + $1,497 one-time build',['3 automations working together','Leads texted back, quotes followed up, reviews asked','Monthly check-in and tuning'],'Build my front office','auto-front','Most chosen'),
   ('Autopilot','1,197','per month + $2,997 one-time build',['Up to 8 automations','Booking, reminders, rebooks and win-backs','New automations added as you grow'],'Go on autopilot','auto-autopilot',''),
 ]),
}
WHY = [('A real person','You can call the people doing the work. No ticket queue, no account manager relay.'),
       ('Creative included','Premium AI ads come with ad management. Most agencies charge extra for creative.'),
       ('You own everything','Your Google profile, ad accounts, pages and data stay in your name.'),
       ('Month to month','No 12-month contract. We earn the next month every month.')]

def plan_cards(rows):
    out = []
    for i,(n,pr,per,bul,cta,plan,hot) in enumerate(rows):
        lis = ''.join(f'<li>{b}</li>' for b in bul)
        tag = f'<span class="tag">{hot}</span>' if hot else ''
        btn = 'btn--go' if hot else 'btn--ghost'
        arrow = ' <span class="arrow">&rarr;</span>' if hot else ''
        out.append(f'<div class="plan{" hot" if hot else ""}">{tag}<span class="plan__tier">Tier {i+1}</span><h3>{n}</h3><div class="price"><sup>$</sup>{pr}<span>/mo</span></div><div class="per">{per}</div>'
                   f'<ul>{lis}</ul><a class="btn {btn}" href="#contact" data-plan="{plan}">{cta}{arrow}</a></div>')
    return '\n'.join(out)

def plans_section():
    tabs = ''.join(f'<button role="tab" aria-selected="{"true" if i==0 else "false"}" id="pt-{k}" aria-controls="pp-{k}" data-pp="{k}"><b>{v[0]}</b><small>{v[1]}</small></button>' for i,(k,v) in enumerate(PRICING.items()))
    tabs += '<button role="tab" aria-selected="false" id="pt-all" aria-controls="pp-all" data-pp="all"><b>All three</b><small>The full system</small></button>'
    panels = ''
    for i,(k,(lab,sub,cls,note,rows)) in enumerate(PRICING.items()):
        panels += f'''
    <div class="ppanel {cls}" role="tabpanel" id="pp-{k}" aria-labelledby="pt-{k}"{"" if i==0 else " hidden"}>
      <div class="plans">
{plan_cards(rows)}
      </div>
      <p class="pnote">{note}</p>
    </div>'''
    why = ''.join(f'<div><b>{t}</b><span>{l}</span></div>' for t,l in WHY)
    return f'''<section class="sec" id="plans" data-at="seo">
  <a class="anchor" id="pricing"></a>
  <div class="wrap">
    <div class="sechead sechead--row">
      <div><span class="kicker rv">Pricing</span><h2 class="rv" style="--d:.05s">Premium work. <span class="sp">Published prices.</span></h2></div>
      <p class="lede rv" style="--d:.1s">No "call for a quote." Pick a service and a tier, or take all three and save. Everything starts with a free growth check.</p>
    </div>
    <div class="switch switch--4 rv" role="tablist" aria-label="Pricing by service" data-at="seo">{tabs}<i class="switch__pill" aria-hidden="true"></i></div>
{panels}
    <div class="ppanel" role="tabpanel" id="pp-all" aria-labelledby="pt-all" hidden>
      <div class="ticket ticket--3">
        <div class="ticket__main">
          <span class="tag">Clipcode Full System</span>
          <h3><span class="vi">Found</span> on Google. <span class="pk">Clicked</span> this week. <span class="cy">Answered</span> in a minute.</h3>
          <ul><li>SEO Market Leader: up to 5 cities, 8 new pages a month</li><li>Ads Growth: Google + Facebook/Instagram, 4 premium AI ads a month</li><li>Automation Front Office: text back, quote follow-up, review asks</li><li>One team, one monthly bill, one number to call</li></ul>
          <a class="btn btn--go btn--lg" href="#contact" data-plan="all">Get the full system <span class="arrow">&rarr;</span></a>
        </div>
        <div class="ticket__stub">
          <div class="was">$3,991/mo separately</div>
          <div class="price"><sup>$</sup>3,297<span>/mo</span></div>
          <div class="per">+ $997 one-time setup, instead of $2,294</div>
          <div class="save">Save $694 every month</div>
        </div>
      </div>
    </div>

    <div class="partner partner--check rv"><div><b>Not sure yet? Free growth check &middot; $0</b><p>We look at your Google profile, where you rank on the map, any ads you run, and how fast you answer a new lead. You get a plain list of what to fix first, and which tier fits.</p></div><a class="btn btn--go" href="#contact" data-plan="check">Get my free check <span class="arrow">&rarr;</span></a></div>

    <div class="why rv"><div class="why__head"><h3>Why we cost <span class="sp">a little more.</span></h3><p class="m">Most local agencies charge around $1,000 a month for SEO and $500 to $1,500 to run ads. We sit just above that, on purpose.</p></div><div class="why__in">{why}</div></div>

    <p class="fine rv">Monthly plans are month to month and cancel anytime. Ad spend is separate and goes straight to the platform; above $25,000 a month in spend, management is 10% of spend. We do the work, but we never promise a number of leads or a ranking.</p>
  </div>
</section>'''

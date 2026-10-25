(function(){
  'use strict';
  var RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function(s,c){return (c||document).querySelector(s)};
  var $$ = function(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s))};

  var yr=$('#yr'); if(yr) yr.textContent=new Date().getFullYear();

  /* nav + progress */
  var nav=$('#nav'), prog=$('#progress'), burger=$('#burger'), links=$('#links');
  var secIds=['automations','industries','how','reel','plans','contact'];
  var tick=false;
  function onScroll(){
    tick=false;
    nav.classList.toggle('on',scrollY>30);
    var max=document.documentElement.scrollHeight-innerHeight;
    prog.style.transform='scaleX('+(max>0?Math.min(1,scrollY/max):0)+')';
    var act=null;
    secIds.forEach(function(id){var el=document.getElementById(id); if(el&&el.getBoundingClientRect().top<innerHeight*.4) act=id;});
    $$('a',links).forEach(function(a){a.classList.toggle('act',act&&a.getAttribute('href')==='#'+act);});
  }
  onScroll(); addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(onScroll);}},{passive:true});
  burger.addEventListener('click',function(){var o=links.classList.toggle('open');burger.setAttribute('aria-expanded',o);});
  $$('a',links).forEach(function(a){a.addEventListener('click',function(){links.classList.remove('open');burger.setAttribute('aria-expanded','false');});});

  /* reveal */
  var io='IntersectionObserver' in window?new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.12,rootMargin:'0px 0px -6% 0px'}):null;
  $$('.rv').forEach(function(el){io?io.observe(el):el.classList.add('in');});

  /* lazy preview videos: load + play only while visible */
  function attach(v){ if(!v.src && v.dataset.src){ v.src=v.dataset.src; } }
  if('IntersectionObserver' in window && !RM){
    var vio=new IntersectionObserver(function(es){
      es.forEach(function(e){
        var v=e.target, tile=v.closest('.tile, .cmark__screen');
        if(e.isIntersecting){ attach(v); var p=v.play(); if(p&&p.catch) p.catch(function(){}); if(tile) v.addEventListener('playing',function(){tile.classList.add('live');},{once:true}); }
        else { v.pause(); }
      });
    },{threshold:.35});
    $$('.tile video, .cmark__screen video').forEach(function(v){vio.observe(v);});
  }

  /* PLAY cursor */
  var cur=$('#cursor'), cx=0,cy=0,tx=0,ty=0,raf=0;
  if(cur && matchMedia('(hover:hover)').matches && !RM){
    addEventListener('pointermove',function(e){tx=e.clientX;ty=e.clientY; if(!raf) raf=requestAnimationFrame(move);},{passive:true});
    function move(){raf=0;cx+=(tx-cx)*.28;cy+=(ty-cy)*.28;cur.style.transform='translate3d('+cx+'px,'+cy+'px,0) scale('+(cur.classList.contains('on')?1:0)+')'; if(Math.abs(tx-cx)>.5||Math.abs(ty-cy)>.5) raf=requestAnimationFrame(move);}
    $$('.tile, .cmark__screen').forEach(function(t){
      t.addEventListener('pointerenter',function(){cur.classList.add('on');move();});
      t.addEventListener('pointerleave',function(){cur.classList.remove('on');move();});
    });
  }

  /* lightbox */
  var lb=$('#lb'), lv=$('#lbVideo'), lt=$('#lbTitle'), tiles=$$('.tile'), idx=0, last=null;
  function show(title,src){
    lt.textContent=title; lv.src=src; lv.currentTime=0;
    lb.classList.add('open'); document.body.style.overflow='hidden';
    var p=lv.play(); if(p&&p.catch) p.catch(function(){});
  }
  function open(i){ idx=(i+tiles.length)%tiles.length; var t=tiles[idx]; show(t.dataset.title,t.dataset.src); }
  function close(){lb.classList.remove('open');lv.pause();lv.removeAttribute('src');lv.load();document.body.style.overflow='';if(last)last.focus();}
  tiles.forEach(function(t,i){t.addEventListener('click',function(){last=t;open(i);});});
  $('#lbX').addEventListener('click',close);
  $('#lbPrev').addEventListener('click',function(){open(idx-1);});
  $('#lbNext').addEventListener('click',function(){open(idx+1);});
  lb.addEventListener('click',function(e){if(e.target===lb)close();});
  addEventListener('keydown',function(e){ if(!lb.classList.contains('open'))return; if(e.key==='Escape')close(); if(e.key==='ArrowLeft')open(idx-1); if(e.key==='ArrowRight')open(idx+1); });
  var w8=$('#watch8'); if(w8) w8.addEventListener('click',function(){last=w8;show(w8.dataset.title,w8.dataset.src);});

  /* screens switcher */
  var scr=$('#screen'), sv=$('video',scr), note=$('#fmtnote'), lab=$('#fmtlabel');
  var info={
    reel:['Reels and Shorts. Full screen, sound on, thumb-stopping from the first frame.','9:16 · Reels, Shorts, TikTok'],
    feed:['The feed. A square crop that has to work muted, in a busy scroll, with the hook inside three seconds.','1:1 · Facebook and Instagram feed'],
    wide:['The wide spot. For YouTube, connected TV and your own website, where there is room for a story.','16:9 · YouTube, TV, your site']
  };
  $$('#screens .tabs button').forEach(function(b){b.addEventListener('click',function(){
    $$('#screens .tabs button').forEach(function(x){x.setAttribute('aria-selected',x===b);});
    scr.dataset.f=b.dataset.f; note.textContent=info[b.dataset.f][0]; lab.textContent=info[b.dataset.f][1];
  });});
  if(sv&&'IntersectionObserver' in window){
    new IntersectionObserver(function(es){es.forEach(function(e){ if(e.isIntersecting){attach(sv); if(!RM){var p=sv.play(); if(p&&p.catch)p.catch(function(){});}} else sv.pause(); });},{threshold:.3}).observe(scr);
  }

  /* chat sequence */
  var chat=$('#chat');
  if(chat&&'IntersectionObserver' in window){var co=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){chat.classList.add('on');co.disconnect();}});},{threshold:.4});co.observe(chat);}

  /* industry tabs */
  var itabs=$$('#industries [role=tab]');
  itabs.forEach(function(b){b.addEventListener('click',function(){
    itabs.forEach(function(x){x.setAttribute('aria-selected',x===b); var pn=document.getElementById('ind-'+x.dataset.ind); if(pn) pn.hidden=(x!==b);});
  });});

  /* hero board: light up one automation at a time */
  var feed=$$('#feed li');
  if(feed.length){
    if(RM){feed.forEach(function(li){li.classList.add('on');});}
    else{var fi=0; (function step(){ feed.forEach(function(li,j){li.classList.toggle('on',j<=fi); li.classList.toggle('now',j===fi);}); fi=(fi+1)%feed.length; setTimeout(step, fi===0?2600:1500); })();}
  }

  /* pricing switcher */
  var sw=$('.switch'), ptabs=$$('.switch [role=tab]');
  var plansSec=$('#plans');
  function pick(k){ ptabs.forEach(function(x){var on=x.dataset.pp===k; x.setAttribute('aria-selected',on); x.tabIndex=on?0:-1; var pn=document.getElementById('pp-'+x.dataset.pp); if(pn) pn.hidden=!on;}); if(sw) sw.dataset.at=k; if(plansSec) plansSec.dataset.at=k; }
  pick('auto');
  ptabs.forEach(function(b){b.addEventListener('click',function(){pick(b.dataset.pp);});});

  /* tablists: left/right arrow keys move between tabs and select them */
  $$('[role=tablist]').forEach(function(list){
    var tabs=$$('[role=tab]',list);
    tabs.forEach(function(t){ if(t.getAttribute('aria-selected')!=='true') t.tabIndex=-1; });
    list.addEventListener('keydown',function(e){
      var i=tabs.indexOf(document.activeElement); if(i<0) return;
      var n=e.key==='ArrowRight'?i+1:e.key==='ArrowLeft'?i-1:e.key==='Home'?0:e.key==='End'?tabs.length-1:null;
      if(n===null) return; e.preventDefault(); n=(n+tabs.length)%tabs.length;
      tabs.forEach(function(t,j){t.tabIndex=j===n?0:-1;}); tabs[n].focus(); tabs[n].click();
    });
  });

  /* plan + trade buttons prefill the form */
  var sel=$('#interest'), msg=$('#message');
  $$('[data-plan]').forEach(function(b){b.addEventListener('click',function(){ if(sel) sel.value=b.dataset.plan; });});
  $$('[data-trade]').forEach(function(b){b.addEventListener('click',function(){ if(sel) sel.value='trade'; if(msg&&!msg.value) msg.value='My trade: '+b.dataset.trade+'. '; });});

  /* form: same endpoint and payload shape as the rest of greenaidigital.com */
  var form=$('#form'), btn=$('#send'), err=$('#err');
  if(form){form.addEventListener('submit',function(e){
    e.preventDefault(); err.style.display='none';
    if(!form.checkValidity()){form.reportValidity();return;}
    var orig=btn.innerHTML; btn.textContent='Sending...'; btn.disabled=true;
    var payload={}; new FormData(form).forEach(function(v,k){payload[k]=v;});
    var opt=form.interest.options[form.interest.selectedIndex];
    payload.form=form.getAttribute('data-form'); payload.source=form.getAttribute('data-source');
    payload.service=opt?opt.text:payload.interest; payload.plan='GreenAI: '+(opt?opt.text:''); payload.reference=payload.website||'';
    fetch(form.getAttribute('action'),{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(payload)})
      .then(function(r){return r.json().catch(function(){return {ok:false};});})
      .then(function(res){if(!res.ok)throw new Error('rejected'); form.classList.add('sent'); form.parentNode.classList.add('sent');})
      .catch(function(){
        btn.innerHTML=orig; btn.disabled=false;
        var lines=[]; new FormData(form).forEach(function(v,k){if(k!=='botcheck'&&String(v).trim())lines.push(k+': '+v);});
        var mail='mailto:jaden@greenaidigital.com?subject='+encodeURIComponent('Clipcode request: '+(form.interest.options[form.interest.selectedIndex]||{}).text)+'&body='+encodeURIComponent(lines.join('\n').slice(0,1800));
        err.innerHTML='That did not go through on our side. <a href="'+mail+'">Send it by email instead</a> (your answers are already filled in), or call <a href="tel:+14807980753">(480) 798-0753</a>.';
        err.style.display='block';
      });
  });}
})();

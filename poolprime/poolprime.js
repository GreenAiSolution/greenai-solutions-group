(function(){
  'use strict';
  var RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function(s,c){return (c||document).querySelector(s)};
  var $$ = function(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s))};

  /* year */
  var yr=$('#yr'); if(yr) yr.textContent=new Date().getFullYear();

  /* nav: solid after scroll, burger */
  var nav=$('#nav'), burger=$('#burger'), links=$('#links');
  function navState(){ nav.classList.toggle('on', window.scrollY>30); }
  navState(); window.addEventListener('scroll',navState,{passive:true});
  burger.addEventListener('click',function(){
    var o=links.classList.toggle('open'); burger.setAttribute('aria-expanded',o);
  });
  $$('a',links).forEach(function(a){a.addEventListener('click',function(){links.classList.remove('open');burger.setAttribute('aria-expanded','false');});});

  /* reveal on scroll */
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target);} });
  },{threshold:.15,rootMargin:'0px 0px -6% 0px'}) : null;
  $$('.rv').forEach(function(el){ io ? io.observe(el) : el.classList.add('in'); });

  /* chat sequence */
  var chat=$('#chat');
  if(chat){ var cio=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){chat.classList.add('on');cio.disconnect();} }); },{threshold:.35}); cio.observe(chat); }

  /* ---------- caustic water ground ---------- */
  var cv=$('#caustics'), cx=cv.getContext('2d'), W=0,H=0,img=null,t0=performance.now(),running=true,last=0;
  var TAU=6.28318530718;
  function size(){
    W=Math.max(140,Math.min(240,Math.round(innerWidth/6))); H=Math.max(80,Math.round(W*innerHeight/innerWidth));
    cv.width=W; cv.height=H; img=cx.createImageData(W,H);
  }
  /* classic water-caustic pattern: five warped iterations per pixel */
  function frame(now){
    if(!running){ requestAnimationFrame(frame); return; }
    if(now-last<50 && !RM){ requestAnimationFrame(frame); return; }
    last=now; var t=(now-t0)/1000*0.45+23, d=img.data, i=0, inten=.005;
    for(var y=0;y<H;y++){
      for(var x=0;x<W;x++){
        var px=((x/W*TAU*2)%TAU)-250, py=((y/H*TAU*2)%TAU)-250, ix=px, iy=py, c=1;
        for(var n=0;n<5;n++){
          var tt=t*(1-3.5/(n+1)), nx=px+Math.cos(tt-ix)+Math.sin(tt+iy), ny=py+Math.sin(tt-iy)+Math.cos(tt+ix);
          ix=nx; iy=ny;
          var ax=px/(Math.sin(ix+tt)/inten), ay=py/(Math.cos(iy+tt)/inten);
          c+=1/Math.sqrt(ax*ax+ay*ay);
        }
        c/=5; c=1.17-Math.pow(c,1.4); c=Math.pow(Math.abs(c),8); if(c>1)c=1;
        d[i]=60*c; d[i+1]=205*c; d[i+2]=255*c; d[i+3]=255; i+=4;
      }
    }
    cx.putImageData(img,0,0);
    if(!RM) requestAnimationFrame(frame);
  }
  size(); window.addEventListener('resize',function(){ clearTimeout(size.t); size.t=setTimeout(function(){size(); if(RM) frame(performance.now());},200); });
  document.addEventListener('visibilitychange',function(){ running=!document.hidden; });
  requestAnimationFrame(frame);

  /* bubbles */
  var bb=$('#bubbles');
  if(bb && !RM){
    for(var k=0;k<16;k++){
      var s=document.createElement('b'), sz=6+Math.random()*22;
      s.style.cssText='left:'+(Math.random()*100)+'%;width:'+sz+'px;height:'+sz+'px;animation-duration:'+(9+Math.random()*14)+'s;animation-delay:-'+(Math.random()*20)+'s;--sx:'+((Math.random()-.5)*120)+'px;opacity:'+(.35+Math.random()*.5);
      bb.appendChild(s);
    }
  }

  /* hero P parallax */
  var stage=$('#stage'), P=$('#heroP');
  if(stage && P && !RM){
    window.addEventListener('pointermove',function(e){
      var x=(e.clientX/innerWidth-.5), y=(e.clientY/innerHeight-.5);
      P.style.setProperty('--px',(x*-26)+'px'); P.style.setProperty('--py',(y*-18)+'px');
    },{passive:true});
  }

  /* timecode */
  var tc=$('#tc'), hero=$('#top'), inHero=true;
  if(tc){
    new IntersectionObserver(function(es){inHero=es[0].isIntersecting;},{threshold:0}).observe(hero);
    var start=performance.now();
    setInterval(function(){
      if(!inHero||document.hidden||RM) return;
      var ms=performance.now()-start, f=Math.floor(ms/41.67)%24, s=Math.floor(ms/1000)%60, m=Math.floor(ms/60000)%60, h=Math.floor(ms/3600000);
      var p=function(n){return (n<10?'0':'')+n};
      tc.textContent=p(h)+':'+p(m)+':'+p(s)+':'+p(f);
    },42);
  }

  /* before / after slider */
  var ba=$('#ba'), rng=$('#baR');
  if(ba&&rng){
    var setPos=function(v){ ba.style.setProperty('--pos',v); };
    rng.addEventListener('input',function(){ interacted=true; setPos(rng.value); });
    var interacted=false;
    if(!RM){
      var played=false;
      new IntersectionObserver(function(es,o){
        if(es[0].isIntersecting && !played){
          played=true; o.disconnect();
          var t1=performance.now(), dur=3600;
          (function step(n){
            if(interacted) return;
            var p=Math.min(1,(n-t1)/dur), e=p<.5?2*p*p:1-Math.pow(-2*p+2,2)/2;
            var v = p<.72 ? 6+(94-6)*(e/(1)) : 0; 
            // sweep 6 -> 94 -> settle 58
            var q = p<.7 ? (p/.7) : 1, qe=q<.5?2*q*q:1-Math.pow(-2*q+2,2)/2;
            var val = p<.7 ? 6+88*qe : 94-36*(1-Math.pow(1-((p-.7)/.3),3));
            setPos(val); rng.value=val;
            if(p<1) requestAnimationFrame(step);
          })(t1);
        }
      },{threshold:.5}).observe(ba);
    }
  }

  /* gauge: water level + section dots */
  var secs=[['top','Open'],['work','Work'],['make','Make'],['how','How'],['plans','Plans'],['sample','Sample']];
  var g=$('#gauge'), fill=$('#gfill'), dots=[];
  secs.forEach(function(s,i){
    var a=document.createElement('a'); a.href='#'+s[0]; a.style.top=(i/(secs.length-1)*100)+'%';
    a.setAttribute('aria-label',s[1]); a.innerHTML='<span>'+s[1]+'</span>'; g.appendChild(a); dots.push(a);
  });
  var ticking=false;
  function gauge(){
    ticking=false;
    var max=document.documentElement.scrollHeight-innerHeight, p=max>0?Math.min(1,scrollY/max):0;
    fill.style.height=(p*100)+'%';
    var act=0;
    secs.forEach(function(s,i){ var el=document.getElementById(s[0]); if(el && el.getBoundingClientRect().top<innerHeight*.45) act=i; });
    dots.forEach(function(d,i){ d.classList.toggle('act',i===act); });
    $$('a',links).forEach(function(a){ a.classList.toggle('act', a.getAttribute('href')==='#'+secs[act][0]); });
  }
  gauge(); window.addEventListener('scroll',function(){ if(!ticking){ticking=true;requestAnimationFrame(gauge);} },{passive:true});
  window.addEventListener('resize',gauge);

  /* click ripple */
  if(!RM) document.addEventListener('pointerdown',function(e){
    var r=document.createElement('i'); r.className='ripple'; r.style.left=e.clientX+'px'; r.style.top=e.clientY+'px';
    document.body.appendChild(r); r.addEventListener('animationend',function(){r.remove();});
  });

  /* plans pick: preselect form */
  $$('.pick').forEach(function(b){ b.addEventListener('click',function(){
    var sel=$('#interest'); if(sel && b.dataset.plan) sel.value=b.dataset.plan;
  }); });

  /* math */
  var profit=$('#profit'), mMonths=$('#mMonths'), mYear=$('#mYear');
  function math(){
    var v=Math.max(500,parseFloat(profit.value)||0), plan=497;
    var months=Math.max(1,Math.round(v/plan));
    mMonths.textContent=months;
    mYear.textContent='$'+(plan*12).toLocaleString('en-US');
  }
  if(profit){ profit.addEventListener('input',math); math(); }

  /* form: same endpoint and payload shape as the rest of greenaidigital.com */
  var form=$('#sampleForm'), btn=$('#send'), err=$('#err');
  if(form){
    form.addEventListener('submit',function(e){
      e.preventDefault(); err.style.display='none';
      if(!form.checkValidity()){ form.reportValidity(); return; }
      var orig=btn.textContent; btn.textContent='Sending...'; btn.disabled=true;
      var payload={}; new FormData(form).forEach(function(v,k){payload[k]=v;});
      payload.form=form.getAttribute('data-form'); payload.source=form.getAttribute('data-source');
      var opt=form.interest.options[form.interest.selectedIndex];
      payload.service=opt?opt.text:payload.interest; payload.plan='PoolPrime: '+(opt?opt.text:''); payload.trade='Pool builder / pool pro'; payload.reference=payload.website||'';
      fetch(form.getAttribute('action'),{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(payload)})
        .then(function(r){return r.json().catch(function(){return {ok:false};});})
        .then(function(res){ if(!res.ok) throw new Error('rejected'); form.parentNode.classList.add('sent'); form.classList.add('sent'); })
        .catch(function(){
          btn.textContent=orig; btn.disabled=false;
          var lines=[]; new FormData(form).forEach(function(v,k){ if(k!=='botcheck'&&String(v).trim()) lines.push(k+': '+v); });
          var mail='mailto:jaden@greenaidigital.com?subject='+encodeURIComponent('PoolPrime sample ad request')+'&body='+encodeURIComponent(lines.join('\n').slice(0,1800));
          err.innerHTML='That did not go through on our side. <a href="'+mail+'">Send it by email instead</a> (your answers are already filled in), or DM POOL to @poolprime.ai on Instagram.';
          err.style.display='block';
        });
    });
  }
})();

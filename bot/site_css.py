"""CSS e JS do site (separados para manter gerar_site.py legivel)."""

CSS = """
:root{--bg:{{BG}};--barra:{{BARRA}};--ac:{{AC}};--preco:{{PRECO}};
 --card:rgba(255,255,255,.04);--bord:rgba(255,255,255,.09);--bord2:rgba(255,255,255,.14);
 --tx:#eaf3ee;--tx2:rgba(255,255,255,.62);--tx3:rgba(255,255,255,.4)}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--tx);
 font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;
 -webkit-font-smoothing:antialiased}
body::before{content:"";position:fixed;inset:0;z-index:-1;
 background:radial-gradient(900px 500px at 80% -10%,var(--barra) 0%,transparent 60%),
 radial-gradient(700px 400px at 0% 0%,rgba(46,230,160,.06) 0%,transparent 55%)}
a{color:inherit;text-decoration:none}
img{display:block}

/* header */
.top{position:sticky;top:0;z-index:50;background:rgba(14,26,20,.82);
 backdrop-filter:blur(14px);border-bottom:1px solid var(--bord)}
.top .in{max-width:1180px;margin:0 auto;padding:12px 22px;display:flex;align-items:center;gap:14px}
.top img{width:44px;height:44px;border-radius:50%;border:2px solid var(--ac)}
.brand b{font-size:16px;letter-spacing:-.01em;display:block}
.brand small{color:var(--ac);font-size:10px;letter-spacing:.16em;font-weight:700}
.top nav{margin-left:auto;display:flex;gap:24px;font-size:14px;color:var(--tx2)}
.top nav a{position:relative;padding:4px 0;transition:color .2s}
.top nav a:hover{color:var(--tx)}
.top nav a::after{content:"";position:absolute;left:0;bottom:-2px;width:0;height:2px;
 background:var(--ac);transition:width .25s}
.top nav a:hover::after{width:100%}

main{max-width:1180px;margin:0 auto;padding:0 22px 70px}

/* hero */
.hero{padding:56px 0 30px;text-align:center}
.hero h1{font-size:clamp(28px,5vw,46px);font-weight:800;letter-spacing:-.03em;line-height:1.1}
.hero h1 span{color:var(--ac)}
.hero p{color:var(--tx2);font-size:17px;margin-top:14px;max-width:560px;margin-inline:auto}

/* busca */
.busca-wrap{max-width:620px;margin:26px auto 0;position:relative}
.busca-wrap input{width:100%;background:var(--card);border:1px solid var(--bord2);
 color:var(--tx);border-radius:14px;padding:16px 20px 16px 50px;font-size:16px;transition:.2s}
.busca-wrap input:focus{outline:0;border-color:var(--ac);background:rgba(255,255,255,.06)}
.busca-wrap::before{content:"🔍";position:absolute;left:18px;top:50%;transform:translateY(-50%);
 opacity:.5;font-size:16px}

/* abas de loja */
.lojas{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:26px 0 8px}
.lojas button{background:var(--card);border:1px solid var(--bord);color:var(--tx2);
 border-radius:30px;padding:9px 18px;font-size:14px;font-weight:600;cursor:pointer;
 display:flex;align-items:center;gap:8px;transition:.2s}
.lojas button:hover{border-color:var(--bord2);color:var(--tx)}
.lojas button.on{background:var(--tx);color:#06231a;border-color:var(--tx)}
.lojas .pt{width:8px;height:8px;border-radius:50%}

/* barra de ordenacao */
.barrafiltro{display:flex;align-items:center;gap:12px;margin:22px 0 20px;flex-wrap:wrap}
.barrafiltro .cont{color:var(--tx3);font-size:13px}
.barrafiltro select{margin-left:auto;background:var(--card);border:1px solid var(--bord);
 color:var(--tx);border-radius:9px;padding:8px 12px;font-size:13.5px;cursor:pointer}

/* secao destaque */
.sec-tit{display:flex;align-items:center;gap:10px;font-size:15px;font-weight:700;
 margin:38px 0 16px;letter-spacing:-.01em}
.sec-tit i{font-style:normal;font-size:18px}
.sec-tit em{font-style:normal;color:var(--tx3);font-weight:500;font-size:13px;margin-left:auto}

/* grade */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(216px,1fr));gap:18px}
.card{background:var(--card);border:1px solid var(--bord);border-radius:16px;overflow:hidden;
 display:flex;flex-direction:column;position:relative;
 opacity:0;transform:translateY(14px);transition:opacity .5s,transform .5s,border-color .2s,box-shadow .2s}
.card.in{opacity:1;transform:none}
.card:hover{border-color:var(--bord2);box-shadow:0 12px 34px rgba(0,0,0,.35);transform:translateY(-4px)}
.card .foto{background:#fff;height:186px;display:flex;align-items:center;justify-content:center;padding:14px;overflow:hidden}
.card .foto img{max-width:100%;max-height:100%;object-fit:contain;transition:transform .4s}
.card:hover .foto img{transform:scale(1.06)}
.selo{position:absolute;top:11px;left:11px;background:var(--preco);color:#fff;font-size:12px;
 font-weight:800;padding:3px 10px;border-radius:20px;z-index:2}
.lojatag{position:absolute;top:11px;right:11px;z-index:2;display:flex;align-items:center;gap:5px;
 background:rgba(0,0,0,.55);backdrop-filter:blur(4px);padding:3px 9px;border-radius:20px;font-size:11px;font-weight:600}
.lojatag .pt{width:7px;height:7px;border-radius:50%}
.card .txt{padding:14px 15px 16px;flex:1;display:flex;flex-direction:column}
.card .tit{font-size:13.5px;line-height:1.45;min-height:56px;color:var(--tx)}
.card .de{color:var(--tx3);text-decoration:line-through;font-size:12.5px;margin-top:10px}
.card .por{font-size:22px;font-weight:800;color:var(--ac);letter-spacing:-.02em}
.card .cat{margin-top:9px;font-size:10.5px;color:var(--tx3);
 border:1px solid var(--bord);border-radius:20px;padding:1px 9px;align-self:flex-start}
.vazio{grid-column:1/-1;text-align:center;color:var(--tx3);padding:50px;font-size:14px}

/* pagina de produto */
.voltar{display:inline-block;color:var(--tx2);font-size:14px;margin:24px 0 8px}
.voltar:hover{color:var(--ac)}
.prod{display:grid;grid-template-columns:minmax(0,440px) 1fr;gap:38px;align-items:start;margin-top:12px}
.prod .foto{background:#fff;border-radius:18px;padding:30px;display:flex;align-items:center;
 justify-content:center;min-height:360px}
.prod .foto img{max-width:100%;max-height:360px;object-fit:contain}
.prod h1{font-size:24px;letter-spacing:-.02em;line-height:1.25}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 18px}
.chip{font-size:11.5px;color:var(--tx2);border:1px solid var(--bord);border-radius:20px;padding:3px 11px;
 display:flex;align-items:center;gap:6px}
.chip .pt{width:7px;height:7px;border-radius:50%}
.preco-de{color:var(--tx3);text-decoration:line-through;font-size:15px}
.preco-atual{font-size:40px;font-weight:800;color:var(--ac);letter-spacing:-.03em;line-height:1.1}
.desc-tag{display:inline-block;color:var(--preco);font-weight:800;margin-top:2px}
.prova{color:var(--ac);font-weight:700;margin-top:12px;display:flex;align-items:center;gap:7px}
.info-linha{color:var(--tx2);font-size:14.5px;margin-top:7px}
.btn{display:inline-flex;align-items:center;gap:9px;background:var(--preco);color:#fff;font-weight:700;
 padding:15px 32px;border-radius:12px;margin-top:22px;font-size:16px;transition:.2s}
.btn:hover{filter:brightness(1.09);transform:translateY(-2px);box-shadow:0 10px 26px rgba(0,0,0,.3)}
.box{background:var(--card);border:1px solid var(--bord);border-radius:16px;padding:22px;margin-top:26px}
.box h2{font-size:15px;margin-bottom:16px;letter-spacing:-.01em}
.gr{width:100%;height:auto}
.sem-grafico{color:var(--tx3);font-size:14px;padding:30px;text-align:center}
.fatos{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:18px;margin-top:16px}
.fatos div{color:var(--tx3);font-size:12.5px}
.fatos b{display:block;color:var(--tx);font-size:17px;font-weight:700;margin-top:3px}

footer{border-top:1px solid var(--bord);margin-top:60px;padding:30px 22px;text-align:center;
 color:var(--tx3);font-size:12.5px;line-height:1.9}
@media(max-width:760px){.prod{grid-template-columns:1fr}.top nav{display:none}
 .hero{padding:40px 0 20px}}
"""

JS = """
(function(){
  const io=new IntersectionObserver((es)=>{es.forEach(e=>{if(e.isIntersecting){
    e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.06});
  document.querySelectorAll('.card').forEach(c=>io.observe(c));

  const grid=document.getElementById('grid');
  const cards=grid?[...grid.querySelectorAll('.card')]:[];
  const num=e=>parseFloat(e.dataset.preco), qd=e=>parseFloat(e.dataset.queda||0);
  const marc=(f)=>[...document.querySelectorAll('input[data-f=\\"'+f+'\\"]:checked')].map(x=>x.value);
  let q='',ord='desc',fmin=0,fmax=0;

  function passa(k, exceto){
    const p=num(k);
    if(exceto!=='loja'){const lj=marc('loja'); if(lj.length&&!lj.includes(k.dataset.loja))return false;}
    if(exceto!=='cat'){const ct=marc('cat'); if(ct.length&&!ct.includes(k.dataset.cat))return false;}
    if(exceto!=='plat'){const pl=marc('plat');
      if(pl.length&&!pl.some(x=>(k.dataset.plat||'').split(' ').includes(x)))return false;}
    if(q&&!k.dataset.titulo.includes(q))return false;
    if((fmin&&p<fmin)||(fmax&&p>fmax))return false;
    return true;
  }

  function facetas(){
    document.querySelectorAll('.side label[data-f]').forEach(l=>{
      const f=l.dataset.f, v=l.dataset.v; let n=0;
      cards.forEach(k=>{
        if(!passa(k,f))return;
        const ok = f==='plat' ? (k.dataset.plat||'').split(' ').includes(v)
                              : (f==='loja'?k.dataset.loja:k.dataset.cat)===v;
        if(ok)n++;
      });
      const c=l.querySelector('.cnt'); if(c)c.textContent=n;
      l.classList.toggle('off', n===0);
      const inp=l.querySelector('input'); if(inp)inp.disabled=(n===0&&!inp.checked);
    });
  }

  function aplica(){
    if(!grid) return;
    const ativo = marc('loja').length||marc('cat').length||marc('plat').length||fmin||fmax||q;
    const dst=document.getElementById('destaques'); if(dst)dst.style.display=ativo?'none':'';
    const gt=document.getElementById('gradetit');
    if(gt)gt.textContent=ativo?'Resultados dos filtros':'Todas as ofertas';
    const vis=[];
    cards.forEach(k=>{
      const s=passa(k,null);
      const oculto=k.style.display==='none'||k.classList.contains('saindo');
      if(s){
        vis.push(k);
        if(oculto){
          k.classList.remove('saindo'); k.style.display=''; k.classList.remove('in');
          requestAnimationFrame(()=>requestAnimationFrame(()=>k.classList.add('in')));
        }else if(!k.classList.contains('in')){
          k.classList.add('in');
        }
      }else if(!oculto){
        k.classList.add('saindo'); k.classList.remove('in');
        ((kk)=>setTimeout(()=>{if(kk.classList.contains('saindo')){kk.style.display='none';kk.classList.remove('saindo');}},220))(k);
      }
    });
    vis.sort((a,b)=> ord==='menor'?num(a)-num(b): ord==='maior'?num(b)-num(a):
      ord==='queda'?qd(b)-qd(a): parseFloat(b.dataset.desc)-parseFloat(a.dataset.desc));
    vis.forEach(k=>grid.appendChild(k));
    const c=document.getElementById('cont'); if(c)c.textContent=vis.length+' produto(s)';
    const nr=document.getElementById('nres'); if(nr)nr.textContent=vis.length;
    const vz=document.getElementById('vazio');
    if(vz){ if(vis.length){ vz.style.display='none'; }
      else{ vz.style.display='block';
        if(q){ vz.innerHTML='Nenhum resultado encontrado.<br><button class=\\"sug-btn\\">Sugerir esse produto — a gente cadastra e monitora o preço</button>';
          const sb=vz.querySelector('.sug-btn'); if(sb)sb.onclick=function(){abrirSug(q);}; }
        else{ vz.textContent='Nenhum produto com esses filtros.'; } } }
    facetas();
  }

  document.querySelectorAll('.side input[data-f]').forEach(i=>i.addEventListener('change',aplica));
  // abas de loja do topo (Todas / Mercado Livre / Amazon) -> sincroniza com os checkboxes e filtra
  document.querySelectorAll('.lojas button').forEach(b=>b.addEventListener('click',()=>{
    document.querySelectorAll('.lojas button').forEach(x=>x.classList.remove('on'));
    b.classList.add('on');
    const lj=b.dataset.loja||'';
    document.querySelectorAll('.side input[data-f=loja]').forEach(i=>{ i.checked = lj ? (i.value===lj) : false; });
    aplica();
  }));
  const pmin=document.getElementById('pmin'),pmax=document.getElementById('pmax');
  [pmin,pmax].forEach(el=>el&&el.addEventListener('input',()=>{
    fmin=+((pmin||{}).value)||0; fmax=+((pmax||{}).value)||0; aplica();}));
  document.querySelectorAll('.faixas button').forEach(b=>b.addEventListener('click',()=>{
    document.querySelectorAll('.faixas button').forEach(x=>x.classList.remove('on'));
    b.classList.add('on'); fmin=+b.dataset.min||0; fmax=+b.dataset.max||0;
    if(pmin)pmin.value=fmin||''; if(pmax)pmax.value=fmax||''; aplica();}));
  const os=document.getElementById('ord');
  if(os)os.addEventListener('change',e=>{ord=e.target.value;aplica()});
  const lp=document.getElementById('limpar');
  if(lp)lp.addEventListener('click',()=>{document.querySelectorAll('.side input[data-f]').forEach(i=>i.checked=false);
    if(pmin)pmin.value='';if(pmax)pmax.value='';fmin=fmax=0;
    document.querySelectorAll('.faixas button').forEach(x=>x.classList.remove('on'));
    const f0=document.querySelector('.faixas button');if(f0)f0.classList.add('on');aplica();});

  const side=document.getElementById('side'),bd=document.getElementById('bd');
  const abrir=(v)=>{if(side){side.classList.toggle('aberta',v);bd&&bd.classList.toggle('on',v)}};
  const fb=document.getElementById('filtrosbtn'); if(fb)fb.addEventListener('click',()=>abrir(true));
  const fc=document.getElementById('fechar'); if(fc)fc.addEventListener('click',()=>abrir(false));
  if(bd)bd.addEventListener('click',()=>abrir(false));
  const ap=document.getElementById('aplicar');
  if(ap)ap.addEventListener('click',()=>{abrir(false);
    const g=document.getElementById('grade'); if(g)g.scrollIntoView({behavior:'smooth',block:'start'});});

  const bi=document.getElementById('busca'),ac=document.getElementById('ac');
  function auto(v){
    if(!ac||!window.PROD)return;
    const t=(v||'').toLowerCase().trim();
    if(t.length<2){ac.classList.remove('on');return}
    const m=window.PROD.filter(x=>x.t.toLowerCase().includes(t)).slice(0,6);
    if(!m.length){ac.innerHTML='<div class=\\"none\\">Nada encontrado para \\"'+t+'\\".<br><button class=\\"sug-btn sug-sm\\">Sugerir esse produto</button></div>';ac.classList.add('on');
      const sb=ac.querySelector('.sug-btn'); if(sb)sb.onclick=function(){abrirSug(t);}; return}
    ac.innerHTML=m.map(x=>'<a href=\\"'+x.u+'\\"><img src=\\"'+x.img+'\\" alt=\\"\\" loading=\\"lazy\\">'
      +'<span class=\\"t\\">'+x.t+'</span><span class=\\"p\\">'+x.p+'</span></a>').join('');
    ac.classList.add('on');
  }
  if(bi){
    bi.addEventListener('input',e=>{q=e.target.value.toLowerCase().trim();auto(e.target.value);aplica()});
    bi.addEventListener('focus',e=>auto(e.target.value));
    document.addEventListener('click',e=>{if(ac&&!e.target.closest('.busca-wrap'))ac.classList.remove('on')});
  }
  // fotos 3D do hero: tilt (mouse) + flutuar + parallax (scroll)
  const tiles=[...document.querySelectorAll('.photo3d')];
  if(tiles.length){
    let px=0,py=0;
    addEventListener('mousemove',e=>{px=(e.clientX/innerWidth-.5);py=(e.clientY/innerHeight-.5);},{passive:true});
    const t0=Date.now();
    (function anim(){requestAnimationFrame(anim);
      const y=window.scrollY,t=(Date.now()-t0)/1000;
      tiles.forEach(el=>{
        const sp=+el.dataset.speed||.2, ph=+el.dataset.ph||0, rz=+el.dataset.rot||0;
        const ty=y*sp+Math.sin(t*.8+ph)*9;
        const ry=px*16, rx=-py*12;
        el.style.transform='translateY('+ty.toFixed(1)+'px) rotateX('+rx.toFixed(1)+'deg) rotateY('+ry.toFixed(1)+'deg) rotate('+rz+'deg)';
      });
    })();
  }
  // parallax dos objetos do hero (legado)
  const floats=[...document.querySelectorAll('.float')];
  if(floats.length){
    let tick=false;
    const move=()=>{const y=window.scrollY;
      floats.forEach(f=>{f.style.transform='translate3d(0,'+(y*(+f.dataset.speed||.2))+'px,0)'});tick=false;};
    window.addEventListener('scroll',()=>{if(!tick){requestAnimationFrame(move);tick=true;}},{passive:true});
    move();
  }
  // header condensa ao rolar
  const top=document.querySelector('.top');
  if(top){const onScroll=()=>top.classList.toggle('scrolled',window.scrollY>20);
    window.addEventListener('scroll',onScroll,{passive:true});onScroll();}
  // contadores do hero animam
  document.querySelectorAll('.herostats b').forEach(el=>{
    const alvo=parseInt(el.textContent);if(isNaN(alvo))return;let n=0;
    const step=Math.max(1,Math.ceil(alvo/28));
    const t=setInterval(()=>{n+=step;if(n>=alvo){n=alvo;clearInterval(t)}el.textContent=n},26);
  });

  aplica();
})();
"""
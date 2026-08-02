"""Tema CLARO — estilo comparador de precos (Google Shopping / Buscape)."""

CSS = """
:root{--bg:#f6f7f9;--pane:#fff;--line:#e8eaed;--line2:#dadce0;
 --tx:#1f2328;--tx2:#5f6368;--tx3:#9aa0a6;--ac:{{AC}};--preco:{{PRECO}};--barra:{{BARRA}}}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--tx);
 font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Arial,sans-serif;
 -webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}img{display:block}

.top{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.9);
 backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.top .in{max-width:1340px;margin:0 auto;padding:11px 22px;display:flex;align-items:center;gap:13px}
.top img{width:40px;height:40px;border-radius:11px}
.brand b{font-size:16px;letter-spacing:-.02em;display:block}
.brand small{color:var(--ac);font-size:9.5px;letter-spacing:.14em;font-weight:700}
.top nav{margin-left:auto;display:flex;gap:8px}
.top nav a{font-size:14px;color:var(--tx2);padding:7px 14px;border-radius:20px;transition:.15s}
.top nav a:hover{background:var(--bg);color:var(--tx)}

.hero{background:var(--pane);border-bottom:1px solid var(--line);padding:52px 22px 34px;text-align:center}
.hero h1{font-size:clamp(24px,4vw,38px);font-weight:800;letter-spacing:-.03em;line-height:1.12;color:var(--tx)}
.hero h1 span{color:var(--ac)}
.hero p{color:var(--tx2);font-size:16px;margin-top:12px}
.busca-wrap{max-width:660px;margin:26px auto 0;position:relative}
.busca-wrap input{width:100%;background:var(--pane);border:1px solid var(--line2);color:var(--tx);
 border-radius:30px;padding:16px 22px 16px 52px;font-size:16px;box-shadow:0 1px 6px rgba(0,0,0,.05);transition:.2s}
.busca-wrap input:focus{outline:0;border-color:var(--ac);box-shadow:0 3px 16px rgba(0,0,0,.1)}

.lojas{display:flex;gap:9px;justify-content:center;flex-wrap:wrap;margin-top:20px}
.lojas button{background:var(--pane);border:1px solid var(--line2);color:var(--tx2);
 border-radius:30px;padding:8px 17px;font-size:13.5px;font-weight:600;cursor:pointer;
 display:flex;align-items:center;gap:8px;transition:.18s}
.lojas button:hover{border-color:var(--tx3)}
.lojas button.on{background:var(--tx);color:#fff;border-color:var(--tx)}
.lojas .pt{width:8px;height:8px;border-radius:50%}

main{max-width:1340px;margin:0 auto;padding:0 22px 70px}
.sec-tit{display:flex;align-items:center;gap:9px;font-size:15px;font-weight:700;
 margin:34px 0 15px;color:var(--tx)}
.sec-tit i{font-style:normal;font-size:17px}
.sec-tit em{font-style:normal;color:var(--tx3);font-weight:500;font-size:12.5px;margin-left:auto}
.barrafiltro{display:flex;margin:16px 0 18px}
.barrafiltro select{margin-left:auto;background:var(--pane);border:1px solid var(--line2);
 color:var(--tx);border-radius:9px;padding:8px 12px;font-size:13.5px;cursor:pointer}

.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}
.card{background:var(--pane);border:1px solid var(--line);border-radius:14px;overflow:hidden;
 display:flex;flex-direction:column;position:relative;
 opacity:0;transform:translateY(12px);transition:opacity .45s,transform .45s,box-shadow .2s,border-color .2s}
.card.in{opacity:1;transform:none}
.card:hover{box-shadow:0 8px 26px rgba(0,0,0,.1);border-color:var(--line2);transform:translateY(-3px)}
.card .foto{background:#fff;height:172px;display:flex;align-items:center;justify-content:center;padding:16px}
.card .foto img{max-width:100%;max-height:100%;object-fit:contain;transition:transform .35s}
.card:hover .foto img{transform:scale(1.05)}
.selo{position:absolute;top:10px;left:10px;background:var(--preco);color:#fff;font-size:12px;
 font-weight:800;padding:3px 9px;border-radius:8px;z-index:2}
.lojatag{position:absolute;top:10px;right:10px;z-index:2;display:flex;align-items:center;gap:5px;
 background:#fff;border:1px solid var(--line);padding:3px 8px;border-radius:20px;font-size:10.5px;
 font-weight:700;color:var(--tx2)}
.lojatag{padding:0;background:none;border:0}
.lg{display:inline-flex;align-items:center;border-radius:6px;padding:3px 8px;
 font-weight:800;font-size:11px;letter-spacing:-.02em;line-height:1;box-shadow:0 1px 3px rgba(0,0,0,.12)}
.lg-mercadolivre{background:#ffe600;color:#2d3277}
.lg-amazon{background:#232f3e;color:#fff}
.lg-amazon i{color:#ff9900;font-style:normal}
.lg-aliexpress{background:#e62e04;color:#fff}
/* termometro */
.termo{display:inline-flex;align-items:center;gap:6px;font-size:11.5px;font-weight:700;
 border-radius:6px;padding:3px 9px;margin-top:9px;align-self:flex-start}
.termo::before{content:"";width:8px;height:8px;border-radius:50%}
.t-verde{background:#e6f4ea;color:#137333}.t-verde::before{background:#137333}
.t-amarelo{background:#fef7e0;color:#a56300}.t-amarelo::before{background:#f9ab00}
.t-vermelho{background:#fce8e6;color:#c5221f}.t-vermelho::before{background:#d93025}
.t-cinza{background:#f1f3f4;color:#5f6368}.t-cinza::before{background:#9aa0a6}
.termo-g{font-size:14px;padding:8px 14px;border-radius:10px;margin:14px 0 4px}
.termo-g::before{width:11px;height:11px}
.rec{color:var(--tx2);font-size:14.5px;margin-top:8px;line-height:1.5}
/* faixa de preco */
.faixas{display:flex;gap:7px;flex-wrap:wrap;margin-top:14px;justify-content:center}
.faixas button{background:var(--pane);border:1px solid var(--line2);color:var(--tx2);
 border-radius:20px;padding:6px 14px;font-size:12.5px;cursor:pointer;transition:.15s}
.faixas button:hover{border-color:var(--tx3)}
.faixas button.on{background:var(--ac);color:#fff;border-color:var(--ac)}
/* nav categorias */
.catnav{display:flex;gap:8px;overflow-x:auto;padding:14px 0 2px;margin-bottom:6px}
.catnav a{white-space:nowrap;font-size:13px;color:var(--tx2);background:var(--pane);
 border:1px solid var(--line);border-radius:20px;padding:6px 14px;transition:.15s}
.catnav a:hover,.catnav a.on{background:var(--tx);color:#fff;border-color:var(--tx)}
.card .txt{padding:12px 14px 15px;flex:1;display:flex;flex-direction:column}
.card .tit{font-size:13px;line-height:1.42;min-height:54px;color:var(--tx)}
.spark{width:100%;height:34px;margin:8px 0 4px;opacity:.9}
.linha-preco{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
.card .de{color:var(--tx3);text-decoration:line-through;font-size:12px}
.card .por{font-size:20px;font-weight:800;color:var(--tx);letter-spacing:-.02em}
.card .cat{margin-top:8px;font-size:10.5px;color:var(--tx3)}
.vazio{grid-column:1/-1;text-align:center;color:var(--tx3);padding:50px;font-size:14px}

.voltar{display:inline-block;color:var(--tx2);font-size:14px;margin:22px 0 6px}
.voltar:hover{color:var(--ac)}
.prod{display:grid;grid-template-columns:minmax(0,430px) 1fr;gap:36px;align-items:start;margin-top:10px}
.prod .foto{background:#fff;border:1px solid var(--line);border-radius:16px;padding:30px;
 display:flex;align-items:center;justify-content:center;min-height:350px}
.prod .foto img{max-width:100%;max-height:350px;object-fit:contain}
.prod h1{font-size:23px;letter-spacing:-.02em;line-height:1.25;color:var(--tx)}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 18px}
.chip{font-size:11.5px;color:var(--tx2);background:var(--pane);border:1px solid var(--line);
 border-radius:20px;padding:3px 11px;display:flex;align-items:center;gap:6px}
.chip.chip-loja{background:none;border:0;padding:0}
.chip .pt{width:7px;height:7px;border-radius:50%}
.preco-de{color:#ef6c6c;text-decoration:line-through;font-size:15px;font-weight:600}
.preco-atual{font-size:38px;font-weight:800;color:var(--tx);letter-spacing:-.03em;line-height:1.1}
.desc-tag{display:inline-block;background:#fce8e6;color:var(--preco);font-weight:700;
 padding:3px 11px;border-radius:8px;margin-top:8px;font-size:14px}
.prova{color:var(--ac);font-weight:700;margin-top:12px}
.info-linha{color:var(--tx2);font-size:14.5px;margin-top:6px}
.btn{display:inline-flex;align-items:center;gap:9px;background:var(--ac);color:#fff;font-weight:700;
 padding:15px 32px;border-radius:11px;margin-top:22px;font-size:16px;box-shadow:0 4px 14px rgba(0,0,0,.12);transition:.2s}
.btn:hover{filter:brightness(1.06);transform:translateY(-2px)}
.box{background:var(--pane);border:1px solid var(--line);border-radius:16px;padding:22px;margin-top:24px}
.box h2{font-size:15px;margin-bottom:16px;color:var(--tx)}
.gr{width:100%;height:auto}
.sem-grafico{color:var(--tx3);font-size:14px;padding:30px;text-align:center}
.fatos{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:16px;margin-top:16px}
.fatos div{color:var(--tx3);font-size:12.5px}
.fatos b{display:block;color:var(--tx);font-size:17px;font-weight:700;margin-top:3px}

footer{border-top:1px solid var(--line);margin-top:56px;padding:28px 22px;text-align:center;
 color:var(--tx3);font-size:12.5px;line-height:1.9;background:var(--pane)}
@media(max-width:760px){.prod{grid-template-columns:1fr}.top nav{display:none}}

/* ===== layout com sidebar ===== */
.layout{display:grid;grid-template-columns:212px 1fr;gap:22px;align-items:start;margin-top:8px}
.side{position:sticky;top:74px;background:var(--pane);border:1px solid var(--line);
 border-radius:14px;padding:18px 18px 22px}
.side .fechar{display:none;position:absolute;top:12px;right:14px;font-size:24px;
 background:none;border:0;color:var(--tx2);cursor:pointer;line-height:1}
.fgrupo{margin-bottom:20px}
.fgrupo h4{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--tx3);margin-bottom:10px}
.fgrupo label{display:flex;align-items:center;gap:10px;font-size:14px;color:var(--tx2);
 padding:5px 0;cursor:pointer}
.fgrupo label:hover{color:var(--tx)}
.fgrupo input[type=checkbox]{accent-color:var(--ac);width:16px;height:16px;cursor:pointer}
.precorow{display:flex;gap:8px;align-items:center}
.precorow input{width:100%;background:var(--bg);border:1px solid var(--line2);border-radius:8px;
 padding:8px 10px;font-size:13px;color:var(--tx)}
.precorow span{color:var(--tx3);font-size:13px}
.limpar{font-size:13px;color:var(--ac);cursor:pointer;background:none;border:0;padding:6px 0 0;font-weight:600}
.filtros-btn{display:none}.backdrop{display:none}
/* autocomplete */
.busca-wrap{position:relative}
.ac{position:absolute;left:0;right:0;top:calc(100% + 8px);background:var(--pane);
 border:1px solid var(--line);border-radius:14px;box-shadow:0 14px 40px rgba(0,0,0,.16);
 overflow:hidden;z-index:60;display:none;text-align:left}
.ac.on{display:block}
.ac a{display:flex;align-items:center;gap:12px;padding:11px 15px;border-bottom:1px solid var(--line)}
.ac a:last-child{border-bottom:0}
.ac a:hover,.ac a.sel{background:var(--bg)}
.ac img{width:40px;height:40px;object-fit:contain;background:#fff;border:1px solid var(--line);
 border-radius:8px;flex:none;padding:2px}
.ac .t{flex:1;font-size:13.5px;color:var(--tx);line-height:1.35}
.ac .p{font-weight:800;color:var(--ac);font-size:14px;white-space:nowrap}
.ac .none{padding:14px 16px;color:var(--tx3);font-size:13.5px}
/* responsivo */
@media(max-width:980px){
 .layout{grid-template-columns:1fr}
 .filtros-btn{display:inline-flex;align-items:center;gap:8px;background:var(--tx);color:#fff;
  border:0;border-radius:10px;padding:11px 18px;font-size:14px;font-weight:600;cursor:pointer;margin:4px 0 16px}
 .side{position:fixed;inset:0 0 0 auto;width:min(330px,88vw);z-index:100;border-radius:0;
  transform:translateX(100%);transition:transform .26s ease;overflow-y:auto;max-height:100vh;padding-top:52px}
 .side.aberta{transform:none;box-shadow:-12px 0 44px rgba(0,0,0,.28)}
 .side .fechar{display:block}
 .backdrop.on{display:block;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:99}
}
@media(max-width:1100px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:820px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:640px){
 .grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
 .card .foto{height:140px;padding:12px}.card .tit{font-size:12px;min-height:48px}
 .card .por{font-size:17px}.card .txt{padding:11px 12px 13px}.spark{height:28px}
 main{padding:0 14px 60px}.hero{padding:34px 16px 22px}
 .busca-wrap input{padding:14px 18px 14px 46px;font-size:15px}
 .sec-tit{font-size:14px;margin:26px 0 12px}.fatos{grid-template-columns:repeat(2,1fr)}
 .preco-atual{font-size:32px}.prod h1{font-size:20px}
}
@media(max-width:380px){.grid{grid-template-columns:1fr}}
.fgrupo label .nm{flex:1}
.fgrupo label .cnt{color:var(--tx3);font-size:12px;font-variant-numeric:tabular-nums;font-weight:600}
.fgrupo label.off{opacity:.4}
.fgrupo label.off input{cursor:not-allowed}
.aplicar{width:100%;background:var(--ac);color:#fff;border:0;border-radius:10px;padding:13px;
 font-size:14px;font-weight:700;cursor:pointer;margin-top:8px;transition:.15s}
.aplicar:hover{filter:brightness(1.06)}

/* ==== REDESIGN ==== */
body{background:#f4f6f9;font-size:15px}
.hero{background:linear-gradient(180deg,#fff 0%,#fbfcfe 100%);border-bottom:1px solid var(--line);padding:60px 22px 40px}
.hero h1{font-size:clamp(27px,4.4vw,44px);font-weight:800;letter-spacing:-.035em;line-height:1.08}
.hero h1 span{color:var(--ac)}
.hero p{font-size:17px;color:var(--tx2);margin-top:14px}
.herostats{display:flex;gap:26px;justify-content:center;margin:22px auto 0;flex-wrap:wrap;color:var(--tx2);font-size:13.5px}
.herostats b{color:var(--tx);font-weight:700}
.busca-wrap input{border-radius:16px;padding:17px 22px 17px 52px;font-size:16px;
 border:1.5px solid var(--line2);box-shadow:0 2px 14px rgba(20,30,60,.06)}
.lojas button{padding:9px 18px;font-weight:600}
.lojas button.on{box-shadow:0 4px 14px rgba(20,30,60,.18)}

.sec-tit{font-size:17px;font-weight:800;letter-spacing:-.02em;margin:40px 0 16px}
.sec-tit i{width:30px;height:30px;display:inline-flex;align-items:center;justify-content:center;
 background:var(--ac);border-radius:9px;font-size:16px;color:#06231a}
.sec-tit em{background:var(--pane);border:1px solid var(--line);border-radius:20px;padding:3px 11px}

.card{border:1px solid var(--line);border-radius:16px;background:var(--pane);
 transition:opacity .45s,transform .28s cubic-bezier(.2,.7,.3,1),box-shadow .25s,border-color .2s}
.card:hover{box-shadow:0 16px 38px rgba(20,30,55,.15);border-color:var(--ac);transform:translateY(-6px)}
.card .foto{height:180px}
.card.hot{border-color:var(--preco)}
.card.hot::after{content:"OFERTA QUENTE";position:absolute;top:0;left:0;right:0;
 background:var(--preco);color:#fff;font-size:9.5px;font-weight:800;letter-spacing:.14em;
 text-align:center;padding:4px;transform:translateY(-100%);transition:transform .25s;z-index:1}
.card.hot:hover::after{transform:none}
.card.hot:hover .selo,.card.hot:hover .lojatag{transform:translateY(22px);transition:transform .25s}
.card .selo,.card .lojatag{transition:transform .25s;z-index:4}
.selo{top:12px;left:12px;font-size:13px;font-weight:800;padding:4px 11px;border-radius:9px;
 letter-spacing:-.02em;box-shadow:0 3px 10px rgba(216,90,48,.35)}
.lojatag{top:12px;right:12px}
.card .tit{font-size:13px;font-weight:500;color:#2b3138;min-height:52px}
.card .por{font-size:22px;font-weight:800}
.economia{display:inline-flex;align-items:center;gap:5px;background:#e6f4ea;color:#137333;
 font-size:11.5px;font-weight:700;padding:3px 9px;border-radius:7px;margin-top:9px;align-self:flex-start}
.termo{font-weight:700;font-size:11.5px;padding:4px 10px;border-radius:7px;margin-top:10px}

.btn{background:var(--ac);color:#06231a;font-weight:800;padding:16px 34px;border-radius:13px;
 font-size:16px;box-shadow:0 8px 22px rgba(30,160,110,.28)}
.btn:hover{transform:translateY(-2px);box-shadow:0 12px 30px rgba(30,160,110,.36)}
.preco-atual{font-size:42px}
.desc-tag{background:#fce8e6;color:#c5221f;font-weight:800}
.termo-g{font-size:14.5px;padding:9px 15px;border-radius:11px}

.side{border-radius:16px;box-shadow:0 4px 20px rgba(20,30,60,.05)}
.fgrupo h4{font-weight:800;color:var(--tx2)}
.aplicar{border-radius:12px;font-weight:800;box-shadow:0 8px 20px rgba(30,160,110,.25)}
.top{border-bottom:1px solid var(--line)}
.top .brand small{letter-spacing:.13em}

/* bloco de ofertas quentes */
.hotbox{background:linear-gradient(135deg,#fff4f0 0%,#ffece6 100%);border:1px solid #ffd9cc;
 border-radius:18px;padding:20px 20px 24px;margin:30px 0}
.hotbox .sec-tit{margin:0 0 16px}
.hotbox .sec-tit i{background:var(--preco);color:#fff}
.hotbox .sec-tit em{background:#fff;border-color:#ffd9cc;color:var(--preco);font-weight:800}

/* ==== HEADER VERDE + CATBAR ==== */
.top{background:var(--barra);border-bottom:0}
.top .brand b{color:#fff}
.top .brand small{color:var(--ac)}
.top img{border-color:var(--ac)}
.top nav a{color:rgba(255,255,255,.82)}
.top nav a:hover{background:rgba(255,255,255,.12);color:#fff}
.catbar{background:var(--barra);border-top:1px solid rgba(255,255,255,.08);
 position:relative;z-index:40}
.catbar .in{max-width:1340px;margin:0 auto;padding:0 14px;display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}
.catbar .in::-webkit-scrollbar{display:none}
.catbar a{display:flex;align-items:center;gap:8px;white-space:nowrap;color:rgba(255,255,255,.78);
 font-size:13.5px;font-weight:600;padding:13px 15px;border-bottom:2px solid transparent;transition:.15s}
.catbar a:hover{color:#fff;border-bottom-color:var(--ac)}
.catbar a.on{color:#fff;border-bottom-color:var(--ac)}
.catbar svg{width:19px;height:19px;stroke:currentColor;fill:none;stroke-width:1.7;
 stroke-linecap:round;stroke-linejoin:round;flex:none}
@media(max-width:640px){.catbar a span{display:none}.catbar a{padding:12px 14px}}

/* ==== REDESIGN 2 ==== */
body{font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
 background:#f3f5f8;color:#141922}
h1,h2,.hero h1,.prod h1,.por,.preco-atual,.sec-tit{font-family:"Sora","Inter",sans-serif}
.mi{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.7;stroke-linecap:round;
 stroke-linejoin:round;vertical-align:-3px;flex:none}

/* header condensa no scroll */
.top .in{transition:height .2s;height:64px}
.top.scrolled .in{height:54px}
.top.scrolled img{width:38px;height:38px}

/* hero anima na entrada */
.hero>*{opacity:0;animation:up .6s cubic-bezier(.2,.7,.3,1) forwards}
.hero h1{animation-delay:.02s}.hero p{animation-delay:.10s}
.herostats{animation-delay:.18s}.busca-wrap{animation-delay:.24s}
.lojas{animation-delay:.30s}.faixas{animation-delay:.36s}
@keyframes up{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
.busca-wrap::before{content:"";position:absolute;left:20px;top:50%;transform:translateY(-50%);
 width:19px;height:19px;opacity:.5;
 background:no-repeat center/contain url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%235b6470' stroke-width='2' stroke-linecap='round'><circle cx='11' cy='11' r='7'/><path d='M21 21l-4-4'/></svg>")}
.busca-wrap input{padding-left:52px}

/* sec-tit com chip SVG */
.sec-tit i{width:30px;height:30px;display:inline-flex;align-items:center;justify-content:center;
 background:var(--ac);border-radius:9px}
.sec-tit i svg{width:18px;height:18px;stroke:#06231a;fill:none;stroke-width:1.8;
 stroke-linecap:round;stroke-linejoin:round}
.hotbox .sec-tit i svg{stroke:#fff}

/* cards mais premium */
.card{border-radius:16px;box-shadow:0 1px 2px rgba(20,25,40,.04)}
.card:hover{box-shadow:0 18px 40px rgba(20,30,60,.16)}
.card .tit{font-weight:500;letter-spacing:-.01em}
.economia .mi{display:none}
.prova .mi,.info-linha .mi{stroke:currentColor}
.prova{display:flex;align-items:center;gap:7px}
.info-linha{display:flex;align-items:center;gap:8px}

/* botoes com feedback */
.btn,.aplicar,.lojas button,.faixas button,.catbar a,.top nav a{will-change:transform}
.btn:active,.aplicar:active{transform:translateY(0) scale(.98)}
.lojas button:active,.faixas button:active{transform:scale(.96)}
.filtros-btn{display:none}
@media(max-width:980px){.filtros-btn{display:inline-flex;align-items:center;gap:8px}}
.filtros-btn .mi{stroke:#fff}

/* pagina de redes */
.rede{flex-direction:row!important;align-items:center;gap:14px;padding:18px 20px}
.rede .mi{width:24px;height:24px;stroke:var(--ac)}
.rede b{font-size:15px;font-weight:600}

/* focus acessivel */
a:focus-visible,button:focus-visible,input:focus-visible{outline:2px solid var(--ac);outline-offset:2px}

@media (prefers-reduced-motion: reduce){.hero>*{opacity:1;animation:none}.card{opacity:1;transform:none}}
.no-js .card{opacity:1;transform:none}

/* ==== REFINO ==== */
/* marca clicavel no header */
.marca{display:flex;align-items:center;gap:13px;text-decoration:none}
.marca:hover .brand b{color:var(--ac)}
/* logo sem borda branca (fundo da marca + corte circular) */
.top img{border:0;background:var(--barra);object-fit:cover;box-shadow:0 0 0 2px var(--ac)}

/* preco: atual a esquerda, "de" a direita em vermelho claro */
.linha-preco{display:flex;align-items:baseline;gap:9px;flex-wrap:wrap}
.linha-preco .de{color:#ef6c6c;text-decoration:line-through;font-size:13px;font-weight:600}

/* espaco entre o termometro e o preco */
.termo{margin-bottom:8px}
.card .txt .spark{margin-top:2px}
.linha-preco{margin-top:6px}

/* dot de "coletando historico" piscando */
.termo.t-cinza::before{animation:pisca 1.1s ease-in-out infinite}
@keyframes pisca{0%,100%{opacity:.35;transform:scale(.85)}50%{opacity:1;transform:scale(1.15)}}

/* rodape ancorado nos cantos */
footer{border-top:1px solid var(--line);margin-top:56px;background:var(--barra);color:rgba(255,255,255,.7)}
.foot-in{max-width:1340px;margin:0 auto;padding:30px 22px;display:flex;align-items:center;
 gap:24px;flex-wrap:wrap}
.foot-marca{display:flex;align-items:center;gap:12px;text-decoration:none;color:#fff}
.foot-marca img{width:44px;height:44px;border-radius:50%;box-shadow:0 0 0 2px var(--ac);
 background:var(--barra);object-fit:cover}
.foot-marca b{font-size:15px;display:block}
.foot-marca small{color:var(--ac);font-size:10px;letter-spacing:.13em;font-weight:700}
.foot-nav{display:flex;gap:18px}
.foot-nav a{color:rgba(255,255,255,.78);font-size:14px}
.foot-nav a:hover{color:#fff}
.foot-aviso{margin-left:auto;text-align:right;font-size:12px;color:rgba(255,255,255,.5);line-height:1.7;max-width:420px}
@media(max-width:760px){.foot-in{flex-direction:column;align-items:flex-start}
 .foot-aviso{margin-left:0;text-align:left}}

/* ==== PRODUTO ==== */
.voltar{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1px solid var(--line2);
 border-radius:11px;padding:10px 16px;font-size:14px;font-weight:600;color:var(--tx2);
 margin:2px 0 10px;transition:.16s;box-shadow:0 1px 3px rgba(20,25,40,.05)}
.voltar:hover{border-color:var(--ac);color:var(--tx);transform:translateX(-3px);
 box-shadow:0 4px 12px rgba(20,30,60,.1)}
.voltar .mi{width:17px;height:17px;stroke:currentColor}
/* selos de beneficios */
.beneficios{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 6px}
.benef{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1px solid var(--line);
 border-radius:11px;padding:11px 15px;font-size:14px;font-weight:600;color:var(--tx);
 box-shadow:0 1px 3px rgba(20,25,40,.05)}
.benef .mi{width:19px;height:19px;stroke-width:1.8}
.benef.frete{background:#e6f4ea;border-color:#c6e6d1;color:#137333}
.benef.frete .mi{stroke:#137333}
.benef.pix{background:#eafaf3;border-color:#bfe9d6;color:#0e8a5f}
.benef.pix .mi{stroke:#0e8a5f}
.benef.parc{color:var(--tx2)}.benef.parc .mi{stroke:var(--tx2)}
/* recomendacao com mais peso */
.rec{background:#f4f6f9;border-radius:11px;padding:13px 16px;color:var(--tx2);font-size:14.5px;
 line-height:1.55;margin-top:12px;border-left:3px solid var(--ac)}
.desc-tag{font-size:15px;padding:5px 13px}
.termo-g{font-size:15px;padding:9px 16px}

/* ==== FULL-BLEED (marca/nav nos cantos) ==== */
.top .in{max-width:none;padding-left:34px;padding-right:34px}
.catbar .in{max-width:none;padding-left:30px;padding-right:30px}
.foot-in{max-width:none;padding-left:34px;padding-right:34px}
@media(max-width:640px){
 .top .in,.catbar .in,.foot-in{padding-left:16px;padding-right:16px}
}

/* ==== LARGURA (menos espaco em branco) ==== */
main{max-width:1660px}
.hotbox{margin-left:0;margin-right:0}
.grid{grid-template-columns:repeat(auto-fill,minmax(236px,1fr))}
@media(max-width:1400px){.grid{grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}}
@media(max-width:1100px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:820px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:380px){.grid{grid-template-columns:1fr}}

/* ==== HERO 3D (objetos parallax) ==== */
.hero{position:relative;overflow:hidden}
.hero>*:not(.hero-bg){position:relative;z-index:2}
.hero-bg{position:absolute;inset:0;z-index:0;pointer-events:none;overflow:hidden;
 opacity:1!important;animation:none!important}
.float{position:absolute;will-change:transform}
.float .bob{width:100%;height:100%;animation:bob 7s ease-in-out infinite;
 transform:rotate(var(--r,0deg))}
.float svg{width:100%;height:100%;display:block}
.float.f0 svg{fill:var(--ac);opacity:.16}
.float.f1 svg{fill:#123a2c;opacity:.10}
.float svg [stroke]{stroke:var(--ac)}
@keyframes bob{0%,100%{transform:rotate(var(--r,0deg)) translateY(0)}
 50%{transform:rotate(var(--r,0deg)) translateY(-16px)}}
@media(max-width:760px){.float{display:none}}
@media (prefers-reduced-motion: reduce){.float .bob{animation:none}}

/* ==== HERO FOTOS 3D ==== */
.hero{position:relative;overflow:hidden}
.hero>*:not(.hero-bg){position:relative;z-index:2}
.hero-bg{position:absolute;inset:0;z-index:0;pointer-events:none;overflow:hidden;
 perspective:1100px;opacity:1!important;animation:none!important}
.photo3d{position:absolute;border-radius:16px;overflow:hidden;background:#fff;
 box-shadow:0 22px 48px rgba(20,30,60,.20),0 4px 12px rgba(20,30,60,.10);
 transform-style:preserve-3d;will-change:transform}
.photo3d{pointer-events:auto;cursor:pointer;text-decoration:none}
.hero-bg a{pointer-events:auto}
/* clique atravessa o texto do hero -> a FOTO INTEIRA fica clicavel (busca/abas seguem clicaveis) */
.hero>h1,.hero>p,.hero>.herostats{pointer-events:none}
.hero>h1 span{pointer-events:none}
.hero .busca-wrap,.hero .lojas,.hero .faixas{pointer-events:auto}
.photo3d img{width:100%;height:100%;object-fit:contain;display:block;padding:12px;
 background:#fff;transition:transform .22s ease}
.photo3d:hover{box-shadow:0 30px 60px rgba(20,30,60,.30),0 6px 16px rgba(20,30,60,.16);z-index:5}
.photo3d:hover img{transform:scale(1.07)}
.photo3d::after{content:"";position:absolute;inset:0;border-radius:16px;
 box-shadow:inset 0 1px 0 rgba(255,255,255,.7);pointer-events:none}
@media(max-width:820px){.hero-bg{display:none}}

/* ==== HOTBOX PREMIUM ==== */
.hotbox{background:linear-gradient(135deg,#0d2a1d 0%,#123a2c 52%,#0b1f18 100%);
 border:0;border-radius:20px;padding:24px 24px 28px;margin:30px 0;position:relative;overflow:hidden;
 box-shadow:0 20px 46px rgba(8,28,18,.30)}
.hotbox::before{content:"";position:absolute;top:-45%;right:-8%;width:440px;height:440px;
 background:radial-gradient(circle,rgba(255,90,60,.22),transparent 62%);pointer-events:none}
.hotbox::after{content:"";position:absolute;bottom:-50%;left:-6%;width:380px;height:380px;
 background:radial-gradient(circle,rgba(46,230,160,.14),transparent 62%);pointer-events:none}
.hotbox>*{position:relative;z-index:1}
.hotbox .sec-tit{color:#fff;margin:0 0 18px}
.hotbox .sec-tit i{background:linear-gradient(135deg,#ff7a45,#ff5a3c);
 box-shadow:0 8px 20px rgba(255,90,60,.5)}
.hotbox .sec-tit i svg{stroke:#fff}
.hotbox .sec-tit em{background:rgba(255,255,255,.12);border:0;color:#ffd9cc;font-weight:800}
.hotbox .card{box-shadow:0 14px 30px rgba(0,0,0,.28)}
.hotbox .card:hover{box-shadow:0 22px 46px rgba(0,0,0,.4)}

/* ==== SEC-HEAD + HOTBOX B ==== */
.sec-head{display:flex;align-items:center;gap:13px;padding-bottom:14px;margin:40px 0 20px;
 border-bottom:1px solid var(--line)}
.sec-head .ico{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;
 justify-content:center;flex:none;background:var(--ac)}
.sec-head .ico svg{width:21px;height:21px;stroke:#06231a;fill:none;stroke-width:1.8;
 stroke-linecap:round;stroke-linejoin:round}
.sec-head h2{font-family:"Sora",Inter,sans-serif;font-size:19px;font-weight:800;letter-spacing:-.02em;
 margin:0;line-height:1.15;color:var(--tx)}
.sec-head p{margin:2px 0 0;font-size:13px;color:var(--tx3)}
.sec-head .rt{margin-left:auto;font-size:12.5px;font-weight:600;color:var(--tx2);
 background:var(--pane);border:1px solid var(--line);border-radius:20px;padding:5px 13px;white-space:nowrap}

/* hotbox = Opção B (branco + barra laranja) */
.hotbox{background:#fff;border:1px solid var(--line);border-left:5px solid var(--preco);
 border-radius:16px;padding:6px 24px 26px;margin:34px 0;
 box-shadow:0 8px 26px rgba(20,30,60,.06)}
.hotbox::before,.hotbox::after{display:none!important}
.hotbox .sec-head{border-bottom-color:var(--line)}
.hotbox .sec-head .ico{background:var(--preco);box-shadow:0 6px 16px rgba(255,90,60,.35)}
.hotbox .sec-head .ico svg{stroke:#fff}
.hotbox .sec-head .rt{background:#fef2f2;border-color:#fbd5d0;color:#c5221f;font-weight:800}
.hotbox .card{box-shadow:0 1px 3px rgba(20,25,40,.06)}

/* ==== SEC-HEAD DEGRADE ==== */
/* cabecalhos das secoes: verde da marca em degrade */
.sec-head{border-bottom:2px solid;border-image:linear-gradient(90deg,var(--ac),rgba(46,230,160,0)) 1}
.sec-head .ico{background:linear-gradient(135deg,var(--ac) 0%,#0f8f66 100%);
 box-shadow:0 6px 16px rgba(18,169,122,.32)}
.sec-head .ico svg{stroke:#06231a}

/* hotbox = Opcao B com fundo laranja claro */
.hotbox{background:#fff7ed;border:1px solid #fbdcc4;border-left:5px solid var(--preco)}
.hotbox .sec-head{border-image:linear-gradient(90deg,#ff9a6b,rgba(255,154,107,0)) 1}
.hotbox .sec-head .ico{background:linear-gradient(135deg,#ff7a45,#ff5a3c);
 box-shadow:0 6px 16px rgba(255,90,60,.35)}
.hotbox .sec-head .ico svg{stroke:#fff}
.hotbox .sec-head h2{color:#7c2d12}
.hotbox .sec-head p{color:#b06a3c}
.hotbox .sec-head .rt{background:#fff;border-color:#fbd5c0;color:#c5221f}

/* ==== ALINHAMENTO ==== */
/* primeiro bloco da coluna de conteudo alinha com o topo da sidebar */
#destaques{margin-top:0}
#destaques>*:first-child{margin-top:0}
.layout>div>*:first-child{margin-top:0}
/* titulo do hotbox centralizado, sem espaco extra em cima */
.hotbox{padding:22px 24px 26px;margin-top:0}
.hotbox .sec-head{margin:0 0 18px}


/* ===== PAGINA DE PRODUTO (remodelada) ===== */
.box-head{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:18px}
.box-head h2{margin:0}
.periodos{margin-left:auto;display:flex;gap:6px;flex-wrap:wrap}
.periodos button{background:#fff;border:1px solid var(--line2);color:var(--tx2);border-radius:20px;
  padding:6px 14px;font-size:12.5px;font-weight:700;cursor:pointer;transition:.15s;font-family:inherit}
.periodos button:hover{border-color:var(--ac);color:var(--tx)}
.periodos button.on{background:var(--ac);color:#06231a;border-color:var(--ac)}
.grafico-wrap{position:relative;height:320px;margin-bottom:4px}
.sem-grafico{padding:34px 18px;text-align:center;color:var(--tx3);font-size:14px;
  background:#fafbfc;border:1px dashed var(--line2);border-radius:12px}
.insights{list-style:none;padding:0;margin:6px 0 0;display:flex;flex-direction:column;gap:12px}
.insights li{display:flex;align-items:flex-start;gap:11px;font-size:14.5px;color:var(--tx2);line-height:1.45}
.insights li::before{content:"";width:10px;height:10px;border-radius:50%;margin-top:5px;flex:none;background:#9aa0a6}
.insights li.verde::before{background:#137333}
.insights li.vermelho::before{background:#d93025}
.insights li.azul::before{background:#1a56c4}
.insights li.cinza::before{background:#9aa0a6}
.semelhantes{margin-top:8px}
.sec-h2{font-family:'Sora',sans-serif;font-size:20px;font-weight:800;color:var(--tx);
  margin:44px 0 20px;padding-bottom:12px;position:relative}
.sec-h2::after{content:"";position:absolute;left:0;bottom:0;width:120px;height:3px;border-radius:3px;
  background:linear-gradient(90deg,var(--ac),rgba(46,230,160,0))}
.semelhantes-grid{grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}



/* ===== UX v2: selos, CTA telegram, voltar-ao-topo ===== */
.flag{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:800;
  padding:3px 9px;border-radius:20px;margin-top:7px;width:fit-content;letter-spacing:.01em}
.flag-menor{background:#e7f6ee;color:#137333}
.flag-menor::before{content:"";width:6px;height:6px;border-radius:50%;background:#25a05f}
.flag-caiu{background:#fff1ec;color:#c5340f}
.flag-caiu::before{content:"↓";font-weight:900;font-size:12px}

.cta-tg{max-width:1660px;margin:40px auto 4px;padding:0 22px}
.cta-tg-in{background:linear-gradient(120deg,var(--barra),#0c2a20);border-radius:22px;
  padding:34px 30px;display:flex;align-items:center;gap:26px;flex-wrap:wrap;justify-content:center;
  box-shadow:0 14px 40px rgba(18,58,44,.22)}
.cta-tg-in .tg-txt{flex:1;min-width:260px}
.cta-tg-in h3{font-family:'Sora',sans-serif;color:#fff;font-size:23px;font-weight:800;
  letter-spacing:-.02em;line-height:1.2}
.cta-tg-in p{color:rgba(255,255,255,.72);font-size:14.5px;margin-top:7px;line-height:1.5}
.cta-tg-in .tg-btn{background:var(--ac);color:#06231a;font-weight:800;font-size:15px;
  padding:15px 26px;border-radius:30px;display:inline-flex;align-items:center;gap:9px;
  white-space:nowrap;box-shadow:0 6px 18px rgba(46,230,160,.4);transition:.15s}
.cta-tg-in .tg-btn:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(46,230,160,.5)}
@media(max-width:640px){.cta-tg-in{padding:26px 20px;text-align:center}
  .cta-tg-in .tg-txt{text-align:center}.cta-tg-in h3{font-size:20px}}

#topo{position:fixed;right:20px;bottom:20px;width:46px;height:46px;border-radius:50%;
  background:var(--tx);border:0;cursor:pointer;display:flex;align-items:center;justify-content:center;
  opacity:0;pointer-events:none;transform:translateY(10px);transition:.2s;z-index:60;
  box-shadow:0 6px 18px rgba(0,0,0,.22)}
#topo.on{opacity:1;pointer-events:auto;transform:none}
#topo svg{width:20px;height:20px;stroke:#fff;stroke-width:2.6;fill:none;stroke-linecap:round;stroke-linejoin:round}



/* ===== UX v3: animacao de filtro + z-index da busca ===== */
.busca-wrap{z-index:50}
.card.saindo{opacity:0;transform:scale(.955) translateY(4px);pointer-events:none;
  transition:opacity .2s ease, transform .2s ease}



/* ===== UX v3.1: reforco z-index da busca sobre abas/chips ===== */
.hero .busca-wrap{position:relative;z-index:80}
.hero .ac{z-index:90}
.hero .lojas,.hero .faixas,.hero .herostats{position:relative;z-index:1}



/* ===== UX v3.2: hero nao corta o dropdown (fotos seguem clipadas no .hero-bg) ===== */
.hero{overflow:visible}



/* ===== icones: Pix preenchido em verde ===== */
.benef.pix{color:#0e8a5f}
.benef.pix .mi{fill:currentColor;stroke:none}

/* ============ Refinamento visual + responsivo ============ */
.lg{display:inline-flex;align-items:center;line-height:1;white-space:nowrap}
.lg .lga{display:none}
/* botoes de periodo do grafico */
.periodos{display:flex;gap:6px;flex-wrap:wrap}
.periodos button{background:var(--pane);border:1px solid var(--line2);color:var(--tx2);
 border-radius:20px;padding:5px 13px;font-size:12.5px;font-weight:600;cursor:pointer;transition:.15s}
.periodos button:hover{border-color:var(--ac);color:var(--ac)}
.periodos button.on{background:var(--ac);color:#fff;border-color:var(--ac);box-shadow:0 3px 10px rgba(46,230,160,.25)}
.grafico-wrap{position:relative;height:300px;margin-top:8px}
.box-head{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:6px}

/* --- Tablet --- */
@media(max-width:820px){ .grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:13px} }

/* --- Celular --- */
@media(max-width:640px){
 .grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
 .card{border-radius:13px}
 .card .foto{height:120px;padding:10px}
 .card .txt{padding:9px 10px 12px}
 .card .tit{font-size:11.5px;min-height:42px;line-height:1.34;font-weight:500}
 .card .por{font-size:16px}
 .card .de{font-size:10.5px}
 .card .cat{font-size:9.5px}
 .spark{height:26px;margin:5px 0 3px}
 .selo{top:7px!important;left:7px!important;font-size:10px!important;padding:2px 6px!important;border-radius:6px!important}
 .lojatag{top:7px!important;right:7px!important}
 .lg{font-size:9px;padding:2px 6px;border-radius:5px}
 .lg .lgt{display:none}.lg .lga{display:inline}
 .card.hot::after{font-size:8.5px;letter-spacing:.03em;padding:3px 0}
 .economia{font-size:9.5px;padding:2px 6px}
 .flag{font-size:9.5px;padding:2px 6px}
 .termo{font-size:10px;padding:2px 7px}
 .grafico-wrap{height:230px}
 .periodos{gap:5px}
 .periodos button{padding:5px 10px;font-size:11.5px}
 .fatos{grid-template-columns:repeat(2,1fr);gap:10px}
 .prod h1{font-size:19px}
 .preco-atual{font-size:30px}
}
/* --- Celular pequeno: manter 2 colunas (nunca 1 card gigante) --- */
@media(max-width:400px){
 .grid{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:9px}
 .card .foto{height:106px;padding:8px}
 .card .tit{font-size:11px;min-height:40px}
 .card .por{font-size:15px}
 .card .txt{padding:8px 9px 11px}
}

"""

# grafico do historico no tema claro (fundo claro)
GRAF_COR = "#15803d"
GRAF_MIN = "#d93025"
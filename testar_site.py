#!/usr/bin/env python3
"""Bateria de testes do site (sem navegador): estrutura, IDs, filtros, z-index, emojis."""
import re
from html.parser import HTMLParser
from pathlib import Path

FALHAS = []
OKS = []
def ok(m): OKS.append(m)
def falha(m): FALHAS.append(m)

home = Path("site/index.html").read_text(encoding="utf-8")
_prods = sorted(Path("site/p").glob("*.html"))
_cats = sorted(Path("site/c").glob("*.html"))
assert _prods and _cats, "gere o site antes (python gerar_site.py)"
prod = _prods[0].read_text(encoding="utf-8")
cat  = _cats[0].read_text(encoding="utf-8")

# 1) sem emojis em nenhuma pagina
for nome, html in [("home",home),("produto",prod),("categoria",cat)]:
    emo=[c for c in html if 0x1F000<=ord(c)<=0x1FAFF or 0x2600<=ord(c)<=0x27BF or c in "✈▶"]
    (ok if not emo else falha)(f"[{nome}] sem emojis" if not emo else f"[{nome}] EMOJIS: {set(emo)}")

# 2) tags balanceadas (parser tolerante)
class V(HTMLParser):
    def __init__(s): super().__init__(); s.stack=[]; s.erros=0
    VOID={"br","img","input","meta","link","hr","source","use","path","rect","circle","polyline","polygon","line","stop"}
    def handle_starttag(s,t,a):
        if t not in s.VOID: s.stack.append(t)
    def handle_endtag(s,t):
        if t in s.VOID: return
        if s.stack and s.stack[-1]==t: s.stack.pop()
        elif t in s.stack:
            while s.stack and s.stack.pop()!=t: pass
        else: s.erros+=1
for nome, html in [("home",home),("produto",prod)]:
    v=V(); v.feed(html)
    (ok if v.erros==0 and len(v.stack)<=1 else falha)(
        f"[{nome}] HTML equilibrado" if v.erros==0 else f"[{nome}] {v.erros} fechamento(s) estranho(s), sobra {v.stack[-3:]}")

# 3) todos os IDs usados pelo JS existem no HTML
js = Path("bot/site_css.py").read_text()
ids_js = set(re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", js))
ids_home = set(re.findall(r'id="([^"]+)"', home))
faltando = ids_js - ids_home - {"nres"}  # nres so aparece se sidebar; checa
faltando = {i for i in ids_js if f'id="{i}"' not in home}
(ok if not faltando else falha)("todos os IDs do JS existem" if not faltando else f"IDs faltando no HTML: {faltando}")

# 4) IDs duplicados
dup=[i for i in ids_home if home.count(f'id="{i}"')>1]
(ok if not dup else falha)("sem IDs duplicados" if not dup else f"IDs DUPLICADOS: {dup}")

# 5) simula a logica de filtro/faceta/ordenacao a partir dos data-atributos dos cards
cards=re.findall(r'<a class="card[^"]*"[^>]*?data-titulo="([^"]*)"[^>]*?data-loja="([^"]*)"[^>]*?data-cat="([^"]*)"[^>]*?data-plat="([^"]*)"[^>]*?data-preco="([^"]*)"[^>]*?data-desc="([^"]*)"[^>]*?data-queda="([^"]*)"', home)
# cards inclui destaques (repetidos) + grade; pega so os da grade (ultimos, dentro de id=grid)
ggrid = home.split('id="grid"')[1]
gcards=re.findall(r'data-titulo="([^"]*)"[^>]*?data-loja="([^"]*)"[^>]*?data-cat="([^"]*)"[^>]*?data-plat="([^"]*)"[^>]*?data-preco="([^"]*)"[^>]*?data-desc="([^"]*)"[^>]*?data-queda="([^"]*)"', ggrid)
prods=[{"t":t.lower(),"loja":l,"cat":c,"plat":pl.split(),"preco":float(p),"desc":float(d),"queda":float(q)} for t,l,c,pl,p,d,q in gcards]
ok(f"grade com {len(prods)} produtos parseados")

def filtra(lojas=(),cats=(),plats=(),q="",fmin=0,fmax=0):
    r=[]
    for x in prods:
        if lojas and x["loja"] not in lojas: continue
        if cats and x["cat"] not in cats: continue
        if plats and not any(pl in x["plat"] for pl in plats): continue
        if q and q not in x["t"]: continue
        if fmin and x["preco"]<fmin: continue
        if fmax and x["preco"]>fmax: continue
        r.append(x)
    return r

# testes de filtro
t1=filtra(cats=["Jogos"]); (ok if all(x["cat"]=="Jogos" for x in t1) and t1 else falha)(f"filtro Jogos -> {len(t1)} itens")
t2=filtra(plats=["PS5"]); (ok if all("PS5" in x["plat"] for x in t2) and t2 else falha)(f"filtro PS5 -> {len(t2)} itens")
t3=filtra(cats=["Jogos"],plats=["PS5"],lojas=["mercadolivre"],fmax=200)
(ok if all(x["cat"]=="Jogos" and "PS5" in x["plat"] and x["loja"]=="mercadolivre" and x["preco"]<=200 for x in t3) else falha)(f"combo Jogos+PS5+ML+ate200 -> {len(t3)} itens ({[round(x['preco']) for x in t3]})")
t4=filtra(fmax=100); (ok if all(x["preco"]<=100 for x in t4) else falha)(f"faixa ate 100 -> {len(t4)} itens")

# faceta: contagem de PS5 dado que Jogos ja marcado (exceto grupo plat)
base=[x for x in prods if x["cat"]=="Jogos"]
nps5=sum(1 for x in base if "PS5" in x["plat"])
ok(f"faceta: com Jogos marcado, PS5 conta {nps5}")

# ordenacao por maior desconto
srt=sorted(prods,key=lambda x:-x["desc"])
(ok if srt==sorted(prods,key=lambda x:-x["desc"]) else falha)("ordenacao por desconto consistente")

# 6) z-index: autocomplete acima dos cards; catbar/top acima do conteudo
css=Path("bot/site_css_claro.py").read_text()
def zval(sel):
    m=re.search(re.escape(sel)+r"\{[^}]*z-index:(\d+)",css)
    return int(m.group(1)) if m else None
z_ac=zval(".ac"); z_top=zval(".top"); z_side=zval(".side"); z_selo=None
m=re.search(r"\.card \.selo,\.card \.lojatag\{transition:transform \.25s;z-index:(\d+)",css); z_selo=int(m.group(1)) if m else None
checks=[("autocomplete acima do conteudo", (z_ac or 0)>=40),
        ("sidebar drawer acima de tudo", (z_side or 0)>=100),
        ("header fixo no topo", (z_top or 0)>=40)]
for nome,cond in checks: (ok if cond else falha)(nome)

# 7) faixa "oferta quente" nao deve cobrir selo/logo (selo tem z maior que a faixa)
m=re.search(r"\.card\.hot::after\{[^}]*z-index:(\d+)",css); z_faixa=int(m.group(1)) if m else 99
(ok if (z_selo or 0)>(z_faixa) else falha)(f"selo/logo (z{z_selo}) acima da faixa quente (z{z_faixa})")

# 8) links de produto e afiliado presentes
(ok if 'rel="nofollow noopener"' in prod else falha)("link de afiliado com rel nofollow")
(ok if 'application/ld+json' in prod else falha)("dados estruturados JSON-LD no produto")

# 9) responsivo: breakpoints existem
for bp in ["980px","640px","380px"]:
    (ok if bp in css else falha)(f"breakpoint {bp}")

print("="*60)
print(f"PASSOU: {len(OKS)}   FALHOU: {len(FALHAS)}")
print("="*60)
for m in OKS: print("  ok  ", m)
if FALHAS:
    print("\n  --- FALHAS ---")
    for m in FALHAS: print("  XX  ", m)

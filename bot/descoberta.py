"""Descoberta automatica de ofertas no Mercado Livre.

Abre as paginas de ofertas com o navegador real, coleta os cards de produto,
filtra pelos seus criterios e cadastra os novos no catalogo - sem voce colar link.
"""
import re
import unicodedata

from bot import config, database, reader, categorias


# ---------- extracao de texto do card ----------
_RE_PRECO = re.compile(r"R\$\s*([\d\.]+(?:,\d{2})?)")
_RE_OFF = re.compile(r"(\d{1,2})\s*%\s*OFF", re.IGNORECASE)


def _num(s):
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


def parse_card(texto):
    """Do texto do card tira (preco, preco_de, desconto%). Ignora valores de parcela."""
    texto = texto or ""
    # valores que sao parcela (ex.: "12x R$ 324,50") devem ser descartados
    parcelas = {_num(v) for v in re.findall(r"\d{1,2}\s*x\s*(?:de\s*)?R\$\s*([\d\.]+(?:,\d{2})?)",
                                            texto, re.IGNORECASE)}
    valores = [_num(p) for p in _RE_PRECO.findall(texto)]
    valores = [v for v in valores if v and v not in parcelas]

    desconto = None
    m = _RE_OFF.search(texto)
    if m:
        desconto = int(m.group(1))

    preco = preco_de = None
    if len(valores) >= 2:
        a, b = valores[0], valores[1]
        preco_de, preco = (a, b) if a > b else (b, a)
    elif valores:
        preco = valores[0]

    if desconto is None and preco and preco_de and preco_de > preco:
        desconto = round((preco_de - preco) / preco_de * 100)
    return preco, preco_de, desconto


JS_COLETAR = """
() => {
  const vistos = new Set();
  const out = [];
  const lixo = /^(mais vendido|oferta do dia|oferta imperd|patrocinado|frete gr|chegar|novo|usado|\\d+%|\\d+$)/i;
  document.querySelectorAll('a[href*="MLB"]').forEach(a => {
    const href = (a.href || '').split('#')[0];
    const m = href.match(/MLB-?\\d{6,}/);
    if (!m) return;
    const id = m[0].replace('-', '');
    if (vistos.has(id)) return;
    const card = a.closest('li, article, div.poly-card, div.andes-card, div.ui-search-result') || a.parentElement;
    if (!card) return;
    const texto = (card.innerText || '').slice(0, 500);
    if (!/R\\$/.test(texto)) return;

    // titulo: atributo title > texto do link > heading do card > 1a linha util
    let titulo = (a.getAttribute('title') || '').trim();
    if (!titulo || lixo.test(titulo)) titulo = (a.innerText || '').trim();
    if (!titulo || lixo.test(titulo)) {
      const h = card.querySelector('h2, h3, .poly-component__title, .ui-search-item__title');
      titulo = h ? (h.innerText || '').trim() : '';
    }
    if (!titulo || lixo.test(titulo)) {
      const linhas = texto.split('\\n').map(s => s.trim())
        .filter(s => s.length > 12 && !lixo.test(s) && !/^R\\$/.test(s));
      titulo = linhas[0] || '';
    }
    if (!titulo || titulo.length < 8) return;
    vistos.add(id);
    out.push({id: id, href: href, titulo: titulo, texto: texto});
  });
  return out;
}
"""


def urls_de_busca():
    """Monta as URLs de busca do ML a partir dos termos do seu nicho."""
    return [f"https://lista.mercadolivre.com.br/{t}" for t in config.DESC_TERMOS]


def coletar(urls=None, scrolls=4, headless=True):
    """Visita as paginas de busca/ofertas e devolve os produtos encontrados."""
    urls = urls or urls_de_busca()
    achados = {}
    with reader.browser(headless=headless) as ctx:
        page = ctx.new_page()
        for url in urls:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)
                for _ in range(scrolls):
                    page.mouse.wheel(0, 2200)
                    page.wait_for_timeout(1200)
                itens = page.evaluate(JS_COLETAR)
            except Exception as e:
                print(f"[erro] {url}: {e}")
                continue
            for it in itens:
                preco, preco_de, desconto = parse_card(it["texto"])
                if not preco:
                    continue
                titulo = (it.get("titulo") or "").strip()[:140]
                achados.setdefault(it["id"], {
                    "id": it["id"], "url": it["href"], "titulo": titulo,
                    "preco": preco, "preco_de": preco_de, "desconto": desconto or 0,
                })
    return list(achados.values())


def _chave_titulo(titulo):
    """Chave para detectar o MESMO produto anunciado por vendedores diferentes."""
    t = unicodedata.normalize("NFKD", (titulo or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    palavras = [p for p in t.split() if len(p) > 2][:6]
    return " ".join(palavras)


def _titulo_ok(titulo):
    t = (titulo or "").lower()
    if len(t) < 8:
        return False
    if any(b in t for b in config.DESC_PALAVRAS_BLOQUEIO):
        return False
    if config.DESC_PALAVRAS_OK and not any(w in t for w in config.DESC_PALAVRAS_OK):
        return False
    return True


def filtrar(itens):
    """Filtra por nicho/desconto/preco, classifica em categorias, aplica cota e ordena."""
    aprovados = []
    for i in itens:
        if not _titulo_ok(i.get("titulo")):
            continue
        if i["desconto"] < config.DESC_MIN_DESCONTO:
            continue
        if config.DESC_PRECO_MIN and i["preco"] < config.DESC_PRECO_MIN:
            continue
        if config.DESC_PRECO_MAX and i["preco"] > config.DESC_PRECO_MAX:
            continue
        cat = categorias.classificar(i["titulo"])
        i["categoria"] = cat["nome"]
        i["cat_prio"] = cat.get("prioridade", 10)
        i["cat_cota"] = cat.get("cota", 999)
        aprovados.append(i)

    # ordena por prioridade da categoria e, dentro dela, por maior desconto
    aprovados.sort(key=lambda x: (-x["cat_prio"], -x["desconto"]))

    # remove duplicatas (mesmo produto, vendedores diferentes) - fica o melhor
    vistos, unicos = set(), []
    for i in aprovados:
        k = _chave_titulo(i["titulo"])
        if k in vistos:
            continue
        vistos.add(k)
        unicos.append(i)
    aprovados = unicos

    # aplica a cota de cada categoria (evita uma categoria dominar tudo)
    usados, out = {}, []
    for i in aprovados:
        c = i["categoria"]
        if usados.get(c, 0) >= i["cat_cota"]:
            continue
        usados[c] = usados.get(c, 0) + 1
        out.append(i)
        if len(out) >= config.DESC_MAX_PRODUTOS:
            break
    return out


def cadastrar(itens, verbose=True):
    """Cadastra no catalogo os que ainda nao existem (com link de afiliado gerado)."""
    from bot.link_ml import montar
    database.init_db()
    existentes = {p["id"] for p in database.get_products(only_active=False)}
    novos = 0
    for i in itens:
        if i["id"] in existentes:
            continue
        try:
            afiliado = montar(i["url"])
        except Exception:
            afiliado = i["url"]
        database.add_product({
            "id": i["id"], "title": i["titulo"], "permalink": i["url"],
            "thumbnail": None, "affiliate_url": afiliado,
            "coupon_code": None, "coupon_note": None,
            "categoria": i.get("categoria"),
            "loja": "mercadolivre",
        })
        database.record_price(i["id"], i["preco"], i.get("preco_de"))
        novos += 1
        if verbose:
            print(f"  + [{i.get('categoria','?'):<16}] {i['desconto']:>3}% R$ {i['preco']:<9} {i['titulo'][:46]}")
    return novos


def rodar(cadastrar_novos=False, headless=True, verbose=True):
    if getattr(config, "MODO_LEVE", False):
        print("MODO_LEVE ativo: a descoberta automatica esta desligada.")
        print("  Ela varre dezenas de paginas e foi o que provocou o bloqueio do ML.")
        print("  Para usar mesmo assim: MODO_LEVE=nao no .env")
        return 0
    brutos = coletar(headless=headless)
    itens = filtrar(brutos)
    if verbose:
        print(f"Coletados: {len(brutos)} | Aprovados nos filtros: {len(itens)}")
    if not cadastrar_novos:
        for i in itens:
            print(f"  [{i.get('categoria','?'):<16}] {i['desconto']:>3}%  R$ {i['preco']:<9} {i['titulo'][:52]}")
        return 0
    n = cadastrar(itens, verbose)
    if verbose:
        print(f"Novos cadastrados: {n}")
    return n

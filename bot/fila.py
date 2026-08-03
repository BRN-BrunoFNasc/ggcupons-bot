"""Fila de postagem: niveis, rodizio entre categorias e furo de fila por queda de preco."""
from datetime import datetime, timezone

from bot import config, database, analytics, cupons, categorias


def _agora():
    return datetime.now(timezone.utc)


def _parse(ts):
    try:
        t = datetime.fromisoformat(ts)
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _minutos_desde(ts):
    t = _parse(ts) if ts else None
    return None if not t else (_agora() - t).total_seconds() / 60.0


# ---------------- classificacao ----------------
def classificar(product, db_path=None):
    hist = database.get_price_history(product["id"], db_path)
    if not hist:
        return None
    summary = analytics.summarize(hist, windows=config.HISTORY_WINDOWS)
    ultimo = hist[-1]
    preco = ultimo["price"]
    de = ultimo.get("original_price")
    desconto = round((de - preco) / de * 100) if (de and preco and de > preco) else 0

    if summary and summary.get("enough_history") and summary.get("is_lowest_window", 0) >= 30:
        tier = "MENOR_PRECO"
    elif cupons.melhor_cupom(product["id"], preco, db_path) or product.get("coupon_code"):
        tier = "CUPOM"
    elif desconto >= config.DESCONTO_FORTE_PCT:
        tier = "DESCONTO_FORTE"
    elif desconto > 0:
        tier = "DESCONTO_LEVE"
    else:
        tier = "SEM_DESCONTO"

    cat_nome = product.get("categoria") or categorias.classificar(product.get("title"))["nome"]
    prioridade = config.PRIORIDADES[tier] * 100 + categorias.prioridade(cat_nome)
    cd = product.get("cooldown_min") or categorias.cooldown(cat_nome) or config.COOLDOWNS[tier]
    return {"tier": tier, "categoria": cat_nome, "prioridade": prioridade,
            "cooldown_min": cd, "desconto": desconto, "preco": preco, "summary": summary}


def esta_liberado(product, cooldown_min):
    m = _minutos_desde(product.get("last_posted_at"))
    if m is None:
        return True, 10 ** 6
    return m >= cooldown_min, m - cooldown_min


def _urgencia(product):
    """Produto com queda de preco recente fura a fila (respeitando um gap minimo)."""
    m = _minutos_desde(product.get("urgente_desde"))
    if m is None or m > config.URGENTE_JANELA_MIN:
        return False, 0
    gap = _minutos_desde(product.get("last_posted_at"))
    if gap is not None and gap < config.URGENTE_GAP_MIN:
        return False, 0
    return True, float(product.get("urgente_queda") or 0)


def listar_status(db_path=None):
    out = []
    for p in database.get_products(only_active=True, db_path=db_path):
        c = classificar(p, db_path)
        if not c:
            continue
        liberado, atraso = esta_liberado(p, c["cooldown_min"])
        urgente, queda = _urgencia(p)
        out.append({**p, **c, "liberado": liberado, "atraso_min": atraso,
                    "urgente": urgente, "queda": queda})
    return out


# ---------------- rodizio de categorias ----------------
def sequencia_rodizio():
    """Monta a ordem de rodizio intercalando as categorias pelos seus 'slots'.

    Ex.: Jogos(3), Consoles(2), Controles(2), Monitores(1) ->
         Jogos, Consoles, Controles, Monitores, Jogos, Consoles, Controles, Jogos
    """
    cats = sorted(categorias.carregar(), key=lambda c: -c.get("prioridade", 0))
    restantes = {c["nome"]: int(c.get("slots", 1)) for c in cats}
    ordem = []
    while any(v > 0 for v in restantes.values()):
        for c in cats:
            n = c["nome"]
            if restantes[n] > 0:
                ordem.append(n)
                restantes[n] -= 1
    return ordem or ["Outros"]


def _minutos_desde_post(product):
    m = _minutos_desde(product.get("last_posted_at"))
    return 10 ** 9 if m is None else m


def pontuacao(x):
    """Pontua a oferta priorizando VARIEDADE (cobrir o catálogo inteiro) e, dentro
    disso, as melhores ofertas.

    A base é o tempo desde o último post (nunca postado -> vai primeiro), o que faz
    o bot percorrer TODOS os produtos antes de repetir. Ofertas boas (desconto,
    menor preço histórico, cupom, mais procurados) ganham um 'adiantamento' em
    minutos virtuais, então aparecem mais cedo — sem monopolizar a fila."""
    # base: ha quanto tempo nao e postado (nunca postado = topo)
    s = float(min(_minutos_desde_post(x), 100000))
    # adiantamento por qualidade (em "minutos virtuais")
    s += (x.get("desconto") or 0) * 6.0          # 30% de desconto ~ +180 min
    summ = x.get("summary") or {}
    if summ.get("enough_history"):
        janela = summ.get("is_lowest_window", 0) or 0
        if janela >= 90:
            s += 400
        elif janela >= 30:
            s += 250
        elif janela >= 7:
            s += 120
    if x.get("tier") == "CUPOM":
        s += 120
    s += (x.get("trend_score") or 0) * 2.0
    if x.get("mais_vendido"):
        s += 60
    return s


def proximo(db_path=None):
    """Sempre posta a MELHOR oferta disponível (não trava por cooldown longo).

    1) Queda de preço detectada agora fura a fila.
    2) Melhor pontuação entre os que NÃO foram postados no anti-repetição.
    3) Se todos já saíram há pouco, posta o que faz mais tempo (garante 1 post/rodada).
    """
    itens = listar_status(db_path)
    if not itens:
        return None

    # 1) urgentes (queda de preço recém-detectada)
    urgentes = [x for x in itens if x["urgente"]]
    if urgentes:
        urgentes.sort(key=lambda x: (x["queda"], pontuacao(x)), reverse=True)
        esc = urgentes[0]
        esc["motivo"] = f"QUEDA DE {esc['queda']:.0f}%"
        return esc

    antirep = getattr(config, "ANTIREPEAT_MIN", 360)
    frescos = [x for x in itens if _minutos_desde_post(x) >= antirep]

    if frescos:
        frescos.sort(key=lambda x: (pontuacao(x), _minutos_desde_post(x)), reverse=True)
        esc = frescos[0]
        esc["motivo"] = f"melhor oferta (score {pontuacao(esc):.0f})"
        return esc

    # todos postados dentro do anti-repetição -> posta o mais antigo (cicla o catálogo)
    itens.sort(key=lambda x: (_minutos_desde_post(x), pontuacao(x)), reverse=True)
    esc = itens[0]
    esc["motivo"] = "ciclo (catálogo todo postado recentemente)"
    return esc

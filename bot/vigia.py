"""Vigia de precos: varre as paginas de busca e detecta quedas quase em tempo real.

Uma varredura carrega dezenas de produtos por pagina, entao da pra monitorar o
catalogo inteiro em poucos minutos - bem mais rapido que abrir produto por produto.
Quando detecta queda relevante, marca o produto como URGENTE e ele fura a fila.
"""
from bot import config, database, descoberta


def _ultimo_preco(pid):
    hist = database.get_price_history(pid)
    return hist[-1]["price"] if hist else None


def varrer(cadastrar_novos=True, verbose=True):
    """Retorna a lista de quedas detectadas.

    Se o ML bloquear (verificacao), interrompe a varredura em vez de insistir —
    insistir sob bloqueio so agrava e prolonga a punicao.
    """
    database.init_db()
    if getattr(config, "MODO_LEVE", False):
        quedas = _varrer_catalogo(cadastrar_novos=cadastrar_novos, verbose=verbose)
        quedas += _varrer_amazon(verbose=verbose)
        return quedas
    try:
        brutos = descoberta.coletar()
    except Exception as e:
        if verbose:
            print(f"[vigia] erro na coleta: {e}")
        return []
    if not brutos:
        if verbose:
            print("[vigia] nada coletado — possivel bloqueio do ML. "
                  "Rode 'python aquecer.py' e aumente VIGIA_INTERVALO_MIN.")
        return []
    catalogo = {p["id"]: p for p in database.get_products(only_active=True)}
    quedas = []
    atualizados = 0

    for i in brutos:
        pid = i["id"]
        if pid not in catalogo:
            continue
        novo = i.get("preco")
        if not novo:
            continue
        anterior = _ultimo_preco(pid)

        # so grava quando o preco MUDA (mantem o historico limpo)
        if anterior is None or abs(novo - anterior) >= 0.01:
            database.record_price(pid, novo, i.get("preco_de"))
            atualizados += 1

        if anterior and novo < anterior:
            queda = (anterior - novo) / anterior * 100
            if queda >= config.QUEDA_URGENTE_PCT:
                database.marcar_urgente(pid, queda)
                quedas.append({"id": pid, "titulo": catalogo[pid].get("title"),
                               "de": anterior, "para": novo, "queda": round(queda, 1)})
                if verbose:
                    print(f"  🚨 QUEDA {queda:.0f}%  R$ {anterior} -> R$ {novo}  "
                          f"{(catalogo[pid].get('title') or '')[:44]}")

    novos = 0
    if cadastrar_novos:
        novos = descoberta.cadastrar(descoberta.filtrar(brutos), verbose=verbose)

    if verbose:
        print(f"[vigia] {len(brutos)} lidos | {atualizados} precos atualizados | "
              f"{len(quedas)} queda(s) | {novos} novo(s) produto(s)")
    return quedas


def _varrer_amazon(verbose=True):
    """Le os precos dos produtos Amazon via Scrape.do (proxy residencial).

    Trava de custo: so re-le um produto se passou AMZ_INTERVALO_H desde a ultima
    leitura (cada leitura gasta tokens da API). Sem SCRAPER_TOKEN, nao faz nada."""
    import os
    from datetime import datetime, timezone
    if not os.environ.get("SCRAPER_TOKEN", "").strip():
        return []
    from bot.lojas.amazon import Amazon

    intervalo_h = float(getattr(config, "AMZ_INTERVALO_H", 24) or 24)
    amz = Amazon()
    agora = datetime.now(timezone.utc)
    produtos = [p for p in database.get_products(only_active=True)
                if (p.get("loja") == "amazon")]
    quedas, lidos, pulados = [], 0, 0

    for p in produtos:
        pid = p["id"]
        hist = database.get_price_history(pid)
        anterior = hist[-1]["price"] if hist else None
        # throttle por tempo desde a ultima leitura
        if hist:
            try:
                t = datetime.fromisoformat(hist[-1].get("recorded_at"))
                if t.tzinfo is None:
                    t = t.replace(tzinfo=timezone.utc)
                if (agora - t).total_seconds() / 3600.0 < intervalo_h:
                    pulados += 1
                    continue
            except Exception:
                pass
        link = p.get("permalink") or p.get("affiliate_url") or pid
        r = amz.ler_produto(link)
        lidos += 1
        if r.get("error"):
            if verbose:
                print(f"  [amazon] {pid}: {r['error']}")
            continue
        novo = r.get("price")
        if novo and (anterior is None or abs(novo - anterior) >= 0.01):
            database.record_price(pid, novo, r.get("original_price"))
        database.atualizar_dados(pid, {
            "title": r.get("title") or None,
            "thumbnail": r.get("thumbnail") or None,
            "parcelas": r.get("parcelas") or "",
            "frete": 1 if r.get("frete") else 0,
            "pagamento": r.get("pagamento") or "",
            "coupon_code": r.get("coupon_code") or "",
            "coupon_note": r.get("coupon_note") or "",
        })
        if anterior and novo and novo < anterior:
            queda = (anterior - novo) / anterior * 100
            if queda >= config.QUEDA_URGENTE_PCT:
                database.marcar_urgente(pid, queda)
                quedas.append({"id": pid, "de": anterior, "para": novo,
                               "queda": round(queda, 1)})
        if verbose:
            print(f"  [amazon] {pid}: R$ {novo}")

    if verbose and (lidos or pulados):
        print(f"[vigia] amazon: {lidos} lido(s) via Scrape.do, {pulados} pulado(s) "
              f"(dentro de {intervalo_h:.0f}h)")
    return quedas


def _varrer_catalogo(cadastrar_novos=True, verbose=True):
    """Modo leve: le a LISTA de afiliado (1 unica pagina), cadastra novos e atualiza tudo."""
    from bot import lista_ml, categorias
    from bot.link_ml import montar
    url = getattr(config, "ML_LISTA_URL", "")
    if not url:
        if verbose:
            print("[vigia] defina ML_LISTA_URL no .env (link da sua lista de afiliado)")
        return []

    itens = lista_ml.ler(url, verbose=verbose)
    if not itens:
        return []

    catalogo = {p["id"]: p for p in database.get_products(only_active=False)}
    quedas = []
    novos = 0
    for i in itens:
        pid, novo = i["id"], i["por"]
        if pid not in catalogo:
            if not cadastrar_novos:
                continue
            cat = categorias.classificar(i.get("titulo"))["nome"]
            try:
                link = montar(i["href"])
            except Exception:
                link = i.get("href")
            database.add_product({
                "id": pid, "title": i.get("titulo"), "permalink": i.get("href"),
                "thumbnail": i.get("img"), "affiliate_url": link,
                "coupon_code": None, "coupon_note": None,
                "categoria": cat, "loja": "mercadolivre",
            })
            if i.get("mais"):
                _c = database._conn()
                _c.execute("UPDATE products SET mais_vendido=1 WHERE id=?", (pid,))
                _c.commit(); _c.close()
            catalogo[pid] = {"title": i.get("titulo")}
            novos += 1
            if verbose:
                print(f"  NOVO  {pid}  {(i.get('titulo') or '')[:44]}")
        anterior = _ultimo_preco(pid)
        if anterior is None or abs(novo - anterior) >= 0.01:
            database.record_price(pid, novo, i.get("de"))
        database.atualizar_dados(pid, {
            "parcelas": i.get("parcelas"),
            "frete": 1 if i.get("frete") else 0,
            "pagamento": "no PIX" if i.get("pix") else None,
            "thumbnail": i.get("img") or None,
            "title": i.get("titulo") or None,
        })
        if anterior and novo < anterior:
            queda = (anterior - novo) / anterior * 100
            if queda >= config.QUEDA_URGENTE_PCT:
                database.marcar_urgente(pid, queda)
                quedas.append({"id": pid, "de": anterior, "para": novo,
                               "queda": round(queda, 1)})
                if verbose:
                    print(f"  QUEDA {queda:.0f}%  R$ {anterior} -> R$ {novo}  "
                          f"{(catalogo[pid].get('title') or '')[:40]}")

    if verbose:
        print(f"[vigia] {len(itens)} conferidos | {novos} novo(s) | {len(quedas)} queda(s)")
    return quedas

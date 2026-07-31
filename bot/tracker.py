"""Orquestracao: grava precos diariamente e posta as boas ofertas (card + texto)."""
from pathlib import Path
from bot import config, database, analytics, message, imagem
from bot import reader
from bot import lojas

CARDS_DIR = Path(__file__).resolve().parent.parent / "data" / "cards"


def record_all_prices(verbose=True):
    database.init_db()
    produtos = database.get_products(only_active=True)
    urls = [p.get("permalink") or p.get("affiliate_url") for p in produtos]
    lidos = reader.read_many(urls)
    for p, u in zip(produtos, urls):
        item = lidos.get(u, {})
        if not item or item.get("price") is None:
            if verbose:
                print(f"[skip] {p['id']} sem preco ({item.get('error')})")
            continue
        database.record_price(p["id"], item["price"], item.get("original_price"))
        if verbose:
            print(f"[ok] {p['id']} R$ {item['price']}")


def _dados_do_banco(product):
    """Monta os dados do produto a partir do que a lista ja trouxe (sem acessar o ML)."""
    hist = database.get_price_history(product["id"])
    if not hist:
        return None
    ultimo = hist[-1]
    return {
        "title": product.get("title"),
        "price": ultimo["price"],
        "original_price": ultimo.get("original_price"),
        "parcelas": product.get("parcelas"),
        "frete": bool(product.get("frete")),
        "pagamento": product.get("pagamento"),
        "thumbnail": product.get("thumbnail"),
        "permalink": product.get("permalink"),
    }


def _preparar(product, verbose=True, ver=False, online=False):
    """Monta info + card + texto do produto.

    Por padrao usa os dados ja gravados pela sincronizacao da lista — assim
    publicar NAO acessa o Mercado Livre (que bloqueia paginas de produto).
    Use online=True para forcar a leitura ao vivo.
    """
    def _p(msg):
        if verbose:
            print(f"   {msg}", flush=True)

    rd = None
    if online:
        alvo = product.get("permalink") or product.get("affiliate_url")
        _p("lendo a pagina do produto (10-20s)...")
        try:
            if ver:
                from bot import reader as _rd
                rd = _rd.read_product(alvo, headless=False)
            else:
                loja = (lojas.por_nome(product.get("loja")) or lojas.detectar(alvo)
                        or lojas.por_nome("mercadolivre"))
                rd = loja.ler_produto(alvo)
        except Exception as e:
            _p(f"erro ao ler: {e}")
            rd = None
        if rd and rd.get("price") is not None:
            database.record_price(product["id"], rd["price"], rd.get("original_price"))
        else:
            _p(f"leitura online falhou ({(rd or {}).get('error','?')}) — usando dados salvos")
            rd = None

    if rd is None:
        rd = _dados_do_banco(product)
        if not rd:
            _p("sem preco salvo. Rode: python sincronizar_lista.py \"URL\" --aplicar")
            return None
        _p(f"preco (da lista): R$ {rd['price']}")

    hist = database.get_price_history(product["id"])
    summary = analytics.summarize(hist, windows=config.HISTORY_WINDOWS)
    info = message.build_info(product, rd, summary)
    cap = message.caption(info)

    _p("gerando o card...")
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    card_path = str(CARDS_DIR / f"{product['id']}.png")
    try:
        imagem.gerar_card({"title": info["title"], "thumbnail": info["thumbnail"]},
                          info, card_path, logo_path=config.LOGO_PATH or None)
    except Exception as e:
        _p(f"erro ao gerar o card: {e}")
        return None
    _p(f"card salvo em {card_path}")
    return {"info": info, "caption": cap, "card": card_path, "summary": summary}


def find_and_post_deals(dry_run=True, verbose=True):
    database.init_db()
    posted = 0
    for p in database.get_products(only_active=True):
        pack = _preparar(p)
        if not pack:
            if verbose:
                print(f"[sem-preco] {p['id']}")
            continue
        if not analytics.is_good_deal(pack["summary"], config.MIN_DISCOUNT_PERCENT):
            if verbose:
                print(f"[nao-oferta] {p['id']}")
            continue
        if dry_run:
            print("=" * 44)
            print("CARD:", pack["card"])
            print(pack["caption"])
        else:
            from bot import telegram_bot
            telegram_bot.send_photo_file(pack["card"], pack["caption"])
            posted += 1
            if verbose:
                print(f"[postado] {p['id']}")
    return posted


def postar_um(product_id, dry_run=False, ver=False):
    """Posta um produto especifico pelo ID (util para testar)."""
    database.init_db()
    produtos = database.get_products(only_active=True)
    if not produtos:
        print("Catalogo vazio. Cadastre produtos antes:")
        print('   python sincronizar_lista.py "https://meli.la/SUA_LISTA" --aplicar')
        return

    alvo = next((p for p in produtos if p["id"] == product_id), None)
    if not alvo:
        print(f"Produto {product_id} nao esta no catalogo.")
        print(f"Produtos disponiveis ({len(produtos)}):")
        for p in produtos[:10]:
            print(f"   {p['id']}  {(p.get('title') or '')[:48]}")
        return

    print(f"Produto: {(alvo.get('title') or '')[:56]}", flush=True)
    pack = _preparar(alvo, ver=ver)
    if not pack:
        print("Nao consegui preparar a publicacao.")
        print("Dica: rode com --ver para ver o navegador e onde travou.")
        return
    if dry_run:
        print("\n--- PREVIA ---")
        print(pack["caption"])
        return
    print("   enviando ao Telegram...", flush=True)
    from bot import telegram_bot
    telegram_bot.send_photo_file(pack["card"], pack["caption"])
    print(f"[ok] publicado: {product_id}")


def montar_caption(info, tier=None):
    return message.caption(info, tier)

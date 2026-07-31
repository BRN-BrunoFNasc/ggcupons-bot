"""Leitor de preco do Mercado Livre via navegador real (Playwright).

O ML bloqueia API e HTML simples. Um navegador de verdade abre a pagina e le o
preco. Tenta varios formatos de URL (catalogo /p/ e anuncio de vendedor) e le
onde aparecer preco. Requer:
    pip install playwright
    playwright install chromium
"""
import os
import re
from contextlib import contextmanager

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")


def extrair_id(texto):
    m = re.search(r"MLB[-]?(\d+)", texto or "", re.IGNORECASE)
    return "MLB" + m.group(1) if m else None


def _to_float(fraction, cents):
    fraction = re.sub(r"\D", "", fraction or "")
    cents = re.sub(r"\D", "", cents or "") or "0"
    if not fraction:
        return None
    return float(f"{fraction}.{cents}")


def _pasta_perfil():
    """Pasta do perfil do navegador.

    NAO pode ficar dentro da pasta do projeto quando ela esta em area protegida
    (ex.: AppData\\Local\\Packages do Windows) — o Chromium nao consegue gravar la.
    Por isso usamos a area de dados do usuario.
    """
    from bot import config
    custom = getattr(config, "PERFIL_NAVEGADOR", "")
    if custom:
        return custom
    base = (os.environ.get("LOCALAPPDATA")          # Windows
            or os.environ.get("XDG_DATA_HOME")      # Linux
            or os.path.expanduser("~/.local/share"))
    if not base or not os.path.isdir(base):
        import tempfile
        base = tempfile.gettempdir()
    return os.path.join(base, "GarimpoGamerBot", "perfil")


PERFIL_DIR = _pasta_perfil()


def _aceitar_cookies(page):
    """Fecha o banner de cookies (uma vez por perfil ja resolve)."""
    for txt in ["Aceitar cookies", "Aceitar todos", "Entendi", "Aceitar"]:
        try:
            b = page.get_by_role("button", name=re.compile(txt, re.I))
            if b.count():
                b.first.click(timeout=2500)
                page.wait_for_timeout(700)
                return True
        except Exception:
            continue
    return False


def bloqueado(page):
    """True se a pagina caiu na verificacao/login do ML."""
    u = page.url or ""
    return ("account-verification" in u) or ("/gz/" in u) or ("/login" in u)


@contextmanager
def browser(headless=True, perfil=True):
    """Navegador com perfil persistente: cookies e historico sobrevivem,
    o que reduz muito a chance de cair na verificacao do ML."""
    from playwright.sync_api import sync_playwright

    args = ["--disable-blink-features=AutomationControlled",
            "--no-sandbox", "--disable-dev-shm-usage",
            "--disable-features=IsolateOrigins,site-per-process"]
    init = ("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
            "Object.defineProperty(navigator,'languages',{get:()=>['pt-BR','pt']});"
            "Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3,4,5]});"
            "window.chrome={runtime:{}};")

    with sync_playwright() as p:
        if perfil:
            try:
                os.makedirs(PERFIL_DIR, exist_ok=True)
                teste = os.path.join(PERFIL_DIR, ".escrita")
                with open(teste, "w") as f:
                    f.write("ok")
                os.remove(teste)
            except Exception as e:
                print(f"[aviso] nao consigo usar o perfil em {PERFIL_DIR}: {e}")
                print("        seguindo sem perfil persistente "
                      "(defina PERFIL_NAVEGADOR no .env para outra pasta)")
                perfil = False
        if perfil:
            ctx = p.chromium.launch_persistent_context(
                PERFIL_DIR, headless=headless, args=args,
                user_agent=UA, locale="pt-BR",
                viewport={"width": 1366, "height": 900},
                timezone_id="America/Sao_Paulo",
                extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9"},
            )
            ctx.add_init_script(init)
            try:
                yield ctx
            finally:
                ctx.close()
        else:
            b = p.chromium.launch(headless=headless, args=args)
            ctx = b.new_context(
                user_agent=UA, locale="pt-BR",
                viewport={"width": 1366, "height": 900},
                timezone_id="America/Sao_Paulo",
                extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9"},
            )
            ctx.add_init_script(init)
            try:
                yield ctx
            finally:
                b.close()


def _extract_fields(page):
    """Le titulo/preco/imagem da pagina ATUAL. Retorna dict ou None se nao houver preco."""
    if not page.locator(".andes-money-amount__fraction").count():
        return None

    def txt(sel):
        loc = page.locator(sel)
        return loc.first.text_content().strip() if loc.count() else None

    title = txt("h1.ui-pdp-title") or txt("h1")

    price = None
    for cont in [".ui-pdp-price__second-line", ".ui-pdp-price", "[data-testid='price']"]:
        c = page.locator(cont)
        if c.count():
            frac = c.locator(".andes-money-amount__fraction")
            if frac.count():
                cents = c.locator(".andes-money-amount__cents")
                price = _to_float(frac.first.text_content(),
                                  cents.first.text_content() if cents.count() else "0")
                if price:
                    break
    if price is None:
        frac = page.locator(".andes-money-amount__fraction").first
        price = _to_float(frac.text_content(), "0")
    if price is None:
        return None

    original = None
    orig = page.locator("s .andes-money-amount__fraction, .andes-money-amount--previous .andes-money-amount__fraction")
    if orig.count():
        original = _to_float(orig.first.text_content(), "0")

    image = None
    og = page.locator("meta[property='og:image']")
    if og.count():
        image = og.first.get_attribute("content")
    if not image:
        img = page.locator(".ui-pdp-gallery__figure img, figure img")
        if img.count():
            image = img.first.get_attribute("src")

    # parcelas e frete (best-effort, pelo texto da pagina)
    parcelas = None
    frete = False
    pagamento = None
    pix_off = None
    try:
        conteudo = page.content()
        mpar = re.search(r"em\s*(\d{1,2})x\s*(?:de\s*)?R\$\s*([\d\.,]+)\s*sem juros", conteudo, re.IGNORECASE)
        if not mpar:
            mpar = re.search(r"(\d{1,2})x\s*R\$\s*([\d\.,]+)\s*sem juros", conteudo, re.IGNORECASE)
        if mpar:
            parcelas = f"{mpar.group(1)}x R$ {mpar.group(2)} sem juros"
        frete = bool(re.search(r"[Ff]rete gr\u00e1tis|[Cc]hegar\u00e1 gr\u00e1tis|[Gg]r\u00e1tis amanh\u00e3", conteudo))
        # forma de pagamento do desconto (ex.: "20% OFF no Pix ou Saldo no Mercado Pago")
        mpix = re.search(r"(\d{1,2})%\s*OFF\s*no\s*Pix", conteudo, re.IGNORECASE)
        if mpix:
            pagamento = "no PIX"
            pix_off = int(mpix.group(1))
        elif re.search(r"no\s*Pix", conteudo, re.IGNORECASE):
            pagamento = "no PIX"
            pix_off = None
        else:
            pagamento = None
            pix_off = None
    except Exception:
        pass

    return {
        "id": extrair_id(page.url),
        "title": title,
        "price": price,
        "original_price": original,
        "parcelas": parcelas,
        "frete": frete,
        "pagamento": pagamento,
        "pix_off": pix_off,
        "permalink": page.url.split("#")[0],
        "thumbnail": image,
    }


def _open_and_read(page, url, wait=25000):
    """Abre a URL, espera o preco e tenta ler. Retorna dict ou None."""
    from bot import ritmo
    if not ritmo.pode_acessar():
        return {"limite": True}
    ritmo.aguardar()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
    except Exception:
        return None
    _aceitar_cookies(page)
    # se caiu em verificacao, espera e tenta uma vez mais
    if bloqueado(page):
        page.wait_for_timeout(3000)
        try:
            page.reload(wait_until="domcontentloaded", timeout=60000)
            _aceitar_cookies(page)
        except Exception:
            pass
    if bloqueado(page):
        return {"bloqueado": True}
    try:
        page.wait_for_selector(".andes-money-amount__fraction", timeout=wait)
    except Exception:
        return None
    return _extract_fields(page)


def _candidatos(item_id):
    num = re.sub(r"\D", "", item_id)
    return [
        f"https://www.mercadolivre.com.br/p/{item_id}",
        f"https://produto.mercadolivre.com.br/MLB-{num}",
        f"https://articulo.mercadolibre.com.br/MLB-{num}",
    ]


def read_product(entrada, headless=True):
    """Recebe link (inclusive meli.la) ou ID. Devolve dados do produto com preco."""
    with browser(headless=headless) as ctx:
        page = ctx.new_page()

        # 1) abre o que foi informado
        if str(entrada).startswith("http"):
            try:
                page.goto(entrada, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(2000)
            except Exception:
                pass
            eh_vitrine = "/social/" in page.url
            # so le direto se NAO for a vitrine (pagina de produto de verdade)
            if not eh_vitrine:
                direto = _extract_fields(page)
                if direto and direto.get("price") is not None:
                    return direto
            item_id = extrair_id(page.url)
            if not item_id:
                html = page.content()
                m = (re.search(r"/p/(MLB\d+)", html) or re.search(r"wid=(MLB\d+)", html))
                item_id = m.group(1) if m else None
            if eh_vitrine and not item_id:
                return {"error": "esse link e a sua vitrine de afiliado, nao um produto. "
                                 "Use o link normal do produto (barra de endereco) para ler o preco.",
                        "final_url": page.url}
        else:
            item_id = extrair_id(entrada)

        if not item_id:
            return {"error": "nao achei o codigo MLB", "final_url": page.url}

        # 2) tenta os formatos de URL conhecidos
        houve_bloqueio = False
        for url in _candidatos(item_id):
            data = _open_and_read(page, url)
            if data and data.get("limite"):
                return {"error": "limite diario de paginas atingido "
                                 "(ajuste LIMITE_DIARIO_PAGINAS no .env)",
                        "id": item_id}
            if data and data.get("bloqueado"):
                houve_bloqueio = True
                continue
            if data and data.get("price") is not None:
                data["id"] = data.get("id") or item_id
                return data

        if houve_bloqueio or bloqueado(page):
            return {"error": "BLOQUEADO: o Mercado Livre pediu verificacao/login. "
                             "Rode 'python aquecer.py' e reduza a frequencia.",
                    "bloqueado": True, "id": item_id, "final_url": page.url}
        return {"error": "preco nao apareceu (layout novo?)",
                "id": item_id, "final_url": page.url}


def read_many(urls, headless=True):
    """Le varios reaproveitando o mesmo navegador."""
    out = {}
    with browser(headless=headless) as ctx:
        page = ctx.new_page()
        for u in urls:
            data = None
            # tenta a URL salva direto; se falhar, tenta os candidatos pelo id
            if str(u).startswith("http"):
                data = _open_and_read(page, u)
            if not (data and data.get("price") is not None):
                item_id = extrair_id(u)
                if item_id:
                    for cand in _candidatos(item_id):
                        data = _open_and_read(page, cand)
                        if data and data.get("price") is not None:
                            break
            out[u] = data or {"error": "sem preco"}
    return out

"""Amazon Brasil.

Link de afiliado: trivial - basta acrescentar ?tag=SEU-TAG-20 na URL do produto.
Dados do produto: a PA-API foi descontinuada (mai/2026) e substituida pela
Creators API, que exige vendas qualificadas recentes para manter o acesso.
Enquanto nao houver acesso a API, a leitura e feita pelo navegador.
"""
import re

from bot import config
from bot.lojas.base import Loja


class Amazon(Loja):
    nome = "amazon"
    rotulo = "Amazon"
    ativa = bool(getattr(config, "AMZ_TAG", ""))
    metodo = "navegador"  # muda para "api" quando a Creators API estiver liberada

    RE_ASIN = re.compile(r"/(?:dp|gp/product|product)/([A-Z0-9]{10})", re.I)

    def detecta(self, s):
        s = str(s or "")
        return ("amazon.com" in s or "amzn.to" in s or "link.amazon" in s
                or bool(self.RE_ASIN.search(s)))

    def extrair_id(self, s):
        m = self.RE_ASIN.search(str(s or ""))
        if m:
            return m.group(1).upper()
        m = re.fullmatch(r"[A-Z0-9]{10}", str(s or "").strip(), re.I)
        return m.group(0).upper() if m else None

    def url_produto(self, asin):
        return f"https://www.amazon.com.br/dp/{asin}"

    def link_afiliado(self, url_ou_id):
        tag = getattr(config, "AMZ_TAG", "")
        asin = self.extrair_id(url_ou_id)
        base = self.url_produto(asin) if asin else str(url_ou_id)
        if not tag:
            return base
        sep = "&" if "?" in base else "?"
        return f"{base}{sep}tag={tag}"

    # Leitor best-effort pela pagina do produto (navegador). A Amazon costuma
    # bloquear IPs de datacenter (CAPTCHA), entao isso pode falhar na nuvem.
    _JS = """
    () => {
      const parseBRL = (s) => {
        if (!s) return null;
        const m = String(s).replace(/[^0-9,\\.]/g, '');
        const n = parseFloat(m.replace(/\\./g, '').replace(',', '.'));
        return isNaN(n) ? null : n;
      };
      const q = (sel) => document.querySelector(sel);
      const t = q('#productTitle');
      const meta = (p) => { const e = document.querySelector('meta[property="'+p+'"]'); return e ? e.content : ''; };
      const title = t ? t.textContent.trim() : (meta('og:title') || '');
      let por = null;
      const pe = q('#corePriceDisplay_desktop_feature_div .a-price .a-offscreen') ||
                 q('#corePrice_feature_div .a-price .a-offscreen') ||
                 q('.a-price .a-offscreen');
      if (pe) por = parseBRL(pe.textContent);
      let de = null;
      const dee = q('.basisPrice .a-offscreen') ||
                  q('span[data-a-strike="true"] .a-offscreen') ||
                  q('.a-text-price .a-offscreen');
      if (dee) de = parseBRL(dee.textContent);
      const im = q('#landingImage') || q('#imgBlkFront');
      const img = im ? (im.getAttribute('src') || '') : (meta('og:image') || '');
      const body = (document.body ? document.body.innerText : '').slice(0, 600);
      const bloqueado = /Digite os caracteres|Robot Check|not a robot|Insira os caracteres|automated access|Sorry, we just need/i.test(body)
                        || !!document.querySelector('form[action*="validateCaptcha"]');
      return { title, por, de, img, bloqueado, amostra: body.slice(0, 160) };
    }
    """

    def ler_produto(self, url_ou_id):
        """Le o produto. Se houver SCRAPER_TOKEN (Scrape.do), usa a API
        (proxy residencial + geo BR, que fura o bloqueio da Amazon).
        Senao, tenta o navegador local (bloqueia na nuvem)."""
        import os
        asin = self.extrair_id(url_ou_id)
        alvo = self.url_produto(asin) if asin else str(url_ou_id)
        token = os.environ.get("SCRAPER_TOKEN", "").strip()
        if token:
            return self._ler_scrapedo(alvo, asin, token)
        return self._ler_navegador(alvo, asin)

    def _ler_scrapedo(self, alvo, asin, token):
        import urllib.parse
        import requests
        # sem render: o preco vem no HTML do servidor da Amazon, entao nao precisa
        # renderizar JS -> gasta menos tokens da Scrape.do.
        api = ("https://api.scrape.do/?token=" + token
               + "&url=" + urllib.parse.quote_plus(alvo)
               + "&super=true&geoCode=br")
        try:
            r = requests.get(api, timeout=90)
        except Exception as e:
            return {"error": f"erro na API scrape.do: {e}"}
        if r.status_code != 200:
            return {"error": f"scrape.do devolveu status {r.status_code}",
                    "amostra": (r.text or "")[:160]}
        return self._parse_html(r.text, alvo, asin)

    @staticmethod
    def _brl(s):
        import re as _re
        if not s:
            return None
        m = _re.sub(r"[^0-9,.]", "", str(s))
        if not m:
            return None
        try:
            return float(m.replace(".", "").replace(",", "."))
        except Exception:
            return None

    def _parse_html(self, html, alvo, asin):
        try:
            from bs4 import BeautifulSoup
        except Exception:
            return {"error": "falta a dependencia beautifulsoup4"}
        soup = BeautifulSoup(html or "", "html.parser")
        txt = soup.get_text(" ", strip=True)[:600]
        import re as _re
        if _re.search(r"Digite os caracteres|Robot Check|not a robot|Insira os caracteres|"
                      r"automated access|continuar comprando|Sorry, we just need", txt, _re.I):
            return {"error": "bloqueado pela Amazon (CAPTCHA)", "amostra": txt[:160]}

        def sel(*seletores):
            for s in seletores:
                el = soup.select_one(s)
                if el:
                    return el
            return None

        t = sel("#productTitle")
        title = t.get_text(strip=True) if t else None
        if not title:
            og = soup.select_one('meta[property="og:title"]')
            title = og.get("content", "").strip() if og else None

        por = None
        for s in ("#corePriceDisplay_desktop_feature_div .a-price .a-offscreen",
                  "#corePriceDisplay_desktop_feature_div .a-offscreen",
                  "#corePrice_feature_div .a-price .a-offscreen",
                  "#corePrice_feature_div .a-offscreen",
                  "#priceblock_ourprice", "#priceblock_dealprice",
                  ".a-price .a-offscreen"):
            el = soup.select_one(s)
            if el:
                por = self._brl(el.get_text())
                if por:
                    break
        de = None
        for s in (".basisPrice .a-offscreen", 'span[data-a-strike="true"] .a-offscreen',
                  ".a-text-price .a-offscreen"):
            el = soup.select_one(s)
            if el:
                de = self._brl(el.get_text())
                if de:
                    break
        img = None
        im = sel("#landingImage", "#imgBlkFront")
        if im and im.get("src"):
            img = im.get("src")
        if not img:
            og = soup.select_one('meta[property="og:image"]')
            if og and og.get("content"):
                img = og.get("content")

        if not por:
            return {"error": "abriu, mas nao achei o preco", "amostra": txt[:160]}

        # ---- infos extras (texto da pagina) ----
        full = soup.get_text(" ", strip=True)
        # parcelas: "6x de R$ 46,65"
        mp = _re.search(r"(\d{1,2})\s*x\s*(?:de\s*)?R\$\s*([\d.,]+)", full)
        parcelas = f"{mp.group(1)}x R$ {mp.group(2)}" if mp else None
        # a vista / Pix
        pagamento = None
        if _re.search(r"\bno\s*pix\b", full, _re.I) or (
                _re.search(r"[àa]\s*vista", full, _re.I) and _re.search(r"\bpix\b", full, _re.I)):
            pagamento = "no PIX"
        # frete gratis
        frete = bool(_re.search(r"(entrega|frete)\s+gr[áa]tis", full, _re.I))
        # cupom: codigo ("cupom ... : GAMES10") e/ou percentual
        coupon_code = coupon_note = None
        mcode = _re.search(r"cupom[^:\n]{0,40}?:\s*([A-Z0-9]{4,15})", full, _re.I)
        if mcode:
            coupon_code = mcode.group(1).upper()
        mpct = _re.search(r"cupom[^%\n]{0,25}?(\d{1,3})\s*%", full, _re.I) or \
               _re.search(r"(\d{1,3})\s*%[^%\n]{0,15}?cupom", full, _re.I)
        if mpct:
            coupon_note = f"{mpct.group(1)}% de desconto com cupom"

        return {"id": asin, "title": title, "price": por, "original_price": de,
                "thumbnail": img, "permalink": alvo, "loja": "amazon",
                "parcelas": parcelas, "frete": frete, "pagamento": pagamento,
                "coupon_code": coupon_code, "coupon_note": coupon_note}

    def _ler_navegador(self, alvo, asin):
        from bot import reader
        try:
            with reader.browser(headless=True) as ctx:
                page = ctx.pages[0] if ctx.pages else ctx.new_page()
                page.goto(alvo, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(4000)
                try:
                    reader._aceitar_cookies(page)
                except Exception:
                    pass
                page.wait_for_timeout(1500)
                data = page.evaluate(self._JS)
        except Exception as e:
            return {"error": f"erro ao abrir a pagina: {e}"}
        if data.get("bloqueado"):
            return {"error": "bloqueado pela Amazon (CAPTCHA/robot check)",
                    "amostra": data.get("amostra")}
        if not data.get("por"):
            return {"error": "abriu, mas nao achei o preco", "amostra": data.get("amostra")}
        return {"id": asin, "title": data.get("title") or None, "price": data.get("por"),
                "original_price": data.get("de"), "thumbnail": data.get("img") or None,
                "permalink": alvo, "loja": "amazon"}

    def urls_descoberta(self):
        return getattr(config, "AMZ_URLS", [])

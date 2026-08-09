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
        from bot import reader
        asin = self.extrair_id(url_ou_id)
        alvo = self.url_produto(asin) if asin else str(url_ou_id)
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
            return {"error": "abriu, mas nao achei o preco",
                    "amostra": data.get("amostra")}
        return {
            "id": asin,
            "title": data.get("title") or None,
            "price": data.get("por"),
            "original_price": data.get("de"),
            "thumbnail": data.get("img") or None,
            "permalink": alvo,
            "loja": "amazon",
        }

    def urls_descoberta(self):
        return getattr(config, "AMZ_URLS", [])

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
        return "amazon.com" in s or "amzn.to" in s or bool(self.RE_ASIN.search(s))

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

    # leitura e descoberta entram quando ativarmos a loja
    def ler_produto(self, url_ou_id):
        return {"error": "Amazon ainda nao configurada (falta AMZ_TAG e o leitor)"}

    def urls_descoberta(self):
        return getattr(config, "AMZ_URLS", [])

"""Mercado Livre. Sem API utilizavel (bloqueada) -> navegador real (Playwright)."""
import re

from bot import config, reader, descoberta
from bot.lojas.base import Loja


class MercadoLivre(Loja):
    nome = "mercadolivre"
    rotulo = "Mercado Livre"
    ativa = True
    metodo = "navegador"

    def detecta(self, s):
        s = str(s or "")
        return bool(re.search(r"MLB-?\d{6,}", s, re.I)) or "mercadolivre.com" in s or "meli.la" in s

    def extrair_id(self, s):
        return reader.extrair_id(s)

    def ler_produto(self, url_ou_id):
        return reader.read_product(url_ou_id)

    def urls_descoberta(self):
        return descoberta.urls_de_busca()

    def coletar(self):
        return descoberta.coletar()

    def link_afiliado(self, url):
        from bot.link_ml import montar
        try:
            return montar(url)
        except Exception:
            return url

"""AliExpress.

Tem API oficial de afiliados (AliExpress Open Platform): busca de produtos em
promocao, detalhes, cupons e GERACAO DE LINK DE AFILIADO por API. Ou seja: nao
precisa de navegador nem raspagem. Requer app aprovado (AppKey/AppSecret).
"""
import re

from bot import config
from bot.lojas.base import Loja


class AliExpress(Loja):
    nome = "aliexpress"
    rotulo = "AliExpress"
    ativa = bool(getattr(config, "ALI_APP_KEY", ""))
    metodo = "api"

    def detecta(self, s):
        s = str(s or "")
        return "aliexpress.com" in s or "s.click.aliexpress" in s

    def extrair_id(self, s):
        m = re.search(r"/item/(\d{6,})", str(s or ""))
        return m.group(1) if m else None

    def url_produto(self, pid):
        return f"https://pt.aliexpress.com/item/{pid}.html"

    # Estes tres metodos usarao a API oficial quando as chaves existirem:
    #   listPromotionProduct  -> descoberta de ofertas
    #   getPromotionProductDetail -> preco/detalhes
    #   getPromotionLinks     -> link de afiliado
    def ler_produto(self, url_ou_id):
        return {"error": "AliExpress ainda nao configurada (falta ALI_APP_KEY/ALI_APP_SECRET)"}

    def coletar(self):
        return []

    def link_afiliado(self, url_ou_id):
        return str(url_ou_id)

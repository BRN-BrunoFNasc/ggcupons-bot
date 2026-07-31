"""Interface comum das lojas. Cada loja implementa estes metodos.

Assim o resto do sistema (fila, cupons, card, telegram, historico) funciona
igual para Mercado Livre, Amazon, AliExpress ou qualquer loja futura.
"""


class Loja:
    nome = "base"
    rotulo = "Loja"
    ativa = False

    # ---- identificacao ----
    def detecta(self, url_ou_id):
        """True se esta URL/ID pertence a esta loja."""
        raise NotImplementedError

    def extrair_id(self, texto):
        """Devolve o ID do produto nesta loja (ex.: MLB123, B08XYZ, 100500123)."""
        raise NotImplementedError

    # ---- leitura de produto ----
    def ler_produto(self, url_ou_id):
        """Devolve dict: id, title, price, original_price, parcelas, frete,
        pagamento, permalink, thumbnail. Ou {'error': ...}."""
        raise NotImplementedError

    # ---- descoberta de ofertas ----
    def urls_descoberta(self):
        """Paginas de busca/ofertas para varrer."""
        return []

    def coletar(self):
        """Devolve lista de dicts: id, url, titulo, preco, preco_de, desconto."""
        return []

    # ---- afiliado ----
    def link_afiliado(self, url_ou_id):
        """Monta o link que gera comissao."""
        raise NotImplementedError

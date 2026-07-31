"""Registro das lojas suportadas."""
from bot.lojas.mercadolivre import MercadoLivre
from bot.lojas.amazon import Amazon
from bot.lojas.aliexpress import AliExpress

_LOJAS = [MercadoLivre(), Amazon(), AliExpress()]


def todas(so_ativas=True):
    return [l for l in _LOJAS if l.ativa or not so_ativas]


def por_nome(nome):
    for l in _LOJAS:
        if l.nome == (nome or "").lower():
            return l
    return None


def detectar(url_ou_id):
    """Descobre a qual loja pertence uma URL/ID. Devolve a loja ou None."""
    for l in _LOJAS:
        try:
            if l.detecta(url_ou_id):
                return l
        except Exception:
            continue
    return None

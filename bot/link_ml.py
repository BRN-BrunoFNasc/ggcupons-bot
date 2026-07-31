"""Monta o link de afiliado do Mercado Livre conforme a estrategia escolhida."""
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from bot import config


def _com_matt(url):
    w, t = config.ML_MATT_WORD, config.ML_MATT_TOOL
    if not (w and t):
        return url
    u = urlparse(str(url).split("#")[0])
    q = parse_qs(u.query)
    q["matt_word"] = [w]
    q["matt_tool"] = [t]
    return urlunparse(u._replace(query=urlencode(q, doseq=True)))


def montar(url_produto):
    e = (config.ML_LINK_ESTRATEGIA or "matt").lower()
    if e == "lista" and config.ML_LISTA_URL:
        return config.ML_LISTA_URL
    if e == "cru":
        return url_produto
    return _com_matt(url_produto)

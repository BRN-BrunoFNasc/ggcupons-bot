"""Categorias do nicho: prioridade, cota por rodada e descanso.

Edite o arquivo categorias.json na raiz do projeto para mudar as regras.
Quanto maior a prioridade, mais o produto aparece (na descoberta e na fila).
"""
import json
import unicodedata
from pathlib import Path


def _norm(s):
    """minusculas e sem acento - deixa a comparacao imune a 'fisico'/'físico'."""
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))

ARQ = Path(__file__).resolve().parent.parent / "categorias.json"
_cache = None

PADRAO = [{"nome": "Outros", "prioridade": 10, "cota": 999, "cooldown_min": None, "palavras": []}]


def carregar(recarregar=False):
    global _cache
    if _cache is None or recarregar:
        try:
            _cache = json.loads(ARQ.read_text(encoding="utf-8"))
        except Exception:
            _cache = PADRAO
    return _cache


def classificar(titulo):
    _r = _via_conhecimento(titulo)
    _kw = _classificar_kw(titulo)
    # se as palavras-chave nao acharam nada claro, usa o conhecimento de familias
    if _kw.get("nome") == "Outros" and _r:
        for c in carregar():
            if c["nome"] == _r:
                return c
    return _kw


def _via_conhecimento(titulo):
    try:
        from bot import conhecimento
        return conhecimento.categoria(titulo)
    except Exception:
        return None


def _classificar_kw(titulo):
    """Devolve a categoria do produto. Vence a palavra-chave MAIS ESPECIFICA
    (a mais longa que aparecer no titulo); empate desempata pela prioridade."""
    t = _norm(titulo)
    outros = None
    melhor = None   # (tamanho_da_palavra, prioridade, categoria)
    for c in carregar():
        if not c.get("palavras"):
            outros = c
            continue
        # se o titulo tem alguma palavra de bloqueio da categoria, ela nem concorre
        if any(_norm(b) in t for b in c.get("bloqueio", [])):
            continue
        for p in c["palavras"]:
            p = _norm(p)
            if p in t:
                cand = (len(p.strip()), c.get("prioridade", 0), c)
                if not melhor or cand[:2] > melhor[:2]:
                    melhor = cand
    if melhor:
        return melhor[2]
    return outros or PADRAO[0]


def por_nome(nome):
    for c in carregar():
        if c["nome"].lower() == (nome or "").lower():
            return c
    return None


def prioridade(nome):
    c = por_nome(nome)
    return c["prioridade"] if c else 10


def cooldown(nome):
    c = por_nome(nome)
    return (c or {}).get("cooldown_min")

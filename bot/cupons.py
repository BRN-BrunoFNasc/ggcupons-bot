"""Regras de cupom: aplica, valida e escolhe o melhor cupom para um produto."""
from datetime import date

from bot import database


def _vencido(validade):
    if not validade:
        return False
    try:
        return date.fromisoformat(str(validade)[:10]) < date.today()
    except Exception:
        return False


def aplicar(preco, c):
    """Retorna (preco_final, desconto_em_reais) ou (None, 0) se nao se aplica."""
    if preco is None:
        return None, 0
    if _vencido(c.get("validade")):
        return None, 0
    if preco < float(c.get("minimo") or 0):
        return None, 0

    if c["tipo"] == "perc":
        desc = preco * float(c["valor"]) / 100.0
        if c.get("teto"):
            desc = min(desc, float(c["teto"]))
    else:  # fixo
        desc = float(c["valor"])

    final = round(preco - desc, 2)
    if final <= 0:
        return None, 0
    return final, round(desc, 2)


def melhor_cupom(product_id, preco, db_path=None):
    """Entre os cupons validos que servem para este produto, devolve o de maior desconto."""
    melhor = None
    for c in database.get_coupons(db_path):
        escopo = (c.get("escopo") or "GLOBAL").upper()
        if escopo not in ("GLOBAL", str(product_id).upper()):
            continue
        final, desc = aplicar(preco, c)
        if final is None:
            continue
        if not melhor or desc > melhor["desconto"]:
            melhor = {"cupom": c, "final": final, "desconto": desc}
    return melhor


def descrever(c):
    """Texto curto da regra: '10% OFF (máx. R$50, mín. R$500)'."""
    p = []
    p.append(f"{int(c['valor'])}% OFF" if c["tipo"] == "perc" else f"R$ {c['valor']:.0f} OFF")
    det = []
    if c.get("teto"):
        det.append(f"máx. R$ {float(c['teto']):.0f}")
    if c.get("minimo"):
        det.append(f"mín. R$ {float(c['minimo']):.0f}")
    if det:
        p.append("(" + ", ".join(det) + ")")
    return " ".join(p)

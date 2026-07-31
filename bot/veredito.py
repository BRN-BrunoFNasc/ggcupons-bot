"""Termometro de preco e recomendacao de compra, a partir do historico."""
from datetime import datetime, timezone, timedelta
from statistics import median


def _parse(ts):
    try:
        t = datetime.fromisoformat(ts)
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def termometro(hist, summary=None):
    """Classifica o preco atual dentro do historico.

    Retorna dict: nivel, label, cor ('verde'|'amarelo'|'vermelho'|'cinza'), rec (texto).
    """
    if not hist:
        return None
    precos = [h["price"] for h in hist]
    atual = precos[-1]
    minimo, maximo = min(precos), max(precos)
    med = median(precos)
    dias = (summary or {}).get("history_days", 0)

    if len(precos) < 3 or dias < 3:
        return {"nivel": "novo", "label": "Coletando histórico", "cor": "cinza",
                "rec": "Ainda estamos formando o histórico deste preço. "
                       "Acompanhe nos próximos dias para saber se é uma boa compra."}

    if atual <= minimo * 1.005:
        return {"nivel": "otimo", "label": "Menor preço já registrado", "cor": "verde",
                "rec": "Melhor momento para comprar: está no menor preço que já registramos."}

    faixa = (maximo - minimo) or 1
    pos = (atual - minimo) / faixa   # 0 = mínimo histórico, 1 = máximo

    if atual <= med * 0.98 or pos <= 0.25:
        return {"nivel": "bom", "label": "Ótimo preço", "cor": "verde",
                "rec": "Boa hora de comprar: o preço está abaixo da média histórica."}
    if pos <= 0.60:
        return {"nivel": "normal", "label": "Preço normal", "cor": "amarelo",
                "rec": "Preço dentro do normal. Não está caro, mas já esteve um pouco menor."}
    return {"nivel": "alto", "label": "Já esteve mais barato", "cor": "vermelho",
            "rec": "Vale esperar: este produto já esteve bem mais barato recentemente."}


def queda_recente(hist, dias=7):
    """% de queda do maior preco dos ultimos N dias ate o preco atual (0 se nao caiu)."""
    if not hist:
        return 0.0
    corte = datetime.now(timezone.utc) - timedelta(days=dias)
    recentes = []
    for h in hist:
        t = _parse(h["recorded_at"])
        if t and t >= corte:
            recentes.append(h["price"])
    if len(recentes) < 2:
        return 0.0
    hi, atual = max(recentes), hist[-1]["price"]
    return round((hi - atual) / hi * 100, 1) if hi > atual else 0.0

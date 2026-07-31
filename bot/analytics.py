"""Analise do historico de preco: minimo/mediana por janela e deteccao de oferta."""
from datetime import datetime, timezone, timedelta
from statistics import median


def _parse(ts):
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return datetime.now(timezone.utc)


def _prices_in_window(history, days, now=None):
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    out = []
    for h in history:
        t = _parse(h["recorded_at"])
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        if t >= cutoff:
            out.append(h["price"])
    return out


def summarize(history, windows=(30, 60, 90), now=None):
    """Recebe o historico (lista de dicts com price/recorded_at) e resume a oferta.

    Retorna dict com:
      current            -> preco atual (ultimo registrado)
      min_by_window      -> {30: x, 60: y, 90: z}
      median_by_window   -> mediana por janela
      is_lowest_window   -> maior janela em que o preco atual e o menor (ou 0)
      discount_vs_min    -> % de desconto do preco atual vs. menor preco geral anterior
      points             -> quantidade de registros no historico
    """
    if not history:
        return None

    current = history[-1]["price"]
    all_prices = [h["price"] for h in history]
    # quantos dias o historico cobre
    try:
        t0 = _parse(history[0]["recorded_at"]); t1 = _parse(history[-1]["recorded_at"])
        history_days = max(0, (t1 - t0).days)
    except Exception:
        history_days = 0
    prev_prices = all_prices[:-1] or all_prices
    lowest_before = min(prev_prices)

    min_by_window, median_by_window = {}, {}
    for w in windows:
        p = _prices_in_window(history, w, now=now)
        if p:
            min_by_window[w] = min(p)
            median_by_window[w] = round(median(p), 2)

    # Maior janela em que o preco atual empata/e o menor
    is_lowest_window = 0
    for w in sorted(windows):
        if w in min_by_window and current <= min_by_window[w] + 0.001:
            is_lowest_window = w

    discount_vs_min = 0.0
    if lowest_before > 0 and current < lowest_before:
        discount_vs_min = round((lowest_before - current) / lowest_before * 100, 1)

    return {
        "current": current,
        "min_by_window": min_by_window,
        "median_by_window": median_by_window,
        "is_lowest_window": is_lowest_window,
        "discount_vs_min": discount_vs_min,
        "lowest_before": lowest_before,
        "points": len(history),
        "history_days": history_days,
        "enough_history": history_days >= 3 and len(history) >= 3,
    }


def is_good_deal(summary, min_discount_percent=5.0):
    """Regra simples: e oferta se bater o menor preco recente OU cair >= X% vs. minimo anterior."""
    if not summary:
        return False
    if summary["is_lowest_window"] >= 30:
        return True
    return summary["discount_vs_min"] >= min_discount_percent

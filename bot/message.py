"""Constroi o texto (caption HTML) persuasivo e o 'info' usado no card visual."""
import random
from html import escape
from bot import config, cupons


def format_brl(value):
    if value is None:
        return "-"
    s = f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def _hist_line(summary):
    if not summary:
        return None
    if summary.get("enough_history"):
        win = summary.get("is_lowest_window", 0)
        if win >= 30:
            return f"📉 <b>Menor preço dos últimos {win} dias!</b>"
        if summary.get("discount_vs_min", 0) > 0:
            return f"📉 <b>{summary['discount_vs_min']}%</b> abaixo do menor preço recente"
        med = summary.get("median_by_window", {})
        if 90 in med:
            return f"📊 Média (90 dias): {format_brl(med[90])}"
    return "🆕 Começamos a monitorar o histórico deste preço"


def build_info(product, rd, summary):
    rd = rd or {}
    por = rd.get("price")
    de = rd.get("original_price")
    desconto = None
    if de and por and de > por:
        desconto = round((de - por) / de * 100)
    # melhor cupom valido que se aplica a este produto/preco
    mc = cupons.melhor_cupom(product.get("id"), por)
    cupom_code = mc["cupom"]["code"] if mc else product.get("coupon_code")
    cupom_regra = cupons.descrever(mc["cupom"]) if mc else product.get("coupon_note")
    preco_cupom = mc["final"] if mc else None
    desc_cupom = mc["desconto"] if mc else None

    return {
        "id": product.get("id"),
        "preco_cupom": preco_cupom,
        "desconto_cupom": desc_cupom,
        "cupom_regra": cupom_regra,
        "title": rd.get("title") or product.get("title"),
        "por": por,
        "de": de,
        "desconto": desconto,
        "parcelas": rd.get("parcelas"),
        "frete": rd.get("frete"),
        "pagamento": rd.get("pagamento"),   # ex.: "no PIX"
        "cupom": cupom_code,
        "cupom_nota": cupom_regra,
        "link": product.get("affiliate_url") or product.get("permalink"),
        "thumbnail": rd.get("thumbnail") or product.get("thumbnail"),
        "hist_line": _hist_line(summary),
    }


SELOS = {
    "MENOR_PRECO":    ["🔥 <b>MENOR PREÇO DO PERÍODO</b>", "📉 <b>PREÇO MAIS BAIXO ATÉ AGORA</b>",
                        "🚨 <b>MÍNIMA HISTÓRICA</b>"],
    "CUPOM":          ["🎟️ <b>OFERTA COM CUPOM</b>", "🎟️ <b>CUPOM LIBERADO</b>"],
    "DESCONTO_FORTE": ["💥 <b>BAIXOU MUITO</b>", "⚡ <b>QUEDA FORTE DE PREÇO</b>"],
    "DESCONTO_LEVE":  ["🏷️ <b>EM OFERTA</b>", "🏷️ <b>COM DESCONTO</b>"],
    "SEM_DESCONTO":   ["🎮 <b>DESTAQUE DO CANAL</b>", "🔎 <b>GARIMPADO PRA VOCÊ</b>",
                        "⭐ <b>MAIS PROCURADO</b>"],
}


def caption(info, tier=None):
    """Texto HTML que acompanha o card no Telegram."""
    L = []
    if tier and tier in SELOS:
        L.append(random.choice(SELOS[tier]))
    L.append(f"🎮 <b>{escape(info['title'] or '')}</b> 🔥")
    L.append("")
    if info.get("desconto"):
        L.append(f"💥 <b>{info['desconto']}% OFF</b>")

    pag = f" {info['pagamento']}" if info.get("pagamento") else ""
    if info.get("de") and info.get("por") and info["de"] > info["por"]:
        L.append(f"De <s>{format_brl(info['de'])}</s> por <b>{format_brl(info['por'])}</b>{pag}")
    else:
        L.append(f"💰 <b>{format_brl(info.get('por'))}</b>{pag}")

    if info.get("parcelas"):
        L.append(f"💳 ou {escape(info['parcelas'])} no cartão")
    if info.get("frete"):
        L.append("🚚 Frete Grátis")
    if info.get("hist_line"):
        L.append("")
        L.append(info["hist_line"])
    # link para a pagina do produto no site (grafico de historico de preco)
    _site = (getattr(config, "SITE_URL", "") or "").rstrip("/")
    _pid = info.get("id")
    if _site and _pid:
        L.append(f'📈 <a href="{escape(_site)}/p/{escape(str(_pid))}.html">Ver histórico de preço</a>')
    if info.get("cupom"):
        L.append("")
        if info.get("preco_cupom"):
            L.append(f"🎟️ Com o cupom <code>{escape(info['cupom'])}</code>: "
                     f"<b>{format_brl(info['preco_cupom'])}</b>")
            if info.get("cupom_nota"):
                L.append(f"<i>{escape(info['cupom_nota'])}</i>")
        else:
            nota = f" ({escape(info['cupom_nota'])})" if info.get("cupom_nota") else ""
            L.append(f"🎟️ CUPOM: <code>{escape(info['cupom'])}</code>{nota}")
    L.append("")
    _lk = (info.get("link") or "").strip()
    if _lk:
        L.append(f'🛒 <a href="{escape(_lk)}">👉 PEGAR OFERTA</a>')
    else:
        L.append("🛒 <b>👉 PEGAR OFERTA</b>")
    L.append("")
    # "Siga o Garimpo" leva para a aba Redes do site (links.html), nao direto pro Telegram
    _siteb = (getattr(config, "SITE_URL", "") or "").rstrip("/")
    destino = (f"{_siteb}/links.html" if _siteb else "") or getattr(config, "CHANNEL_INVITE", "")
    marca = escape(config.BRAND_NAME.title())
    if destino:
        L.append(f'📣 <a href="{escape(destino)}">Siga o {marca}</a> '
                 f"— ofertas de games e tech todo dia")
    else:
        L.append(f"📣 Siga o {marca} — ofertas de games e tech todo dia")
    return "\n".join(L)

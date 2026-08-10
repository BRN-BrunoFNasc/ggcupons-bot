#!/usr/bin/env python3
"""Gera o site estatico (ofertas + historico + busca + filtro por loja).

    python gerar_site.py

Produz 'site/' com home (busca, abas por loja, destaques), pagina de cada
produto com grafico, e pagina de links. Estatico: hospedagem gratuita.
"""
import html
from datetime import datetime, timezone
from pathlib import Path

from bot import database, analytics, config
from bot.grafico import svg, spark
from bot.veredito import termometro, queda_recente
import json
from bot import site_css, site_css_claro

TEMA = (config.SITE_TEMA or "claro").lower()
if TEMA != "claro":
    print("AVISO: o tema 'escuro' esta desatualizado (sem os componentes novos). Usando 'claro'.")
    TEMA = "claro"
_MOD = site_css_claro
CSS = _MOD.CSS
JS = site_css.JS  # o mesmo JS serve para os dois temas
GRAF = (getattr(_MOD, "GRAF_COR", None), getattr(_MOD, "GRAF_MIN", None))

SAIDA = Path("site")

LOJAS = {
    "mercadolivre": ("Mercado Livre", "#ffe600"),
    "amazon":       ("Amazon", "#ff9900"),
    "aliexpress":   ("AliExpress", "#e62e04"),
}

def logo_loja(loja):
    # .lgt = nome cheio (desktop) | .lga = abreviacao (mobile, evita cobrir o selo de desconto)
    if loja == "mercadolivre":
        return ('<span class="lg lg-mercadolivre">'
                '<span class="lgt">Mercado Livre</span><span class="lga">ML</span></span>')
    if loja == "amazon":
        return ('<span class="lg lg-amazon">'
                '<span class="lgt">amaz<i>o</i>n</span><span class="lga">a<i>m</i>z</span></span>')
    if loja == "aliexpress":
        return ('<span class="lg lg-aliexpress">'
                '<span class="lgt">AliExpress</span><span class="lga">Ali</span></span>')
    nome, _ = LOJAS.get(loja, ("Loja", "#888"))
    return '<span class="lg" style="background:#eee;color:#333">' + e(nome) + '</span>'


def termo_html(t, grande=False):
    if not t:
        return ""
    cls = "termo termo-g" if grande else "termo"
    return '<span class="' + cls + ' t-' + t["cor"] + '">' + e(t["label"]) + '</span>'



def plataformas(titulo):
    t = " " + (titulo or "").lower() + " "
    out = []
    if "ps5" in t or "playstation 5" in t: out.append("PS5")
    if "ps4" in t or "playstation 4" in t: out.append("PS4")
    if "xbox" in t: out.append("Xbox")
    if "switch" in t or "nintendo" in t: out.append("Switch")
    if " pc " in t or "notebook" in t or "computador" in t: out.append("PC")
    return out


def prod_index(dados, base=""):
    idx = [{"t": d["p"].get("title") or "", "p": brl(d["por"]),
            "u": f"{base}p/{d['p']['id']}.html", "img": d["p"].get("thumbnail") or ""}
           for d in dados]
    return "<script>window.PROD=" + json.dumps(idx, ensure_ascii=False) + "</script>"


def cat_slug(c):
    import re, unicodedata
    s = unicodedata.normalize("NFKD", (c or "outros").lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "outros"


def brl(v):
    if v is None:
        return "—"
    return "R$ " + f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def e(s):
    return html.escape(str(s or ""))


def _cor(c):
    return "#%02x%02x%02x" % tuple(c)


_ICONES = {
    'jogos': '<svg width="20" height="20" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.6"/><circle cx="12" cy="12" r="2.4"/><path d="M12 3.6a8.5 8.5 0 0 1 6 2.5"/></svg>',
    'games': '<svg width="20" height="20" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.6"/><circle cx="12" cy="12" r="2.4"/><path d="M12 3.6a8.5 8.5 0 0 1 6 2.5"/></svg>',
    'consoles': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.6" y="2.5" width="6.6" height="19" rx="2"/><line x1="5.9" y1="5" x2="5.9" y2="9"/><line x1="4.2" y1="17.4" x2="7.6" y2="17.4"/><line x1="4.2" y1="19.2" x2="7.6" y2="19.2"/><path d="M11 13.2h8.4a2.5 2.5 0 0 1 2.45 3.02l-.28 1.3a2 2 0 0 1-3.62.62l-.5-.86h-3.1l-.5.86a2 2 0 0 1-3.62-.62l-.28-1.3A2.5 2.5 0 0 1 11 13.2z"/><path d="M13.3 15.4h1.7M14.15 14.55v1.7"/><circle cx="18.4" cy="15.1" r=".55" fill="currentColor" stroke="none"/><circle cx="19.7" cy="16.2" r=".55" fill="currentColor" stroke="none"/></svg>',
    'console': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.6" y="2.5" width="6.6" height="19" rx="2"/><line x1="5.9" y1="5" x2="5.9" y2="9"/><line x1="4.2" y1="17.4" x2="7.6" y2="17.4"/><line x1="4.2" y1="19.2" x2="7.6" y2="19.2"/><path d="M11 13.2h8.4a2.5 2.5 0 0 1 2.45 3.02l-.28 1.3a2 2 0 0 1-3.62.62l-.5-.86h-3.1l-.5.86a2 2 0 0 1-3.62-.62l-.28-1.3A2.5 2.5 0 0 1 11 13.2z"/><path d="M13.3 15.4h1.7M14.15 14.55v1.7"/><circle cx="18.4" cy="15.1" r=".55" fill="currentColor" stroke="none"/><circle cx="19.7" cy="16.2" r=".55" fill="currentColor" stroke="none"/></svg>',
    'controles': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M6.8 11h3.2M8.4 9.4v3.2"/><circle cx="15.4" cy="11" r=".7" fill="currentColor" stroke="none"/><circle cx="17.6" cy="12.8" r=".7" fill="currentColor" stroke="none"/><path d="M17.2 6.2H6.8A4 4 0 0 0 2.9 9.4C2.6 10.6 2 14.4 2 15.8A2.6 2.6 0 0 0 4.6 18.4c1 0 1.5-.5 2-1l1.1-1.1a2 2 0 0 1 1.4-.6h5.8a2 2 0 0 1 1.4.6l1.1 1.1c.5.5 1 1 2 1a2.6 2.6 0 0 0 2.6-2.6c0-1.4-.6-5.2-.9-6.4a4 4 0 0 0-3.9-3.2Z"/></svg>',
    'controle': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M6.8 11h3.2M8.4 9.4v3.2"/><circle cx="15.4" cy="11" r=".7" fill="currentColor" stroke="none"/><circle cx="17.6" cy="12.8" r=".7" fill="currentColor" stroke="none"/><path d="M17.2 6.2H6.8A4 4 0 0 0 2.9 9.4C2.6 10.6 2 14.4 2 15.8A2.6 2.6 0 0 0 4.6 18.4c1 0 1.5-.5 2-1l1.1-1.1a2 2 0 0 1 1.4-.6h5.8a2 2 0 0 1 1.4.6l1.1 1.1c.5.5 1 1 2 1a2.6 2.6 0 0 0 2.6-2.6c0-1.4-.6-5.2-.9-6.4a4 4 0 0 0-3.9-3.2Z"/></svg>',
    'joysticks': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M6.8 11h3.2M8.4 9.4v3.2"/><circle cx="15.4" cy="11" r=".7" fill="currentColor" stroke="none"/><circle cx="17.6" cy="12.8" r=".7" fill="currentColor" stroke="none"/><path d="M17.2 6.2H6.8A4 4 0 0 0 2.9 9.4C2.6 10.6 2 14.4 2 15.8A2.6 2.6 0 0 0 4.6 18.4c1 0 1.5-.5 2-1l1.1-1.1a2 2 0 0 1 1.4-.6h5.8a2 2 0 0 1 1.4.6l1.1 1.1c.5.5 1 1 2 1a2.6 2.6 0 0 0 2.6-2.6c0-1.4-.6-5.2-.9-6.4a4 4 0 0 0-3.9-3.2Z"/></svg>',
    'fones': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M4 13.5v-1.5a8 8 0 0 1 16 0v1.5"/><rect x="2.6" y="13" width="4.4" height="7" rx="2.2"/><rect x="17" y="13" width="4.4" height="7" rx="2.2"/></svg>',
    'fone': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M4 13.5v-1.5a8 8 0 0 1 16 0v1.5"/><rect x="2.6" y="13" width="4.4" height="7" rx="2.2"/><rect x="17" y="13" width="4.4" height="7" rx="2.2"/></svg>',
    'headsets': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M4 13.5v-1.5a8 8 0 0 1 16 0v1.5"/><rect x="2.6" y="13" width="4.4" height="7" rx="2.2"/><rect x="17" y="13" width="4.4" height="7" rx="2.2"/></svg>',
    'headset': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M4 13.5v-1.5a8 8 0 0 1 16 0v1.5"/><rect x="2.6" y="13" width="4.4" height="7" rx="2.2"/><rect x="17" y="13" width="4.4" height="7" rx="2.2"/></svg>',
    'monitores': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.4" y="3.4" width="19.2" height="13" rx="2"/><line x1="8.5" y1="20.4" x2="15.5" y2="20.4"/><line x1="12" y1="16.4" x2="12" y2="20.4"/></svg>',
    'monitor': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.4" y="3.4" width="19.2" height="13" rx="2"/><line x1="8.5" y1="20.4" x2="15.5" y2="20.4"/><line x1="12" y1="16.4" x2="12" y2="20.4"/></svg>',
    'mouse': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="6.5" y="3" width="11" height="18" rx="5.5"/><line x1="12" y1="7" x2="12" y2="11"/></svg>',
    'mouses': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="6.5" y="3" width="11" height="18" rx="5.5"/><line x1="12" y1="7" x2="12" y2="11"/></svg>',
    'acessorios gamer': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="6.5" y="3" width="11" height="18" rx="5.5"/><line x1="12" y1="7" x2="12" y2="11"/></svg>',
    'acessorios': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="6.5" y="3" width="11" height="18" rx="5.5"/><line x1="12" y1="7" x2="12" y2="11"/></svg>',
    'gift card': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="3" y="8.2" width="18" height="4.4" rx="1"/><path d="M12 8.2V21"/><path d="M19.5 12.6V19a2 2 0 0 1-2 2h-11a2 2 0 0 1-2-2v-6.4"/><path d="M7.6 8.2a2.5 2.5 0 0 1 0-5C11 3.2 12 8.2 12 8.2s1-5 4.4-5a2.5 2.5 0 0 1 0 5"/></svg>',
    'gift cards': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="3" y="8.2" width="18" height="4.4" rx="1"/><path d="M12 8.2V21"/><path d="M19.5 12.6V19a2 2 0 0 1-2 2h-11a2 2 0 0 1-2-2v-6.4"/><path d="M7.6 8.2a2.5 2.5 0 0 1 0-5C11 3.2 12 8.2 12 8.2s1-5 4.4-5a2.5 2.5 0 0 1 0 5"/></svg>',
    'vale presente': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="3" y="8.2" width="18" height="4.4" rx="1"/><path d="M12 8.2V21"/><path d="M19.5 12.6V19a2 2 0 0 1-2 2h-11a2 2 0 0 1-2-2v-6.4"/><path d="M7.6 8.2a2.5 2.5 0 0 1 0-5C11 3.2 12 8.2 12 8.2s1-5 4.4-5a2.5 2.5 0 0 1 0 5"/></svg>',
    'tv': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.5" y="7" width="19" height="12" rx="2"/><path d="M7.5 3.5 12 7l4.5-3.5"/></svg>',
    'tvs': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.5" y="7" width="19" height="12" rx="2"/><path d="M7.5 3.5 12 7l4.5-3.5"/></svg>',
    'televisao': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.5" y="7" width="19" height="12" rx="2"/><path d="M7.5 3.5 12 7l4.5-3.5"/></svg>',
    'televisão': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.5" y="7" width="19" height="12" rx="2"/><path d="M7.5 3.5 12 7l4.5-3.5"/></svg>',
    'smart tv': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.5" y="7" width="19" height="12" rx="2"/><path d="M7.5 3.5 12 7l4.5-3.5"/></svg>',
    'teclado': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M5.5 9.5h.01M9 9.5h.01M12.5 9.5h.01M16 9.5h.01M18.5 9.5h.01M5.5 12.5h.01M9 12.5h.01M12.5 12.5h.01M16 12.5h.01M18.5 12.5h.01M8 15.3h8"/></svg>',
    'teclados': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M5.5 9.5h.01M9 9.5h.01M12.5 9.5h.01M16 9.5h.01M18.5 9.5h.01M5.5 12.5h.01M9 12.5h.01M12.5 12.5h.01M16 12.5h.01M18.5 12.5h.01M8 15.3h8"/></svg>',
    'cabos': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M9 2v6M15 2v6"/><path d="M6.5 8h11v3a5.5 5.5 0 0 1-11 0z"/><path d="M12 16.5V22"/></svg>',
    'cabo': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M9 2v6M15 2v6"/><path d="M6.5 8h11v3a5.5 5.5 0 0 1-11 0z"/><path d="M12 16.5V22"/></svg>',
    'adaptadores': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M9 2v6M15 2v6"/><path d="M6.5 8h11v3a5.5 5.5 0 0 1-11 0z"/><path d="M12 16.5V22"/></svg>',
    'carregadores': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.5" y="7" width="15.5" height="10" rx="2"/><path d="M21.5 11v2"/><path d="M11 9.5 9 12.5h3l-2 3"/></svg>',
    'webcam': '<svg width="20" height="20" viewBox="0 0 24 24"><circle cx="12" cy="9.5" r="6"/><circle cx="12" cy="9.5" r="2.2"/><path d="M8.5 20.5 9.5 17h5l1 3.5z"/></svg>',
    'webcams': '<svg width="20" height="20" viewBox="0 0 24 24"><circle cx="12" cy="9.5" r="6"/><circle cx="12" cy="9.5" r="2.2"/><path d="M8.5 20.5 9.5 17h5l1 3.5z"/></svg>',
    'cadeira gamer': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M7.5 4.5A1.5 1.5 0 0 1 9 3h6a1.5 1.5 0 0 1 1.5 1.5V11H7.5z"/><path d="M6.5 11h11v2.5a3 3 0 0 1-3 3h-5a3 3 0 0 1-3-3z"/><path d="M12 16.5V21M8.5 21h7"/></svg>',
    'cadeiras': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M7.5 4.5A1.5 1.5 0 0 1 9 3h6a1.5 1.5 0 0 1 1.5 1.5V11H7.5z"/><path d="M6.5 11h11v2.5a3 3 0 0 1-3 3h-5a3 3 0 0 1-3-3z"/><path d="M12 16.5V21M8.5 21h7"/></svg>',
    'cadeiras gamer': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M7.5 4.5A1.5 1.5 0 0 1 9 3h6a1.5 1.5 0 0 1 1.5 1.5V11H7.5z"/><path d="M6.5 11h11v2.5a3 3 0 0 1-3 3h-5a3 3 0 0 1-3-3z"/><path d="M12 16.5V21M8.5 21h7"/></svg>',
    'cadeira': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M7.5 4.5A1.5 1.5 0 0 1 9 3h6a1.5 1.5 0 0 1 1.5 1.5V11H7.5z"/><path d="M6.5 11h11v2.5a3 3 0 0 1-3 3h-5a3 3 0 0 1-3-3z"/><path d="M12 16.5V21M8.5 21h7"/></svg>',
    'armazenamento': '<svg width="20" height="20" viewBox="0 0 24 24"><line x1="22" y1="12" x2="2" y2="12"/><path d="M5.4 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.4-6.9A2 2 0 0 0 16.8 4H7.2a2 2 0 0 0-1.8 1.1z"/><circle cx="6.5" cy="16" r=".7" fill="currentColor" stroke="none"/><circle cx="9.5" cy="16" r=".7" fill="currentColor" stroke="none"/></svg>',
    'ssd': '<svg width="20" height="20" viewBox="0 0 24 24"><line x1="22" y1="12" x2="2" y2="12"/><path d="M5.4 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.4-6.9A2 2 0 0 0 16.8 4H7.2a2 2 0 0 0-1.8 1.1z"/><circle cx="6.5" cy="16" r=".7" fill="currentColor" stroke="none"/><circle cx="9.5" cy="16" r=".7" fill="currentColor" stroke="none"/></svg>',
    'hd': '<svg width="20" height="20" viewBox="0 0 24 24"><line x1="22" y1="12" x2="2" y2="12"/><path d="M5.4 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.4-6.9A2 2 0 0 0 16.8 4H7.2a2 2 0 0 0-1.8 1.1z"/><circle cx="6.5" cy="16" r=".7" fill="currentColor" stroke="none"/><circle cx="9.5" cy="16" r=".7" fill="currentColor" stroke="none"/></svg>',
    'hds': '<svg width="20" height="20" viewBox="0 0 24 24"><line x1="22" y1="12" x2="2" y2="12"/><path d="M5.4 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.4-6.9A2 2 0 0 0 16.8 4H7.2a2 2 0 0 0-1.8 1.1z"/><circle cx="6.5" cy="16" r=".7" fill="currentColor" stroke="none"/><circle cx="9.5" cy="16" r=".7" fill="currentColor" stroke="none"/></svg>',
    'ssds': '<svg width="20" height="20" viewBox="0 0 24 24"><line x1="22" y1="12" x2="2" y2="12"/><path d="M5.4 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.4-6.9A2 2 0 0 0 16.8 4H7.2a2 2 0 0 0-1.8 1.1z"/><circle cx="6.5" cy="16" r=".7" fill="currentColor" stroke="none"/><circle cx="9.5" cy="16" r=".7" fill="currentColor" stroke="none"/></svg>',
    'processador': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="5.5" y="5.5" width="13" height="13" rx="1.6"/><rect x="9.5" y="9.5" width="5" height="5" rx=".6"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/></svg>',
    'processadores': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="5.5" y="5.5" width="13" height="13" rx="1.6"/><rect x="9.5" y="9.5" width="5" height="5" rx=".6"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/></svg>',
    'hardware': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="5.5" y="5.5" width="13" height="13" rx="1.6"/><rect x="9.5" y="9.5" width="5" height="5" rx=".6"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/></svg>',
    'placas': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="5.5" y="5.5" width="13" height="13" rx="1.6"/><rect x="9.5" y="9.5" width="5" height="5" rx=".6"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/></svg>',
    'notebook': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M5 5.5h14a1.5 1.5 0 0 1 1.5 1.5v8.5H3.5V7A1.5 1.5 0 0 1 5 5.5z"/><path d="M2 15.5h20l-.9 2.2a1 1 0 0 1-.9.8H3.8a1 1 0 0 1-.9-.8z"/></svg>',
    'notebooks': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M5 5.5h14a1.5 1.5 0 0 1 1.5 1.5v8.5H3.5V7A1.5 1.5 0 0 1 5 5.5z"/><path d="M2 15.5h20l-.9 2.2a1 1 0 0 1-.9.8H3.8a1 1 0 0 1-.9-.8z"/></svg>',
    'laptop': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M5 5.5h14a1.5 1.5 0 0 1 1.5 1.5v8.5H3.5V7A1.5 1.5 0 0 1 5 5.5z"/><path d="M2 15.5h20l-.9 2.2a1 1 0 0 1-.9.8H3.8a1 1 0 0 1-.9-.8z"/></svg>',
    'laptops': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M5 5.5h14a1.5 1.5 0 0 1 1.5 1.5v8.5H3.5V7A1.5 1.5 0 0 1 5 5.5z"/><path d="M2 15.5h20l-.9 2.2a1 1 0 0 1-.9.8H3.8a1 1 0 0 1-.9-.8z"/></svg>',
    'celular': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="6" y="2" width="12" height="20" rx="2.6"/><line x1="12" y1="18" x2="12" y2="18.01"/></svg>',
    'celulares': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="6" y="2" width="12" height="20" rx="2.6"/><line x1="12" y1="18" x2="12" y2="18.01"/></svg>',
    'smartphone': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="6" y="2" width="12" height="20" rx="2.6"/><line x1="12" y1="18" x2="12" y2="18.01"/></svg>',
    'smartphones': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="6" y="2" width="12" height="20" rx="2.6"/><line x1="12" y1="18" x2="12" y2="18.01"/></svg>',
    'bateria': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.5" y="7" width="15.5" height="10" rx="2"/><path d="M21.5 11v2"/><path d="M11 9.5 9 12.5h3l-2 3"/></svg>',
    'baterias': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.5" y="7" width="15.5" height="10" rx="2"/><path d="M21.5 11v2"/><path d="M11 9.5 9 12.5h3l-2 3"/></svg>',
    'powerbank': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.5" y="7" width="15.5" height="10" rx="2"/><path d="M21.5 11v2"/><path d="M11 9.5 9 12.5h3l-2 3"/></svg>',
    'powerbanks': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.5" y="7" width="15.5" height="10" rx="2"/><path d="M21.5 11v2"/><path d="M11 9.5 9 12.5h3l-2 3"/></svg>',
    'carregador': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="2.5" y="7" width="15.5" height="10" rx="2"/><path d="M21.5 11v2"/><path d="M11 9.5 9 12.5h3l-2 3"/></svg>',
    'microfone': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10.5v.5a7 7 0 0 0 14 0v-.5"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="8.5" y1="22" x2="15.5" y2="22"/></svg>',
    'microfones': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10.5v.5a7 7 0 0 0 14 0v-.5"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="8.5" y1="22" x2="15.5" y2="22"/></svg>',
    'mic': '<svg width="20" height="20" viewBox="0 0 24 24"><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10.5v.5a7 7 0 0 0 14 0v-.5"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="8.5" y1="22" x2="15.5" y2="22"/></svg>',
    'cooler': '<svg width="20" height="20" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6"/><path d="M12 10.4c1.8-3.2-.5-6-1.8-6.3-.4 2 .3 4.3 1.8 6.3z"/><path d="M13.6 12c3.2 1.8 6-.5 6.3-1.8-2-.4-4.3.3-6.3 1.8z"/><path d="M12 13.6c-1.8 3.2.5 6 1.8 6.3.4-2-.3-4.3-1.8-6.3z"/><path d="M10.4 12c-3.2-1.8-6 .5-6.3 1.8 2 .4 4.3-.3 6.3-1.8z"/></svg>',
    'coolers': '<svg width="20" height="20" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6"/><path d="M12 10.4c1.8-3.2-.5-6-1.8-6.3-.4 2 .3 4.3 1.8 6.3z"/><path d="M13.6 12c3.2 1.8 6-.5 6.3-1.8-2-.4-4.3.3-6.3 1.8z"/><path d="M12 13.6c-1.8 3.2.5 6 1.8 6.3.4-2-.3-4.3-1.8-6.3z"/><path d="M10.4 12c-3.2-1.8-6 .5-6.3 1.8 2 .4 4.3-.3 6.3-1.8z"/></svg>',
    'ventilador': '<svg width="20" height="20" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6"/><path d="M12 10.4c1.8-3.2-.5-6-1.8-6.3-.4 2 .3 4.3 1.8 6.3z"/><path d="M13.6 12c3.2 1.8 6-.5 6.3-1.8-2-.4-4.3.3-6.3 1.8z"/><path d="M12 13.6c-1.8 3.2.5 6 1.8 6.3.4-2-.3-4.3-1.8-6.3z"/><path d="M10.4 12c-3.2-1.8-6 .5-6.3 1.8 2 .4 4.3-.3 6.3-1.8z"/></svg>',
    'ventiladores': '<svg width="20" height="20" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6"/><path d="M12 10.4c1.8-3.2-.5-6-1.8-6.3-.4 2 .3 4.3 1.8 6.3z"/><path d="M13.6 12c3.2 1.8 6-.5 6.3-1.8-2-.4-4.3.3-6.3 1.8z"/><path d="M12 13.6c-1.8 3.2.5 6 1.8 6.3.4-2-.3-4.3-1.8-6.3z"/><path d="M10.4 12c-3.2-1.8-6 .5-6.3 1.8 2 .4 4.3-.3 6.3-1.8z"/></svg>',
    'fans': '<svg width="20" height="20" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6"/><path d="M12 10.4c1.8-3.2-.5-6-1.8-6.3-.4 2 .3 4.3 1.8 6.3z"/><path d="M13.6 12c3.2 1.8 6-.5 6.3-1.8-2-.4-4.3.3-6.3 1.8z"/><path d="M12 13.6c-1.8 3.2.5 6 1.8 6.3.4-2-.3-4.3-1.8-6.3z"/><path d="M10.4 12c-3.2-1.8-6 .5-6.3 1.8 2 .4 4.3-.3 6.3-1.8z"/></svg>',
    'outros': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M12.6 2.6A2 2 0 0 0 11.2 2H4a2 2 0 0 0-2 2v7.2a2 2 0 0 0 .6 1.4l8.7 8.7a2.4 2.4 0 0 0 3.4 0l6.6-6.6a2.4 2.4 0 0 0 0-3.4z"/><circle cx="7.4" cy="7.4" r="1.5"/></svg>',
}
_CATS = []


def _carregar_visual():
    """Le config_visual.json (gerado pelo painel web). Opcional: se nao existir,
    devolve mapa vazio e nada muda. Formato: {"icones": {"<Categoria>": "<chave>"}}."""
    caminho = Path(__file__).resolve().parent / "config_visual.json"
    try:
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
        return dados.get("icones", {}) or {}
    except (FileNotFoundError, ValueError):
        return {}


_VISUAL_ICONES = _carregar_visual()


def _icone(cat):
    key = (cat or "").strip().lower()
    # Override do painel: aceita o nome exato da categoria ou a versao minuscula.
    escolha = _VISUAL_ICONES.get(cat) or _VISUAL_ICONES.get(key)
    if escolha:
        escolha = str(escolha).strip().lower()
        if escolha in _ICONES:
            return _ICONES[escolha]
    return _ICONES.get(key, _ICONES["outros"])


_SICONES = {
    'hot': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.4-.5-2-1-3-1.1-2.1-.2-4 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.1.4-2.3 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>',
    'queda': '<svg width="20" height="20" viewBox="0 0 24 24"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>',
    'star': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M12 3l2.5 5.1 5.6.8-4 4 1 5.6-5-2.7-5 2.7 1-5.6-4-4 5.6-.8z"/></svg>',
    'grid': '<svg width="20" height="20" viewBox="0 0 24 24"><path d="M6 2 3 6v13a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
}


def _beneficios(p):
    b = []
    if p.get("pagamento"):
        b.append(f'<span class="benef pix">{_mini("pix")} À vista {e(p.get("pagamento"))}</span>')
    if p.get("parcelas"):
        b.append(f'<span class="benef parc">{_mini("card")} {e(p.get("parcelas"))}</span>')
    if p.get("frete"):
        b.append(f'<span class="benef frete">{_mini("frete")} Frete grátis</span>')
    return f'<div class="beneficios">{"".join(b)}</div>' if b else ""


def _sechead(icon, titulo, sub="", tag="", hid="", tid=""):
    ida = f' id="{hid}"' if hid else ""
    idt = f' id="{tid}"' if tid else ""
    subh = f"<p>{e(sub)}</p>" if sub else ""
    tagh = f'<span class="rt">{tag}</span>' if tag else ""
    return (f'<div class="sec-head"{ida}><span class="ico">{icon}</span>'
            f'<div><h2{idt}>{e(titulo)}</h2>{subh}</div>{tagh}</div>')


def _sicon(name):
    return _SICONES.get(name, _SICONES["grid"])


_MINI = {
    'frete': '<svg class="mi" viewBox="0 0 24 24"><path d="M14 17.5V6.5a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h1.2"/><path d="M9.6 17.5H14"/><path d="M18.8 17.5H20a1 1 0 0 0 1-1v-3.1a1 1 0 0 0-.22-.62l-2.6-3.26A1 1 0 0 0 17.4 9H14"/><circle cx="7" cy="17.7" r="1.9"/><circle cx="16.6" cy="17.7" r="1.9"/></svg>',
    'card': '<svg class="mi" viewBox="0 0 24 24"><rect x="2.4" y="5.2" width="19.2" height="13.6" rx="2.2"/><line x1="2.4" y1="9.6" x2="21.6" y2="9.6"/><line x1="6" y1="14.4" x2="10" y2="14.4"/></svg>',
    'queda': '<svg class="mi" viewBox="0 0 24 24"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>',
    'menu': '<svg class="mi" viewBox="0 0 24 24"><line x1="4" y1="6.5" x2="20" y2="6.5"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17.5" x2="20" y2="17.5"/></svg>',
    'pix': '<svg class="mi" viewBox="0 0 24 24"><path fill="currentColor" stroke="none" d="M12 2.8 8 6.8l4 4 4-4z M12 21.2 8 17.2l4-4 4 4z M2.8 12 6.8 8l4 4-4 4z M21.2 12 17.2 8l-4 4 4 4z"/></svg>',
    'seta': '<svg class="mi" viewBox="0 0 24 24"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>',
    'telegram': '<svg class="mi" viewBox="0 0 24 24"><path d="M14.5 21.4a.5.5 0 0 0 .95 0l6.1-18a.5.5 0 0 0-.64-.64l-18 6.1a.5.5 0 0 0 0 .95l7.7 3.1z"/><path d="M21.4 3.2 10.6 14"/></svg>',
    'whatsapp': '<svg class="mi" viewBox="0 0 24 24"><path d="M3.5 20.5l1.2-4.3A8.3 8.3 0 1 1 8 19.4z"/><path fill="currentColor" stroke="none" d="M8.8 8.4c-.2.3-.5.9-.5 1.6 0 1 .7 2.1 1 2.4.5.7 1.7 2 3.4 2.5.9.3 1.4.2 1.9-.1.3-.2.6-.7.7-1 .1-.3 0-.5-.2-.6l-1.4-.7c-.2-.1-.4 0-.5.1l-.4.5c-.1.1-.3.2-.5.1-.7-.3-1.4-.8-1.9-1.7-.1-.2 0-.4.1-.5l.4-.4c.1-.2.1-.3 0-.5l-.6-1.3c-.2-.4-.4-.4-.6-.4z"/></svg>',
    'instagram': '<svg class="mi" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r="1.1" fill="currentColor" stroke="none"/></svg>',
    'tiktok': '<svg class="mi" viewBox="0 0 24 24"><path d="M13.4 3.5v10.8a3.3 3.3 0 1 1-2.6-3.2"/><path d="M13.4 4.2A5.2 5.2 0 0 0 18.6 9"/></svg>',
    'youtube': '<svg class="mi" viewBox="0 0 24 24"><rect x="2.4" y="5.6" width="19.2" height="12.8" rx="3.8"/><path d="M10.2 9.2 15 12l-4.8 2.8z" fill="currentColor" stroke="none"/></svg>',
}


def _mini(k):
    return _MINI.get(k, "")


def _preparar_logo(origem, destino, tam=200):
    """Recorta a borda quase-branca do logo e salva uma versao circular limpa."""
    try:
        from PIL import Image, ImageDraw
    except Exception:
        import shutil; shutil.copy(origem, destino); return
    im = Image.open(origem).convert("RGBA")
    rgb = im.convert("RGB"); px = rgb.load(); w, h = rgb.size
    def branco(p): return p[0] > 236 and p[1] > 236 and p[2] > 236
    x0, y0, x1, y1 = w, h, 0, 0
    passo = max(1, min(w, h)//360)
    for y in range(0, h, passo):
        for x in range(0, w, passo):
            if not branco(px[x, y]):
                x0=min(x0,x); y0=min(y0,y); x1=max(x1,x); y1=max(y1,y)
    if x1 > x0 and y1 > y0:
        im = im.crop((x0, y0, x1+1, y1+1))
    lado = max(im.size)
    quad = Image.new("RGBA", (lado, lado), (0,0,0,0))
    quad.alpha_composite(im, ((lado-im.width)//2, (lado-im.height)//2))
    sup = tam*4
    quad = quad.resize((sup, sup), Image.LANCZOS)
    mask = Image.new("L", (sup, sup), 0)
    ImageDraw.Draw(mask).ellipse([0,0,sup-1,sup-1], fill=255)
    out = Image.new("RGBA", (sup, sup), (0,0,0,0))
    out.paste(quad, (0,0), mask)
    out.resize((tam, tam), Image.LANCZOS).save(destino)


def _gerar_favicons(logo_png, saida, cor_fundo="#123a2c"):
    """Gera favicon.ico, favicons PNG e apple-touch-icon a partir do logo."""
    try:
        from PIL import Image
    except Exception:
        return
    try:
        base = Image.open(logo_png).convert("RGBA")
    except Exception:
        return
    # favicons transparentes (circular do logo)
    for tam in (16, 32, 180):
        base.resize((tam, tam), Image.LANCZOS).save(saida / f"favicon-{tam}x{tam}.png")
    # favicon.ico multi-tamanho
    try:
        base.resize((64, 64), Image.LANCZOS).save(
            saida / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    except Exception:
        base.resize((32, 32), Image.LANCZOS).save(saida / "favicon.ico")
    # apple-touch-icon: logo sobre fundo solido da marca (iOS nao gosta de transparencia)
    h = cor_fundo.lstrip("#")
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) if len(h) >= 6 else (18, 58, 44)
    fundo = Image.new("RGBA", (180, 180), rgb + (255,))
    logo180 = base.resize((150, 150), Image.LANCZOS)
    fundo.alpha_composite(logo180, (15, 15))
    fundo.convert("RGB").save(saida / "apple-touch-icon.png")


def _herobg(itens, base=""):
    """Fotos reais dos produtos flutuando ao fundo do hero (link para o produto)."""
    itens = [(pid, img) for pid, img in (itens or []) if img][:11]
    if not itens:
        return ""
    # Duas colunas coladas nas BORDAS (esquerda <=7% / direita >=88%), deixando
    # todo o centro livre para titulo, busca, abas e filtros. (top, left, tam, vel, rot)
    # Espalhadas pela faixa lateral (left variando 0-14% e 84-93%), escalonadas
    # em x e y pra nao empilhar. Escondem em telas <1100px (ver CSS). (top,left,tam,vel,rot)
    pos = [("4%", "2%", 150, 0.15, -7),    ("3%", "90%", 146, 0.26, 7),
           ("18%", "14%", 110, 0.30, 6),   ("18%", "84%", 114, 0.19, -6),
           ("35%", "1%", 134, 0.22, -5),   ("36%", "93%", 128, 0.16, 8),
           ("52%", "13%", 106, 0.34, 7),   ("54%", "85%", 116, 0.28, -5),
           ("69%", "3%", 126, 0.13, -6),   ("73%", "91%", 102, 0.40, 10),
           ("86%", "12%", 98, 0.36, 9)]
    tiles = ""
    for k, (pid, img) in enumerate(itens):
        t, l, w, sp, r = pos[k % len(pos)]
        tiles += (f'<a class="photo3d" href="{base}p/{pid}.html" data-speed="{sp}" data-ph="{k*1.3:.1f}" data-rot="{r}" '
                  f'style="top:{t};left:{l};width:{w}px;height:{w}px">'
                  f'<img src="{e(img)}" alt="" loading="lazy"></a>')
    return f'<div class="hero-bg">{tiles}</div>'



def _insights(d):
    from statistics import median
    s = d.get("s") or {}
    precos = [h["price"] for h in d["hist"]]
    atual = d["por"]
    med = median(precos) if precos else atual
    out = []
    if s.get("enough_history") and s.get("is_lowest_window", 0) >= 30:
        out.append(("verde", f"Está no menor preço dos últimos {s['is_lowest_window']} dias."))
    if med and abs(atual - med) / med >= 0.03:
        pc = round(abs(atual - med) / med * 100)
        if atual < med:
            out.append(("verde", f"Está {pc}% abaixo da média histórica ({brl(med)})."))
        else:
            out.append(("vermelho", f"Está {pc}% acima da média histórica ({brl(med)})."))
    else:
        out.append(("cinza", f"Preço próximo da média histórica ({brl(med)})."))
    if len(precos) >= 2 and precos[0] != atual:
        dv = atual - precos[0]
        pc = round(abs(dv) / precos[0] * 100)
        if dv < 0:
            out.append(("verde", f"Caiu {brl(-dv)} ({pc}%) desde que começamos a monitorar."))
        else:
            out.append(("cinza", f"Subiu {brl(dv)} ({pc}%) desde que começamos a monitorar."))
    if d.get("termo"):
        out.append(("azul", d["termo"]["rec"]))
    return out[:4]


def _hist_box(d):
    hist = [{"d": h["recorded_at"], "p": round(h["price"], 2)} for h in d["hist"]]
    corg = GRAF[0] or _cor(config.COR_LINHA)
    cormin = GRAF[1] or _cor(config.COR_PRECO)
    _loja = (d.get("p") or {}).get("loja") or ""
    if len(hist) < 2:
        if _loja == "amazon":
            corpo = ('<div class="sem-grafico">📊 <b>Em construção</b> — o histórico de preço '
                     'deste produto da Amazon estará disponível em breve.</div>')
        else:
            corpo = ('<div class="sem-grafico">Histórico em construção — '
                     'acompanhamos o preço todos os dias, volte em breve.</div>')
        botoes = ""
    else:
        botoes = ('<div class="periodos">'
                  '<button data-dias="1">24h</button>'
                  '<button data-dias="7">7 dias</button>'
                  '<button data-dias="30" class="on">30 dias</button>'
                  '<button data-dias="90">90 dias</button>'
                  '<button data-dias="0">Tudo</button></div>')
        corpo = ('<div class="grafico-wrap"><canvas id="grafico"></canvas></div>'
                 '<div class="fatos" id="stats">'
                 '<div>Menor preço<b id="st-min"></b></div>'
                 '<div>Maior preço<b id="st-max"></b></div>'
                 '<div>Preço médio<b id="st-med"></b></div>'
                 '<div>Preço atual<b id="st-atual"></b></div></div>')
    ins = "".join(f'<li class="{c}">{e(t)}</li>' for c, t in _insights(d))
    return (f'<div class="box"><div class="box-head"><h2>Histórico de preço</h2>{botoes}</div>'
            f'{corpo}</div>'
            f'<div class="box"><h2>O que os dados dizem</h2><ul class="insights">{ins}</ul></div>'
            f'<script>window.HIST={json.dumps(hist)};window.CORG="{corg}";window.CORMIN="{cormin}";</script>')


def _semelhantes(d, por_cat):
    cat = d["p"].get("categoria") or "Outros"
    outros = [x for x in por_cat.get(cat, []) if x["p"]["id"] != d["p"]["id"]]
    outros = sorted(outros, key=lambda x: -x.get("relevancia", 0))[:8]
    if not outros:
        return ""
    cards = "".join(card_html(x, base="../") for x in outros)
    return (f'<section class="semelhantes"><h2 class="sec-h2">Produtos semelhantes</h2>'
            f'<div class="grid semelhantes-grid">{cards}</div></section>')


PRODUTO_JS = """
document.querySelectorAll('.card').forEach(function(c){c.classList.add('in');});
(function(){
  var H=window.HIST||[]; if(H.length<2||!window.Chart) return;
  var cv=document.getElementById('grafico'); if(!cv) return;
  var brl=function(v){return 'R$ '+Number(v).toFixed(2).replace('.',',');};
  var z=function(n){return (n<10?'0':'')+n;};
  var dt=function(s){
    if(s==null) return new Date(NaN);
    s=String(s);
    if(s.length<=10) return new Date(s+'T00:00');            // data pura -> meia-noite local
    if(!/[zZ]|[+-]\d\d:?\d\d$/.test(s)) s+='Z';               // sem fuso -> grava em UTC
    return new Date(s);                                        // getHours() ja devolve hora LOCAL
  };
  var chart, dias=30;
  function fatia(){ // pontos REAIS na janela; 24h mostra o horario real de cada leitura
    if(!dias) return H;
    var jan=(dias===1)?24*36e5:dias*864e5;
    var corte=Date.now()-jan;
    var f=H.filter(function(x){return dt(x.d).getTime()>=corte;});
    return f.length>=2?f:H.slice(-2);
  }
  function stats(arr){
    var ps=arr.map(function(x){return x.p;});
    var mn=Math.min.apply(null,ps), mx=Math.max.apply(null,ps);
    var med=ps.reduce(function(a,b){return a+b;},0)/ps.length, at=ps[ps.length-1];
    function g(id,v){var e=document.getElementById(id); if(e)e.textContent=brl(v);}
    g('st-min',mn);g('st-max',mx);g('st-med',med);g('st-atual',at);
    return {mn:mn,mx:mx};
  }
  // linha vertical tracejada seguindo o mouse
  var vline={id:'vline',afterDatasetsDraw:function(c){
    var t=c.tooltip; if(!(t&&t._active&&t._active.length))return;
    var x=t._active[0].element.x, a=c.chartArea, g=c.ctx;
    g.save();g.beginPath();g.moveTo(x,a.top);g.lineTo(x,a.bottom);
    g.lineWidth=1;g.strokeStyle=window.CORG+'55';g.setLineDash([4,4]);g.stroke();g.restore();
  }};
  function porDia(a){ var m={},o=[]; a.forEach(function(x){ m[x.d.slice(0,10)]=x; });
    Object.keys(m).sort().forEach(function(k){ o.push(m[k]); }); return o; }
  function render(){
    var raw=fatia(); stats(raw);              // stats usam o dado real
    var porHora=(dias===1);   // formato do eixo depende do FILTRO, nao dos dados
    // nas visoes de dias, 1 ponto por dia (ultimo preco do dia) -> linha limpa, sem dia repetido
    var arr=raw; if(!porHora){ var ag=porDia(raw); if(ag.length>=2) arr=ag; }
    var _ps=arr.map(function(x){return x.p;});
    var mn=Math.min.apply(null,_ps), mx=Math.max.apply(null,_ps);
    var labels=arr.map(function(x){var d=dt(x.d);
      return porHora?(z(d.getHours())+':'+z(d.getMinutes())):(z(d.getDate())+'/'+z(d.getMonth()+1));});
    var data=arr.map(function(x){return x.p;});
    var destaca=function(x,i){return (mn!==mx && x.p===mn)||i===arr.length-1;};
    var cores=arr.map(function(x,i){return (mn!==mx && x.p===mn)?window.CORMIN:(i===arr.length-1?window.CORG:'rgba(0,0,0,0)');});
    var raios=arr.map(function(x,i){return destaca(x,i)?4.5:0;});
    if(chart)chart.destroy();
    chart=new Chart(cv,{type:'line',data:{labels:labels,datasets:[{data:data,fill:true,
      borderColor:window.CORG,borderWidth:2.6,tension:.32,clip:8,
      pointBackgroundColor:cores,pointBorderColor:'#fff',pointBorderWidth:1.5,pointRadius:raios,
      pointHoverRadius:6,pointHoverBorderWidth:2,pointHoverBackgroundColor:window.CORG,
      backgroundColor:function(ctx){var ch=ctx.chart,ca=ch.chartArea; if(!ca)return window.CORG+'22';
        var g=ch.ctx.createLinearGradient(0,ca.top,0,ca.bottom);
        g.addColorStop(0,window.CORG+'45');g.addColorStop(1,window.CORG+'00');return g;}}]},
      options:{responsive:true,maintainAspectRatio:false,animation:{duration:450},
        layout:{padding:{top:8,right:6,left:2,bottom:2}},
        interaction:{mode:'index',intersect:false},
        plugins:{legend:{display:false},tooltip:{
          backgroundColor:'#0f1a15',borderColor:window.CORG,borderWidth:1,padding:{x:12,y:9},
          cornerRadius:10,displayColors:false,caretSize:6,
          titleColor:'#a8c4b6',titleFont:{size:11,weight:'500'},
          bodyColor:'#fff',bodyFont:{size:15,weight:'800'},
          callbacks:{
            title:function(i){var d=dt(arr[i[0].dataIndex].d);
              return d.getDate()+'/'+z(d.getMonth()+1)+' · '+z(d.getHours())+':'+z(d.getMinutes());},
            label:function(i){return brl(i.raw);}}}},
        scales:{
          y:{ticks:{callback:function(v){return brl(v);},font:{size:11},color:'#9aa0a6',maxTicksLimit:5,padding:6},
             grid:{color:'rgba(0,0,0,.06)',drawTicks:false},border:{display:false}},
          x:{ticks:{maxTicksLimit:7,autoSkip:true,maxRotation:0,font:{size:11},color:'#9aa0a6',padding:4},
             grid:{display:false},border:{display:false}}}},
      plugins:[vline]});
  }
  document.querySelectorAll('.periodos button').forEach(function(b){
    b.addEventListener('click',function(){
      document.querySelectorAll('.periodos button').forEach(function(x){x.classList.remove('on');});
      b.classList.add('on'); dias=+b.dataset.dias; render();});
  });
  render();
})();
"""


def cabecalho(titulo, desc, base="", canonical="", cat_atual="", og_image="", og_dims=True):
    logo = f'<img src="{base}logo.png" alt="">' if (SAIDA / "logo.png").exists() else ""
    url = (config.SITE_URL + "/" + canonical) if canonical else config.SITE_URL
    ogimg = og_image or (config.SITE_URL + "/og/home.png")
    css = (CSS.replace("{{BG}}", _cor(config.COR_RODAPE))
              .replace("{{BARRA}}", _cor(config.COR_BARRA))
              .replace("{{AC}}", _cor(config.COR_LINHA))
              .replace("{{PRECO}}", _cor(config.COR_PRECO)))
    return f"""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titulo)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<link rel="icon" href="{base}favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="{base}favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{base}favicon-16x16.png">
<link rel="apple-touch-icon" href="{base}apple-touch-icon.png">
<meta property="og:site_name" content="{e(config.BRAND_NAME)}">
<meta property="og:title" content="{e(titulo)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}"><meta property="og:type" content="website">
<meta property="og:image" content="{e(ogimg)}"><meta property="og:image:alt" content="{e(titulo)}">
{'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">' if og_dims else ''}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(titulo)}"><meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{e(ogimg)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<header class="top"><div class="in">
<a class="marca" href="{base}index.html">{logo}<div class="brand"><b>{e(config.BRAND_NAME)}</b><small>{e(config.BRAND_SUB)}</small></div></a>
<nav><a href="{base}index.html">Ofertas</a><a href="{base}links.html">Redes</a></nav>
</div></header>""" + _catbar(base, cat_atual)


def _catbar(base, cat_atual=""):
    if not _CATS:
        return ""
    links = "".join(
        f'<a class="{"on" if c == cat_atual else ""}" href="{base}c/{cat_slug(c)}.html">'
        f'{_icone(c)}<span>{e(c)}</span></a>' for c in _CATS)
    return f'<div class="catbar"><div class="in">{links}</div></div>'


def _cta_telegram(base=""):
    link = e(config.CHANNEL_INVITE or "")
    if not link:
        return ""
    ico = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="#06231a">'
           '<path d="M22 3 2 11l6 2 2 6 3-4 5 4 4-16z"/></svg>')
    return (f'<section class="cta-tg"><div class="cta-tg-in">'
            f'<div class="tg-txt"><h3>Receba as ofertas antes de todo mundo</h3>'
            f'<p>As maiores quedas de preço e os cupons caem primeiro no nosso canal do '
            f'Telegram — de graça, sem spam.</p></div>'
            f'<a class="tg-btn" href="{link}" target="_blank" rel="noopener">{ico}Entrar no canal &rarr;</a>'
            f'</div></section>')


FAQ = [
    ("O Garimpo Gamer Cupons é gratuito?",
     "Sim, 100% gratuito. Você não paga nada para ver as ofertas nem para usar o site."),
    ("Como vocês ganham dinheiro?",
     "Usamos links de afiliado. Quando você compra por um link nosso, a loja nos paga uma "
     "pequena comissão — e o preço para você continua exatamente o mesmo."),
    ("Os preços e descontos são confiáveis?",
     "Coletamos os preços automaticamente e mostramos o histórico real de cada produto, "
     "para você ver se o desconto é de verdade. Ainda assim, confira sempre o valor na "
     "loja antes de finalizar a compra."),
    ("De quais lojas são as ofertas?",
     "No momento, Mercado Livre e Amazon. Estamos sempre avaliando novas lojas."),
    ("Com que frequência os preços são atualizados?",
     "Várias vezes ao dia, de forma automática."),
    ("Como recebo as ofertas em primeira mão?",
     "Siga nossos canais nas redes sociais — publicamos as melhores ofertas o dia todo."),
]


# Script independente (fora do JS principal): enquete + sugestao de produto.
# Fica num <script> separado de proposito -> se o JS principal der algum erro,
# o modal e a enquete continuam funcionando (abrir, fechar, enviar).
_WIDGETS_JS = '''<script>
(function(){
  var W3F='04f8e848-dcb9-4c66-af97-4f78de1f5e63';
  function w3f(payload,ok,fail){
    fetch('https://api.web3forms.com/submit',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(Object.assign({access_key:W3F},payload))})
      .then(function(r){return r.json();}).then(function(j){j.success?ok():fail(j.message||'erro');}).catch(function(e){fail(e.message);});
  }
  window.abrirSug=function(nome){
    var bg=document.getElementById('sugbg'); if(!bg)return;
    var n=document.getElementById('sug-nome'),l=document.getElementById('sug-link'),er=document.getElementById('sug-erro');
    var box=bg.querySelector('.sugbox');
    if(box && !document.getElementById('sug-enviar')){ box.innerHTML=window._sugForm; ligarEnviar(); }
    n=document.getElementById('sug-nome'); l=document.getElementById('sug-link'); er=document.getElementById('sug-erro');
    if(n)n.value=nome||''; if(l)l.value=''; if(er)er.textContent='';
    bg.classList.add('on');
    var ac=document.getElementById('ac'); if(ac)ac.classList.remove('on');
    if(n)n.focus();
  };
  function fechar(){ var bg=document.getElementById('sugbg'); if(bg)bg.classList.remove('on'); }
  function ligarEnviar(){
    var env=document.getElementById('sug-enviar'); if(!env)return;
    env.onclick=function(){
      var nome=(document.getElementById('sug-nome').value||'').trim();
      var link=(document.getElementById('sug-link').value||'').trim();
      var er=document.getElementById('sug-erro');
      if(!nome){er.textContent='Informe o nome do produto.';return;}
      if(!link){er.textContent='Informe o link do produto.';return;}
      env.disabled=true; env.textContent='Enviando...';
      w3f({subject:'Sugestao de produto - GGCupons',from_name:'Sugestao GGCupons',produto:nome,link:link},
        function(){ var bg=document.getElementById('sugbg'); bg.querySelector('.sugbox').innerHTML='<h3>Recebido!</h3><p>Vamos cadastrar e monitorar o preco desse produto. Obrigado pela sugestao!</p><button id="sug-ok">Fechar</button>'; var ok=document.getElementById('sug-ok'); if(ok)ok.onclick=fechar; },
        function(m){ er.textContent='Erro ao enviar: '+m; env.disabled=false; env.textContent='Enviar sugestao'; });
    };
  }
  var bg=document.getElementById('sugbg');
  if(bg){
    var box=bg.querySelector('.sugbox'); if(box)window._sugForm=box.innerHTML;
    var x=document.getElementById('sug-x'); if(x)x.onclick=fechar;
    bg.addEventListener('click',function(e){ if(e.target===bg)fechar(); });
    document.addEventListener('keydown',function(e){ if(e.key==='Escape')fechar(); });
    ligarEnviar();
  }
  var poll=document.getElementById('poll');
  if(poll){
    var skip=false; try{skip=!!localStorage.getItem('gg_poll');}catch(e){}
    if(!skip){
      var opts=document.getElementById('poll-opts');
      ['Mercado Livre','Amazon'].forEach(function(loja){
        var b=document.createElement('button'); b.className='poll-op'; b.textContent=loja;
        b.onclick=function(){
          w3f({subject:'Enquete: loja preferida - GGCupons',from_name:'Enquete GGCupons',loja:loja},function(){},function(){});
          try{localStorage.setItem('gg_poll','1');}catch(e){}
          poll.innerHTML='<div class="poll-q">Valeu pela resposta!</div>';
          setTimeout(function(){poll.classList.remove('on');},1800);
        };
        opts.appendChild(b);
      });
      var px=document.getElementById('poll-x'); if(px)px.onclick=function(){ poll.classList.remove('on'); try{localStorage.setItem('gg_poll','1');}catch(e){} };
      setTimeout(function(){ poll.classList.add('on'); },3500);
    }
  }
})();
</script>'''


def _rodape(base="", full=False):
    logo = f'<img src="{base}logo.png" alt="">' if (SAIDA / "logo.png").exists() else ""
    ano = datetime.now(timezone.utc).year
    faq = ""
    if full:
        itens = "".join(
            f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in FAQ)
        faq = (f'<section class="faq-wrap" id="faq"><h2 class="faq-h">Perguntas frequentes</h2>'
               f'{itens}</section>')
    return faq + f'''<footer class="gg-footer">
<div class="gg-foot-top">
  <div class="gg-foot-brand">
    <a class="gg-foot-logo" href="{base}index.html">{logo}<span><b>{e(config.BRAND_NAME)}</b><small>{e(config.BRAND_SUB)}</small></span></a>
    <p>Comparamos preços de games e tech todos os dias e mostramos o histórico real de cada
    produto — para você saber se o desconto é de verdade antes de comprar.</p>
  </div>
  <div class="gg-foot-cols">
    <div class="gg-foot-col"><h5>Navegação</h5>
      <a href="{base}index.html">Ofertas</a>
      <a href="{base}index.html#faq">Perguntas frequentes</a>
      <a href="{base}links.html">Nossas redes</a>
    </div>
    <div class="gg-foot-col"><h5>Lojas</h5>
      <a href="{base}c/jogos.html">Jogos</a>
      <a href="{base}c/consoles.html">Consoles</a>
      <a href="{base}index.html">Ver todas</a>
    </div>
    <div class="gg-foot-col"><h5>Contato</h5>
      <a href="mailto:contato@ggcupons.com">contato@ggcupons.com</a>
      <p>Sugestões de produtos e parcerias são bem-vindas.</p>
    </div>
  </div>
</div>
<div class="gg-foot-bottom"><div class="gg-foot-bottom-in">
  <span>© {ano} {e(config.BRAND_NAME.title())}. Todos os direitos reservados.</span>
  <span>Links de afiliado — o preço para você é o mesmo. Preços coletados automaticamente
  e sujeitos a alteração; confira sempre na loja.</span>
</div></div>
</footer>
<button id="topo" aria-label="Voltar ao topo"><svg viewBox="0 0 24 24"><path d="M6 15l6-6 6 6"/></svg></button>
<div class="poll" id="poll"><button class="poll-x" id="poll-x" aria-label="Fechar">✕</button>
<div class="poll-q">Qual loja você prefere comprar?</div><div class="poll-opts" id="poll-opts"></div></div>
<div class="sugbg" id="sugbg"><div class="sugbox">
<button class="sug-x" id="sug-x" aria-label="Fechar">✕</button><h3>Sugerir produto</h3>
<p>A gente cadastra e passa a monitorar o histórico de preço pra você.</p>
<input id="sug-nome" placeholder="Nome do produto *"><input id="sug-link" placeholder="Link do produto *">
<div id="sug-erro"></div><button id="sug-enviar">Enviar sugestão</button></div></div>
<script>(function(){{var b=document.getElementById('topo');if(!b)return;
addEventListener('scroll',function(){{b.classList.toggle('on',scrollY>500);}},{{passive:true}});
b.addEventListener('click',function(){{scrollTo({{top:0,behavior:'smooth'}});}});}})();</script>
''' + _WIDGETS_JS + '''
</body></html>'''





def _lojatag(loja):
    nome, cor = LOJAS.get(loja, ("Loja", "#888"))
    return nome, cor


def card_html(d, base="", hot_forcado=False):
    p = d["p"]
    mini = spark(d["hist"], cor=GRAF[0] or _cor(config.COR_LINHA)) if TEMA == "claro" else ""
    de_html = f'<span class="de">{brl(d["de"])}</span>' if d["de"] else ""
    selo = f'<span class="selo">-{d["desc"]}%</span>' if d["desc"] else ""
    hot = " hot" if (hot_forcado or d.get("ehot")) else ""
    econ = (f'<span class="economia">Economize {brl(d["de"]-d["por"])}</span>'
            if d["de"] and d["de"] > d["por"] else "")
    sd = d.get("s") or {}
    flag = ""
    if sd.get("enough_history") and sd.get("is_lowest_window", 0) >= 30:
        flag = f'<span class="flag flag-menor">Menor preço em {sd["is_lowest_window"]}d</span>'
    elif d.get("queda", 0) > 0:
        flag = '<span class="flag flag-caiu">Caiu de preço</span>'
    return f"""<a class="card{hot}" href="{base}p/{p['id']}.html"
 data-titulo="{e((p.get('title') or '').lower())}" data-loja="{e(p.get('loja') or '')}"
 data-cat="{e(p.get('categoria') or '')}" data-plat="{e(' '.join(plataformas(p.get('title'))))}" data-preco="{d['por']}" data-desc="{d['desc']}" data-queda="{d.get('queda',0)}">
{selo}<span class="lojatag">{logo_loja(p.get('loja'))}</span>
<div class="foto"><img src="{e(p.get('thumbnail'))}" alt="{e(p.get('title'))}" loading="lazy"></div>
<div class="txt"><div class="tit">{e((p.get('title') or '')[:76])}</div>
{termo_html(d.get('termo'))}{mini}
<div class="linha-preco"><span class="por">{brl(d['por'])}</span>{de_html}</div>
{flag}{econ}
<span class="cat">{e(p.get('categoria') or '')}</span></div></a>"""


def gerar():
    database.init_db()
    produtos = database.get_products(only_active=True)
    if not produtos:
        print("Catálogo vazio. Rode antes: python sincronizar_lista.py --aplicar")
        return

    SAIDA.mkdir(exist_ok=True)
    (SAIDA / "p").mkdir(exist_ok=True)
    for _o in (SAIDA / "p").glob("*.html"): _o.unlink()
    if config.LOGO_PATH and Path(config.LOGO_PATH).exists():
        _preparar_logo(config.LOGO_PATH, str(SAIDA / "logo.png"))
    if (SAIDA / "logo.png").exists():
        _gerar_favicons(SAIDA / "logo.png", SAIDA, _cor(config.COR_BARRA))

    global _CATS
    _presentes = {p.get("categoria") or "Outros" for p in produtos}
    try:
        from bot import categorias as _cats_mod
        _ordem = [c.get("nome") for c in _cats_mod.carregar()]
    except Exception:
        _ordem = []
    _idx = {nome: i for i, nome in enumerate(_ordem)}
    # ordena pela posicao no categorias.json (o que o painel controla); resto vai ao fim, alfabetico
    _CATS = sorted(_presentes, key=lambda c: (_idx.get(c, 10_000), c))

    dados = []
    for p in produtos:
        hist = database.get_price_history(p["id"])
        if not hist:
            continue
        s = analytics.summarize(hist, windows=config.HISTORY_WINDOWS)
        de = hist[-1].get("original_price")
        por = hist[-1]["price"]
        desc = round((de - por) / de * 100) if de and de > por else 0
        trend = p.get("trend_score") or 0
        maisvend = 1 if p.get("mais_vendido") else 0
        posts = database.contar_posts(p["id"])
        # base = selo "mais vendido" da loja (sinal confiavel);
        # trend do Google complementa; posts entram como reforco leve
        relevancia = maisvend * 50 + trend * 0.5 + min(posts, 12) * 3
        dados.append({"p": p, "hist": hist, "s": s, "por": por, "de": de, "desc": desc,
                      "posts": posts, "trend": trend, "relevancia": relevancia,
                      "termo": termometro(hist, s), "queda": queda_recente(hist)})

    # marca as OFERTAS QUENTES uma vez (top por desconto) -> destaque em todo o site
    for d in sorted(dados, key=lambda x: -x["desc"]):
        if d["desc"] > 0:
            d["ehot"] = True
    for d in sorted([x for x in dados if x.get("ehot")], key=lambda x: -x["desc"])[8:]:
        d["ehot"] = False  # mantem no maximo 8 como "quentes"

    por_cat = {}
    for d in dados:
        por_cat.setdefault(d["p"].get("categoria") or "Outros", []).append(d)

    # ---------- paginas de produto ----------
    for d in dados:
        p, s = d["p"], d["s"]
        precos = [h["price"] for h in d["hist"]]
        nome_loja, cor = _lojatag(p.get("loja"))
        desc_html = ""
        if d['de'] and d['de'] > d['por']:
            desc_html = f'<div class="desc-tag">{d["desc"]}% de desconto · economize {brl(d["de"]-d["por"])}</div>'
        elif d['desc']:
            desc_html = f'<div class="desc-tag">{d["desc"]}% de desconto</div>'
        corpo = f"""<main><a class="voltar" href="../index.html">{_mini('seta')} Todas as ofertas</a>
<div class="prod">
<div class="foto"><img src="{e(p.get('thumbnail'))}" alt="{e(p.get('title'))}"></div>
<div>
  <h1>{e(p.get('title'))}</h1>
  <div class="chips">
    <span class="chip chip-loja">{logo_loja(p.get('loja'))}</span>
    <span class="chip">{e(p.get('categoria') or '')}</span>
    <span class="chip">Monitorado há {(s or {}).get('history_days', 0)} dia(s)</span>
  </div>
  {f'<div class="preco-de">{brl(d["de"])}</div>' if d['de'] else ''}
  <div class="preco-atual">{brl(d['por'])}</div>
  {desc_html}
  {termo_html(d.get('termo'), grande=True)}
  {_beneficios(p)}
  <a class="btn" href="{e(p.get('affiliate_url'))}" target="_blank" rel="nofollow noopener">
    Ver oferta na {e(nome_loja)} →</a>
</div></div>
{_hist_box(d)}
{_semelhantes(d, por_cat)}
</main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>{PRODUTO_JS}</script>"""
        ld = {"@context": "https://schema.org", "@type": "Product",
              "name": p.get("title"),
              "image": p.get("thumbnail") or "",
              "category": p.get("categoria") or "",
              "offers": {"@type": "Offer", "price": f"{d['por']:.2f}",
                         "priceCurrency": "BRL", "availability": "https://schema.org/InStock",
                         "url": f"{config.SITE_URL}/p/{p['id']}.html",
                         "seller": {"@type": "Organization",
                                    "name": LOJAS.get(p.get("loja"), ("Loja",))[0]}}}
        ldjson = ('<script type="application/ld+json">'
                  + json.dumps(ld, ensure_ascii=False) + '</script>')
        # banner de compartilhamento do produto (foto + preco no estilo da marca)
        og_prod, og_wide = (p.get("thumbnail") or ""), False
        try:
            from bot import og as _og
            _ogp = SAIDA / "og" / f"p-{p['id']}.png"
            _ogp.parent.mkdir(parents=True, exist_ok=True)
            _og.gerar_produto(str(_ogp), p.get("title") or "", d["por"], d.get("de"),
                              d.get("desc") or 0, p.get("loja") or "",
                              p.get("thumbnail") or "", brand=config.BRAND_NAME)
            og_prod, og_wide = f"{config.SITE_URL}/og/p-{p['id']}.png", True
        except Exception as _e:
            print(f"[og] produto {p['id']}: fallback ({_e})")
        pag = (cabecalho(f"{p.get('title')} por {brl(d['por'])} — {config.BRAND_NAME}",
                         f"Histórico de preço de {p.get('title')}. Saiba se {brl(d['por'])} "
                         f"é um bom preço antes de comprar.", base="../",
                         canonical=f"p/{p['id']}.html",
                         og_image=og_prod, og_dims=og_wide)
               + corpo + ldjson + _cta_telegram("../") + _rodape("../"))
        (SAIDA / "p" / f"{p['id']}.html").write_text(pag, encoding="utf-8")

    # ---------- home ----------
    lojas_presentes = [k for k in LOJAS if any(d["p"].get("loja") == k for d in dados)]
    abas = '<button class="on" data-loja="">Todas</button>'
    for k in lojas_presentes:
        nome, cor = LOJAS[k]
        abas += f'<button data-loja="{k}"><span class="pt" style="background:{cor}"></span>{nome}</button>'

    procurados = [d for d in sorted(dados, key=lambda x: -x["relevancia"]) if d["relevancia"] > 0][:4]
    quedas = sorted([x for x in dados if x["queda"] > 0], key=lambda x: -x["queda"])[:4]
    todos = sorted(dados, key=lambda x: -x["desc"])
    cats_h = sorted({d["p"].get("categoria") or "Outros" for d in dados})
    plats_h = [pl for pl in ["PS5", "PS4", "Xbox", "Switch", "PC"]
               if any(pl in plataformas(d["p"].get("title")) for d in dados)]
    def _grupo(titulo, campo, itens):
        ls = "".join(
            f'<label data-f="{campo}" data-v="{e(v)}">'
            f'<input type="checkbox" data-f="{campo}" value="{e(v)}">'
            f'<span class="nm">{e(rot)}</span><span class="cnt"></span></label>'
            for v, rot in itens)
        return f'<div class="fgrupo"><h4>{e(titulo)}</h4>{ls}</div>'
    sidebar = (
        '<button class="fechar" id="fechar">×</button>'
        + _grupo("Loja", "loja", [(k, LOJAS[k][0]) for k in lojas_presentes])
        + _grupo("Categoria", "cat", [(c, c) for c in cats_h])
        + (_grupo("Plataforma", "plat", [(p, p) for p in plats_h]) if plats_h else "")
        + '<div class="fgrupo"><h4>Faixa de preço</h4>'
          '<div class="precorow"><input id="pmin" type="number" placeholder="mín" min="0">'
          '<span>—</span><input id="pmax" type="number" placeholder="máx" min="0"></div>'
          '<button class="limpar" id="limpar">Limpar filtros</button></div>'
          '<button class="aplicar" id="aplicar">Ver <span id="nres">0</span> produtos</button>')
    faixas = ('<div class="faixas" id="faixas">'
              '<button class="on" data-min="0" data-max="0">Qualquer preço</button>'
              '<button data-min="0" data-max="100">Até R$100</button>'
              '<button data-min="100" data-max="300">R$100–300</button>'
              '<button data-min="300" data-max="800">R$300–800</button>'
              '<button data-min="800" data-max="2000">R$800–2mil</button>'
              '<button data-min="2000" data-max="0">Acima de R$2mil</button></div>')

    hots = [d for d in sorted(dados, key=lambda x: -x["desc"]) if d.get("ehot")]
    sec_hot = ""
    if hots:
        sec_hot = ('<div class="hotbox">' + _sechead(_sicon('hot'), 'Ofertas quentes', 'Os maiores descontos do momento') + '<div class="grid">'
                   + "".join(card_html(d, hot_forcado=True) for d in hots) + "</div></div>")
    sec_procurados = ""
    if procurados:
        sec_procurados = (_sechead(_sicon('star'), 'Mais procurados', 'Os produtos que mais divulgamos') + '<div class="grid">'
                          + "".join(card_html(d) for d in procurados) + "</div>")
    sec_quedas = ""
    if quedas:
        sec_quedas = (_sechead(_sicon('queda'), 'Maiores quedas recentes', 'Preços que caíram nos últimos 7 dias') + '<div class="grid">'
                      + "".join(card_html(d) for d in quedas) + "</div>")

    home = (cabecalho(f"{config.BRAND_NAME} — ofertas de games e tecnologia com histórico de preço",
                      "Ofertas de games, consoles, controles e tecnologia da Amazon, "
                      "Mercado Livre e AliExpress, com histórico de preço real.")
            + f"""<section class="hero">{_herobg([(d["p"]["id"], d["p"].get("thumbnail")) for d in todos])}
<h1>As melhores ofertas de <span>games e tech</span>,<br>com histórico de preço real</h1>
<p>Comparamos o preço todos os dias. Descubra se o desconto é de verdade antes de comprar.</p>
<div class="herostats"><span><b>{len(dados)}</b> ofertas monitoradas</span>
<span><b>{len(lojas_presentes)}</b> lojas</span>
<span>Preço conferido <b>todo dia</b></span></div>
<div class="busca-wrap"><input id="busca" type="search" placeholder="Buscar produto..." autocomplete="off"><div class="ac" id="ac"></div></div>
<div class="lojas">{abas}</div>
{faixas}
</section>
<main>
<button class="filtros-btn" id="filtrosbtn">{_mini('menu')} Filtros</button>
<div class="layout">
  <aside class="side" id="side">{sidebar}</aside>
  <div>
    <div id="destaques">{sec_hot}{sec_quedas}{sec_procurados}</div>
    <div class="sec-head" id="grade"><span class="ico">{_sicon('grid')}</span><div><h2 id="gradetit">Todas as ofertas</h2><p>Use os filtros ao lado para refinar</p></div><span class="rt"><span id="cont"></span></span></div>
    <div class="barrafiltro"><select id="ord">
      <option value="desc">Maior desconto</option>
      <option value="menor">Menor preço</option>
      <option value="maior">Maior preço</option>
      <option value="queda">Maior queda recente</option>
    </select></div>
    <div class="grid" id="grid">{''.join(card_html(d) for d in todos)}</div>
    <div class="vazio" id="vazio" style="display:none">Nenhum produto com esses filtros.</div>
  </div>
</div>
<div class="backdrop" id="bd"></div>
</main>
{_cta_telegram("")}
{prod_index(todos)}
<script>{JS}</script>""" + _rodape("", full=True))
    (SAIDA / "index.html").write_text(home, encoding="utf-8")

    # ---------- paginas por categoria ----------
    (SAIDA / "c").mkdir(exist_ok=True)
    for _o in (SAIDA / "c").glob("*.html"): _o.unlink()
    for cat, lst in por_cat.items():
        lst = sorted(lst, key=lambda x: -x["desc"])
        cats_all = sorted(por_cat)
        nav = '<div class="catnav"><a href="../index.html">Tudo</a>' + "".join(
            f'<a class="{"on" if c==cat else ""}" href="{cat_slug(c)}.html">{e(c)}</a>'
            for c in cats_all) + '</div>'
        corpo = (f'<section class="hero">' + _herobg([(d['p']['id'], d['p'].get('thumbnail')) for d in lst], base='../') +
                 f'<h1>{e(cat)} <span>em oferta</span></h1>'
                 f'<p>Ofertas de {e(cat.lower())} com histórico de preço real.</p>'
                 f'<div class="busca-wrap"><input id="busca" type="search" '
                 f'placeholder="Buscar em {e(cat.lower())}..." autocomplete="off">'
                 f'<div class="ac" id="ac"></div></div></section>'
                 '<main>' + _sechead(_sicon('grid'), f'{cat} em oferta', 'Ordenadas pelo maior desconto', tag='<span id="cont"></span>', hid='grade') +
                 f'<div class="grid" id="grid">'
                 + "".join(card_html(d, base="../") for d in lst)
                 + '<div class="vazio" id="vazio" style="display:none">Nada encontrado.</div>'
                 + f'</div></main>{prod_index(lst, base="../")}<script>{JS}</script>')
        pag = (cabecalho(f"{cat} em oferta — {config.BRAND_NAME}",
                         f"Ofertas de {cat.lower()} com histórico de preço. "
                         f"Games e tecnologia com desconto verificado.",
                         base="../", canonical=f"c/{cat_slug(cat)}.html", cat_atual=cat,
                         og_image=f"{config.SITE_URL}/og/cat-{cat_slug(cat)}.png")
               + corpo + _cta_telegram("../") + _rodape("../"))
        (SAIDA / "c" / f"{cat_slug(cat)}.html").write_text(pag, encoding="utf-8")

    # ---------- banners de compartilhamento (Open Graph) ----------
    try:
        from bot import og as _og
        _og.gerar_todos(str(SAIDA / "og"), list(por_cat.keys()), cat_slug, brand=config.BRAND_NAME)
        print(f"[og] {1 + len(por_cat)} banner(s) de compartilhamento gerados")
    except Exception as _e:
        print(f"[og] aviso: nao gerou banners ({_e})")

    # ---------- links ----------
    redes = [("Canal no Telegram", config.CHANNEL_INVITE, "telegram"),
             ("Canal no WhatsApp", config.WHATSAPP, "whatsapp"),
             ("Instagram", config.INSTAGRAM, "instagram"),
             ("TikTok", config.TIKTOK, "tiktok"),
             ("YouTube", config.YOUTUBE, "youtube")]
    botoes = "".join(
        f'<a class="card in rede" href="{e(u)}" target="_blank">{_mini(ic)}'
        f'<b>{e(n)}</b></a>' for n, u, ic in redes if u)
    pag = (cabecalho(f"Redes — {config.BRAND_NAME}", "Todos os nossos canais")
           + f'<main><section class="hero" style="padding-bottom:10px"><h1>Nossos canais</h1>'
             f'<p>Ofertas todos os dias, onde você preferir.</p></section>'
             f'<div class="grid">{botoes}</div></main>' + _rodape(''))
    (SAIDA / "links.html").write_text(pag, encoding="utf-8")

    # ---------- SEO ----------
    hoje = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [config.SITE_URL + "/", config.SITE_URL + "/links.html"]
    urls += [f"{config.SITE_URL}/p/{d['p']['id']}.html" for d in dados]
    urls += [f"{config.SITE_URL}/c/{cat_slug(c)}.html" for c in por_cat]
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{u}</loc><lastmod>{hoje}</lastmod></url>\n" for u in urls)
          + "</urlset>\n")
    (SAIDA / "sitemap.xml").write_text(sm, encoding="utf-8")
    (SAIDA / "responsivo.html").write_text("""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="utf-8"><title>Teste responsivo</title><style>
body{margin:0;background:#1a1d21;font-family:system-ui;color:#eee;padding:22px}
.telas{display:flex;gap:26px;align-items:flex-start;overflow-x:auto}
.rot{font-size:12px;color:#9aa0a6;margin-bottom:8px}
.m{background:#000;border-radius:20px;padding:10px}
iframe{border:0;border-radius:10px;background:#fff;display:block}
</style></head><body><h3 style="font-weight:600">Pré-visualização — 3 larguras</h3>
<div class="telas">
<div><div class="rot">Celular · 375px</div><div class="m"><iframe src="index.html" width="375" height="700"></iframe></div></div>
<div><div class="rot">Tablet · 768px</div><div class="m"><iframe src="index.html" width="768" height="700"></iframe></div></div>
<div><div class="rot">Desktop · 1280px</div><div class="m"><iframe src="index.html" width="1280" height="700"></iframe></div></div>
</div></body></html>""", encoding="utf-8")

    (SAIDA / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {config.SITE_URL}/sitemap.xml\n", encoding="utf-8")

    print(f"Site gerado em '{SAIDA}/'")
    print(f"  {len(dados)} produto(s) | lojas: {', '.join(LOJAS[k][0] for k in lojas_presentes)}")
    print("\nAbra site/index.html no navegador para testar.")


if __name__ == "__main__":
    gerar()

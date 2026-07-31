#!/usr/bin/env python3
"""Mostra qual link de afiliado cada produto esta usando.

    python links.py            -> resumo por tipo de link
    python links.py --todos    -> lista produto por produto
"""
import sys
from bot import database


def tipo(url):
    u = (url or "")
    if "meli.la" in u:
        return "meli.la (oficial - rastreio garantido)"
    if "matt_word=" in u and "matt_tool=" in u:
        return "montado (matt_word+matt_tool) - NAO CONFIRMADO"
    if "tag=" in u:
        return "amazon (tag)"
    if not u:
        return "SEM LINK DE AFILIADO"
    # matt_event_ts sozinho NAO identifica afiliado, e so um carimbo de tempo
    return "SEM RASTREIO DE AFILIADO"


if __name__ == "__main__":
    database.init_db()
    prods = database.get_products(only_active=False)
    resumo = {}
    for p in prods:
        resumo[tipo(p.get("affiliate_url"))] = resumo.get(tipo(p.get("affiliate_url")), 0) + 1

    print("RESUMO DOS LINKS:")
    for k, v in sorted(resumo.items(), key=lambda x: -x[1]):
        print(f"  {v:>3} produto(s)  ->  {k}")

    if "--todos" in sys.argv:
        print("\nDETALHE:")
        for p in prods:
            print(f"\n  {p['id']}  [{tipo(p.get('affiliate_url'))}]")
            print(f"    {(p.get('title') or '')[:60]}")
            print(f"    {(p.get('affiliate_url') or '-')[:110]}")

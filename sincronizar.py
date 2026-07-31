#!/usr/bin/env python3
"""Sincroniza o catalogo a partir do arquivo meus_links.txt.

Voce gera os links no painel de afiliados e cola no arquivo. O bot le, cadastra
os produtos novos com o LINK REAL de afiliado, atualiza precos e joga na fila.

    python sincronizar.py            -> mostra o que faria (nao grava)
    python sincronizar.py --aplicar  -> cadastra/atualiza de verdade
"""
import re
import sys
from pathlib import Path

from bot import database, lojas, categorias

ARQ = Path(__file__).resolve().parent / "meus_links.txt"
RE_URL = re.compile(r"https?://\S+")


def ler_arquivo():
    """Devolve lista de (url_produto, link_afiliado, cupom)."""
    if not ARQ.exists():
        print(f"Arquivo nao encontrado: {ARQ}")
        return []
    linhas = []
    for bruto in ARQ.read_text(encoding="utf-8").splitlines():
        linha = bruto.strip()
        if not linha or linha.startswith("#"):
            continue
        partes = [p.strip() for p in linha.split("|")]
        urls = [p for p in partes if RE_URL.fullmatch(p or "")]
        cupom = next((p for p in partes if p and not RE_URL.fullmatch(p)), None)
        if not urls:
            print(f"  [ignorado] sem URL: {linha[:60]}")
            continue
        produto = urls[0]
        afiliado = urls[1] if len(urls) > 1 else None
        linhas.append((produto, afiliado, cupom))
    return linhas


def sincronizar(aplicar=False):
    database.init_db()
    print("AVISO: este fluxo abre a pagina de cada produto e pode ser bloqueada pelo ML.")
    print("       Prefira: python sincronizar_lista.py --aplicar (le a sua lista, 1 pagina)\n")
    itens = ler_arquivo()
    if not itens:
        print("Nada para sincronizar. Cole seus links em meus_links.txt")
        return

    existentes = {p["id"] for p in database.get_products(only_active=False)}
    novos = atualizados = falhas = 0
    print(f"Lendo {len(itens)} linha(s) do arquivo...\n")

    for url_prod, url_afil, cupom in itens:
        loja = lojas.detectar(url_prod)
        if not loja or not loja.ativa:
            print(f"  [erro] loja nao suportada: {url_prod[:60]}")
            falhas += 1
            continue

        if not url_afil:
            print(f"  [aviso] sem link de afiliado (vai postar sem comissao): {url_prod[:56]}")

        data = loja.ler_produto(url_prod)
        if data.get("error") or data.get("price") is None:
            print(f"  [erro] nao li o preco: {url_prod[:56]} ({data.get('error')})")
            falhas += 1
            continue

        cat = categorias.classificar(data.get("title"))["nome"]
        marca = "NOVO" if data["id"] not in existentes else "atualizado"
        print(f"  [{marca:<10}] {data['id']:<15} R$ {data['price']:<10} "
              f"[{cat:<16}] {(data.get('title') or '')[:38]}")

        if aplicar:
            database.add_product({
                "id": data["id"], "title": data["title"],
                "permalink": data["permalink"], "thumbnail": data["thumbnail"],
                "affiliate_url": url_afil or data["permalink"],
                "coupon_code": cupom, "coupon_note": None,
                "categoria": cat, "loja": loja.nome,
            })
            database.record_price(data["id"], data["price"], data.get("original_price"))
        if data["id"] in existentes:
            atualizados += 1
        else:
            novos += 1

    print(f"\nResumo: {novos} novo(s) | {atualizados} atualizado(s) | {falhas} falha(s)")
    if not aplicar:
        print("(simulacao - rode com --aplicar para gravar)")


if __name__ == "__main__":
    sincronizar(aplicar="--aplicar" in sys.argv)

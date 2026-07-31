#!/usr/bin/env python3
"""Cadastra um produto lendo a pagina via navegador (Playwright).

Uso:
    python add_produto.py "https://meli.la/xxxxx"
    python add_produto.py "https://meli.la/xxxxx" --cupom GAMER10 --nota "min R$100"
    python add_produto.py "https://meli.la/xxxxx" --link "https://link-de-afiliado-do-produto"

O link informado e salvo como link de afiliado (para postar e ganhar comissao).
A leitura de preco usa a pagina oficial do produto.
"""
import sys
from bot import database
from bot import lojas


def main():
    if len(sys.argv) < 2:
        print("Informe o link do anuncio.")
        return
    entrada = sys.argv[1]
    print("AVISO: o Mercado Livre costuma bloquear a leitura de pagina de produto.")
    print("       O fluxo recomendado e adicionar na sua lista de afiliado e rodar:")
    print("       python sincronizar_lista.py --aplicar")
    print()
    args = sys.argv[2:]

    def opt(flag):
        return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else None

    loja = lojas.detectar(entrada)
    if not loja:
        print("Nao reconheci a loja desse link."); return
    if not loja.ativa:
        print(f"A loja {loja.rotulo} ainda nao esta configurada."); return
    print(f"Loja: {loja.rotulo}. Lendo o produto...")
    data = loja.ler_produto(entrada)
    if data.get("error") or data.get("price") is None:
        print("Nao consegui ler o preco:", data.get("error"))
        print("  id:", data.get("id"), "| titulo:", data.get("title"))
        return

    database.init_db()
    product = {
        "id": data["id"],
        "title": data["title"],
        "permalink": data["permalink"],          # pagina oficial (para reler o preco)
        "thumbnail": data["thumbnail"],
        "affiliate_url": opt("--link") or loja.link_afiliado(data.get("permalink") or entrada),
        "loja": loja.nome,  # link que ganha comissao (para postar)
        "coupon_code": opt("--cupom"),
        "coupon_note": opt("--nota"),
    }
    database.add_product(product)
    database.record_price(data["id"], data["price"], data.get("original_price"))
    print(f"OK! Cadastrado: {data['title']}")
    print(f"    ID: {data['id']}  |  Preco de hoje: R$ {data['price']}")
    print(f"    Link de afiliado salvo: {product['affiliate_url'][:60]}...")


if __name__ == "__main__":
    main()

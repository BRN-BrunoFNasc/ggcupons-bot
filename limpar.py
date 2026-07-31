#!/usr/bin/env python3
"""Limpa o catalogo para recomecar do zero.

    python limpar.py                 -> mostra o que existe hoje (nao apaga)
    python limpar.py --produtos      -> apaga produtos + historico de precos
    python limpar.py --tudo          -> apaga produtos, historico, log de posts e cupons
    python limpar.py --tudo --manter-cupons

Os arquivos (categorias.json, .env, template, logo) NAO sao tocados.
"""
import sys
from bot import database


def resumo():
    con = database._conn()
    def n(t):
        try:
            return con.execute(f"SELECT COUNT(*) c FROM {t}").fetchone()["c"]
        except Exception:
            return 0
    dados = {t: n(t) for t in ("products", "price_history", "posts_log", "coupons")}
    con.close()
    return dados


def main():
    database.init_db()
    antes = resumo()
    print("SITUACAO ATUAL:")
    for k, v in antes.items():
        print(f"  {k:<16} {v}")

    if "--produtos" not in sys.argv and "--tudo" not in sys.argv:
        print("\nNada foi apagado. Use --produtos ou --tudo para limpar.")
        return

    con = database._conn()
    con.execute("DELETE FROM price_history")
    con.execute("DELETE FROM products")
    if "--tudo" in sys.argv:
        con.execute("DELETE FROM posts_log")
        if "--manter-cupons" not in sys.argv:
            con.execute("DELETE FROM coupons")
    con.execute("DELETE FROM estado WHERE chave='rodizio_pos'")
    con.commit(); con.close()

    print("\nLIMPO. Situacao agora:")
    for k, v in resumo().items():
        print(f"  {k:<16} {v}")
    print("\nProximo passo: adicione produtos a sua lista de afiliado e rode")
    print('  python sincronizar_lista.py "https://meli.la/SUA_LISTA" --aplicar')


if __name__ == "__main__":
    main()

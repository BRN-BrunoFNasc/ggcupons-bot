#!/usr/bin/env python3
"""Remove ou pausa produtos do catalogo.

    python remover.py MLB54963150            -> pausa (nao posta mais, mantem historico)
    python remover.py MLB54963150 --apagar   -> apaga de vez
    python remover.py --duplicados           -> mostra produtos com titulo parecido
    python remover.py --categoria MLB123 Jogos  -> corrige a categoria de um produto
"""
import sys
from bot import database


def _con():
    return database._conn()


def pausar(pid, apagar=False):
    con = _con()
    if apagar:
        con.execute("DELETE FROM price_history WHERE product_id=?", (pid,))
        con.execute("DELETE FROM products WHERE id=?", (pid,))
        print("Apagado:", pid)
    else:
        con.execute("UPDATE products SET active=0 WHERE id=?", (pid,))
        print("Pausado (nao sera mais postado):", pid)
    con.commit(); con.close()


def set_categoria(pid, cat):
    con = _con()
    con.execute("UPDATE products SET categoria=? WHERE id=?", (cat, pid))
    con.commit(); con.close()
    print(f"{pid} -> categoria '{cat}'")


def duplicados():
    from bot.descoberta import _chave_titulo
    grupos = {}
    for p in database.get_products(only_active=False):
        grupos.setdefault(_chave_titulo(p.get("title")), []).append(p)
    achou = False
    for k, itens in grupos.items():
        if len(itens) > 1:
            achou = True
            print(f"\nParecidos ({len(itens)}):")
            for p in itens:
                print(f"   {p['id']:<16} {(p.get('title') or '')[:60]}")
    if not achou:
        print("Nenhum duplicado encontrado.")


if __name__ == "__main__":
    database.init_db()
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == "--duplicados":
        duplicados()
    elif a[0] == "--categoria" and len(a) >= 3:
        set_categoria(a[1], a[2])
    else:
        pausar(a[0], "--apagar" in a)

#!/usr/bin/env python3
"""Mostra o catalogo: nivel, frequencia, ultimo post e se esta liberado."""
from bot import database, fila

if __name__ == "__main__":
    database.init_db()
    itens = fila.listar_status()
    if not itens:
        print("Nenhum produto cadastrado."); raise SystemExit
    print(f"{'ID':<16}{'LOJA':<14}{'CATEGORIA':<18}{'NIVEL':<16}{'FREQ':<9}{'DESC':<6}{'PRECO':<11}{'LIB':<5}TITULO")
    print("-" * 124)
    for i in sorted(itens, key=lambda x: -x["prioridade"]):
        freq = f"{i['cooldown_min']}min"
        lib = "SIM" if i["liberado"] else "nao"
        print(f"{i['id']:<16}{(i.get('loja') or '-'):<14}{(i.get('categoria') or '-'):<18}{i['tier']:<16}{freq:<9}"
              f"{str(i['desconto'])+'%':<6}{('R$ '+str(i['preco'])):<11}{lib:<5}{(i['title'] or '')[:34]}")
    print(f"\nTotal: {len(itens)} produto(s) | posts ja feitos: {database.contar_posts()}")

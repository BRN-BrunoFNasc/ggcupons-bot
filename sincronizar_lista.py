#!/usr/bin/env python3
"""Sincroniza o catalogo com a SUA LISTA de afiliado do Mercado Livre.

Le a pagina publica da lista (que o ML nao bloqueia) e cadastra/atualiza todos
os produtos de uma vez: preco, preco 'de', parcelas, frete e foto.

    python sincronizar_lista.py "https://meli.la/2byuhxD"
    python sincronizar_lista.py "https://meli.la/2byuhxD" --aplicar
    python sincronizar_lista.py --aplicar          (usa ML_LISTA_URL do .env)
"""
import sys

from bot import lista_ml, database, categorias, config
from bot.link_ml import montar


def sincronizar(url_lista, aplicar=False, headless=True, verbose=True):
    itens = lista_ml.ler(url_lista, headless=headless, verbose=verbose)
    if not itens:
        print("Nada lido. A lista pode estar vazia ou o ML bloqueou.")
        return 0

    database.init_db()
    existentes = {p["id"]: p for p in database.get_products(only_active=False)}
    novos = atualizados = 0

    print(f"\n{'':<10}{'ID':<15}{'PRECO':>11}{'DE':>11}  {'CATEGORIA':<17}TITULO")
    print("-" * 104)

    for i in itens:
        cat = categorias.classificar(i["titulo"])["nome"]
        marca = "NOVO" if i["id"] not in existentes else "atualiza"
        print(f"{marca:<10}{i['id']:<15}"
              f"{('R$ '+format(i['por'],'.2f')):>11}"
              f"{('R$ '+format(i['de'],'.2f')) if i.get('de') else '-':>11}  "
              f"{cat:<17}{(i['titulo'] or '')[:38]}")

        if not aplicar:
            continue

        # link de afiliado: preferencia pela estrategia configurada
        link = montar(i["href"])
        dados = {
            "id": i["id"], "title": i["titulo"], "permalink": i["href"],
            "thumbnail": i.get("img") or (existentes.get(i["id"], {}) or {}).get("thumbnail"),
            "affiliate_url": link, "coupon_code": None, "coupon_note": None,
            "categoria": cat, "loja": "mercadolivre",
        }
        database.add_product(dados)
        database.atualizar_dados(i["id"], {
            "parcelas": i.get("parcelas"),
            "frete": 1 if i.get("frete") else 0,
            "pagamento": "no PIX" if i.get("pix") else None,
            "thumbnail": i.get("img") or None,
        })
        if i.get("mais"):
            con2 = database._conn()
            con2.execute("UPDATE products SET mais_vendido=1 WHERE id=?", (i["id"],))
            con2.commit(); con2.close()
        database.record_price(i["id"], i["por"], i.get("de"))
        if i["id"] in existentes:
            atualizados += 1
        else:
            novos += 1

    if aplicar:
        print(f"\n{novos} novo(s), {atualizados} atualizado(s).")
    else:
        print(f"\n(simulacao — use --aplicar para gravar)")
    return novos + atualizados


if __name__ == "__main__":
    url = next((a for a in sys.argv[1:] if a.startswith("http")), config.ML_LISTA_URL)
    if not url:
        print('Informe a URL: python sincronizar_lista.py "https://meli.la/..."')
        print("ou defina ML_LISTA_URL no .env")
        sys.exit()
    sincronizar(url, aplicar="--aplicar" in sys.argv, headless="--ver" not in sys.argv)

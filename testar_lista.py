#!/usr/bin/env python3
"""Testa a leitura estruturada da sua lista de afiliado.

    python testar_lista.py "https://meli.la/2byuhxD"
    python testar_lista.py "https://meli.la/2byuhxD" --ver
"""
import sys
sys.path.insert(0, ".")
from bot import lista_ml, config

url = next((a for a in sys.argv[1:] if a.startswith("http")), config.ML_LISTA_URL)
if not url:
    print('Informe a URL da lista.'); sys.exit()

itens = lista_ml.ler(url, headless="--ver" not in sys.argv)
if not itens:
    print("Nada lido (bloqueado ou lista vazia)."); sys.exit()

print(f"\n{'ID':<15}{'PRECO':>11}{'DE':>11}{'OFF':>6}  {'PARCELAS':<22}FRETE  TITULO")
print("-" * 118)
for i in itens:
    print(f"{i['id']:<15}"
          f"{('R$ '+format(i['por'],'.2f')):>11}"
          f"{('R$ '+format(i['de'],'.2f')) if i.get('de') else '-':>11}"
          f"{(str(i['desconto'])+'%') if i['desconto'] else '-':>6}  "
          f"{(i.get('parcelas') or '-'):<22}"
          f"{'sim' if i.get('frete') else '-':<7}"
          f"{(i.get('titulo') or '')[:40]}")
print(f"\n{len(itens)} produto(s). Imagens: "
      f"{sum(1 for i in itens if i.get('img'))} com foto.")

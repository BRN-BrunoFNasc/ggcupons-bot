#!/usr/bin/env python3
"""Testa se este ambiente (ex.: GitHub Actions) consegue LER uma pagina de
produto da Amazon. So imprime o resultado - nao grava nada, nao posta.

Uso: python testar_amazon.py "https://www.amazon.com.br/.../dp/ASIN"
"""
import sys

from bot.lojas.amazon import Amazon

url = sys.argv[1] if len(sys.argv) > 1 else "https://www.amazon.com.br/dp/B0GGLJCJQM"

print("=" * 60)
print("Testando leitura da Amazon a partir DESTE ambiente")
print("URL:", url)
print("=" * 60)

r = Amazon().ler_produto(url)

if r.get("error"):
    print("\n>>> RESULTADO: A Amazon NAO deixou ler daqui.")
    print("    Motivo:", r["error"])
    if r.get("amostra"):
        print("    Amostra da pagina:", repr(r["amostra"]))
    print("\n    -> Conclusao: leitura automatica da Amazon NAO e confiavel aqui.")
    print("       Melhor manter o preco manual + 'Em construcao'.")
else:
    print("\n>>> RESULTADO: LEU COM SUCESSO! 🎉")
    print("    Titulo :", r.get("title"))
    print("    Preco  :", r.get("price"))
    print("    De     :", r.get("original_price"))
    print("    Imagem :", (r.get("thumbnail") or "")[:80])
    print("\n    -> Conclusao: da pra ligar o monitoramento automatico da Amazon.")

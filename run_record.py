#!/usr/bin/env python3
"""Grava os precos do dia usando o VIGIA (le a sua lista de afiliado - 1 pagina).

Substitui o metodo antigo de abrir a pagina de cada produto (que o Mercado
Livre bloqueia). Rode 1x/dia ou deixe o run_loop cuidar disso.
"""
from bot import vigia

if __name__ == "__main__":
    vigia.varrer(cadastrar_novos=False)

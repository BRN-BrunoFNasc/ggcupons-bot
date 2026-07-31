#!/usr/bin/env python3
"""Descobre ofertas no Mercado Livre automaticamente.

    python descobrir.py               -> so mostra o que achou (nao cadastra)
    python descobrir.py --cadastrar   -> cadastra os novos no catalogo
    python descobrir.py --ver         -> com navegador visivel (debug)
"""
import sys
from bot import descoberta

if __name__ == "__main__":
    descoberta.rodar(cadastrar_novos="--cadastrar" in sys.argv,
                     headless="--ver" not in sys.argv)

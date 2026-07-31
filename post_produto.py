#!/usr/bin/env python3
"""Posta (ou previa) um produto especifico, com card visual + texto.

Uso:
    python post_produto.py MLB54963150            -> previa (mostra o texto e gera o card)
    python post_produto.py MLB54963150 --publicar -> posta no canal
    python post_produto.py MLB54963150 --ver      -> abre o navegador (depuracao)
"""
import sys
from bot import tracker

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Informe o ID do produto (ex.: MLB54963150)")
        sys.exit()
    pid = sys.argv[1]
    publicar = "--publicar" in sys.argv
    tracker.postar_um(pid, dry_run=not publicar, ver="--ver" in sys.argv)
    if not publicar:
        print("\n(previa - veja o card gerado em data/cards/. Use --publicar para postar)")

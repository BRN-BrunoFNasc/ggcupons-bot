#!/usr/bin/env python3
"""Posta as boas ofertas no canal do Telegram.

Uso:
    python3 run_post.py            -> previa (nao posta)
    python3 run_post.py --publicar -> posta de verdade no canal
"""
import sys
from bot.tracker import find_and_post_deals

if __name__ == "__main__":
    dry = "--publicar" not in sys.argv
    n = find_and_post_deals(dry_run=dry)
    if dry:
        print("\n(previa - nada foi postado. use --publicar para postar)")
    else:
        print(f"{n} oferta(s) postada(s).")

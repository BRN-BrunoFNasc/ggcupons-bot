#!/usr/bin/env python3
"""Define de quanto em quanto tempo um produto pode ser postado.

Uso:
    python frequencia.py MLB54963150 15      -> a cada 15 minutos
    python frequencia.py MLB54963150 1440    -> 1x por dia
    python frequencia.py MLB54963150 auto    -> volta ao padrao do nivel
"""
import sys
from bot import database

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python frequencia.py MLB123 <minutos|auto>"); sys.exit()
    pid, val = sys.argv[1], sys.argv[2].lower()
    database.init_db()
    database.set_cooldown(pid, None if val == "auto" else int(val))
    print(f"OK: {pid} -> {'padrao do nivel' if val=='auto' else val + ' min'}")

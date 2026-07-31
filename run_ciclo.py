#!/usr/bin/env python3
"""Executa UM ciclo: escolhe o proximo produto liberado e posta.

    python run_ciclo.py             -> previa (nao posta)
    python run_ciclo.py --publicar  -> posta no canal
"""
import sys
from bot import ciclo

if __name__ == "__main__":
    ciclo.executar(publicar="--publicar" in sys.argv)

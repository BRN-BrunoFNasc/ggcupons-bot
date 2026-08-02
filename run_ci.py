#!/usr/bin/env python3
"""Entrypoint do agendamento (GitHub Actions).

Modos:
  python run_ci.py --vigia      -> so le precos + cadastra novos produtos da lista
  python run_ci.py --postar     -> so posta 1 oferta no Telegram (usa preco do banco)
  python run_ci.py --publicar   -> faz os dois e publica (comportamento antigo)
  python run_ci.py              -> faz os dois em modo preview (nao posta)
"""
import sys
from bot import vigia, ciclo

args = sys.argv[1:]
modo_vigia = ("--vigia" in args) or ("--postar" not in args)
modo_postar = ("--postar" in args) or ("--vigia" not in args)
publicar = ("--publicar" in args) or ("--postar" in args)

if modo_vigia:
    try:
        vigia.varrer(cadastrar_novos=True)
    except Exception as e:
        print("[aviso] vigia falhou:", e)

if modo_postar:
    ciclo.executar(publicar=publicar)

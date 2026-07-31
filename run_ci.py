#!/usr/bin/env python3
"""Um ciclo completo para o agendamento (GitHub Actions):
grava precos + cadastra novos produtos da lista, e posta a proxima oferta.
Uso: python run_ci.py --publicar
"""
import sys
from bot import vigia, ciclo

publicar = "--publicar" in sys.argv
try:
    vigia.varrer(cadastrar_novos=True)
except Exception as e:
    print("[aviso] vigia falhou:", e)
ciclo.executar(publicar=publicar)

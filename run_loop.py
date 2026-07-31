#!/usr/bin/env python3
"""Roda 24h: vigia os precos e posta em rodizio entre as categorias.

    python run_loop.py --publicar
    python run_loop.py                (previa, nao posta)
Pare com Ctrl+C.
"""
import sys, time
from datetime import datetime

from bot import config, ciclo, vigia

if __name__ == "__main__":
    publicar = "--publicar" in sys.argv
    print(f"Loop iniciado {datetime.now():%H:%M}. "
          f"Post a cada {config.CICLO_MIN}min | vigia a cada {config.VIGIA_INTERVALO_MIN}min | "
          f"{'PUBLICANDO' if publicar else 'PREVIA'}")
    ultima_vigia = 0
    try:
        while True:
            agora = time.time()
            # 1) vigia de precos (detecta quedas e cadastra novidades)
            if agora - ultima_vigia >= config.VIGIA_INTERVALO_MIN * 60:
                try:
                    print(f"\n[{datetime.now():%H:%M}] varrendo precos...")
                    vigia.varrer(verbose=True)
                except Exception as e:
                    print("[erro vigia]", e)
                ultima_vigia = agora
            # 2) posta o proximo da fila
            try:
                print(f"[{datetime.now():%H:%M}] ciclo de postagem")
                ciclo.executar(publicar=publicar)
            except Exception as e:
                print("[erro ciclo]", e)
            time.sleep(config.CICLO_MIN * 60)
    except KeyboardInterrupt:
        print("\nLoop encerrado.")

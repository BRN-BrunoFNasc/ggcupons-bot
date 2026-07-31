"""Controle de ritmo de acesso: pausas humanas e limite diario de paginas.

Acessar rapido e sempre no mesmo intervalo e o que denuncia um robo. Aqui as
pausas sao sorteadas e ha um teto diario, para o bot nao se queimar.
"""
import random
import time
from datetime import date

from bot import config, database

_ultimo = [0.0]


def _hoje():
    return date.today().isoformat()


def paginas_hoje():
    try:
        d = database.estado_get("paginas_data", "")
        n = int(database.estado_get("paginas_qtd", "0") or 0)
        return n if d == _hoje() else 0
    except Exception:
        return 0


def _registrar():
    try:
        if database.estado_get("paginas_data", "") != _hoje():
            database.estado_set("paginas_data", _hoje())
            database.estado_set("paginas_qtd", 1)
        else:
            database.estado_set("paginas_qtd", paginas_hoje() + 1)
    except Exception:
        pass


def pode_acessar():
    """False se ja bateu o teto diario."""
    return paginas_hoje() < config.LIMITE_DIARIO_PAGINAS


def aguardar():
    """Espera um intervalo humano desde o ultimo acesso, e contabiliza."""
    espera = random.uniform(config.PAUSA_MIN_SEG, config.PAUSA_MAX_SEG)
    passou = time.time() - _ultimo[0]
    if passou < espera:
        time.sleep(espera - passou)
    _ultimo[0] = time.time()
    _registrar()


def resumo():
    return f"{paginas_hoje()}/{config.LIMITE_DIARIO_PAGINAS} paginas hoje"

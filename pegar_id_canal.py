#!/usr/bin/env python3
"""Descobre o ID numerico de um canal do Telegram (util ao criar um canal novo).

Antes de rodar:
 1. O bot precisa ser ADMINISTRADOR do canal.
 2. Poste qualquer mensagem no canal (o bot so enxerga o canal depois disso).

    python pegar_id_canal.py
"""
import sys

import requests

sys.path.insert(0, ".")
from bot import config


def main():
    if not config.TELEGRAM_BOT_TOKEN:
        print("Defina TELEGRAM_BOT_TOKEN no .env")
        return
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/getUpdates"
    try:
        r = requests.get(url, timeout=20).json()
    except Exception as e:
        print("Erro ao consultar o Telegram:", e)
        return

    achou = False
    for up in r.get("result", []):
        chat = (up.get("channel_post") or up.get("my_chat_member") or {}).get("chat") or {}
        if chat.get("type") == "channel":
            achou = True
            print(f"Canal: {chat.get('title')}  ->  ID: {chat.get('id')}")

    if not achou:
        print("Nao encontrei nenhum canal nas atualizacoes.")
        print("Confira: (1) o bot e ADMIN do canal? (2) voce postou uma mensagem agora?")


if __name__ == "__main__":
    main()

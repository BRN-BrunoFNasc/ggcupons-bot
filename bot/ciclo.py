"""Um ciclo de postagem: escolhe o proximo da fila, le, monta e posta."""
from datetime import datetime

from bot import config, database, fila, tracker


def executar(publicar=False, verbose=True):
    database.init_db()

    if config.PAUSA_MADRUGADA and 0 <= datetime.now().hour < 6:
        if verbose:
            print("[pausa] madrugada — nada postado")
        return None

    item = fila.proximo()
    if not item:
        if verbose:
            print("[fila] nenhum produto liberado agora (todos em descanso)")
        return None

    if verbose:
        print(f"[fila] {item['id']} | {item.get('categoria','?')} | {item['tier']} | "
              f"{item.get('motivo','')}")

    pack = tracker._preparar(item)   # le o preco agora, grava historico, monta card + texto
    if not pack:
        if verbose:
            print(f"[erro] nao consegui ler {item['id']}")
        return None

    # reclassifica com o preco recem-lido (o nivel pode ter mudado)
    novo = fila.classificar(item) or item
    tier = novo["tier"]
    if item.get("urgente"):
        tier = "MENOR_PRECO" if tier == "MENOR_PRECO" else "DESCONTO_FORTE"
    caption = tracker.montar_caption(pack["info"], tier)

    if not publicar:
        print("=" * 46)
        print("NIVEL:", tier, "| CARD:", pack["card"])
        print(caption)
        return {"item": item, "tier": tier, "preview": True}

    from bot import telegram_bot
    telegram_bot.send_photo_file(pack["card"], caption)
    database.marcar_postado(item["id"], tier, pack["info"].get("por"))
    database.limpar_urgente(item["id"])
    if verbose:
        print(f"[postado] {item['id']} ({tier})")
    return {"item": item, "tier": tier, "preview": False}

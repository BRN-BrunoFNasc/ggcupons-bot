"""Envio de mensagens para o canal do Telegram via Bot API."""
import requests

from bot import config

API = "https://api.telegram.org"


def _base():
    return f"{API}/bot{config.TELEGRAM_BOT_TOKEN}"


def send_message(text, chat_id=None, disable_preview=False):
    chat_id = chat_id or config.TELEGRAM_CHANNEL_ID
    resp = requests.post(
        f"{_base()}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": disable_preview,
        },
        timeout=20,
    )
    if not resp.ok:
        raise requests.HTTPError(f"Telegram {resp.status_code}: {resp.text[:500]}")
    return resp.json()


def send_photo(photo_url, caption, chat_id=None):
    chat_id = chat_id or config.TELEGRAM_CHANNEL_ID
    resp = requests.post(
        f"{_base()}/sendPhoto",
        json={
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": "HTML",
        },
        timeout=20,
    )
    if not resp.ok:
        raise requests.HTTPError(f"Telegram {resp.status_code}: {resp.text[:500]}")
    return resp.json()


def post_offer(product, message):
    """Posta com imagem se houver thumbnail; senao, so texto."""
    thumb = product.get("thumbnail")
    if thumb:
        try:
            return send_photo(thumb, message)
        except Exception:
            pass  # se a imagem falhar, cai para texto
    return send_message(message)


def send_photo_file(path, caption, chat_id=None):
    """Envia uma imagem LOCAL (arquivo) com legenda."""
    chat_id = chat_id or config.TELEGRAM_CHANNEL_ID
    with open(path, "rb") as f:
        resp = requests.post(
            f"{_base()}/sendPhoto",
            data={"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"},
            files={"photo": f},
            timeout=60,
        )
    if not resp.ok:
        raise requests.HTTPError(f"Telegram {resp.status_code}: {resp.text[:500]}")
    return resp.json()

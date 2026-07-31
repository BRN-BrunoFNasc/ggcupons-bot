"""Inteligencia de titulo: identifica a FAMILIA do produto e o termo de busca.

Resolve casos como 'Dualsense' e 'Controle sem fio PS5' serem o mesmo produto,
para (1) categorizar melhor e (2) usar um termo unico no Google Trends.
"""
import re
import unicodedata


def _norm(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip()


# familia: nome, categoria, termo p/ trends, apelidos (mais especifico primeiro)
FAMILIAS = [
    # ---- controles ----
    ("DualSense", "Controles", "DualSense PS5",
     ["dualsense", "dual sense", "controle sem fio playstation 5", "controle sem fio ps5",
      "controle ps5", "controle playstation 5"]),
    ("DualShock 4", "Controles", "DualShock 4",
     ["dualshock", "dual shock", "controle ps4", "controle playstation 4"]),
    ("Controle Xbox", "Controles", "Controle Xbox Series",
     ["controle xbox", "xbox wireless controller", "controle series x", "controle series s",
      "controle sem fio xbox"]),
    ("Controle Switch Pro", "Controles", "Controle Pro Nintendo Switch",
     ["switch pro controller", "controle pro", "joy-con", "joy con", "joycon", "hori split pad"]),
    # ---- consoles ----
    ("PlayStation 5", "Consoles", "PlayStation 5",
     ["console ps5", "console playstation 5", "playstation 5 slim", "ps5 slim",
      "ps5 digital", "ps5 pro"]),
    ("PlayStation 4", "Consoles", "PlayStation 4",
     ["console ps4", "console playstation 4", "playstation 4 slim", "ps4 slim"]),
    ("Xbox Series X", "Consoles", "Xbox Series X", ["xbox series x"]),
    ("Xbox Series S", "Consoles", "Xbox Series S", ["xbox series s"]),
    ("Nintendo Switch 2", "Consoles", "Nintendo Switch 2", ["switch 2", "nintendo switch 2"]),
    ("Nintendo Switch OLED", "Consoles", "Nintendo Switch OLED", ["switch oled"]),
    ("Nintendo Switch", "Consoles", "Nintendo Switch",
     ["console nintendo switch", "switch lite"]),
    # ---- fones ----
    ("Headset Gamer", "Fones", "Headset Gamer",
     ["headset gamer", "fone gamer", "headphone gamer", "headset sem fio gamer"]),
    ("Fone Bluetooth", "Fones", "Fone Bluetooth",
     ["fone de ouvido bluetooth", "earbud", "airdots", "fone sem fio"]),
    # ---- monitores ----
    ("Monitor Gamer", "Monitores", "Monitor Gamer",
     ["monitor gamer", "monitor 144hz", "monitor 165hz", "monitor curvo"]),
    ("Monitor Portatil", "Monitores", "Monitor Portatil", ["monitor portatil", "monitor portátil"]),
    # ---- acessorios ----
    ("Mouse Gamer", "Acessorios Gamer", "Mouse Gamer", ["mouse gamer", "mouse sem fio gamer"]),
    ("Teclado Mecanico", "Acessorios Gamer", "Teclado Mecanico",
     ["teclado mecanico", "teclado gamer"]),
    ("Cadeira Gamer", "Acessorios Gamer", "Cadeira Gamer", ["cadeira gamer"]),
    ("Gift Card", "Gift Card", "Gift Card", ["gift card", "cartao presente", "psn", "game pass", "steam"]),
]

# palavras de ruido removidas na extracao generica do termo
RUIDO = set(_norm(w) for w in [
    "sem", "fio", "com", "para", "cor", "preto", "branco", "azul", "vermelho", "verde",
    "edicao", "limitada", "especial", "midia", "fisica", "digital", "novo", "lacrado",
    "original", "nacional", "gb", "tb", "polegadas", "pol", "kit", "bivolt", "rgb",
    "de", "do", "da", "e", "o", "a", "jogo", "console", "gamer", "wireless"])


def identificar(titulo):
    """Retorna (familia, categoria, termo) ou None se nao reconhecer."""
    t = " " + _norm(titulo) + " "
    for nome, cat, termo, apelidos in FAMILIAS:
        for ap in apelidos:
            if " " + _norm(ap) + " " in t or _norm(ap) in _norm(titulo):
                return {"familia": nome, "categoria": cat, "termo": termo}
    return None


def categoria(titulo):
    """Categoria pela familia (se reconhecida), senao None."""
    r = identificar(titulo)
    return r["categoria"] if r else None


PLATAFORMAS = set(_norm(w) for w in [
    "ps5", "ps4", "ps3", "playstation", "xbox", "series", "switch", "nintendo",
    "pc", "one", "x", "s", "steam", "midia", "fisica", "física"])


def _nome_jogo(titulo):
    """Extrai o nome do jogo (tira 'jogo', plataforma, edicao, ruido)."""
    palavras = []
    for w in _norm(titulo).split():
        if w in PLATAFORMAS or w in RUIDO or len(w) <= 1:
            continue
        palavras.append(w)
    return " ".join(palavras[:5]).title() or _norm(titulo)[:30]


def termo_busca(titulo, categoria=None):
    """Termo para o Google Trends, ciente da categoria."""
    r = identificar(titulo)
    if r and (categoria is None or r["categoria"] == categoria):
        return r["termo"]
    if categoria == "Jogos" or (categoria is None and "jogo" in _norm(titulo)):
        return _nome_jogo(titulo)
    if r:
        return r["termo"]
    palavras = [w for w in _norm(titulo).split() if w not in RUIDO and len(w) > 2]
    return " ".join(palavras[:3]).title() or _norm(titulo)[:30]

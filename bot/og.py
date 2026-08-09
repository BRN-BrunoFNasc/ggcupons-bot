"""Gera banners de compartilhamento (Open Graph) 1200x630 com Pillow.

- home.png     -> banner da marca (compartilhar a tela principal)
- cat-<slug>.png -> banner por categoria (compartilhar uma categoria)

Produtos NAO tem banner gerado: usam a propria foto do produto como og:image
(a imagem do produto + o preco vao no titulo/descricao das meta tags).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
FONTES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fontes")
_SYS = "/usr/share/fonts/truetype/dejavu"

# paleta da marca (verde escuro -> quase preto, com menta de destaque)
BG_TOP = "#12402E"
BG_BOT = "#0B1712"
MENTA = "#2EE6A0"
LARANJA = "#FF5A3C"
BRANCO = "#F3FBF7"
CINZA = "#9FC3B4"

_cache = {}


def _font(size, peso="bold"):
    cand = {
        "bold": [os.path.join(FONTES_DIR, "Poppins-Bold.ttf"), _SYS + "/DejaVuSans-Bold.ttf"],
        "med":  [os.path.join(FONTES_DIR, "Poppins-Medium.ttf"), _SYS + "/DejaVuSans.ttf"],
        "reg":  [os.path.join(FONTES_DIR, "Poppins-Regular.ttf"), _SYS + "/DejaVuSans.ttf"],
    }[peso]
    key = (size, peso)
    if key in _cache:
        return _cache[key]
    for c in cand:
        try:
            f = ImageFont.truetype(c, size)
            _cache[key] = f
            return f
        except Exception:
            pass
    f = ImageFont.load_default()
    _cache[key] = f
    return f


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _grad(c1, c2):
    """Gradiente vertical rapido (faz 1px de largura e estica)."""
    c1, c2 = _hex(c1), _hex(c2)
    strip = Image.new("RGB", (1, H))
    px = strip.load()
    for y in range(H):
        t = y / (H - 1)
        px[0, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return strip.resize((W, H)).convert("RGBA")


def _fundo():
    img = _grad(BG_TOP, BG_BOT)
    # circulos translucidos numa camada separada (pra o alpha valer de verdade)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov, "RGBA")
    od.ellipse([W - 250, H - 290, W + 190, H + 150], fill=_hex(MENTA) + (60,))
    od.ellipse([W - 140, -150, W + 210, 200], fill=_hex(MENTA) + (40,))
    od.ellipse([-130, H - 210, 200, H + 100], fill=_hex(LARANJA) + (48,))
    img = Image.alpha_composite(img, ov)
    d = ImageDraw.Draw(img, "RGBA")
    # pontinhos + faixa lateral (solidos, por cima)
    for i in range(7):
        x = 70 + i * 26
        d.ellipse([x, 80, x + 9, 89], fill=_hex(MENTA) + (170,))
    d.rectangle([0, 0, 14, H], fill=_hex(MENTA))
    return img, d


def _wrap(d, texto, font, maxw):
    palavras, linhas, cur = texto.split(), [], ""
    for p in palavras:
        teste = (cur + " " + p).strip()
        if d.textlength(teste, font=font) <= maxw:
            cur = teste
        else:
            if cur:
                linhas.append(cur)
            cur = p
    if cur:
        linhas.append(cur)
    return linhas


def _pill(d, x, y, texto, font, cor_txt, cor_bg):
    tw = d.textlength(texto, font=font)
    b = d.textbbox((0, 0), texto, font=font)
    th = b[3] - b[1]
    padx, pady = 20, 12
    d.rounded_rectangle([x, y, x + tw + padx * 2, y + th + pady * 2], radius=(th + pady * 2) // 2,
                        fill=cor_bg)
    d.text((x + padx, y + pady - b[1]), texto, font=font, fill=cor_txt)
    return y + th + pady * 2


def _marca(d, brand):
    f = _font(30, "bold")
    b = d.textbbox((0, 0), brand, font=f)
    d.text((60, H - 78), brand, font=f, fill=_hex(MENTA))
    fd = _font(22, "med")
    d.text((60, H - 44), "ggcupons.com.br", font=fd, fill=_hex(CINZA))


def _salvar(img, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    img.convert("RGB").save(caminho, "PNG", optimize=True)


def gerar_home(caminho, brand="GARIMPO GAMER CUPONS"):
    img, d = _fundo()
    _pill(d, 60, 70, "HISTORICO DE PRECO REAL", _font(24, "bold"), _hex(BG_BOT), _hex(MENTA))
    # titulo grande com destaque na menta
    ft = _font(74, "bold")
    y = 165
    d.text((60, y), "As melhores ofertas de", font=ft, fill=_hex(BRANCO))
    y += 92
    linha2 = "games e tech"
    d.text((60, y), linha2, font=ft, fill=_hex(MENTA))
    w2 = d.textlength(linha2, font=ft)
    d.text((60 + w2 + 18, y), ", todo dia.", font=ft, fill=_hex(BRANCO))
    # subtitulo
    fs = _font(32, "med")
    for i, ln in enumerate(_wrap(d, "Comparamos o preco todos os dias — descubra se o desconto e de verdade antes de comprar.", fs, 1000)):
        d.text((60, 380 + i * 44), ln, font=fs, fill=_hex(CINZA))
    _marca(d, brand)
    _salvar(img, caminho)


def gerar_categoria(caminho, categoria, brand="GARIMPO GAMER CUPONS"):
    img, d = _fundo()
    _pill(d, 60, 70, "OFERTAS EM DESTAQUE", _font(24, "bold"), _hex(BG_BOT), _hex(MENTA))
    # nome da categoria bem grande (ajusta o tamanho pra caber)
    cat = categoria.upper()
    tam = 118
    ft = _font(tam, "bold")
    while d.textlength(cat, font=ft) > W - 120 and tam > 48:
        tam -= 6
        ft = _font(tam, "bold")
    linhas = _wrap(d, cat, ft, W - 120)
    y = 175
    for ln in linhas[:2]:
        d.text((60, y), ln, font=ft, fill=_hex(BRANCO))
        y += tam + 8
    # barra menta sob o titulo
    d.rounded_rectangle([62, y + 6, 62 + 220, y + 18], radius=6, fill=_hex(MENTA))
    fs = _font(30, "med")
    d.text((60, y + 42), f"Ofertas de {categoria} com historico de preco real",
           font=fs, fill=_hex(CINZA))
    _marca(d, brand)
    _salvar(img, caminho)


def gerar_todos(pasta, categorias, slug, brand="GARIMPO GAMER CUPONS"):
    """Gera home.png + cat-<slug>.png pra cada categoria. `slug` e a funcao cat_slug."""
    gerar_home(os.path.join(pasta, "home.png"), brand=brand)
    for c in categorias:
        gerar_categoria(os.path.join(pasta, f"cat-{slug(c)}.png"), c, brand=brand)

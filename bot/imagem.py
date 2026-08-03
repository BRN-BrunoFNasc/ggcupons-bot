"""Card visual da oferta - estilo limpo (logo + foto + preco + convite)."""
import io
import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from bot import config

W = H = 1080
HEADER_BG = (14, 26, 20)      # verde bem escuro (marca)
FOOTER_BG = (18, 58, 44)      # verde escuro
BODY_BG = (255, 255, 255)     # branco limpo
GREEN = (46, 230, 160)
ORANGE = (255, 90, 60)
WHITE = (255, 255, 255)

HEADER_H = 150
FOOTER_H = 175

FONTDIR = "/usr/share/fonts/truetype/dejavu"


FONTES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fontes")

# ordem de preferencia: fontes embutidas > fontes do sistema
_CAMINHOS = {
    "bold":    [os.path.join(FONTES_DIR, "Poppins-Bold.ttf"),
                "C:/Windows/Fonts/Montserrat-Bold.ttf",
                "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "medium":  [os.path.join(FONTES_DIR, "Poppins-Medium.ttf"),
                "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "regular": [os.path.join(FONTES_DIR, "Poppins-Regular.ttf"),
                "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
}
_cache_fontes = {}


def _font(size, bold=True, peso=None):
    peso = peso or ("bold" if bold else "regular")
    chave = (peso, size)
    if chave in _cache_fontes:
        return _cache_fontes[chave]
    for caminho in _CAMINHOS.get(peso, _CAMINHOS["bold"]):
        try:
            f = ImageFont.truetype(caminho, size)
            _cache_fontes[chave] = f
            return f
        except Exception:
            continue
    f = ImageFont.load_default()
    _cache_fontes[chave] = f
    return f


def _fmt(v):
    if v is None:
        return ""
    s = f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s


def _center(d, text, y, font, fill, w=W, x0=0):
    b = d.textbbox((0, 0), text, font=font)
    d.text((x0 + (w - (b[2] - b[0])) / 2, y), text, font=font, fill=fill)


def _fit(img, bw, bh):
    r = min(bw / img.width, bh / img.height)
    return img.resize((max(1, int(img.width * r)), max(1, int(img.height * r))))


def _produto_img(url):
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        im = Image.open(io.BytesIO(r.content))
        if im.mode != "RGBA":
            im = im.convert("RGBA")
        return im
    except Exception:
        ph = Image.new("RGBA", (600, 600), (240, 240, 240, 255))
        ImageDraw.Draw(ph).text((240, 290), "sem imagem", fill=(160, 160, 160))
        return ph


def _qr(data, size):
    import qrcode
    q = qrcode.QRCode(border=1, box_size=8)
    q.add_data(data)
    q.make(fit=True)
    return q.make_image(fill_color="black", back_color="white").convert("RGBA").resize((size, size))


def _link_redes():
    """URL da aba Redes do site (links.html). Fallback: convite do Telegram."""
    site = (getattr(config, "SITE_URL", "") or "").rstrip("/")
    return (site + "/links.html") if site else config.CHANNEL_INVITE


def gerar_card(product, info, out_path, logo_path=None):
    # 1) template com zonas definidas (arte de designer)
    tpl = config.TEMPLATE_PATH
    if tpl and os.path.exists(tpl):
        return gerar_card_template(product, info, out_path, tpl, logo_path=logo_path)
    # 2) arte de fundo gerada por IA (estrutura desenhada por cima)
    fundo = getattr(config, "FUNDO_PATH", "")
    if fundo and os.path.exists(fundo):
        return gerar_card_fundo(product, info, out_path, fundo, logo_path=logo_path)
    # 3) layout limpo desenhado por codigo (padrao)
    return gerar_card_limpo(product, info, out_path, logo_path=logo_path)


def _grad_v(img, box, c1, c2):
    """Gradiente vertical dentro de uma caixa."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    alt = max(1, y1 - y0)
    for i in range(alt):
        t = i / alt
        d.line([(x0, y0 + i), (x1, y0 + i)],
               fill=(int(c1[0] + (c2[0] - c1[0]) * t),
                     int(c1[1] + (c2[1] - c1[1]) * t),
                     int(c1[2] + (c2[2] - c1[2]) * t)))


def _clarear(c, f=0.18):
    return tuple(min(255, int(v + (255 - v) * f)) for v in c)


def _escurecer(c, f=0.25):
    return tuple(int(v * (1 - f)) for v in c)


def _texto_na_caixa(d, texto, box, font, fill):
    """Centraliza o texto na caixa medindo a altura real dos glifos."""
    x0, y0, x1, y1 = box
    b = d.textbbox((0, 0), texto, font=font)
    larg, alt = b[2] - b[0], b[3] - b[1]
    x = x0 + ((x1 - x0) - larg) / 2 - b[0]
    y = y0 + ((y1 - y0) - alt) / 2 - b[1]
    d.text((x, y), texto, font=font, fill=fill)


def _texto_riscado(d, texto, cx, y, font, fill, esp=3):
    """Escreve o texto centrado em cx com uma linha do tamanho EXATO do texto."""
    b = d.textbbox((0, 0), texto, font=font)
    larg = b[2] - b[0]
    x = cx - larg / 2 - b[0]
    d.text((x, y), texto, font=font, fill=fill)
    real = d.textbbox((x, y), texto, font=font)      # posicao real dos glifos
    meio = (real[1] + real[3]) / 2
    d.line([real[0], meio, real[2], meio], fill=fill, width=esp)
    return real


def _logo_circular(caminho, tam, cor_anel=None, espessura=4):
    """Recorta o logo em circulo (sem o fundo quadrado) e opcionalmente poe um anel."""
    im = Image.open(caminho).convert("RGBA")
    lado = min(im.size)
    im = im.crop((((im.width - lado) // 2), ((im.height - lado) // 2),
                  ((im.width - lado) // 2) + lado, ((im.height - lado) // 2) + lado))
    sup = tam * 4
    im = im.resize((sup, sup), Image.LANCZOS)
    mask = Image.new("L", (sup, sup), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, sup - 1, sup - 1], fill=255)
    out = Image.new("RGBA", (sup, sup), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    if cor_anel:
        ImageDraw.Draw(out).ellipse(
            [espessura * 2, espessura * 2, sup - espessura * 2, sup - espessura * 2],
            outline=cor_anel + (255,), width=espessura * 4)
    return out.resize((tam, tam), Image.LANCZOS)


def _grad_diag(img, box, c1, c2):
    """Gradiente na diagonal — mais vivo que o vertical."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    g = Image.new("RGB", (w, h))
    px = g.load()
    for y in range(h):
        for x in range(0, w, 4):
            t = (x / w * 0.75 + y / h * 0.25)
            c = (int(c1[0] + (c2[0] - c1[0]) * t),
                 int(c1[1] + (c2[1] - c1[1]) * t),
                 int(c1[2] + (c2[2] - c1[2]) * t))
            for k in range(4):
                if x + k < w:
                    px[x + k, y] = c
    img.paste(g, (x0, y0))


def _grad_arredondado(base, box, c1, c2, raio=22):
    """Retangulo arredondado preenchido com gradiente vertical."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dg = ImageDraw.Draw(grad)
    for i in range(h):
        t = i / max(1, h)
        dg.line([(0, i), (w, i)],
                fill=(int(c1[0] + (c2[0] - c1[0]) * t),
                      int(c1[1] + (c2[1] - c1[1]) * t),
                      int(c1[2] + (c2[2] - c1[2]) * t), 255))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=raio, fill=255)
    base.paste(grad, (x0, y0), mask)


def _sombra(base, box, raio=20, blur=18, forca=70, desloc=(0, 8)):
    """Sombra suave sob um elemento."""
    camada = Image.new("RGBA", base.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    ImageDraw.Draw(camada).rounded_rectangle(
        [x0 + desloc[0], y0 + desloc[1], x1 + desloc[0], y1 + desloc[1]],
        radius=raio, fill=(0, 0, 0, forca))
    camada = camada.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(camada)


def gerar_card_limpo(product, info, out_path, logo_path=None):
    """Layout minimalista com acabamento: gradientes, sombras e tipografia Poppins."""
    C = config
    HD, FT, LINHA = 138, 164, 6
    BRANCO = (255, 255, 255)

    img = Image.new("RGBA", (W, H), (255, 255, 255, 255))

    # ---------- topo ----------
    _grad_diag(img, (0, 0, W, HD), _escurecer(C.COR_BARRA, .22), _clarear(C.COR_BARRA, .16))
    d = ImageDraw.Draw(img)

    # brilho sutil atras do logo
    brilho = Image.new("RGBA", (W, HD), (0, 0, 0, 0))
    ImageDraw.Draw(brilho).ellipse([-60, -HD, 320, HD * 2],
                                   fill=C.COR_LINHA + (26,))
    img.alpha_composite(brilho.filter(ImageFilter.GaussianBlur(40)), (0, 0))

    # faixas diagonais decorativas na direita
    dec = Image.new("RGBA", (W, HD), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dec)
    for i in range(9):
        x = W - 250 + i * 30
        dd.line([(x, HD + 20), (x + 90, -20)], fill=C.COR_LINHA + (34,), width=7)
    img.alpha_composite(dec, (0, 0))

    # linha de destaque com degrade
    _grad_arredondado(img, (0, HD, W, HD + LINHA),
                      C.COR_LINHA, _escurecer(C.COR_LINHA, .45), raio=0)

    d = ImageDraw.Draw(img)
    logo_path = logo_path or (C.LOGO_PATH or None)
    tx = 46
    if logo_path and os.path.exists(logo_path):
        try:
            tam = HD - 34
            lg = _logo_circular(logo_path, tam, cor_anel=C.COR_LINHA, espessura=3)
            img.alpha_composite(lg, (34, (HD - tam) // 2))
            tx = 34 + tam + 26
        except Exception:
            pass

    d = ImageDraw.Draw(img)
    # marca + assinatura
    nome = C.BRAND_NAME
    f_nome = _font(38)
    d.text((tx, HD // 2 - 34), nome, font=f_nome, fill=BRANCO)
    sub = getattr(C, "BRAND_SUB", "") or "OFERTAS DE GAMES E TECH"
    d.text((tx + 2, HD // 2 + 8), sub, font=_font(19, peso="medium"), fill=C.COR_LINHA)

    # ---------- corpo ----------
    topo, base_y = HD + LINHA, H - FT
    reserva = 210                       # espaco do bloco de preco
    area_h = (base_y - topo) - reserva

    prod = _produto_img(info.get("thumbnail") or product.get("thumbnail") or "")
    prod = _fit(prod, W - 300, area_h - 20)
    px = (W - prod.width) // 2
    py = topo + 26 + (area_h - prod.height) // 2

    # (sombra sob o produto removida - o usuario achou feio)
    if prod.mode == "RGBA":
        img.alpha_composite(prod, (px, py))
    else:
        img.paste(prod, (px, py))

    d = ImageDraw.Draw(img)

    # ---------- selo de desconto ----------
    if info.get("desconto"):
        r, cx, cy = 78, W - 126, topo + 96
        _sombra(img, (cx - r, cy - r, cx + r, cy + r), raio=r, blur=14, forca=60, desloc=(0, 5))
        d = ImageDraw.Draw(img)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=C.COR_PRECO + (255,))
        d.ellipse([cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7],
                  outline=(255, 255, 255, 110), width=2)
        _center(d, f"{int(info['desconto'])}%", cy - 34, _font(40), BRANCO, w=2 * r, x0=cx - r)
        _center(d, "OFF", cy + 8, _font(23), BRANCO, w=2 * r, x0=cx - r)

    # ---------- preco ----------
    preco = info.get("preco_cupom") or info.get("por")
    by = base_y - 132

    # linha de cima: "De R$ X" riscado  ou  "COM CUPOM XX"
    if info.get("preco_cupom"):
        _center(d, f"COM O CUPOM {info.get('cupom','')}", by - 52, _font(27), C.COR_PRECO)
    elif info.get("de") and info.get("por") and info["de"] > info["por"]:
        _texto_riscado(d, f"De {_fmt(info['de'])}", W / 2, by - 54,
                       _font(28, peso="medium"), (150, 150, 155))

    # a faixa acompanha o tamanho do preco (com respiro dos lados)
    _ftxt = _font(60)
    _b = d.textbbox((0, 0), _fmt(preco), font=_ftxt)
    _larg = (_b[2] - _b[0]) + 150          # respiro lateral
    _larg = max(430, min(_larg, W - 300))  # limites de seguranca
    caixa = (int((W - _larg) / 2), by, int((W + _larg) / 2), by + 108)
    _sombra(img, caixa, raio=24, blur=20, forca=64, desloc=(0, 9))
    _grad_arredondado(img, caixa, _clarear(C.COR_PRECO, .16), _escurecer(C.COR_PRECO, .14), raio=24)
    d = ImageDraw.Draw(img)
    _texto_na_caixa(d, _fmt(preco), caixa, _font(60), BRANCO)

    # ---------- rodape ----------
    _grad_v(img, (0, H - FT, W, H), _clarear(C.COR_RODAPE, .08), _escurecer(C.COR_RODAPE, .10))
    d = ImageDraw.Draw(img)
    d.rectangle([0, H - FT, W, H - FT + 3], fill=C.COR_LINHA)
    try:
        qr = _qr(_link_redes(), 116)
        qx, qy = W - 158, H - FT + 24
        d.rounded_rectangle([qx - 8, qy - 8, qx + 124, qy + 124], radius=12, fill=BRANCO)
        img.alpha_composite(qr, (qx, qy))
    except Exception:
        pass
    d.text((48, H - FT + 42), "Siga-nos em nossas redes sociais",
           font=_font(34), fill=BRANCO)
    d.text((48, H - FT + 92), "Promoções e Cupons todos os dias!",
           font=_font(34), fill=C.COR_TEXTO2)

    img.convert("RGB").save(out_path, "PNG")
    return out_path


# ============================================================
# Card usando TEMPLATE (imagem de fundo gerada por IA)
# ============================================================
def _paste_fit(img, sub, zona, mask=True):
    x0, y0, x1, y1 = zona
    s = _fit(sub, x1 - x0, y1 - y0)
    px = x0 + ((x1 - x0) - s.width) // 2
    py = y0 + ((y1 - y0) - s.height) // 2
    if mask and s.mode == "RGBA":
        img.paste(s, (px, py), s)
    else:
        img.paste(s, (px, py))


def _fit_text(d, text, zona, max_size, fill, bold=True):
    """Escreve o texto centralizado na zona, diminuindo a fonte ate caber."""
    x0, y0, x1, y1 = zona
    size = max_size
    while size > 10:
        f = _font(size, bold)
        b = d.textbbox((0, 0), text, font=f)
        if (b[2] - b[0]) <= (x1 - x0) * 0.94 and (b[3] - b[1]) <= (y1 - y0) * 0.9:
            break
        size -= 2
    f = _font(size, bold)
    b = d.textbbox((0, 0), text, font=f)
    d.text((x0 + ((x1 - x0) - (b[2] - b[0])) / 2,
            y0 + ((y1 - y0) - (b[3] - b[1])) / 2 - b[1]), text, font=f, fill=fill)


def gerar_card_template(product, info, out_path, template_path, logo_path=None):
    base = Image.open(template_path).convert("RGB")
    if base.size != (W, H):
        base = base.resize((W, H))
    img = base
    d = ImageDraw.Draw(img)

    # logo
    logo_path = logo_path or (config.LOGO_PATH or None)
    if logo_path and os.path.exists(logo_path):
        try:
            _paste_fit(img, Image.open(logo_path).convert("RGBA"), config.ZONA_LOGO)
        except Exception:
            pass

    # foto do produto
    prod = _produto_img(info.get("thumbnail") or product.get("thumbnail") or "")
    _paste_fit(img, prod, config.ZONA_FOTO)

    # selo de desconto (canto sup. direito da zona da foto)
    if info.get("desconto"):
        fx0, fy0, fx1, fy1 = config.ZONA_FOTO
        r = 80
        cx, cy = fx1 - 10, fy0 + 40
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ORANGE)
        _center(d, f"-{int(info['desconto'])}%", cy - 34, _font(40), WHITE, w=2 * r, x0=cx - r)
        _center(d, "OFF", cy + 12, _font(25), WHITE, w=2 * r, x0=cx - r)

    # preco na faixa (com cupom aplicado, se houver)
    preco_card = info.get("preco_cupom") or info.get("por")
    if info.get("preco_cupom"):
        zx0, zy0, zx1, zy1 = config.ZONA_PRECO
        _fit_text(d, f"COM CUPOM {info.get('cupom','')}",
                  (zx0, zy0 - 46, zx1, zy0 - 6), 28, (60, 60, 60))
    _fit_text(d, _fmt(preco_card), config.ZONA_PRECO, 66, WHITE)

    # QR
    try:
        qx0, qy0, qx1, qy1 = config.ZONA_QR
        _paste_fit(img, _qr(_link_redes(), qx1 - qx0), config.ZONA_QR)
    except Exception:
        pass

    # CTA no rodape
    cx0, cy0, cx1, cy1 = config.ZONA_CTA
    d.text((cx0, cy0 + 8), "Siga-nos em nossas redes sociais", font=_font(36), fill=WHITE)
    d.text((cx0, cy0 + 58), "Promoções e Cupons todos os dias!", font=_font(36), fill=GREEN)

    img.save(out_path, "PNG")
    return out_path


# ============================================================
# Card sobre ARTE DE FUNDO gerada por IA
# A IA faz so a arte (atmosfera, textura, cor).
# O codigo desenha toda a estrutura por cima, com precisao.
# ============================================================
def _cover(img, w, h):
    """Redimensiona cobrindo a area toda, cortando o excesso (tipo background-size:cover)."""
    r = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * r) + 1, int(img.height * r) + 1))
    x = (img.width - w) // 2
    y = (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def _painel(base, box, cor, raio=22, sombra=True):
    """Desenha um painel translucido com cantos arredondados sobre a arte."""
    x0, y0, x1, y1 = box
    if sombra:
        sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([x0 + 4, y0 + 6, x1 + 4, y1 + 8],
                                             radius=raio, fill=(0, 0, 0, 90))
        base.alpha_composite(sh)
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle(box, radius=raio, fill=cor)
    base.alpha_composite(ov)


def gerar_card_fundo(product, info, out_path, fundo_path, logo_path=None):
    base = Image.open(fundo_path).convert("RGBA")
    base = _cover(base, W, H)

    # escurece levemente o topo e a base para o texto sempre ter contraste
    veu = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dv = ImageDraw.Draw(veu)
    for i in range(HEADER_H):
        dv.line([(0, i), (W, i)], fill=(6, 14, 10, int(190 * (1 - i / HEADER_H))))
    for i in range(FOOTER_H):
        y = H - FOOTER_H + i
        dv.line([(0, y), (W, y)], fill=(6, 14, 10, int(200 * (i / FOOTER_H))))
    base.alpha_composite(veu)

    d = ImageDraw.Draw(base)

    # ---- marca ----
    logo_path = logo_path or (config.LOGO_PATH or None)
    tx = 45
    if logo_path and os.path.exists(logo_path):
        try:
            lg = _fit(Image.open(logo_path).convert("RGBA"), 104, 104)
            base.alpha_composite(lg, (38, (HEADER_H - lg.height) // 2 - 8))
            tx = 38 + lg.width + 24
        except Exception:
            pass
    d.text((tx, HEADER_H // 2 - 30), config.BRAND_NAME, font=_font(42), fill=WHITE)

    # ---- painel branco da foto ----
    card = [70, 178, W - 70, 712]
    _painel(base, card, (255, 255, 255, 245), raio=24)
    prod = _produto_img(info.get("thumbnail") or product.get("thumbnail") or "")
    prod = _fit(prod, card[2] - card[0] - 70, card[3] - card[1] - 60)
    px = card[0] + ((card[2] - card[0]) - prod.width) // 2
    py = card[1] + ((card[3] - card[1]) - prod.height) // 2
    if prod.mode == "RGBA":
        base.alpha_composite(prod, (px, py))
    else:
        base.paste(prod, (px, py))

    # ---- selo de desconto ----
    d = ImageDraw.Draw(base)
    if info.get("desconto"):
        r = 78
        cx, cy = W - 128, 208
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ORANGE + (255,))
        _center(d, f"-{int(info['desconto'])}%", cy - 32, _font(40), WHITE, w=2 * r, x0=cx - r)
        _center(d, "OFF", cy + 12, _font(25), WHITE, w=2 * r, x0=cx - r)

    # ---- faixa de preco ----
    preco = info.get("preco_cupom") or info.get("por")
    if info.get("preco_cupom"):
        _center(d, f"COM CUPOM {info.get('cupom','')}", 726, _font(26), GREEN)
    by = 762
    _painel(base, [215, by, W - 215, by + 100], ORANGE + (255,), raio=20, sombra=False)
    d = ImageDraw.Draw(base)
    _center(d, _fmt(preco), by + 24, _font(58), WHITE)

    # ---- rodape ----
    try:
        qr = _qr(config.CHANNEL_INVITE, 122)
        _painel(base, [W - 168, H - 148, W - 34, H - 14], (255, 255, 255, 255), raio=12, sombra=False)
        base.alpha_composite(qr, (W - 162, H - 142))
    except Exception:
        pass
    d = ImageDraw.Draw(base)
    d.text((48, H - 132), "Siga-nos em nossas redes sociais", font=_font(35), fill=WHITE)
    d.text((48, H - 84), "Promoções e Cupons todos os dias!", font=_font(35), fill=GREEN)

    base.convert("RGB").save(out_path, "PNG")
    return out_path

#!/usr/bin/env python3
"""Mostra como uma imagem fica como AVATAR (recorte circular, tamanhos reais).

    python testar_avatar.py logo.png
    python testar_avatar.py logo.png --saida previa.png

Gera uma previa com o recorte circular nos tamanhos em que o avatar realmente
aparece no Telegram/WhatsApp. Serve para decidir ANTES de adotar a arte.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

TAMANHOS = [(40, "lista de conversas"), (64, "cabeçalho"),
            (100, "perfil pequeno"), (160, "perfil grande")]


def circular(img, tam):
    im = img.convert("RGBA").resize((tam, tam), Image.LANCZOS)
    mask = Image.new("L", (tam * 4, tam * 4), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, tam * 4, tam * 4], fill=255)
    mask = mask.resize((tam, tam), Image.LANCZOS)
    out = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("Uso: python testar_avatar.py IMAGEM.png"); return
    origem = Path(args[0])
    if not origem.exists():
        print("Arquivo nao encontrado:", origem); return
    saida = "previa_avatar.png"
    if "--saida" in sys.argv:
        i = sys.argv.index("--saida")
        if i + 1 < len(sys.argv):
            saida = sys.argv[i + 1]

    src = Image.open(origem)
    # quadrado central (e assim que os apps recortam)
    lado = min(src.size)
    src = src.crop((((src.width - lado) // 2), ((src.height - lado) // 2),
                    ((src.width - lado) // 2) + lado, ((src.height - lado) // 2) + lado))

    MARG, GAP = 44, 44
    larg = MARG * 2 + sum(t for t, _ in TAMANHOS) + GAP * (len(TAMANHOS) - 1)
    MAXT = max(t for t, _ in TAMANHOS)
    topo, alt_linha = 62, MAXT + 40
    altura = topo + alt_linha * 2 + 34

    tela = Image.new("RGB", (larg, altura), (245, 245, 247))
    d = ImageDraw.Draw(tela)
    # faixas: clara em cima, escura embaixo (para conferir contraste nos 2 temas)
    d.rectangle([0, topo, larg, topo + alt_linha], fill=(255, 255, 255))
    d.rectangle([0, topo + alt_linha, larg, topo + alt_linha * 2], fill=(24, 24, 27))

    x = MARG
    for tam, rotulo in TAMANHOS:
        av = circular(src, tam)
        cy1 = topo + alt_linha // 2
        cy2 = topo + alt_linha + alt_linha // 2
        tela.paste(av, (x, cy1 - tam // 2), av)
        tela.paste(av, (x, cy2 - tam // 2), av)
        d.text((x, 44), f"{tam}px", fill=(110, 110, 116))
        d.text((x, altura - 26), rotulo[:16], fill=(150, 150, 156))
        x += tam + GAP

    d.text((40, 16), f"PREVIA DE AVATAR — {origem.name}", fill=(24, 24, 27))
    tela.save(saida)
    print(f"Previa salva em: {saida}")
    print("Se nos tamanhos pequenos virar mancha, a arte esta detalhada demais.")


if __name__ == "__main__":
    main()

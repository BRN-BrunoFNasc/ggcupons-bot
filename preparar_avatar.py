#!/usr/bin/env python3
"""Prepara uma arte para virar AVATAR de canal (sem cantos brancos).

Muitas artes vem como um circulo colorido dentro de um quadrado branco. Ao ser
recortado em circulo pelo app, sobra um anel claro na borda. Este script
recorta a arte, detecta a cor de fundo e gera um avatar com cor ate a borda.

    python preparar_avatar.py mascote.png
    python preparar_avatar.py mascote.png --saida avatar.png --tamanho 512
    python preparar_avatar.py mascote.png --zoom 1.06     (corta um pouco mais)
"""
import sys
from collections import Counter
from pathlib import Path

from PIL import Image


def _arg(flag, padrao=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return padrao


def recortar_conteudo(im, tol=26):
    """Corta as bordas quase brancas, deixando so a arte."""
    rgb = im.convert("RGB")
    larg, alt = rgb.size
    px = rgb.load()

    def branco(p):
        return p[0] > 255 - tol and p[1] > 255 - tol and p[2] > 255 - tol

    x0, y0, x1, y1 = larg, alt, 0, 0
    passo = max(1, min(larg, alt) // 400)
    for y in range(0, alt, passo):
        for x in range(0, larg, passo):
            if not branco(px[x, y]):
                x0 = min(x0, x); y0 = min(y0, y)
                x1 = max(x1, x); y1 = max(y1, y)
    if x1 <= x0 or y1 <= y0:
        return im
    return im.crop((x0, y0, x1 + 1, y1 + 1))


def cor_de_fundo(im):
    """Cor predominante na borda da arte (o fundo do circulo)."""
    rgb = im.convert("RGB").resize((120, 120))
    px = rgb.load()
    amostras = []
    for i in range(120):
        for p in [(i, 6), (i, 113), (6, i), (113, i), (i, 60), (60, i)]:
            amostras.append(px[p])
    # ignora tons quase brancos
    amostras = [c for c in amostras if not (c[0] > 235 and c[1] > 235 and c[2] > 235)]
    if not amostras:
        return (18, 42, 32)
    return Counter(amostras).most_common(1)[0][0]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); return
    origem = Path(args[0])
    if not origem.exists():
        print("Arquivo nao encontrado:", origem); return

    saida = _arg("--saida", "avatar.png")
    tam = int(_arg("--tamanho", "512"))
    zoom = float(_arg("--zoom", "1.02"))

    im = Image.open(origem).convert("RGBA")
    print(f"  original      : {im.size[0]}x{im.size[1]}")

    arte = recortar_conteudo(im)
    print(f"  apos recorte  : {arte.size[0]}x{arte.size[1]}")

    fundo = cor_de_fundo(arte)
    print(f"  cor de fundo  : RGB{fundo}")

    # quadrado com a cor do fundo, arte centralizada e com leve zoom
    lado = max(arte.size)
    tela = Image.new("RGBA", (lado, lado), fundo + (255,))
    tela.alpha_composite(arte, (((lado - arte.width) // 2), ((lado - arte.height) // 2)))

    if zoom > 1:
        novo = int(lado * zoom)
        tela = tela.resize((novo, novo), Image.LANCZOS)
        c = (novo - lado) // 2
        tela = tela.crop((c, c, c + lado, c + lado))

    tela = tela.resize((tam, tam), Image.LANCZOS)
    tela.convert("RGB").save(saida, "PNG")
    print(f"\n  Avatar salvo  : {saida}  ({tam}x{tam})")
    print(f"  Agora teste   : python testar_avatar.py {saida}")


if __name__ == "__main__":
    main()

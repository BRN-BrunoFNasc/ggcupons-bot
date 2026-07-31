#!/usr/bin/env python3
"""Aquece o perfil do navegador do bot no Mercado Livre.

Abre o ML como um visitante comum: home, uma busca, um produto. Isso cria
cookies e historico no perfil, o que reduz muito a chance de cair na tela de
verificacao. Rode UMA VEZ, e de novo se o bot voltar a ser bloqueado.

    python aquecer.py            (janela visivel - recomendado)
    python aquecer.py --oculto
"""
import sys
import time

sys.path.insert(0, ".")
from bot import reader

PASSOS = [
    ("https://www.mercadolivre.com.br/", "pagina inicial"),
    ("https://lista.mercadolivre.com.br/console-playstation-5", "busca"),
    ("https://www.mercadolivre.com.br/ofertas", "ofertas"),
]


def main():
    headless = "--oculto" in sys.argv
    print("\nAquecendo o perfil do navegador...")
    print(f"perfil: {reader.PERFIL_DIR}\n")

    with reader.browser(headless=headless) as ctx:
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for url, nome in PASSOS:
            print(f"  visitando {nome}...", flush=True)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(2500)
                reader._aceitar_cookies(page)
                # rolagem leve, como um humano
                for _ in range(3):
                    page.mouse.wheel(0, 700)
                    page.wait_for_timeout(900)
                estado = "BLOQUEADO" if reader.bloqueado(page) else "ok"
                print(f"     {estado}  ({page.url[:64]})")
            except Exception as e:
                print(f"     erro: {str(e)[:70]}")
            time.sleep(2)

        # teste final: consegue ler um produto?
        print("\n  testando a leitura de um produto...", flush=True)
        d = reader._open_and_read(page, "https://www.mercadolivre.com.br/p/MLB54963150")
        if d and d.get("price"):
            print(f"     SUCESSO — preco lido: R$ {d['price']}")
            print("\nPerfil aquecido. O bot deve voltar a funcionar.")
        elif d and d.get("bloqueado"):
            print("     ainda BLOQUEADO.")
            print("\nO Mercado Livre ainda esta exigindo verificacao. O que fazer:")
            print("  1. Espere algumas horas (o bloqueio costuma ser temporario)")
            print("  2. Aumente VIGIA_INTERVALO_MIN no .env (ex.: 30 ou 60)")
            print("  3. Rode 'python aquecer.py' de novo mais tarde")
        else:
            print("     nao li o preco, mas tambem nao houve bloqueio.")


if __name__ == "__main__":
    main()

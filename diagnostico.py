#!/usr/bin/env python3
"""Diagnostico da leitura de preco: descobre SE e anti-robo ou mudanca de layout.

    python diagnostico.py MLB54963150
    python diagnostico.py MLB54963150 --ver     (mostra o navegador)

Salva captura de tela e HTML em data/diag/ para inspecao.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, ".")
from bot import reader, database

SAIDA = Path("data/diag")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pid = args[0] if args else "MLB54963150"
    headless = "--ver" not in sys.argv
    SAIDA.mkdir(parents=True, exist_ok=True)

    # pega o link salvo, se existir
    database.init_db()
    alvo = None
    for p in database.get_products(only_active=False):
        if p["id"] == pid:
            alvo = p.get("permalink") or p.get("affiliate_url")
            break
    urls = [u for u in [alvo, f"https://www.mercadolivre.com.br/p/{pid}"] if u]

    with reader.browser(headless=headless) as ctx:
        page = ctx.new_page()
        for url in urls:
            print("\n" + "=" * 70)
            print("URL:", url[:100])
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(4000)
            except Exception as e:
                print("  ERRO ao abrir:", e)
                continue

            final = page.url
            print("  final :", final[:100])
            print("  titulo:", (page.title() or "")[:80])

            # 1) e pagina de verificacao / bloqueio?
            bloqueio = any(k in final for k in ("account-verification", "/gz/", "login", "captcha"))
            texto = ""
            try:
                texto = page.inner_text("body")[:4000]
            except Exception:
                pass
            sinais = [s for s in ["Verifique", "verificação", "robô", "Digite seu e-mail",
                                  "iniciar sessão", "Acesso negado", "captcha"]
                      if s.lower() in texto.lower()]
            print(f"  URL de bloqueio: {'SIM' if bloqueio else 'nao'}")
            print(f"  sinais de verificacao no texto: {sinais or 'nenhum'}")

            # 2) os seletores conhecidos existem?
            print("\n  -- seletores conhecidos --")
            for sel in [".andes-money-amount__fraction", ".andes-money-amount__cents",
                        ".ui-pdp-price__second-line", "h1.ui-pdp-title",
                        "[itemprop=price]", "meta[itemprop=price]"]:
                try:
                    n = page.locator(sel).count()
                except Exception:
                    n = -1
                print(f"     {sel:<38} {n}")

            # 3) existe preco no texto visivel?
            precos = re.findall(r"R\$\s*[\d\.]+(?:,\d{2})?", texto)
            print(f"\n  precos no texto visivel: {precos[:6] or 'NENHUM'}")

            # 4) quais classes parecem de preco? (descobre layout novo)
            try:
                classes = page.evaluate("""
                () => {
                  const out = {};
                  document.querySelectorAll('*').forEach(e => {
                    const t = (e.childElementCount === 0 ? (e.textContent||'') : '').trim();
                    if (/^R?\\$?\\s*[\\d\\.]{2,}(,\\d{2})?$/.test(t) && t.length < 14) {
                      (e.className && typeof e.className === 'string' ? e.className : '')
                        .split(/\\s+/).filter(Boolean).forEach(c => out[c] = (out[c]||0)+1);
                    }
                  });
                  return Object.entries(out).sort((a,b)=>b[1]-a[1]).slice(0,12);
                }""")
                print("\n  -- classes de elementos que contem numeros/preco --")
                for c, n in classes:
                    print(f"     {c:<46} {n}")
                if not classes:
                    print("     (nenhuma — a pagina provavelmente nao carregou o produto)")
            except Exception as e:
                print("  erro ao inspecionar classes:", e)

            # 5) evidencias
            nome = re.sub(r"\W+", "_", url)[-40:]
            try:
                page.screenshot(path=str(SAIDA / f"{pid}_{nome}.png"), full_page=False)
                (SAIDA / f"{pid}_{nome}.html").write_text(page.content(), encoding="utf-8")
                print(f"\n  captura e HTML salvos em {SAIDA}/")
            except Exception as e:
                print("  nao salvou evidencia:", e)

    print("\n" + "=" * 70)
    print("COMO LER O RESULTADO:")
    print("  - 'URL de bloqueio: SIM' ou sinais de verificacao -> ANTI-ROBO")
    print("    (solucao: esperar, reduzir frequencia, aumentar VIGIA_INTERVALO_MIN)")
    print("  - seletores = 0 MAS ha precos no texto visivel     -> LAYOUT NOVO")
    print("    (solucao: atualizar os seletores com as classes listadas acima)")
    print("  - seletores = 0 e NENHUM preco no texto            -> pagina nao carregou")


if __name__ == "__main__":
    main()

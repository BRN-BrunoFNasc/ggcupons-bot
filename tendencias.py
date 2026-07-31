#!/usr/bin/env python3
"""Atualiza a popularidade dos produtos pelo Google Trends (o que a internet procura).

    python tendencias.py            -> consulta e grava as notas
    python tendencias.py --ver      -> mostra os termos e notas

Agrupa produtos pelo mesmo termo (ex.: 'Dualsense' e 'controle PS5' -> um termo).
A API do Trends e nao-oficial e limitada: rode 1x/dia. Se o Google bloquear,
as notas anteriores sao mantidas.
"""
import random
import sys
import time

from bot import database, conhecimento

ANCORA = "PlayStation 5"   # termo de referencia presente em todos os lotes


def termos_do_catalogo():
    mapa = {}
    for p in database.get_products(only_active=True):
        termo = (p.get("termo") or "").strip() or conhecimento.termo_busca(
            p.get("title"), p.get("categoria"))
        mapa.setdefault(termo, []).append(p["id"])
    return mapa


def atualizar(geo="BR", timeframe="today 1-m", verbose=True):
    try:
        from pytrends.request import TrendReq
    except Exception:
        print("Instale a dependencia: pip install pytrends"); return
    mapa = termos_do_catalogo()
    termos = [t for t in mapa if t]
    if not termos:
        print("Catalogo vazio."); return

    UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/122.0 Safari/537.36")
    py = TrendReq(hl="pt-BR", tz=180, timeout=(10, 25), retries=2, backoff_factor=1.5,
                  requests_args={"headers": {"User-Agent": UA}})
    scores = {}
    lotes = [termos[i:i + 4] for i in range(0, len(termos), 4)]
    if verbose:
        print(f"{len(termos)} termo(s) em {len(lotes)} lote(s). Ancora: {ANCORA}")

    for li, lote in enumerate(lotes, 1):
        grupo = lote + ([ANCORA] if ANCORA not in lote else [])
        ok = False
        for tentativa in range(1, 4):        # ate 3 tentativas por lote
            try:
                py.build_payload(grupo, timeframe=timeframe, geo=geo)
                df = py.interest_over_time()
                if df is None or df.empty:
                    if verbose:
                        print(f"  lote {li}: sem dados")
                else:
                    medias = {t: float(df[t].tail(6).mean()) for t in grupo if t in df.columns}
                    base = medias.get(ANCORA) or 0
                    for t in lote:
                        v = medias.get(t, 0)
                        scores[t] = round(min(100, v / base * 60), 1) if base else round(v, 1)
                        if verbose:
                            print(f"  {scores[t]:>5}  {t}")
                ok = True
                break
            except Exception as e:
                msg = str(e)
                if "429" in msg and tentativa < 3:
                    espera = 30 * tentativa + random.uniform(5, 20)
                    if verbose:
                        print(f"  lote {li}: bloqueado (429), tentativa {tentativa}/3 — "
                              f"aguardando {espera:.0f}s...")
                    time.sleep(espera)
                else:
                    if verbose:
                        print(f"  lote {li}: ERRO ({msg[:70]}) — mantendo notas anteriores")
                    break
        time.sleep(random.uniform(12, 25))   # pausa longa entre lotes

    database.init_db()
    n = 0
    for termo, ids in mapa.items():
        if termo not in scores:
            continue
        for pid in ids:
            database.set_trend(pid, scores[termo])
            n += 1
    print(f"\nNotas de tendencia atualizadas: {n} produto(s), {len(scores)} termo(s).")


if __name__ == "__main__":
    if "--ver" in sys.argv:
        for termo, ids in termos_do_catalogo().items():
            print(f"  {termo:<32} {len(ids)} produto(s)")
        print()
    atualizar()

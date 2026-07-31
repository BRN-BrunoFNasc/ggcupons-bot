#!/usr/bin/env python3
"""Painel de controle local do bot (uso interno).

    python painel.py
    -> abre em http://localhost:8080

Mostra catalogo, cupons, links, historico de posts e permite agir por botao.
Roda so na sua maquina; nao exponha na internet.
"""
import sys
import re
import json as _json
import subprocess
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from bot import database, fila, categorias, cupons as C, config

BASE = Path(__file__).resolve().parent
app = Flask(__name__,
            template_folder=str(BASE / "templates"),
            static_folder=str(BASE / "static"))

# ---- job em segundo plano (acoes demoradas usam navegador) ----
JOB = {"rodando": False, "nome": None, "log": [], "fim": None}


def _log(msg):
    JOB["log"].append(f"{datetime.now():%H:%M:%S}  {msg}")
    JOB["log"][:] = JOB["log"][-200:]


def _rodar_job(nome, fn):
    if JOB["rodando"]:
        return False
    JOB.update({"rodando": True, "nome": nome, "log": [], "fim": None})

    def alvo():
        try:
            _log(f"iniciando: {nome}")
            fn()
            _log("concluido")
        except Exception as e:
            _log(f"ERRO: {e}")
            _log(traceback.format_exc()[-600:])
        finally:
            JOB["rodando"] = False
            JOB["fim"] = datetime.now().strftime("%H:%M:%S")

    threading.Thread(target=alvo, daemon=True).start()
    return True


def _idade(ts):
    if not ts:
        return "nunca"
    try:
        t = datetime.fromisoformat(ts)
        t = t if t.tzinfo else t.replace(tzinfo=timezone.utc)
        m = (datetime.now(timezone.utc) - t).total_seconds() / 60
        if m < 60:
            return f"{int(m)}min"
        if m < 1440:
            return f"{int(m//60)}h"
        return f"{int(m//1440)}d"
    except Exception:
        return "?"


def _tipo_link(url):
    u = url or ""
    if "meli.la" in u:
        return ("oficial", "ok")
    if "matt_word" in u or "matt_tool" in u:
        return ("montado", "aviso")
    if "tag=" in u:
        return ("amazon", "ok")
    if not u:
        return ("sem link", "erro")
    return ("cru", "erro")


# ------------------------- API -------------------------
@app.get("/ping")
def ping():
    """Rota instantanea (nao toca no banco) - serve para testar se o servidor subiu."""
    return "pong", 200


@app.get("/")
def home():
    try:
        return render_template("painel.html", marca=config.BRAND_NAME)
    except Exception as e:
        return (f"<h2>Erro ao carregar o template</h2><pre>{e}</pre>"
                f"<p>Esperado em: {BASE / 'templates' / 'painel.html'}</p>"), 500


@app.get("/api/status")
def api_status():
    try:
        itens = fila.listar_status()
    except Exception as e:
        return jsonify({"erro": str(e), "produtos": [], "cupons": [], "posts": [],
                        "resumo": {"total": 0, "liberados": 0, "urgentes": 0,
                                   "posts_total": 0, "por_categoria": {}, "por_nivel": {},
                                   "sem_link_valido": 0},
                        "rodizio": [], "categorias": [], "job": JOB}), 200
    produtos = []
    for i in itens:
        tipo, sit = _tipo_link(i.get("affiliate_url"))
        produtos.append({
            "id": i["id"], "titulo": i.get("title") or "", "loja": i.get("loja") or "-",
            "categoria": i.get("categoria") or "-", "tier": i["tier"],
            "preco": i.get("preco"), "desconto": i.get("desconto") or 0,
            "freq": i["cooldown_min"], "liberado": i["liberado"],
            "urgente": i.get("urgente", False),
            "ultimo_post": _idade(i.get("last_posted_at")),
            "link": i.get("affiliate_url") or "", "link_tipo": tipo, "link_sit": sit,
            "permalink": i.get("permalink") or "",
            "manual": i.get("cooldown_min") is not None and i.get("cooldown_min") == i.get("cooldown_min"),
        })

    _cx = database._conn()
    for pp in [dict(r) for r in _cx.execute(
            "SELECT id,title,categoria,loja,affiliate_url,permalink FROM products WHERE active=0").fetchall()]:
        _t, _s = _tipo_link(pp.get("affiliate_url"))
        produtos.append({"id": pp["id"], "titulo": pp.get("title") or "", "loja": pp.get("loja") or "-",
                         "categoria": pp.get("categoria") or "-", "tier": "PAUSADO", "preco": None,
                         "desconto": 0, "freq": "", "liberado": False, "urgente": False,
                         "ultimo_post": "", "link": pp.get("affiliate_url") or "", "link_tipo": _t,
                         "link_sit": _s, "permalink": pp.get("permalink") or "", "pausado": True})
    _cx.close()

    con = database._conn()
    posts = [dict(r) for r in con.execute(
        "SELECT p.product_id, p.tier, p.price, p.posted_at, pr.title "
        "FROM posts_log p LEFT JOIN products pr ON pr.id=p.product_id "
        "ORDER BY p.posted_at DESC LIMIT 20").fetchall()]
    con.close()
    for p in posts:
        p["quando"] = _idade(p["posted_at"])

    por_cat, por_tier = {}, {}
    for i in itens:
        por_cat[i.get("categoria") or "-"] = por_cat.get(i.get("categoria") or "-", 0) + 1
        por_tier[i["tier"]] = por_tier.get(i["tier"], 0) + 1

    cupons = []
    for c in database.get_coupons():
        cupons.append({**c, "regra": C.descrever(c),
                       "vencido": C._vencido(c.get("validade"))})

    return jsonify({
        "produtos": produtos, "cupons": cupons, "posts": posts,
        "resumo": {
            "total": len(itens),
            "liberados": sum(1 for i in itens if i["liberado"]),
            "urgentes": sum(1 for i in itens if i.get("urgente")),
            "posts_total": database.contar_posts(),
            "por_categoria": por_cat, "por_nivel": por_tier,
            "sem_link_valido": sum(1 for p in produtos if p["link_sit"] != "ok"),
        },
        "rodizio": fila.sequencia_rodizio(),
        "categorias": [c["nome"] for c in categorias.carregar()],
        "job": JOB,
    })


@app.post("/api/produto/<pid>/<acao>")
def api_produto(pid, acao):
    database.init_db()
    d = request.get_json(silent=True) or {}
    if acao == "pausar":
        con = database._conn(); con.execute("UPDATE products SET active=0 WHERE id=?", (pid,))
        con.commit(); con.close()
    elif acao == "ativar":
        con = database._conn(); con.execute("UPDATE products SET active=1 WHERE id=?", (pid,))
        con.commit(); con.close()
    elif acao == "apagar":
        con = database._conn()
        con.execute("DELETE FROM price_history WHERE product_id=?", (pid,))
        con.execute("DELETE FROM products WHERE id=?", (pid,))
        con.commit(); con.close()
    elif acao == "frequencia":
        v = d.get("minutos")
        database.set_cooldown(pid, None if v in ("", "auto", None) else int(v))
    elif acao == "categoria":
        con = database._conn()
        con.execute("UPDATE products SET categoria=? WHERE id=?", (d.get("categoria"), pid))
        con.commit(); con.close()
    elif acao == "postar":
        from bot import tracker
        _rodar_job(f"postar {pid}", lambda: tracker.postar_um(pid, dry_run=False))
    else:
        return jsonify({"erro": "acao desconhecida"}), 400
    return jsonify({"ok": True})


@app.post("/api/cupom")
def api_cupom_add():
    d = request.get_json(force=True)
    database.init_db()
    database.add_coupon({
        "code": d["code"], "tipo": d.get("tipo", "perc"), "valor": float(d.get("valor") or 0),
        "minimo": float(d.get("minimo") or 0),
        "teto": float(d["teto"]) if d.get("teto") else None,
        "validade": d.get("validade") or None,
        "escopo": d.get("escopo") or "GLOBAL", "obs": d.get("obs"),
    })
    return jsonify({"ok": True})


@app.delete("/api/cupom/<code>")
def api_cupom_del(code):
    database.init_db(); database.del_coupon(code)
    return jsonify({"ok": True})


@app.post("/api/acao/<nome>")
def api_acao(nome):
    d = request.get_json(silent=True) or {}
    if nome == "ciclo":
        from bot import ciclo
        ok = _rodar_job("ciclo de postagem", lambda: ciclo.executar(publicar=True))
    elif nome == "sincronizar":
        import sincronizar_lista
        url = d.get("url") or config.ML_LISTA_URL
        ok = _rodar_job("sincronizar lista", lambda: sincronizar_lista.sincronizar(url, aplicar=True))
    elif nome == "descobrir":
        from bot import descoberta
        ok = _rodar_job("descobrir ofertas", lambda: descoberta.rodar(cadastrar_novos=False))
    elif nome == "vigia":
        from bot import vigia
        ok = _rodar_job("varredura de precos", lambda: vigia.varrer(cadastrar_novos=False))
    else:
        return jsonify({"erro": "acao desconhecida"}), 400
    return jsonify({"ok": ok, "ocupado": not ok})


@app.get("/api/job")
def api_job():
    return jsonify(JOB)



# ---------------- CONFIG (ci.env) + FREQUENCIA (cron) ----------------
CI_ENV = BASE / "ci.env"
WORKFLOW = BASE / ".github" / "workflows" / "atualizar.yml"
CATS_JSON = BASE / "categorias.json"

CONFIG_CAMPOS = [
    ("MIN_DISCOUNT_PERCENT", "Desconto mínimo para postar (%)"),
    ("DESCONTO_FORTE_PCT", "Desconto considerado forte (%)"),
    ("CD_MENOR_PRECO", "Descanso — menor preço (min)"),
    ("CD_CUPOM", "Descanso — cupom (min)"),
    ("CD_DESC_FORTE", "Descanso — desconto forte (min)"),
    ("CD_DESC_LEVE", "Descanso — desconto leve (min)"),
    ("CD_SEM_DESCONTO", "Descanso — sem desconto (min)"),
    ("PAUSA_MADRUGADA", "Pausar de madrugada (sim/nao)"),
]


def _ler_env(path):
    d = {}
    if path.exists():
        for ln in path.read_text(encoding="utf-8").splitlines():
            s = ln.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            d[k.strip()] = v.split(" #", 1)[0].strip()
    return d


def _escrever_env(path, updates):
    linhas = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    vistos, out = set(), []
    for ln in linhas:
        s = ln.strip()
        if s and not s.startswith("#") and "=" in s:
            k = s.split("=", 1)[0].strip()
            if k in updates:
                out.append(f"{k}={updates[k]}")
                vistos.add(k)
                continue
        out.append(ln)
    for k, v in updates.items():
        if k not in vistos:
            out.append(f"{k}={v}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def _cron_horas():
    if not WORKFLOW.exists():
        return None
    m = re.search(r"cron:\s*'0 \*/(\d+) \* \* \*'", WORKFLOW.read_text(encoding="utf-8"))
    return int(m.group(1)) if m else None


def _set_cron_horas(h):
    h = max(1, min(23, int(h)))
    txt = WORKFLOW.read_text(encoding="utf-8")
    txt = re.sub(r"- cron:\s*'0 \*/\d+ \* \* \*'[^\n]*",
                 f"- cron: '0 */{h} * * *'      # a cada {h} horas (UTC)", txt)
    WORKFLOW.write_text(txt, encoding="utf-8")


@app.get("/api/config")
def api_config_get():
    env = _ler_env(CI_ENV)
    return jsonify({
        "campos": [{"k": k, "label": lb, "valor": env.get(k, "")} for k, lb in CONFIG_CAMPOS],
        "cron_horas": _cron_horas(),
    })


@app.post("/api/config")
def api_config_set():
    d = request.get_json(force=True)
    vals = d.get("valores", {}) or {}
    ups = {k: str(vals[k]) for k, _ in CONFIG_CAMPOS if k in vals and str(vals[k]).strip() != ""}
    if ups:
        _escrever_env(CI_ENV, ups)
        if (BASE / ".env").exists():
            _escrever_env(BASE / ".env", ups)
    if d.get("cron_horas"):
        _set_cron_horas(d["cron_horas"])
    return jsonify({"ok": True})


# ---------------- CATEGORIAS ----------------
@app.get("/api/categorias")
def api_cats_get():
    con = database._conn()
    rows = con.execute("SELECT COALESCE(categoria,'Outros') c, COUNT(*) n "
                       "FROM products GROUP BY c ORDER BY n DESC").fetchall()
    con.close()
    return jsonify([{"nome": r["c"], "n": r["n"]} for r in rows])


@app.post("/api/categoria/<acao>")
def api_categoria(acao):
    d = request.get_json(force=True)
    con = database._conn()
    if acao == "renomear":
        con.execute("UPDATE products SET categoria=? WHERE categoria=?", (d["novo"], d["antigo"]))
        con.commit()
        con.close()
        if CATS_JSON.exists():
            cats = _json.loads(CATS_JSON.read_text(encoding="utf-8"))
            for c in cats:
                if c.get("nome") == d["antigo"]:
                    c["nome"] = d["novo"]
            CATS_JSON.write_text(_json.dumps(cats, ensure_ascii=False, indent=2), encoding="utf-8")
        return jsonify({"ok": True})
    if acao == "apagar":
        destino = d.get("destino") or "Outros"
        con.execute("UPDATE products SET categoria=? WHERE categoria=?", (destino, d["nome"]))
        con.commit()
        con.close()
        return jsonify({"ok": True})
    con.close()
    if acao == "criar":
        cats = _json.loads(CATS_JSON.read_text(encoding="utf-8")) if CATS_JSON.exists() else []
        if not any(c.get("nome") == d["nome"] for c in cats):
            palavras = [p.strip() for p in (d.get("palavras", "") or "").split(",") if p.strip()]
            cats.append({"nome": d["nome"], "prioridade": 50, "cota": 999,
                         "cooldown_min": None, "palavras": palavras})
            CATS_JSON.write_text(_json.dumps(cats, ensure_ascii=False, indent=2), encoding="utf-8")
        return jsonify({"ok": True})
    return jsonify({"erro": "acao desconhecida"}), 400


# ---------------- ENVIAR PRO GITHUB ----------------
@app.post("/api/github/push")
def api_github_push():
    try:
        subprocess.run(["git", "-C", str(BASE), "add", "-A"],
                       check=True, capture_output=True, text=True)
        subprocess.run(["git", "-C", str(BASE), "commit", "-m", "painel: ajustes do admin"],
                       capture_output=True, text=True)
        p = subprocess.run(["git", "-C", str(BASE), "push"], capture_output=True, text=True)
        if p.returncode != 0:
            return jsonify({"ok": False,
                            "msg": "Não consegui dar push automático. Abra o GitHub Desktop e clique em Commit + Push.",
                            "detalhe": (p.stderr or "")[-300:]})
        return jsonify({"ok": True, "msg": "Enviado! A automação vai usar na próxima rodada."})
    except FileNotFoundError:
        return jsonify({"ok": False,
                        "msg": "Git não está instalado no PATH. Salve pelo GitHub Desktop: Commit + Push."})
    except Exception as e:
        return jsonify({"ok": False,
                        "msg": "Não consegui enviar automaticamente. Use o GitHub Desktop (Commit + Push).",
                        "detalhe": str(e)[-200:]})


def _porta_livre(preferida=None):
    """Acha uma porta que o Windows realmente permita usar.

    O Windows (Hyper-V/WSL) reserva faixas de portas; tentar usar uma delas
    da WinError 10013. Aqui testamos varias ate achar uma boa.
    """
    import socket
    candidatas = ([preferida] if preferida else []) + [8090, 8000, 5050, 9000, 7777, 3000, 8123, 0]
    for p in candidatas:
        if p is None:
            continue
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", p))
            real = s.getsockname()[1]
            s.close()
            return real, (p != preferida and preferida is not None)
        except OSError:
            pass
        finally:
            try:
                s.close()
            except Exception:
                pass
    return None, False


if __name__ == "__main__":
    pedida = None
    for a in sys.argv[1:]:
        if a.isdigit():
            pedida = int(a)

    porta, trocou = _porta_livre(pedida or 8080)
    if porta is None:
        print("\nNao consegui abrir nenhuma porta. Verifique firewall/antivirus.")
        sys.exit(1)
    if trocou:
        print(f"\n  (a porta {pedida or 8080} esta bloqueada pelo Windows — usando {porta})")

    print("\n== Painel do bot ==")
    print("  pasta      :", BASE)
    tpl = BASE / "templates" / "painel.html"
    print("  template   :", "OK" if tpl.exists() else "NAO ENCONTRADO -> " + str(tpl))
    try:
        database.init_db()
        n = len(database.get_products(only_active=False))
        print(f"  banco      : OK ({n} produto(s))")
    except Exception as e:
        print("  banco      : ERRO ->", e)
        print("               (feche o run_loop.py e tente de novo)")

    print(f"\n  Abra no navegador:  http://127.0.0.1:{porta}")
    print(f"  Teste rapido     :  http://127.0.0.1:{porta}/ping")
    print("  (Ctrl+C para encerrar)\n", flush=True)

    usar_flask = "--flask" in sys.argv
    if not usar_flask:
        try:
            from waitress import serve
            print(">> servidor: waitress (recomendado no Windows)\n", flush=True)
            serve(app, host="127.0.0.1", port=porta, threads=8)
            sys.exit(0)
        except ImportError:
            print(">> waitress nao instalado (pip install waitress); usando Flask\n", flush=True)
        except Exception as e:
            print(f">> waitress falhou ({e}); usando Flask\n", flush=True)

    print(">> servidor: Flask\n", flush=True)
    app.run(host="127.0.0.1", port=porta, debug=False, threaded=True)

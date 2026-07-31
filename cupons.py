#!/usr/bin/env python3
"""Gerencia os cupons do canal.

Cadastrar:
  python cupons.py add JOGAPRIME perc 10 --minimo 500 --teto 50 --validade 2026-08-31
  python cupons.py add BEMVINDO fixo 30 --minimo 200 --validade 2026-07-31
  python cupons.py add SOPS5 perc 8 --escopo MLB54963150      (cupom so de um produto)

Listar / remover:
  python cupons.py list
  python cupons.py rm JOGAPRIME

tipo: 'perc' (porcentagem) ou 'fixo' (reais)
escopo: GLOBAL (padrao, vale para todos) ou um ID de produto
"""
import sys
from datetime import date
from bot import database, cupons as C


def _opt(args, flag, default=None):
    if flag in args:
        i = args.index(flag)
        if i + 1 < len(args):
            return args[i + 1]
    return default


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    cmd = sys.argv[1].lower()
    database.init_db()

    if cmd == "add":
        if len(sys.argv) < 5:
            print("Uso: python cupons.py add CODIGO <perc|fixo> VALOR [opcoes]"); return
        args = sys.argv[5:]
        c = {
            "code": sys.argv[2], "tipo": sys.argv[3].lower(), "valor": float(sys.argv[4]),
            "minimo": float(_opt(args, "--minimo", 0) or 0),
            "teto": float(_opt(args, "--teto")) if _opt(args, "--teto") else None,
            "validade": _opt(args, "--validade"),
            "escopo": _opt(args, "--escopo", "GLOBAL"),
            "obs": _opt(args, "--obs"),
        }
        if c["tipo"] not in ("perc", "fixo"):
            print("tipo precisa ser 'perc' ou 'fixo'"); return
        database.add_coupon(c)
        print(f"Cupom {c['code'].upper()} salvo: {C.descrever(c)}"
              + (f" | vale ate {c['validade']}" if c["validade"] else "")
              + (f" | so no produto {c['escopo']}" if c["escopo"] != "GLOBAL" else ""))

    elif cmd == "list":
        lst = database.get_coupons()
        if not lst:
            print("Nenhum cupom cadastrado."); return
        print(f"{'CODIGO':<16}{'REGRA':<34}{'ESCOPO':<16}{'VALIDADE':<12}SITUACAO")
        print("-" * 92)
        for c in lst:
            venc = ""
            if c.get("validade"):
                try:
                    venc = "VENCIDO" if date.fromisoformat(c["validade"][:10]) < date.today() else "ok"
                except Exception:
                    venc = "?"
            else:
                venc = "sem prazo"
            print(f"{c['code']:<16}{C.descrever(c):<34}{(c['escopo'] or 'GLOBAL'):<16}"
                  f"{(c.get('validade') or '-'):<12}{venc}")

    elif cmd == "rm":
        database.del_coupon(sys.argv[2])
        print("Removido:", sys.argv[2].upper())
    else:
        print(__doc__)


if __name__ == "__main__":
    main()

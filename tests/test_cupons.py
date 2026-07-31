import os, sys, tempfile
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot import database, cupons


def run():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False); db = tmp.name; tmp.close()
    database.init_db(db)
    hoje = date.today()

    database.add_coupon({"code":"PERC10","tipo":"perc","valor":10,"minimo":500,"teto":50,
                         "validade":str(hoje+timedelta(days=10)),"escopo":"GLOBAL"}, db)
    database.add_coupon({"code":"FIXO30","tipo":"fixo","valor":30,"minimo":200,
                         "validade":None,"escopo":"GLOBAL"}, db)
    database.add_coupon({"code":"VENCIDO","tipo":"perc","valor":50,"minimo":0,
                         "validade":str(hoje-timedelta(days=1)),"escopo":"GLOBAL"}, db)
    database.add_coupon({"code":"SOPS5","tipo":"perc","valor":8,"minimo":0,
                         "validade":None,"escopo":"MLB999"}, db)

    # 1000 reais: PERC10 daria 100 mas teto 50 -> 50. FIXO30 -> 30. Melhor = PERC10 (50)
    m = cupons.melhor_cupom("MLB111", 1000.0, db)
    assert m["cupom"]["code"] == "PERC10" and m["desconto"] == 50 and m["final"] == 950.0, m

    # 300 reais: PERC10 nao aplica (min 500). FIXO30 aplica -> 270
    m = cupons.melhor_cupom("MLB111", 300.0, db)
    assert m["cupom"]["code"] == "FIXO30" and m["final"] == 270.0, m

    # 100 reais: nenhum aplica (minimos nao atingidos), VENCIDO ignorado
    assert cupons.melhor_cupom("MLB111", 100.0, db) is None

    # cupom de escopo especifico so vale no produto dele
    m = cupons.melhor_cupom("MLB999", 100.0, db)
    assert m["cupom"]["code"] == "SOPS5" and m["final"] == 92.0, m

    os.unlink(db)
    print("CUPONS OK ✅  (teto, mínimo, validade e escopo funcionando)")


if __name__ == "__main__":
    run()
